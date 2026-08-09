"""Unit tests for the Kubernetes fit-probe orchestration boundaries."""

from __future__ import annotations

import io
import json
import subprocess
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from experiments.harness import kubernetes_fit_probe as kube
from experiments.harness.kubernetes_fit_probe import KubernetesProbe, validate_run


def _scenario(scenario_type: str = "baseline") -> dict[str, Any]:
    return {
        "scenario_id": f"{scenario_type}-v1",
        "scenario_type": scenario_type,
        "workload": {"requests_before_fault": 1, "requests_during_fault": 1, "requests_after_fault": 1},
        "fault": {"latency_ms": 12},
        "expected_event_types": ["run_started", "reset_completed", "run_completed"],
    }


def _probe(tmp_path: Path, scenario_type: str = "baseline") -> KubernetesProbe:
    return KubernetesProbe(_scenario(scenario_type), tmp_path)


class _Process:
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


def test_helpers_and_run_command_cover_success_and_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_text("hello", encoding="utf-8")

    assert kube.utc_now().endswith("Z")
    assert kube.sha256_file(payload) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    success = kube.run_command(["python", "-c", "print('ok')"])
    assert success.stdout.strip() == "ok"
    failed = kube.run_command(["python", "-c", "raise SystemExit(3)"], check=False)
    assert failed.returncode == 3
    with pytest.raises(RuntimeError, match="command failed"):
        kube.run_command(["python", "-c", "raise SystemExit(4)"])
    monkeypatch.setattr(kube, "ROOT", tmp_path)


