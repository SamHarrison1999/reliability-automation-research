# Phase 3 technical experiment protocol

**Protocol ID:** `phase-3-technical-reliability-v1`

**Status:** Draft for review; do not treat dry-runs as pilot evidence

**Related design record:** [`../research-design/phase-3.md`](../research-design/phase-3.md)

**Metric catalogue:** [`../metrics/technical-metrics.md`](../metrics/technical-metrics.md)

## Objective

Produce comparable, reproducible technical trials for the minimal OrderFlow slice under a bounded fault model. The protocol is designed to estimate whether the proposed measurement and reset procedures are feasible and to prepare a later technical pilot; it does not establish that one reliability-automation strategy is universally superior.

## Research question or feasibility claim addressed

The protocol addresses the technical part of RQ1: whether a standardised manual-recovery baseline and a rule-based automated-recovery condition can be compared using detection latency, recovery time, failure impact and intervention records under controlled faults.

It does not address RQ2 or any human construct. No participant is present in these trials.

## System and versions

Each trial must record:

- repository commit SHA;
- scenario and trial-manifest hashes;
- environment-manifest hash;
- target model and deployment context;
- service/image versions and digests where applicable;
- Python/controller version;
- Kubernetes, Docker or other runtime versions where applicable;
- detection-rule version;
- metric-derivation tool version; and
- host/runner information sufficient to explain a failed or invalid trial.

The local-process fit probe and Docker Desktop Kubernetes target are separate evidence streams. They must not be pooled without a reviewed equivalence decision.

## Independent and controlled variables

### Independent variable

`automation_condition`:

- `manual`: standardised external recovery command;
- `automated`: rule-based controller invokes the same scenario-specific recovery action.

### Scenario factor

- `no-fault-v1` control;
- `service-termination-v1`;
- `dependency-latency-v1`.

### Controlled variables

- workload version and request counts;
- service topology and versions;
- fault target and parameters;
- detection rule and threshold;
- trial target environment;
- clean-reset contract;
- observation windows;
- event schema and clock source;
- run-order generation procedure; and
- resource limits and concurrency settings.

## Planned repetition and run order

The technical pilot planning target is **at least 10 valid trials per condition × fault-scenario cell**, with a separately recorded reserve allowance for invalid technical runs. This is a feasibility/pilot target, not a statistical power calculation.

The no-fault scenario is run as a control block. Fault scenarios are blocked, and condition order is balanced or pseudo-randomised before execution. The generated order file is committed or retained with the raw records before the first trial. Outcomes must not be used to reorder later trials.

If the target environment cannot support the planned repetitions, record the deviation and treat the result as protocol feasibility evidence rather than a completed comparison.

## Trial manifest

The protocol-supporting manifest must contain at least:

```json
{
  "protocol_id": "phase-3-technical-reliability-v1",
  "trial_id": "generated-unique-id",
  "scenario_id": "service-termination-v1",
  "automation_condition": "manual",
  "repetition": 1,
  "run_order": 1,
  "detection_rule_version": "detection-v1",
  "recovery_action_version": "recovery-v1",
  "target_model": "declared-target-model",
  "environment_manifest": "path-or-digest"
}
```

The manifest is immutable after trial start. If a trial must be amended, create a new trial identifier and preserve the original manifest and failure record.

## Run procedure

1. **Preflight:** verify the branch commit, tool versions, target context, manifest hashes, output path and absence of an existing active trial.
2. **Register trial:** write `trial_started` with scenario, condition, repetition, run order and protocol version.
3. **Reset:** stop or delete prior workload services according to the target-specific reset contract; start the declared versions; wait for readiness; verify the clean-state fingerprint.
4. **Baseline workload:** run the fixed pre-fault requests and record every request and response.
5. **Inject fault:** apply the declared fault to the declared target and write `injection_started` only after the controller confirms application.
6. **Detect:** evaluate the shared detection rule and write `fault_detected` with the rule version and observed signal. If the rule cannot be evaluated, mark the trial invalid.
7. **Recover:** for `manual`, issue the standardised external recovery command; for `automated`, allow the rule-based controller to issue the same recovery command. Record the initiator and command version.
8. **Verify recovery:** wait for readiness and the post-recovery success criterion; write `recovery_completed` and `post_recovery_check`.
9. **Revert/close fault:** record `injection_ended` and confirm the target has returned to the expected state.
10. **Post-recovery workload:** run the declared requests and record responses and latency.
11. **Cleanup:** return the environment to the clean state and write `cleanup_completed`.
12. **Validate and classify:** calculate event-completeness and reset checks, classify the trial as valid or excluded, preserve raw records, and write `trial_completed`.

