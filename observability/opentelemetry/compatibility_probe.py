#!/usr/bin/env python3
"""Run and verify a real OpenTelemetry Python SDK to Collector trace path."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata
import json
import platform
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROBE_VERSION = "otel-sdk-collector-compatibility-v2"
COLLECTOR_IMAGE = "otel/opentelemetry-collector:0.158.0"


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def get_json(url: str, timeout: float = 2.0) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def installed_package_versions() -> dict[str, str]:
    names = (
        "opentelemetry-api",
        "opentelemetry-exporter-otlp-proto-http",
        "opentelemetry-proto",
        "opentelemetry-sdk",
    )
    return {name: importlib.metadata.version(name) for name in names}


def wait_for_collector(collector_endpoint: str, timeout_seconds: float = 20.0) -> None:
    parsed = urllib.parse.urlparse(collector_endpoint)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    deadline = time.monotonic() + timeout_seconds
    last_error = "not attempted"
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(0.2)
    raise RuntimeError(f"Collector endpoint did not become reachable: {last_error}")


def wait_for_sink(sink_url: str, timeout_seconds: float = 20.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = "not attempted"
    while time.monotonic() < deadline:
        try:
            payload = get_json(f"{sink_url.rstrip('/')}/healthz", timeout=1.0)
            if payload.get("status") == "ready":
                return
            last_error = f"unexpected health response: {payload}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(0.2)
    raise RuntimeError(f"telemetry sink did not become ready: {last_error}")


def read_sink_payloads(sink_url: str) -> list[bytes]:
    payload = get_json(f"{sink_url.rstrip('/')}/records")
    encoded = payload.get("payloads_base64")
    if not isinstance(encoded, list) or not all(isinstance(item, str) for item in encoded):
        raise RuntimeError("sink returned an invalid payload list")
    return [base64.b64decode(item) for item in encoded]


def read_sink_raw_payloads(sink_url: str) -> list[bytes]:
    payload = get_json(f"{sink_url.rstrip('/')}/records")
    encoded = payload.get("raw_payloads_base64")
    if not isinstance(encoded, list) or not all(isinstance(item, str) for item in encoded):
        raise RuntimeError("sink returned an invalid raw payload list")
    return [base64.b64decode(item) for item in encoded]


def read_sink_content_encodings(sink_url: str) -> list[str]:
    payload = get_json(f"{sink_url.rstrip('/')}/records")
    encodings = payload.get("content_encodings")
    if not isinstance(encodings, list) or not all(isinstance(item, str) for item in encodings):
        raise RuntimeError("sink returned invalid content encodings")
    return encodings


def emit_spans(collector_endpoint: str, run_id: str, span_count: int) -> None:
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    except ImportError as exc:
        raise RuntimeError("install the repository observability extra before running the probe") from exc

    provider = TracerProvider(resource=Resource.create({"service.name": "orderflow-otel-compatibility-probe"}))
    exporter = OTLPSpanExporter(endpoint=collector_endpoint)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(PROBE_VERSION)
    trace.set_tracer_provider(provider)
    try:
        for sequence in range(1, span_count + 1):
            with tracer.start_as_current_span("compatibility-probe-span") as span:
                span.set_attribute("probe.run_id", run_id)
                span.set_attribute("probe.sequence", sequence)
                span.set_attribute("probe.emitted_at", utc_now())
    finally:
        provider.shutdown()


def decode_spans(payloads: list[bytes]) -> list[dict[str, Any]]:
    try:
        from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
    except ImportError as exc:
        raise RuntimeError("install opentelemetry-proto before decoding Collector payloads") from exc

    spans: list[dict[str, Any]] = []
    for payload in payloads:
        request = ExportTraceServiceRequest()
        request.ParseFromString(payload)
        for resource_spans in request.resource_spans:
            for scope_spans in resource_spans.scope_spans:
                for span in scope_spans.spans:
                    attributes = {item.key: item.value for item in span.attributes}
                    spans.append(
                        {
                            "name": span.name,
                            "trace_id": span.trace_id.hex(),
                            "span_id": span.span_id.hex(),
                            "sequence": int(attributes["probe.sequence"].int_value),
                            "run_id": attributes["probe.run_id"].string_value,
                            "start_time_unix_nano": int(span.start_time_unix_nano),
                            "end_time_unix_nano": int(span.end_time_unix_nano),
                        }
                    )
    return spans


def evaluate(
    run_id: str,
    payloads: list[bytes],
    spans: list[dict[str, Any]],
    expected_count: int,
    raw_payloads: list[bytes] | None = None,
    content_encodings: list[str] | None = None,
) -> dict[str, Any]:
    sequences = sorted(int(item["sequence"]) for item in spans if item["run_id"] == run_id)
    timestamps = [int(item["start_time_unix_nano"]) for item in spans if item["run_id"] == run_id]
    return {
        "expected_span_count": expected_count,
        "received_payload_count": len(payloads),
        "decoded_span_count": len(spans),
        "run_span_count": len(sequences),
        "sequence_values": sequences,
        "sequence_complete": sequences == list(range(1, expected_count + 1)),
        "timestamps_parseable": all(timestamp > 0 for timestamp in timestamps),
        "timestamps_non_decreasing": timestamps == sorted(timestamps),
        "payload_sha256": [sha256_bytes(payload) for payload in payloads],
        "raw_transport_payload_sha256": [sha256_bytes(payload) for payload in (raw_payloads or [])],
        "content_encodings": content_encodings or [],
        "span_records": spans,
    }


def run_probe(collector_endpoint: str, sink_url: str, output_root: Path, span_count: int) -> dict[str, Any]:
    run_id = f"otel-compat-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    metadata: dict[str, Any] = {
        "probe_version": PROBE_VERSION,
        "run_id": run_id,
        "started_at": utc_now(),
        "collector_endpoint": collector_endpoint,
        "sink_url": sink_url,
        "expected_span_count": span_count,
        "collector_image": COLLECTOR_IMAGE,
        "python_package_versions": installed_package_versions(),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payloads: list[bytes] = []
    raw_payloads: list[bytes] = []
    content_encodings: list[str] = []
    try:
        wait_for_sink(sink_url)
        wait_for_collector(collector_endpoint)
        emit_spans(collector_endpoint, run_id, span_count)
        deadline = time.monotonic() + 20.0
        while time.monotonic() < deadline:
            payloads = read_sink_payloads(sink_url)
            raw_payloads = read_sink_raw_payloads(sink_url)
            content_encodings = read_sink_content_encodings(sink_url)
            if payloads:
                break
            time.sleep(0.2)
        spans = decode_spans(payloads)
        evaluation = evaluate(run_id, payloads, spans, span_count, raw_payloads, content_encodings)
    except Exception as exc:
        result = {**metadata, "status": "blocked", "error": f"{type(exc).__name__}: {exc}", "completed_at": utc_now()}
        (run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (run_dir / "raw-payloads.json").write_text(
            json.dumps(
                {
                    "payloads_base64": [base64.b64encode(item).decode("ascii") for item in payloads],
                    "raw_transport_payloads_base64": [base64.b64encode(item).decode("ascii") for item in raw_payloads],
                    "content_encodings": content_encodings,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        raise

    result = {
        **metadata,
        **evaluation,
        "status": "passed" if evaluation["sequence_complete"] and evaluation["timestamps_parseable"] else "failed",
        "completed_at": utc_now(),
    }
    (run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_dir / "raw-payloads.json").write_text(
        json.dumps(
            {
                "payloads_base64": [base64.b64encode(item).decode("ascii") for item in payloads],
                "raw_transport_payloads_base64": [base64.b64encode(item).decode("ascii") for item in raw_payloads],
                "content_encodings": content_encodings,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if not result["sequence_complete"] or not result["timestamps_parseable"]:
        raise RuntimeError(f"OpenTelemetry compatibility validation failed: {result}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collector-endpoint", default="http://127.0.0.1:4318/v1/traces")
    parser.add_argument("--sink-url", default="http://127.0.0.1:4319")
    parser.add_argument("--output-root", type=Path, default=Path("results/observability/opentelemetry"))
    parser.add_argument("--span-count", type=int, default=5)
    args = parser.parse_args()
    result = run_probe(args.collector_endpoint, args.sink_url, args.output_root, args.span_count)
    print(
        json.dumps({"status": "passed", "run_id": result["run_id"], "decoded_span_count": result["decoded_span_count"]})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
