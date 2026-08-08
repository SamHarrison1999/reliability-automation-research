# Technology selection

Phase 2 compares candidate systems and tools against research criteria. The scores are provisional desk-research judgements. They are not empirical findings and must be challenged by the fit probe described in [`../research-design/phase-2.md`](../research-design/phase-2.md).

## Selection boundary

The study needs a small, stateful, multi-service system with:

- a controlled workload;
- observable service and dependency boundaries;
- a safe way to introduce deterministic failures;
- versioned deployment and rollback behaviour; and
- a clean reset that can be repeated without using real payments, personal data or production traffic.

The first candidate is the purpose-built **OrderFlow** benchmark. An adapted open-source benchmark remains a comparator because reuse may improve external validity while reducing control over state, dependencies and participant-facing explanations.

## Decision status

| Area | Phase 2 position | Status |
|---|---|---|
| System | OrderFlow carried into fit probe | Provisional |
| Experimental target | Kubernetes evaluated as primary target | Provisional |
| Local development | Docker Compose may support lightweight development/reset | Conditional |
| CI | Portable controller plus repository CI | Accepted boundary |
| Instrumentation | OpenTelemetry candidate | Provisional |
| Metrics backend | Prometheus candidate | Provisional |
| Fault injection | Harness-controlled faults first; Chaos Mesh candidate for Kubernetes | Provisional |
| Human study | Not implemented or conducted | Deferred |

## Evidence rule

Official documentation is used to establish what a tool is designed to provide. It does not establish that the tool will behave adequately in this experiment. That requires a versioned fit probe with measured reset, targeting, reversion and telemetry checks.

