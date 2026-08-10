# Phase 5 primary batch freeze and execution procedure

**Status:** Pre-data implementation; generate the batch only after the tooling
commit passes the full quality gate.

The primary pilot has two distinct ordering identities:

- `primary_schedule_slot`: fixed 1–50 position in the pre-generated primary
  schedule;
- `run_order`: actual attempt sequence including activated reserves.

With no invalid attempts these values are identical. A reserve increases the
actual run order of subsequent attempts without changing the frozen 50-slot
primary schedule.

The primary executor does not accept scenario, condition or slot parameters.
`--plan-next` is read-only. `--execute-next --confirm-frozen-primary` executes
only the state-machine-derived next attempt.

Invalid primary evidence is never deleted. Reserve 1 for the same cell becomes
the only permissible next action. If reserve 1 is invalid, reserve 2 becomes the
only permissible next action. Two invalid reserves in one cell pause the pilot.

A valid reserve supplies the valid observation for the same planned cell
repetition. The schedule then resumes at the next primary slot.

The batch freeze is invalid if any primary evidence already exists. The batch
manifest and primary run-order are deterministic and timestamp-free.
