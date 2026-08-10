from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "experiments" / "harness" / "phase_5_development_audit.py"
INDEX = ROOT / "experiments" / "manifests" / "phase-5-development-validation-index.json"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase_5_development_audit", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )


def make_run(
    root: Path,
    trial_id: str,
    scenario: str,
    condition: str,
    repo_sha: str,
    recovery_hash: str | None,
    span_count: int,
    inventory_instances: int,
) -> None:
    run = root / trial_id
    checks = {"one": True, "two": True}
    write_json(
        run / "validity.json",
        {
            "trial_id": trial_id,
            "passed": True,
            "classification": "valid-development-feasibility-trial",
            "evidence_boundary": "phase-5-implementation-feasibility-only",
            "pilot_batch_id": None,
            "primary_schedule_slot": None,
            "checks": checks,
        },
    )
    write_json(run / "metadata.json", {"repository_commit_sha": repo_sha})
    write_json(
        run / "trial-manifest.json",
        {
            "trial_id": trial_id,
            "scenario_id": scenario,
            "automation_condition": condition,
            "evidence_boundary": "phase-5-implementation-feasibility-only",
            "pilot_batch_id": None,
            "primary_schedule_slot": None,
            "repetition": 0,
            "run_order": 0,
            "canonical_recovery_action_sha256": recovery_hash,
        },
    )

    if scenario == "no-fault-v1":
        requests = [
            {
                "request_index": index,
                "phase": "no-fault",
                "status": 201,
                "latency_ms": 20.0 + index,
            }
            for index in range(1, 8)
        ]
        controller_events: list[dict[str, Any]] = []
    elif scenario == "dependency-latency-v1":
        requests = [
            {"request_index": 1, "phase": "before-fault", "status": 201, "latency_ms": 20.0},
            {"request_index": 2, "phase": "before-fault", "status": 201, "latency_ms": 21.0},
            {"request_index": 3, "phase": "during-fault", "status": 201, "latency_ms": 140.0},
            {"request_index": 4, "phase": "during-fault", "status": 201, "latency_ms": 141.0},
            {"request_index": 5, "phase": "during-fault", "status": 201, "latency_ms": 142.0},
            {"request_index": 6, "phase": "after-recovery", "status": 201, "latency_ms": 22.0},
            {"request_index": 7, "phase": "after-recovery", "status": 201, "latency_ms": 23.0},
        ]
        controller_events = fault_events(condition, recovery_hash)
    else:
        requests = [
            {"request_index": 1, "phase": "before-fault", "status": 201, "latency_ms": 20.0},
            {"request_index": 2, "phase": "before-fault", "status": 201, "latency_ms": 21.0},
            {"request_index": 3, "phase": "during-fault", "status": 502, "latency_ms": 15.0},
            {"request_index": 4, "phase": "during-fault", "status": 502, "latency_ms": 15.0},
            {"request_index": 5, "phase": "during-fault", "status": 502, "latency_ms": 15.0},
            {"request_index": 6, "phase": "after-recovery", "status": 201, "latency_ms": 22.0},
            {"request_index": 7, "phase": "after-recovery", "status": 201, "latency_ms": 23.0},
        ]
        controller_events = fault_events(condition, recovery_hash)

    write_json(run / "workload.json", {"requests": requests})
    write_jsonl(run / "events.jsonl", controller_events)

    service_events: list[dict[str, Any]] = []
    for instance in range(inventory_instances):
        service_events.append(
            {
                "event_id": f"{trial_id}-inventory-instance-{instance}-00001",
                "source_component": "inventory",
                "service_instance_id": f"instance-{instance}",
            }
        )
    service_events.append(
        {
            "event_id": f"{trial_id}-order-api-instance-0-00001",
            "source_component": "order-api",
            "service_instance_id": "order-instance",
        }
    )
    write_jsonl(run / "service-events.jsonl", service_events)
    write_json(
        run / "otel-spans.json",
        {
            "signatures_match_structured_events": True,
            "expected_order_span_count": span_count,
            "observed_order_span_count": span_count,
        },
    )


