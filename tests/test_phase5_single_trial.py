from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "experiments" / "harness" / "phase_5_single_trial.py"
PILOT_MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase_5_single_trial", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(PILOT_MANIFEST.read_text(encoding="utf-8")))


def test_development_guard_rejects_primary_or_invalid_condition_selection() -> None:
    module = load_module()

    with pytest.raises(ValueError, match="development-validation"):
        module.validate_development_selection("no-fault-v1", "control", False)
    with pytest.raises(ValueError, match="condition=control"):
        module.validate_development_selection("no-fault-v1", "manual", True)
    with pytest.raises(ValueError, match="manual or condition=automated"):
        module.validate_development_selection("service-termination-v1", "control", True)
    with pytest.raises(ValueError, match="unsupported"):
        module.validate_development_selection("unknown", "control", True)

    module.validate_development_selection("no-fault-v1", "control", True)
    module.validate_development_selection("service-termination-v1", "manual", True)
    module.validate_development_selection("dependency-latency-v1", "automated", True)


def test_canonical_recovery_action_is_scenario_level_not_condition_specific() -> None:
    module = load_module()
    manifest = load_manifest()

    termination = module.canonical_recovery_action(manifest, "service-termination-v1")
    latency = module.canonical_recovery_action(manifest, "dependency-latency-v1")

    assert termination["action_id"] == "scale-inventory-one-v1"
    assert termination["replicas"] == 1
    assert latency["action_id"] == "clear-inventory-fault-v1"
    assert latency["payload"] == {"mode": "none"}
    assert module.sha256_json(termination) == module.sha256_json(
        manifest["scenarios"]["service-termination-v1"]["recovery_action"]
    )


def test_canonical_recovery_action_rejects_no_fault_control() -> None:
    module = load_module()

    with pytest.raises(ValueError, match="no recovery action"):
        module.canonical_recovery_action(load_manifest(), "no-fault-v1")


def test_development_trial_manifest_never_claims_batch_or_primary_slot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    trial = module.Phase5DevelopmentTrial("service-termination-v1", "manual", tmp_path, True)
    trial.run_dir.mkdir(parents=True)

    monkeypatch.setattr(
        module,
        "run_command",
        lambda args, check=True: subprocess.CompletedProcess(args, 0, stdout="abc123\n", stderr=""),
    )
    trial.materialise_trial_manifest()

    payload = json.loads(trial.trial_manifest_file.read_text(encoding="utf-8"))
    assert payload["evidence_boundary"] == "phase-5-implementation-feasibility-only"
    assert payload["primary_schedule_slot"] is None
    assert payload["pilot_batch_id"] is None
    assert payload["reserve"] is False
    assert payload["repetition"] == 0
    assert payload["run_order"] == 0
    assert payload["canonical_recovery_action_sha256"] == module.sha256_json(
        load_manifest()["scenarios"]["service-termination-v1"]["recovery_action"]
    )


def test_workload_request_records_controller_boundaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    trial = module.Phase5DevelopmentTrial("dependency-latency-v1", "manual", tmp_path, True)
    trial.run_dir.mkdir(parents=True)

    monkeypatch.setattr(
        trial,
        "request",
        lambda port, path, method="GET", body=None, timeout=3.0: (
            201,
            {"status": "accepted", "order_id": body["order_id"] if body else ""},
            0.123,
        ),
    )
    record = trial.workload_request("during-fault", 3)

    assert record["request_index"] == 3
    assert record["status"] == 201
    assert record["latency_ms"] == 123.0
    assert record["request_event_id"].startswith("phase5-controller-")
    assert record["response_event_id"].startswith("phase5-controller-")
    assert [event["event_type"] for event in trial.events] == [
        "workload_request",
        "workload_response",
    ]


def test_shared_latency_detector_requires_three_consecutive_observations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    trial = module.Phase5DevelopmentTrial("dependency-latency-v1", "automated", tmp_path, True)
    trial.run_dir.mkdir(parents=True)

    responses = iter([121.0, 130.0, 140.0])

    def fake_workload(phase: str, request_index: int) -> dict[str, Any]:
        latency = next(responses)
        response_event = trial.emit(
            "workload_response",
            phase=phase,
            request_index=request_index,
            order_id=f"order-{request_index}",
            status=201,
            latency_ms=latency,
        )
        return {
            "request_index": request_index,
            "status": 201,
            "latency_ms": latency,
            "response_event_id": response_event["event_id"],
        }

    monkeypatch.setattr(trial, "workload_request", fake_workload)
    next_index = trial.detect_fault(3)

    assert next_index == 6
    assert sum(event["event_type"] == "detection_evaluation" for event in trial.events) == 3
    detected = [event for event in trial.events if event["event_type"] == "fault_detected"]
    assert len(detected) == 1
    assert detected[0]["detection_rule_id"] == "three-orders-over-100ms-v1"


