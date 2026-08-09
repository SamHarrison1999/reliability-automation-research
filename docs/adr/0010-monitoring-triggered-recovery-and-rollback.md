# ADR 0010: Use monitoring-triggered recovery with a bounded rollback extension

- **Status:** Recovery condition accepted for Phase 3 dry-runs; automated deployment rollback deferred pending its own validation
- **Date:** 2026-08-09
- **Related records:** ADR 0004, ADR 0005, ADR 0007, ADR 0008

## Context

The proposed comparison needs a technical automated-recovery condition. A
monitoring signal must trigger a pre-specified action, while the manual
baseline must use the same action and differ only in who or what initiates it.
Kubernetes also offers deployment revision rollback, but introducing faulty
deployments and rollback semantics into the first comparison would add a
second intervention dimension.

## Decision

1. Use a **versioned monitoring/detection rule** over declared service health,
   workload and telemetry events to emit `fault_detected`.
2. In the automated condition, the portable controller invokes a declared,
   reversible recovery action after the detection rule is satisfied.
3. In the manual baseline, the same recovery action is issued by the
   standardised external command after the same detection event. The command
   is scripted for reproducibility and is not evidence about human operator
   behaviour.
4. Record `fault_detected`, `recovery_started`, `recovery_completed`,
   `post_recovery_check` and cleanup events separately.
5. Treat **automated Kubernetes deployment rollback** as a bounded extension
   for a later dry-run. It is not part of the first manual-versus-automated
   recovery comparison until a faulty-deployment scenario, readiness window,
   rollback target and clean-reset test have passed.

## Alternatives considered

| Alternative | Reason not selected for the first comparison |
|---|---|
| Trigger recovery from the first failed request | Confounds fault occurrence, request scheduling and detection |
| Compare manual recovery directly with deployment rollback | Changes both recovery initiation and recovery mechanism |
| Trigger on an unversioned dashboard alert | Alert evaluation and buffering would not be reproducible |
| Allow an operator to choose the action | Introduces human behaviour before participant approval and weakens treatment control |

## Feasibility evidence

The fit probe records health, workload, fault, recovery, readiness, deployment
and rollback event classes in resettable synthetic runs. The Phase 3 protocol
defines the explicit detection and recovery boundaries required for a valid
comparison. This supports implementation feasibility and measurement design;
it is not evidence that monitoring-triggered recovery or rollback improves
reliability.

## Validation gate

Before the automated condition contributes to a pilot comparison:

- the detection rule must be identical across conditions;
- the same recovery action and version must be invoked;
- trigger, decision, action and completion timestamps must be present;
- recovery must be reversible and the clean-state fingerprint must pass; and
- an invalid or incomplete telemetry bundle must exclude the trial rather than
  silently impute a detection or recovery time.

