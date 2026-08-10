#!/usr/bin/env python3
"""Deterministically derive Phase 5 technical metrics from immutable raw trials.

The initial CLI target is the five committed development-validation bundles.
Those records remain implementation-feasibility evidence and are never
promoted into the future primary pilot dataset by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / "experiments" / "manifests" / "phase-5-development-validation-index.json"
DEFAULT_RAW_ROOT = ROOT / "results" / "phase-5" / "development" / "raw"
DEFAULT_PROCESSED_OUTPUT = ROOT / "data" / "processed" / "phase-5" / "development" / "observations.json"
DEFAULT_SUMMARY_OUTPUT = ROOT / "analysis" / "phase_5" / "development-summary.json"
PHASE5_METRIC_CATALOGUE = ROOT / "docs" / "metrics" / "phase-5-technical-metrics.md"

TOOL_VERSION = "phase-5-metric-derivation-v1.0"
EVIDENCE_BOUNDARY = "phase-5-implementation-feasibility-only"
SUCCESS_STATUS = 201
P95_MIN_COUNT = 5

FAULT_SCENARIOS = {
    "dependency-latency-v1",
    "service-termination-v1",
}
CELL_ORDER = [
    ("no-fault-v1", "control"),
    ("dependency-latency-v1", "manual"),
    ("dependency-latency-v1", "automated"),
    ("service-termination-v1", "manual"),
    ("service-termination-v1", "automated"),
]


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""

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
    """Hash parsed JSON/JSONL content independent of platform line endings."""

    if path.suffix == ".jsonl":
        value: object = load_jsonl(path)
    elif path.suffix == ".json":
        value = load_json(path)
    else:
        value = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash exact file bytes for versioned repository inputs."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_timestamp(value: object) -> datetime:
    """Parse the controller's required UTC timestamp representation."""

    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"timestamp is not UTC Z form: {value!r}")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp lacks timezone: {value!r}")
    return parsed.astimezone(UTC)


def duration_ms(start: dict[str, Any], end: dict[str, Any]) -> float:
    """Return a non-negative duration between two controller events."""

    value = (parse_timestamp(end.get("timestamp")) - parse_timestamp(start.get("timestamp"))).total_seconds() * 1000.0
    if value < 0:
        raise ValueError(f"negative event duration: {start.get('event_id')} -> {end.get('event_id')}")
    return round(value, 3)


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


def events_of_type(events: list[dict[str, Any]], event_type: str) -> list[dict[str, Any]]:
    """Return controller events of one type."""

    return [event for event in events if event.get("event_type") == event_type]


