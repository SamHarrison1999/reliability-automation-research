# Metric observation record

Phase 3 derived metrics must be stored as records that retain their provenance. A metric record is not a replacement for the raw JSON Lines event bundle.

## Required fields

| Field | Meaning |
|---|---|
| `metric_id` | Stable identifier from `docs/metrics/technical-metrics.md` |
| `metric_version` | Version of the operational definition |
| `trial_id` | Trial that produced the observation |
| `run_id` | Runtime event-bundle identifier |
| `scenario_id` | Versioned fault/control scenario |
| `automation_condition` | `manual` or `automated`, where applicable |
| `repetition` | Planned repetition number |
| `value` | Numeric value, boolean value or `null` when missing |
| `unit` | `ms`, `ratio`, `count`, `boolean` or `proportion` |
| `status` | `observed`, `missing`, `excluded` or `quality-control` |
| `source_event_ids` | Event identifiers used in the derivation |
| `missing_reason` | Required when `value` is `null` |
| `analysis_version` | Version of the derivation implementation |
| `created_at` | UTC creation timestamp |

## Rules

- Keep one record per metric and trial.
- Preserve `null` for missing primary outcomes; do not substitute zero.
- Preserve excluded trials and their reasons.
- Store the raw bundle path or immutable object identifier in the surrounding analysis manifest.
- Never add participant identifiers, real payment data or production traffic to this record.
