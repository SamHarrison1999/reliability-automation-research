# ADR 0019: Frozen primary batch and sequential execution guard

**Status:** Accepted

**Date:** 2026-08-10

## Context

The primary timing and analysis contracts are committed before primary data.
The remaining pre-data requirement is to bind the exact execution snapshot,
generate the 50-slot schedule and prevent accidental outcome-adaptive
reordering or arbitrary reserve use.

Committing generated batch files in the same commit as the execution code would
create an awkward provenance cycle: the batch needs to bind code that must
already have a stable commit and byte identity.

## Decision

Phase 5 Slice 6 uses two commits.

The first commit adds the batch-freeze generator, separate primary prototype and
guarded primary executor. No batch is generated and no Kubernetes trial runs in
that commit.

After that commit is clean and quality-validated, the freeze generator:

- requires no primary raw evidence;
- requires a clean tracked tree;
- binds the source commit SHA;
- binds exact SHA-256 values for all execution/analysis/prototype sources;
- generates the deterministic 50-slot run order;
- pre-declares exactly ten same-cell reserve templates;
- writes a deterministic timestamp-free batch manifest;
- accepts a byte-identical rerun but refuses divergent overwrite.

A second commit then stores only the generated run-order and batch artefacts.

Primary execution derives the next permissible action from preserved raw
evidence. The operator cannot select scenario, condition or slot. Primary
schedule slots execute sequentially. If an attempt is invalid, the next action
must be same-cell reserve 1; if that is invalid, same-cell reserve 2; exhaustion
pauses the pilot. A valid reserve resolves that planned repetition and execution
returns to the next primary schedule slot.

## Consequences

Outcome-adaptive primary reordering is structurally prevented.

Invalid evidence remains preserved.

The freeze commit can change repository HEAD without invalidating the source
snapshot: runtime verifies the exact bound file hashes, while the batch records
the earlier source commit that contained those files.

The primary executor reuses the already validated Kubernetes mechanics but
writes primary identity, actual attempt run order, planned schedule slot,
reserve provenance and the frozen batch/source binding.

No human-performance or production-readiness claim follows from this guard.
