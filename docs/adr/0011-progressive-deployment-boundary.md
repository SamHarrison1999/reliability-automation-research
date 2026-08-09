# ADR 0011: Defer progressive deployment from the first technical comparison

- **Status:** Accepted as a scope boundary for Phase 3; future extension
- **Date:** 2026-08-09
- **Related records:** ADR 0004, ADR 0007 and ADR 0010

## Context

Canary or progressive deployment is relevant to continuous delivery, but it
changes traffic allocation, exposure duration, promotion criteria and rollback
semantics at the same time as the recovery strategy. Those variables would make
the first comparison harder to attribute and would require a separate
faulty-deployment scenario.

## Decision

Do not include canary, blue/green or other progressive deployment in the first
Phase 3 technical comparison. Use a single declared deployment revision per
trial and keep the initial comparison focused on monitoring-triggered recovery
under service-termination and dependency-latency faults.

Progressive deployment may be added only as a separately versioned protocol
extension after its traffic split, promotion gate, exposure window, rollback
target, reset contract and contamination checks have been validated.

## Evidence and consequences

The Phase 2 fit probe demonstrated resettable service boundaries and a version
transition/rollback event path, while the Phase 3 design identifies canary
deployment as an additional intervention dimension. This supports deferring it
for control and feasibility reasons. It does not establish that progressive
deployment is harmful or that the selected single-revision model is superior
in production.

