# Phase 3 research-design record: fault model, metrics and experiment protocol

**Project:** PhD Preparation – Reliability Automation and Software Engineering Practice

**Working title:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

**Phase:** 3

**Status:** Design complete and locked; local-process event implementation is complete and dry-run validation remains outstanding
**Date started:** 2026-08-09

## Objective

Define a bounded technical experiment that can compare reliability-automation strategies on a reproducible OrderFlow system without conflating technical telemetry with human evidence. Phase 3 converts the provisional Phase 0/2 design into:

- an explicit fault model;
- operational definitions for technical outcomes;
- a separate provisional specification for developer-practice constructs that are not measurable from technical telemetry;
- a versioned trial and reset protocol; and
- a machine-readable trial allocation and event contract; and
- pre-specified validity, exclusion and provenance rules.

This phase defines the experiment. It does not claim that the proposed automation improves reliability, and it does not authorise human-participant work.

## Research questions and evidence boundary

### Technical question addressed

**RQ1:** Under controlled fault scenarios in a reproducible transactional service system, how do different reliability-automation strategies affect detection time, recovery time, failure impact and manual intervention?

The primary technical unit of analysis is one valid **trial**: one automation condition, one fault scenario, one fixed workload, one clean reset and one recorded event bundle.

### Questions not addressed by this phase

RQ2 concerns engineers' diagnosis, recovery and escalation decisions. A technical trial can measure system events and controller actions, but it cannot establish workload, trust, understanding, reasoning or decision rationale. Those constructs remain outside this protocol and require a separately reviewed human-participant protocol and ethics process.

## Scope and design commitments

| Design element | Phase 3 commitment |
|---|---|
| Candidate system | Minimal OrderFlow transactional slice: `order-api` and `inventory` dependency |
| Workload | Fixed synthetic order workload, versioned with the trial manifest |
| Primary independent variable | Recovery strategy: standardised manual baseline vs rule-based automated recovery |
| Fault factors | No-fault baseline, inventory service termination, inventory dependency latency |
| Detection rule | Shared, versioned detection rule; it must not change between recovery conditions |
| Primary technical outcomes | Detection latency, recovery time and failure impact |
| Secondary outcomes | Failed requests, request-latency change, recovery success, intervention count and telemetry completeness |
| Deployment target | Target environment selected in Phase 2; local-process and Kubernetes records remain separately labelled |
| Telemetry | Pinned OpenTelemetry SDK/Collector trace path with raw capture plus structured event contract |
| Data | Synthetic technical records only; no participant identifiers, real payments or production traffic |
| Inference boundary | Feasibility and pre-specified technical comparison only; no universal or causal claim before the pilot is reviewed |

## Automation conditions

The technical pilot should use the following conditions unless a reviewed amendment records a different intervention:

### M — standardised manual-recovery baseline

The fault is injected and detected using the shared controller and detection rule. Recovery is initiated by an external, pre-specified recovery command after the detection event. The command and its timestamp are recorded as an intervention. The baseline is scripted for reproducibility; it is not a human-participant measure of operator performance.

### A — rule-based automated recovery

The same fault, workload, detection rule, service versions and reset procedure are used. Once the detection rule is satisfied, the controller invokes the pre-specified recovery action without the external recovery command. The trigger, decision, action and completion events must be recorded separately.

The conditions must differ only in who or what initiates the recovery action. A future automated rollback condition is deferred until a faulty-deployment scenario and its rollback semantics have been specified; it must not be introduced implicitly into the first comparison.

## Fault model

The complete fault model is recorded in [`../fault-model/phase-3-fault-model.md`](../fault-model/phase-3-fault-model.md). The first technical pilot is restricted to faults with:

1. a single declared target;
2. a deterministic trigger point;
3. a bounded duration or explicit reversion action;
4. no permanent data mutation;
5. an observable injection and recovery boundary; and
6. a clean-reset check that can detect contamination.

The Phase 2 scenarios remain the feasibility set. They are not yet evidence that the automation conditions are comparable, because the existing fit-probe records were not run under the Phase 3 condition labels and do not contain the complete detection-event contract.

## Metrics

