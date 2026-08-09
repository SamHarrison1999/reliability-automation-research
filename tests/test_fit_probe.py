"""Unit and boundary tests for the portable fit-probe controller."""

from __future__ import annotations

import io
import json
import subprocess
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path
from typing import Any, cast
from unittest.mock import Mock

import pytest

from experiments.harness import fit_probe
from experiments.harness.fit_probe import ProbeRun, check_run, load_json


def _manifest() -> dict[str, object]:
    return {
        "manifest_version": "1.0.0",
        "target_model": "local-process-fit-probe",
        "experimental_target": "kubernetes",
        "reset_contract": ["stop", "start", "ready"],
        "services": {
            "inventory": {"port": 18381, "version": "inventory-v1"},
            "order-api": {"port": 18380, "version": "order-api-v1"},
        },
    }


def _scenario(scenario_type: str = "baseline") -> dict[str, object]:
    return {
        "manifest_version": "1.0.0",
        "scenario_id": f"{scenario_type}-v1",
        "scenario_type": scenario_type,
        "workload": {"requests_before_fault": 1, "requests_during_fault": 1, "requests_after_fault": 1},
        "fault": {"target": "inventory", "latency_ms": 7},
        "deployment_transition": {"upgrade_version": "order-api-v2", "rollback_version": "order-api-v1"},
        "expected_event_types": ["run_started", "run_completed"],
    }


class _Process:
    """Small process double with configurable cleanup behaviour."""

    pid = 123
    returncode = 0

    def __init__(self, running: bool = True, timeout_on_wait: bool = False) -> None:
        self.running = running
        self.timeout_on_wait = timeout_on_wait
        self.terminated = False
        self.killed = False

    def poll(self) -> int | None:
        return None if self.running else self.returncode

    def terminate(self) -> None:
        self.terminated = True
        self.running = False

    def kill(self) -> None:
        self.killed = True
        self.running = False

    def wait(self, timeout: float | None = None) -> int:
        if self.timeout_on_wait and not self.killed:
            raise subprocess.TimeoutExpired("fake", timeout if timeout is not None else 0)
        return self.returncode


def _run(tmp_path: Path, scenario_type: str = "baseline") -> ProbeRun:
    return ProbeRun(_manifest(), _scenario(scenario_type), tmp_path)


def _event(event_type: str, run_id: str = "no-fault-v1-run-1", source: str = "service") -> dict[str, object]:
    """Build the smallest event accepted by ``check_run``."""
    event: dict[str, object] = {
        "event_id": f"{source}-{event_type}",
        "run_id": run_id,
        "scenario_id": "no-fault-v1",
        "source_component": source,
        "event_type": event_type,
        "timestamp": "2026-08-09T00:00:00.000Z",
        "trace_id": "trace-1",
    }
    if source != "fit-probe-controller":
        event["span_id"] = "span-1"
    return event


def test_load_json_reads_a_scenario_manifest() -> None:
    """Load one of the versioned scenario manifests from the repository."""
    scenario = load_json(Path("experiments/scenarios/no-fault.json"))

    assert scenario["scenario_id"] == "no-fault-v1"
    assert scenario["scenario_type"] == "baseline"


