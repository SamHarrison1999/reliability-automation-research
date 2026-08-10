# Phase 5 primary pilot analysis contract

**Status:** Pre-primary; implementation frozen before the batch is generated

**Protocol:** `phase-5-technical-pilot-v1`

**Timing contract:** `phase-5-primary-timing-v1`

**Analysis tool:** `phase-5-primary-metric-derivation-v1.0`

This contract applies only to future primary Phase 5 raw trials. It does not
replace or reinterpret the five committed development-validation observations.

## Separation from development analysis

`analysis/phase_5/phase_5_metrics.py` remains the historical development
derivation implementation. Its committed outputs used inherited UTC event
timing and remain implementation-feasibility evidence only.

Primary trials use the separate
`analysis/phase_5/phase_5_primary_metrics.py` path. Development evidence is
explicitly rejected by the primary tool.

## Primary timing

Every controller-authored primary event must contain:

- `timestamp`: UTC audit time;
- `monotonic_ns`: same-controller-process monotonic time.

Primary elapsed durations use only `monotonic_ns`. UTC must never substitute
for a missing, invalid or negative monotonic boundary.

The primary formulas are:

- `detection_latency_ms` =
  `(fault_detected.monotonic_ns - injection_started.monotonic_ns) / 1_000_000`;
- `recovery_time_ms` =
  `(recovery_completed.monotonic_ns - injection_started.monotonic_ns) / 1_000_000`;
- `active_recovery_duration_ms` =
  `(recovery_completed.monotonic_ns - recovery_started.monotonic_ns) / 1_000_000`;
- `time_to_first_post_recovery_success_ms` uses the successful
  `workload_response` referenced by `recovery_completed`, minus
  `injection_started`, again using monotonic time.

No monotonic subtraction is valid across processes.

## Fault interval and failure impact

The primary fault interval remains half-open:

`[injection_started, injection_ended)`

Offered requests belong to the fault interval according to controller
`monotonic_ns`, not UTC and not their JSONL file position.

`failure_impact_rate` is:

`failed paired responses / offered requests in the monotonic fault interval`

The numerator, denominator and unresolved count are retained. A request without
exactly one paired response makes failure impact missing rather than silently
counting it as either success or failure.

## Functional recovery

`fault_application_verified` precedes `injection_started`.

`recovery_action_completed` records successful technical recovery-action
completion. `injection_ended` records fault reversion.
`recovery_completed` follows the first successful functional post-recovery
request. `post_recovery_check` records the two-request stability window.

The primary recovery metric therefore remains fault-relative and ends at
functional recovery, not command completion.

## No-fault control

The no-fault control does not possess detection, recovery or fault-impact
outcomes. Those primary metrics are `not_applicable`; they are never encoded as
zero.

## Request latency summaries

p50 is the ordinary median.

p95 uses Type-7 linear interpolation and is reported only for a declared window
with at least five completed latency observations. Smaller windows retain
`p95_ms = null` and `p95_status = insufficient_count`.

## Primary trial identity

A primary observation is accepted only when its raw manifest and validity file
agree on:

- evidence boundary `technical-pilot-only`;
- non-empty `pilot_batch_id`;
- positive `primary_schedule_slot`;
- positive `repetition`;
- positive `run_order`;
- pilot manifest version `1.1.0`;
- controller version `phase-5-single-trial-controller-v0.2`.

The frozen batch will add stronger source-file and schedule binding before any
primary execution.

## Missing data and exclusion

No missing metric boundary is imputed. Missing or invalid monotonic timing is
reported as missing and cannot fall back to UTC.

Raw trial validity remains authoritative for trial inclusion. Metric-level
missingness remains visible even when other trial quality evidence is retained.

## Analysis boundary

The future 50-valid-trial pilot is descriptive:

- individual trial values;
- valid/excluded counts;
- median, Q1, Q3, IQR and useful minimum/maximum values per fault
  scenario × condition;
- failure-impact numerators and denominators;
- recovery-success counts;
- intervention and automation-decision counts;
- measurement-quality indicators and exclusion ledger.

No p-values, null-hypothesis tests, powered-effect claims, production-readiness
claims, human-effect claims or universal reliability claims are produced by
this primary path.
