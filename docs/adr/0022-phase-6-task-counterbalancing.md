# ADR 0022: Phase 6 matched task and counterbalance design

- **Status:** Accepted
- **Date:** 2026-08-12

## Decision

Use four matched OrderFlow task variants and four deterministic counterbalance
sequences.

Each participant sees two manual-decision and two automation-assisted tasks.

Across sequence groups each task variant appears equally under both human
conditions.

Each participant's two automation-assisted tasks contain one correct and one
incorrect recommendation.

## Rationale

This provides direct evidence of:

- diagnosis;
- recovery selection;
- escalation;
- acceptance;
- override; and
- reliance calibration.

The design separates human-facing decision support from Phase 5 autonomous
technical recovery.

## Safety

All actions are simulated through a bounded interface.

Participants never receive unrestricted shell or Kubernetes access.
