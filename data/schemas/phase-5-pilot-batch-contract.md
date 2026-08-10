# Phase 5 pilot and batch contract

**Schema version:** `1.0.0`

**Status:** Locked for Slice 2 implementation

**Protocol:** `phase-5-technical-pilot-v1`

**Design manifest:** `../../experiments/manifests/phase-5-pilot-manifest.json`

## Purpose

This contract separates three immutable identities:

1. **pilot design manifest** - committed source defining permitted cells,
   treatment invariants, allocation and run-order constraints;
2. **primary run-order file** - deterministic 50-slot allocation derived only
   from the design manifest and fixed seed; and
3. **batch manifest** - created immediately before pilot execution and binding
   the committed design/run order to source, deployment, images and environment.

No file in this contract is itself a trial result.

## Pilot-manifest invariants

The committed Phase 5 pilot manifest must declare exactly five cells:

| Cell | Scenario | Condition | Primary valid target | Reserve |
|---|---|---|---:|---:|
| `no-fault-control` | `no-fault-v1` | `control` | 10 | 2 |
| `service-termination-manual` | `service-termination-v1` | `manual` | 10 | 2 |
| `service-termination-automated` | `service-termination-v1` | `automated` | 10 | 2 |
| `dependency-latency-manual` | `dependency-latency-v1` | `manual` | 10 | 2 |
| `dependency-latency-automated` | `dependency-latency-v1` | `automated` | 10 | 2 |

The design therefore permits 50 primary valid observations and at most 10
logged reserve attempts.

For both fault scenarios the manifest must declare one canonical recovery action
at scenario level. Conditions may select the initiator/executor but may not
supply different recovery commands.

## Primary run-order contract

The generated run-order object contains:

- `run_order_version`;
- `generator_version`;
- `protocol_id`;
- `manifest_version`;
- `pilot_manifest_sha256`;
- `seed`;
- `primary_slot_count`;
- a machine-readable `balance_summary`; and
- `slots`.

It deliberately contains **no timestamp, hostname, Git SHA or environment
metadata**. Those values would make allocation bytes vary without changing the
experimental design.

The same manifest bytes and seed must therefore produce byte-identical canonical
run-order JSON on every supported platform.

### Slot fields

Every primary slot contains:

- `schedule_slot` - 1..50;
- `cycle` - execution cycle 1..10;
- `cycle_position` - 1..5;
- `design_cycle_id` - constrained cycle used before deterministic seed ordering;
- `cell_id`;
- `scenario_id`;
- `automation_condition`;
- `repetition` - 1..10 within the cell;
- `reserve` - always `false` for the primary schedule.

Reserve attempts are not silently pre-populated as ordinary primary slots.

## Counterbalancing requirements

Across the ten cycles:

1. each cycle contains all five cells exactly once;
2. service termination is the first fault scenario in five cycles;
3. dependency latency is the first fault scenario in five cycles;
4. manual is first within the service-termination pair in five cycles;
5. automated is first in the other five;
6. manual is first within the dependency-latency pair in five cycles;
7. automated is first in the other five; and
8. the no-fault control occupies each cycle position 1..5 exactly twice.

The fixed seed deterministically orders the ten already-balanced design cycles
by SHA-256 ranking. The algorithm does not depend on Python's pseudo-random
implementation.

## Immutable-write rule

When asked to write a primary run-order file:

- create it if absent;
- if it already exists with byte-identical canonical JSON, leave it unchanged;
- if it exists with any different bytes, stop with an error.

No overwrite flag is permitted.

## Batch-manifest contract

Slice 3/5 will materialise a batch manifest before primary execution. At
minimum it must bind:

- `batch_id`;
- protocol and pilot-manifest versions;
- repository commit SHA;
- pilot-manifest SHA-256;
- primary run-order SHA-256;
- protocol SHA-256;
- Phase 5 Kubernetes-manifest SHA-256;
- Phase 4 prototype-manifest SHA-256;
- application image identities;
- OpenTelemetry Collector identity;
- OTel dependency-lock SHA-256;
- controller and metric-derivation versions;
- Kubernetes/Docker/tool versions;
- target context; and
- batch start UTC timestamp.

The batch manifest becomes immutable when primary trial 1 starts.

## Reserve activation record

A reserve attempt requires:

- same `cell_id` as the invalid source attempt;
- `reserve=true`;
- next reserve index for the cell;
- invalid source `trial_id`;
- pre-specified exclusion code;
- activation timestamp; and
- batch/run-order identities.

Reserve activation cannot modify the 50-slot primary run-order file.

## Evidence boundary

The manifest and run-order generator are experimental-design infrastructure.
Generating or testing them does not start the Phase 5 technical pilot and does
not create empirical evidence.
