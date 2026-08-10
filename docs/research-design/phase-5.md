# Phase 5 research-design record: experiment harness and technical pilot

**Project:** PhD Preparation - Reliability Automation and Software Engineering Practice

**Working title:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

**Phase:** 5

**Status:** Design gate defined; pilot implementation and execution not started

**Date started:** 2026-08-10

## Objective

Execute a bounded technical pilot that tests whether the Phase 3 comparison
protocol can be implemented reproducibly on the Phase 4 OrderFlow Kubernetes
prototype and whether its raw records support deterministic validity
classification, metric derivation and descriptive analysis.

Phase 5 is a pilot and measurement-feasibility phase. It may produce technical
pilot observations, but it is not a confirmatory experiment, a production
benchmark or a human-participant study.

The roadmap exit evidence is:

> Repeated technical runs produce validated raw records and analysis from raw data.

## Inherited boundary

Phase 5 inherits rather than reopens the following accepted decisions:

- the empirical object remains the two-service OrderFlow benchmark
  (`order-api` -> `inventory`);
- Docker Desktop Kubernetes is the validated local prototype target;
- OpenTelemetry traces are a secondary observation path while structured
  immutable records remain the authoritative audit boundary;
- deterministic harness-controlled availability and latency faults remain the
  first fault classes;
- the comparison remains the standardised external/manual recovery baseline
  versus rule-based automated recovery;
- both conditions use the same detection rule and the same scenario-specific
  recovery action;
- rollback as a treatment, progressive delivery, platform chaos tooling,
  production integrations and human-participant work remain deferred; and
- Phase 3 dry runs and Phase 4 reproducibility runs remain feasibility evidence
  and must not be reclassified as Phase 5 pilot trials.

## Phase 5 design decisions

### Experimental target

The Phase 5 pilot uses **Docker Desktop Kubernetes only**.

Local-process execution remains useful historical feasibility evidence but is
not a Phase 5 comparison target and is not pooled with Kubernetes observations.
This removes an avoidable environment factor from the first pilot.

The Phase 4 prototype is reused as research infrastructure. Phase 5 may add
trial identity, fault-control and experiment-controller behaviour, but it must
not expand the business topology merely for realism.

### Protocol versioning

Phase 5 creates a new protocol identity:

`phase-5-technical-pilot-v1`

The Phase 3 protocol, design manifest and dry-run outputs remain immutable
historical design/feasibility records. Phase 5 may refine implementation details
before the first pilot trial, but after a Phase 5 batch starts its manifest and
run order are immutable.

### Comparison conditions

The condition identifiers remain:

- `manual`: standardised external recovery baseline;
- `automated`: rule-based automated recovery.

For the `manual` condition, no research participant is present. After the
shared detection rule is satisfied, a separate baseline executor invokes the
declared recovery command and records an external intervention event.

For the `automated` condition, the rule-based controller invokes the same
recovery command after the same detector produces the same decision boundary.

No artificial "human reaction time" is inserted into the manual condition.
Doing so would manufacture a treatment advantage rather than measure one.

The intended treatment difference is therefore the recovery-initiator/control
path, not the detection threshold, recovery command, workload, fault,
environment or an invented operator delay.

### Detection interpretation

Detection remains measured because the Phase 3 metric catalogue specifies
`detection_latency_ms`, but the detector is deliberately held constant across
conditions.

Phase 5 therefore treats detection latency primarily as a detector-fidelity and
balance measure. A condition difference in detection latency is not interpreted
as a recovery-automation effect unless a later reviewed protocol explicitly
changes detection itself as part of the treatment.

### Scenario set

The Phase 5 pilot retains three scenario roles:

1. `no-fault-v1` - quality-control observation;
2. `service-termination-v1` - inventory availability loss;
3. `dependency-latency-v1` - 120 ms inventory dependency latency.

No additional fault class is authorised in Phase 5 v1.

### Kubernetes service-termination mechanism

The availability fault is implemented by scaling the `inventory` Deployment to
zero replicas and verifying that no inventory pod remains ready.

Recovery scales the same Deployment back to one replica and waits for
readiness plus the declared post-recovery workload success.

This mechanism is preferred over deleting or killing one inventory pod because
the Kubernetes Deployment controller would otherwise immediately replace the
pod, introducing platform self-healing as an undeclared recovery mechanism.

Both conditions use the same scale-to-one recovery action.

### Dependency-latency mechanism

The latency fault uses the existing inventory control boundary:

```text
POST /__control
{"mode": "latency", "latency_ms": 120}
```

Recovery clears the fault with:

```text
POST /__control
{"mode": "none"}
```

The controller must verify the returned fault state and must independently
verify that cleanup leaves `mode=none`.

### No-fault quality control

The Phase 3 no-fault design included a version-transition/rollback quality
control. Phase 5 removes that deployment-transition requirement from the pilot
control because:

