#!/usr/bin/env python3
"""Generate the deterministic primary run order for the Phase 5 technical pilot.

This module is allocation infrastructure only.  It never deploys OrderFlow,
injects a fault, invokes a recovery action or writes trial evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"
GENERATOR_VERSION = "phase-5-pilot-run-order-generator-v1"

CELL_IDS = {
    "no-fault-control",
    "service-termination-manual",
    "service-termination-automated",
    "dependency-latency-manual",
    "dependency-latency-automated",
}
FAULT_SCENARIOS = ("service-termination-v1", "dependency-latency-v1")


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def canonical_json_bytes(value: object) -> bytes:
    """Return stable pretty JSON bytes used for committed/generated artefacts."""

    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash a file without normalising its bytes."""

    return sha256_bytes(path.read_bytes())


def cells_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index pilot cells and reject duplicate IDs."""

    cells: dict[str, dict[str, Any]] = {}
    for cell in manifest["pilot_cells"]:
        cell_id = str(cell["cell_id"])
        if cell_id in cells:
            raise ValueError(f"duplicate pilot cell: {cell_id}")
        cells[cell_id] = cast(dict[str, Any], cell)
    return cells


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Validate the invariants required by the v1 run-order generator."""

    if manifest.get("protocol_id") != "phase-5-technical-pilot-v1":
        raise ValueError("unexpected Phase 5 protocol ID")
    if manifest.get("manifest_version") != "1.0.0":
        raise ValueError("unexpected Phase 5 manifest version")

    target = manifest.get("target", {})
    if target.get("execution_context") != "docker-desktop-kubernetes":
        raise ValueError("Phase 5 v1 requires Docker Desktop Kubernetes only")

    indexed = cells_by_id(manifest)
    if set(indexed) != CELL_IDS:
        raise ValueError("Phase 5 v1 requires exactly the five declared pilot cells")

    for cell_id, cell in indexed.items():
        if int(cell["valid_repetitions"]) != 10:
            raise ValueError(f"{cell_id} must declare 10 valid repetitions")
        if int(cell["reserve_slots"]) != 2:
            raise ValueError(f"{cell_id} must declare two reserve slots")

    allocation = manifest.get("allocation", {})
    if allocation.get("planned_valid_trials") != 50:
        raise ValueError("Phase 5 v1 planned-valid allocation must be 50")
    if allocation.get("primary_slots") != 50:
        raise ValueError("Phase 5 v1 must have 50 primary slots")
    if allocation.get("reserve_slots") != 10:
        raise ValueError("Phase 5 v1 must have 10 reserve slots")
    if allocation.get("maximum_attempted_slots") != 60:
        raise ValueError("Phase 5 v1 maximum attempted slots must be 60")

    order = manifest.get("run_order", {})
    if order.get("generator_version") != GENERATOR_VERSION:
        raise ValueError("manifest/generator version mismatch")
    if order.get("run_order_version") != "phase-5-pilot-run-order-v1":
        raise ValueError("unexpected run-order version")
    if order.get("seed") != "phase-5-pilot-run-order-v1":
        raise ValueError("unexpected Phase 5 v1 run-order seed")
    if order.get("cycle_count") != 10 or order.get("slots_per_cycle") != 5:
        raise ValueError("Phase 5 v1 requires ten five-slot cycles")
    if order.get("primary_order_contains_reserve_slots") is not False:
        raise ValueError("reserve slots must not be pre-populated in the primary order")

    invariants = manifest.get("treatment_invariants", {})
    for field in (
        "same_detector_across_conditions",
        "same_recovery_action_across_conditions",
        "same_fault_across_conditions",
        "same_workload_across_conditions",
        "same_environment_across_conditions",
    ):
        if invariants.get(field) is not True:
            raise ValueError(f"required treatment invariant is not locked: {field}")

    scenarios = manifest.get("scenarios", {})
    for scenario_id in FAULT_SCENARIOS:
        scenario = scenarios.get(scenario_id)
        if not isinstance(scenario, dict):
            raise ValueError(f"missing fault scenario: {scenario_id}")
        if scenario.get("condition_ids") != ["manual", "automated"]:
            raise ValueError(f"unexpected conditions for {scenario_id}")
        if not isinstance(scenario.get("recovery_action"), dict):
            raise ValueError(f"missing canonical recovery action: {scenario_id}")


