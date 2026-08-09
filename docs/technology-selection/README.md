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
| System | Minimal OrderFlow slice carried into the technical pilot | Accepted for bounded pilot |
| Packaging/runtime | Docker images; Docker Desktop Kubernetes primary local target | Accepted for bounded pilot |
| Local development | Docker Compose may support lightweight development/reset | Conditional |
| CI | Portable controller plus repository CI | Accepted boundary |
| Instrumentation | OpenTelemetry Python SDK → OTLP/HTTP → Collector trace path | Accepted for pinned small-trace path |
| Metrics backend | Prometheus remains a later candidate; raw records do not require a dashboard | Open |
| Recovery | Monitoring-triggered rule-based recovery for Phase 3 comparison | Accepted for dry-runs; pilot gate applies |
| Automated rollback | Kubernetes deployment rollback as a separately validated extension | Deferred |
| Progressive deployment | Canary/blue-green/progressive rollout | Deferred from first comparison |
| Fault injection | Harness-controlled service/dependency faults first | Accepted for bounded pilot |
| Human study | Not implemented or conducted | Deferred |

## Evidence rule

Official documentation establishes intended capability; the recorded fit probes
and compatibility result establish only technical feasibility for the tested
versions and scenarios. They do not establish reliability effects,
generalisability or human-participant claims. See
[`../adr/0012-phase-2-technology-decision-closeout.md`](../adr/0012-phase-2-technology-decision-closeout.md).
