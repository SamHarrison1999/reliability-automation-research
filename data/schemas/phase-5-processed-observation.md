# Phase 5 processed technical observation schema

**Schema version:** `1.0.0`

**Producer:** `analysis/phase_5/phase_5_metrics.py`

A processed observation is a deterministic raw-derived record. It never
replaces the raw trial directory.

## Identity

Required fields:

- `trial_id`
- `run_id`
- `scenario_id`
- `automation_condition`
- `repetition`
- `run_order`
- `repository_commit_sha`
- `canonical_recovery_action_sha256`
- `evidence_class`
- `eligible_for_primary_pilot_analysis`
- `analysis_tool_version`
- `analysis_tool_source_sha256`

Development validation must have:

- `evidence_class = phase-5-development-validation`
- `eligible_for_primary_pilot_analysis = false`
- `pilot_batch_id = null`
- `primary_schedule_slot = null`

## Metric record

Each primary/secondary metric uses:

```json
{
  "value": 123.0,
  "status": "observed",
  "source_event_ids": ["event-a", "event-b"]
}
```

Allowed statuses are:

- `observed`
- `missing`
- `not_applicable`

Missing metrics add a machine-readable `reason`. No missing metric is assigned
a substitute numeric value.

Failure impact additionally retains:

- `failed_requests`
- `offered_requests`
- `unresolved_requests`

## Request latency windows

Each declared phase/window includes count, minimum, maximum, p50 and p95.
`p95_ms` is null with `p95_status=insufficient_count` when fewer than five
completed request latency observations exist.

## Measurement quality

The observation records:

- required-event completeness
- timestamp completeness
- trace-correlation completeness
- reset duration
- pre/post clean-state result
- contamination flag
- raw validity decision/classification

## Provenance

`raw_source_canonical_sha256` contains a semantic digest for each parsed
JSON/JSONL input used in derivation. Metric source-event IDs provide the
boundary-level audit trail.

Processed development outputs are validation fixtures for the analysis
pipeline. They are not pilot observations and must never be pooled with the
future primary dataset.
