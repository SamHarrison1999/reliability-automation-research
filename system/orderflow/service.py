#!/usr/bin/env python3
"""Minimal deterministic OrderFlow service used only by the Phase 2 fit probe."""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{time.time_ns() % 1_000_000_000:09d}Z"


class ServiceState:
    def __init__(
        self,
        role: str,
        port: int,
        version: str,
        event_file: Path,
        run_id: str,
        scenario_id: str,
        trial_id: str | None = None,
        automation_condition: str | None = None,
        repetition: int | None = None,
        run_order: int | None = None,
    ):
        self.role = role
        self.port = port
        self.version = version
        self.event_file = event_file
        self.run_id = run_id
        self.scenario_id = scenario_id
        self.trial_id = trial_id
        self.automation_condition = automation_condition
        self.repetition = repetition
        self.run_order = run_order
        self.service_instance_id = uuid.uuid4().hex if trial_id is not None else None
        self.sequence = 0
        self.fault_mode = "none"
        self.latency_ms = 0

    def emit(self, event_type: str, **fields: Any) -> dict[str, Any]:
        self.sequence += 1
        event = {
            "event_id": (
                f"{self.trial_id}-{self.role}-{self.service_instance_id}-{self.sequence:05d}"
                if self.trial_id
                else f"{self.role}-{self.sequence:05d}"
            ),
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "source_component": self.role,
            "event_type": event_type,
            "timestamp": utc_now(),
            "trace_id": fields.pop("trace_id", uuid.uuid4().hex),
            "span_id": uuid.uuid4().hex[:16],
            "software_version": self.version,
            "telemetry_contract": "otel-compatible-structured-event-v1",
            **fields,
        }
        if self.trial_id is not None:
            event["trial_id"] = self.trial_id
            event["automation_condition"] = self.automation_condition
            event["repetition"] = self.repetition
            event["run_order"] = self.run_order
            event["service_instance_id"] = self.service_instance_id
        self.event_file.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(event, sort_keys=True)
        with self.event_file.open("a", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
        # Containerised runs use stdout as the portable log transport.
        print(encoded, flush=True)
        return event


class Handler(BaseHTTPRequestHandler):
    state: ServiceState
    dependency_url: str

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return cast(dict[str, Any], json.loads(raw.decode("utf-8")))

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.state.emit("readiness_check", status="ready")
            self.send_json(200, {"status": "ready", "component": self.state.role, "version": self.state.version})
            return
        if self.path == "/version":
            self.send_json(200, {"component": self.state.role, "version": self.state.version})
            return
        if self.state.role == "inventory" and self.path.startswith("/reserve"):
            order_id = self.path.split("order_id=", 1)[-1]
            trace_id = uuid.uuid4().hex
            self.state.emit("dependency_request_received", order_id=order_id, trace_id=trace_id)
            if self.state.fault_mode == "latency":
                self.state.emit(
                    "dependency_fault_applied",
                    fault_mode="latency",
                    latency_ms=self.state.latency_ms,
                    trace_id=trace_id,
                )
                time.sleep(self.state.latency_ms / 1000)
            if self.state.fault_mode == "failure":
                self.state.emit(
                    "dependency_failure_returned", fault_mode="failure", order_id=order_id, trace_id=trace_id
                )
                self.send_json(503, {"status": "dependency-failure", "order_id": order_id})
                return
            self.state.emit("dependency_request_succeeded", order_id=order_id, trace_id=trace_id)
            self.send_json(200, {"status": "reserved", "order_id": order_id})
            return
        self.send_json(404, {"error": "not-found"})

    def do_POST(self) -> None:
        if self.path == "/__control" and self.state.role == "inventory":
            payload = self.read_json()
            mode = payload.get("mode", "none")
            if mode not in {"none", "latency", "failure"}:
                self.send_json(400, {"error": "unsupported-fault-mode"})
                return
            self.state.fault_mode = mode
            self.state.latency_ms = int(payload.get("latency_ms", 0)) if mode == "latency" else 0
            self.state.emit("fault_state_changed", fault_mode=mode, latency_ms=self.state.latency_ms)
            self.send_json(200, {"mode": mode, "latency_ms": self.state.latency_ms})
            return
        if self.path == "/orders" and self.state.role == "order-api":
            payload = self.read_json()
            order_id = str(payload.get("order_id", ""))
            trace_id = uuid.uuid4().hex
            self.state.emit("workload_request_received", order_id=order_id, trace_id=trace_id)
            request = urllib.request.Request(
                f"{self.dependency_url}/reserve?order_id={order_id}",
                method="GET",
            )
            self.state.emit("dependency_request_started", dependency="inventory", order_id=order_id, trace_id=trace_id)
            try:
                with urllib.request.urlopen(request, timeout=1.0) as response:
                    dependency_status = response.status
            except (urllib.error.URLError, TimeoutError) as exc:
                self.state.emit(
                    "dependency_request_failed",
                    dependency="inventory",
                    order_id=order_id,
                    error=type(exc).__name__,
                    trace_id=trace_id,
                )
                self.state.emit(
                    "workload_request_failed", order_id=order_id, reason="dependency-unavailable", trace_id=trace_id
                )
                self.send_json(502, {"status": "failed", "order_id": order_id})
                return
            if dependency_status != 200:
                self.state.emit(
                    "dependency_response_failed",
                    dependency="inventory",
                    status=dependency_status,
                    order_id=order_id,
                    trace_id=trace_id,
                )
                self.state.emit(
                    "workload_request_failed", order_id=order_id, reason="dependency-failure", trace_id=trace_id
                )
                self.send_json(502, {"status": "failed", "order_id": order_id})
                return
            self.state.emit("workload_request_succeeded", order_id=order_id, trace_id=trace_id)
            self.send_json(201, {"status": "accepted", "order_id": order_id, "version": self.state.version})
            return
        # Consume an unrecognised POST body before closing the connection.  Windows
        # can reset a socket when the server closes with unread request bytes.
        self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self.send_json(404, {"error": "not-found"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["order-api", "inventory"], required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--scenario-id", required=True)
    parser.add_argument("--trial-id")
    parser.add_argument("--automation-condition", choices=["control", "manual", "automated"])
    parser.add_argument("--repetition", type=int)
    parser.add_argument("--run-order", type=int)
    parser.add_argument("--dependency-url", default="")
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    state = ServiceState(
        args.role,
        args.port,
        args.version,
        args.event_file,
        args.run_id,
        args.scenario_id,
        args.trial_id,
        args.automation_condition,
        args.repetition,
        args.run_order,
    )
    handler_type = type("OrderFlowHandler", (Handler,), {})
    handler_type.state = state  # type: ignore[attr-defined]
    handler_type.dependency_url = args.dependency_url  # type: ignore[attr-defined]
    server = ThreadingHTTPServer((args.host, args.port), handler_type)

    def stop(_signum: int, _frame: Any) -> None:
        state.emit("service_stopped", reason="signal")
        server.shutdown()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    state.emit("service_started", port=args.port)
    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI entry point
    sys.exit(main())