def _design_cycle(design_cycle_id: int) -> list[str]:
    """Construct one constrained five-cell cycle before seed ordering."""

    if not 1 <= design_cycle_id <= 10:
        raise ValueError("design cycle must be in 1..10")

    index = design_cycle_id - 1
    no_fault_position = (index % 5) + 1

    service_first = index % 2 == 0
    service_manual_first = index < 5
    latency_manual_first = index % 2 == 0

    service_pair = (
        ["service-termination-manual", "service-termination-automated"]
        if service_manual_first
        else ["service-termination-automated", "service-termination-manual"]
    )
    latency_pair = (
        ["dependency-latency-manual", "dependency-latency-automated"]
        if latency_manual_first
        else ["dependency-latency-automated", "dependency-latency-manual"]
    )

    fault_cells = service_pair + latency_pair if service_first else latency_pair + service_pair
    cycle = list(fault_cells)
    cycle.insert(no_fault_position - 1, "no-fault-control")
    return cycle


def _ordered_design_cycles(seed: str) -> list[tuple[int, list[str]]]:
    """Order balanced design cycles using version-independent SHA-256 ranking."""

    cycles = [(cycle_id, _design_cycle(cycle_id)) for cycle_id in range(1, 11)]
    return sorted(
        cycles,
        key=lambda item: hashlib.sha256(f"{seed}:{item[0]}".encode()).hexdigest(),
    )


