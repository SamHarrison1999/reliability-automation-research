from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"
CONTRACT = ROOT / "data" / "schemas" / "phase-5-pilot-batch-contract.md"


def load_manifest() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(MANIFEST.read_text(encoding="utf-8")))


def test_phase5_manifest_identity_and_target() -> None:
    manifest = load_manifest()

    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["manifest_type"] == "phase-5-technical-pilot-manifest"
    assert manifest["protocol_id"] == "phase-5-technical-pilot-v1"
    assert manifest["design_status"] == "locked-for-implementation"
    assert manifest["evidence_boundary"] == "technical-pilot-only"

    assert manifest["target"]["execution_context"] == "docker-desktop-kubernetes"
    assert manifest["target"]["kubernetes_context"] == "docker-desktop"
    assert manifest["target"]["topology"] == ["order-api", "inventory"]


def test_phase5_manifest_locks_five_cells_and_50_plus_10_allocation() -> None:
    manifest = load_manifest()
    cells = {cell["cell_id"]: cell for cell in manifest["pilot_cells"]}

    assert set(cells) == {
        "no-fault-control",
        "service-termination-manual",
        "service-termination-automated",
        "dependency-latency-manual",
        "dependency-latency-automated",
    }
    assert all(cell["valid_repetitions"] == 10 for cell in cells.values())
    assert all(cell["reserve_slots"] == 2 for cell in cells.values())

    assert manifest["allocation"] == {
        "planned_valid_trials": 50,
        "primary_slots": 50,
        "reserve_slots": 10,
        "maximum_attempted_slots": 60,
        "interpretation": ("Pilot/feasibility allocation inherited from Phase 3; not a statistical power calculation."),
    }


def test_phase5_service_termination_avoids_kubernetes_self_healing_confound() -> None:
    manifest = load_manifest()
    scenario = manifest["scenarios"]["service-termination-v1"]

    assert scenario["fault"]["mode"] == "deployment-scale-zero"
    assert scenario["fault"]["apply_action"] == {
        "action_id": "scale-inventory-zero-v1",
        "kind": "kubernetes-scale",
        "deployment": "inventory",
        "replicas": 0,
    }
    assert scenario["recovery_action"]["action_id"] == "scale-inventory-one-v1"
    assert scenario["recovery_action"]["replicas"] == 1
    assert scenario["detection_rule"]["readiness_short_circuit"] is False


def test_phase5_latency_uses_existing_inventory_control_boundary() -> None:
    manifest = load_manifest()
    scenario = manifest["scenarios"]["dependency-latency-v1"]

    assert scenario["fault"]["latency_ms"] == 120
    assert scenario["fault"]["apply_action"]["path"] == "/__control"
    assert scenario["fault"]["apply_action"]["payload"] == {
        "mode": "latency",
        "latency_ms": 120,
    }
    assert scenario["detection_rule"]["threshold_ms"] == 100
    assert scenario["recovery_action"]["payload"] == {"mode": "none"}


def test_phase5_no_fault_control_does_not_add_rollback_treatment() -> None:
    manifest = load_manifest()
    control = manifest["scenarios"]["no-fault-v1"]

    assert control["role"] == "quality-control"
    assert control["fault"] is None
    assert control["condition_ids"] == ["control"]
    assert "rollback-treatment" in control["explicit_exclusions"]
    assert "deployment-transition-treatment" in control["explicit_exclusions"]


def test_phase5_treatment_and_analysis_boundaries_are_explicit() -> None:
    manifest = load_manifest()

    assert manifest["conditions"]["manual"]["artificial_operator_delay_ms"] == 0
    assert manifest["treatment_invariants"] == {
        "same_detector_across_conditions": True,
        "same_recovery_action_across_conditions": True,
        "same_fault_across_conditions": True,
        "same_workload_across_conditions": True,
        "same_environment_across_conditions": True,
        "only_planned_difference": "recovery-initiator-control-path",
    }
    assert manifest["analysis_boundary"]["confirmatory_inference"] is False
    assert manifest["analysis_boundary"]["p_values"] is False
    assert manifest["analysis_boundary"]["detection_latency_interpretation"] == ("shared-detector-fidelity-and-balance")


def test_phase5_reserve_slots_are_not_primary_schedule_slots() -> None:
    manifest = load_manifest()

    assert manifest["run_order"]["primary_order_contains_reserve_slots"] is False
    assert manifest["reserve_policy"]["activation"] == "only_after_invalid_attempt_in_same_cell"
    assert manifest["reserve_policy"]["source_invalid_trial_id_required"] is True
    assert manifest["reserve_policy"]["invalid_trial_preservation_required"] is True


def test_phase5_batch_contract_documents_immutable_boundaries() -> None:
    text = CONTRACT.read_text(encoding="utf-8")

    for required in (
        "pilot design manifest",
        "primary run-order file",
        "batch manifest",
        "byte-identical canonical",
        "Reserve activation cannot modify the 50-slot primary run-order file",
        "does not start the Phase 5 technical pilot",
    ):
        assert required in text
