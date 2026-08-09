# Progress ledger

## Project status

- **Current phase:** Phase 3 - fault model, metrics and experiment protocol
- **Status:** Design draft in progress; Phase 2 technology decisions are closed for the bounded technical pilot; Phase 1 remains an accessible-corpus baseline with database-comprehensive updating deferred
- **Empirical data collected:** Synthetic technical-feasibility records only; no participant or production data
- **Participant recruitment:** Not started
- **Ethics approval:** Not obtained
- **Application implementation:** Full application deferred; minimal fit-probe slice and harness are present

## Phase 0 record

### Objective

Translate the proposal into a bounded research design and a repository that keeps research infrastructure, experimental variables, empirical data, findings and software implementation distinct.

### Research rationale

The proposal combines system reliability and human decision-making. Those claims require different evidence sources. Establishing the separation before implementation prevents telemetry from being treated as a proxy for human workload or reasoning.

### Deliverables

- [x] Repository bootstrap scripts for Bash and PowerShell
- [x] Initial repository structure and data-boundary rules
- [x] Provisional research questions
- [x] Provisional variables and evidence sources
- [x] Phase-gated roadmap
- [x] ADRs for repository boundaries and provisional technology decisions
- [x] Literature-review protocol drafted and versioned
- [x] Seed evidence matrix created with primary/secondary status labels
- [ ] Named database searches executed and provenance recorded
- [ ] Evidence matrix fully charted from full text
- [ ] Preliminary literature map and evidence gaps reviewed

### Validation

- `bash scripts/verify-repository.sh` passes.
- No application implementation is present.
- Protected data directories contain only `.gitkeep` markers.
- The original proposal is retained under `docs/proposal/source/`.

### Risks and threats to validity

- The candidate transactional domain may not represent other software domains.
- A purpose-built system may have ecological-validity limitations compared with production systems.
- Human-participant claims cannot be made until recruitment, protocol and ethics are resolved.
- Automation conditions may differ in more than one property unless the intervention is carefully controlled.
- Small pilot samples may establish feasibility but not generalisable effects.

## Decision log

| Date | Decision | Reason | Evidence/status |
|---|---|---|---|
| 2026-08-08 | Start with repository and research design only | The proposal does not yet justify implementation details | Phase 0 scaffold |
| 2026-08-08 | Treat technical and human evidence as separate streams | System telemetry cannot establish workload or decision rationale | Methodological constraint |
| 2026-08-08 | Defer canary deployment from the first pilot | It introduces another major intervention dimension | Provisional scope decision |
| 2026-08-08 | Use a scoping review/evidence map for Phase 1 | The expected evidence is heterogeneous across industrial studies, operational datasets, fault-injection experiments and human-factors evidence | `docs/literature/phase-1-review-protocol.md` v0.1 |
| 2026-08-08 | Separate primary studies from secondary reviews and conceptual papers | Reviews support citation chaining, while conceptual proposals cannot establish empirical findings | `docs/literature/evidence-matrix.csv` status fields |
| 2026-08-08 | Treat human evidence as a dedicated extraction dimension | Telemetry and incident logs do not by themselves establish workload, trust or decision rationale | Phase 0 validity boundary; review question RQ-S3 |

## Phase 2 record

### Objective

Select and justify the candidate experimental system and technology boundary using explicit research criteria, while keeping implementation subordinate to the research design.

### Deliverables

- [x] Selection criteria and scoring rubric
- [x] Candidate-system and technology comparison matrix
- [x] Candidate-system, deployment, observability and fault-injection ADRs
- [x] Candidate architecture and experiment-control diagrams
- [x] Fit-probe protocol
- [x] Portable local fit probe completed and measured evidence recorded
- [x] Provisional choices accepted, deferred or bounded after validation

### Validation status

The local-process and Docker Desktop Kubernetes fit probes establish technical
feasibility for the bounded OrderFlow slice and controlled fault boundary. The
real OpenTelemetry SDK/Collector trace compatibility probe also passed for the
pinned versions. No participant data or empirical-effect claim has been added.

### Phase 2 decision log

