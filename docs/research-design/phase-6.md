# Phase 6 research-design record: human-participant protocol and ethics

**Project:** PhD Preparation ? Reliability Automation and Software Engineering Practice

**Working title:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

**Phase:** 6

**Status:** Human-study design and ethics preparation in progress

**Date started:** 2026-08-11

## Objective

Design an ethics-ready human-participant study that can directly address RQ2
without treating Phase 5 technical telemetry as evidence of engineers'
workload, trust, understanding or decision quality.

Phase 6 prepares the participant protocol, tasks, measurements, recruitment
rules, consent materials, data-management plan and analysis boundary.

Phase 6 does not authorise participant recruitment or data collection.

## Research question

**RQ2:** How do different reliability-automation strategies influence software
engineers' diagnosis, recovery and escalation decisions during structured
continuous-delivery tasks?

## Evidence boundary

Phase 5 and Phase 6 use separate empirical streams.

Phase 5 contains synthetic technical-pilot evidence about the behaviour of the
OrderFlow system and its recovery controllers.

Phase 6 defines a future human-participant evidence stream.

Technical telemetry must not be labelled as evidence of:

- participant workload;
- participant trust;
- participant understanding;
- participant reasoning;
- participant decision quality; or
- human reaction time.

Likewise, future participant task timings must not be substituted for the
technical recovery-time metric derived in Phase 5.

## Institutional ethics gate

The project is currently preparing for a future Open University PhD
application rather than executing research as an approved OU
human-participant study.

The Phase 6 package may therefore become ready for institutional review before
formal ethics approval can be obtained.

Until the relevant institutional approval exists:

- no participant may be recruited;
- no participant data may be collected;
- no feasibility participant may be treated as an informal exception;
- no study advertisement may imply institutional approval; and
- Phase 7 participant execution remains blocked.

The repository must distinguish:

1. `protocol-ready` ? the study package is internally complete and ready for
   supervisor/institutional review; from
2. `ethics-approved` ? approval has actually been granted through the
   relevant institutional process.

Only the second state can authorise participant recruitment.

## Provisional human-study architecture

The smallest defensible RQ2 study is a within-participant, counterbalanced
comparison between two human-facing reliability conditions.

### Condition H-M ? manual decision baseline

The participant receives:

- an incident notification;
- a controlled set of OrderFlow observability evidence;
- the permitted recovery actions; and
- the option to escalate.

The participant records a diagnosis and chooses the recovery or escalation
action.

### Condition H-A ? automation-assisted decision condition

The participant receives the same underlying evidence plus a transparent
automation recommendation.

The participant may:

- accept the recommendation;
- override it with another permitted recovery action; or
- escalate.

The automation recommendation is not assumed to be correct in every scenario.
Participants must be informed that automation may be fallible.

This allows reliance and override behaviour to be observed without deception.

The human-facing automation condition is not the same empirical intervention
as the fully automated Phase 5 technical controller. Results from the two
studies must not be pooled.

## Experimental structure

The provisional design uses matched variants of the existing OrderFlow fault
families:

- dependency latency; and
- service termination.

Each participant should encounter both human-facing conditions without seeing
an identical task twice.

Scenario variants, condition order and task order must be frozen before
approved participant execution.

Counterbalancing must limit systematic order and learning effects.

A participant must not receive unrestricted shell, Docker or Kubernetes
access. Recovery choices should be exposed through a controlled task
interface so that safety, logging and task comparability remain bounded.

## Provisional outcome hierarchy

Primary human outcomes:

1. diagnosis accuracy;
2. recovery-decision appropriateness; and
3. escalation appropriateness.

Secondary outcomes may include:

- task completion time;
- recovery-task success;
- perceived workload;
- automation understanding;
- behavioural and self-reported reliance/trust calibration;
- unsafe or prohibited action count; and
- retrospective explanation quality.

No composite score should be introduced unless its construction and
interpretation are justified before participant collection.

