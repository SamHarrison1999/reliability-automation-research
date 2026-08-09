# OpenTelemetry implementation plan

OpenTelemetry is accepted for the pinned small-trace technical path. The
current fit probe also retains a compatible structured JSONL event contract so
raw records can be inspected without a dashboard or backend.

The optional Collector configuration is in
[`observability/opentelemetry/collector-config.yaml`](../../observability/opentelemetry/collector-config.yaml).
It is a compatibility-probe input only. Grafana, Prometheus, Elasticsearch,
Kibana and Logstash are deliberately not required for this stage.

The completed compatibility probe recorded:

- SDK and Collector versions;
- event completeness and export representation;
- timestamp ordering and run correlation; and
- raw transport and decoded payload hashes.

The result is recorded in
[`phase-2-otel-compatibility-result.md`](phase-2-otel-compatibility-result.md).
Load behaviour, metrics/logs compatibility, cross-host clock assumptions and
Kubernetes telemetry equivalence remain open validation tasks.

No telemetry result should be interpreted as participant workload, trust,
understanding or decision rationale. Those constructs require the separately
approved human-participant protocol.
