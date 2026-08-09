# ADR 0012: Close Phase 2 technology decisions for the bounded technical pilot

- **Status:** Accepted for the bounded Phase 3 technical pilot
- **Date:** 2026-08-09
- **Related records:** ADR 0003–0011

## Decision summary

| Area | Decision | Evidence boundary |
|---|---|---|
| System | Carry the minimal purpose-built OrderFlow slice forward | Local and Docker Desktop Kubernetes fit probes; synthetic feasibility only |
| Packaging/runtime | Build bounded services as Docker images and use Docker Desktop Kubernetes as the primary local experimental target | Four Kubernetes runs passed their declared checks, including a clean-reset repeat |
| Local development | Docker Compose/local process may support development and diagnosis | No Compose/Kubernetes equivalence claim without a parity check |
| CI/CD | GitHub Actions validates code, infrastructure and repository boundaries; the portable controller executes trials | Workflow/scripts and fit-probe provenance boundary |
| Observability | Use the pinned Python OpenTelemetry SDK → OTLP/HTTP → Collector trace path with raw capture; retain JSONL as the audit-friendly event boundary | Two Windows runs passed; corrected run decoded all five spans in order |
| Metrics backend | Keep Prometheus as a later metrics-backend candidate; dashboards are not required for raw evidence | Backend suitability and load behaviour remain untested |
| Recovery | Use a shared monitoring/detection rule and compare scripted manual initiation with rule-based automated initiation | Phase 3 protocol and dry-run gate; no reliability-effect claim |
| Automated rollback | Keep Kubernetes deployment rollback as a separately validated extension | Local version rollback exists; Kubernetes rollback semantics are not accepted as a completed intervention validation |
| Progressive deployment | Defer canary/blue-green/progressive deployment from the first comparison | Scope/control decision, not a performance or reliability finding |
| Fault injection | Use deterministic harness-controlled service/dependency faults first; do not add Chaos Mesh/Litmus yet | Repeated targeting/reversion evidence; broader platform-fault coverage remains future work |

## Evidence rule

These decisions establish a feasible, bounded implementation and measurement
boundary. They do not establish reliability effects, production readiness,
generalisability, human workload, trust, understanding or decision rationale.
The Phase 3 dry-runs and later technical pilot must preserve the target model,
condition labels, manifests, reset checks, telemetry validity checks and
exclusion ledger.

## Exit criteria recorded

- local-process and Docker Desktop Kubernetes fit-probe evidence is retained
  separately;
- the OpenTelemetry compatibility probe passed for the pinned trace path;
- every selected or deferred technology has an explicit validation boundary;
- progressive deployment and automated deployment rollback are not silently
  introduced into the first comparison; and
- no participant or production data has been collected.

