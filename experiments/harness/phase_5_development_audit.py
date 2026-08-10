#!/usr/bin/env python3
"""Audit the five immutable Phase 5 development-validation evidence bundles.

The audit derives only implementation-feasibility checks.  It never promotes
development runs into pilot evidence and never calculates treatment effects.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / "experiments" / "manifests" / "phase-5-development-validation-index.json"
DEFAULT_RAW_ROOT = ROOT / "results" / "phase-5" / "development" / "raw"
DEFAULT_OUTPUT = ROOT / "results" / "phase-5" / "development" / "audit.json"
EVIDENCE_BOUNDARY = "phase-5-implementation-feasibility-only"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load newline-delimited JSON objects."""

    return [
        cast(dict[str, Any], json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def count_event(events: list[dict[str, Any]], event_type: str) -> int:
    """Count one controller event type."""

    return sum(event.get("event_type") == event_type for event in events)


def unique_nonempty(values: list[Any]) -> list[str]:
    """Return sorted unique non-empty string values."""

    return sorted({str(value) for value in values if value not in (None, "")})


def require(condition: bool, message: str) -> None:
    """Raise a stable validation error."""

    if not condition:
        raise ValueError(message)


def audit_workload(scenario_id: str, workload: dict[str, Any]) -> dict[str, Any]:
    """Validate the scenario-specific seven-request development workload."""

    requests = cast(list[dict[str, Any]], workload.get("requests", []))
    require(len(requests) == 7, f"{scenario_id}: expected seven workload requests")

    before = [record for record in requests if record.get("phase") == "before-fault"]
    during = [record for record in requests if record.get("phase") == "during-fault"]
    after = [record for record in requests if record.get("phase") == "after-recovery"]
    no_fault = [record for record in requests if record.get("phase") == "no-fault"]

    checks: dict[str, bool]
    if scenario_id == "no-fault-v1":
        checks = {
            "seven_no_fault_requests": len(no_fault) == 7,
            "all_no_fault_requests_success": all(int(record.get("status", 0)) == 201 for record in no_fault),
            "all_no_fault_requests_below_latency_detector": all(
                float(record.get("latency_ms", 0.0)) <= 100.0 for record in no_fault
            ),
        }
    elif scenario_id == "dependency-latency-v1":
        checks = {
            "two_pre_fault_requests": len(before) == 2,
            "three_during_fault_requests": len(during) == 3,
            "two_post_recovery_requests": len(after) == 2,
            "pre_fault_success_and_below_threshold": all(
                int(record.get("status", 0)) == 201 and float(record.get("latency_ms", 0.0)) <= 100.0
                for record in before
            ),
            "during_fault_success_and_above_threshold": all(
                int(record.get("status", 0)) == 201 and float(record.get("latency_ms", 0.0)) > 100.0
                for record in during
            ),
            "post_recovery_success_and_below_threshold": all(
                int(record.get("status", 0)) == 201 and float(record.get("latency_ms", 0.0)) <= 100.0
                for record in after
            ),
        }
    elif scenario_id == "service-termination-v1":
        checks = {
            "two_pre_fault_requests": len(before) == 2,
            "three_during_fault_requests": len(during) == 3,
            "two_post_recovery_requests": len(after) == 2,
            "pre_fault_success": all(int(record.get("status", 0)) == 201 for record in before),
            "during_fault_non_success": all(int(record.get("status", 0)) != 201 for record in during),
            "post_recovery_success": all(int(record.get("status", 0)) == 201 for record in after),
        }
    else:
        raise ValueError(f"unsupported scenario in development evidence: {scenario_id}")

    require(all(checks.values()), f"{scenario_id}: workload validation failed: {checks}")
    return {
        "checks": checks,
        "latencies_ms": [float(record.get("latency_ms", 0.0)) for record in requests],
        "statuses": [int(record.get("status", 0)) for record in requests],
    }


def audit_event_contract(
    scenario_id: str,
    condition: str,
    events: list[dict[str, Any]],
    expected_recovery_hash: str | None,
) -> dict[str, Any]:
    """Validate detector, initiator and recovery event invariants."""

    if scenario_id == "no-fault-v1":
        checks = {
            "no_fault_has_no_fault_detection": count_event(events, "fault_detected") == 0,
            "no_fault_has_no_recovery": count_event(events, "recovery_started") == 0,
            "no_fault_has_no_manual_intervention": count_event(events, "external_intervention") == 0,
            "no_fault_has_no_automation_decision": count_event(events, "automation_evaluation") == 0,
        }
        require(all(checks.values()), f"no-fault controller boundary failed: {checks}")
        return {"checks": checks, "recovery_hashes": []}

    expected_counts = {
        "fault_application_verified": 1,
        "injection_started": 1,
        "detection_evaluation": 3,
        "fault_detected": 1,
        "recovery_started": 1,
        "recovery_action_completed": 1,
        "injection_ended": 1,
        "recovery_completed": 1,
        "post_recovery_check": 1,
    }
    observed_counts = {event_type: count_event(events, event_type) for event_type in expected_counts}
    count_checks = {
        event_type: observed_counts[event_type] == expected for event_type, expected in expected_counts.items()
    }

    manual_count = count_event(events, "external_intervention")
    automation_count = count_event(events, "automation_evaluation")
    initiator_ok = (
        manual_count == 1 and automation_count == 0
        if condition == "manual"
        else manual_count == 0 and automation_count == 1
    )

    recovery_events = [
        event
        for event in events
        if event.get("event_type")
        in {
            "external_intervention",
            "automation_evaluation",
            "recovery_started",
            "recovery_action_completed",
            "recovery_completed",
        }
    ]
    recovery_hashes = unique_nonempty([event.get("canonical_recovery_action_sha256") for event in recovery_events])
    hash_ok = expected_recovery_hash is not None and recovery_hashes == [expected_recovery_hash]

    checks = {
        **count_checks,
        "condition_specific_initiator_only": initiator_ok,
        "one_canonical_recovery_hash": hash_ok,
    }
    require(
        all(checks.values()),
        f"{scenario_id}/{condition}: controller event validation failed: {checks}",
    )
    return {
        "checks": checks,
        "event_counts": {
            **observed_counts,
            "external_intervention": manual_count,
            "automation_evaluation": automation_count,
        },
        "recovery_hashes": recovery_hashes,
    }


def audit_one_run(entry: dict[str, Any], raw_root: Path) -> dict[str, Any]:
    """Audit one immutable development-validation trial directory."""

    trial_id = str(entry["trial_id"])
    run_dir = raw_root / trial_id
    require(run_dir.is_dir(), f"missing indexed trial directory: {trial_id}")

    required_files = (
        "validity.json",
        "metadata.json",
        "trial-manifest.json",
        "workload.json",
        "events.jsonl",
        "service-events.jsonl",
        "otel-spans.json",
    )
    for filename in required_files:
        require((run_dir / filename).is_file(), f"{trial_id}: missing {filename}")

    validity = load_json(run_dir / "validity.json")
    metadata = load_json(run_dir / "metadata.json")
    manifest = load_json(run_dir / "trial-manifest.json")
    workload = load_json(run_dir / "workload.json")
    events = load_jsonl(run_dir / "events.jsonl")
    service_events = load_jsonl(run_dir / "service-events.jsonl")
    otel = load_json(run_dir / "otel-spans.json")

    scenario_id = str(entry["scenario_id"])
    condition = str(entry["automation_condition"])

    identity_checks = {
        "trial_id_matches_index": manifest.get("trial_id") == trial_id,
        "scenario_matches_index": manifest.get("scenario_id") == scenario_id,
        "condition_matches_index": manifest.get("automation_condition") == condition,
        "repository_sha_matches_index": (metadata.get("repository_commit_sha") == entry["repository_commit_sha"]),
        "development_evidence_boundary": (
            validity.get("evidence_boundary") == EVIDENCE_BOUNDARY
            and manifest.get("evidence_boundary") == EVIDENCE_BOUNDARY
        ),
        "not_pilot_batch_evidence": (
            validity.get("pilot_batch_id") is None
            and validity.get("primary_schedule_slot") is None
            and manifest.get("pilot_batch_id") is None
            and manifest.get("primary_schedule_slot") is None
        ),
        "repetition_zero": manifest.get("repetition") == 0,
        "run_order_zero": manifest.get("run_order") == 0,
        "validity_passed": validity.get("passed") is True,
        "development_classification": (validity.get("classification") == "valid-development-feasibility-trial"),
        "all_recorded_validity_checks_true": all(
            value is True for value in cast(dict[str, Any], validity.get("checks", {})).values()
        ),
    }
    require(
        all(identity_checks.values()),
        f"{trial_id}: identity/validity audit failed: {identity_checks}",
    )

    recovery_hash = manifest.get("canonical_recovery_action_sha256")
    require(
        recovery_hash == entry["canonical_recovery_action_sha256"],
        f"{trial_id}: manifest recovery hash differs from indexed observation",
    )

    workload_audit = audit_workload(scenario_id, workload)
    event_audit = audit_event_contract(
        scenario_id,
        condition,
        events,
        cast(str | None, entry["canonical_recovery_action_sha256"]),
    )

    event_ids = [str(event.get("event_id", "")) for event in service_events]
    duplicate_ids = [event_id for event_id, count in Counter(event_ids).items() if event_id and count > 1]
    require(not duplicate_ids, f"{trial_id}: duplicate service event IDs: {duplicate_ids}")

    inventory_instances = unique_nonempty(
        [event.get("service_instance_id") for event in service_events if event.get("source_component") == "inventory"]
    )
    expected_instances = int(entry["expected_inventory_instance_count"])
    require(
        len(inventory_instances) == expected_instances,
        f"{trial_id}: inventory service instance count {len(inventory_instances)} != {expected_instances}",
    )

    expected_spans = int(entry["expected_order_span_count"])
    telemetry_checks = {
        "structured_event_otel_parity": (otel.get("signatures_match_structured_events") is True),
        "expected_span_count_matches_index": (int(otel.get("expected_order_span_count", -1)) == expected_spans),
        "observed_span_count_matches_expected": (int(otel.get("observed_order_span_count", -1)) == expected_spans),
    }
    require(
        all(telemetry_checks.values()),
        f"{trial_id}: telemetry audit failed: {telemetry_checks}",
    )

    return {
        "trial_id": trial_id,
        "scenario_id": scenario_id,
        "automation_condition": condition,
        "repository_commit_sha": metadata["repository_commit_sha"],
        "canonical_recovery_action_sha256": recovery_hash,
        "identity_and_validity_checks": identity_checks,
        "workload_audit": workload_audit,
        "controller_event_audit": event_audit,
        "service_event_count": len(service_events),
        "inventory_service_instance_count": len(inventory_instances),
        "inventory_service_instance_ids": inventory_instances,
        "duplicate_service_event_ids": duplicate_ids,
        "telemetry_audit": telemetry_checks,
        "expected_order_span_count": expected_spans,
    }


def build_audit(index: dict[str, Any], raw_root: Path) -> dict[str, Any]:
    """Build the deterministic five-cell development evidence audit."""

    require(index.get("evidence_boundary") == EVIDENCE_BOUNDARY, "unexpected evidence boundary")
    entries = cast(list[dict[str, Any]], index.get("runs", []))
    require(
        len(entries) == int(index.get("expected_cell_count", 0)) == 5,
        "development evidence index must contain exactly five runs",
    )

    audited = [audit_one_run(entry, raw_root) for entry in entries]
    cells = {(item["scenario_id"], item["automation_condition"]) for item in audited}
    expected_cells = {
        ("no-fault-v1", "control"),
        ("dependency-latency-v1", "manual"),
        ("dependency-latency-v1", "automated"),
        ("service-termination-v1", "manual"),
        ("service-termination-v1", "automated"),
    }
    require(cells == expected_cells, f"unexpected audited development cells: {cells}")

    pair_hashes: dict[str, dict[str, str]] = {}
    for scenario_id in ("dependency-latency-v1", "service-termination-v1"):
        pair = {
            str(item["automation_condition"]): str(item["canonical_recovery_action_sha256"])
            for item in audited
            if item["scenario_id"] == scenario_id
        }
        require(set(pair) == {"manual", "automated"}, f"missing condition for {scenario_id}")
        require(
            pair["manual"] == pair["automated"],
            f"recovery action differs by condition for {scenario_id}",
        )
        pair_hashes[scenario_id] = pair

    return {
        "audit_version": "1.0.0",
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "pilot_evidence": False,
        "all_five_development_cells_validated": True,
        "paired_recovery_action_hashes_match": True,
        "development_run_count": len(audited),
        "cells": audited,
        "paired_recovery_action_hashes": pair_hashes,
        "claim_boundary": {
            "supports": [
                "bounded implementation feasibility",
                "fault application and reversion feasibility",
                "shared detector execution feasibility",
                "condition-specific initiator attribution",
                "same recovery-action identity across paired conditions",
                "structured-event and OpenTelemetry parity for these development runs",
                "service-instance provenance across inventory restart",
            ],
            "does_not_support": [
                "reliability improvement claims",
                "condition effect estimates",
                "production readiness",
                "generalisation to other systems",
                "human or developer-practice effects",
            ],
        },
    }


def write_deterministic(path: Path, payload: dict[str, Any]) -> None:
    """Write deterministic audit JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Audit indexed evidence and optionally write the deterministic result."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    audit = build_audit(load_json(args.index), args.raw_root)
    write_deterministic(args.output, audit)
    print(
        json.dumps(
            {
                "all_five_development_cells_validated": audit["all_five_development_cells_validated"],
                "paired_recovery_action_hashes_match": audit["paired_recovery_action_hashes_match"],
                "development_run_count": audit["development_run_count"],
                "output": str(args.output),
                "evidence_boundary": EVIDENCE_BOUNDARY,
                "pilot_evidence": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI boundary
    raise SystemExit(main())
