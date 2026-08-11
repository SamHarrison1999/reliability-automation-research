# ADR 0020: Phase 6 human-study and ethics boundary

- **Status:** Accepted for Phase 6 protocol design
- **Date:** 2026-08-11

## Context

RQ1 technical evidence and RQ2 human evidence require different units of
analysis and different ethical/data-management controls.

Phase 5 produced synthetic technical evidence from the OrderFlow benchmark.
Those records cannot establish what engineers understand, why they act, how
much workload they experience or whether reliance on automation is
well-calibrated.

Phase 6 must therefore create a separate human-participant protocol.

The project is also in application preparation rather than authorised
participant execution. A protocol can be made ready for review without
implying that ethics approval exists.

## Decision

Phase 6 will:

1. maintain a strict boundary between Phase 5 technical evidence and future
   participant evidence;
2. design a controlled, within-participant comparison of manual decision
   support and automation-assisted decision support;
3. use matched OrderFlow incident variants rather than expose participants to
   unrestricted infrastructure control;
4. collect diagnosis, recovery and escalation decisions directly from
   participants;
5. treat workload, automation understanding, reliance/trust calibration and
   explanation quality as direct human constructs requiring participant
   instruments or responses;
6. use retrospective typed explanations by default rather than concurrent
   think-aloud;
7. exclude audio/video/screen recording from the initial feasibility design;
8. keep all identifiable and pseudonymised participant data outside the public
   repository; and
9. distinguish `protocol-ready` from `ethics-approved`.

No participant recruitment is allowed until the relevant institutional
approval is actually recorded.

## Consequences

### Positive

- RQ2 receives direct human evidence rather than telemetry proxies.
- Participant task exposure remains technically controlled.
- Within-participant comparison reduces between-person expertise variation.
- Counterbalancing can address learning/order effects.
- Typed retrospective rationale avoids altering timed task execution as much as
  concurrent think-aloud.
- Removing default audio/video collection reduces privacy and data-management
  burden.
- The repository can demonstrate ethics readiness during PhD application
  preparation without falsely claiming approval.

### Costs and limitations

- A controlled task interface reduces ecological realism compared with
  unrestricted operational work.
- Within-participant designs are vulnerable to learning and carry-over effects,
  requiring matched scenario variants and counterbalancing.
- Automation-assisted human interaction is not identical to the autonomous
  Phase 5 controller and must be interpreted separately.
- Professional recruitment may limit feasibility sample size.
- Formal ethics approval remains an external dependency.

## Alternatives rejected

### Infer human effects from Phase 5 telemetry

Rejected because system events cannot establish workload, trust,
understanding or decision rationale.

### Give participants unrestricted Kubernetes access

Rejected because it increases safety risk, environmental variability and
measurement ambiguity without being necessary for the RQ2 feasibility study.

### Use concurrent think-aloud as the default

Rejected because verbalisation can interfere with timed diagnosis and recovery
tasks.

### Collect webcam or screen recordings by default

Rejected because they increase privacy and data-management burden without a
demonstrated need for the initial feasibility study.

### Treat protocol completion as ethics approval

Rejected because document readiness and institutional approval are distinct
states.
