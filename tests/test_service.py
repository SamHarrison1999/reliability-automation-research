"""Unit and HTTP-boundary tests for the deterministic OrderFlow service."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import pytest

from system.orderflow import service
from system.orderflow.service import Handler, ServiceState


def test_service_event_contains_experiment_provenance(tmp_path: Path) -> None:
    """Service events must contain the fields required by the telemetry contract."""
    event_file = tmp_path / "events.jsonl"
    state = ServiceState("inventory", 8081, "inventory-v1", event_file, "run-1", "scenario-1")

    event = state.emit("test_event", example="value")

    assert event["run_id"] == "run-1"
    assert event["scenario_id"] == "scenario-1"
    assert event["source_component"] == "inventory"
    assert event["telemetry_contract"] == "otel-compatible-structured-event-v1"
    persisted = json.loads(event_file.read_text(encoding="utf-8"))
    assert persisted["event_type"] == "test_event"


def test_service_event_sequence_is_monotonic(tmp_path: Path) -> None:
    """Events from one service instance receive increasing sequence identifiers."""
    state = ServiceState("inventory", 8081, "inventory-v1", tmp_path / "events.jsonl", "run-1", "scenario-1")

    first = state.emit("first")
    second = state.emit("second")

    assert first["event_id"] == "inventory-00001"
    assert second["event_id"] == "inventory-00002"


def _start_server(tmp_path: Path, role: str, dependency_url: str = "") -> tuple[Any, ServiceState, threading.Thread]:
    from http.server import ThreadingHTTPServer

    event_file = tmp_path / f"{role}.jsonl"
    server = cast(Any, ThreadingHTTPServer(("127.0.0.1", 0), cast(Any, type("TestHandler", (Handler,), {}))))
    state = ServiceState(role, server.server_port, f"{role}-v1", event_file, "run-1", "scenario-1")
    server.RequestHandlerClass.state = state
    server.RequestHandlerClass.dependency_url = dependency_url
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, state, thread


def _request(
    port: int, path: str, method: str = "GET", payload: dict[str, object] | None = None
) -> tuple[int, dict[str, object]]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method)
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode())


def _stop_server(server: Any, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_service_state_honours_supplied_trace_id_and_prints_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state = ServiceState("inventory", 8081, "inventory-v1", tmp_path / "events.jsonl", "run-1", "scenario-1")
    printed: list[str] = []
    monkeypatch.setattr("builtins.print", lambda value, flush: printed.append(value))

    event = state.emit("trace_event", trace_id="provided", field="value")

    assert event["trace_id"] == "provided"
    assert event["field"] == "value"
    assert json.loads(printed[0])["event_type"] == "trace_event"


def test_inventory_http_endpoints_cover_health_version_reserve_and_faults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, state, thread = _start_server(tmp_path, "inventory")
    try:
        assert _request(server.server_port, "/healthz")[0] == 200
        assert _request(server.server_port, "/version")[1]["version"] == "inventory-v1"
        assert _request(server.server_port, "/reserve?order_id=abc")[1]["status"] == "reserved"

        monkeypatch.setattr(service.time, "sleep", lambda _seconds: None)
        assert _request(server.server_port, "/__control", "POST", {"mode": "latency", "latency_ms": 5})[0] == 200
        assert _request(server.server_port, "/reserve?order_id=slow")[0] == 200
        assert _request(server.server_port, "/__control", "POST", {"mode": "failure"})[0] == 200
        assert _request(server.server_port, "/reserve?order_id=failed")[0] == 503
        assert _request(server.server_port, "/__control", "POST", {"mode": "none"})[1]["latency_ms"] == 0
        assert _request(server.server_port, "/__control", "POST", {"mode": "unsupported"})[0] == 400
        assert _request(server.server_port, "/unknown")[0] == 404
        assert state.fault_mode == "none"
    finally:
        _stop_server(server, thread)


def test_order_api_success_dependency_failure_and_connection_failure(tmp_path: Path) -> None:
    inventory, inventory_state, inventory_thread = _start_server(tmp_path, "inventory")
    order, _, order_thread = _start_server(tmp_path, "order-api", f"http://127.0.0.1:{inventory.server_port}")
    try:
        assert _request(order.server_port, "/orders", "POST", {"order_id": "ok"})[0] == 201
        inventory_state.fault_mode = "failure"
        assert _request(order.server_port, "/orders", "POST", {"order_id": "bad"})[0] == 502
        order.RequestHandlerClass.dependency_url = "http://127.0.0.1:1"
        assert _request(order.server_port, "/orders", "POST", {"order_id": "offline"})[0] == 502
        assert _request(order.server_port, "/__control", "POST", {"mode": "none"})[0] == 404
        assert _request(order.server_port, "/unknown")[0] == 404
    finally:
        _stop_server(order, order_thread)
        _stop_server(inventory, inventory_thread)


def test_order_handler_returns_502_for_a_non_http_error_dependency_response(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state = ServiceState("order-api", 8080, "order-api-v1", tmp_path / "events.jsonl", "run-1", "scenario-1")
    handler = cast(Any, object.__new__(Handler))
    handler.state = state
    handler.dependency_url = "http://dependency"
    handler.path = "/orders"
    handler.read_json = lambda: {"order_id": "non-200"}
    handler.send_json = Mock()

    class Response:
        status = 503

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    monkeypatch.setattr(service.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())

    handler.do_POST()

    assert handler.send_json.call_args.args == (502, {"status": "failed", "order_id": "non-200"})


def test_handler_helpers_read_empty_json_and_suppress_access_logs(monkeypatch: pytest.MonkeyPatch) -> None:
    handler = cast(Any, object.__new__(Handler))
    handler.headers = {}
    handler.rfile = SimpleNamespace(read=lambda _length: b"{}")

    assert handler.read_json() == {}
    handler.log_message("ignored")


def test_service_main_builds_server_registers_signals_and_closes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}

    class FakeServer:
        server_port = 8080

        def __init__(self, address: tuple[str, int], handler_type: type[Handler]) -> None:
            captured["address"] = address
            captured["handler"] = handler_type

        def serve_forever(self, poll_interval: float) -> None:
            captured["poll_interval"] = poll_interval

        def shutdown(self) -> None:
            captured["shutdown"] = True

        def server_close(self) -> None:
            captured["closed"] = True

    signals: dict[int, object] = {}
    monkeypatch.setattr(service, "ThreadingHTTPServer", FakeServer)
    monkeypatch.setattr(service.signal, "signal", lambda signum, callback: signals.__setitem__(signum, callback))
    monkeypatch.setattr(
        "sys.argv",
        [
            "service",
            "--role",
            "order-api",
            "--port",
            "8080",
            "--version",
            "v1",
            "--event-file",
            str(tmp_path / "events.jsonl"),
            "--run-id",
            "run-1",
            "--scenario-id",
            "scenario-1",
            "--dependency-url",
            "http://127.0.0.1:8081",
        ],
    )

    assert service.main() == 0
    assert captured["address"] == ("127.0.0.1", 8080)
    assert captured["poll_interval"] == 0.05
    assert captured["closed"] is True
    callback = next(iter(signals.values()))
    callback(15, None)  # type: ignore[operator]
    assert captured["shutdown"] is True
