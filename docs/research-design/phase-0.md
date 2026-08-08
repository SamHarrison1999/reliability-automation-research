# Phase 0 research-design baseline

## Source proposal

The supplied proposal is retained at [`../proposal/source/Sam_Harrison_PhD_Proposal.pdf`](../proposal/source/Sam_Harrison_PhD_Proposal.pdf). It proposes a mixed-methods study of reliability automation, system reliability and human decision-making in continuous-delivery environments.

The proposal is the starting point, not evidence for the claims the eventual study will make.

## Problem statement

Reliability automation can change both system behaviour and the work engineers perform during failure detection, diagnosis and recovery. The research problem is to determine how those effects can be studied with evidence that is technically measurable, human-relevant and reproducible.

## Working aim

Empirically examine how reliability-oriented automation mechanisms influence technical reliability outcomes and software engineers' decision-making during structured continuous-delivery failure-recovery tasks.

## Provisional research questions

### RQ1 - Technical reliability

Under controlled fault scenarios in a reproducible transactional service system, how do different reliability-automation strategies affect detection time, recovery time, failure impact and manual intervention?

### RQ2 - Engineering practice

How do different reliability-automation strategies influence software engineers' diagnosis, recovery and escalation decisions during structured continuous-delivery tasks?

### Methodological objective

Develop and evaluate a reproducible experimental environment capable of producing trustworthy comparisons across repeated runs.

This objective carries forward the original reproducibility question without making the empirical scope unnecessarily broad.

## Candidate empirical object

The current candidate is **OrderFlow**, a purpose-built transactional benchmark application. Its selection remains provisional and must be compared with established open-source alternatives in Phase 2.

Candidate components are:

- API gateway;
- order service;
- inventory service;
- payment simulator;
- notification service;
- database;
- asynchronous messaging component; and
- synthetic client workload.

The domain is useful as a candidate because it can expose stateful and stateless services, synchronous and asynchronous dependencies, user-visible failures, deployment consequences and controlled failure propagation. It must remain small enough to reset and manipulate experimentally.

Explicit exclusions are real payments, personal data and production traffic.

## Experimental model

| Element | Provisional definition |
|---|---|
| Independent variable | Reliability-automation strategy |
| Candidate conditions | Manual recovery baseline; automated deployment rollback; monitoring-triggered automated recovery |
| Initial fault factors | Service crash; faulty deployment; dependency latency/failure |
| Primary technical outcomes | Recovery time; failure impact/blast radius |
| Secondary technical outcomes | Detection latency; failed requests; deployment outcome; rollback events; manual interventions |
| Human outcomes | Diagnosis accuracy; recovery decision; escalation decision; task completion time; perceived workload; trust/understanding measures |
| Controls | Fixed workload, versioned configuration, isolated reset, deterministic scenario seed where applicable, recorded software/infrastructure version identifiers |

The first pilot should compare at least two conditions and a small number of deterministic fault scenarios. Progressive/canary deployment is deferred until the design can accommodate it without confounding the initial comparison.

## Evidence sources

### Technical evidence

- versioned experiment manifest;
- fault-injection event and timestamp;
- deployment, rollback and service-state events;
- metrics, logs and traces;
- workload requests and outcomes;
- software, container and infrastructure version identifiers; and
- reset and environment-health checks.

### Human/engineering-practice evidence

- structured recovery-task action sequence;
- task outcome and error classification;
- interaction logs;
- think-aloud or retrospective explanation, if justified by the protocol;
- post-task workload/trust/understanding measures; and
- optional screen/audio recording only with explicit consent and approved data handling.

The human evidence plan is not final and requires literature review, participant feasibility work and ethics approval.

## Validity boundary

Technical pilot results would demonstrate infrastructure and measurement feasibility, not universal superiority of an automation strategy. Human findings would be limited by participant sample, expertise, task realism, learning effects, demand characteristics and the chosen benchmark domain.

## Open decisions for later phases

1. Which software system best meets the selection criteria: OrderFlow, an adapted open-source benchmark or another candidate?
2. Which deployment and observability technologies provide the best balance of validity, repeatability, cost and explainability?
3. How should recovery time and failure impact be operationalised so the measures are not ambiguous?
4. Which participant population, task duration, sample and qualitative method are feasible and ethically acceptable?
5. Which automation intervention can be manipulated while holding other operational factors constant?
