# Phase 2 fit-probe results

**Probe:** `phase-2-fit-probe-v1`
**Execution date:** 2026-08-08
**Evidence type:** Synthetic technical feasibility only
**Status:** Local and Docker Desktop Kubernetes fit probes passed; the real OpenTelemetry SDK/Collector trace path also passed

## Scope

The probe challenged the smallest OrderFlow slice authorised by Phase 2: an order API calling an inventory dependency. It used a fixed synthetic order workload, versioned JSON manifests, a clean-reset procedure, controller events and service events written to JSON Lines bundles.

The local execution target was `local-process-fit-probe`. A separate Docker
Desktop Kubernetes execution used the same bounded service/scenario boundary
and is recorded separately under `results/fit-probe/kubernetes-raw/`.

## Reproduction

From the repository root:

```bash
python3 -m py_compile system/orderflow/service.py experiments/harness/fit_probe.py
python3 experiments/harness/fit_probe.py
```

The command writes the summary to `results/fit-probe/fit-probe-summary.json` and raw event bundles under `results/fit-probe/raw/`.

## Runs

| Scenario | Run identifier | Raw events | Workload outcome | Result |
|---|---|---:|---|---|
| No fault, version update and rollback | `no-fault-v1-20260808T181955409346Z-36d519eb` | 116 | 10 successful, 0 failed | Passed |
| Inventory service termination | `service-termination-v1-20260808T182004377879Z-51acf959` | 81 | 4 successful, 3 failed, 2 recovery requests successful | Passed |
| Inventory dependency latency, 120 ms | `dependency-latency-v1-20260808T182011049940Z-50ac0833` | 82 | 7 successful, 0 failed; fault-period request latency about 125 ms | Passed |
| Clean-reset repeat of dependency latency | `dependency-latency-v1-20260808T182015902974Z-e98e7be9` | 81 | 7 successful, 0 failed; fault-period request latency about 130 ms | Passed |

The two dependency-latency runs used the same scenario manifest and the second records the first run identifier in `repeat_of`. Their controller event sequences were structurally identical, with the expected runtime timing variation.

## Acceptance checks

All local runs passed the following checks:

- unique run identifier;
- versioned scenario and environment manifests;
- distinguishable scenario identifier;
- required reset, workload, fault, recovery and completion event classes;
- timestamps on all events;
- trace fields on service events;
- explicit target component for fault scenarios;
- inspectable JSON Lines raw records; and
- clean-state verification before workload execution.

The no-fault run also recorded an `order-api-v1` to `order-api-v2` deployment transition, a readiness check, a rollback to `order-api-v1` and successful post-rollback requests.

## Interpretation

The local and Kubernetes probes support carrying the following bounded choices
forward:

1. OrderFlow is sufficiently small and controllable for the next technical design stage.
2. Harness-controlled service and dependency faults are targetable, timestamped and reversible in the local slice.
3. A portable controller and structured telemetry contract can produce raw records without dashboard access.
4. Docker image packaging and Docker Desktop Kubernetes are feasible for the
   declared technical pilot environment.

The probes do not establish runtime equivalence across environments, lossless
telemetry under load, backend suitability, or that any automation strategy
improves reliability. They also do not compare OrderFlow with the adapted
open-source benchmark alternative.

## Limitations and required follow-up

- Preserve local-process and Docker Desktop Kubernetes records as separate evidence streams.
- Use the selected OpenTelemetry path in Phase 3 trials and exclude any trial whose telemetry boundaries cannot be established.
- Compare the local contract with Docker Compose only if Compose remains a candidate development path.
- Validate load, metrics/logs, cross-host clock and Kubernetes telemetry equivalence separately if they become necessary.
- Keep the raw records classified as synthetic technical-feasibility evidence; they are not reliability findings, participant data or human evidence.