def fault_events(condition: str, recovery_hash: str | None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = [
        {"event_type": "fault_application_verified"},
        {"event_type": "injection_started"},
        {"event_type": "detection_evaluation"},
        {"event_type": "detection_evaluation"},
        {"event_type": "detection_evaluation"},
        {"event_type": "fault_detected"},
    ]
    events.append(
        {
            "event_type": ("external_intervention" if condition == "manual" else "automation_evaluation"),
            "canonical_recovery_action_sha256": recovery_hash,
        }
    )
    for event_type in (
        "recovery_started",
        "recovery_action_completed",
        "injection_ended",
        "recovery_completed",
        "post_recovery_check",
    ):
        event: dict[str, Any] = {"event_type": event_type}
        if event_type in {
            "recovery_started",
            "recovery_action_completed",
            "recovery_completed",
        }:
            event["canonical_recovery_action_sha256"] = recovery_hash
        events.append(event)
    return events


def test_committed_index_declares_exactly_five_non_pilot_runs() -> None:
    index = json.loads(INDEX.read_text(encoding="utf-8"))

    assert index["expected_cell_count"] == 5
    assert index["pilot_evidence"] is False
    assert index["evidence_boundary"] == "phase-5-implementation-feasibility-only"
    assert len(index["runs"]) == 5

    cells = {(run["scenario_id"], run["automation_condition"]) for run in index["runs"]}
    assert cells == {
        ("no-fault-v1", "control"),
        ("dependency-latency-v1", "manual"),
        ("dependency-latency-v1", "automated"),
        ("service-termination-v1", "manual"),
        ("service-termination-v1", "automated"),
    }


def test_build_audit_validates_five_cells_and_pair_hashes(tmp_path: Path) -> None:
    module = load_module()
    latency_hash = "latency-hash"
    termination_hash = "termination-hash"
    index: dict[str, Any] = {
        "evidence_boundary": "phase-5-implementation-feasibility-only",
        "expected_cell_count": 5,
        "runs": [
            {
                "trial_id": "nf",
                "scenario_id": "no-fault-v1",
                "automation_condition": "control",
                "repository_commit_sha": "sha-a",
                "canonical_recovery_action_sha256": None,
                "expected_order_span_count": 35,
                "expected_inventory_instance_count": 1,
            },
            {
                "trial_id": "lm",
                "scenario_id": "dependency-latency-v1",
                "automation_condition": "manual",
                "repository_commit_sha": "sha-b",
                "canonical_recovery_action_sha256": latency_hash,
                "expected_order_span_count": 35,
                "expected_inventory_instance_count": 1,
            },
            {
                "trial_id": "la",
                "scenario_id": "dependency-latency-v1",
                "automation_condition": "automated",
                "repository_commit_sha": "sha-b",
                "canonical_recovery_action_sha256": latency_hash,
                "expected_order_span_count": 35,
                "expected_inventory_instance_count": 1,
            },
            {
                "trial_id": "tm",
                "scenario_id": "service-termination-v1",
                "automation_condition": "manual",
                "repository_commit_sha": "sha-b",
                "canonical_recovery_action_sha256": termination_hash,
                "expected_order_span_count": 32,
                "expected_inventory_instance_count": 2,
            },
            {
                "trial_id": "ta",
                "scenario_id": "service-termination-v1",
                "automation_condition": "automated",
                "repository_commit_sha": "sha-b",
                "canonical_recovery_action_sha256": termination_hash,
                "expected_order_span_count": 32,
                "expected_inventory_instance_count": 2,
            },
        ],
    }

    for entry in index["runs"]:
        make_run(
            tmp_path,
            entry["trial_id"],
            entry["scenario_id"],
            entry["automation_condition"],
            entry["repository_commit_sha"],
            entry["canonical_recovery_action_sha256"],
            entry["expected_order_span_count"],
            entry["expected_inventory_instance_count"],
        )

    result = module.build_audit(index, tmp_path)

    assert result["all_five_development_cells_validated"] is True
    assert result["paired_recovery_action_hashes_match"] is True
    assert result["development_run_count"] == 5
    assert result["pilot_evidence"] is False


def test_audit_rejects_condition_specific_recovery_hash_drift(tmp_path: Path) -> None:
    module = load_module()
    index: dict[str, Any] = {
        "evidence_boundary": "phase-5-implementation-feasibility-only",
        "expected_cell_count": 5,
        "runs": [
            {
                "trial_id": "nf",
                "scenario_id": "no-fault-v1",
                "automation_condition": "control",
                "repository_commit_sha": "sha",
                "canonical_recovery_action_sha256": None,
                "expected_order_span_count": 35,
                "expected_inventory_instance_count": 1,
            },
            {
                "trial_id": "lm",
                "scenario_id": "dependency-latency-v1",
                "automation_condition": "manual",
                "repository_commit_sha": "sha",
                "canonical_recovery_action_sha256": "one",
                "expected_order_span_count": 35,
                "expected_inventory_instance_count": 1,
            },
            {
                "trial_id": "la",
                "scenario_id": "dependency-latency-v1",
                "automation_condition": "automated",
                "repository_commit_sha": "sha",
                "canonical_recovery_action_sha256": "two",
                "expected_order_span_count": 35,
                "expected_inventory_instance_count": 1,
            },
            {
                "trial_id": "tm",
                "scenario_id": "service-termination-v1",
                "automation_condition": "manual",
                "repository_commit_sha": "sha",
                "canonical_recovery_action_sha256": "term",
                "expected_order_span_count": 32,
                "expected_inventory_instance_count": 2,
            },
            {
                "trial_id": "ta",
                "scenario_id": "service-termination-v1",
                "automation_condition": "automated",
                "repository_commit_sha": "sha",
                "canonical_recovery_action_sha256": "term",
                "expected_order_span_count": 32,
                "expected_inventory_instance_count": 2,
            },
        ],
    }

    for entry in index["runs"]:
        make_run(
            tmp_path,
            entry["trial_id"],
            entry["scenario_id"],
            entry["automation_condition"],
            entry["repository_commit_sha"],
            entry["canonical_recovery_action_sha256"],
            entry["expected_order_span_count"],
            entry["expected_inventory_instance_count"],
        )

    with pytest.raises(ValueError, match="recovery action differs by condition"):
        module.build_audit(index, tmp_path)


def test_audit_rejects_duplicate_service_event_ids(tmp_path: Path) -> None:
    module = load_module()
    entry = {
        "trial_id": "tm",
        "scenario_id": "service-termination-v1",
        "automation_condition": "manual",
        "repository_commit_sha": "sha",
        "canonical_recovery_action_sha256": "term",
        "expected_order_span_count": 32,
        "expected_inventory_instance_count": 2,
    }
    make_run(tmp_path, "tm", "service-termination-v1", "manual", "sha", "term", 32, 2)

    service_path = tmp_path / "tm" / "service-events.jsonl"
    events = module.load_jsonl(service_path)
    events.append(dict(events[0]))
    write_jsonl(service_path, events)

    with pytest.raises(ValueError, match="duplicate service event IDs"):
        module.audit_one_run(entry, tmp_path)