def test_check_run_accepts_a_complete_baseline_bundle(tmp_path: Path) -> None:
    """A complete baseline bundle should pass structural validation."""
    scenario = load_json(Path("experiments/scenarios/no-fault.json"))
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()

    required_events = [
        "run_started",
        "reset_completed",
        "workload_started",
        "workload_request",
        "workload_response",
        "deployment_update_started",
        "deployment_update_completed",
        "rollback_started",
        "rollback_completed",
        "run_completed",
    ]
    required_events.append("clean_state_verified")
    events = [_event(event_type, source="fit-probe-controller") for event_type in required_events]
    (run_dir / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
    (run_dir / "metadata.json").write_text("{}\n", encoding="utf-8")

    result = check_run(run_dir, scenario)

    assert result["passed"] is True
    assert result["missing_event_types"] == []


def test_check_run_rejects_a_bundle_with_missing_events(tmp_path: Path) -> None:
    """A bundle missing a required event class must fail validation."""
    scenario = load_json(Path("experiments/scenarios/no-fault.json"))
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    (run_dir / "events.jsonl").write_text(
        json.dumps(_event("run_started", source="fit-probe-controller")) + "\n", encoding="utf-8"
    )

    result = check_run(run_dir, scenario)

    assert result["passed"] is False
    assert "reset_completed" in result["missing_event_types"]


def test_utc_now_and_sha256_file_are_stable_helpers(tmp_path: Path) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_text("hello", encoding="utf-8")

    assert fit_probe.utc_now().endswith("Z")
    assert fit_probe.sha256_file(payload) == ("2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")


def test_probe_run_emits_events_and_builds_component_urls(tmp_path: Path) -> None:
    run = _run(tmp_path)

    event = run.emit("test_event", answer=42)

    assert event["event_id"] == "controller-00001"
    assert event["answer"] == 42
    assert run.url("inventory", "/healthz") == "http://127.0.0.1:18381/healthz"
    assert json.loads(run.event_file.read_text(encoding="utf-8"))["event_type"] == "test_event"


@pytest.mark.parametrize("body", [None, {"order_id": "one"}])
def test_probe_request_returns_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, body: dict[str, object] | None
) -> None:
    run = _run(tmp_path)

    class Response:
        status = 200

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"status":"ok"}'

    captured: list[urllib.request.Request] = []

    def fake_urlopen(request: urllib.request.Request, **_kwargs: object) -> Response:
        captured.append(request)
        return Response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    status, response, elapsed = run.request("inventory", "/healthz", method="POST", body=body)

    assert (status, response) == (200, {"status": "ok"})
    assert elapsed >= 0
    assert captured[0].get_header("Content-type") == ("application/json" if body is not None else None)


def test_probe_request_handles_http_and_connection_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run = _run(tmp_path)
    http_error = urllib.error.HTTPError(
        run.url("inventory", "/healthz"), 503, "failed", Message(), io.BytesIO(b'{"error":"down"}')
    )
    monkeypatch.setattr(urllib.request, "urlopen", Mock(side_effect=http_error))
    assert run.request("inventory", "/healthz")[0:2] == (503, {"error": "down"})
    for error in (urllib.error.URLError("offline"), TimeoutError(), ConnectionError()):
        monkeypatch.setattr(urllib.request, "urlopen", Mock(side_effect=error))
        status, body, _ = run.request("inventory", "/healthz")
        assert status == 0
        assert body == {"error": type(error).__name__}


