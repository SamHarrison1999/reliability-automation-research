# ADR 0014: Phase 4 OpenTelemetry runtime observation path

- Status: Accepted
- Date: 2026-08-10

## Context

Phase 4 requires the smallest OrderFlow benchmark to be deployed and observed
reproducibly. Phase 2 already validated a bounded trace transport using
OpenTelemetry Python 1.44.0, OTLP/HTTP and OpenTelemetry Collector 0.158.0.
The Phase 4 JSONL event stream remains the authoritative audit record.

## Decision

Phase 4 mirrors each structured OrderFlow service event into one OpenTelemetry
span. The span carries the run identifier, component, event type, order
identifier when present, and the structured event trace/span identifiers.

The runtime uses a version-controlled exact dependency lock at
`observability/opentelemetry/phase4-requirements.lock` (SHA-256 `9b0cd979109fe6054562678dce5ddb6089bf309ab8e0955de68c4e28dbd239e8`),
installs binary wheels only, and exports to the in-cluster Collector over OTLP/HTTP. The Collector image is
`otel/opentelemetry-collector:0.158.0` with digest
`sha256:5b97e6e3550ec6e48a71dba6f6304d349a293af8df4ee1f51da67be94fce2ecd` and exports traces to the existing repository-controlled
HTTP sink.

The reproducibility controller retains both decoded and original OTLP payloads
and requires the 15 order-related spans from the fixed three-request workload
to match the 15 order-related structured JSONL events exactly.

## Consequences

This supplies an independent, auditable trace transport without changing the
OrderFlow request semantics or replacing the JSONL audit record.

The approach intentionally does not claim production-grade distributed tracing,
losslessness under load, metrics/logs coverage, backend suitability, dashboard
quality, cross-host clock accuracy, or human-participant validity. Those remain
outside the Phase 4 evidence boundary.
