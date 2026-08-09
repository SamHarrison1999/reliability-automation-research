# Phase 2 OpenTelemetry compatibility result

**Status:** Passed for the pinned technical trace path
**Probe version:** `otel-sdk-collector-compatibility-v2`
**Run:** `otel-compat-20260809T140133761014Z-9e9c46bf`
**Completed:** 2026-08-09
**Evidence type:** Synthetic technical compatibility evidence only

## Tested path

```text
OpenTelemetry Python SDK 1.44.0
  -> OTLP/HTTP exporter 1.44.0
  -> OpenTelemetry Collector 0.158.0
  -> repository-controlled HTTP sink
  -> decompressed OTLP protobuf decoding
```

The sink retained the original gzip-compressed transport body and the decoded
protobuf payload separately. This fixed the first probe's transport/decoding
failure and makes the transport representation auditable.

## Result

| Check | Result |
|---|---|
| Collector reachable | Passed |
| Sink received payload | Passed; 1 payload |
| Expected spans | 5 |
| Decoded spans | 5 |
| Run identifier preserved | Passed |
| Sequence values | `1, 2, 3, 4, 5` |
| Sequence complete exactly once | Passed |
| Timestamps parseable | Passed |
| Timestamp order non-decreasing | Passed |
| Transport encoding recorded | `gzip` |
| Python packages | `opentelemetry-api`, `sdk`, `proto` and OTLP HTTP exporter `1.44.0` |
| Collector image | `otel/opentelemetry-collector:0.158.0` |

The machine-readable result is retained at:

`results/observability/opentelemetry/otel-compat-20260809T140133761014Z-9e9c46bf/result.json`

The first v1 run is also retained as provenance: it was blocked by attempting
to decode the Collector's gzip-compressed body before the v2 fix. It is not
counted as a passing run.

## Interpretation boundary

This result supports using the pinned Python SDK/OTLP HTTP/Collector path for
small technical trace telemetry in the next stage. It does not establish
losslessness under load, metrics or logs compatibility, cross-host clock
accuracy, Kubernetes telemetry equivalence, backend suitability or any human
participant construct. Those require separate validation.
