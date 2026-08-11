# Phase 6 participant task record schema

This schema describes the future participant-task record.

No actual participant records are authorised in Phase 6.

## Identity

- `study_participant_id`: pseudonymous study identifier
- `sequence_id`: counterbalance sequence
- `task_id`
- `scenario_family`
- `variant_id`
- `human_condition`

Direct identifiers are forbidden in this record.

## Context

- `task_started_at`
- `evidence_displayed_at`
- `decision_submitted_at`
- `interruption_status`
- `authority_profile`

## Decision evidence

- `submitted_diagnosis`
- `submitted_action`
- `recommendation_response`
- `retrospective_explanation`

## Derived scoring

Derived only against the frozen answer key:

- `diagnosis_accuracy`
- `recovery_decision_appropriate`
- `escalation_appropriateness`
- `decision_time_s`
- `recovery_task_success`
- `reliance_calibration`

## Workload

Retain each NASA-TLX dimension separately.

- `mental_demand`
- `physical_demand`
- `temporal_demand`
- `performance`
- `effort`
- `frustration`
- `raw_tlx_mean`

## Automation-assisted exploratory fields

Only applicable in H-A:

- `perceived_recommendation_correctness`
- `decision_confidence`
- `future_reliance_intention`

## Validity

- `task_record_valid`
- `timing_interpretable`
- `missing_reason`
- `researcher_note_code`

Free-text researcher notes must not contain participant direct identifiers.

## Public-repository boundary

This schema may be public.

Filled participant records may not be committed to the public repository.
