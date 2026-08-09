# Literature-review Stage 1 handoff

Target branch: `research/complete-literature-review`

Apply this package at the repository root. It advances Phase 1 from draft review
infrastructure to a finalised v1.0 protocol and database search strategy.

## Files

- replaces `docs/literature/phase-1-review-protocol.md`;
- replaces `docs/literature/phase-1-search-execution-plan.md`;
- replaces `docs/literature/search-log.csv` with a richer, still-unexecuted
  provenance schema;
- updates `docs/literature/README.md`;
- adds `docs/literature/protocol-audit-and-rq-refinement.md`;
- adds `docs/literature/quality-appraisal-guide.md`; and
- adds `docs/literature/quality-appraisal.csv`.

The package does not overwrite the seed screening log, evidence matrix,
references, claim register, literature map, PRISMA ledger or full-text charting
guide.

## Evidence status

No database search count, screening decision, full-text finding or synthesis
claim was fabricated. The next task is to smoke-test and then execute the T, H
and M search families using the reviewer's authenticated database access.

## Suggested validation

```powershell
git diff --check
git status --short
```

Review the diff before committing because this package deliberately replaces
the protocol, search plan, search log and literature README.
