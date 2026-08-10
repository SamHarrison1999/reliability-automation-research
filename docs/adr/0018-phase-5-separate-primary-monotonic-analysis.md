# ADR 0018: Separate primary monotonic analysis path

**Status:** Accepted

**Date:** 2026-08-10

## Context

The five Phase 5 development-validation trials and their derived outputs were
committed before the pre-primary timing correction. Those development outputs
used the inherited UTC-duration implementation.

ADR 0017 then required future primary elapsed-duration metrics to use
same-controller-process `monotonic_ns` without UTC fallback.

Changing the existing development-analysis module in place would make its
historical role less clear and could create accidental reinterpretation of
already committed development outputs.

## Decision

1. Leave `analysis/phase_5/phase_5_metrics.py` as the historical
   development-validation analysis path.
2. Add `analysis/phase_5/phase_5_primary_metrics.py` as the only primary
   per-trial derivation path.
3. Require primary duration and fault-window membership to use
   `monotonic_ns`.
4. Forbid UTC fallback for primary timing.
5. Reject development evidence in the primary tool.
6. Require primary batch/slot/repetition/run-order identity and the frozen
   primary evidence boundary.
7. Keep OpenTelemetry outside primary timing derivation.
8. Test the primary derivation semantics synthetically before any primary raw
   trial exists.
9. Do not execute a Kubernetes trial as part of this change.

## Consequences

Historical development outputs remain unchanged and reproducible under their
recorded analysis version.

The later batch-freeze record can bind a distinct primary metric tool by exact
SHA-256 before primary trial 1.

Primary raw evidence with missing monotonic boundaries cannot be made usable by
substituting wall-clock UTC.
