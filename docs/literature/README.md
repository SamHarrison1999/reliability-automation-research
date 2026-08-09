# Literature review workspace

Phase 1 uses a scoping-review and systematic evidence-mapping design.

## Current stage

The protocol and database search strategy are finalised for platform
smoke-testing. The actual database searches, deduplication, screening, full-text
assessment, extraction, quality appraisal and synthesis have **not** yet been
completed.

Do not describe Phase 1 as complete until the exit criteria in
`phase-1-review-protocol.md` are met.

## Core documents

- `protocol-audit-and-rq-refinement.md` — audit decisions, refined PhD
  questions and final review questions;
- `phase-1-review-protocol.md` — versioned review protocol;
- `phase-1-search-execution-plan.md` — search families, database translations,
  smoke test and execution order;
- `search-log.csv` — one immutable provenance row per planned/executed query;
- `screening-log.csv` — title/abstract and full-text decisions;
- `evidence-matrix.csv` — full-text evidence chart;
- `full-text-charting-guide.md` — extraction and claim-boundary rules;
- `quality-appraisal-guide.md` and `quality-appraisal.csv` — design-sensitive
  critical appraisal;
- `claim-register.csv` — source-linked synthesis claims;
- `prisma-flow.csv` — record-flow counts and status; and
- `literature-map.md` — provisional and later verified evidence map.

## Evidence boundary

The nine existing records are a seed map. `abstract_only` records cannot support
substantive findings. `secondary_context_only` records assist terminology and
citation chasing but are not primary empirical studies. Compatibility probes,
prototype telemetry and Phase 2/3 technical records are project feasibility
evidence, not findings from the external literature.

System telemetry may measure technical events. It does not directly measure
engineer workload, cognition, trust, understanding or decision rationale.

## Immediate next gate

1. Confirm access to ACM Digital Library, IEEE Xplore and either Scopus or Web
   of Science Core Collection.
2. Smoke-test search families T, H and M without recording final result counts.
3. Record any prospective strategy amendment.
4. Execute and export the final queries.
5. Deduplicate the combined exports.
6. Run the 20-record title/abstract pilot before full screening.

Never invent or estimate database counts. Preserve exact queries, dates,
filters, export names and provenance.
