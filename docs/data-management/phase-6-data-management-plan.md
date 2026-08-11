# Phase 6 draft Data Management Plan

**Status:** Application-preparation DMP; must be reconciled with the current
institutional DMP template before participant collection

## Project

Reliability Automation and Software Engineering Practice.

## Data lifecycle

The future human study may generate:

1. recruitment/contact data;
2. consent records;
3. eligibility screening data;
4. pseudonymised participant-task records;
5. questionnaire/workload responses;
6. typed retrospective explanations;
7. protocol/technical provenance;
8. derived scoring; and
9. anonymised aggregate outputs.

Phase 6 itself collects no participant data.

## Data minimisation

The study does not require:

- exact date of birth;
- employer/customer names;
- home address;
- health data;
- ethnicity;
- religion;
- politics;
- sexual orientation;
- biometric data;
- audio;
- video; or
- screen recordings.

Participants are instructed not to place confidential professional information
or personal identifiers in free text.

## Identifiers

The research dataset uses a random study participant ID.

Recruitment/contact details and the participant-ID mapping are held separately.

The mapping is used only for operational administration and withdrawal during
the approved withdrawal window.

## Storage during research

Once the project is institutionally authorised, personal/pseudonymised data
must be stored only in storage approved for the corresponding data
classification by the Open University/relevant host institution.

The public GitHub repository is not approved participant-data storage.

Local downloads should be avoided unless the approved security plan expressly
allows them.

## Version control

Public Git may contain:

- blank forms;
- protocol text;
- schemas;
- synthetic task definitions;
- synthetic fixtures;
- analysis code;
- non-identifying provenance; and
- appropriately anonymised/aggregate outputs.

It must not contain:

- recruitment contact lists;
- signed/electronic consent records;
- participant-ID mapping;
- filled participant questionnaires;
- participant-level task logs; or
- pseudonymised participant records.

## Retention

Current OU guidance generally expects most retained research data and related
records to be stored for a minimum of ten years.

The exact retention schedule must be re-verified and approved when the formal
DMP is submitted.

Operational recruitment/contact data and the participant identity link should
be deleted when they are no longer required for consent, payment, withdrawal
or governance, subject to the approved institutional retention schedule.

## Withdrawal/anonymisation boundary

The planned participant withdrawal period is 14 calendar days following the
session.

The identity link must remain available through the approved withdrawal window.

After the withdrawal window and required administrative checks, the project may
destroy the identity link when consistent with the approved DMP.

After irreversible anonymisation, individual withdrawal may no longer be
possible.

## Backup

Approved institutional storage must provide the backup/recovery controls
required by the University's information-security policy.

The public Git repository is not a participant-data backup.

## Sharing

The preference is to share:

- protocols;
- schemas;
- software;
- synthetic data; and
- aggregate/anonymised outputs.

Participant-level data will be shared only if:

1. consent covers the proposed sharing;
2. disclosure risk is acceptably low;
3. ethics/data-protection approval permits it; and
4. the approved repository/access control is appropriate.

Where participant data cannot be openly shared, metadata and a justified access
statement may be published instead.

## DMP institutional gate

Current OU policy requires a DMP before research data collection and provides
ORDO for research-data-management planning/archiving.

The formal DMP must be reviewed/uploaded through the process applicable when
the researcher is registered and before collection starts.

This repository document is preparation for that process rather than evidence
that the institutional DMP requirement has already been satisfied.
