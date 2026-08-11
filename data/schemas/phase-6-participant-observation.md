# Phase 6 participant observation schema

**Status:** Schema only; participant data collection is not authorised

## Participant pseudonym

`study_participant_id`

The value must not encode:

- name;
- email address;
- employee identifier;
- date of birth; or
- other direct identifier.

## Session fields

- `sequence_id`
- `session_started_at`
- `session_completed_at`
- `eligibility_confirmed`
- `consent_record_reference`

The consent record itself is stored separately.

## Task observations

Each task contains:

- task identity;
- condition;
- scenario family;
- authority profile;
- timestamps;
- submitted diagnosis;
- submitted action;
- recommendation response where applicable;
- workload dimensions;
- exploratory ratings where applicable;
- typed retrospective explanation;
- validity/missingness information; and
- derived rubric values.

## Post-study observations

- four automation-understanding items;
- broad professional-experience categories;
- protocol-feedback fields.

## Forbidden fields

The observation dataset must not contain:

- participant name;
- email;
- postal address;
- telephone number;
- employer name;
- customer/client name;
- exact date of birth;
- IP address retained for research analysis;
- credentials/secrets; or
- special-category information not explicitly approved.

## Provenance

Future datasets require:

- protocol version;
- task-manifest hash;
- study-interface version;
- scoring-rubric version;
- analysis-plan version; and
- ethics approval/reference metadata held at project level.

## Public repository

Filled participant observations are prohibited from the public Git repository.

Only synthetic fixtures may instantiate this schema publicly.
