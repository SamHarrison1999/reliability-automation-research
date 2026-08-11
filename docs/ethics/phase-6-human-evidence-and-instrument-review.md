# Phase 6 human-evidence and instrument review

**Status:** Accepted Phase 6 measurement basis

**Date:** 2026-08-12

## Purpose

Select a bounded set of human measures for RQ2 without treating system
telemetry as evidence of workload, trust, understanding or decision rationale.

RQ2 is:

> How do different reliability-automation strategies influence software
> engineers' diagnosis, recovery and escalation decisions during structured
> continuous-delivery tasks?

The primary evidence must therefore come from participant decisions and task
responses.

## Measurement hierarchy

The study prioritises directly observable task decisions over subjective
constructs.

### Primary outcomes

1. diagnosis accuracy;
2. recovery-decision appropriateness; and
3. escalation appropriateness.

These are task-specific and scored against answer keys frozen before
participant collection.

### Secondary outcomes

- task decision time;
- recovery-task success;
- perceived workload;
- automation understanding;
- behavioural reliance calibration;
- exploratory self-reported reliance/confidence; and
- retrospective explanation quality.

## Workload instrument decision

The study will use the six NASA Task Load Index dimensions:

- Mental Demand;
- Physical Demand;
- Temporal Demand;
- Performance;
- Effort; and
- Frustration.

For the Phase 7 feasibility study the dimensions will be collected after each
task using the declared 0-100 response scale.

The feasibility analysis will retain all six dimension scores and calculate an
unweighted arithmetic mean, labelled `raw_tlx_mean`.

This is explicitly an unweighted/raw operationalisation. It must not be
described as the original weighted NASA-TLX procedure.

NASA currently makes TLX available for use without requiring permission. The
official instructions must be reviewed again before the approved study is
implemented.

## Trust and reliance decision

A broad questionnaire score called "trust" is not a primary outcome.

The central trust-related construct is behavioural reliance calibration:

- accepting a correct recommendation;
- overriding an incorrect recommendation;
- escalating when the recommendation conflicts with authority or evidence;
- accepting an incorrect recommendation; or
- rejecting a correct recommendation.

The first three behaviours are potentially calibrated responses. The last two
are potentially miscalibrated responses, subject to the pre-specified task
answer key.

Task-specific exploratory ratings may ask:

- perceived likelihood that the recommendation was correct;
- confidence in the participant's final decision; and
- willingness to use the same recommendation mechanism on another comparable
  task.

These are custom exploratory ratings, not a validated general trust scale.

No aggregate "trust score" will be created from them.

## Automation-understanding measure

Post-study comprehension questions will assess whether the participant
understands:

1. what evidence triggers the recommendation;
2. that a recommendation is not guaranteed to be correct;
3. that the participant remains responsible for accepting, overriding or
   escalating; and
4. that the recommendation mechanism does not have unrestricted authority.

Each item is scored correct or incorrect against a frozen answer key.

## Expertise/context measures

The pre-task questionnaire may collect:

- years of professional software/operations experience;
- current or recent broad role category;
- frequency of production-incident involvement;
- familiarity with CI/CD;
- familiarity with service observability;
- familiarity with Kubernetes/cloud-native systems; and
- prior experience with automated remediation.

Exact employer, customer, project and production-system names must not be
requested.

No special-category demographic information is required to answer RQ2.

## Explanation method

After each task the participant provides a short typed explanation of why they
selected the diagnosis and recovery/escalation decision.

The feasibility study uses explanations primarily to test whether the rubric is
usable.

If explanation-quality scores are later used as comparative outcomes, the
protocol must provide appropriate independent coding and agreement procedures.

## Instrument selection boundary

Instrument selection is frozen for the feasibility protocol as:

- direct task-specific decision measures for the primary outcomes;
- NASA-TLX dimensions with declared raw/unweighted feasibility scoring;
- behavioural reliance calibration;
- custom exploratory recommendation/confidence ratings;
- bespoke automation-comprehension questions; and
- short retrospective typed explanations.

No additional psychometric scale may be added after participant collection
begins without an approved protocol amendment.

## Sources informing this decision

- Open University Human Research Ethics guidance and applicant checklist;
- NASA official Task Load Index guidance;
- Hart and Staveland's NASA-TLX work;
- Jian, Bisantz and Drury (2000), *Foundations for an Empirically Determined
  Scale of Trust in Automated Systems*;
- current human-automation measurement literature.

The repository records the design decision rather than reproducing
copyright-restricted questionnaire items from third-party publications.
