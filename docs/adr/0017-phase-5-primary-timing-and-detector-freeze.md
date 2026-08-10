# ADR 0017: Phase 5 primary timing and detector freeze correction

**Status:** Accepted

**Date:** 2026-08-10

## Context

The five Phase 5 development-validation cells and their deterministic derived
development outputs were committed before primary data collection. A
pre-primary inspection then identified two operational specification gaps:

1. both detector descriptions stated "three consecutive" observations in prose
   but the machine-readable pilot manifest did not expose the observation count
   as a numeric field; and
2. primary elapsed-duration metrics were still specified against millisecond
   UTC wall-clock timestamps even though all compared boundaries are authored
   by one controller process.

The inspection also confirmed that fault-start semantics were already
implemented correctly: `fault_application_verified` precedes
`injection_started`.

No primary pilot trial had been executed when this correction was accepted.

## Decision

1. Increment the pilot manifest to `1.1.0`.
2. Set `detection_window_request_count = 3` in the shared workload and both
   fault detector rules.
3. Preserve `timestamp` as the UTC audit clock.
4. Add integer `monotonic_ns` to every future controller-authored event.
5. Increment the single-trial controller to
   `phase-5-single-trial-controller-v0.2`.
6. Require primary elapsed durations to use same-controller-process
   `monotonic_ns` differences converted to milliseconds.
7. Require primary failure-interval request membership to use monotonic
   boundaries.
8. Do not fall back to UTC when a required primary monotonic boundary is
   missing or invalid.
9. Keep OpenTelemetry corroborative only.
10. Keep `injection_started` after positive fault verification.
11. Keep `recovery_action_completed`, `injection_ended` and functional
    `recovery_completed` as distinct boundaries.
12. Do not rewrite the five committed development raw bundles or their
    `phase-5-metric-derivation-v1.0` outputs.
13. Do not execute an additional Kubernetes development trial solely for this
    instrumentation correction; validate it through static contract checks,
    controller/unit tests and the full repository quality gate before the
    primary batch is frozen.

## Rationale

A monotonic clock is not subject to wall-clock adjustments and is therefore
the stronger source for elapsed time measured wholly within one controller
process. Retaining UTC alongside it preserves human-readable provenance and
cross-record auditability.

The change occurs before primary data and therefore avoids mixing timing
definitions within the primary dataset.

## Consequences

Historical development timing values remain valid only as implementation and
analysis-pipeline validation evidence under their recorded v1.0 derivation.
They are not reanalysed to manufacture monotonic values that were never
recorded.

Every primary trial must contain `monotonic_ns` on the required controller
events. Missing monotonic boundaries produce missing primary duration metrics
and may contribute to trial/metric exclusion according to the frozen protocol.

This correction changes measurement instrumentation, not the treatment,
fault, detector logic, workload allocation, recovery action or research claim
boundary.
