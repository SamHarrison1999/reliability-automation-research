# ADR 0007: Bound the first technical comparison to recovery initiation

- **Status:** Proposed for Phase 3 review
- **Date:** 2026-08-09
- **Related records:** ADR 0003, ADR 0004, ADR 0005 and ADR 0006

## Context

Phase 2 established a provisional OrderFlow slice, a portable controller, deterministic harness faults and a structured telemetry contract. Phase 3 must define a comparison that can isolate reliability-automation effects without adding a large application, a human-participant study or several intervention dimensions at once.

The initial fit-probe scenarios are suitable feasibility cases, but the existing records do not yet contain a condition label or the complete detection-event boundary needed for a technical comparison. A protocol is therefore required before new trial data is collected.

## Decision

1. Compare a standardised manual-recovery baseline with a rule-based automated-recovery condition.
2. Hold the fault manifest, workload, detection rule, versions, target environment and reset contract constant within a comparison block.
3. Use the existing no-fault, service-termination and dependency-latency scenarios as the initial catalogue.
4. Treat detection latency, recovery time and failure-impact rate as primary technical outcomes.
5. Require explicit `fault_detected`, condition-labelled `recovery_started`, `recovery_completed`, cleanup and validity events before a trial can contribute to a primary comparison.
6. Keep a scripted manual baseline as a technical control; do not interpret its intervention count as human behaviour.
7. Defer faulty deployments, platform-level chaos tools, cascading faults and canary deployment until separate validation tasks are passed.

## Alternatives considered

| Alternative | Reason not selected for the first comparison |
|---|---|
| Compare manual recovery with automated rollback immediately | Requires a faulty-deployment scenario and introduces rollback semantics as a second intervention dimension |
| Use real human operators for the technical pilot | Would mix technical reliability outcomes with human-participant evidence before protocol and ethics approval |
| Add Chaos Mesh or Litmus now | Adds platform/control-plane and cleanup variables before the harness boundary is validated |
| Pool all fault classes into one reliability score | Hides scenario-specific mechanisms and makes attribution ambiguous |
| Infer detection from the first failed request | Confounds fault occurrence, request scheduling and detection; an explicit detection event is required |

## Consequences

The design has stronger internal control and a clear measurement boundary, but the scripted baseline cannot answer the human engineering-practice question. The first comparison has narrower fault coverage and should be reported as a technical pilot. A later protocol amendment may add deployment rollback or platform faults only after their own fault, reset and validity criteria are defined.

## Validation required before acceptance

- Implement the trial-manifest and condition fields.
- Demonstrate that manual and automated conditions invoke the same recovery operation.
- Record explicit detection and recovery decision events.
- Run dry-runs for every scenario and condition without treating them as pilot evidence.
- Verify clean reset and contamination checks between trials.
- Test event export, ordering and loss using the selected OpenTelemetry path or document the structured-contract limitation.
- Review the design against the completed Phase 1 evidence map.
