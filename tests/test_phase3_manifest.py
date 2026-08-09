"""Validation tests for the locked Phase 3 design manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "experiments" / "manifests" / "phase-3-trial-manifest.json"


def load_manifest() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))


def test_phase3_manifest_has_locked_design_and_expected_allocation() -> None:
    manifest = load_manifest()

    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["design_status"] == "locked-for-implementation"
    assert manifest["replication_plan"]["planned_valid_trials"] == 50
    assert manifest["replication_plan"]["planned_maximum_trial_slots"] == 60


def test_phase3_manifest_crosses_faults_with_recovery_conditions() -> None:
    manifest = load_manifest()

    assert [condition["condition_id"] for condition in manifest["conditions"]] == ["manual", "automated"]
    cells = manifest["replication_plan"]["fault_cells"]
    assert {cell["scenario_id"] for cell in cells} == {
        "service-termination-v1",
        "dependency-latency-v1",
    }
    assert all(cell["condition_ids"] == ["manual", "automated"] for cell in cells)


def test_fault_scenarios_have_detection_recovery_and_validity_contract() -> None:
    manifest = load_manifest()
    fault_scenarios = [scenario for scenario in manifest["scenarios"] if scenario["role"] == "fault-comparison"]

    for scenario in fault_scenarios:
        required = set(scenario["required_events"])
        assert {"injection_started", "fault_detected", "recovery_started"}.issubset(required)
        assert {"recovery_completed", "post_recovery_check", "cleanup_completed"}.issubset(required)
        assert scenario["detection_rule"]["version"] == "detection-v1"
        assert scenario["recovery_action"]["manual"] == scenario["recovery_action"]["automated"]
