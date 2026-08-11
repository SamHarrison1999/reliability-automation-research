# ADR 0024: Phase 6 participant data boundary

- **Status:** Accepted
- **Date:** 2026-08-12

## Decision

All future participant-identifiable and participant-level pseudonymised data
remain outside the public Git repository.

Identity/administration information is separated from research observations.

The study uses data minimisation and does not intentionally collect
special-category data.

An institutional DMP and any required Data Protection review remain mandatory
before data collection.

## Consequences

The public repository can reproduce the protocol and synthetic analysis
structure without exposing participants.

Participant-level reproducibility will rely on controlled institutional data
access/provenance rather than public raw-data commits.
