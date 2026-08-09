# OpenTelemetry implementation plan

OpenTelemetry is the selected instrumentation and transport candidate, not a
completed Phase 2 validation result. The current fit probe uses a compatible
structured JSONL event contract so raw records can be inspected without a
dashboard or backend.

The optional Collector configuration is in
[`observability/opentelemetry/collector-config.yaml`](../../observability/opentelemetry/collector-config.yaml).
It is a compatibility-probe input only. Grafana, Prometheus, Elasticsearch,
Kibana and Logstash are deliberately not required for this stage.

The next probe should record:

- SDK and Collector versions;
- event completeness and export failures;
- timestamp ordering and clock assumptions;
- duplicate, delayed and missing record handling; and
- whether the raw event bundle can still be exported independently of a UI.

No telemetry result should be interpreted as participant workload, trust,
understanding or decision rationale. Those constructs require the separately
approved human-participant protocol.