## Explanation method

Concurrent think-aloud is not the default Phase 6 design because it may alter
task timing and workload.

The initial protocol should instead request a short retrospective typed
explanation after each task.

Audio, video, webcam and screen recording are excluded from the initial
feasibility protocol unless a later ethics-reviewed amendment demonstrates a
clear research need.

## Participant population

The target population is adult software practitioners or technically relevant
participants with sufficient experience to understand service incidents,
observability evidence and recovery decisions.

Exact inclusion thresholds, recruitment routes, expertise strata and
compensation must be frozen in the recruitment protocol before ethics
submission.

The feasibility study is expected to use a small sample to test protocol
operation, not to support powered or generalisable effect claims.

## Accessibility

The participant protocol should be usable remotely and should minimise
unnecessary barriers.

The design should support:

- keyboard navigation;
- readable and resizable text;
- clear task instructions;
- participant-controlled breaks;
- no mandatory webcam;
- explicit pause handling for timing measures; and
- reasonable adjustments that do not invalidate the declared measurement
  boundary.

The study must be presented as research rather than an assessment of
professional competence.

## Data boundary

Participant-identifiable or pseudonymised data must not be committed to this
public repository.

The public repository may contain only items such as:

- blank participant-facing forms;
- protocol documents;
- schemas;
- synthetic fixtures;
- code required for the controlled task environment;
- non-identifying provenance records; and
- appropriately approved aggregate or anonymised outputs.

Any participant identity mapping must be stored separately from research
responses in institutionally approved storage.

## Phase 6 analysis boundary

Phase 7 is a feasibility study.

Its analysis should focus on:

- completion and exclusion rates;
- task duration and protocol burden;
- missing-data patterns;
- instrument operation;
- scenario and interface problems;
- direction and spread of observed outcomes; and
- participant feedback relevant to protocol revision.

Phase 7 must not be converted retrospectively into a powered confirmatory
study.

Any later confirmatory participant study requires a separately frozen analysis
plan and an appropriate sample-size justification.

## Phase 6 slices

### 6A ? human-study design gate

Freeze the human/technical evidence boundary, provisional study architecture
and formal ethics blocker.

### 6B ? human-evidence and instrument review

Update the human-evidence strand before freezing workload, trust/reliance and
understanding instruments.

### 6C ? participant and recruitment protocol

Specify population, eligibility, expertise measurement, recruitment,
accessibility, compensation and coercion safeguards.

### 6D ? task and scenario protocol

Specify matched scenario variants, task evidence, allowed actions, answer
keys, automation recommendations and researcher-only walkthroughs.

### 6E ? measurement and analysis protocol

Freeze constructs, timestamps, scoring, missing-data rules, counterbalancing
and feasibility analysis.

### 6F ? participant ethics pack

Prepare participant information, consent, withdrawal, debrief and risk
materials.

### 6G ? data management and privacy

Prepare the data-management plan, pseudonymisation boundary, retention and
destruction rules, data schema and repository restrictions.

### 6H ? protocol validation and closeout

Validate the package without participants and prepare it for
supervisor/institutional review.

## Phase 6 exit states

### Protocol-ready

May be declared when:

- recruitment rules are complete;
- tasks and answer keys are complete;
- participant-facing materials are complete;
- measures and analysis rules are complete;
- data-management and privacy plans are complete;
- researcher-only protocol walkthroughs pass; and
- repository validation passes.

This state does not authorise recruitment.

### Ethics-approved

May be declared only when the relevant institutional process has actually
approved the study and any required data-protection/data-management processes
are satisfied.

Phase 7 remains blocked until this state exists.

## Explicit non-authorisations

Phase 6 does not by itself authorise:

- participant recruitment;
- participant data collection;
- informal friends/family pilot participants;
- retrospective ethics approval;
- use of Phase 5 telemetry as human evidence;
- production-system access by participants; or
- confirmatory statistical claims.
