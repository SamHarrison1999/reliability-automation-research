# ADR 0001: Separate research evidence from implementation artefacts

- **Status:** Accepted for Phase 0
- **Date:** 2026-08-08

## Context

The proposed study contains both technical reliability outcomes and claims about engineering decision-making. The repository must not blur software infrastructure, experimental variables, empirical data and findings.

## Decision

Use explicit top-level boundaries:

- `system/` and `infrastructure/` for research infrastructure;
- `experiments/` for versioned scenarios, manifests and harness code;
- `data/raw/` for immutable collected records, excluded from Git;
- `data/processed/` for derived datasets, excluded from Git;
- `analysis/` for scripts/notebooks that derive results from data;
- `results/` for generated artefacts; and
- `docs/` for protocols, decisions, literature and interpretation.

Participant data, recordings, credentials and personally identifying information must not be committed. A technical pilot must not be described as a human-participant result.

## Consequences

The structure creates some duplication in documentation, but it makes provenance and claims easier to audit. Automated validation will fail when protected data directories contain files other than `.gitkeep`.
