# ADR 0005: Use an OpenTelemetry-centred telemetry boundary

- **Status:** Accepted for the bounded technical trace path; metrics/logs backend remains open
- **Date:** 2026-08-08

## Context

The study needs correlated timestamps for workload requests, faults, deployment events, service state and recovery actions. A backend-specific instrumentation strategy could make the experiment harder to reproduce or transfer.

## Options considered

| Option | Evidence | Advantages | Risks/limitations |
|---|---|---|---|
| OpenTelemetry instrumentation and collector | [OpenTelemetry documentation](https://opentelemetry.io/docs/what-is-opentelemetry/) | Common instrumentation and transport boundary for traces, metrics and logs | Export loss, clock differences and collector configuration still need testing |
| Direct backend-specific instrumentation | Prometheus documentation and candidate design | May be simpler for a narrow metric set | Tighter coupling and weaker portability across backends |
| Vendor-specific observability stack | Not selected as a research dependency | Potentially rich operational features | Cost, opaque processing and transferability risks conflict with the reproducibility boundary |

## Decision

Use **OpenTelemetry as the instrumentation and transport candidate** for the fit probe. Use Prometheus as the first metrics-backend candidate, but leave the trace and log backend open until the compatibility test. Every raw event must carry an experiment identifier, run identifier, scenario identifier, source component, event type, timestamp and software/environment version information where applicable.

## Validation

- Verify correlation between a workload request and service/dependency spans.
- Measure whether event timestamps preserve the ordering needed by the proposed metrics.
- Test missing, duplicated and delayed telemetry handling.
- Export a raw event bundle without requiring a dashboard to interpret it.
- Repeat the same scenario and compare event completeness before any analysis.

## Consequences

Telemetry is evidence about system events and measurement infrastructure. It is not evidence of participant workload, trust, understanding or decision rationale. Those constructs require a separately approved human-participant protocol.

## Compatibility result

The pinned Python OpenTelemetry SDK/OTLP HTTP exporter `1.44.0` to
`otel/opentelemetry-collector:0.158.0` path passed the repository-controlled
compatibility probe. Run `otel-compat-20260809T140133761014Z-9e9c46bf` received
and decoded all five sequence-labelled spans, preserved the run identifier,
recorded non-zero non-decreasing timestamps and retained the Collector's
gzip-compressed transport payload.

This closes the small-trace SDK/Collector feasibility check. It does not close
load, metrics/logs, cross-host clock, Kubernetes-equivalence or backend
suitability questions. The structured JSONL bundle remains the audit-friendly
authoritative record until a reviewed production of the Phase 3 event contract
uses the compatibility path.