def test_start_service_adds_dependency_url_and_records_process(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run = _run(tmp_path)
    process = _Process()
    popen = Mock(return_value=process)
    monkeypatch.setattr(fit_probe.subprocess, "Popen", popen)

    run.start_service("order-api", "order-api-v2")

    command = popen.call_args.args[0]
    assert "--dependency-url" in command
    assert run.processes["order-api"] is process
    assert run.events[-1]["service_version"] == "order-api-v2"
    run.start_service("inventory")
    assert popen.call_count == 2


def test_stop_service_covers_missing_finished_and_kill_cleanup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run = _run(tmp_path)
    run.stop_service("inventory", "not-started")
    finished = _Process(running=False)
    run.processes["inventory"] = cast(Any, finished)
    run.stop_service("inventory", "already-finished")
    stubborn = _Process(timeout_on_wait=True)
    run.processes["order-api"] = cast(Any, stubborn)
    run.stop_service("order-api", "forced-cleanup")

    assert finished.terminated is False
    assert stubborn.terminated is True
    assert stubborn.killed is True
    assert [event["event_type"] for event in run.events] == ["service_process_stopped", "service_process_stopped"]


def test_stop_all_stops_every_registered_process(tmp_path: Path) -> None:
    run = _run(tmp_path)
    first = _Process()
    second = _Process()
    run.processes = cast(Any, {"inventory": first, "order-api": second})

    run.stop_all("test-cleanup")

    assert run.processes == {}
    assert first.terminated is True
    assert second.terminated is True


def test_wait_ready_success_and_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run = _run(tmp_path)
    run.request = Mock(return_value=(200, {}, 0.0))  # type: ignore[method-assign]
    run.wait_ready()
    assert run.events[-1]["result"] == "ready"

    failed = _run(tmp_path / "failed")
    failed.request = Mock(return_value=(500, {}, 0.0))  # type: ignore[method-assign]
    clock = iter([0.0, 0.0, 10.0])
    monkeypatch.setattr(fit_probe.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(fit_probe.time, "sleep", lambda _seconds: None)
    with pytest.raises(RuntimeError, match="did not become ready"):
        failed.wait_ready()
    assert failed.events[-1]["result"] == "failed"


def test_reset_starts_both_services_and_records_clean_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run = _run(tmp_path)
    run.stop_all = Mock()  # type: ignore[method-assign]
    run.start_service = Mock()  # type: ignore[method-assign]
    run.wait_ready = Mock()  # type: ignore[method-assign]

    run.reset()

    run.stop_all.assert_called_once_with("clean-reset")
    assert run.start_service.call_count == 2
    assert run.events[-1]["event_type"] == "reset_completed"


def test_workload_records_success_and_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run = _run(tmp_path)
    run.request = Mock(side_effect=[(201, {"status": "accepted"}, 0.01), (502, {"status": "failed"}, 0.02)])  # type: ignore[method-assign]
    monkeypatch.setattr(fit_probe.time, "sleep", lambda _seconds: None)

    outcomes = run.workload(2, "test-phase")

    assert [item["result"] for item in outcomes] == ["success", "failure"]
    assert run.events[-1]["event_type"] == "workload_response"


def test_transition_and_dependency_fault_boundaries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run = _run(tmp_path)
    run.stop_service = Mock()  # type: ignore[method-assign]
    run.start_service = Mock()  # type: ignore[method-assign]
    run.wait_ready = Mock()  # type: ignore[method-assign]
    run.request = Mock(side_effect=[(200, {}, 0.0), (200, {}, 0.0), (500, {}, 0.0)])  # type: ignore[method-assign]

    run.transition_version("order-api-v2", "deployment_update")
    run.apply_dependency_fault("latency", 10)
    run.clear_dependency_fault()
    assert run.started_versions["order-api"] == "order-api-v2"
    with pytest.raises(RuntimeError, match="could not apply"):
        run.apply_dependency_fault("failure")

    run.request = Mock(return_value=(503, {}, 0.0))  # type: ignore[method-assign]
    with pytest.raises(RuntimeError, match="could not clear"):
        run.clear_dependency_fault()


@pytest.mark.parametrize("scenario_type", ["baseline", "service-termination", "dependency-latency"])
def test_execute_completes_each_scenario_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, scenario_type: str
) -> None:
    monkeypatch.setattr(fit_probe, "ROOT", tmp_path)
    monkeypatch.setattr(fit_probe, "sha256_file", lambda _path: "hash")
    run = _run(tmp_path, scenario_type)
    run.reset = Mock()  # type: ignore[method-assign]
    run.stop_all = Mock()  # type: ignore[method-assign]
    run.wait_ready = Mock()  # type: ignore[method-assign]
    run.start_service = Mock()  # type: ignore[method-assign]
    run.stop_service = Mock()  # type: ignore[method-assign]
    run.transition_version = Mock()  # type: ignore[method-assign]
    run.apply_dependency_fault = Mock()  # type: ignore[method-assign]
    run.clear_dependency_fault = Mock()  # type: ignore[method-assign]
    run.workload = Mock(return_value=[{"result": "success", "status": 201}])  # type: ignore[method-assign]

    metadata = run.execute()

    assert metadata["scenario_id"] == f"{scenario_type}-v1"
    assert metadata["event_count"] >= 2
    run.stop_all.assert_called_once_with("run-complete")


def test_execute_rejects_unknown_scenario(tmp_path: Path) -> None:
    run = _run(tmp_path, "unsupported")
    run.reset = Mock()  # type: ignore[method-assign]
    run.stop_all = Mock()  # type: ignore[method-assign]

    with pytest.raises(ValueError, match="unsupported scenario"):
        run.execute()


@pytest.mark.parametrize(
    ("scenario_type", "source", "target", "metadata", "expected"),
    [
        ("service-termination", "service", True, True, True),
        ("dependency-latency", "service", True, True, True),
        ("baseline", "fit-probe-controller", False, True, True),
        ("baseline", "service", False, False, False),
    ],
)
def test_check_run_evaluates_service_and_baseline_contracts(
    tmp_path: Path,
    scenario_type: str,
    source: str,
    target: bool,
    metadata: bool,
    expected: bool,
) -> None:
    scenario = _scenario(scenario_type)
    scenario["expected_event_types"] = ["run_started"]
    run_dir = tmp_path / scenario_type
    run_dir.mkdir()
    events = []
    for event_type in ("run_started", "reset_completed", "clean_state_verified"):
        event = _event(event_type, run_id=f"{scenario_type}-v1-run", source=source)
        event["scenario_id"] = scenario["scenario_id"]
        if target:
            event["target_component"] = "inventory"
        events.append(event)
    (run_dir / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
    if metadata:
        (run_dir / "metadata.json").write_text("{}\n", encoding="utf-8")

    result = check_run(run_dir, scenario)

    assert result["passed"] is expected


def test_main_records_successful_runs_with_repeat_metadata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    scenarios = [
        _scenario("baseline"),
        _scenario("service-termination"),
        _scenario("dependency-latency"),
        _scenario("dependency-latency"),
    ]
    monkeypatch.setattr(fit_probe, "load_json", Mock(side_effect=[_manifest(), *scenarios]))

    class FakeRun:
        counter = 0

        def __init__(
            self, _manifest: object, scenario: dict[str, object], output_root: Path, repeat_of: str | None = None
        ) -> None:
            FakeRun.counter += 1
            self.run_id = f"run-{FakeRun.counter}"
            self.run_dir = output_root / self.run_id
            self.event_file = self.run_dir / "events.jsonl"
            self.metadata_file = self.run_dir / "metadata.json"
            self.scenario = scenario
            self.repeat_of = repeat_of
            self.run_dir.mkdir(parents=True, exist_ok=True)

        def execute(self) -> dict[str, object]:
            self.event_file.write_text(json.dumps({"event_type": "run_started"}) + "\n", encoding="utf-8")
            metadata = {"run_id": self.run_id, "scenario_id": self.scenario["scenario_id"]}
            self.metadata_file.write_text(json.dumps(metadata), encoding="utf-8")
            return metadata

        def stop_all(self, _reason: str) -> None:
            return None

        def emit(self, *_args: object, **_kwargs: object) -> None:
            return None

    monkeypatch.setattr(fit_probe, "ProbeRun", FakeRun)
    monkeypatch.setattr(fit_probe, "check_run", lambda *_args: {"passed": True})
    monkeypatch.setattr("sys.argv", ["fit_probe", "--output-root", str(tmp_path / "raw")])

    assert fit_probe.main() == 0
    summary = json.loads((tmp_path / "fit-probe-summary.json").read_text(encoding="utf-8"))
    assert summary["all_local_checks_passed"] is True


def test_main_returns_failure_and_records_exception(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    scenarios = [_scenario("baseline")] * 4
    monkeypatch.setattr(fit_probe, "load_json", Mock(side_effect=[_manifest(), *scenarios]))

    class FailingRun:
        def __init__(
            self, _manifest: object, scenario: dict[str, object], output_root: Path, repeat_of: str | None = None
        ) -> None:
            self.run_id = "failed-run"
            self.run_dir = output_root / self.run_id
            self.event_file = self.run_dir / "events.jsonl"
            self.metadata_file = self.run_dir / "metadata.json"
            self.run_dir.mkdir(parents=True, exist_ok=True)

        def execute(self) -> dict[str, object]:
            raise RuntimeError("boom")

        def stop_all(self, _reason: str) -> None:
            return None

        def emit(self, *_args: object, **_kwargs: object) -> None:
            return None

    monkeypatch.setattr(fit_probe, "ProbeRun", FailingRun)
    monkeypatch.setattr("sys.argv", ["fit_probe", "--output-root", str(tmp_path / "raw")])

    assert fit_probe.main() == 1