def test_emit_kubectl_and_rollout(tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    probe.kubectl = Mock(return_value=subprocess.CompletedProcess(["kubectl"], 0, "", ""))  # type: ignore[method-assign]

    probe.emit("test_event", value=1)
    probe.wait_rollout("inventory")

    assert probe.events[0]["event_type"] == "test_event"
    probe.kubectl.assert_called_once_with(
        "-n", kube.NAMESPACE, "rollout", "status", "deployment/inventory", "--timeout=120s"
    )


def test_kubectl_delegates_to_run_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    expected = subprocess.CompletedProcess(["kubectl"], 0, "ok", "")
    delegated = Mock(return_value=expected)
    monkeypatch.setattr(kube, "run_command", delegated)

    assert probe.kubectl("get", "pods", check=False) is expected
    delegated.assert_called_once_with(["kubectl", "get", "pods"], check=False)


def test_wait_pods_handles_ready_and_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    ready_payload = {"items": [{"status": {"conditions": [{"type": "Ready", "status": "True"}]}}]}
    probe.kubectl = Mock(return_value=subprocess.CompletedProcess(["kubectl"], 0, json.dumps(ready_payload), ""))  # type: ignore[method-assign]
    clock = iter([0.0, 1.0])
    monkeypatch.setattr(kube.time, "monotonic", lambda: next(clock))
    probe.wait_pods("app=inventory", 1)

    retry = _probe(tmp_path / "retry")
    retry_payload: dict[str, Any] = {"items": [{"status": {"conditions": []}}]}
    retry.kubectl = Mock(  # type: ignore[method-assign]
        side_effect=[
            subprocess.CompletedProcess(["kubectl"], 0, json.dumps(retry_payload), ""),
            subprocess.CompletedProcess(["kubectl"], 0, json.dumps(ready_payload), ""),
        ]
    )
    retry_clock = iter([0.0, 0.0, 1.0, 2.0])
    monkeypatch.setattr(kube.time, "monotonic", lambda: next(retry_clock))
    monkeypatch.setattr(kube.time, "sleep", lambda _seconds: None)
    retry.wait_pods("app=inventory", 1)

    failed = _probe(tmp_path / "failed")
    failed.kubectl = Mock(  # type: ignore[method-assign]
        side_effect=[
            subprocess.CompletedProcess(["kubectl"], 1, "", "error"),
            subprocess.CompletedProcess(["kubectl"], 1, "", "error"),
        ]
    )
    timeout_clock = iter([0.0, 0.0, 200.0])
    monkeypatch.setattr(kube.time, "monotonic", lambda: next(timeout_clock))
    monkeypatch.setattr(kube.time, "sleep", lambda _seconds: None)
    with pytest.raises(RuntimeError, match="expected state"):
        failed.wait_pods("app=inventory", 1)


def test_stop_port_forwards_handles_finished_and_forced_processes(tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    finished = _Process(running=False)
    forced = _Process(timeout_on_wait=True)
    probe.port_forwards = [finished, forced]  # type: ignore[list-item]

    probe.stop_port_forwards()

    assert probe.port_forwards == []
    assert forced.terminated is True
    assert forced.killed is True


def test_start_port_forward_covers_ready_exit_and_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    process = _Process()

    class Socket:
        def __enter__(self) -> Socket:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def connect_ex(self, _address: tuple[str, int]) -> int:
            return 0

    monkeypatch.setattr(kube.subprocess, "Popen", Mock(return_value=process))
    monkeypatch.setattr(kube.socket, "socket", lambda: Socket())
    monkeypatch.setattr(kube.time, "monotonic", lambda: 0.0)
    probe.start_port_forward("inventory", 19081, 8081)
    assert probe.port_forwards == [process]

    exited = _probe(tmp_path / "exited")
    dead = _Process(running=False)
    monkeypatch.setattr(kube.subprocess, "Popen", Mock(return_value=dead))
    with pytest.raises(RuntimeError, match="exited"):
        exited.start_port_forward("inventory", 19081, 8081)

    timeout_probe = _probe(tmp_path / "timeout")
    pending = _Process()
    monkeypatch.setattr(kube.subprocess, "Popen", Mock(return_value=pending))
    monkeypatch.setattr(kube.time, "monotonic", Mock(side_effect=[0.0, 0.0, 30.0]))
    monkeypatch.setattr(kube.socket, "socket", lambda: Socket())
    Socket.connect_ex = lambda self, _address: 1  # type: ignore[method-assign]
    monkeypatch.setattr(kube.time, "sleep", lambda _seconds: None)
    with pytest.raises(RuntimeError, match="did not become ready"):
        timeout_probe.start_port_forward("inventory", 19081, 8081)


def test_request_handles_success_http_error_and_connection_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    probe = _probe(tmp_path)

    class Response:
        status = 200

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"status":"ok"}'

    monkeypatch.setattr(kube.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    assert probe.request(19081, "/healthz", "POST", {"x": 1})[0:2] == (200, {"status": "ok"})
    error = urllib.error.HTTPError("http://probe", 503, "failed", Message(), io.BytesIO(b'{"error":"down"}'))
    monkeypatch.setattr(kube.urllib.request, "urlopen", Mock(side_effect=error))
    assert probe.request(19081, "/healthz")[0:2] == (503, {"error": "down"})
    for exception in (urllib.error.URLError("offline"), TimeoutError(), ConnectionError()):
        monkeypatch.setattr(kube.urllib.request, "urlopen", Mock(side_effect=exception))
        assert probe.request(19081, "/healthz")[0] == 0


def test_capture_service_logs_filters_and_persists_events(tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    valid = {"run_id": probe.run_id, "event_id": "service-1", "timestamp": "2", "event_type": "ok"}
    other = {"run_id": "other", "event_id": "service-2", "timestamp": "1"}
    payload = {
        "items": [
            {"metadata": {"name": "inventory-pod", "labels": {"app": "inventory"}}},
            {"metadata": {"name": "bad"}},
        ]
    }
    logs = subprocess.CompletedProcess(
        ["kubectl"], 0, "not-json\n" + json.dumps(other) + "\n" + json.dumps(valid) + "\n", ""
    )
    probe.kubectl = Mock(  # type: ignore[method-assign]
        side_effect=[
            subprocess.CompletedProcess(["kubectl"], 0, json.dumps(payload), ""),
            subprocess.CompletedProcess(["kubectl"], 1, "", "failed"),
            logs,
        ]
    )

    probe.capture_service_logs()

    assert len(probe.service_events) == 1
    assert json.loads(probe.service_event_file.read_text(encoding="utf-8"))["event_id"] == "service-1"

    unavailable = _probe(tmp_path / "unavailable")
    unavailable.kubectl = Mock(return_value=subprocess.CompletedProcess(["kubectl"], 1, "", "failed"))  # type: ignore[method-assign]
    unavailable.capture_service_logs()
    assert not unavailable.service_event_file.exists()


def test_reset_and_workload_cover_readiness_and_requests(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    probe.stop_port_forwards = Mock()  # type: ignore[method-assign]
    probe.kubectl = Mock(return_value=subprocess.CompletedProcess(["kubectl"], 0, "", ""))  # type: ignore[method-assign]
    probe.wait_rollout = Mock()  # type: ignore[method-assign]
    probe.wait_pods = Mock()  # type: ignore[method-assign]
    probe.start_port_forward = Mock()  # type: ignore[method-assign]
    probe.request = Mock(side_effect=[(200, {}, 0.01), (200, {}, 0.01), (201, {}, 0.01)])  # type: ignore[method-assign]
    monkeypatch.setattr(kube.time, "sleep", lambda _seconds: None)

    probe.reset()
    outcomes = probe.workload(1, "phase")

    assert outcomes[0]["result"] == "success"
    assert probe.start_port_forward.call_count == 2
    assert probe.events[-1]["event_type"] == "workload_response"

    failed = _probe(tmp_path / "not-ready")
    failed.stop_port_forwards = Mock()  # type: ignore[method-assign]
    failed.kubectl = Mock(return_value=subprocess.CompletedProcess(["kubectl"], 0, "", ""))  # type: ignore[method-assign]
    failed.wait_rollout = Mock()  # type: ignore[method-assign]
    failed.wait_pods = Mock()  # type: ignore[method-assign]
    failed.start_port_forward = Mock()  # type: ignore[method-assign]
    failed.request = Mock(return_value=(503, {}, 0.01))  # type: ignore[method-assign]
    clock = iter([0.0, 0.0, 30.0])
    monkeypatch.setattr(kube.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(kube.time, "sleep", lambda _seconds: None)
    with pytest.raises(RuntimeError, match="through port-forward"):
        failed.reset()


def test_version_and_fault_boundaries(tmp_path: Path) -> None:
    probe = _probe(tmp_path)
    probe.kubectl = Mock(return_value=subprocess.CompletedProcess(["kubectl"], 0, "", ""))  # type: ignore[method-assign]
    probe.wait_rollout = Mock()  # type: ignore[method-assign]
    probe.request = Mock(return_value=(200, {}, 0.0))  # type: ignore[method-assign]
    probe.dependency_fault("latency", 3)
    probe.clear_dependency_fault()
    probe.set_order_version("order-api-v2", "deployment_update")
    probe.set_order_version("order-api-v1", "rollback")
    assert probe.events[-1]["event_type"] == "rollback_completed"

    probe.request = Mock(return_value=(503, {}, 0.0))  # type: ignore[method-assign]
    with pytest.raises(RuntimeError, match="apply"):
        probe.dependency_fault("latency")
    with pytest.raises(RuntimeError, match="clear"):
        probe.clear_dependency_fault()


@pytest.mark.parametrize("scenario_type", ["baseline", "service-termination", "dependency-latency"])
def test_execute_covers_all_scenario_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, scenario_type: str) -> None:
    monkeypatch.setattr(kube, "ROOT", tmp_path)
    monkeypatch.setattr(kube, "MANIFEST", tmp_path / "manifest.yaml")
    monkeypatch.setattr(kube, "SCENARIO_DIR", tmp_path / "scenarios")
    monkeypatch.setattr(kube, "sha256_file", lambda _path: "hash")
    monkeypatch.setattr(
        kube, "run_command", Mock(return_value=subprocess.CompletedProcess(["kubectl"], 0, "docker-desktop\n", ""))
    )
    probe = _probe(tmp_path / scenario_type, scenario_type)
    probe.reset = Mock()  # type: ignore[method-assign]
    probe.workload = Mock(return_value=[{"result": "success"}])  # type: ignore[method-assign]
    probe.set_order_version = Mock()  # type: ignore[method-assign]
    probe.dependency_fault = Mock()  # type: ignore[method-assign]
    probe.clear_dependency_fault = Mock()  # type: ignore[method-assign]
    probe.kubectl = Mock()  # type: ignore[method-assign]
    probe.wait_pods = Mock()  # type: ignore[method-assign]
    probe.wait_rollout = Mock()  # type: ignore[method-assign]
    probe.stop_port_forwards = Mock()  # type: ignore[method-assign]
    probe.start_port_forward = Mock()  # type: ignore[method-assign]
    probe.capture_service_logs = Mock()  # type: ignore[method-assign]

    metadata = probe.execute()

    assert metadata["scenario_id"] == f"{scenario_type}-v1"
    assert probe.stop_port_forwards.call_count >= 1


def test_execute_writes_metadata_even_when_scenario_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(kube, "ROOT", tmp_path)
    monkeypatch.setattr(kube, "MANIFEST", tmp_path / "manifest.yaml")
    monkeypatch.setattr(kube, "SCENARIO_DIR", tmp_path / "scenarios")
    monkeypatch.setattr(kube, "sha256_file", lambda _path: "hash")
    probe = _probe(tmp_path / "failure")
    probe.reset = Mock(side_effect=RuntimeError("reset failed"))  # type: ignore[method-assign]
    probe.stop_port_forwards = Mock()  # type: ignore[method-assign]
    with pytest.raises(RuntimeError, match="reset failed"):
        probe.execute()
    assert probe.stop_port_forwards.called
    assert not probe.metadata_file.exists()


def test_validate_run_accepts_and_rejects_bundles(tmp_path: Path) -> None:
    scenario = _scenario("service-termination")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    event = {
        "run_id": "service-termination-v1-run",
        "scenario_id": scenario["scenario_id"],
        "source_component": "inventory",
        "event_type": "reset_completed",
        "timestamp": "1",
        "trace_id": "trace",
        "span_id": "span",
        "target_component": "inventory",
    }
    (run_dir / "events.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    (run_dir / "metadata.json").write_text("{}\n", encoding="utf-8")
    result = validate_run(run_dir, scenario)
    assert result["passed"] is False
    assert "run_started" in result["missing_event_types"]
    assert kube.scenario_paths()[0].name == "no-fault.json"


def test_validate_run_accepts_complete_service_bundle(tmp_path: Path) -> None:
    scenario = _scenario("service-termination")
    run_dir = tmp_path / "complete"
    run_dir.mkdir()
    events = [
        {
            "run_id": scenario["scenario_id"],
            "scenario_id": scenario["scenario_id"],
            "source_component": "inventory",
            "event_type": event_type,
            "timestamp": "1",
            "trace_id": "trace",
            "span_id": "span",
            "target_component": "inventory",
        }
        for event_type in ("run_started", "reset_completed", "clean_state_verified", "run_completed")
    ]
    (run_dir / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
    (run_dir / "metadata.json").write_text("{}\n", encoding="utf-8")

    assert validate_run(run_dir, scenario)["passed"] is True


def test_execute_rejects_unsupported_scenario(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(kube, "ROOT", tmp_path)
    monkeypatch.setattr(kube, "MANIFEST", tmp_path / "manifest.yaml")
    monkeypatch.setattr(kube, "SCENARIO_DIR", tmp_path / "scenarios")
    monkeypatch.setattr(kube, "sha256_file", lambda _path: "hash")
    probe = _probe(tmp_path / "unsupported", "unsupported")
    probe.reset = Mock()  # type: ignore[method-assign]
    probe.stop_port_forwards = Mock()  # type: ignore[method-assign]

    with pytest.raises(ValueError, match="unsupported scenario"):
        probe.execute()


def test_main_success_failure_and_exception_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    scenario_paths = []
    for index in range(4):
        path = tmp_path / f"scenario-{index}.json"
        path.write_text(json.dumps(_scenario("baseline")), encoding="utf-8")
        scenario_paths.append(path)
    monkeypatch.setattr(kube, "scenario_paths", lambda: scenario_paths)
    monkeypatch.setattr(kube.shutil, "which", lambda _tool: "/usr/bin/tool")
    monkeypatch.setattr(kube, "run_command", Mock(return_value=subprocess.CompletedProcess(["kubectl"], 0, "", "")))

    class FakeProbe:
        counter = 0

        def __init__(self, scenario: dict[str, Any], output_root: Path, repeat_of: str | None = None) -> None:
            FakeProbe.counter += 1
            self.run_id = f"run-{FakeProbe.counter}"
            self.run_dir = output_root / self.run_id
            self.scenario = scenario
            self.run_dir.mkdir(parents=True, exist_ok=True)

        def execute(self) -> dict[str, Any]:
            return {"run_id": self.run_id}

        def stop_port_forwards(self) -> None:
            return None

        def emit(self, *_args: object, **_kwargs: object) -> None:
            return None

    monkeypatch.setattr(kube, "KubernetesProbe", FakeProbe)
    monkeypatch.setattr(kube, "validate_run", lambda *_args: {"passed": True})
    monkeypatch.setattr(
        "sys.argv", ["kubernetes_fit_probe", "--output-root", str(tmp_path / "raw"), "--keep-namespace"]
    )
    assert kube.main() == 0

    monkeypatch.setattr(kube, "validate_run", lambda *_args: {"passed": False})
    monkeypatch.setattr("sys.argv", ["kubernetes_fit_probe", "--output-root", str(tmp_path / "raw-failed")])
    assert kube.main() == 1

    class ErrorProbe(FakeProbe):
        def execute(self) -> dict[str, Any]:
            raise RuntimeError("probe failed")

    monkeypatch.setattr(kube, "KubernetesProbe", ErrorProbe)
    monkeypatch.setattr("sys.argv", ["kubernetes_fit_probe", "--output-root", str(tmp_path / "raw-error")])
    assert kube.main() == 1


def test_main_returns_two_when_kubernetes_tools_are_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(kube.shutil, "which", lambda _tool: None)
    monkeypatch.setattr("sys.argv", ["kubernetes_fit_probe", "--output-root", str(tmp_path / "raw")])

    assert kube.main() == 2
