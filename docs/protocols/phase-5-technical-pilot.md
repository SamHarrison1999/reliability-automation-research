# Phase 5 technical pilot protocol

**Protocol ID:** `phase-5-technical-pilot-v1`

**Status:** Design locked for implementation; pilot execution not started

**Related design record:** `../research-design/phase-5.md`

**Inherited metric catalogue:** `../metrics/technical-metrics.md`

**Inherited fault model:** `../fault-model/phase-3-fault-model.md`

## Purpose

Operationalise the Phase 3 recovery-condition comparison on the reproducible
Phase 4 Kubernetes prototype without expanding the treatment or claiming
confirmatory evidence.

This protocol governs Phase 5 implementation and pilot execution. It does not
rewrite the historical Phase 3 protocol or reclassify Phase 3/4 outputs.

## Technical question

Can the standardised external/manual recovery baseline and the rule-based
automated recovery condition be executed repeatedly on the same Kubernetes
prototype while preserving:

- the same fault;
- the same detector;
- the same recovery action;
- clean reset;
- auditable treatment identity;
- complete metric boundaries; and
- deterministic raw-to-analysis provenance?

The pilot may describe technical condition differences but is not powered for a
generalised effect claim.

## Target

Execution context:

`docker-desktop-kubernetes`

Prototype lineage:

`orderflow-phase-4-v1`

Required components:

- order-api;
- inventory;
- OpenTelemetry Collector;
- repository-controlled telemetry sink; and
- Phase 5 experiment controller outside the treatment services.

The experiment controller may patch trial identity/configuration and apply the
declared fault. It must not change application behaviour between conditions.

## Conditions

### Manual

Condition ID: `manual`

The shared detector records `fault_detected`. A separate baseline executor then
invokes the declared recovery action and records an externally initiated
intervention.

No person is a research participant in this condition and no artificial human
reaction delay is introduced.

### Automated

Condition ID: `automated`

The same detector records `fault_detected`. The rule-based recovery controller
then invokes the same declared recovery action and records the automation
decision and initiation.

### Treatment invariant

For a given scenario, the recovery command/action representation must hash or
canonicalise identically across conditions. A mismatch invalidates the trial
and blocks the pilot batch until reviewed.

## Scenarios

### no-fault-v1

Role: quality control.

Procedure:

1. verify clean namespace/target state;
2. deploy the declared Phase 5 configuration;
3. verify readiness and versions;
4. execute the fixed synthetic workload;
5. capture structured/OTel observation;
6. cleanup;
7. verify clean state.

No fault, recovery or deployment-transition treatment is executed.

### service-termination-v1

Target: `inventory`.

Trigger: after two successful pre-fault order requests.

Injection:

`kubectl scale deployment/inventory --replicas=0`

The controller verifies that the Deployment reports zero desired replicas and
that no inventory pod is ready before `injection_started` is considered
confirmed.

Detection:

three consecutive non-success order responses.

Inventory readiness failure is recorded as quality evidence but does not
short-circuit this workload-based detection rule.

Recovery in both conditions:

`kubectl scale deployment/inventory --replicas=1`

Completion requires inventory readiness and the first declared successful
post-recovery order response.

Cleanup independently verifies one healthy inventory replica before namespace
teardown/reset.

### dependency-latency-v1

Target: inventory dependency boundary.

Trigger: after two successful pre-fault order requests.

Injection:

```json
{"mode": "latency", "latency_ms": 120}
```

sent to inventory `POST /__control`.

The returned control state must confirm `mode=latency` and `latency_ms=120`.

Detection:

three consecutive completed order requests with observed latency greater than
100 ms.

Recovery in both conditions:

```json
{"mode": "none"}
```

sent to inventory `POST /__control`.

Completion requires returned `mode=none`, inventory readiness and the declared
post-recovery latency/success check.

Cleanup independently verifies `mode=none`.

## Allocation

Primary valid-trial target:

| Cell | Valid trials |
|---|---:|
| no-fault control | 10 |
| service termination / manual | 10 |
| service termination / automated | 10 |
| dependency latency / manual | 10 |
| dependency latency / automated | 10 |

Total: 50 valid trials.

Reserve allowance:

- 2 no-fault controls;
- 2 service-termination/manual;
- 2 service-termination/automated;
- 2 dependency-latency/manual;
- 2 dependency-latency/automated.

Maximum attempted slots under protocol v1: 60.

A reserve slot is activated only for the same cell as an invalid primary or
reserve trial. The invalid trial remains counted as attempted/excluded.

## Deterministic run order

Seed: `phase-5-pilot-run-order-v1`.

The primary order contains ten cycles of five trials.

Each cycle includes one instance of every pilot cell. The generator must ensure:

- service termination appears before dependency latency in exactly five cycles;
- dependency latency appears before service termination in exactly five cycles;
- manual appears before automated in exactly five service-termination cycles;
- automated appears before manual in the other five;
- manual appears before automated in exactly five dependency-latency cycles;
- automated appears before manual in the other five; and
- the no-fault control occupies positions 1-5 exactly twice each.

The generator may use a standard pseudo-random number generator only to choose
among schedules satisfying those constraints. Given the fixed seed and
manifest, the resulting schedule must be deterministic.

Before primary trial 1:

1. write the concrete order file;
2. write its SHA-256 into the batch manifest;
3. write the source manifest/protocol hashes;
4. refuse execution if any of those files change afterward.

Trial outcomes never influence the primary schedule.

Reserve trials are appended after the primary slot that establishes the need
for replacement, but their activation reason and source invalid trial ID are
recorded.

## Trial identity

Every attempted trial receives a unique `trial_id` before deployment.

Required trial-manifest fields include:

- protocol ID/version;
- batch ID;
- trial ID;
- schedule slot;
- cycle;
- scenario;
- condition;
- repetition;
- reserve flag;
- reserve activation reason/source trial ID when applicable;
- repository commit SHA;
- pilot-manifest SHA-256;
- protocol SHA-256;
- run-order SHA-256;
- Kubernetes manifest SHA-256;
- prototype manifest SHA-256;
- image identities;
- Collector identity;
- dependency-lock SHA-256;
- controller version;
- target/context versions; and
- UTC start timestamp.

The trial manifest is written before treatment execution and is immutable after
`trial_started`.

## Trial procedure

1. Verify source tree and batch files match the frozen hashes.
2. Verify there is no active Phase 5 namespace or unresolved contamination.
3. Materialise the immutable trial manifest.
4. Deploy/import the pinned Phase 4-derived images and Collector.
5. Patch trial identity/scenario/condition into both OrderFlow services.
6. Wait for telemetry sink, Collector, inventory and order-api readiness.
7. Verify versions, images and clean fault state.
8. Emit `trial_started`, reset/clean-state events and begin workload.
9. Complete two successful pre-fault requests for a fault trial.
10. Apply and positively verify the declared fault.
11. Emit `injection_started`.
12. Continue the fixed workload while evaluating the shared detector.
13. Emit detector evaluations and exactly one `fault_detected` boundary.
14. Invoke the condition-specific initiator path.
15. Assert that the canonical recovery action is the same for both conditions.
16. Emit `recovery_started` with the declared initiator.
17. Verify recovery completion.
18. Emit `recovery_completed` and close/revert the fault.
19. Complete two post-recovery workload requests/checks.
20. Capture structured events and OTel payload/span evidence.
21. Validate event completeness, detector/recovery identity and OTel parity.
22. Cleanup the namespace and independently verify absence/clean state.
23. Write validity/exclusion record and `trial_completed`.
24. Never overwrite or reuse the trial directory.

Cleanup executes even after workload, fault, detector or recovery failure.

A cleanup failure blocks the next slot.

## Workload

For fault scenarios:

- 2 successful pre-fault orders;
- fault injection;
- workload requests sufficient to satisfy or fail the declared three-observation
  detector;
- recovery;
- 2 post-recovery orders.

Nominal inter-request delay: 20 ms.

Request timeout: 2,000 ms.

Retries: 0.

The exact offered requests and all responses are retained. Requests continue
through the detection/recovery interval as implemented by the frozen workload
driver; metric windows are assigned by event timestamps rather than file order.

For no-fault quality control, the Phase 5 manifest defines a fixed request
count and the same workload generator/version used by the fault trials.

## Required technical events

Fault trials require at least:

```text
trial_started
reset_started
clean_state_verified
reset_completed
workload_started
workload_request
workload_response
injection_started
fault_detected
recovery_started
recovery_completed
injection_ended
post_recovery_check
observation_verified
otel_observation_verified
cleanup_completed
trial_completed
```

Automated trials additionally require an `automation_evaluation` record that
produces the recovery decision.

Manual trials additionally require an `external_intervention` record.

No-fault controls omit injection/detection/recovery events and require the
deployment/readiness/workload/observation/reset boundaries instead.

## Validity classification

The controller produces an explicit trial-level validity record.

Primary comparison validity requires:

- clean reset before workload;
- exact source/batch hashes;
- declared target and condition;
- positively verified fault application;
- one valid shared detection boundary;
- correct initiator;
- identical canonical recovery action across conditions;
- verified recovery;
- required event completeness;
- parseable timestamps;
- sufficient structured/OTel observation to establish required boundaries;
- post-recovery criterion;
- completed cleanup;
- no contamination before the next trial; and
- complete provenance.

A trial may retain usable secondary quality observations while being excluded
from a primary metric. Missing primary metric boundaries are never imputed.

## Stop conditions

Pause the batch before the next trial when:

- cleanup does not return the target to the clean fingerprint;
- a source/configuration file differs from the frozen batch hash;
- a fault cannot be reverted;
- the detector implementation is found to differ by condition;
- the canonical recovery action differs by condition;
- more than two reserve slots are exhausted in any one cell; or
- a failure reveals a protocol defect requiring a version change.

A protocol defect requires a new protocol/manifest version. Do not continue a
mixed-version primary batch and later pool it silently.

## Raw evidence

Each trial raw directory retains:

- immutable trial manifest;
- controller events;
- service events;
- workload records;
- OTel payload and decoded span records;
- environment/image/tool metadata;
- validity/exclusion record; and
- cleanup/reset evidence.

The batch root retains:

- frozen Phase 5 pilot manifest;
- concrete run order;
- batch manifest;
- trial index;
- exclusion ledger; and
- batch validity summary.

## Metric derivation

Metrics are derived only after trial validity classification from raw event
records using the Phase 3 metric definitions.

Every processed metric observation retains:

- batch/trial/run IDs;
- scenario and condition;
- metric ID/value/unit;
- numerator/denominator where applicable;
- source event IDs;
- raw-file SHA-256 values; and
- metric-derivation tool version.

No primary value is hand-entered or imputed.

`detection_latency_ms` is retained but interpreted as a shared-detector
fidelity/balance metric for this treatment design.

## Analysis

The pilot analysis reports descriptive values only:

- attempted/valid/excluded counts;
- exclusion reasons;
- individual trial metric values;
- median and IQR by condition x fault scenario;
- minimum/maximum where useful;
- failure-impact numerator/denominator;
- recovery-success counts;
- intervention/automation-decision counts; and
- measurement-quality indicators.

No-fault controls remain separate.

No p-value or confirmatory effect claim is part of protocol v1.

## Evidence boundary

Phase 5 technical records can support statements about the feasibility and
observed behaviour of this bounded pilot.

They cannot establish:

- universal reliability improvement;
- production readiness;
- effects in other systems/environments;
- human workload, trust, understanding or decision quality; or
- equivalence between scripted external recovery and real engineer behaviour.