def build_primary_run_order(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the deterministic 50-slot counterbalanced primary schedule."""

    validate_manifest(manifest)
    indexed = cells_by_id(manifest)
    seed = str(manifest["run_order"]["seed"])
    repetitions: Counter[str] = Counter()
    slots: list[dict[str, Any]] = []

    schedule_slot = 0
    for execution_cycle, (design_cycle_id, cycle_cells) in enumerate(_ordered_design_cycles(seed), start=1):
        for cycle_position, cell_id in enumerate(cycle_cells, start=1):
            schedule_slot += 1
            repetitions[cell_id] += 1
            cell = indexed[cell_id]
            slots.append(
                {
                    "schedule_slot": schedule_slot,
                    "cycle": execution_cycle,
                    "cycle_position": cycle_position,
                    "design_cycle_id": design_cycle_id,
                    "cell_id": cell_id,
                    "scenario_id": cell["scenario_id"],
                    "automation_condition": cell["automation_condition"],
                    "repetition": repetitions[cell_id],
                    "reserve": False,
                }
            )

    validate_primary_run_order(slots)
    return slots


def balance_summary(slots: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the auditable counterbalancing summary for a primary schedule."""

    by_cycle: dict[int, list[dict[str, Any]]] = {}
    for slot in slots:
        by_cycle.setdefault(int(slot["cycle"]), []).append(slot)

    no_fault_positions: Counter[int] = Counter()
    scenario_first: Counter[str] = Counter()
    condition_first: dict[str, Counter[str]] = {scenario_id: Counter() for scenario_id in FAULT_SCENARIOS}

    for cycle_slots in by_cycle.values():
        ordered = sorted(cycle_slots, key=lambda item: int(item["cycle_position"]))
        for slot in ordered:
            if slot["cell_id"] == "no-fault-control":
                no_fault_positions[int(slot["cycle_position"])] += 1

        scenario_positions: dict[str, list[dict[str, Any]]] = {
            scenario_id: [slot for slot in ordered if slot["scenario_id"] == scenario_id]
            for scenario_id in FAULT_SCENARIOS
        }
        first_scenario = min(
            FAULT_SCENARIOS,
            key=lambda scenario_id: min(int(slot["cycle_position"]) for slot in scenario_positions[scenario_id]),
        )
        scenario_first[first_scenario] += 1

        for scenario_id, scenario_slots in scenario_positions.items():
            first_condition = min(scenario_slots, key=lambda slot: int(slot["cycle_position"]))["automation_condition"]
            condition_first[scenario_id][str(first_condition)] += 1

    return {
        "cell_counts": dict(sorted(Counter(str(slot["cell_id"]) for slot in slots).items())),
        "no_fault_position_counts": {str(position): no_fault_positions[position] for position in range(1, 6)},
        "fault_scenario_first_counts": {scenario_id: scenario_first[scenario_id] for scenario_id in FAULT_SCENARIOS},
        "condition_first_counts": {
            scenario_id: {condition: condition_first[scenario_id][condition] for condition in ("manual", "automated")}
            for scenario_id in FAULT_SCENARIOS
        },
    }


def validate_primary_run_order(slots: list[dict[str, Any]]) -> None:
    """Reject a schedule that violates the locked v1 allocation/balance."""

    if len(slots) != 50:
        raise ValueError("primary run order must contain exactly 50 slots")
    if [int(slot["schedule_slot"]) for slot in slots] != list(range(1, 51)):
        raise ValueError("schedule_slot must be contiguous 1..50")
    if any(slot.get("reserve") is not False for slot in slots):
        raise ValueError("primary schedule cannot contain reserve slots")

    by_cycle: dict[int, list[dict[str, Any]]] = {}
    for slot in slots:
        by_cycle.setdefault(int(slot["cycle"]), []).append(slot)
    if set(by_cycle) != set(range(1, 11)):
        raise ValueError("primary run order must contain cycles 1..10")

    for cycle, cycle_slots in by_cycle.items():
        if len(cycle_slots) != 5:
            raise ValueError(f"cycle {cycle} must contain five slots")
        if {str(slot["cell_id"]) for slot in cycle_slots} != CELL_IDS:
            raise ValueError(f"cycle {cycle} does not contain every pilot cell exactly once")
        if {int(slot["cycle_position"]) for slot in cycle_slots} != set(range(1, 6)):
            raise ValueError(f"cycle {cycle} positions must be 1..5")

    summary = balance_summary(slots)
    if set(summary["cell_counts"].values()) != {10}:
        raise ValueError("every pilot cell must occur exactly ten times")
    if summary["no_fault_position_counts"] != {str(position): 2 for position in range(1, 6)}:
        raise ValueError("no-fault control must occupy each cycle position exactly twice")
    if set(summary["fault_scenario_first_counts"].values()) != {5}:
        raise ValueError("each fault scenario must be first in exactly five cycles")
    for scenario_id in FAULT_SCENARIOS:
        if summary["condition_first_counts"][scenario_id] != {
            "manual": 5,
            "automated": 5,
        }:
            raise ValueError(f"condition order is not balanced for {scenario_id}")

    repetitions: dict[str, list[int]] = {}
    for slot in slots:
        repetitions.setdefault(str(slot["cell_id"]), []).append(int(slot["repetition"]))
    if any(values != list(range(1, 11)) for values in repetitions.values()):
        raise ValueError("cell repetitions must be contiguous 1..10 in execution order")


def build_run_order_payload(manifest_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Build the timestamp-free immutable primary run-order object."""

    slots = build_primary_run_order(manifest)
    return {
        "run_order_version": manifest["run_order"]["run_order_version"],
        "generator_version": GENERATOR_VERSION,
        "protocol_id": manifest["protocol_id"],
        "manifest_version": manifest["manifest_version"],
        "pilot_manifest_sha256": sha256_file(manifest_path),
        "seed": manifest["run_order"]["seed"],
        "primary_slot_count": len(slots),
        "balance_summary": balance_summary(slots),
        "slots": slots,
    }


def write_immutable_run_order(path: Path, payload: dict[str, Any]) -> bool:
    """Write once; return False for an exact existing file and reject differences."""

    encoded = canonical_json_bytes(payload)
    if path.exists():
        if path.read_bytes() != encoded:
            raise FileExistsError(f"refusing to overwrite different run order: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = load_json(args.pilot_manifest)
    payload = build_run_order_payload(args.pilot_manifest, manifest)
    created = write_immutable_run_order(args.output, payload)

    result = {
        "created": created,
        "output": str(args.output),
        "run_order_sha256": sha256_bytes(canonical_json_bytes(payload)),
        "primary_slot_count": payload["primary_slot_count"],
        "balance_summary": payload["balance_summary"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI wrapper
    raise SystemExit(main())
