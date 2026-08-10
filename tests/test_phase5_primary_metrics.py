from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "analysis" / "phase_5" / "phase_5_primary_metrics.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase_5_primary_metrics", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event(
    event_id: str,
    event_type: str,
    monotonic_ns: int | None = None,
    **fields: Any,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "event_id": event_id,
        "event_type": event_type,
        "timestamp": "2026-08-10T15:00:00.000Z",
        **fields,
    }
    if monotonic_ns is not None:
        record["monotonic_ns"] = monotonic_ns
    return record


def test_primary_duration_uses_monotonic_not_utc() -> None:
    module = load_module()
    events = [
        event(
            "start",
            "injection_started",
            1_000_000_000,
            timestamp="2026-08-10T15:00:10.000Z",
        ),
        event(
            "end",
            "fault_detected",
            1_125_500_000,
            timestamp="2026-08-10T15:00:10.999Z",
        ),
    ]

    result = module.duration_metric(
        events,
        "injection_started",
        "fault_detected",
    )

    assert result["status"] == "observed"
    assert result["value"] == 125.5


def test_primary_duration_refuses_utc_fallback() -> None:
    module = load_module()
    events = [
        event(
            "start",
            "injection_started",
            timestamp="2026-08-10T15:00:00.000Z",
        ),
        event(
            "end",
            "fault_detected",
            2_000_000_000,
            timestamp="2026-08-10T15:00:00.100Z",
        ),
    ]

    result = module.duration_metric(
        events,
        "injection_started",
        "fault_detected",
    )

    assert result["status"] == "missing"
    assert result["value"] is None
    assert "invalid_monotonic_ns_injection_started" in result["reason"]


def test_primary_duration_rejects_negative_monotonic_delta() -> None:
    module = load_module()
    events = [
        event("start", "injection_started", 2_000_000_000),
        event("end", "fault_detected", 1_000_000_000),
    ]

    result = module.duration_metric(
        events,
        "injection_started",
        "fault_detected",
    )

    assert result["status"] == "missing"
    assert "negative monotonic duration" in result["reason"]


def test_failure_impact_uses_half_open_monotonic_interval() -> None:
    module = load_module()
    events = [
        event("inject", "injection_started", 100),
        event(
            "request-before",
            "workload_request",
            99,
            order_id="before",
            request_index=2,
        ),
        event(
            "response-before",
            "workload_response",
            101,
            order_id="before",
            request_index=2,
            status=502,
        ),
        event(
            "request-a",
            "workload_request",
            100,
            order_id="a",
            request_index=3,
        ),
        event(
            "response-a",
            "workload_response",
            120,
            order_id="a",
            request_index=3,
            status=502,
        ),
        event(
            "request-b",
            "workload_request",
            150,
            order_id="b",
            request_index=4,
        ),
        event(
            "response-b",
            "workload_response",
            170,
            order_id="b",
            request_index=4,
            status=201,
        ),
        event(
            "request-at-end",
            "workload_request",
            200,
            order_id="end",
            request_index=5,
        ),
        event(
            "response-at-end",
            "workload_response",
            210,
            order_id="end",
            request_index=5,
            status=502,
        ),
        event("end", "injection_ended", 200),
    ]

    result = module.derive_failure_impact(events)

    assert result["status"] == "observed"
    assert result["failed_requests"] == 1
    assert result["offered_requests"] == 2
    assert result["unresolved_requests"] == 0
    assert result["value"] == 0.5


def test_failure_impact_refuses_request_without_monotonic_time() -> None:
    module = load_module()
    events = [
        event("inject", "injection_started", 100),
        event(
            "request-a",
            "workload_request",
            None,
            order_id="a",
            request_index=3,
        ),
        event("end", "injection_ended", 200),
    ]

    result = module.derive_failure_impact(events)

    assert result["status"] == "missing"
    assert result["reason"] == "invalid_monotonic_ns_workload_request"


def test_no_fault_metrics_are_not_applicable() -> None:
    module = load_module()
    assert module.not_applicable("no_fault_control") == {
        "value": None,
        "status": "not_applicable",
        "source_event_ids": [],
        "reason": "no_fault_control",
    }


def test_primary_identity_rejects_development_or_unbound_trial() -> None:
    module = load_module()
    validity = {
        "evidence_boundary": "technical-pilot-only",
        "pilot_batch_id": "batch-a",
        "primary_schedule_slot": 1,
    }
    manifest = {
        "manifest_type": "phase-5-development-trial-manifest",
        "evidence_boundary": "phase-5-implementation-feasibility-only",
        "manifest_version": "1.1.0",
        "controller_version": "phase-5-single-trial-controller-v0.2",
        "pilot_batch_id": None,
        "primary_schedule_slot": None,
        "repetition": 0,
        "run_order": 0,
    }

    try:
        module.validate_primary_identity(manifest, validity)
    except ValueError as exc:
        assert "not a Phase 5 primary trial manifest" in str(exc)
    else:
        raise AssertionError("development manifest was accepted as primary")


def test_primary_identity_accepts_fully_bound_trial() -> None:
    module = load_module()
    manifest = {
        "manifest_type": "phase-5-primary-trial-manifest",
        "evidence_boundary": "technical-pilot-only",
        "manifest_version": "1.1.0",
        "controller_version": "phase-5-single-trial-controller-v0.2",
        "pilot_batch_id": "phase5-primary-batch-test",
        "primary_schedule_slot": 7,
        "repetition": 2,
        "run_order": 7,
    }
    validity = {
        "evidence_boundary": "technical-pilot-only",
        "pilot_batch_id": "phase5-primary-batch-test",
        "primary_schedule_slot": 7,
    }

    module.validate_primary_identity(manifest, validity)


def test_measurement_quality_reports_no_utc_fallback() -> None:
    module = load_module()
    events = [
        event("trial", "trial_started", 100),
        event("reset-start", "reset_started", 110),
        event("clean", "clean_state_verified", 120),
        event("reset-end", "reset_completed", 130),
        event("workload", "workload_started", 140),
        event(
            "request",
            "workload_request",
            None,
            order_id="a",
            request_index=1,
        ),
        event(
            "response",
            "workload_response",
            160,
            order_id="a",
            request_index=1,
            status=201,
        ),
        event("workload-end", "workload_completed", 170),
        event("observation", "observation_verified", 180),
        event("otel", "otel_observation_verified", 190),
        event("cleanup", "cleanup_completed", 200),
        event("completed", "trial_completed", 210),
    ]

    quality = module.measurement_quality(
        "no-fault-v1",
        events,
        {"passed": True, "classification": "valid-primary-pilot-trial"},
    )

    assert quality["utc_fallback_permitted"] is False
    assert quality["primary_duration_clock"] == "controller-monotonic-ns"
    assert quality["primary_monotonic_completeness"] < 1.0
    assert quality["primary_monotonic_invalid_event_ids"] == ["request"]


def test_primary_tool_source_does_not_reference_development_metric_tool() -> None:
    source = MODULE.read_text(encoding="utf-8")

    assert "phase_5_metrics import" not in source
    assert "utc_fallback_permitted" in source
    assert "controller_monotonic_ns" in source
