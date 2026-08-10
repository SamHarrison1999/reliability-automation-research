# Progress ledger

## Project status

- **Current phase:** Phase 5 - experiment harness and technical pilot (complete); Phase 6 human-participant protocol and ethics is the next gate
- **Status:** Phase 5 exit criterion satisfied; 50 planned slots resolved from 53 preserved attempts, with deterministic processed data and descriptive analysis committed
- **Empirical data collected:** Phase 5 comparative technical-pilot evidence plus earlier feasibility/reproducibility records; no participant or production data
- **Participant recruitment:** Not started
- **Ethics approval:** Not obtained
- **Application implementation:** Minimal reproducible OrderFlow prototype and frozen Phase 5 technical-pilot harness complete; participant protocol execution has not started

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

- [x] Fault model and scenario catalogue finalised (`docs/fault-model/phase-3-fault-model.md`)
- [x] Manual versus rule-based automated recovery boundary finalised
- [x] Technical metric catalogue operationalised (`docs/metrics/technical-metrics.md`)
- [x] Developer-practice measurement boundary specified separately (`docs/metrics/developer-practice-metrics.md`)
- [x] Technical experiment protocol finalised for implementation (`docs/protocols/phase-3-technical-experiment.md`)
- [x] Machine-readable trial manifest and contract committed (`experiments/manifests/phase-3-trial-manifest.json`)
- [x] Metric provenance record documented (`data/schemas/metric-observation-record.md`)
- [x] Phase 3 decision ADR drafted (`docs/adr/0007-phase-3-fault-metrics-protocol.md`)
- [x] Trial-flow diagram drafted
- [x] Review against the accessible Phase 1 evidence map (`docs/research-design/phase-3-evidence-review.md`)
- [x] Implement and validate the Phase 3 trial harness/event additions
- [x] Complete dry-runs for each scenario and recovery condition

### Phase 3 evidence boundary

The existing Phase 2 raw bundles are not Phase 3 comparison trials: they lack the final automation-condition and explicit detection-event contract. They remain synthetic technical-feasibility evidence. No metric from them should be presented as evidence that an automation strategy improves reliability.

The Phase 3 local-process harness was validated with an initial and a repeat
five-trial dry-run matrix. Each matrix selected five trials, produced five
valid trials and excluded none. The dry-run records are feasibility evidence
only and are not pilot findings.

### Phase 3 decision log

| Date | Decision | Reason | Evidence/status |
|---|---|---|---|
| 2026-08-09 | Compare standardised manual recovery with rule-based automated recovery | Isolates recovery initiation while holding fault, workload, detection rule, versions and reset constant | ADR 0007; accepted for implementation |
| 2026-08-09 | Retain no-fault, service-termination and dependency-latency scenarios | Preserves the smallest Phase 2 feasibility set | Fault model; final design boundary |
| 2026-08-09 | Make detection latency, recovery time and failure impact primary outcomes | Gives each RQ1 outcome an explicit event boundary before implementation | Technical metric catalogue; operationalised |
| 2026-08-09 | Require immutable trial manifests and explicit exclusion records | Prevents post-hoc condition changes, silent imputation and contamination | Technical protocol and manifest contract; finalised |
| 2026-08-09 | Keep developer-practice measures separate from technical telemetry | Prevents system events being mislabelled as workload, trust, understanding or decision rationale | Developer-practice metric specification; provisional for later ethics review |
| 2026-08-09 | Defer faulty deployments, platform chaos faults and canary deployment | Avoids adding intervention dimensions before the first comparison is validated | Fault model/ADR 0007; accepted boundary |

## Phase 4 record

### Objective

Promote the minimal OrderFlow feasibility slice into a versioned technical
prototype that can be reset, deployed and observed reproducibly on the bounded
Docker Desktop Kubernetes target without executing the Phase 5 comparison
experiment.

### Deliverables

- [x] Phase 4 research-design gate and explicit Phase 4/Phase 5 boundary
- [x] Versioned OrderFlow prototype manifest and immutable base-image provenance
- [x] Prototype-specific Kubernetes deployment contract
- [x] Reproducibility controller with clean-state, provenance and fresh-output checks
- [x] Explicit Docker-to-Kubernetes-node image import with digest equality checks
- [x] Pinned OpenTelemetry 1.44.0 / Collector 0.158.0 trace path
- [x] Version-controlled OTel dependency lock and Collector digest
- [x] Raw/decoded OTLP payload retention and structured-event/OTel parity validation
- [x] Two fresh final full-telemetry reproducibility validations
- [x] Derived Phase 4 reproducibility summary separated from raw run bundles
- [x] Final repository-wide close-out quality gate

### Validation evidence

Final acceptance runs:

- `phase4-repro-20260810T134202072483Z-5a519a99`
- `phase4-repro-20260810T134620018339Z-4efc01f5`

Both runs used repository commit
`207337f481f81e34d99bb9682ee2a642709e1fe4`, controller
`phase-4-reproducibility-controller-v1.2`, identical Kubernetes/prototype
manifest hashes, identical OrderFlow image identity, identical pinned Collector
identity, three successful synthetic requests, exact 15/15 structured-event to
OTel order-span parity and verified clean teardown.