def test_recovery_initiator_paths_share_same_canonical_action_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    manifest = load_manifest()
    expected_hash = module.sha256_json(manifest["scenarios"]["dependency-latency-v1"]["recovery_action"])

    hashes: dict[str, str] = {}
    for condition in ("manual", "automated"):
        trial = module.Phase5DevelopmentTrial("dependency-latency-v1", condition, tmp_path / condition, True)
        trial.run_dir.mkdir(parents=True)
        trial.recovery_action_hash = expected_hash
        monkeypatch.setattr(
            trial,
            "request",
            lambda port, path, method="GET", body=None, timeout=3.0: (
                200,
                {"mode": "none"},
                0.001,
            ),
        )
        trial.recover()
        recovery = [event for event in trial.events if event["event_type"] == "recovery_started"][0]
        hashes[condition] = recovery["canonical_recovery_action_sha256"]

        event_types = {event["event_type"] for event in trial.events}
        if condition == "manual":
            assert "external_intervention" in event_types
            assert "automation_evaluation" not in event_types
        else:
            assert "automation_evaluation" in event_types
            assert "external_intervention" not in event_types

    assert hashes == {"manual": expected_hash, "automated": expected_hash}


def test_validity_labels_output_as_development_feasibility_not_pilot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    trial = module.Phase5DevelopmentTrial("no-fault-v1", "control", tmp_path, True)
    trial.run_dir.mkdir(parents=True)
    trial.trial_manifest_file.write_text("{}\n", encoding="utf-8")
    trial.metadata_file.write_text("{}\n", encoding="utf-8")
    trial.image_records = {
        service: {"tag": service, "image_id": "sha256:test"} for service in ("inventory", "order-api", "telemetry-sink")
    }
    trial.node_image_records = {
        service: {"reference": service, "digest": "sha256:test"}
        for service in ("inventory", "order-api", "telemetry-sink", "otel-collector")
    }
    for event_type in (
        "preflight_completed",
        "source_tree_verified",
        "deployment_completed",
        "readiness_verified",
        "version_verified",
        "workload_completed",
        "observation_verified",
        "otel_observation_verified",
    ):
        trial.emit(event_type)
    trial.emit("clean_state_verified", stage="before_deploy", namespace_present=False)
    trial.emit("clean_state_verified", stage="after_cleanup", namespace_present=False)

    validity = trial.write_validity()

    assert validity["evidence_boundary"] == "phase-5-implementation-feasibility-only"
    assert validity["pilot_batch_id"] is None
    assert validity["primary_schedule_slot"] is None
    assert validity["checks"]["development_guard"] is True
    assert validity["checks"]["primary_schedule_not_consumed"] is True
    assert validity["passed"] is True


def test_cleanup_deletes_namespace_even_when_fault_restoration_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    trial = module.Phase5DevelopmentTrial("service-termination-v1", "manual", tmp_path, True)
    trial.run_dir.mkdir(parents=True)

    def fail_restore() -> None:
        raise RuntimeError("restore failed")

    commands: list[tuple[str, ...]] = []

    def fake_kubectl(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        commands.append(args)
        if args[:2] == ("get", "namespace"):
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="not found")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(trial, "verify_fault_clean_for_cleanup", fail_restore)
    monkeypatch.setattr(trial, "capture_service_logs", lambda stage: None)
    monkeypatch.setattr(trial, "stop_all_port_forwards", lambda: None)
    monkeypatch.setattr(trial, "kubectl", fake_kubectl)

    with pytest.raises(
        RuntimeError,
        match="fault-state cleanup failed before verified namespace removal",
    ):
        trial.cleanup()

    assert any(args[:2] == ("delete", "namespace") for args in commands)
    assert any(
        event["event_type"] == "clean_state_verified"
        and event.get("stage") == "after_cleanup"
        and event.get("namespace_present") is False
        for event in trial.events
    )
    assert any(
        event["event_type"] == "cleanup_completed" and event.get("result") == "clean-with-pre-teardown-error"
        for event in trial.events
    )
