#!/usr/bin/env python3
"""Small HTTP sink used to inspect OTLP payloads in the compatibility probe."""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast


class SinkState:
    """Thread-safe storage for raw OTLP request bodies."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.payloads: list[bytes] = []
        self.raw_payloads: list[bytes] = []
        self.content_encodings: list[str] = []
        self._lock = threading.Lock()

    def add(self, payload: bytes, content_encoding: str | None) -> int:
        encoding = (content_encoding or "identity").strip().lower()
        if encoding in {"", "identity"}:
            decoded_payload = payload
        elif encoding == "gzip":
            decoded_payload = gzip.decompress(payload)
        else:
            raise ValueError(f"unsupported Content-Encoding: {content_encoding}")

        with self._lock:
            index = len(self.payloads) + 1
            self.output_dir.mkdir(parents=True, exist_ok=True)
            (self.output_dir / f"payload-{index:04d}.transport").write_bytes(payload)
            (self.output_dir / f"payload-{index:04d}.pb").write_bytes(decoded_payload)
            self.payloads.append(decoded_payload)
            self.raw_payloads.append(payload)
            self.content_encodings.append(encoding)
            return index

    def snapshot(self) -> list[bytes]:
        with self._lock:
            return list(self.payloads)

    def snapshot_records(self) -> tuple[list[bytes], list[bytes], list[str]]:
        with self._lock:
            return (
                list(self.payloads),
                list(self.raw_payloads),
                list(self.content_encodings),
            )


class SinkHandler(BaseHTTPRequestHandler):
    """Accept OTLP HTTP payloads and expose them for the probe process."""

    state: SinkState

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path == "/healthz":
            self._send_json(200, {"status": "ready"})
            return
        if self.path == "/records":
            payloads, raw_payloads, content_encodings = self.state.snapshot_records()
            self._send_json(
                200,
                {
                    "payload_count": len(payloads),
                    "payloads_base64": [base64.b64encode(payload).decode("ascii") for payload in payloads],
                    "raw_payloads_base64": [base64.b64encode(payload).decode("ascii") for payload in raw_payloads],
                    "content_encodings": content_encodings,
                },
            )
            return
        self._send_json(404, {"error": "not-found"})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/v1/traces":
            self._send_json(404, {"error": "not-found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)
        try:
            index = self.state.add(payload, self.headers.get("Content-Encoding"))
        except (OSError, ValueError) as exc:
            self._send_json(415, {"accepted": False, "error": str(exc)})
            return
        self._send_json(200, {"accepted": True, "payload_index": index})

    def log_message(self, _format: str, *_args: object) -> None:
        return


def build_server(host: str, port: int, output_dir: Path) -> tuple[ThreadingHTTPServer, SinkState]:
    state = SinkState(output_dir)
    handler_type = cast(type[SinkHandler], type("CompatibilitySinkHandler", (SinkHandler,), {}))
    handler_type.state = state
    return ThreadingHTTPServer((host, port), handler_type), state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=4319)
    parser.add_argument("--output-dir", type=Path, default=Path("/data"))
    args = parser.parse_args()
    server, _ = build_server(args.host, args.port, args.output_dir)
    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