| Date | Decision | Reason | Evidence/status |
|---|---|---|---|
| 2026-08-08 | Carry OrderFlow into the fit probe | Provides the strongest provisional control over state, faults, workload and participant-facing explanations | ADR 0003; not final |
| 2026-08-08 | Evaluate Kubernetes as the primary experimental target | Deployment and rollback behaviour are part of the proposed intervention | ADR 0004; validation required |
| 2026-08-08 | Use an OpenTelemetry-centred telemetry boundary | Separates instrumentation from the eventual telemetry backend | ADR 0005; validation required |
| 2026-08-08 | Start with harness-controlled deterministic faults | Protects repeatability before adding platform-level fault-tool complexity | ADR 0006; validation required |
| 2026-08-08 | Execute the portable local fit probe | Test the smallest authorised OrderFlow slice before introducing Kubernetes control-plane complexity | `docs/fit-probe/phase-2-fit-probe-results.md`; local checks passed |
| 2026-08-09 | Accept Docker images and Docker Desktop Kubernetes for the bounded technical pilot | Four Kubernetes fit-probe runs passed their declared checks, including a clean-reset repeat | ADR 0004; `results/fit-probe/kubernetes-fit-probe-summary.json` |
| 2026-08-09 | Accept the pinned OpenTelemetry SDK/Collector trace path | Five spans were received, decoded, correlated and ordered; gzip transport was retained | ADR 0008; `docs/observability/phase-2-otel-compatibility-result.md` |
| 2026-08-09 | Separate CI/CD validation from experiment execution | Keeps hosted-runner state out of the experimental condition | ADR 0009 |
| 2026-08-09 | Use monitoring-triggered recovery and defer deployment rollback/progressive delivery | Preserves a one-dimension first comparison and a bounded dry-run gate | ADRs 0010–0011 |
| 2026-08-09 | Close Phase 2 technology decisions | Every choice is accepted, deferred or bounded with explicit evidence limits | ADR 0012 |

## Phase 3 record

### Objective

Define a bounded technical comparison of recovery initiation strategies under the existing OrderFlow fault boundary, with metric derivations and reset/exclusion rules specified before new trial data is collected.

### Design package

- [x] Fault model and scenario catalogue drafted (`docs/fault-model/phase-3-fault-model.md`)
- [x] Manual versus rule-based automated recovery boundary drafted
- [x] Technical metric catalogue drafted (`docs/metrics/technical-metrics.md`)
- [x] Technical experiment protocol drafted (`docs/protocols/phase-3-technical-experiment.md`)
- [x] Metric provenance record documented (`data/schemas/metric-observation-record.md`)
- [x] Phase 3 decision ADR drafted (`docs/adr/0007-phase-3-fault-metrics-protocol.md`)
- [x] Trial-flow diagram drafted
- [ ] Review against completed Phase 1 evidence map
- [ ] Implement and validate the Phase 3 trial manifest/event additions
- [ ] Complete dry-runs for each scenario and recovery condition

### Phase 3 evidence boundary

The existing Phase 2 raw bundles are not Phase 3 comparison trials: they lack the final automation-condition and explicit detection-event contract. They remain synthetic technical-feasibility evidence. No metric from them should be presented as evidence that an automation strategy improves reliability.

### Phase 3 decision log

| Date | Decision | Reason | Evidence/status |
|---|---|---|---|
| 2026-08-09 | Compare standardised manual recovery with rule-based automated recovery | Isolates recovery initiation while holding fault, workload, detection rule, versions and reset constant | ADR 0007; proposed |
| 2026-08-09 | Retain no-fault, service-termination and dependency-latency scenarios | Preserves the smallest Phase 2 feasibility set | Fault model; drafted |
| 2026-08-09 | Make detection latency, recovery time and failure impact primary outcomes | Gives each RQ1 outcome an explicit event boundary before implementation | Technical metric catalogue; drafted |
| 2026-08-09 | Require immutable trial manifests and explicit exclusion records | Prevents post-hoc condition changes, silent imputation and contamination | Technical protocol; drafted |
| 2026-08-09 | Defer faulty deployments, platform chaos faults and canary deployment | Avoids adding intervention dimensions before the first comparison is validated | Fault model/ADR 0007; proposed |
