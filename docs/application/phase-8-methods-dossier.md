# Phase 8 methods dossier

## Research model

The proposed doctorate contains two linked but empirically separate streams.

### Stream T ? technical reliability

Unit:

one valid controlled technical trial.

Manipulation:

recovery-automation strategy under a declared fault scenario.

Evidence:

- structured fault/recovery events;
- workload events;
- intervention records;
- validity records;
- environment/version provenance;
- corroborating traces.

Core outcomes:

- recovery time;
- failure impact;
- intervention requirement.

### Stream H ? engineering practice

Unit:

one participant-task observation nested within one participant.

Manipulation:

manual-decision versus automation-assisted incident-response support.

Evidence:

- diagnosis;
- recovery/escalation decision;
- decision timing;
- automation accept/override/escalate behaviour;
- workload;
- comprehension;
- retrospective explanation.

Core outcomes:

- diagnosis accuracy;
- recovery-decision appropriateness;
- escalation appropriateness.

## Integration

The streams are not pooled.

Integration asks whether technical behaviour and human decision evidence tell
compatible, complementary or conflicting stories about reliability automation.

Examples:

- a technically faster recovery mechanism may increase inappropriate reliance;
- a human-preferred strategy may not reduce technical failure impact;
- technical effects may differ across fault models while decision effects differ
  across task/authority contexts.

## Technical empirical object

OrderFlow is a purpose-built transactional benchmark.

The initial slice contains:

- order API;
- inventory dependency;
- synthetic workload;
- Kubernetes deployment;
- structured telemetry; and
- deterministic recovery/fault control.

## Technical pilot boundary

Phase 5 is pre-application feasibility evidence.

It is not the final doctoral experiment.

Future doctoral technical work may:

- replicate the frozen comparison;
- increase repetitions where justified;
- add carefully specified fault variants;
- test another benchmark or software domain;
- add an additional automation strategy only when independently specified.

Any extension requires a new experimental version rather than silently altering
Phase 5.

## Human study boundary

Phase 6 provides a protocol-ready feasibility design.

Participant execution requires actual ethics/institutional approval.

The feasibility sample is designed to examine:

- task comprehension;
- burden;
- interface operation;
- missingness;
- measurement behaviour;
- learning/order problems; and
- recruitment practicality.

A later main participant study requires its own sample-size and analysis
justification.

## Principal validity threats

### Construct validity

- recovery time is not the same as overall reliability;
- workload ratings are not decision quality;
- behavioural reliance is not a universal trust construct;
- technical intervention count is not human workload.

### Internal validity

- shared detector behaviour can affect timing;
- participant learning/order effects;
- scenario/task imbalance;
- recommendation correctness effects.

### External validity

- purpose-built benchmark;
- limited fault families;
- controlled incidents rather than production work;
- professional participant sampling.

### Conclusion validity

- Phase 5 is descriptive pilot evidence;
- Phase 7 feasibility sample is descriptive;
- later inference requires a separately justified design.

## Reproducibility

The research repository records:

- source versions;
- manifests;
- run order;
- raw technical evidence;
- deterministic processed data;
- analysis code;
- protocol documents; and
- claim boundaries.

Participant-identifiable/pseudonymised records remain outside public Git.