The metric catalogue and derivation rules are recorded in [`../metrics/technical-metrics.md`](../metrics/technical-metrics.md). Primary outcomes are only calculated when their required event boundaries are present. Missing values are not silently imputed.

The most important distinction is between:

- **fault-relative metrics**, which use injection, detection and recovery timestamps;
- **workload metrics**, which use offered and completed request records; and
- **measurement-quality metrics**, which determine whether a trial is interpretable.

Developer-practice constructs are intentionally separated into [`../metrics/developer-practice-metrics.md`](../metrics/developer-practice-metrics.md). They require participant actions, explanations or questionnaires and therefore belong to a later ethics-approved protocol, not this technical trial.

## Trial structure

Each trial must have a unique trial identifier and must record:

- repository commit and scenario-manifest hash;
- environment, image and tool versions;
- target model and deployment context;
- scenario and automation condition;
- repetition number and run order;
- reset outcome and state fingerprint;
- all controller, service, fault, detection, recovery and workload events; and
- a validity decision with an explicit exclusion reason when required.

The planned design is blocked by scenario and balanced by recovery condition where practical. Run order must be generated and stored before execution; it must not be rearranged after seeing outcomes.

The locked machine-readable allocation is [`../../experiments/manifests/phase-3-trial-manifest.json`](../../experiments/manifests/phase-3-trial-manifest.json). It specifies 50 planned valid trials: 10 no-fault controls and 40 fault-comparison trials, with two reserve slots per cell. Its contract is documented in [`../../data/schemas/phase-3-trial-manifest.md`](../../data/schemas/phase-3-trial-manifest.md).

## Phase 3 deliverables

- [x] Bounded fault model and scenario catalogue finalised for the first technical comparison.
- [x] Automation-condition boundary finalised.
- [x] Technical metric operationalisations finalised.
- [x] Developer-practice metric boundary specified separately for later human-participant work.
- [x] Trial, reset, contamination and exclusion rules finalised.
- [x] Threats to validity and carry-forward limitations recorded.
- [x] Technical experiment protocol finalised for implementation.
- [x] Machine-readable trial manifest and manifest contract committed.
- [x] Phase 3 decision ADR accepted for implementation.
- [x] Review the protocol against the accessible Phase 1 evidence map (`phase-3-evidence-review.md`).
- [x] Validate the event additions required for detection and condition comparison in the local-process harness.
- [x] Implement the smallest protocol-supporting trial harness and raw-record validity tooling.
- [x] Run a dry-run without treating it as pilot evidence.

## Implementation explicitly deferred

- full OrderFlow application implementation;
- real payment or production integrations;
- participant recruitment, consent, tasks or human-data collection;
- claims about cognitive workload, trust, understanding or decision rationale from technical telemetry;
- a broad chaos-engineering platform comparison;
- canary/progressive deployment as an additional intervention;
- confirmatory statistical claims about reliability improvement.

## Exit criteria

The Phase 3 design package is complete when:

- the fault model is bounded and each pilot scenario has a declared target, trigger, duration, recovery action and reset test;
- primary and secondary metrics have exact event boundaries, units, aggregation and missing-data rules;
- automation conditions differ only in recovery initiation under the stated control assumptions;
- the trial protocol specifies run order, repetition, reset, contamination checks and exclusion handling;
- the event contract can represent condition, detection and recovery decisions without relying on dashboard screenshots;
- the protocol has been checked against the Phase 1 evidence status and known validity threats; and
- the machine-readable manifest and event contract are committed.

The implementation gate remains open until a dry-run in the declared checkout shows that the protocol can be executed without collecting human-participant data. Dry-run records must not be reported as pilot findings.

## Known limitations carried forward

- Phase 1 database searching and full-text charting remain outstanding in the repository record.
- The local fit probe demonstrated technical feasibility only; it did not compare automation conditions.
- The pinned OpenTelemetry SDK/Collector path passed the small-trace compatibility check; load, metrics/logs and Kubernetes-equivalence validation remain open.
- A purpose-built OrderFlow slice improves control but may reduce external validity.
- A scripted manual baseline isolates the recovery mechanism but does not represent real engineer behaviour.
- The planned repetitions are a feasibility/pilot design, not a statistical power justification.
