# Phase 2 research-design record: software-system and technology selection

**Project:** PhD Preparation – Reliability Automation and Software Engineering Practice  
**Working title:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments  
**Phase:** 2  
**Status:** In progress; selections are provisional until the fit probe is completed  
**Date started:** 2026-08-08

## Objective

Select and justify a candidate experimental system and technology boundary that can support a reproducible technical reliability study without allowing implementation convenience to determine the research design.

Phase 2 is a selection and feasibility phase. It does not claim that a selected tool or architecture improves reliability, and it does not authorise participant recruitment or human-data collection.

## Relationship to Phase 1

The repository's Phase 1 protocol remains the authority for the literature-review process. In the current working copy, database searching and full-text charting are still recorded as outstanding. Phase 2 can prepare and document candidate choices, but it cannot be declared complete until the Phase 1 exit criteria and the Phase 2 validation criteria have both been reviewed.

## Research criteria

Candidate options will be assessed against the following weighted criteria. Scores are desk-research judgements, not empirical measurements.

| Criterion | Weight | Question |
|---|---:|---|
| Experimental control | 25 | Can the intervention, workload, fault timing and reset state be controlled independently? |
| Reproducibility and reset reliability | 20 | Can another researcher recreate a clean run with versioned configuration and bounded environmental assumptions? |
| Observability and provenance | 15 | Can events, metrics, traces, versions and timestamps be collected with sufficient provenance? |
| Fault-injection precision | 15 | Can scenarios target a defined service or dependency and be reverted safely? |
| Participant-task explainability | 10 | Can the system and automation behaviour be explained to participants without unnecessary platform complexity? |
| Resource and CI feasibility | 10 | Can the environment run within realistic local and CI limits? |
| External validity | 5 | Does the candidate resemble relevant continuous-delivery and cloud-native practice without importing uncontrolled complexity? |

Scores use a 0–3 scale: 0 = does not meet the criterion, 1 = weak fit, 2 = workable with restrictions, 3 = strong provisional fit. A score is not accepted until the validation task in the matrix has passed.

## Provisional Phase 2 decisions

1. **Candidate system:** carry the purpose-built **OrderFlow** transactional benchmark into the fit probe. An adapted open-source benchmark remains the main alternative. OrderFlow is not yet accepted as the final empirical object.
2. **Deployment model:** evaluate Kubernetes as the primary experimental target because deployment, service health and rollback behaviour are part of the proposed intervention. Docker Compose may be used for local development or a lightweight reset path only if parity with the experimental target is demonstrated.
3. **CI/CD boundary:** keep the experiment controller portable and command-line driven. GitHub Actions remains repository validation infrastructure; it is not the sole source of experimental reproducibility.
4. **Telemetry boundary:** use OpenTelemetry as the instrumentation and transport candidate, with a backend selected only after a compatibility probe. Prometheus is the first metrics-backend candidate; a trace/log backend remains open.
5. **Fault boundary:** implement the first deterministic scenarios at application or dependency boundaries under the experiment controller. Chaos Mesh is the primary Kubernetes fault-injection candidate; Litmus remains an alternative. No fault tool is final until reset, targeting and reversion tests pass.
6. **Data boundary:** produce versioned manifests and raw event bundles, but do not add participant data or claim pilot findings. Raw and processed data remain separate, and generated outputs remain reproducible from raw records.

These are decisions about what to test next. They are not claims that one technology is superior in general.

## Phase 2 deliverables

- [x] Selection criteria and scoring rubric.
- [x] Candidate-system and technology comparison matrix.
- [x] Candidate-system ADR.
- [x] Deployment-model ADR.
- [x] Observability and data-provenance ADR.
- [x] Fault-injection ADR.
- [x] Candidate architecture diagram.
- [x] Experimental-control/data-flow diagram.
- [x] Phase 2 fit-probe plan.
- [ ] Complete the fit probe without collecting human-participant data.
- [ ] Record measured reset, startup, telemetry and fault-reversion results.
- [ ] Review Phase 1 literature completion and update the decision evidence.
- [ ] Accept or reject the provisional choices in a follow-up ADR update.

## Fit-probe plan

The fit probe must be the smallest test capable of challenging the provisional choices:

1. Define the service and dependency boundaries for a minimal OrderFlow slice.
2. Create a versioned environment manifest and a clean-reset command.
3. Run a fixed synthetic workload without faults and verify health and telemetry completeness.
4. Inject one service-termination scenario and one dependency-latency or dependency-failure scenario.
5. Verify that each scenario is targeted, timestamped, reverted and distinguishable in the raw event bundle.
6. Exercise one deployment-version change and one rollback path in the selected target model.
7. Repeat the same run from a clean reset and compare event completeness, ordering and outcome classification.
8. Record failures, resource use, version identifiers and unresolved threats; do not interpret the run as evidence of automation effectiveness.

## Implementation tasks authorised by this phase

- Minimal infrastructure and environment manifests needed for the fit probe.
- A versioned experiment-controller interface and deterministic scenario configuration.
- Health checks, telemetry wiring and raw-event capture.
- Repository validation and reproducibility scripts.

## Implementation explicitly deferred

- A full production-like application.
- Human-participant tasks, recruitment or data collection.
- Claims about workload, trust, cognition or decision rationale from telemetry.
- A large service topology, canary deployment, real payments or production traffic.
- Statistical claims about reliability improvement.

## Validation criteria

Phase 2 may be closed only when:

- every selected option has an ADR, alternative and validation task;
- the candidate architecture can be explained without relying on undocumented infrastructure;
- a clean-reset and version-recording procedure is specified;
- the fit probe produces a complete raw event bundle for at least one no-fault run and two deterministic fault scenarios;
- the selected fault mechanism can be targeted and reverted without contaminating the next run;
- the provisional deployment and telemetry choices are tested together rather than selected independently;
- the Phase 1 evidence status and unresolved literature limitations are reflected in the decisions; and
- no human-participant data or empirical-effect claim has been introduced.

## Threats to validity

- Desk-based scores may reflect documentation quality rather than actual tool behaviour.
- The purpose-built OrderFlow domain may provide stronger control at the cost of external validity.
- Kubernetes adds operational complexity that may itself affect timing and reset reliability.
- Fault-injection tools may introduce control-plane behaviour that is mistaken for application behaviour.
- Observability pipelines can lose, reorder or timestamp events differently across components.
- A fit probe may demonstrate feasibility but cannot establish the effect of an automation strategy.
- The Phase 1 review may later change the appropriate system or technology criteria.

## Phase 2 exit record

This document remains **in progress** until the fit-probe evidence is recorded. The next phase is the fault model, metric operationalisation and experiment protocol; it must not begin as a completed phase until the selection decisions have been validated.
