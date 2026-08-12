# Phase 8 supervisor briefing

## Proposed project

**Reliability Automation and Software Engineering Practice in Continuous
Delivery Environments**

## Research problem

Reliability automation changes system behaviour but can also change the
diagnosis, recovery and escalation work performed by software engineers.

Technical telemetry and direct human evidence are therefore treated as
different empirical streams.

## Research questions

### RQ1

Under controlled fault scenarios in a reproducible transactional service
system, how do different recovery-automation strategies affect recovery time,
failure impact and required intervention?

### RQ2

How does automation-assisted incident response influence software engineers'
diagnosis, recovery and escalation decisions during structured
continuous-delivery tasks?

## What changed following earlier feedback

- the research-question set has been reduced to two;
- the empirical software is explicitly identified;
- construction and selection of the software are explained;
- technical empirical-data sources are operationalised;
- participant evidence is collected separately;
- software-domain limitations are explicit; and
- the human/software-engineering dimension is directly measured.

## Empirical software

OrderFlow is a purpose-built transactional benchmark.

The bounded initial slice contains:

- `order-api`;
- `inventory`;
- synthetic workload;
- Kubernetes deployment;
- dependency-latency faults;
- service-termination faults; and
- versioned recovery strategies.

## Pre-application technical evidence

Phase 4 established reproducible deployment, reset and observation.

Phase 5 resolved all 50 planned technical slots from 53 preserved attempts and
produced 50 valid resolving observations.

Those results are treated as methodological and descriptive pilot evidence.

They do not establish universal automation superiority or production
readiness.

## Human-study preparation

Phase 6 specifies:

- professional participant population;
- within-participant counterbalanced tasks;
- manual and automation-assisted conditions;
- diagnosis, recovery and escalation measures;
- workload and behavioural reliance measures;
- consent and withdrawal;
- accessibility/risk controls; and
- data-management/privacy boundaries.

No participants have been recruited.

Formal ethics approval has not been obtained.

## Methodological contribution

The project preserves distinct:

- technical-system evidence; and
- human decision evidence.

Integration occurs at research interpretation rather than by treating telemetry
as a proxy for workload, understanding, trust or decision rationale.

## Principal recognised limitations

- purpose-built benchmark external validity;
- bounded fault families;
- incomplete full scoping review;
- professional participant recruitment;
- feasibility sample limitations;
- ethics dependency; and
- supervisory team not yet confirmed.
