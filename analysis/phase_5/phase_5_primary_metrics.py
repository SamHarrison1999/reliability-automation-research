#!/usr/bin/env python3
"""Primary Phase 5 metric derivation using controller monotonic time.

This module is intentionally separate from ``phase_5_metrics.py``.  The older
module is the historical development-validation derivation implementation and
must remain reproducible for the five committed development bundles.

No UTC wall-clock fallback is permitted for primary elapsed-time metrics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
PRIMARY_RAW_ROOT = ROOT / "results" / "phase-5" / "raw"
DEVELOPMENT_RAW_ROOT = ROOT / "results" / "phase-5" / "development"
PILOT_MANIFEST = ROOT / "experiments" / "manifests" / "phase-5-pilot-manifest.json"
PRIMARY_METRIC_CONTRACT = ROOT / "docs" / "metrics" / "phase-5-primary-analysis.md"

TOOL_VERSION = "phase-5-primary-metric-derivation-v1.0"
TIMING_CONTRACT_VERSION = "phase-5-primary-timing-v1"
EVIDENCE_BOUNDARY = "technical-pilot-only"
EXPECTED_PILOT_MANIFEST_VERSION = "1.1.0"
EXPECTED_CONTROLLER_VERSION = "phase-5-single-trial-controller-v0.2"
SUCCESS_STATUS = 201
P95_MIN_COUNT = 5
FAULT_SCENARIOS = {
    "dependency-latency-v1",
    "service-termination-v1",
}


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load JSON Lines records."""

    return [
        cast(dict[str, Any], json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def canonical_json_bytes(value: object) -> bytes:
    """Return a stable semantic JSON representation."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_source_sha256(path: Path) -> str:
    """Hash parsed JSON/JSONL independent of text line endings."""

    if path.suffix == ".jsonl":
        value: object = load_jsonl(path)
    elif path.suffix == ".json":
        value = load_json(path)
    else:
        value = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the exact byte SHA-256 of one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def monotonic_ns(event: dict[str, Any]) -> int:
    """Return a valid primary controller monotonic timestamp.

    Booleans are rejected even though ``bool`` is an ``int`` subclass.
    """

    value = event.get("monotonic_ns")
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"event {event.get('event_id')!r} has no valid integer monotonic_ns")
    if value < 0:
        raise ValueError(f"event {event.get('event_id')!r} has negative monotonic_ns")
    return value


def monotonic_duration_ms(start: dict[str, Any], end: dict[str, Any]) -> float:
    """Return a non-negative same-process elapsed duration in milliseconds."""

    delta = monotonic_ns(end) - monotonic_ns(start)
    if delta < 0:
        raise ValueError(f"negative monotonic duration: {start.get('event_id')} -> {end.get('event_id')}")
    return round(delta / 1_000_000.0, 6)


def percentile_type7(values: list[float], probability: float) -> float:
    """Return a Type-7 linearly interpolated percentile."""

    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("percentile probability must be between zero and one")

    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def latency_summary(values: list[float]) -> dict[str, Any]:
    """Summarise one declared request-latency window."""

    if not values:
        return {
            "count": 0,
            "minimum_ms": None,
            "maximum_ms": None,
            "p50_ms": None,
            "p95_ms": None,
            "p95_status": "insufficient_count",
        }

    p95: float | None = None
    p95_status = "insufficient_count"
    if len(values) >= P95_MIN_COUNT:
        p95 = round(percentile_type7(values, 0.95), 3)
        p95_status = "observed"

    return {
        "count": len(values),
        "minimum_ms": round(min(values), 3),
        "maximum_ms": round(max(values), 3),
        "p50_ms": round(statistics.median(values), 3),
        "p95_ms": p95,
        "p95_status": p95_status,
    }


def metric(
    value: Any,
    status: str,
    source_event_ids: list[str] | None = None,
    reason: str | None = None,
    **fields: Any,
) -> dict[str, Any]:
    """Construct an auditable metric record."""

    record: dict[str, Any] = {
        "value": value,
        "status": status,
        "source_event_ids": source_event_ids or [],
    }
    if reason is not None:
        record["reason"] = reason
    record.update(fields)
    return record


def not_applicable(reason: str) -> dict[str, Any]:
    """Construct a not-applicable metric."""

    return metric(None, "not_applicable", reason=reason)


def events_of_type(events: list[dict[str, Any]], event_type: str) -> list[dict[str, Any]]:
    """Return events of one controller event class."""

    return [event for event in events if event.get("event_type") == event_type]


def unique_boundary(
    events: list[dict[str, Any]],
    event_type: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Return exactly one primary boundary and validate monotonic time."""

    matches = events_of_type(events, event_type)
    if not matches:
        return None, f"missing_{event_type}"
    if len(matches) > 1:
        return None, f"duplicate_{event_type}"
    try:
        monotonic_ns(matches[0])
    except ValueError:
        return None, f"invalid_monotonic_ns_{event_type}"
    return matches[0], None


def duration_metric(
    events: list[dict[str, Any]],
    start_type: str,
    end_type: str,
) -> dict[str, Any]:
    """Derive a primary duration with no UTC fallback."""

    start, start_reason = unique_boundary(events, start_type)
    end, end_reason = unique_boundary(events, end_type)
    reasons = [reason for reason in (start_reason, end_reason) if reason]
    if reasons or start is None or end is None:
        return metric(
            None,
            "missing",
            reason=";".join(reasons) if reasons else "missing_boundary",
        )
    try:
        value = monotonic_duration_ms(start, end)
    except ValueError as exc:
        return metric(
            None,
            "missing",
            [str(start.get("event_id", "")), str(end.get("event_id", ""))],
            reason=str(exc),
        )
    return metric(
        value,
        "observed",
        [str(start["event_id"]), str(end["event_id"])],
    )


def request_identity(event: dict[str, Any]) -> tuple[str, int]:
    """Return stable request identity."""

    return (str(event.get("order_id", "")), int(event.get("request_index", -1)))


def derive_failure_impact(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Derive primary failure impact using monotonic fault membership."""

    injection_started, start_reason = unique_boundary(events, "injection_started")
    injection_ended, end_reason = unique_boundary(events, "injection_ended")
    reasons = [reason for reason in (start_reason, end_reason) if reason]
    if reasons or injection_started is None or injection_ended is None:
        return metric(
            None,
            "missing",
            reason=";".join(reasons) if reasons else "missing_fault_interval",
            failed_requests=0,
            offered_requests=0,
            unresolved_requests=0,
        )

    start_ns = monotonic_ns(injection_started)
    end_ns = monotonic_ns(injection_ended)
    if end_ns < start_ns:
        return metric(
            None,
            "missing",
            reason="negative_fault_interval",
            failed_requests=0,
            offered_requests=0,
            unresolved_requests=0,
        )

    offered: list[dict[str, Any]] = []
    for request in events_of_type(events, "workload_request"):
        try:
            request_ns = monotonic_ns(request)
        except ValueError:
            return metric(
                None,
                "missing",
                reason="invalid_monotonic_ns_workload_request",
                failed_requests=0,
                offered_requests=0,
                unresolved_requests=0,
            )
        if start_ns <= request_ns < end_ns:
            offered.append(request)

    responses: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for response in events_of_type(events, "workload_response"):
        responses.setdefault(request_identity(response), []).append(response)

    failed = 0
    unresolved = 0
    response_ids: list[str] = []
    for request in offered:
        matches = responses.get(request_identity(request), [])
        if len(matches) != 1:
            unresolved += 1
            continue
        response = matches[0]
        response_ids.append(str(response.get("event_id", "")))
        try:
            status = int(response.get("status", 0))
        except (TypeError, ValueError):
            unresolved += 1
            continue
        if status != SUCCESS_STATUS:
            failed += 1

    source_ids = [
        str(injection_started["event_id"]),
        *[str(request.get("event_id", "")) for request in offered],
        *response_ids,
        str(injection_ended["event_id"]),
    ]

    if unresolved:
        return metric(
            None,
            "missing",
            source_ids,
            reason="unresolved_or_duplicate_response_in_fault_interval",
            failed_requests=failed,
            offered_requests=len(offered),
            unresolved_requests=unresolved,
        )
    if not offered:
        return metric(
            None,
            "missing",
            source_ids,
            reason="no_offered_request_in_fault_interval",
            failed_requests=0,
            offered_requests=0,
            unresolved_requests=0,
        )

    return metric(
        round(failed / len(offered), 6),
        "observed",
        source_ids,
        failed_requests=failed,
        offered_requests=len(offered),
        unresolved_requests=0,
    )


def derive_time_to_first_post_recovery_success(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Derive functional recovery timing from the referenced success event."""

    injection_started, start_reason = unique_boundary(events, "injection_started")
    recovery_completed, recovery_reason = unique_boundary(events, "recovery_completed")
    reasons = [reason for reason in (start_reason, recovery_reason) if reason]
    if reasons or injection_started is None or recovery_completed is None:
        return metric(
            None,
            "missing",
            reason=";".join(reasons) if reasons else "missing_boundary",
        )

    response_id = recovery_completed.get("post_recovery_response_event_id")
    if not isinstance(response_id, str) or not response_id:
        return metric(
            None,
            "missing",
            [str(injection_started["event_id"]), str(recovery_completed["event_id"])],
            reason="recovery_completed_missing_post_recovery_response_reference",
        )

    matches = [
        event
        for event in events_of_type(events, "workload_response")
        if event.get("event_id") == response_id and int(event.get("status", 0)) == SUCCESS_STATUS
    ]
    if len(matches) != 1:
        return metric(
            None,
            "missing",
            [str(injection_started["event_id"]), str(recovery_completed["event_id"])],
            reason="referenced_post_recovery_success_not_unique",
        )

    response = matches[0]
    try:
        value = monotonic_duration_ms(injection_started, response)
    except ValueError as exc:
        return metric(
            None,
            "missing",
            [str(injection_started["event_id"]), str(response["event_id"])],
            reason=str(exc),
        )

    return metric(
        value,
        "observed",
        [
            str(injection_started["event_id"]),
            str(response["event_id"]),
            str(recovery_completed["event_id"]),
        ],
    )


def derive_latency_windows(workload: dict[str, Any]) -> dict[str, Any]:
    """Derive descriptive request latency windows."""

    requests = cast(list[dict[str, Any]], workload.get("requests", []))
    phases = sorted({str(record.get("phase")) for record in requests if record.get("phase") not in (None, "")})

    windows: dict[str, Any] = {}
    for phase in phases:
        values = [
            float(record["latency_ms"])
            for record in requests
            if record.get("phase") == phase and record.get("latency_ms") is not None
        ]
        windows[phase] = latency_summary(values)

    all_values = [float(record["latency_ms"]) for record in requests if record.get("latency_ms") is not None]
    windows["all_requests"] = latency_summary(all_values)
    return windows


def derive_latency_inflation(
    scenario_id: str,
    workload: dict[str, Any],
) -> dict[str, Any]:
    """Return within-trial median fault/pre-fault latency ratio."""

    if scenario_id not in FAULT_SCENARIOS:
        return not_applicable("no_fault_control_has_no_fault_window")

    requests = cast(list[dict[str, Any]], workload.get("requests", []))
    before = [
        float(record["latency_ms"])
        for record in requests
        if record.get("phase") == "before-fault" and record.get("latency_ms") is not None
    ]
    during = [
        float(record["latency_ms"])
        for record in requests
        if record.get("phase") == "during-fault" and record.get("latency_ms") is not None
    ]
    if not before or not during:
        return metric(None, "missing", reason="missing_latency_window")

    before_median = statistics.median(before)
    if before_median <= 0:
        return metric(None, "missing", reason="non_positive_pre_fault_median")

    during_median = statistics.median(during)
    return metric(
        round(during_median / before_median, 6),
        "observed",
        before_fault_p50_ms=round(before_median, 3),
        during_fault_p50_ms=round(during_median, 3),
    )


def derive_recovery_success(
    scenario_id: str,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Require action completion, functional completion and stability check."""

    if scenario_id not in FAULT_SCENARIOS:
        return not_applicable("no_fault_control_has_no_recovery")

    action, action_reason = unique_boundary(events, "recovery_action_completed")
    recovery, recovery_reason = unique_boundary(events, "recovery_completed")
    post, post_reason = unique_boundary(events, "post_recovery_check")
    reasons = [reason for reason in (action_reason, recovery_reason, post_reason) if reason is not None]
    if reasons or action is None or recovery is None or post is None:
        return metric(
            0,
            "observed",
            reason=";".join(reasons) if reasons else "missing_recovery_boundary",
        )

    success = post.get("result") == "passed"
    return metric(
        1 if success else 0,
        "observed",
        [str(action["event_id"]), str(recovery["event_id"]), str(post["event_id"])],
    )


def validate_primary_identity(
    manifest: dict[str, Any],
    validity: dict[str, Any],
) -> None:
    """Reject any development or incompletely bound trial."""

    if manifest.get("manifest_type") != "phase-5-primary-trial-manifest":
        raise ValueError("not a Phase 5 primary trial manifest")
    if manifest.get("evidence_boundary") != EVIDENCE_BOUNDARY:
        raise ValueError("unexpected primary evidence boundary")
    if validity.get("evidence_boundary") != EVIDENCE_BOUNDARY:
        raise ValueError("validity evidence boundary mismatch")
    if manifest.get("manifest_version") != EXPECTED_PILOT_MANIFEST_VERSION:
        raise ValueError("unexpected Phase 5 pilot manifest version")
    if manifest.get("controller_version") != EXPECTED_CONTROLLER_VERSION:
        raise ValueError("unexpected Phase 5 primary controller version")

    batch_id = manifest.get("pilot_batch_id")
    slot = manifest.get("primary_schedule_slot")
    repetition = manifest.get("repetition")
    run_order = manifest.get("run_order")

    if not isinstance(batch_id, str) or not batch_id:
        raise ValueError("primary trial is missing pilot_batch_id")
    if isinstance(slot, bool) or not isinstance(slot, int) or slot < 1:
        raise ValueError("primary trial is missing a valid primary_schedule_slot")
    if isinstance(repetition, bool) or not isinstance(repetition, int) or repetition < 1:
        raise ValueError("primary trial is missing a valid repetition")
    if isinstance(run_order, bool) or not isinstance(run_order, int) or run_order < 1:
        raise ValueError("primary trial is missing a valid run_order")

    if validity.get("pilot_batch_id") != batch_id:
        raise ValueError("validity pilot_batch_id mismatch")
    if validity.get("primary_schedule_slot") != slot:
        raise ValueError("validity primary_schedule_slot mismatch")


def required_monotonic_event_types(scenario_id: str) -> set[str]:
    """Return controller event classes required to carry monotonic time."""

    base = {
        "trial_started",
        "reset_started",
        "clean_state_verified",
        "reset_completed",
        "workload_started",
        "workload_request",
        "workload_response",
        "workload_completed",
        "observation_verified",
        "otel_observation_verified",
        "cleanup_completed",
        "trial_completed",
    }
    if scenario_id in FAULT_SCENARIOS:
        base.update(
            {
                "fault_application_verified",
                "injection_started",
                "detection_evaluation",
                "fault_detected",
                "recovery_started",
                "recovery_action_completed",
                "injection_ended",
                "recovery_completed",
                "post_recovery_check",
            }
        )
    return base


def measurement_quality(
    scenario_id: str,
    events: list[dict[str, Any]],
    validity: dict[str, Any],
) -> dict[str, Any]:
    """Derive primary monotonic timing completeness and raw validity."""

    required_types = required_monotonic_event_types(scenario_id)
    required_instances = [event for event in events if event.get("event_type") in required_types]

    monotonic_valid = 0
    invalid_ids: list[str] = []
    for event in required_instances:
        try:
            monotonic_ns(event)
        except ValueError:
            invalid_ids.append(str(event.get("event_id", "")))
        else:
            monotonic_valid += 1

    completeness = monotonic_valid / len(required_instances) if required_instances else 0.0

    return {
        "primary_monotonic_completeness": round(completeness, 6),
        "primary_monotonic_invalid_event_ids": invalid_ids,
        "primary_duration_clock": "controller-monotonic-ns",
        "utc_fallback_permitted": False,
        "trial_valid": validity.get("passed") is True,
        "validity_classification": validity.get("classification"),
    }


def derive_primary_observation(run_dir: Path) -> dict[str, Any]:
    """Derive one future primary observation from one immutable raw bundle."""

    resolved = run_dir.resolve()
    development = DEVELOPMENT_RAW_ROOT.resolve()
    if resolved == development or development in resolved.parents:
        raise ValueError("primary analysis refuses development evidence")

    required_files = {
        "events": run_dir / "events.jsonl",
        "workload": run_dir / "workload.json",
        "validity": run_dir / "validity.json",
        "metadata": run_dir / "metadata.json",
        "trial_manifest": run_dir / "trial-manifest.json",
    }
    for name, path in required_files.items():
        if not path.is_file():
            raise ValueError(f"missing required primary raw source {name}: {path}")

    events = load_jsonl(required_files["events"])
    workload = load_json(required_files["workload"])
    validity = load_json(required_files["validity"])
    metadata = load_json(required_files["metadata"])
    manifest = load_json(required_files["trial_manifest"])
    validate_primary_identity(manifest, validity)

    scenario_id = str(manifest["scenario_id"])
    condition = str(manifest["automation_condition"])

    if scenario_id in FAULT_SCENARIOS:
        primary = {
            "detection_latency_ms": duration_metric(events, "injection_started", "fault_detected"),
            "recovery_time_ms": duration_metric(events, "injection_started", "recovery_completed"),
            "failure_impact_rate": derive_failure_impact(events),
        }
        failure = primary["failure_impact_rate"]
        secondary = {
            "active_recovery_duration_ms": duration_metric(events, "recovery_started", "recovery_completed"),
            "time_to_first_post_recovery_success_ms": (derive_time_to_first_post_recovery_success(events)),
            "failed_requests_count": metric(
                failure.get("failed_requests"),
                "observed" if failure.get("status") == "observed" else "missing",
                failure.get("source_event_ids", []),
                reason=failure.get("reason"),
            ),
            "latency_inflation_ratio": derive_latency_inflation(scenario_id, workload),
            "recovery_success": derive_recovery_success(scenario_id, events),
            "manual_intervention_count": metric(
                len(events_of_type(events, "external_intervention")),
                "observed",
                [str(event["event_id"]) for event in events_of_type(events, "external_intervention")],
            ),
            "automation_decision_count": metric(
                len(events_of_type(events, "automation_evaluation")),
                "observed",
                [str(event["event_id"]) for event in events_of_type(events, "automation_evaluation")],
            ),
        }
    else:
        primary = {
            "detection_latency_ms": not_applicable("no_fault_control"),
            "recovery_time_ms": not_applicable("no_fault_control"),
            "failure_impact_rate": not_applicable("no_fault_control"),
        }
        secondary = {
            "active_recovery_duration_ms": not_applicable("no_fault_control"),
            "time_to_first_post_recovery_success_ms": not_applicable("no_fault_control"),
            "failed_requests_count": not_applicable("no_fault_control"),
            "latency_inflation_ratio": not_applicable("no_fault_control"),
            "recovery_success": not_applicable("no_fault_control"),
            "manual_intervention_count": metric(len(events_of_type(events, "external_intervention")), "observed"),
            "automation_decision_count": metric(len(events_of_type(events, "automation_evaluation")), "observed"),
        }

    source_hashes = {name: canonical_source_sha256(path) for name, path in required_files.items()}

    return {
        "observation_version": "1.0.0",
        "analysis_tool_version": TOOL_VERSION,
        "timing_contract_version": TIMING_CONTRACT_VERSION,
        "evidence_class": "phase-5-primary-pilot",
        "eligible_for_primary_pilot_analysis": True,
        "trial_id": manifest["trial_id"],
        "run_id": manifest["run_id"],
        "scenario_id": scenario_id,
        "automation_condition": condition,
        "repetition": manifest["repetition"],
        "run_order": manifest["run_order"],
        "primary_schedule_slot": manifest["primary_schedule_slot"],
        "pilot_batch_id": manifest["pilot_batch_id"],
        "repository_commit_sha": metadata["repository_commit_sha"],
        "bound_source_commit_sha": manifest.get("bound_source_commit_sha"),
        "canonical_recovery_action_sha256": manifest.get("canonical_recovery_action_sha256"),
        "timing_contract": {
            "duration_source": "controller_monotonic_ns",
            "audit_clock": "utc_timestamp",
            "utc_fallback_permitted": False,
            "fault_interval": "[injection_started,injection_ended)",
            "recovery_time_definition": "recovery_completed-injection_started",
            "opentelemetry_used_for_primary_timing": False,
        },
        "primary_metrics": primary,
        "secondary_metrics": secondary,
        "request_latency_windows": derive_latency_windows(workload),
        "measurement_quality": measurement_quality(scenario_id, events, validity),
        "provenance": {
            "metric_contract": str(PRIMARY_METRIC_CONTRACT.relative_to(ROOT)),
            "metric_contract_sha256": sha256_file(PRIMARY_METRIC_CONTRACT),
            "pilot_manifest_sha256": sha256_file(PILOT_MANIFEST),
            "raw_source_canonical_sha256": source_hashes,
        },
    }


def write_deterministic(path: Path, payload: dict[str, Any]) -> None:
    """Write stable JSON with no generated timestamp."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    """Derive one primary trial observation."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    trial_dir = args.trial_dir.resolve()
    primary_root = PRIMARY_RAW_ROOT.resolve()
    if trial_dir == primary_root or primary_root not in trial_dir.parents:
        parser.error("--trial-dir must be one immutable trial directory beneath results/phase-5/raw")

    try:
        observation = derive_primary_observation(trial_dir)
    except ValueError as exc:
        parser.error(str(exc))

    if args.output is not None:
        write_deterministic(args.output, observation)

    print(
        json.dumps(
            {
                "analysis_tool_version": TOOL_VERSION,
                "trial_id": observation["trial_id"],
                "pilot_batch_id": observation["pilot_batch_id"],
                "primary_schedule_slot": observation["primary_schedule_slot"],
                "eligible_for_primary_pilot_analysis": True,
                "primary_monotonic_completeness": observation["measurement_quality"]["primary_monotonic_completeness"],
                "utc_fallback_permitted": False,
                "output": str(args.output) if args.output is not None else None,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI boundary
    sys.exit(main())