def unique_boundary(
    events: list[dict[str, Any]],
    event_type: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Return one required boundary or a missing/duplicate reason."""

    matches = events_of_type(events, event_type)
    if not matches:
        return None, f"missing_{event_type}"
    if len(matches) > 1:
        return None, f"duplicate_{event_type}"
    try:
        parse_timestamp(matches[0].get("timestamp"))
    except ValueError:
        return None, f"invalid_timestamp_{event_type}"
    return matches[0], None


def duration_metric(
    events: list[dict[str, Any]],
    start_type: str,
    end_type: str,
) -> dict[str, Any]:
    """Derive a duration without imputing missing/duplicate boundaries."""

    start, start_reason = unique_boundary(events, start_type)
    end, end_reason = unique_boundary(events, end_type)
    reasons = [reason for reason in (start_reason, end_reason) if reason is not None]
    if reasons or start is None or end is None:
        return metric(
            None,
            "missing",
            reason=";".join(reasons) if reasons else "missing_boundary",
        )
    try:
        value = duration_ms(start, end)
    except ValueError as exc:
        return metric(
            None,
            "missing",
            [str(start["event_id"]), str(end["event_id"])],
            reason=str(exc),
        )
    return metric(
        value,
        "observed",
        [str(start["event_id"]), str(end["event_id"])],
    )


def not_applicable(reason: str) -> dict[str, Any]:
    """Construct a not-applicable metric record."""

    return metric(None, "not_applicable", reason=reason)


def request_identity(event: dict[str, Any]) -> tuple[str, int]:
    """Return the stable order/request identity used to pair controller events."""

    return (str(event.get("order_id", "")), int(event.get("request_index", -1)))


def derive_failure_impact(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Derive failure impact from request timestamps in the half-open fault interval."""

    injection_started, start_reason = unique_boundary(events, "injection_started")
    injection_ended, end_reason = unique_boundary(events, "injection_ended")
    reasons = [reason for reason in (start_reason, end_reason) if reason is not None]
    if reasons or injection_started is None or injection_ended is None:
        return metric(
            None,
            "missing",
            reason=";".join(reasons) if reasons else "missing_fault_interval",
            failed_requests=0,
            offered_requests=0,
            unresolved_requests=0,
        )

    try:
        start_time = parse_timestamp(injection_started.get("timestamp"))
        end_time = parse_timestamp(injection_ended.get("timestamp"))
    except ValueError as exc:
        return metric(
            None,
            "missing",
            reason=str(exc),
            failed_requests=0,
            offered_requests=0,
            unresolved_requests=0,
        )

    if end_time < start_time:
        return metric(
            None,
            "missing",
            reason="negative_fault_interval",
            failed_requests=0,
            offered_requests=0,
            unresolved_requests=0,
        )

    offered: list[dict[str, Any]] = []
    for event in events_of_type(events, "workload_request"):
        try:
            timestamp = parse_timestamp(event.get("timestamp"))
        except ValueError:
            return metric(
                None,
                "missing",
                reason="invalid_workload_request_timestamp",
                failed_requests=0,
                offered_requests=0,
                unresolved_requests=0,
            )
        if start_time <= timestamp < end_time:
            offered.append(event)

    responses: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for response in events_of_type(events, "workload_response"):
        responses.setdefault(request_identity(response), []).append(response)

    failed = 0
    unresolved = 0
    response_event_ids: list[str] = []
    for request in offered:
        matches = responses.get(request_identity(request), [])
        if len(matches) != 1:
            unresolved += 1
            continue
        response = matches[0]
        response_event_ids.append(str(response.get("event_id", "")))
        try:
            status = int(response.get("status", 0))
        except (TypeError, ValueError):
            unresolved += 1
            continue
        if status != SUCCESS_STATUS:
            failed += 1

    source_ids = [
        str(injection_started["event_id"]),
        *[str(event.get("event_id", "")) for event in offered],
        *response_event_ids,
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
    """Use the response explicitly referenced by the Phase 5 recovery boundary."""

    injection_started, start_reason = unique_boundary(events, "injection_started")
    recovery_completed, recovery_reason = unique_boundary(events, "recovery_completed")
    reasons = [reason for reason in (start_reason, recovery_reason) if reason is not None]
    if reasons or injection_started is None or recovery_completed is None:
        return metric(
            None,
            "missing",
            reason=";".join(reasons) if reasons else "missing_boundary",
        )

    response_event_id = recovery_completed.get("post_recovery_response_event_id")
    if not response_event_id:
        return metric(
            None,
            "missing",
            [str(injection_started["event_id"]), str(recovery_completed["event_id"])],
            reason="recovery_completed_missing_post_recovery_response_reference",
        )
    matches = [
        event
        for event in events_of_type(events, "workload_response")
        if event.get("event_id") == response_event_id and int(event.get("status", 0)) == SUCCESS_STATUS
    ]
    if len(matches) != 1:
        return metric(
            None,
            "missing",
            [str(injection_started["event_id"]), str(recovery_completed["event_id"])],
            reason="referenced_post_recovery_success_not_unique",
        )
    try:
        value = duration_ms(injection_started, matches[0])
    except ValueError as exc:
        return metric(
            None,
            "missing",
            [
                str(injection_started["event_id"]),
                str(matches[0].get("event_id", "")),
            ],
            reason=str(exc),
        )
    return metric(
        value,
        "observed",
        [
            str(injection_started["event_id"]),
            str(matches[0]["event_id"]),
            str(recovery_completed["event_id"]),
        ],
    )


def derive_latency_windows(workload: dict[str, Any]) -> dict[str, Any]:
    """Derive per-phase request latency summaries from workload records."""

    requests = cast(list[dict[str, Any]], workload.get("requests", []))
    phases = sorted({str(record.get("phase", "")) for record in requests if record.get("phase")})
    windows: dict[str, Any] = {}
    for phase in phases:
        latencies = [
            float(record["latency_ms"])
            for record in requests
            if record.get("phase") == phase and record.get("latency_ms") is not None
        ]
        windows[phase] = latency_summary(latencies)

    all_latencies = [float(record["latency_ms"]) for record in requests if record.get("latency_ms") is not None]
    windows["all_requests"] = latency_summary(all_latencies)
    return windows


def derive_latency_inflation(
    scenario_id: str,
    workload: dict[str, Any],
) -> dict[str, Any]:
    """Compare median during-fault latency with the same trial's pre-fault median."""

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
    denominator = statistics.median(before)
    if denominator <= 0:
        return metric(None, "missing", reason="non_positive_pre_fault_median")
    return metric(
        round(statistics.median(during) / denominator, 6),
        "observed",
        reason=None,
        before_fault_p50_ms=round(statistics.median(before), 3),
        during_fault_p50_ms=round(statistics.median(during), 3),
    )


def derive_recovery_success(
    scenario_id: str,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Require action completion, functional recovery and the stability check."""

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


def required_event_types(scenario_id: str) -> list[str]:
    """Return the Phase 5 scenario-level required controller event classes."""

    base = [
        "trial_started",
        "reset_started",
        "clean_state_verified",
        "reset_completed",
        "workload_started",
        "workload_completed",
        "observation_verified",
        "otel_observation_verified",
        "cleanup_completed",
        "trial_completed",
    ]
    if scenario_id in FAULT_SCENARIOS:
        return [
            *base,
            "fault_application_verified",
            "injection_started",
            "fault_detected",
            "recovery_started",
            "recovery_action_completed",
            "recovery_completed",
            "injection_ended",
            "post_recovery_check",
        ]
    return base


def measurement_quality(
    scenario_id: str,
    events: list[dict[str, Any]],
    service_events: list[dict[str, Any]],
    validity: dict[str, Any],
) -> dict[str, Any]:
    """Derive Phase 5 measurement-quality outcomes."""

    required = required_event_types(scenario_id)
    present = [event_type for event_type in required if events_of_type(events, event_type)]
    required_event_completeness = len(present) / len(required)

    required_instances = [event for event in events if str(event.get("event_type", "")) in set(required)]
    parseable = 0
    for event in required_instances:
        try:
            parse_timestamp(event.get("timestamp"))
        except ValueError:
            continue
        parseable += 1
    timestamp_completeness = parseable / len(required_instances) if required_instances else 0.0

    order_service_events = [event for event in service_events if event.get("order_id")]
    correlation_fields = (
        "trace_id",
        "span_id",
        "run_id",
        "trial_id",
        "order_id",
        "source_component",
        "event_type",
    )
    correlated = [
        event
        for event in order_service_events
        if all(event.get(field) not in (None, "") for field in correlation_fields)
    ]
    trace_completeness = len(correlated) / len(order_service_events) if order_service_events else 0.0

    before_clean = any(
        event.get("event_type") == "clean_state_verified"
        and event.get("stage") == "before_deploy"
        and event.get("namespace_present") is False
        for event in events
    )
    after_clean = any(
        event.get("event_type") == "clean_state_verified"
        and event.get("stage") == "after_cleanup"
        and event.get("namespace_present") is False
        for event in events
    )

    return {
        "required_event_completeness": round(required_event_completeness, 6),
        "timestamp_completeness": round(timestamp_completeness, 6),
        "trace_correlation_completeness": round(trace_completeness, 6),
        "reset_duration_ms": duration_metric(events, "reset_started", "reset_completed"),
        "clean_state_verified": before_clean and after_clean,
        "contamination_detected": not after_clean,
        "trial_valid": validity.get("passed") is True,
        "validity_classification": validity.get("classification"),
    }


def derive_observation(run_dir: Path, index_entry: dict[str, Any]) -> dict[str, Any]:
    """Derive one auditable Phase 5 development observation."""

    trial_id = str(index_entry["trial_id"])
    required_files = {
        "events": run_dir / "events.jsonl",
        "service_events": run_dir / "service-events.jsonl",
        "workload": run_dir / "workload.json",
        "validity": run_dir / "validity.json",
        "metadata": run_dir / "metadata.json",
        "trial_manifest": run_dir / "trial-manifest.json",
        "otel_spans": run_dir / "otel-spans.json",
    }
    for name, path in required_files.items():
        if not path.is_file():
            raise ValueError(f"{trial_id}: missing required raw source {name}: {path}")

    events = load_jsonl(required_files["events"])
    service_events = load_jsonl(required_files["service_events"])
    workload = load_json(required_files["workload"])
    validity = load_json(required_files["validity"])
    metadata = load_json(required_files["metadata"])
    manifest = load_json(required_files["trial_manifest"])

    scenario_id = str(manifest["scenario_id"])
    condition = str(manifest["automation_condition"])
    if scenario_id != index_entry["scenario_id"] or condition != index_entry["automation_condition"]:
        raise ValueError(f"{trial_id}: trial identity differs from development evidence index")
    if validity.get("evidence_boundary") != EVIDENCE_BOUNDARY:
        raise ValueError(f"{trial_id}: unexpected evidence boundary")
    if validity.get("pilot_batch_id") is not None or validity.get("primary_schedule_slot") is not None:
        raise ValueError(f"{trial_id}: development metric tool refuses pilot-labelled evidence")

    if scenario_id in FAULT_SCENARIOS:
        primary = {
            "detection_latency_ms": duration_metric(events, "injection_started", "fault_detected"),
            "recovery_time_ms": duration_metric(events, "injection_started", "recovery_completed"),
            "failure_impact_rate": derive_failure_impact(events),
        }
        secondary = {
            "active_recovery_duration_ms": duration_metric(events, "recovery_started", "recovery_completed"),
            "time_to_first_post_recovery_success_ms": (derive_time_to_first_post_recovery_success(events)),
            "failed_requests_count": None,
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
            "rollback_duration_ms": not_applicable("phase_5_v1_no_fault_control_has_no_deployment_rollback"),
        }
        failure_metric = primary["failure_impact_rate"]
        secondary["failed_requests_count"] = metric(
            failure_metric.get("failed_requests"),
            ("observed" if failure_metric.get("status") == "observed" else "missing"),
            failure_metric.get("source_event_ids", []),
            reason=failure_metric.get("reason"),
        )
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
            "manual_intervention_count": metric(
                len(events_of_type(events, "external_intervention")),
                "observed",
            ),
            "automation_decision_count": metric(
                len(events_of_type(events, "automation_evaluation")),
                "observed",
            ),
            "rollback_duration_ms": not_applicable("phase_5_v1_no_fault_control_excludes_deployment_rollback"),
        }

    source_digests = {name: canonical_source_sha256(path) for name, path in required_files.items()}
    return {
        "observation_version": "1.0.0",
        "analysis_tool_version": TOOL_VERSION,
        "evidence_class": "phase-5-development-validation",
        "eligible_for_primary_pilot_analysis": False,
        "trial_id": trial_id,
        "run_id": manifest["run_id"],
        "scenario_id": scenario_id,
        "automation_condition": condition,
        "repetition": manifest["repetition"],
        "run_order": manifest["run_order"],
        "repository_commit_sha": metadata["repository_commit_sha"],
        "pilot_batch_id": None,
        "primary_schedule_slot": None,
        "canonical_recovery_action_sha256": manifest.get("canonical_recovery_action_sha256"),
        "timing_contract": {
            "source": "controller_utc_event_timestamps",
            "fault_interval": "[injection_started,injection_ended)",
            "recovery_time_definition": "recovery_completed-injection_started",
            "recovery_completed_semantics": (
                "first_successful_functional_post_recovery_request"
                if scenario_id in FAULT_SCENARIOS
                else "not_applicable"
            ),
            "opentelemetry_used_for_primary_timing": False,
        },
        "primary_metrics": primary,
        "secondary_metrics": secondary,
        "request_latency_windows": derive_latency_windows(workload),
        "measurement_quality": measurement_quality(scenario_id, events, service_events, validity),
        "provenance": {
            "metric_catalogue": str(PHASE5_METRIC_CATALOGUE.relative_to(ROOT)),
            "metric_catalogue_sha256": sha256_file(PHASE5_METRIC_CATALOGUE),
            "raw_source_canonical_sha256": source_digests,
        },
    }


def numeric_metric_values(
    observations: list[dict[str, Any]],
    section: str,
    metric_id: str,
) -> list[dict[str, Any]]:
    """Extract observed numeric metric values with trial identity."""

    values: list[dict[str, Any]] = []
    for observation in observations:
        record = cast(dict[str, Any], observation[section][metric_id])
        if record.get("status") != "observed":
            continue
        value = record.get("value")
        if not isinstance(value, (int, float)):
            continue
        values.append(
            {
                "trial_id": observation["trial_id"],
                "value": float(value),
            }
        )
    return values


def descriptive_numeric(values: list[dict[str, Any]]) -> dict[str, Any]:
    """Return deterministic descriptive statistics for trial-level values."""

    numeric = [float(item["value"]) for item in values]
    if not numeric:
        return {
            "n": 0,
            "individual_values": [],
            "median": None,
            "q1": None,
            "q3": None,
            "iqr": None,
            "minimum": None,
            "maximum": None,
        }
    q1 = percentile_type7(numeric, 0.25)
    q3 = percentile_type7(numeric, 0.75)
    return {
        "n": len(numeric),
        "individual_values": values,
        "median": round(statistics.median(numeric), 6),
        "q1": round(q1, 6),
        "q3": round(q3, 6),
        "iqr": round(q3 - q1, 6),
        "minimum": round(min(numeric), 6),
        "maximum": round(max(numeric), 6),
    }


def summarise_observations(observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce descriptive per-cell development summaries only."""

    cells: list[dict[str, Any]] = []
    for scenario_id, condition in CELL_ORDER:
        selected = [
            observation
            for observation in observations
            if observation["scenario_id"] == scenario_id and observation["automation_condition"] == condition
        ]
        primary_summaries = {
            metric_id: descriptive_numeric(numeric_metric_values(selected, "primary_metrics", metric_id))
            for metric_id in (
                "detection_latency_ms",
                "recovery_time_ms",
                "failure_impact_rate",
            )
        }
        secondary_summaries = {
            metric_id: descriptive_numeric(numeric_metric_values(selected, "secondary_metrics", metric_id))
            for metric_id in (
                "active_recovery_duration_ms",
                "time_to_first_post_recovery_success_ms",
                "failed_requests_count",
                "latency_inflation_ratio",
                "recovery_success",
                "manual_intervention_count",
                "automation_decision_count",
            )
        }

        failure_records = [
            cast(dict[str, Any], observation["primary_metrics"]["failure_impact_rate"])
            for observation in selected
            if observation["primary_metrics"]["failure_impact_rate"]["status"] == "observed"
        ]
        cells.append(
            {
                "scenario_id": scenario_id,
                "automation_condition": condition,
                "attempted_trials": len(selected),
                "valid_trials": sum(
                    observation["measurement_quality"]["trial_valid"] is True for observation in selected
                ),
                "excluded_trials": sum(
                    observation["measurement_quality"]["trial_valid"] is not True for observation in selected
                ),
                "primary_metrics": primary_summaries,
                "secondary_metrics": secondary_summaries,
                "failure_impact_totals": {
                    "failed_requests": sum(int(record.get("failed_requests", 0)) for record in failure_records),
                    "offered_requests": sum(int(record.get("offered_requests", 0)) for record in failure_records),
                },
                "trial_latency_windows": [
                    {
                        "trial_id": observation["trial_id"],
                        "request_latency_windows": observation["request_latency_windows"],
                    }
                    for observation in selected
                ],
            }
        )

    return {
        "summary_version": "1.0.0",
        "analysis_tool_version": TOOL_VERSION,
        "analysis_tool_source_sha256": sha256_file(Path(__file__)),
        "evidence_class": "phase-5-development-validation",
        "eligible_for_primary_pilot_analysis": False,
        "descriptive_only": True,
        "confirmatory_inference": False,
        "p_values_included": False,
        "conditions_pooled": False,
        "no_fault_pooled_with_fault_scenarios": False,
        "quantile_method": "type-7-linear-interpolation",
        "development_run_count": len(observations),
        "cells": cells,
        "claim_boundary": {
            "supports": [
                "metric-derivation implementation validation",
                "descriptive development-run measurement quality",
            ],
            "does_not_support": [
                "manual-versus-automation effect estimates",
                "reliability improvement claims",
                "confirmatory inference",
                "production readiness",
                "human or developer-practice effects",
            ],
        },
    }


def build_development_outputs(
    index: dict[str, Any],
    raw_root: Path,
    index_path: Path = DEFAULT_INDEX,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Derive development observations and their descriptive validation summary."""

    if index.get("evidence_boundary") != EVIDENCE_BOUNDARY:
        raise ValueError("development index has an unexpected evidence boundary")
    if index.get("pilot_evidence") is not False:
        raise ValueError("development metric pipeline refuses pilot evidence indexes")

    entries = cast(list[dict[str, Any]], index.get("runs", []))
    observations = [derive_observation(raw_root / str(entry["trial_id"]), entry) for entry in entries]
    cells = {(observation["scenario_id"], observation["automation_condition"]) for observation in observations}
    if cells != set(CELL_ORDER):
        raise ValueError(f"development evidence does not cover the exact five cells: {cells}")

    processed = {
        "dataset_version": "1.0.0",
        "analysis_tool_version": TOOL_VERSION,
        "analysis_tool_source_sha256": sha256_file(Path(__file__)),
        "evidence_class": "phase-5-development-validation",
        "eligible_for_primary_pilot_analysis": False,
        "source_index": str(index_path.relative_to(ROOT)),
        "source_index_sha256": sha256_file(index_path),
        "observation_count": len(observations),
        "observations": observations,
    }
    return processed, summarise_observations(observations)


def write_deterministic(path: Path, payload: dict[str, Any]) -> None:
    """Write stable pretty JSON without timestamps or host-dependent fields."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    """CLI for deterministic development evidence derivation."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument(
        "--processed-output",
        type=Path,
        default=DEFAULT_PROCESSED_OUTPUT,
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_OUTPUT,
    )
    args = parser.parse_args()

    processed, summary = build_development_outputs(load_json(args.index), args.raw_root, args.index)
    write_deterministic(args.processed_output, processed)
    write_deterministic(args.summary_output, summary)

    print(
        json.dumps(
            {
                "analysis_tool_version": TOOL_VERSION,
                "development_observation_count": processed["observation_count"],
                "eligible_for_primary_pilot_analysis": False,
                "processed_output": str(args.processed_output),
                "processed_sha256": sha256_file(args.processed_output),
                "summary_output": str(args.summary_output),
                "summary_sha256": sha256_file(args.summary_output),
                "descriptive_only": True,
                "p_values_included": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI boundary
    raise SystemExit(main())
