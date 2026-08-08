# Phase 2 fit-probe results

**Probe:** `phase-2-fit-probe-v1`  
**Execution date:** 2026-08-08  
**Evidence type:** Synthetic technical feasibility only  
**Status:** Local fit probe passed; Kubernetes and a real OpenTelemetry collector remain untested

## Scope

The probe challenged the smallest OrderFlow slice authorised by Phase 2: an order API calling an inventory dependency. It used a fixed synthetic order workload, versioned JSON manifests, a clean-reset procedure, controller events and service events written to JSON Lines bundles.

The local execution target was `local-process-fit-probe`. Docker, Kubernetes, Kind and Minikube were unavailable in the execution environment. The Kubernetes manifest is versioned under [`infrastructure/kubernetes/orderflow-fit-probe.yaml`](../../infrastructure/kubernetes/orderflow-fit-probe.yaml), but it was not executed and no Kubernetes result is claimed.

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

The local probe supports carrying the following provisional choices forward:

1. OrderFlow is sufficiently small and controllable for the next technical design stage.
2. Harness-controlled service and dependency faults are targetable, timestamped and reversible in the local slice.
3. A portable controller and structured telemetry contract can produce raw records without dashboard access.

The probe does not establish that Kubernetes is a suitable experimental target, that OpenTelemetry SDK/collector export is complete, or that any automation strategy improves reliability. It also does not compare OrderFlow with the adapted open-source benchmark alternative.

## Limitations and required follow-up

- Execute the same manifests against a pinned Kubernetes environment and record deployment, reset, targeting and rollback behaviour.
- Use `scripts/run-phase-2-kubernetes-fit-probe.ps1` after Docker Desktop Kubernetes is ready; its output must be reviewed and added as a separate Kubernetes evidence record rather than replacing these local results.
- Replace or augment the structured event exporter with the selected OpenTelemetry SDK/collector path and test export loss, ordering and correlation.
- Compare the local contract with Docker Compose only if Compose remains a candidate development path.
- Complete the Phase 1 literature searches and full-text charting before treating the Phase 2 decisions as final.
- Keep the raw records classified as synthetic technical-feasibility evidence; they are not reliability findings, participant data or human evidence.
