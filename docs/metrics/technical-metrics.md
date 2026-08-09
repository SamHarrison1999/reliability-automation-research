# Phase 3 technical metric catalogue

**Status:** Operationalised for the Phase 3 technical design; implementation and dry-run validation pending

**Primary unit:** Valid trial (`condition × scenario × repetition`)

**Time basis:** UTC event timestamps; durations reported in milliseconds unless stated otherwise

## Metric rules

Metrics are derived from raw event bundles, not dashboards or hand-edited summaries. Every derived observation must retain the source `run_id`, `scenario_id`, `automation_condition`, source event identifiers and the analysis-tool version.

No primary metric is imputed. If a required event boundary is missing, the metric is `missing` and the trial or metric-specific exclusion reason is recorded. A run may be retained for quality-control reporting while being excluded from a particular outcome.

The fault interval is half-open: `[injection_started, injection_ended)`. The recovery interval is `[recovery_started, recovery_completed]`. Requests are assigned using their recorded event timestamp, not their position in the JSON Lines file.

## Primary technical outcomes

| Metric ID | Construct | Operational definition | Source events | Aggregation |
|---|---|---|---|---|
| `detection_latency_ms` | Speed of fault recognition | `timestamp(fault_detected) − timestamp(injection_started)` | `injection_started`, `fault_detected` | Per valid fault trial; median and distribution by condition/scenario |
| `recovery_time_ms` | Time from fault injection to completed recovery | `timestamp(recovery_completed) − timestamp(injection_started)` | `injection_started`, `recovery_completed` | Per valid fault trial; median and distribution by condition/scenario |
| `failure_impact_rate` | Proportion of offered requests failing during the fault interval | `failed_requests_in_fault_interval / offered_requests_in_fault_interval` | `workload_request`, `workload_response`, injection boundaries | Per trial; report numerator and denominator with the rate |

`recovery_time_ms` is intentionally fault-relative. The separate active recovery duration below prevents the detection period from being hidden when comparing conditions.

## Secondary technical outcomes

| Metric ID | Operational definition | Purpose |
|---|---|---|
| `active_recovery_duration_ms` | `recovery_completed − recovery_started` | Separates recovery action time from detection latency |
| `time_to_first_post_recovery_success_ms` | First successful response after `recovery_completed` minus `injection_started` | Confirms usable service recovery, not only readiness |
| `failed_requests_count` | Count of responses classified as failure in the fault interval | Reports the numerator behind failure impact |
| `request_latency_p50_ms` | Median `latency_ms` for responses in a declared phase/window | Describes central request latency |
| `request_latency_p95_ms` | 95th percentile `latency_ms` for responses in a declared phase/window | Describes tail latency; report only when the window has the pre-specified minimum count |
| `latency_inflation_ratio` | Median fault-window latency divided by median no-fault/before-fault latency in the same trial block | Compares degradation while preserving units in the underlying metrics |
| `recovery_success` | `1` if readiness and the post-recovery success criterion both pass; otherwise `0` | Distinguishes completed command from restored service |
| `manual_intervention_count` | Count of externally initiated recovery/intervention events, excluding scheduled reset and workload commands | Measures intervention required by the technical condition; not human performance |
| `automation_decision_count` | Count of rule evaluations that produce a recovery decision | Detects duplicate or repeated automated actions |
| `rollback_duration_ms` | `rollback_completed − rollback_started` in the no-fault/version-transition control where present | Quality-control measure for deployment transitions |

## Measurement-quality outcomes

| Metric ID | Operational definition | Acceptance rule |
|---|---|---|
| `required_event_completeness` | Number of required event classes present divided by number required by the scenario/condition contract | Must be `1.0` for a valid trial |
| `timestamp_completeness` | Events with parseable UTC timestamps divided by all required events | Must be `1.0` for a valid trial |
| `trace_correlation_completeness` | Required service events with the expected correlation fields divided by required service events | Threshold is protocol-configured and reported, not silently discarded |
| `reset_duration_ms` | `reset_completed − reset_started` | Report as quality-control; missing reset boundaries invalidate the trial |
| `clean_state_verified` | Boolean from the reset contract and state fingerprint check | Must be `true` before workload starts and after cleanup |
| `contamination_detected` | Boolean indicating residual process/pod/fault/state after cleanup | Must be `false` before the next trial |
| `trial_valid` | Composite validity decision from event, reset, fault, recovery and provenance checks | Primary outcomes are interpreted only for valid trials |

## Event requirements

The Phase 3 contract adds or standardises these event fields:

- `trial_id`;
- `automation_condition` (`manual` or `automated`);
- `repetition` and `run_order`;
- `detection_rule_version`;
- `initiator` on recovery and intervention events;
- `fault_id` and `fault_phase` where applicable;
- `parent_event_id` or equivalent correlation for derived decisions; and
- `environment_manifest_sha256` and `scenario_manifest_sha256` in trial metadata.

Required events by fault trial are:

```text
trial_started
reset_started
clean_state_verified
reset_completed
workload_started
injection_started
fault_detected
recovery_started
recovery_completed
injection_ended
post_recovery_check
cleanup_completed
trial_completed
```

Workload request and response events are required wherever the workload is active. The exact ordering of `injection_ended` and `recovery_started` is scenario-defined; the derived analysis uses timestamps and the scenario contract rather than assuming file order.

## Missing-data and exclusion rules

1. Missing primary boundaries produce a missing metric; do not infer a timestamp from a neighbouring event.
2. Duplicate required boundary events invalidate the trial unless the protocol explicitly marks one as a retry and preserves both records.
3. A failed reset, unrecorded intervention or unverified cleanup invalidates the trial for comparison.
4. A workload request without a response is counted as an unresolved request only if the event contract records the request; it is not silently treated as success or failure.
5. Percentiles are not reported for windows below the pre-specified minimum of five completed responses.
6. Excluded trials remain in the raw dataset and in the exclusion ledger.
7. Technical metric values must not be re-labelled as human workload, trust, understanding or decision quality.

## Planned analysis summary

For the technical pilot, report per-cell counts, valid/excluded counts, medians, interquartile ranges, minimum/maximum where useful, and individual trial values. Display condition-by-scenario results rather than collapsing all fault classes into one number. The pilot is not powered for a confirmatory claim; any later inferential analysis requires a reviewed analysis plan after the Phase 1 evidence and technical data quality are assessed.

## Developer-practice boundary

Developer-practice constructs are specified separately in [`developer-practice-metrics.md`](developer-practice-metrics.md). They are not technical-trial metrics and must not be inferred from the records defined here.
