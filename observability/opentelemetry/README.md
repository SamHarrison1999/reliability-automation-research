# OpenTelemetry compatibility boundary

The service currently emits an OpenTelemetry-compatible structured event
contract to JSONL. It does not yet use an OpenTelemetry SDK or Collector.

`collector-config.yaml` is an optional, local-only configuration for a later
compatibility probe. It accepts OTLP over HTTP or gRPC and writes received
records to the Collector debug exporter. It is intentionally not started by
the normal fit probe and does not introduce a permanent metrics, trace or log
backend.

The compatibility probe must separately test SDK instrumentation, Collector
configuration, event completeness, timestamp ordering, duplicate or delayed
records, and raw-bundle export. Until those tests pass, the existing JSONL
records remain the authoritative fit-probe evidence boundary.

