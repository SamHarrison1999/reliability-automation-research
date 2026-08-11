# Phase 6 human-participant measures

**Status:** Frozen for Phase 6 protocol design

**Evidence class:** Future human-participant evidence only

## Primary measures

| ID | Construct | Unit | Operationalisation |
|---|---|---|---|
| `diagnosis_accuracy` | Fault diagnosis | binary | 1 when submitted diagnosis matches the frozen task key; otherwise 0 |
| `recovery_decision_appropriate` | Recovery decision | binary | 1 when the selected recovery/escalation decision matches the frozen task key |
| `escalation_appropriateness` | Escalation decision | categorical | `appropriate`, `not_required`, `inappropriate_escalation`, or `missed_escalation` |

No technical telemetry metric is substituted for these outcomes.

## Secondary behavioural measures

### `decision_time_s`

Elapsed time between the task evidence becoming available and submission of the
participant's final diagnosis/action decision.

Breaks are scheduled between tasks.

If an unscheduled interruption occurs during a timed task, the decision
response may be retained but timing is marked `not_interpretable`.

### `recovery_task_success`

Whether the submitted action produces the task-defined successful outcome in
the controlled simulation.

### `recommendation_response`

Automation-assisted tasks classify the participant response as:

- `accept`;
- `override`; or
- `escalate`.

### `reliance_calibration`

Derived from recommendation correctness, authority constraints and the final
participant decision.

Allowed categories are:

- `appropriate_acceptance`;
- `appropriate_override`;
- `appropriate_escalation`;
- `inappropriate_acceptance`;
- `inappropriate_rejection`; or
- `not_applicable`.

This is behavioural calibration, not a general psychological trust score.

## Workload

Six NASA-TLX dimensions are collected after every task:

- Mental Demand;
- Physical Demand;
- Temporal Demand;
- Performance;
- Effort;
- Frustration.

Each dimension is retained separately.

For feasibility analysis only:

`raw_tlx_mean = arithmetic mean of the six dimension ratings`

The result must be labelled raw/unweighted and must not be described as the
original weighted NASA-TLX score.

## Exploratory recommendation ratings

Automation-assisted tasks may collect separate 0-100 ratings for:

- perceived recommendation correctness;
- confidence in the participant's final decision; and
- willingness to use the same recommendation mechanism in another comparable
  incident.

Each rating is reported separately.

No combined trust scale is calculated.

## Automation understanding

Four post-study comprehension items are scored binary.

`automation_understanding_score` is the sum from 0 through 4.

The answer key is frozen before participant execution.

## Explanation quality

Typed retrospective explanations may be coded on three dimensions:

1. evidence use;
2. causal reasoning; and
3. acknowledgement of uncertainty/authority.

Each dimension uses a 0-2 rubric.

The feasibility study primarily tests rubric operation. Comparative claims from
the explanation score require the declared coding/reliability procedure.

## Missing data

Missing questionnaire or task values are never silently imputed.

Each missing value receives a reason such as:

- `participant_skipped`;
- `technical_failure`;
- `task_interrupted`;
- `withdrawn`;
- `not_applicable`; or
- `other_recorded_reason`.

## Separation from Phase 5

Phase 5 `recovery_time_ms`, `manual_intervention_count` and
`automation_decision_count` remain technical measures.

They are not participant workload, participant decision time or reliance
measures and must never be pooled with this measurement stream.