For the no-fault control, omit fault and recovery events and execute only the declared deployment transition/rollback path. The control must still run reset, workload, readiness, cleanup and telemetry checks.

## Reset and contamination controls

The reset contract must verify:

- no prior service process, pod or fault controller remains active;
- declared service versions are active;
- the target dependency has no injected mode or latency;
- the state fingerprint matches the empty synthetic state;
- readiness checks pass for all required services;
- output is written to a new trial directory; and
- no events from another trial share the new `trial_id`.

After every trial, cleanup is mandatory even when the workload or recovery action fails. A cleanup failure invalidates the trial and blocks the next trial until a fresh reset is independently verified.

## Data collected

Technical records only:

- trial metadata and immutable manifests;
- controller events;
- service and dependency events;
- workload requests and responses;
- fault, detection, recovery and cleanup events;
- deployment/readiness/rollback events where applicable;
- raw telemetry export and export-loss diagnostics;
- version and environment metadata; and
- a validity/exclusion ledger.

Do not collect participant identifiers, screen/audio recordings, real payment information or production traffic.

## Exclusion and failure criteria

Exclude a trial from primary comparison when any of the following occurs:

- reset or clean-state verification fails;
- the target, scenario or condition differs from the trial manifest;
- required event boundaries are missing, duplicated or unparseable;
- the fault is not applied or cannot be reverted;
- recovery is initiated by an undeclared action;
- a process/pod/fault/state contaminates the next trial;
- the target environment changes during a comparison block without a recorded block boundary;
- telemetry loss prevents the primary metric boundaries from being established; or
- an unplanned manual repair changes the treatment.

An invalid trial is not deleted. Store the raw bundle, metadata and an exclusion reason. If a failure reveals a protocol defect, update the protocol version before continuing rather than silently mixing versions.

## Analysis plan

Derive the metrics in [`../metrics/technical-metrics.md`](../metrics/technical-metrics.md) from raw event bundles. Report:

- trial counts and valid/excluded counts per condition and scenario;
- primary metric values for each valid trial;
- median and interquartile range for each condition × scenario cell;
- failure-impact numerator and denominator;
- recovery-success counts;
- measurement-quality indicators; and
- an exclusion ledger with reasons.

Retain individual trial values and source event identifiers. Do not pool no-fault and fault scenarios into one primary outcome. Do not use the technical results to infer human workload, trust, understanding or decision rationale.

## Threats to validity

- The scripted manual baseline controls timing but is not representative of real engineers.
- A purpose-built transactional system may not generalise to other continuous-delivery systems.
- Local-process and Kubernetes timing may not be equivalent.
- The detection rule may favour one fault class or automation condition.
- Request counts are small in the fit-probe lineage and may be inadequate for stable tail-latency estimates.
- Clock skew, buffering and event reordering may change derived durations.
- The recovery action may be easier to automate for service termination than dependency latency.
- Repetition on one host or cluster may underestimate environmental variation.
- Phase 1 literature gaps may change the choice of intervention or outcome.
- The pinned OpenTelemetry SDK/Collector trace path passed the small-trace compatibility check; each trial must still record telemetry completeness and exclude runs whose event boundaries cannot be established.

## Reproduction command

The implementation command must be versioned before the protocol is declared executable. The intended interface is:

```bash
python3 experiments/harness/phase_3_trial.py \
  --protocol docs/protocols/phase-3-technical-experiment.md \
  --trial-manifest experiments/manifests/phase-3-trial.json \
  --output-root results/phase-3/raw
```

This command is intentionally a planned interface at the design stage. Do not run it until the harness, event additions and trial-manifest schema have been implemented and reviewed.
