# ADR 0015: Phase 5 technical-pilot execution boundary

**Status:** Accepted

**Date:** 2026-08-10

## Context

Phase 3 defined the fault/recovery comparison and validated its local-process
protocol-supporting harness. Phase 4 then established a reproducible Kubernetes
OrderFlow prototype with immutable provenance and a bounded OpenTelemetry
observation path.

Phase 5 must now convert those two lines of feasibility evidence into one
technical pilot without adding environment, treatment or human-participant
dimensions that would make the resulting observations difficult to interpret.

Several design choices therefore need to be fixed before pilot implementation:

- which execution environment is authoritative for the pilot;
- how service termination is represented without Kubernetes self-healing
  becoming an undeclared recovery mechanism;
- what the scripted `manual` baseline means in a study with no participant;
- whether the Phase 3 no-fault deployment-transition control should be carried
  into a prototype that deliberately deferred rollback; and
- how repeated trials are ordered to reduce temporal drift.

## Decision

### One pilot environment

Use the Phase 4 Docker Desktop Kubernetes prototype as the sole Phase 5 pilot
execution environment.

Do not pool local-process and Kubernetes timings.

### Preserve the treatment definition

Keep condition IDs `manual` and `automated`.

Both conditions use the same detector and exact recovery action. `manual`
means a standardised external baseline executor, not a human-participant
measurement. No artificial reaction-time delay is introduced.

### Make Kubernetes availability loss harness-controlled

Represent `service-termination-v1` by scaling the inventory Deployment from one
replica to zero.

Recover by scaling the same Deployment from zero to one.

This avoids the Deployment controller immediately replacing a deleted pod and
therefore avoids Kubernetes self-healing becoming an unplanned treatment.

### Retain the existing latency control boundary

Use inventory `POST /__control` with 120 ms latency for injection and
`mode=none` for reversion.

### Refine the no-fault control before pilot data

Phase 5 no-fault trials are workload/readiness/telemetry/reset quality controls
only.

Do not introduce the Phase 3 version-transition/rollback quality-control path
into Phase 5 v1. Deployment rollback remains outside the treatment and was not a
Phase 4 acceptance requirement.

The Phase 3 documents and dry-run evidence remain unchanged and retain their
historical meaning.

### Retain the 50-valid-trial pilot allocation

Use ten valid observations for each of the five pilot cells, with two reserve
slots per cell.

This is a feasibility allocation, not a power calculation.

### Counterbalance over time

Generate ten deterministic five-trial cycles. Every cycle contains all five
pilot cells. Balance scenario order, condition order and no-fault position
across the ten cycles using the fixed seed `phase-5-pilot-run-order-v1`.

Freeze and hash the concrete order before the first primary trial.

### Interpret detection conservatively

Retain `detection_latency_ms` because it is already operationalised, but do not
claim it is caused by recovery condition when detection is intentionally held
constant.

## Consequences

### Positive

- removes execution-context pooling from the first pilot;
- prevents Kubernetes self-healing from contaminating the availability fault;
- avoids manufacturing an automation advantage with an arbitrary human-delay
  constant;
- keeps recovery-action semantics identical across conditions;
- prevents an unrelated rollback mechanism from entering the treatment;
- distributes cells across time to reduce cluster/host drift;
- preserves the Phase 3 and Phase 4 evidence histories unchanged; and
- makes an unexpectedly small treatment contrast an interpretable pilot result
  rather than something to hide.

### Costs and limitations

- the scripted manual baseline is not representative of a real engineer;
- Kubernetes remains a single local host/cluster context;
- ten trials per cell do not constitute a confirmatory sample-size argument;
- the availability fault is operationalised as zero replicas rather than an
  uncontrolled process crash;
- the treatment may produce small differences because deliberate human delay is
  excluded; and
- a later main study may need a revised intervention after pilot evidence is
  inspected.

## Rejected alternatives

### Use both local-process and Kubernetes trials

Rejected because environment would become another comparison factor and Phase 4
already established Kubernetes as the reproducible prototype target.

### Delete an inventory pod for service termination

Rejected because the Kubernetes Deployment controller may recreate it
automatically, confounding the declared recovery initiator.

### Add a fixed manual delay

Rejected because the chosen delay would directly determine part of the observed
automation advantage without representing measured human behaviour.

### Carry deployment rollback into the no-fault control

Rejected because it adds a mechanism outside the Phase 5 recovery comparison
and outside the Phase 4 accepted prototype evidence.

### Increase repetitions for apparent statistical strength

Rejected because Phase 5 is explicitly a feasibility/pilot phase and has no
reviewed power calculation justifying a confirmatory sample size.
