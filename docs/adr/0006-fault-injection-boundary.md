# ADR 0006: Start with deterministic harness-controlled faults

- **Status:** Accepted for the first bounded technical pilot; platform-fault tools deferred
- **Date:** 2026-08-08

## Context

The first technical scenarios must be reproducible, targeted and reversible. Kubernetes fault-injection platforms may provide useful platform-level scenarios, but they can also introduce control-plane behaviour and cleanup requirements that complicate interpretation.

## Options considered

| Option | Evidence | Advantages | Risks/limitations |
|---|---|---|---|
| Harness-controlled application/dependency faults | Phase 0 control requirements | Deterministic timing, simple scenario manifests and direct explanation | Does not represent every platform-level failure mode |
| Chaos Mesh | [Overview](https://chaos-mesh.org/docs/) and [HTTP fault documentation](https://chaos-mesh.org/docs/simulate-http-chaos-on-kubernetes/) | Declarative Kubernetes faults across pod, network and HTTP boundaries | Operator/control-plane effects, version sensitivity and cleanup risk |
| Litmus | [Chaos workflow documentation](https://docs.litmuschaos.io/docs/3.5.0/concepts/chaos-workflow) | Composed experiments and explicit execution steps | Additional platform surface and feasibility cost for a small first probe |

## Decision

Use **harness-controlled application or dependency faults** for the first fit-probe scenarios. Carry Chaos Mesh as the primary Kubernetes fault-tool candidate and Litmus as an alternative. Do not select a platform fault tool for the technical pilot until targeting, reversion, timing and contamination checks pass.

## Validation

- Define scenario manifests independently of the automation condition.
- Verify that the same scenario can be invoked twice from a clean reset.
- Record injection-start, injection-end, observed-failure and recovery events.
- Confirm that cleanup returns the target and unrelated services to the expected state.
- Compare the harness fault with one platform fault before deciding whether platform-level injection is required.

## Consequences

The first comparison prioritises internal validity and repeatability. The eventual study may have narrower fault coverage than a general chaos-engineering platform. That limitation must be reported rather than hidden behind a broad tool choice.

## Phase 2 close-out

The local-process and Docker Desktop Kubernetes fit probes repeatedly targeted
the declared service/dependency boundaries, recorded injection and recovery
events, and returned to the clean state. This supports the harness-controlled
fault boundary for the first technical pilot. It does not establish coverage
of platform-level failures or show that a fault tool improves reliability.
