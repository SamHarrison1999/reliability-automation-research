# Phase 3 fault model and scenario catalogue

**Status:** Final design boundary; protocol-supporting implementation and repeat dry-run validation complete

**System boundary:** Minimal OrderFlow slice (`order-api` → `inventory`)

**Evidence type:** Synthetic technical records only

## Purpose

This document defines which failures are in scope for the first technical comparison and which are deliberately deferred. A fault is an experimental treatment only when its target, trigger, exposure window, reversion, expected observations and reset test are specified before execution.

## Fault-model dimensions

| Dimension | Required definition |
|---|---|
| Target | One named service or dependency; no wildcard targeting |
| Fault mode | Controlled availability or latency perturbation |
| Trigger | Deterministic request count or controller event |
| Exposure window | Injection start and injection end recorded in UTC |
| Recovery | Named action and initiator: manual baseline or rule-based automation |
| Reversion | Explicit command or platform action returning the target to its expected state |
| Workload | Fixed request counts before, during and after the fault |
| Expected effect | Pre-specified observable change in service response or latency |
| State safety | No real payment, personal or persistent business data |
| Reset test | Readiness plus clean-state fingerprint before the next trial |

## In-scope scenario catalogue

| Scenario | Fault class | Target | Trigger | Exposure | Recovery action | Expected technical signal |
|---|---|---|---|---|---|---|
| `no-fault-v1` | Baseline/control | None | Fixed workload start | No fault | Version transition and rollback only | No fault-relative interval; deployment and rollback events present |
| `service-termination-v1` | Availability failure | `inventory` | After two successful requests | Until recovery action begins | Restart/restore `inventory` | Failed requests during unavailability, then successful post-recovery requests |
| `dependency-latency-v1` | Performance degradation | `inventory` dependency boundary | After two successful requests | 120 ms injected latency until clear | Clear latency fault | Increased request latency during the fault window, with reversion afterward |

The existing JSON manifests under `experiments/scenarios/` remain Phase 2 feasibility manifests. The locked Phase 3 design manifest at `experiments/manifests/phase-3-trial-manifest.json` adds the automation condition, repetition, run-order position, detection-rule version and expected recovery action without changing the underlying fault definition.

## Scenario invariants

The following must remain constant across recovery conditions within a scenario block:

- scenario manifest and fault parameters;
- target component and dependency topology;
- workload request counts and request-generation version;
- service and infrastructure versions;
- detection rule and threshold;
- clean-reset contract;
- observation window definitions; and
- target environment for the comparison block.

The recovery initiator and the condition-specific recovery command are the only planned treatment differences.

## Detection boundary

The pilot must distinguish four events that are currently only partially represented by the fit probe:

1. `injection_started`: the controller has applied the declared fault;
2. `fault_detected`: the shared detection rule has been satisfied;
3. `recovery_started`: a recovery action has begun, with `initiator` set to `manual` or `automation`;
4. `recovery_completed`: the target has passed the declared recovery/readiness check.

For automated recovery, the protocol should additionally record `automation_evaluation` with the rule version, observed signal and decision. For the manual baseline, the external recovery command must be recorded as an intervention event.

The existing fit-probe event bundles can support feasibility checks, but runs lacking `fault_detected` and condition labels must not be backfilled and analysed as Phase 3 trials.

## Recovery semantics

### Service termination

- Manual baseline: external command restarts the `inventory` service after detection.
- Automated condition: the rule-based controller invokes the same restart operation after the same detection rule is satisfied.
- Completion: the `inventory` readiness check succeeds and the post-recovery workload receives the declared successful response.

### Dependency latency

- Manual baseline: external command clears the injected latency after detection.
- Automated condition: the rule-based controller clears the same latency fault after the same detection rule is satisfied.
- Completion: the dependency readiness check succeeds and the post-recovery latency observation window is recorded.

### No-fault baseline

No recovery comparison is made. The scenario verifies ordinary workload, version transition, rollback, reset and telemetry behaviour. It is a quality-control scenario and may be used to estimate normal request latency for within-run comparisons.

## Deferred fault classes

| Deferred class | Reason for deferral |
|---|---|
| Faulty deployment | Requires a versioned defect model and a clear rollback treatment |
| Dependency hard failure | Adds a second availability mechanism before latency semantics are validated |
| Network partition or packet loss | Adds platform/control-plane and timing complexity |
| Database corruption or persistent state fault | Conflicts with the no-persistent-data and clean-reset boundary |
| Multi-target or cascading faults | Makes attribution and blast-radius interpretation ambiguous |
| Chaos Mesh/Litmus fault injection | Requires independent targeting, reversion and contamination validation |
| Canary/progressive deployment fault | Adds another intervention dimension and is already deferred by Phase 0 |

## Fault validity checks

A fault application is valid only if all of the following are recorded:

- declared target matches the observed target;
- injection start and end events are present and ordered;
- the intended fault signal is observable in the workload or service events;
- the recovery action is attributable to the declared condition;
- the target returns to the expected state; and
- the next reset passes without residual fault state.

If a fault cannot be applied or reverted cleanly, preserve the raw records, mark the trial invalid, record the reason and do not replace the run with an unlogged manual repair.
