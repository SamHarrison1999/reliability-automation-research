# Phase 2 fit-probe protocol

**Status:** Executed locally on 2026-08-08; local checks passed, selected Kubernetes and OpenTelemetry runtime paths remain untested.
**Purpose:** Challenge the provisional Phase 2 system and technology choices.
**Evidence type:** Technical feasibility only; no human-participant data.

## Objective

Determine whether the provisional OrderFlow/Kubernetes/OpenTelemetry/fault-boundary combination can be reset, exercised, observed and repeated with sufficient provenance for a later technical pilot.

## Required inputs

- versioned system and infrastructure manifests (`infrastructure/local-fit-probe.json` and `infrastructure/kubernetes/orderflow-fit-probe.yaml`);
- a fixed synthetic workload implemented by `experiments/harness/fit_probe.py`;
- `experiments/scenarios/no-fault.json`;
- `experiments/scenarios/service-termination.json`;
- `experiments/scenarios/dependency-latency.json`;
- the versioned clean-reset procedure in the controller;
- service health-readiness checks; and
- `results/fit-probe/raw/` as the raw-event capture location outside protected source-data directories.

## Procedure

1. Record repository commit, image digests, runtime versions and host/runner information.
2. Reset the environment and verify readiness.
3. Run the no-fault workload and capture all expected event classes.
4. Reset the environment.
5. Run the service-termination scenario and capture injection, observed failure, automation, recovery and cleanup events.
6. Reset the environment.
7. Run the dependency-latency or dependency-failure scenario.
8. Repeat one scenario from a clean reset.
9. Compare event completeness, timestamps, state and contamination indicators.
10. Record failures and limitations; do not estimate an automation effect.

## Minimum acceptance checks

- Every run has a unique run identifier and a versioned manifest.
- The scenario is distinguishable from ordinary workload failure.
- Injection and cleanup have explicit start/end records.
- The target service can be identified without relying on dashboard screenshots.
- The next run starts from the documented clean state.
- Raw records can be copied and inspected without access to a live cluster.

## Execution record

The executed local probe and its limitations are recorded in [`docs/fit-probe/phase-2-fit-probe-results.md`](../fit-probe/phase-2-fit-probe-results.md). It completed one no-fault run, one service-termination run, one dependency-latency run and one clean-reset repeat. The no-fault run included a version update and rollback.

The probe environment did not contain `docker`, `kubectl`, `kind` or `minikube`. Therefore the execution target was a local-process surrogate, not Kubernetes. Service events used an OpenTelemetry-compatible structured field contract, but no OpenTelemetry SDK or collector was executed.

## Exclusions

Do not recruit participants, collect participant data, use real payment data, use production systems or publish the fit-probe outputs as reliability findings.
