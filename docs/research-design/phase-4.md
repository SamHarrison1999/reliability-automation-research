# Phase 4 research-design record: reproducible technical prototype

**Project:** PhD Preparation – Reliability Automation and Software Engineering Practice

**Working title:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

**Phase:** 4

**Status:** Design gate defined; implementation not yet started

**Date started:** 2026-08-10

## Objective

Promote the existing minimal OrderFlow feasibility slice into a versioned, reproducible technical prototype that can be built, deployed, reset and observed repeatedly on the accepted Docker Desktop Kubernetes target.

Phase 4 establishes the research object and its reproducibility boundary. It does not execute the Phase 5 technical pilot, estimate reliability effects, introduce human participants, or establish production readiness.

## Inherited decisions

Phase 4 carries forward the accepted Phase 0–3 boundaries rather than reopening them:

- the prototype remains the minimal `order-api` → `inventory` OrderFlow slice;
- Docker images and Docker Desktop Kubernetes remain the bounded local experimental target;
- local-process and Kubernetes evidence remain separately labelled;
- deterministic harness-controlled service/dependency faults remain the accepted first fault boundary;
- monitoring-triggered rule-based recovery and the standardised external baseline remain the planned comparison conditions;
- OpenTelemetry remains the accepted instrumentation/transport boundary for traces;
- structured immutable research records remain authoritative for provenance and audit;
- GitHub Actions validates repository quality but is not itself an experimental condition; and
- automated deployment rollback, progressive delivery, platform chaos tools, production integrations and human-participant work remain deferred.

## Phase boundary

Phase 4 is an infrastructure and reproducibility phase. The prototype may exercise deterministic synthetic workload and bounded validation scenarios only to demonstrate build, deployment, reset and observation behaviour.

Repeated condition-by-scenario pilot execution, technical outcome analysis and interpretation belong to Phase 5. Phase 4 validation output must therefore be labelled reproducibility or feasibility evidence, not pilot findings.

## Prototype boundary

The smallest complete prototype contains:

1. `order-api`, accepting synthetic order requests;
2. `inventory`, providing the declared dependency boundary;
3. versioned container packaging;
4. versioned Kubernetes deployment and service configuration;
5. readiness and version checks;
6. deterministic synthetic workload support;
7. clean reset and contamination checks;
8. structured event/provenance capture; and
9. the accepted OpenTelemetry trace transport integrated sufficiently to validate observation of the prototype.

No additional business service is required for Phase 4 unless implementation evidence demonstrates that the two-service boundary cannot satisfy the repository-defined exit criterion.

## Reproducibility contract

Each Phase 4 validation execution must use a fresh output directory and record at least:

- repository commit SHA;
- prototype/environment manifest version and SHA-256;
- Kubernetes manifest SHA-256;
- service versions and container image identities/digests where available;
- Docker and Kubernetes versions;
- controller/validation-tool version;
- target context;
- execution identifier and timestamps;
- deployment/readiness results;
- workload/observation checks;
- reset and contamination results; and
- an explicit overall validity decision.

Generated evidence must be separated from source configuration. Raw records must not be overwritten by processed summaries.

## Acceptance criteria

Phase 4 is complete only when all of the following have been demonstrated:

- [ ] The prototype topology, configuration and environment boundary are version controlled.
- [ ] The declared OrderFlow images can be built reproducibly from the repository checkout.
- [ ] A clean Docker Desktop Kubernetes target can deploy the declared prototype configuration.
- [ ] `order-api` and `inventory` pass declared readiness and version checks.
- [ ] A deterministic synthetic workload traverses the `order-api` → `inventory` boundary.
- [ ] Prototype execution records immutable repository, manifest, image/runtime and environment provenance.
- [ ] The accepted OpenTelemetry trace path can observe/correlate the prototype execution without requiring a dashboard as evidence.
- [ ] Structured raw records remain sufficient to audit the required deployment, workload, observation and reset boundaries.
- [ ] Cleanup/reset returns the target to the declared clean-state fingerprint with no residual injected fault or prototype state.
- [ ] The complete deploy → readiness → workload → observe → cleanup/reset sequence succeeds in at least two fresh validation executions.
- [ ] Repeated validation uses fresh output directories and does not silently reuse or overwrite prior evidence.
- [ ] Automated tests cover the new prototype, configuration/provenance and reproducibility validation boundaries.
- [ ] Formatting, linting, typing, security, infrastructure validation, repository compliance and the complete project quality gate pass.
- [ ] Raw validation evidence and derived summaries are clearly separated and labelled as Phase 4 reproducibility evidence only.
- [ ] Roadmap, progress ledger and top-level project status are updated only after the evidence above has been inspected.

## Planned implementation sequence

### Slice 1 — design gate

Define this Phase 4 record and lock the prototype/reproducibility boundary before implementation.

### Slice 2 — prototype packaging

Promote the existing two-service fit-probe implementation into an explicitly versioned prototype while preserving the established service behaviour and Phase 3 event identity contract.

### Slice 3 — Kubernetes deployment contract

Add prototype-specific Kubernetes/environment configuration independent of fit-probe placeholders. Pin the declared service versions and record image identities.

### Slice 4 — reset and provenance validation

Implement the Phase 4 validation controller/scripts for clean deployment, readiness, workload, observation, cleanup and contamination checks with immutable provenance.

### Slice 5 — OpenTelemetry integration

Exercise the already accepted SDK → OTLP/HTTP → Collector trace path against the actual prototype. Preserve structured records as the audit-friendly authoritative research boundary.

### Slice 6 — repeat reproducibility validation

Execute at least two fresh validation runs, inspect their raw evidence and compare only the pre-specified reproducibility invariants.

### Slice 7 — close-out

Run the complete quality gate, update status documentation, prepare focused commits and open the Phase 4 pull request. Do not merge or begin Phase 5 until every Phase 4 acceptance criterion is evidenced.

## Explicit exclusions

Phase 4 does not include:

- the planned Phase 5 condition-by-scenario pilot matrix;
- statistical or inferential claims about reliability improvement;
- human-participant recruitment, tasks, data or ethics work;
- production traffic, payments or personal data;
- additional research questions;
- Chaos Mesh, Litmus or uncontrolled chaos engineering;
- canary, blue-green or other progressive deployment as a treatment;
- automated deployment rollback as a new comparison condition;
- a production observability platform or dashboard requirement; or
- claims that local-process and Kubernetes timings are equivalent.

## Risks and controls

| Risk | Control |
|---|---|
| Fit-probe artefacts are mistaken for the final prototype | Introduce explicit Phase 4 version/configuration labels without rewriting validated feasibility evidence |
| Kubernetes behaviour contaminates interpretation | Record target/runtime versions and keep target-specific evidence explicit |
| Observability integration changes the treatment | Treat telemetry as measurement infrastructure and validate it independently of recovery-condition semantics |
| Generated output is mistaken for empirical findings | Label all Phase 4 output as reproducibility/feasibility evidence and defer technical comparison to Phase 5 |
| Reset leaves residual state | Make clean-state and contamination checks acceptance requirements and block subsequent validation after failure |
| Scope expands for realism | Retain the two-service slice unless evidence shows it cannot satisfy the Phase 4 exit criterion |

## Exit evidence

The repository roadmap defines the Phase 4 exit evidence as demonstrating that **the smallest benchmark system can be reset, deployed and observed reproducibly**.

This record operationalises that statement without broadening the research question or moving Phase 5 pilot execution into Phase 4.
