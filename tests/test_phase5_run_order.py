from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "experiments" / "harness" / "phase_5_run_order.py"
MANIFEST_PATH = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase_5_run_order", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))


def test_primary_run_order_has_exact_allocation_and_cell_repetitions() -> None:
    module = load_module()
    manifest = load_manifest()

    slots = module.build_primary_run_order(manifest)

    assert len(slots) == 50
    assert [slot["schedule_slot"] for slot in slots] == list(range(1, 51))
    assert not any(slot["reserve"] for slot in slots)

    counts = Counter(slot["cell_id"] for slot in slots)
    assert counts == {
        "no-fault-control": 10,
        "service-termination-manual": 10,
        "service-termination-automated": 10,
        "dependency-latency-manual": 10,
        "dependency-latency-automated": 10,
    }

    for cell_id in counts:
        repetitions = [slot["repetition"] for slot in slots if slot["cell_id"] == cell_id]
        assert repetitions == list(range(1, 11))


def test_every_cycle_contains_all_five_cells_once() -> None:
    module = load_module()
    slots = module.build_primary_run_order(load_manifest())

    expected = {
        "no-fault-control",
        "service-termination-manual",
        "service-termination-automated",
        "dependency-latency-manual",
        "dependency-latency-automated",
    }
    for cycle in range(1, 11):
        cycle_slots = [slot for slot in slots if slot["cycle"] == cycle]
        assert len(cycle_slots) == 5
        assert {slot["cell_id"] for slot in cycle_slots} == expected
        assert {slot["cycle_position"] for slot in cycle_slots} == set(range(1, 6))


def test_counterbalancing_constraints_are_exact() -> None:
    module = load_module()
    slots = module.build_primary_run_order(load_manifest())
    summary = module.balance_summary(slots)

    assert summary["no_fault_position_counts"] == {
        "1": 2,
        "2": 2,
        "3": 2,
        "4": 2,
        "5": 2,
    }
    assert summary["fault_scenario_first_counts"] == {
        "service-termination-v1": 5,
        "dependency-latency-v1": 5,
    }
    assert summary["condition_first_counts"] == {
        "service-termination-v1": {"manual": 5, "automated": 5},
        "dependency-latency-v1": {"manual": 5, "automated": 5},
    }


def test_run_order_is_deterministic_and_timestamp_free() -> None:
    module = load_module()
    manifest = load_manifest()

    first = module.build_run_order_payload(MANIFEST_PATH, manifest)
    second = module.build_run_order_payload(MANIFEST_PATH, manifest)

    assert module.canonical_json_bytes(first) == module.canonical_json_bytes(second)
    assert first == second
    assert "created_at" not in first
    assert "timestamp" not in first
    assert first["pilot_manifest_sha256"] == module.sha256_file(MANIFEST_PATH)


def test_seed_changes_execution_cycle_order_without_breaking_balance() -> None:
    module = load_module()
    manifest = load_manifest()
    original = module.build_primary_run_order(manifest)

    changed = cast(dict[str, Any], json.loads(json.dumps(manifest)))
    changed["run_order"]["seed"] = "phase-5-pilot-run-order-v1-alternative-test-seed"

    # The locked validator intentionally rejects a production seed change.  Exercise
    # the version-independent cycle ranking directly to prove the seed has meaning.
    original_cycles = module._ordered_design_cycles(manifest["run_order"]["seed"])
    changed_cycles = module._ordered_design_cycles(changed["run_order"]["seed"])

    assert [item[0] for item in original_cycles] != [item[0] for item in changed_cycles]
    assert len(original) == 50


def test_manifest_validation_rejects_treatment_or_allocation_drift() -> None:
    module = load_module()
    manifest = load_manifest()

    bad_allocation = cast(dict[str, Any], json.loads(json.dumps(manifest)))
    bad_allocation["allocation"]["primary_slots"] = 51
    with pytest.raises(ValueError, match="50 primary slots"):
        module.validate_manifest(bad_allocation)

    bad_treatment = cast(dict[str, Any], json.loads(json.dumps(manifest)))
    bad_treatment["treatment_invariants"]["same_recovery_action_across_conditions"] = False
    with pytest.raises(ValueError, match="same_recovery_action_across_conditions"):
        module.validate_manifest(bad_treatment)


def test_immutable_writer_is_idempotent_but_refuses_different_bytes(tmp_path: Path) -> None:
    module = load_module()
    payload = module.build_run_order_payload(MANIFEST_PATH, load_manifest())
    output = tmp_path / "run-order.json"

    assert module.write_immutable_run_order(output, payload) is True
    first_bytes = output.read_bytes()

    assert module.write_immutable_run_order(output, payload) is False
    assert output.read_bytes() == first_bytes

    output.write_text('{"different": true}\n', encoding="utf-8")
    with pytest.raises(FileExistsError, match="refusing to overwrite different run order"):
        module.write_immutable_run_order(output, payload)


def test_payload_records_auditable_balance_summary() -> None:
    module = load_module()
    payload = module.build_run_order_payload(MANIFEST_PATH, load_manifest())

    assert payload["generator_version"] == "phase-5-pilot-run-order-generator-v1"
    assert payload["run_order_version"] == "phase-5-pilot-run-order-v1"
    assert payload["protocol_id"] == "phase-5-technical-pilot-v1"
    assert payload["primary_slot_count"] == 50
    assert set(payload["balance_summary"]["cell_counts"].values()) == {10}
