# Phase 3 trial-manifest contract

**Schema version:** `1.0.0`

**Status:** Design locked for implementation

The machine-readable design manifest is [`../../experiments/manifests/phase-3-trial-manifest.json`](../../experiments/manifests/phase-3-trial-manifest.json). It defines the permitted cells, workload, fault parameters, detection rules, recovery actions, replication target, event contract, validity rules and analysis outputs.

## Manifest roles

The committed manifest is a design manifest. It is not an execution result and must not be edited after a trial starts. Each executed trial receives an immutable trial manifest containing the design values plus execution values:

- `trial_id`;
- `repetition` and `run_order`;
- `execution_context`;
- repository commit SHA;
- scenario and environment manifest hashes;
- tool and service versions; and
- UTC trial-start timestamp.

The concrete run-order file is generated from the design manifest before execution and retained with the raw results. Trial outcomes must not change the generated order.

## Required invariants

1. The no-fault scenario is a quality-control block, not a recovery-condition comparison.
2. The two fault scenarios are crossed with exactly `manual` and `automated` recovery conditions.
3. The fault, workload, detection rule, versions, environment and reset contract remain constant within a comparison block.
4. Manual and automated conditions invoke the same scenario-specific recovery action; only the initiator changes.
5. The detection rule is versioned and declared before execution.
6. A trial is invalid when reset, event completeness, fault application/reversion, recovery attribution, cleanup or provenance checks fail.
7. Missing primary metric boundaries remain missing; they are never inferred or replaced with zero.

## Planned allocation

| Block | Conditions | Valid repetitions | Reserve | Purpose |
|---|---|---:|---:|---|
| `no-fault-v1` | control | 10 | 2 | Reset, workload, deployment-transition and telemetry quality control |
| `service-termination-v1` | manual, automated | 10 each | 2 each | Availability-failure comparison |
| `dependency-latency-v1` | manual, automated | 10 each | 2 each | Performance-degradation comparison |

The target is 50 valid trials and up to 10 reserve slots. These are feasibility/pilot planning targets, not a power calculation.

## Execution record requirements

Every event must carry the identity fields in the manifest event contract. Recovery events must identify the initiator and recovery-action version. Automated evaluations must preserve the detection-rule version, observed signal, decision and parent event. The raw event bundle, metadata, manifest, validity decision and exclusion reason are retained together.

## Developer-practice boundary

This contract governs technical trials only. It does not collect or infer developer-practice constructs such as workload, trust, understanding, diagnosis rationale or escalation reasoning. Those measures are specified separately for a future human-participant protocol and require ethics approval before collection.
