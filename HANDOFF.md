# OpenTelemetry compatibility handoff

Target branch: `feat/opentelemetry-compatibility-check`

Apply this package at the repository root after switching to that branch. It
adds a real Python SDK -> OTLP HTTP -> OpenTelemetry Collector -> HTTP sink
probe. The probe preserves the received OTLP protobuf payloads and writes a
machine-readable result record. It does not claim compatibility until the
Docker-backed command completes successfully.

Run after extraction:

```powershell
.\scripts\run-opentelemetry-compatibility.ps1
```

The result is written under `results/observability/opentelemetry/`. The stack
is removed after the probe unless `-KeepStack` is supplied.

The sink handles the Collector's gzip-compressed OTLP/HTTP export. It stores
the decompressed protobuf for independent decoding and preserves the original
transport body separately for hashing and auditability.

The current workspace could not execute this probe because Docker and the
OpenTelemetry Python packages are unavailable here.
