# Phase 2 fit-probe protocol

**Status:** Planned; do not run until the environment and scenario manifests are versioned.  
**Purpose:** Challenge the provisional Phase 2 system and technology choices.  
**Evidence type:** Technical feasibility only; no human-participant data.

## Objective

Determine whether the provisional OrderFlow/Kubernetes/OpenTelemetry/fault-boundary combination can be reset, exercised, observed and repeated with sufficient provenance for a later technical pilot.

## Required inputs

- versioned system and infrastructure manifests;
- a fixed synthetic workload;
- one no-fault manifest;
- one service-termination manifest;
- one dependency-latency or dependency-failure manifest;
- a clean-reset command;
- a health-readiness check; and
- a raw-event capture location outside protected source data directories.

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

## Exclusions

Do not recruit participants, collect participant data, use real payment data, use production systems or publish the fit-probe outputs as reliability findings.