The development failures and the successful pre-OTel run remain retained
unchanged as provenance. See `docs/reproducibility/phase-4-validation.md` and
`results/phase-4/phase-4-reproducibility-summary.json`.

### Phase 4 evidence boundary

Phase 4 establishes reproducible build/deploy/workload/observation/reset
behaviour only. It does not estimate reliability effects, compare recovery
conditions, establish production readiness or provide human-participant
evidence.

### Phase 4 decision log

| Date | Decision | Reason | Evidence/status |
|---|---|---|---|
| 2026-08-10 | Keep the two-service OrderFlow slice as the Phase 4 research object | It satisfies the declared deployment/workload/observation boundary without adding business-domain scope | `docs/research-design/phase-4.md` |
| 2026-08-10 | Pin build provenance and disable BuildKit provenance attestations for the local validation images | Prevents attestation metadata from changing the outer image identity across otherwise identical local builds | ADR 0013 |
| 2026-08-10 | Explicitly stream Docker images into the Docker Desktop Kubernetes node runtime | `imagePullPolicy: Never` requires node-visible images; the normal Docker image store was insufficient | Phase 4 development failure provenance; controller v1.1+ |
| 2026-08-10 | Mirror structured events into the bounded OTel trace path while retaining JSONL as authoritative | Adds independent trace-transport evidence without replacing the audit record or broadening into metrics/logs dashboards | ADR 0014 |
| 2026-08-10 | Require two final runs under the completed OTel architecture | Prevents the earlier pre-OTel success from being misclassified as final Phase 4 acceptance evidence | Final runs listed above |
## Phase 5 record

### Objective

Execute the bounded technical pilot defined by the Phase 3 protocol on
the reproducible Phase 4 OrderFlow platform, preserve complete attempt
provenance, derive the frozen technical metrics and perform bounded
descriptive analysis without crossing into participant or
production-readiness claims.

### Deliverables

- [x] Phase 5 pilot design gate and machine-readable manifest
- [x] Deterministic 50-slot balanced run order and frozen batch
- [x] Primary trial controller with manual and rule-based automated recovery
- [x] Development validation separated from primary evidence
- [x] Monotonic-clock primary metric derivation
- [x] 53 preserved primary/reserve attempts
- [x] 50 valid resolving observations across five balanced design cells
- [x] Three invalid attempts preserved without imputation
- [x] Deterministic processed-dataset derivation
- [x] Byte-for-byte reproduced processed dataset
- [x] Deterministic descriptive-analysis tooling
- [x] Byte-for-byte reproduced descriptive-analysis result
- [x] Phase 5 result interpretation and closeout documentation

### Validation evidence

The immutable raw-corpus anchor is:

`b832c96c1dd3665f6025394447b35db58cd0e2a9`

The processed-dataset anchor is:

`be3119d44842a8b737a86e0f40dca37b3aa4dbf7`

The descriptive-result anchor is:

`76396710e96088f79323039ae3a91aa3e53732c0`

The descriptive result SHA-256 is:

`547aff9a56dc3fa4dac09929f68c5d57248338af0f317cc7951bca0a0e5170ed`

Collection resolved all 50 planned slots from 53 attempts. The invalid
run orders were 19, 21 and 22; reserve run orders were 20, 22 and 23.
No invalid primary metric was imputed.

### Principal pilot findings

Dependency-latency trials showed a small, directionally consistent
reduction in recovery time under the automated condition.

Service-termination trials showed substantial timing variability and
no consistent paired recovery-time advantage.

Failure impact did not discriminate between recovery conditions under
either fault model.

These findings are descriptive technical-pilot evidence and do not
constitute confirmatory or production-level evidence.

### Phase 5 evidence boundary

Phase 5 establishes bounded comparative technical evidence for the
purpose-built OrderFlow pilot only.

It does not establish:

- statistical significance;
- production readiness;
- generalisable causal effects;
- developer workload;
- developer trust;
- developer understanding;
- human decision rationale.

Human-participant evidence remains a separate Phase 6/7 stream.

### Phase 5 decision log

| Date | Decision | Reason | Evidence/status |
|---|---|---|---|
| 2026-08-10 | Freeze a balanced 50-slot primary schedule before primary collection | Prevents post-result changes to condition allocation or repetition order | `phase-5-primary-batch-v1`; immutable batch provenance |
| 2026-08-10 | Preserve invalid attempts and resolve planned slots only through the predefined reserve mechanism | Prevents silent deletion, imputation or ad-hoc reruns | 53 attempts; invalid run orders 19, 21 and 22 |
| 2026-08-10 | Use controller monotonic timestamps for primary elapsed durations | Avoids wall-clock adjustment effects and UTC fallback | `phase-5-primary-timing-v1` |
| 2026-08-10 | Treat detection latency as a shared-detector fidelity/balance measure | Both recovery conditions use the same detector | Phase 5 descriptive-analysis contract |
| 2026-08-10 | Keep the Phase 5 analysis descriptive | The technical pilot is not a powered confirmatory study | No NHST, p-values or significance claims |
| 2026-08-10 | Close Phase 5 without additional post-result trials | The frozen schedule is complete and the exit criterion is met | `docs/pilot/phase-5-closeout.md` |
