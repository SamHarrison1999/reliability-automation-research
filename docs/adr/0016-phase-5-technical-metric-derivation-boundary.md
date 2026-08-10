# ADR 0016: Phase 5 technical metric derivation boundary

**Status:** Accepted

**Date:** 2026-08-10

## Context

The Phase 5 technical controller and five development-validation cells are
implemented before primary pilot execution. Metric derivation must now be
frozen before the 50-valid-trial batch so analysis decisions cannot adapt to
observed pilot outcomes.

The Phase 3 catalogue already defines the primary constructs. Phase 5 adds a
functional recovery boundary, Kubernetes-specific fault application and a
strict development/pilot evidence separation.

## Decision

1. Preserve the Phase 3 primary definitions for detection latency, fault-
   relative recovery time and failure impact.
2. Treat Phase 5 `injection_started` as the positively verified active-fault
   boundary.
3. Treat Phase 5 `recovery_completed` as functional recovery, anchored after
   the first successful post-recovery order response.
4. Keep `recovery_action_completed` separate so command/readiness completion
   cannot substitute for usable recovery.
5. Use controller UTC event timestamps for primary duration metrics. OTel is
   corroborative only.
6. Assign offered requests to the half-open fault interval by the recorded
   `workload_request` timestamp.
7. Do not impute missing/duplicate boundaries or unresolved responses.
8. Use Type-7 linear interpolation for quartiles and p95; suppress p95 below
   five completed responses.
9. Generate only descriptive per-cell summaries in Phase 5 v1.
10. Store development-derived outputs separately and mark them ineligible for
    primary pilot analysis.
11. Use canonical semantic SHA-256 provenance for JSON/JSONL source content so
    repository EOL normalisation cannot create false source-identity drift.
12. Add the `analysis/` tree to the repository lint, format, mypy and Bandit
    quality boundary.

## Consequences

The pilot analysis contract is fixed before primary data collection. Recovery
time includes detection plus recovery and ends only when the service has
demonstrated a successful post-recovery request. Active recovery duration is
available separately.

Development timings can validate derivation mechanics but cannot estimate
manual-versus-automation effects. The later primary batch must not import the
five development observations.

No new claim about reliability improvement, production readiness, humans or
generalisability follows from accepting this ADR.
