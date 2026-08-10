# Phase 4 reproducibility validation

**Evidence type:** Synthetic technical reproducibility evidence only
**Phase:** 4 — Reproducible technical prototype
**Validation date:** 2026-08-10
**Acceptance source commit:** `207337f481f81e34d99bb9682ee2a642709e1fe4`
**Controller:** `phase-4-reproducibility-controller-v1.2`

## Result

Phase 4 met its declared reproducibility exit evidence: the smallest OrderFlow
benchmark was reset, deployed and observed reproducibly on the bounded Docker
Desktop Kubernetes target.

Two fresh full-telemetry validation executions passed every declared validity
check without a source/configuration change between them:

| Acceptance run | Result | Validity checks | Workload | OTel order-span parity |
|---|---|---:|---:|---:|
| `phase4-repro-20260810T134202072483Z-5a519a99` | Passed | 16/16 | 3/3 HTTP 201 | 15/15 |
| `phase4-repro-20260810T134620018339Z-4efc01f5` | Passed | 16/16 | 3/3 HTTP 201 | 15/15 |

Both runs used independent run identifiers and fresh output directories.

## Cross-run invariants

The inspected final runs agreed on all pre-specified reproducibility invariants:

- repository commit: `207337f481f81e34d99bb9682ee2a642709e1fe4`;
- controller version: `phase-4-reproducibility-controller-v1.2`;
- Kubernetes context: `docker-desktop`;
- Kubernetes manifest SHA-256: `0defaabd9d685a9cd5eb20fb2d59e89b6caba4f9130d198ee32169b8b235e261`;
- prototype manifest SHA-256: `8f131766f323dcdb5930e0b0ba3ac611bab4089646e40fb32e486674afe79ba5`;
- OrderFlow inventory/order-api/telemetry-sink image identity:
  `sha256:57e69aa0c2962b4371112a93a12638322e4e7fc472d9d7c065b75c616d004514`;
- OpenTelemetry Collector image:
  `otel/opentelemetry-collector:0.158.0`;
- Collector image identity: `sha256:5b97e6e3550ec6e48a71dba6f6304d349a293af8df4ee1f51da67be94fce2ecd`;
- OTel requirements-lock SHA-256: `9b0cd979109fe6054562678dce5ddb6089bf309ab8e0955de68c4e28dbd239e8`;
- three deterministic synthetic order requests accepted per run;
- 15 order-related structured events mirrored into 15 decoded OTel spans per run;
- five order-related events/spans per order;
- both `order-api` and `inventory` represented in the OTel evidence;
- exact structured-event signature parity reported `true`; and
- namespace absence verified after cleanup.

The run-specific latency values are retained as raw observations but are not
treated as reproducibility invariants or as Phase 4 findings.

## Observation boundary

The JSONL service-event stream remains the authoritative audit record.
OpenTelemetry is an independent, bounded trace-transport validation path.

Each mirrored OTel span carries the structured event's run, component, event,
order and structured trace/span identifiers as attributes. The OTel SDK also
creates its own transport span/trace identifiers. Phase 4 therefore establishes
auditable OTel observation and correlation, **not** propagated end-to-end
distributed tracing context.

The Collector path is limited to small technical trace telemetry:

```text
OrderFlow event
  -> OpenTelemetry Python SDK / OTLP HTTP 1.44.0
  -> OpenTelemetry Collector 0.158.0
  -> repository-controlled telemetry sink
  -> retained transport body + decoded OTLP protobuf
```

No dashboard, metrics pipeline or logs pipeline is required as evidence.

## Development-run provenance

Earlier Phase 4 runs are intentionally retained rather than deleted or
rewritten:

| Run | Classification | Outcome |
|---|---|---|
| `phase4-repro-20260810T124057041846Z-339f0021` | development failure | Rollout timed out because the Docker Desktop Kubernetes node did not yet contain the locally built images. |
| `phase4-repro-20260810T125936013508Z-e4f884fc` | development failure | The first automated import attempted to reference a host temporary archive from inside the Kubernetes node container. |
| `phase4-repro-20260810T130407749389Z-c7a2ab97` | successful pre-OTel reproducibility validation | Deployment/readiness/workload/structured observation/reset passed, but this run predates the required Collector/OTLP Phase 4 acceptance path. |
| `phase4-repro-20260810T134202072483Z-5a519a99` | final acceptance run 1 | Passed all full-telemetry Phase 4 checks. |
| `phase4-repro-20260810T134620018339Z-4efc01f5` | final acceptance run 2 | Passed all full-telemetry Phase 4 checks and reproduced the declared invariants from run 1. |

The failed runs are development evidence about harness/environment corrections,
not excluded empirical trials and not evidence of reliability effects.

## Interpretation boundary

This evidence supports only the Phase 4 methodological statement that the
bounded prototype can be built, reset, deployed and observed reproducibly in
the declared local Kubernetes environment.

It does **not** establish:

- that automation improves reliability;
- comparative detection/recovery/failure-impact outcomes;
- production readiness or scalability;
- OTel losslessness under load;
- local-process/Kubernetes timing equivalence;
- human workload, trust, understanding or decision quality; or
- any participant-study conclusion.

Those claims remain outside Phase 4. Condition-by-scenario technical pilot
execution and analysis belong to Phase 5.
