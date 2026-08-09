# OpenTelemetry compatibility boundary

The normal fit probe still emits the existing structured JSONL event contract.
This branch adds a separate real SDK-to-Collector compatibility probe; it does
not silently replace the authoritative raw-event path.

Run the probe from the repository root with:

```powershell
.\scripts\run-opentelemetry-compatibility.ps1
```

The probe uses the Python SDK and OTLP HTTP exporter, sends traces through the
pinned Collector image, and records both the Collector's raw transport output
and decompressed OTLP protobuf in an independent sink. See
[`docs/observability/phase-2-otel-compatibility-probe.md`](../../docs/observability/phase-2-otel-compatibility-probe.md).

Until a result bundle passes the acceptance criteria, the compatibility path is
still provisional. The JSONL event bundles remain the authoritative
fit-probe evidence boundary.
