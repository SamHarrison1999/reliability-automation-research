# Phase 4 validation results

This directory contains **synthetic technical reproducibility evidence only**.

## Layout

- `raw/<run-id>/` — immutable per-run controller, workload, structured-event,
  provenance, validity and (where applicable) OTel transport/span records.
- `phase-4-reproducibility-summary.json` — derived cross-run close-out summary.

Raw run directories must not be edited, renamed, reused or overwritten after
execution. Failed development runs are retained alongside successful runs.

The two final Phase 4 acceptance runs are:

- `phase4-repro-20260810T134202072483Z-5a519a99`
- `phase4-repro-20260810T134620018339Z-4efc01f5`

The detailed interpretation and evidence boundary are documented in
`docs/reproducibility/phase-4-validation.md`.

These records contain no participant data, personal data, production traffic or
real payment information.
