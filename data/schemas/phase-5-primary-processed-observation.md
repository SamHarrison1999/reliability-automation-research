# Phase 5 primary processed observation schema

**Schema version:** `1.0.0`

**Producer:** `analysis/phase_5/phase_5_primary_metrics.py`

Primary processed observations are deterministic derivatives of immutable
primary raw trial bundles.

## Required identity

A primary observation contains:

- `trial_id`
- `run_id`
- `scenario_id`
- `automation_condition`
- `repetition`
- `run_order`
- `primary_schedule_slot`
- `pilot_batch_id`
- `repository_commit_sha`
- `bound_source_commit_sha`
- `canonical_recovery_action_sha256`
- `analysis_tool_version`
- `timing_contract_version`
- `evidence_class = phase-5-primary-pilot`
- `eligible_for_primary_pilot_analysis = true`

The raw trial manifest must identify itself as
`phase-5-primary-trial-manifest` with evidence boundary
`technical-pilot-only`.

## Metric record

Metrics use:

```json
{
  "value": 123.456,
  "status": "observed",
  "source_event_ids": ["event-a", "event-b"]
}
```

Statuses are `observed`, `missing` or `not_applicable`.

Primary elapsed-time metrics require integer `monotonic_ns` on both required
controller boundaries. Missing monotonic time cannot use UTC fallback.

Failure impact also records:

- `failed_requests`
- `offered_requests`
- `unresolved_requests`

## Measurement quality

Each observation records primary monotonic completeness, invalid monotonic
event IDs, raw validity/classification, the duration clock and a machine-readable
`utc_fallback_permitted = false`.

## Provenance

Canonical semantic SHA-256 values are retained for each JSON/JSONL raw source
used by the derivation. The observation also records the exact primary metric
contract and pilot manifest SHA-256 values.

The batch-freeze step will additionally bind the primary execution and analysis
source files before trial 1.
