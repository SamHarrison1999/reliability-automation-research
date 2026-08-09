# ADR 0008: Validate the OpenTelemetry SDK/Collector boundary with a raw sink

- **Status:** Accepted for the pinned technical trace path; broader telemetry validation remains open
- **Date:** 2026-08-09

## Context

Phase 2 selected an OpenTelemetry-centred instrumentation and transport
boundary provisionally, but the original fit probe used only an
OpenTelemetry-compatible JSONL event contract. A real SDK-to-Collector path
was required before it could be used as a technical-pilot telemetry path.

## Decision

Use a version-pinned Python SDK, OTLP/HTTP, local OpenTelemetry Collector and
repository-controlled raw sink for the technical trace path. Retain the raw
transport body and decoded OTLP protobuf separately. Keep the JSONL event
bundle as an audit-friendly evidence boundary; a dashboard is never required
to interpret a trial.

## Result

The corrected v2 probe passed on 2026-08-09 under run
`otel-compat-20260809T140133761014Z-9e9c46bf`: five emitted spans were received,
decoded and matched to sequence values 1–5 exactly once, with parseable
non-decreasing timestamps. The transport was recorded as `gzip`, and both the
raw transport payload and decoded payload were retained. The tested package
set was OpenTelemetry Python `1.44.0`; the Collector image was
`otel/opentelemetry-collector:0.158.0`.

## Interpretation boundary

This result establishes only the tested small-trace Python/Collector/OTLP path.
It does not establish losslessness under load, metrics/logs compatibility,
cross-host clock accuracy, Kubernetes telemetry equivalence, backend
suitability or human-participant validity.