- rollback is not one of the two recovery treatments;
- automated deployment rollback remains explicitly deferred;
- the Phase 4 accepted prototype demonstrated workload, observation and reset,
  not a version-transition treatment; and
- adding rollback would create an unrelated mechanism immediately before the
  first technical comparison.

The Phase 5 no-fault control therefore verifies clean deployment, readiness,
fixed synthetic workload, telemetry completeness and clean reset only.

This is a pre-data protocol refinement. The Phase 3 files remain unchanged and
the difference is recorded explicitly rather than silently reinterpreted.

## Pilot allocation

Phase 5 retains the Phase 3 pilot-sized replication target:

- 10 valid no-fault quality-control trials;
- 10 valid `manual` service-termination trials;
- 10 valid `automated` service-termination trials;
- 10 valid `manual` dependency-latency trials;
- 10 valid `automated` dependency-latency trials.

Total planned valid trials: **50**.

Reserve allowance:

- two reserve slots for each fault scenario x condition cell; and
- two reserve no-fault controls.

Maximum available trial slots: **60**.

The reserve is activated only after a trial is classified invalid under the
pre-specified validity rules. Invalid trials remain in the raw record and are
never silently replaced.

The repetition count is a pilot/feasibility target inherited from Phase 3, not a
statistical power calculation.

## Run-order design

The primary 50-trial schedule is generated before the first pilot trial using
the fixed seed:

`phase-5-pilot-run-order-v1`

The schedule contains ten five-trial cycles. Each cycle contains exactly:

- one no-fault quality-control trial;
- one manual service-termination trial;
- one automated service-termination trial;
- one manual dependency-latency trial; and
- one automated dependency-latency trial.

Across ten cycles:

- each fault scenario is first in five cycles and second in five cycles;
- each condition is first within its scenario pair in five cycles and second
  in five cycles; and
- the no-fault control occupies each of the five cycle positions exactly twice.

Cycle construction and the final order are deterministic from the fixed seed.
The concrete run-order file is persisted and hashed before trial 1. Outcomes
must never alter later ordering.

This cycle design is preferred to executing twenty same-scenario trials in one
long block because it reduces confounding from host/cluster drift while
retaining exact condition balance.

Reserve slots are held outside the primary 50-slot schedule and are appended
only for the cell whose preceding trial was invalid.

## Workload and detection boundary

The Phase 3 v1 workload and detector thresholds are retained for the first
pilot unless Slice 2 validation demonstrates an internal inconsistency:

- two successful pre-fault requests;
- fault injection;
- shared scenario-specific detector;
- recovery after detection;
- two post-recovery requests;
- no client retries;
- 2,000 ms request timeout;
- 20 ms nominal inter-request delay.

Service termination uses three consecutive non-success order responses as the
pilot detection signal. Inventory readiness remains a validation signal but is
not allowed to short-circuit the shared workload-based detection rule.

Dependency latency uses three consecutive completed order requests above
100 ms, with 120 ms injected latency.

Keeping the shared detector workload-based prevents Kubernetes readiness timing
from becoming an undeclared condition-specific shortcut.

## Data lifecycle

Phase 5 separates evidence into four boundaries:

```text
results/phase-5/raw/
    immutable batch/trial records

data/processed/phase-5/
    deterministic metric observations derived from raw records

analysis/phase-5/
    versioned analysis code and machine-readable summaries

docs/pilot/
    human-readable interpretation after evidence inspection
```

Raw trial bundles are authoritative and immutable after each trial closes.
Processed values must be reproducible from raw records and retain source event
identifiers, trial IDs, source hashes and analysis-tool version.

No metric is manually edited to make a trial usable.

## Metrics

Phase 5 retains the Phase 3 metric catalogue.

Primary technical records:

- `detection_latency_ms`;
- `recovery_time_ms`;
- `failure_impact_rate`.

Interpretation is narrowed as follows:

- `detection_latency_ms` is a shared-detector fidelity/balance outcome rather
  than an expected recovery-condition effect;
- `recovery_time_ms` and `failure_impact_rate` are the main
  condition-sensitive pilot outcomes; and
- individual numerator/denominator counts are always retained for
  `failure_impact_rate`.

Secondary and quality metrics remain those already operationalised in
`docs/metrics/technical-metrics.md`.

## Analysis boundary

The Phase 5 analysis is descriptive and feasibility-oriented.

For every condition x fault-scenario cell report:

- planned, attempted, valid and excluded trial counts;
- individual valid-trial values;
- median;
- interquartile range;
- minimum and maximum where useful;
- failure-impact numerators and denominators;
- recovery-success count;
- manual intervention and automation-decision counts; and
- measurement-quality indicators.

No-fault quality controls are reported separately and are not pooled into a
fault outcome.

No null-hypothesis significance test, p-value, powered-effect claim or
generalised causal conclusion is authorised by Phase 5 v1. A later inferential
analysis requires a separately reviewed plan informed by pilot data quality and
the literature review.

