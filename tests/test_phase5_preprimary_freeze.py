from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"
CONTROLLER = ROOT / "experiments" / "harness" / "phase_5_single_trial.py"
PROTOCOL = ROOT / "docs" / "protocols" / "phase-5-technical-pilot.md"
METRICS = ROOT / "docs" / "metrics" / "phase-5-technical-metrics.md"


def test_preprimary_manifest_freezes_numeric_detection_window() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["manifest_version"] == "1.1.0"
    assert manifest["shared_workload"]["detection_window_request_count"] == 3

    for scenario_id in (
        "dependency-latency-v1",
        "service-termination-v1",
    ):
        assert manifest["scenarios"][scenario_id]["detection_rule"]["detection_window_request_count"] == 3


def test_preprimary_manifest_freezes_primary_timing_authority() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    timing = manifest["timing_authority"]

    assert timing["timing_contract_version"] == "phase-5-primary-timing-v1"
    assert timing["audit_clock_field"] == "timestamp"
    assert timing["duration_clock_field"] == "monotonic_ns"
    assert timing["duration_clock_scope"] == "single-controller-process"
    assert timing["primary_duration_clock_required"] is True
    assert timing["opentelemetry_primary_duration_source"] is False
    assert timing["fault_interval_start_event"] == "injection_started"
    assert timing["fault_interval_start_semantics"] == ("after-positive-fault-verification")
    assert timing["recovery_completion_event"] == "recovery_completed"


def test_controller_emits_monotonic_clock_on_every_controller_event() -> None:
    source = CONTROLLER.read_text(encoding="utf-8")

    assert 'CONTROLLER_VERSION = "phase-5-single-trial-controller-v0.2"' in source
    assert '"timestamp": utc_now(),' in source
    assert '"monotonic_ns": time.monotonic_ns(),' in source

    timestamp_position = source.index('"timestamp": utc_now(),')
    monotonic_position = source.index('"monotonic_ns": time.monotonic_ns(),')
    assert monotonic_position > timestamp_position


def test_protocol_and_metric_contract_record_preprimary_correction() -> None:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    metrics = METRICS.read_text(encoding="utf-8")

    assert "detection_window_request_count" in protocol
    assert "`monotonic_ns`" in protocol
    assert "UTC MUST NOT substitute" in protocol
    assert "`recovery_action_completed` and `injection_ended`" in protocol

    assert "controller `monotonic_ns` is the authoritative" in metrics
    assert "UTC MUST NOT be used as a" in metrics
    assert "phase-5-metric-derivation-v1.0" in metrics
    assert "OpenTelemetry is corroborative only" in metrics
