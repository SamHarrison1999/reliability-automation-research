# Phase 6 scoring rubrics

## Diagnosis

`diagnosis_accuracy = 1`

only when the submitted diagnosis matches the task manifest's
`diagnosis_key`.

Otherwise:

`diagnosis_accuracy = 0`

No partial diagnosis credit is used in the feasibility study.

## Recovery decision

`recovery_decision_appropriate = 1`

only when the final submitted action matches the manifest's
`appropriate_action`.

Otherwise the value is 0.

## Escalation appropriateness

If escalation is expected:

- selected escalation -> `appropriate`;
- direct action selected -> `missed_escalation`.

If escalation is not expected:

- direct appropriate action -> `not_required`;
- escalation -> `inappropriate_escalation`.

## Reliance calibration

For H-A only.

If the automation recommendation is correct:

- accept -> `appropriate_acceptance`;
- override/escalate without task justification -> `inappropriate_rejection`.

If the automation recommendation is incorrect because authority requires
escalation:

- escalate -> `appropriate_escalation`;
- accept -> `inappropriate_acceptance`;
- override to another unauthorised direct action -> `inappropriate_acceptance`.

A future scenario with an incorrect recommendation but a different authorised
recovery action may use `appropriate_override`.

## Explanation quality feasibility rubric

### Evidence use

- 0: no relevant evidence;
- 1: mentions relevant evidence without linking it clearly to the decision;
- 2: identifies the decisive evidence and uses it appropriately.

### Causal reasoning

- 0: no causal account or contradicts the evidence;
- 1: plausible but incomplete causal account;
- 2: coherent diagnosis-to-action explanation.

### Uncertainty/authority

- 0: ignores material uncertainty or role authority;
- 1: acknowledges uncertainty/authority without integrating it;
- 2: explicitly incorporates uncertainty or authority into the decision.

Maximum exploratory score: 6.

The score is not a primary outcome.

## Automation understanding answer domains

The four comprehension items must establish that the participant understands:

1. recommendation trigger/evidence boundary;
2. recommendation fallibility;
3. participant decision responsibility; and
4. restricted action authority.

Each item is binary.

Maximum score: 4.
