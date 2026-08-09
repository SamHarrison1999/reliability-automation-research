# Phase 2 research-design record: software-system and technology selection

**Project:** PhD Preparation – Reliability Automation and Software Engineering Practice
**Working title:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments
**Phase:** 2
**Status:** Technology-decision close-out complete for the bounded technical pilot; broader validation remains phase-gated
**Date started:** 2026-08-08

## Objective

Select and justify a candidate experimental system and technology boundary that can support a reproducible technical reliability study without allowing implementation convenience to determine the research design.

Phase 2 is a selection and feasibility phase. It does not claim that a selected tool or architecture improves reliability, and it does not authorise participant recruitment or human-data collection.

## Relationship to Phase 1

The repository's Phase 1 protocol remains the authority for the literature-review process. The accessible-corpus review is retained as the current baseline; authenticated database-comprehensive updating is a separate later review task. That limitation does not turn technical fit evidence into reliability-effect evidence.

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

## Final Phase 2 technology decisions for the bounded technical pilot

1. **Candidate system:** carry the purpose-built **OrderFlow** transactional benchmark into the bounded technical pilot. An adapted open-source benchmark remains a future comparator, not a silently interchangeable system.
2. **Deployment model:** build services as Docker images and use Docker Desktop Kubernetes as the primary local experimental target. Docker Compose/local process remains a development and diagnosis path only; no parity is assumed.
3. **CI/CD boundary:** keep the experiment controller portable and command-line driven. GitHub Actions is repository validation infrastructure, not the experimental condition or sole source of reproducibility.
4. **Telemetry boundary:** use the pinned OpenTelemetry Python SDK → OTLP/HTTP → Collector trace path with raw capture. Retain the JSONL event bundle for audit; Prometheus and any trace/log backend remain separate backend decisions.
5. **Recovery boundary:** use a shared monitoring/detection rule and compare scripted manual recovery initiation with rule-based automated initiation. Automated deployment rollback is a separately validated extension.
6. **Progressive deployment:** defer canary, blue/green and other progressive rollout from the first comparison because it adds traffic-allocation and promotion variables.
7. **Fault boundary:** implement the first deterministic scenarios at application or dependency boundaries under the experiment controller. Chaos Mesh and Litmus remain future alternatives, not selected dependencies.
8. **Data boundary:** produce versioned manifests and raw event bundles, but do not add participant data or claim pilot findings. Raw and processed data remain separate, and generated outputs remain reproducible from raw records.

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
- [x] Complete the portable local fit probe without collecting human-participant data.
- [x] Record measured reset, startup, telemetry and fault-reversion results for the local target.
- [x] Record the Docker Desktop Kubernetes fit-probe close-out.
- [x] Complete and record the real OpenTelemetry SDK/Collector compatibility check.
- [x] Accept, defer or bound each technology choice in formal ADRs.
- [ ] Validate the Phase 3 trial manifest, detection events and recovery conditions through dry-runs.

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

The Phase 2 technical decision close-out records that:

- every selected option has an ADR, alternative and validation task;
- the candidate architecture can be explained without relying on undocumented infrastructure;
- a clean-reset and version-recording procedure is specified;
- the fit probe produces a complete raw event bundle for at least one no-fault run and two deterministic fault scenarios;
- the selected fault mechanism can be targeted and reverted without contaminating the next run;
- the deployment and telemetry choices are tested together rather than selected independently;
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

## Fit-probe evidence

The local and Docker Desktop Kubernetes fit-probe results are recorded in
[`docs/fit-probe/phase-2-fit-probe-results.md`](../fit-probe/phase-2-fit-probe-results.md).
The real SDK/Collector result is recorded in
[`docs/observability/phase-2-otel-compatibility-result.md`](../observability/phase-2-otel-compatibility-result.md).
Together they support the bounded technology decisions; they remain synthetic
technical-feasibility evidence and do not establish reliability effects.

## Phase 2 exit record

The Phase 2 technology-decision close-out is recorded in ADRs 0009–0012. The
next phase is the fault model, metric operationalisation and experiment
protocol. Its dry-run gate remains open, and no full application,
participant work or empirical-effect claim is authorised by this close-out.
