# ADR 0004: Evaluate Kubernetes as the primary experimental target

- **Status:** Accepted for Phase 2 fit probe
- **Date:** 2026-08-08

## Context

The proposed intervention includes deployment and rollback behaviour, and the project is concerned with continuous-delivery environments. The runtime must therefore expose versioned service deployment and health-state transitions without making local development impossible.

## Options considered

| Option | Evidence | Advantages | Risks/limitations |
|---|---|---|---|
| Docker Compose as primary target | [Compose documentation](https://docs.docker.com/compose/) | Low resource cost, declarative multi-container lifecycle and easy local reset | Does not by itself represent cluster scheduling, rollout or Kubernetes-oriented fault mechanisms |
| Kubernetes as primary target | [Kubernetes overview](https://kubernetes.io/docs/concepts/overview/) | Represents container orchestration, service discovery, deployment and cluster health behaviour | Control-plane complexity, resource cost, version sensitivity and possible timing contamination |
| Compose for development plus Kubernetes for experiments | Official documentation and Phase 0 cloud-native direction | Separates low-cost development from the target environment | Parity between environments becomes a validity condition rather than an assumption |

## Decision

Evaluate **Kubernetes as the primary experimental target**. Docker Compose may support local development or a lightweight reset path, but technical pilot results must identify the environment in which they were collected. No claim of Compose/Kubernetes equivalence may be made without a parity check.

## Validation

- Record exact runtime and cluster versions.
- Measure clean start, health readiness, deployment update and rollback times.
- Verify that the same service-level health and telemetry contract works in the intended local and CI environments.
- Test whether the fault-injection candidate can target and revert one service without affecting unrelated services.
- Record resource requirements and whether repeated resets contaminate later runs.

## Consequences

Kubernetes is a methodological dependency and a possible confounder. The protocol must distinguish application recovery from orchestration recovery. If the fit probe shows that the control plane prevents reliable repeated runs, this ADR must be revisited before implementation proceeds.
