# Progress ledger

## Project status

- **Current phase:** Phase 1 - scoping review and literature map
- **Status:** In progress; protocol and seed evidence map created, database searches and full-text charting outstanding
- **Empirical data collected:** None
- **Participant recruitment:** Not started
- **Ethics approval:** Not obtained
- **Application implementation:** Not started

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
