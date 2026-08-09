# OpenTelemetry compatibility result

The compatibility probe writes one `result.json` record per run under
`results/observability/opentelemetry/<run_id>/`.

## Required result fields

| Field | Meaning |
|---|---|
| `status` | `passed`, `failed` or `blocked` |
| `probe_version` | Version of the probe contract |
| `run_id` | Unique compatibility-probe run identifier |
| `collector_endpoint` | OTLP endpoint used by the SDK exporter |
| `expected_span_count` | Number of spans emitted by the probe |
| `received_payload_count` | Number of OTLP payloads received by the sink |
| `decoded_span_count` | Number of spans decoded from received protobuf payloads |
| `run_span_count` | Number of decoded spans carrying this run identifier |
| `sequence_values` | Sequence attributes observed in the received spans |
| `sequence_complete` | Whether every expected sequence value was received exactly once |
| `timestamps_parseable` | Whether received spans contain valid non-zero timestamps |
| `timestamps_non_decreasing` | Whether received span start timestamps preserve emission order |
| `payload_sha256` | Hashes of decompressed OTLP protobuf payloads |
| `raw_transport_payload_sha256` | Hashes of the exact HTTP bodies received by the sink, before decompression |
| `content_encodings` | HTTP `Content-Encoding` values observed for each payload |
| `span_records` | Decoded technical span records used for validation |

The decompressed protobuf payloads are retained in `raw-payloads.json` and as
sink-side `.pb` files. The exact HTTP bodies are retained as sink-side
`.transport` files and in `raw-payloads.json`. A passing result requires
complete sequence delivery and parseable timestamps. It is not evidence about
human workload, trust, understanding or decision rationale.
