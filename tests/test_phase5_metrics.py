from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis" / "phase_5" / "phase_5_metrics.py"
INDEX = ROOT / "experiments" / "manifests" / "phase-5-development-validation-index.json"
RAW_ROOT = ROOT / "results" / "phase-5" / "development" / "raw"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase_5_metrics", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event(
    event_id: str,
    event_type: str,
    timestamp: str,
    **fields: Any,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "timestamp": timestamp,
        **fields,
    }


def test_type7_percentile_and_p95_minimum_count() -> None:
    module = load_module()

    assert module.percentile_type7([1.0, 2.0, 3.0, 4.0], 0.25) == 1.75
    assert module.percentile_type7([1.0, 2.0, 3.0, 4.0], 0.75) == 3.25

    short = module.latency_summary([10.0, 20.0, 30.0])
    assert short["p50_ms"] == 20.0
    assert short["p95_ms"] is None
    assert short["p95_status"] == "insufficient_count"

    eligible = module.latency_summary([10.0, 20.0, 30.0, 40.0, 50.0])
    assert eligible["p95_status"] == "observed"
    assert eligible["p95_ms"] == 48.0


def test_duration_metric_does_not_impute_missing_or_duplicate_boundary() -> None:
    module = load_module()
    events = [
        event("start", "injection_started", "2026-08-10T10:00:00.000Z"),
        event("end", "fault_detected", "2026-08-10T10:00:00.125Z"),
    ]

    observed = module.duration_metric(events, "injection_started", "fault_detected")
    assert observed["status"] == "observed"
    assert observed["value"] == 125.0

    missing = module.duration_metric(events[:1], "injection_started", "fault_detected")
    assert missing["status"] == "missing"
    assert "missing_fault_detected" in missing["reason"]

    duplicate = module.duration_metric(
        [events[0], dict(events[0], event_id="start-2"), events[1]],
        "injection_started",
        "fault_detected",
    )
    assert duplicate["status"] == "missing"
    assert "duplicate_injection_started" in duplicate["reason"]


def test_failure_impact_uses_request_timestamps_not_phase_labels() -> None:
    module = load_module()
    events = [
        event("inject", "injection_started", "2026-08-10T10:00:00.100Z"),
        event(
            "request-1",
            "workload_request",
            "2026-08-10T10:00:00.110Z",
            order_id="a",
            request_index=3,
            phase="misleading-label",
        ),
        event(
            "response-1",
            "workload_response",
            "2026-08-10T10:00:00.120Z",
            order_id="a",
            request_index=3,
            status=502,
        ),
        event(
            "request-2",
            "workload_request",
            "2026-08-10T10:00:00.130Z",
            order_id="b",
            request_index=4,
        ),
        event(
            "response-2",
            "workload_response",
            "2026-08-10T10:00:00.140Z",
            order_id="b",
            request_index=4,
            status=201,
        ),
        event("end", "injection_ended", "2026-08-10T10:00:00.200Z"),
    ]

    result = module.derive_failure_impact(events)

    assert result["status"] == "observed"
    assert result["failed_requests"] == 1
    assert result["offered_requests"] == 2
    assert result["unresolved_requests"] == 0
    assert result["value"] == 0.5


def test_failure_impact_marks_unresolved_request_missing() -> None:
    module = load_module()
    events = [
        event("inject", "injection_started", "2026-08-10T10:00:00.100Z"),
        event(
            "request-1",
            "workload_request",
            "2026-08-10T10:00:00.110Z",
            order_id="a",
            request_index=3,
        ),
        event("end", "injection_ended", "2026-08-10T10:00:00.200Z"),
    ]

    result = module.derive_failure_impact(events)

    assert result["status"] == "missing"
    assert result["offered_requests"] == 1
    assert result["unresolved_requests"] == 1
    assert result["value"] is None


def test_no_fault_primary_metrics_are_not_applicable_in_committed_evidence() -> None:
    module = load_module()
    index = module.load_json(INDEX)
    no_fault = next(entry for entry in index["runs"] if entry["scenario_id"] == "no-fault-v1")

    observation = module.derive_observation(
        RAW_ROOT / no_fault["trial_id"],
        no_fault,
    )

    assert observation["eligible_for_primary_pilot_analysis"] is False
    for metric_id in (
        "detection_latency_ms",
        "recovery_time_ms",
        "failure_impact_rate",
    ):
        assert observation["primary_metrics"][metric_id]["status"] == "not_applicable"
        assert observation["primary_metrics"][metric_id]["value"] is None


def test_committed_development_evidence_derives_exact_five_cells() -> None:
    module = load_module()

    processed, summary = module.build_development_outputs(
        module.load_json(INDEX),
        RAW_ROOT,
    )

    assert processed["observation_count"] == 5
    assert processed["eligible_for_primary_pilot_analysis"] is False
    assert summary["development_run_count"] == 5
    assert summary["descriptive_only"] is True
    assert summary["confirmatory_inference"] is False
    assert summary["p_values_included"] is False
    assert summary["conditions_pooled"] is False

    cells = {
        (observation["scenario_id"], observation["automation_condition"]) for observation in processed["observations"]
    }
    assert cells == {
        ("no-fault-v1", "control"),
        ("dependency-latency-v1", "manual"),
        ("dependency-latency-v1", "automated"),
        ("service-termination-v1", "manual"),
        ("service-termination-v1", "automated"),
    }


def test_committed_fault_observations_retain_primary_boundaries_and_counts() -> None:
    module = load_module()
    processed, _ = module.build_development_outputs(
        module.load_json(INDEX),
        RAW_ROOT,
    )

    fault_observations = [
        observation for observation in processed["observations"] if observation["scenario_id"] != "no-fault-v1"
    ]
    assert len(fault_observations) == 4

    for observation in fault_observations:
        assert observation["primary_metrics"]["detection_latency_ms"]["status"] == "observed"
        assert observation["primary_metrics"]["recovery_time_ms"]["status"] == "observed"
        failure = observation["primary_metrics"]["failure_impact_rate"]
        assert failure["status"] == "observed"
        assert failure["offered_requests"] == 3
        assert observation["secondary_metrics"]["recovery_success"]["value"] == 1
        assert observation["measurement_quality"]["trial_valid"] is True
        assert observation["measurement_quality"]["contamination_detected"] is False


def test_deterministic_write_is_byte_identical(tmp_path: Path) -> None:
    module = load_module()
    payload = {"b": [2, 1], "a": {"x": True}}
    output = tmp_path / "result.json"

    module.write_deterministic(output, payload)
    first = output.read_bytes()
    module.write_deterministic(output, payload)
    second = output.read_bytes()

    assert first == second
    assert first.endswith(b"\n")