## Validity and reserve rules

A trial is invalid for the primary comparison if any of the following occurs:

- pre-trial clean-state verification fails;
- the committed trial manifest, scenario, condition or target does not match
  execution;
- the declared fault is not positively verified;
- required event boundaries are missing, duplicated or unparseable;
- the shared detection rule cannot be evaluated;
- recovery is initiated through the wrong condition path;
- the recovery action differs between conditions;
- post-recovery readiness/success criteria fail;
- OTel/structured-record completeness is insufficient to establish required
  boundaries;
- cleanup or contamination checks fail;
- repository/environment provenance is incomplete; or
- an unplanned repair changes the treatment.

Invalid raw evidence is retained with an explicit exclusion code.

A cleanup failure blocks the next trial until an independent clean reset passes.
The next reserve slot for that cell may be used only after the environment is
revalidated.

## Acceptance criteria

Phase 5 is complete only when all of the following are evidenced:

- [ ] The Phase 5 protocol, pilot manifest, batch identity and run-order
      generation procedure are version controlled.
- [ ] The concrete primary run order is generated before trial execution,
      hashed and retained immutably.
- [ ] The Phase 4 prototype is reused on Docker Desktop Kubernetes without an
      unreviewed topology or treatment change.
- [ ] Service termination and dependency latency can be applied, positively
      verified, reverted and contamination-checked on the Phase 5 target.
- [ ] Manual and automated conditions share the same detector and exact
      scenario-specific recovery action.
- [ ] Every attempted trial writes a fresh immutable raw bundle and explicit
      validity classification.
- [ ] Invalid/excluded trials are preserved and reserve activation is
      attributable to a pre-specified exclusion.
- [ ] The planned 50 valid pilot observations are completed, or a documented
      protocol-feasibility stop condition is reached without disguising the
      shortfall.
- [ ] Metric derivation is deterministic from raw records and does not impute
      missing primary boundaries.
- [ ] Processed metric records retain trial/source-event/hash provenance.
- [ ] Descriptive analysis is reproducible from processed records without
      manual result editing.
- [ ] No-fault controls and the two fault scenarios remain separately
      interpretable.
- [ ] A fresh re-analysis of the same raw evidence reproduces the processed
      metrics and summary outputs byte-for-byte or with explicitly documented
      non-semantic metadata differences.
- [ ] Automated tests cover run-order generation, fault/recovery semantics,
      validity/exclusion logic, reserve activation, metric derivation and
      analysis boundaries.
- [ ] Formatting, linting, typing, security, infrastructure, repository
      compliance and the complete quality gate pass.
- [ ] Raw, processed and interpreted outputs are clearly labelled as Phase 5
      technical pilot evidence only.
- [ ] Status documentation is updated only after the Phase 5 evidence is
      inspected.

## Planned implementation sequence

### Slice 1 - design gate

Lock this research-design record, the technical pilot protocol and the material
execution decisions before implementation.

### Slice 2 - machine-readable pilot contract

Add the Phase 5 pilot manifest, batch schema, deterministic balanced run-order
generator and static contract tests. No pilot trial executes in this slice.

### Slice 3 - Kubernetes trial controller

Build the Phase 5 controller on the Phase 4 deployment/provenance substrate.
Implement one-trial execution, immutable bundles, clean reset, workload,
fault/detection/recovery paths and validity classification.

### Slice 4 - fault and condition validation

Exercise only non-pilot development/validation slots to establish that each
fault can be applied/reverted and that manual/automated paths invoke the exact
same recovery action. These outputs remain implementation-feasibility evidence.

### Slice 5 - metric derivation and analysis pipeline

Implement raw-to-processed metric derivation, exclusion ledger generation and
descriptive analysis before collecting the primary pilot batch.

### Slice 6 - technical pilot execution

Freeze the batch manifest and concrete run order, then execute the planned
50-valid-trial pilot with reserve activation only when required.

### Slice 7 - reproducible analysis and close-out

Re-derive and re-analyse from raw evidence, inspect exclusions and limitations,
run the full quality gate, update status documentation and close Phase 5 by PR.

## Explicit exclusions

Phase 5 v1 does not include:

- human participants or human-performance measurements;
- an artificial operator-reaction delay;
- production systems, traffic, payments or personal data;
- a new benchmark topology;
- a new fault class;
- deployment rollback as a treatment;
- canary/progressive delivery;
- Chaos Mesh, Litmus or uncontrolled platform faults;
- statistical power claims or confirmatory inference;
- pooling local-process and Kubernetes timing evidence; or
- treating OTel spans as a substitute for the authoritative structured record.

## Exit evidence

Phase 5 exits only when repeated technical trials produce validated raw records
and a reproducible analysis derived from those raw records, with the pilot
limitations and exclusions preserved explicitly.
