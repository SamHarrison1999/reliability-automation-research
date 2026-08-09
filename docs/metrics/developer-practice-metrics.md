# Developer-practice metric specification

**Status:** Provisional design for a later human-participant protocol

**Collection status:** Not collected in Phase 3; ethics approval and a separate participant protocol are required

Technical telemetry can describe system and controller events, but it cannot establish why an engineer acted, what they understood, how much workload they experienced or whether they trusted an automation. The following constructs are therefore specified as a separate measurement stream rather than added to the technical trial metrics.

## Provisional constructs and operationalisations

| Metric ID | Construct | Operational definition | Required source | Phase 3 status |
|---|---|---|---|---|
| `diagnosis_accuracy` | Correct identification of the active fault | Categorical score against a pre-specified scenario answer key; report correct/incorrect and permitted partial-credit rubric | Participant task response plus scenario ground truth | Not collected |
| `diagnosis_time_s` | Time to reach a recorded diagnosis | `diagnosis_submitted_at − fault_notice_at`; pauses and timeout handling must be specified before data collection | Instrumented task timestamps | Not collected |
| `recovery_task_success` | Effective completion of the recovery task | Binary outcome based on service recovery and task-specific success criteria, separate from the technical trial's recovery event | Task outcome plus system event validation | Not collected |
| `recovery_time_s` | Time taken by a participant to complete recovery | `recovery_completed_at − fault_notice_at`; report alongside, not as a substitute for, technical recovery time | Instrumented task timestamps | Not collected |
| `escalation_appropriateness` | Whether escalation matches the scenario rubric | Pre-specified independent rubric: appropriate, premature, delayed or absent; adjudication procedure required | Participant action log and coded response | Not collected |
| `unsafe_action_count` | Actions that violate the task safety rules | Count of pre-defined unsafe commands or changes, with each action retained for audit | Instrumented command/action log | Not collected |
| `explanation_quality` | Quality of diagnosis/recovery rationale | Blinded rubric scored against evidence use, causal explanation and uncertainty acknowledgement; inter-rater agreement required | Post-task explanation, coded by independent raters | Not collected |
| `perceived_workload` | Subjective task workload | Score from a validated instrument selected in the ethics-approved protocol; instrument, scoring and language must be frozen before recruitment | Participant questionnaire | Not collected |
| `trust_calibration` | Whether reliance is proportionate to observed automation behaviour | Pre-specified questionnaire and behavioural reliance indicators, analysed separately rather than inferred from a telemetry event | Participant questionnaire plus action log | Not collected |
| `automation_understanding` | Understanding of what the automation does and does not do | Scenario-specific comprehension questions scored against an answer key | Post-task questionnaire | Not collected |

## Separation rules

- Do not append these constructs to `data/schemas/metric-observation-record.md` for Phase 3 technical runs.
- Do not label `manual_intervention_count`, `recovery_time_ms` or `automation_decision_count` as human workload, trust, understanding or decision quality.
- The technical trial may provide system ground truth for a later participant task, but participant actions and explanations require their own consent, identifiers/pseudonyms, retention rules and ethics-approved protocol.
- The final instrument, scoring rubrics, participant sample and analysis model remain open until the literature review is updated and the human-participant protocol is reviewed.
