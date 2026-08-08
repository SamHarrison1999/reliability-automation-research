# ADR 0002: Keep technology choices provisional until research criteria are reviewed

- **Status:** Accepted for Phase 0
- **Date:** 2026-08-08

## Context

The source proposal names Docker, Kubernetes, GitHub Actions, Prometheus and Grafana. Naming tools does not yet explain why they are suitable for this empirical study. Other tools may offer better reproducibility, observability, fault control or cost characteristics.

## Decision

Do not treat the proposal's technology names as permanent selections. Phase 1 will establish the evidence base and Phase 2 will compare candidate tools against explicit criteria:

- reproducibility and reset reliability;
- experimental control and fault-injection precision;
- observability completeness and timestamp quality;
- support for the chosen deployment model;
- cost and local/CI feasibility;
- version stability and maintenance;
- explainability to participants and reviewers; and
- threats to internal and external validity.

Technology decisions must be recorded in new ADRs with alternatives, evidence, consequences and validation checks.

## Consequences

The first repository contains no application stack. This delays implementation slightly but reduces the risk of building an impressive system whose design cannot answer the research questions.
