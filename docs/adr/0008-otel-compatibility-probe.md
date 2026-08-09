# ADR 0008: Validate the OpenTelemetry SDK/Collector boundary with a raw sink

- **Status:** Proposed until the Docker-backed probe passes
- **Date:** 2026-08-09

## Context

Phase 2 selected an OpenTelemetry-centred instrumentation and transport
boundary provisionally, but the repository had only an OpenTelemetry-compatible
JSONL event contract. A real SDK-to-Collector path must be tested before it is
used as the technical experiment's primary telemetry path.

## Options considered

| Option | Evidence | Advantages | Risks/limitations |
|---|---|---|---|
| Python SDK -> OTLP Collector -> independent raw HTTP sink | Phase 2 observability ADR; official OpenTelemetry exporter and Collector documentation | Tests the real transport while retaining raw payloads for independent verification | Trace-only probe; does not establish load behaviour or backend suitability |
| SDK -> vendor/backend directly | Not selected | Fewer local components | Couples the research evidence boundary to a backend and makes payload verification less independent |
| Continue with structured JSONL only | Existing fit-probe evidence | Minimal and easy to inspect | Does not validate the intended SDK/Collector compatibility boundary |

## Decision

Add a separate, version-pinned compatibility probe using the Python SDK, OTLP
HTTP, a local OpenTelemetry Collector and a repository-controlled raw sink.
The probe sends sequence-labelled spans and decodes the Collector's forwarded
OTLP protobuf payloads. The JSONL event contract remains authoritative until a
passing result is reviewed.

## Validation

The probe passes only when the Collector and sink are reachable, every emitted
sequence is received exactly once, timestamps are parseable, the run identifier
survives the path, and the raw transport plus decoded payload/result bundle is
retained. The sink explicitly handles the Collector's gzip-compressed OTLP/HTTP
export and records its content encoding.

## Consequences

The result establishes only the tested Python/Collector/OTLP path for small
technical traces. It does not establish losslessness under load, Kubernetes
compatibility, cross-host clock accuracy, metrics/logs compatibility or human
participant validity. Those remain separate validation tasks.
