# Phase 5 technical metric derivation contract

**Status:** Locked before primary pilot execution

**Protocol:** `phase-5-technical-pilot-v1`

**Parent catalogue:** [`technical-metrics.md`](technical-metrics.md)

**Analysis tool:** `phase-5-metric-derivation-v1.0`

This document preserves the Phase 3 technical metric catalogue while fixing
the exact Phase 5 implementation boundaries before any primary pilot trial is
executed.

## Primary metrics

For fault trials:

| Metric | Phase 5 v1 derivation |
|---|---|
| `detection_latency_ms` | `timestamp(fault_detected) - timestamp(injection_started)` |
| `recovery_time_ms` | `timestamp(recovery_completed) - timestamp(injection_started)` |
| `failure_impact_rate` | failed paired responses / offered requests whose `workload_request` timestamp falls in `[injection_started, injection_ended)` |

`injection_started` is the controller boundary emitted after positive
verification that the declared fault is active. It is the operational start of
the measured fault interval; Kubernetes command invocation time is not folded
into detection latency.

`recovery_completed` is functional in Phase 5 v1: it is emitted only after the
first successful post-recovery order response. A successful command/readiness
boundary alone is recorded separately as `recovery_action_completed`.

The no-fault control records all three primary fault metrics as
`not_applicable`, never as zero.

## Missing data

No boundary is imputed. A missing or duplicate required boundary produces a
metric with `status=missing` and a reason. Failure impact is also missing when
an offered request in the fault interval cannot be paired with exactly one
response. The numerator, denominator and unresolved count remain visible.

A trial can therefore retain measurement-quality information even when one
specific metric is missing.

## Secondary metrics

- `active_recovery_duration_ms`:
  `recovery_completed - recovery_started`.
- `time_to_first_post_recovery_success_ms`: the successful
  `workload_response` explicitly referenced by `recovery_completed`, minus
  `injection_started`.
- `failed_requests_count`: numerator from failure impact.
- request latency p50: ordinary median within the declared phase/window.
- request latency p95: Type-7 linear interpolation, reported only for windows
  containing at least five completed responses.
- `latency_inflation_ratio`: median during-fault latency / median pre-fault
  latency within the same trial.
- `recovery_success`: one only when recovery action completion, functional
  recovery and `post_recovery_check=result:passed` are all present.
- `manual_intervention_count`: number of `external_intervention` events.
- `automation_decision_count`: number of `automation_evaluation` events.
- rollback duration: not applicable to Phase 5 v1 because the no-fault control
  deliberately excludes deployment transition/rollback.

Latency inflation for service termination is descriptive only; rapid failure
responses can make this ratio less intuitive than in the latency-fault cell.

## Time and telemetry authority

Controller UTC event timestamps remain the Phase 5 v1 duration source because
the Phase 3 catalogue pre-specified UTC event timing and all required
boundaries are controller-authored in one process. Durations with negative,
missing or unparseable boundaries are rejected.

OpenTelemetry is corroborative only. OTLP export timing, Collector timing and
synchronous exporter completion are never used in a primary duration metric.

## Percentiles and quartiles

All interpolated quantiles use the Type-7 rule:

`h = (n - 1) * p`

with linear interpolation between the adjacent ordered observations.

Cell-summary Q1/Q3/IQR therefore use `p=.25` and `p=.75`; p95 uses `p=.95`.
This rule is dependency-free and version-stable.

## Source provenance

Every processed observation retains trial/run identity, repository commit,
recovery-action identity, metric source event IDs and canonical semantic
SHA-256 values for its JSON/JSONL raw inputs.

Canonical source hashes parse JSON/JSONL and re-serialise sorted compact JSON
before hashing. This makes provenance stable across the repository's deliberate
LF text canonicalisation and Windows working-tree newline behaviour without
modifying raw evidence.

## Development/pilot separation

The Slice 5 validation inputs are the five committed development-validation
runs. Their processed output is written under
`data/processed/phase-5/development/` and is machine-labelled
`eligible_for_primary_pilot_analysis=false`.

The later primary pilot will use a separately frozen batch and processed
dataset. Development observations are never appended to, pooled with or
relabelled as primary pilot observations.

## Analysis boundary

Phase 5 v1 summaries report individual values and descriptive statistics by
scenario × condition. No-fault remains separate. No p-values, null-hypothesis
tests, powered-effect claims or generalised causal conclusions are produced by
this pipeline.
