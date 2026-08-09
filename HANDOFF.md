# Phase 1B handoff — search execution and evidence batch 01

This package is intended to be applied on the user's local branch:
`research/phase-1-literature-evidence`.

It records the first supplementary discovery pass and a first-pass verified
evidence batch. It does **not** claim that the actual literature review is
complete and it does not replace the required authenticated ACM Digital Library,
IEEE Xplore and Scopus/Web of Science searches.

## Apply

Copy the contents of `docs/literature/` into the repository's
`docs/literature/` directory. Keep the existing protocol, seed matrix and
primary search log. Append `search-log-append.csv` to `search-log.csv` only if
the supplementary rows are to be retained in the same log; otherwise retain it
as an auditable annex.

The `evidence-batch-01.csv`, `quality-appraisal-batch-01.csv` and
`claim-register-batch-01.csv` files are append-only evidence-stage inputs. Do
not silently overwrite the existing seed files. After review, merge verified
rows into the canonical files with stable paper IDs and preserve the batch
files as provenance.

## Validation

```powershell
git diff --check
git status --short
```

Before committing, confirm that no restricted full-text PDFs or licensed
database exports have been copied into the repository.
