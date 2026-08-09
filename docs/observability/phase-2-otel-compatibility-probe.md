# Phase 2 OpenTelemetry SDK/Collector compatibility probe

**Status:** Probe implemented; execution evidence pending

The probe accepts the Collector's standard gzip-compressed OTLP/HTTP export,
decompresses it before protobuf parsing, and retains the original transport
body separately. This is required because the Collector's OTLP/HTTP exporter
uses gzip compression by default.

## Purpose

This probe tests the specific Phase 2 boundary that remained unvalidated: a
Python OpenTelemetry SDK emits OTLP HTTP traces, an OpenTelemetry Collector
receives and forwards them, and an independent HTTP sink records the received
protobuf payloads for decoding and completeness checks.

It is a compatibility and measurement-quality test. It is not a performance
experiment and does not select a permanent backend.

## Stack

| Component | Role | Version boundary |
|---|---|---|
| OpenTelemetry Python SDK | Creates the test spans | 1.44.0 package set |
| OTLP HTTP exporter | Sends protobuf traces to the Collector | 1.44.0 package set |
| OpenTelemetry Collector | Receives OTLP and exports to the sink | 0.158.0 image |
| HTTP sink | Stores raw HTTP transport bodies and decoded OTLP protobuf for independent decoding | Repository probe code |

The versions are pinned for this probe so that a future run can distinguish a
compatibility change from an unrecorded dependency update.

## Procedure

From the repository root on Windows:

```powershell
.\scripts\run-opentelemetry-compatibility.ps1
```

The script installs the observability extra, starts the Collector and sink,
emits five spans, waits for the sink to receive data, decompresses and decodes
the received OTLP protobuf payloads and writes a raw/result bundle. It removes the
containers and network when complete.

Use `-KeepStack` only when diagnosing a failed run. Do not edit the generated
result bundle by hand.

## Acceptance criteria

- the Collector becomes reachable on OTLP HTTP;
- the sink receives at least one OTLP payload;
- every emitted sequence value is received exactly once;
- every received span has a non-zero timestamp;
- the run identifier is preserved through the SDK, Collector and sink path;
- raw transport payload hashes, content encodings and decoded records are retained; and
- the result records the exact package/image versions and host context.

If Docker, package installation, Collector startup, export, decoding or
completeness fails, the result is a failed or blocked compatibility check. It
must not be converted into a pass by omitting missing spans.

## Interpretation boundary

A pass supports the provisional use of the SDK/Collector path for technical
telemetry in the fit probe. It does not establish losslessness under load,
cross-host clock accuracy, Kubernetes compatibility, backend suitability or
human-participant validity. Those require separate tests.
