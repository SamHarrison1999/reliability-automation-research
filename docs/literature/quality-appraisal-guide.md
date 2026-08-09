# Design-sensitive quality-appraisal guide

**Protocol:** `phase-1-review-protocol.md` v1.0
**Status:** Prospective appraisal rules; no study has been appraised under this version

## Purpose

Critical appraisal determines how confidently an included study can contribute
to a claim. It does not convert heterogeneous designs into a league table and is
not an automatic inclusion threshold.

Use one judgement per applicable domain:

- `low_concern` — adequately addressed for the claim being considered;
- `some_concern` — a limitation exists but does not make the evidence unusable;
- `high_concern` — the limitation substantially weakens the relevant inference;
- `insufficient_information` — reporting or access does not permit judgement;
- `not_applicable` — domain does not apply to the design.

Every judgement needs a page, section, table or figure reference and a concise
rationale.

## Common domains for all empirical studies

1. Clear aim and fit between question and method.
2. Context, system/domain and unit of analysis described.
3. Data provenance and collection procedure traceable.
4. Outcome/construct definitions valid for the claim.
5. Analysis method appropriate and reported.
6. Missing data, exclusions and negative results addressed.
7. Findings supported by presented evidence.
8. Limitations and conflicts/funding reported.
9. Reproducibility information sufficient for independent understanding or
   replication, where applicable.

## Controlled technical experiments and tool evaluations

Assess:

- intervention and comparator are explicit;
- fault, workload, environment, versions and reset are controlled;
- run order, repetitions and unit of analysis are justified;
- detection/recovery/service-impact boundaries are operationalised;
- concurrent changes and contamination are prevented or measured;
- statistical summaries reflect dependence and variability;
- failed/invalid runs and missing telemetry are visible; and
- artefacts/configuration/raw or derived data are available or sufficiently
  described.

A benchmark experiment may have low internal-validity concern and high
transferability concern at the same time. Record both.

## Observational, field and operational-data studies

Assess:

- system/organisation and observation period are clear;
- incident, deployment or event inclusion rules are defined;
- data completeness, censoring and instrumentation changes are addressed;
- confounding and selection mechanisms are considered;
- temporal ordering supports the claimed relationship;
- model validation avoids leakage and inappropriate baselines; and
- transferability beyond the observed organisation/system is bounded.

Operational correlations do not establish that automation caused an outcome.

## Qualitative studies

Assess:

- sampling strategy and participant roles fit the question;
- recruitment and context are transparent;
- data-collection method and researcher role are described;
- analysis is systematic and traceable;
- reflexivity and contradictory cases are addressed;
- quotations/observations support interpretations; and
- ethics/consent and confidentiality are reported where applicable.

Participant opinion about reliability is not itself a technical reliability
measure; it can validly evidence experience, perception or practice.

## Mixed-methods studies

Appraise each component under its own domains, then assess:

- why methods were combined;
- whether sampling and timing support integration;
- how findings were integrated rather than merely placed side by side; and
- whether contradictions between components were examined.

## Experience reports

Assess:

- organisation, system and time period are identifiable;
- the report distinguishes observation from recommendation;
- data supporting claimed effects are presented;
- implementation and outcome selection are transparent; and
- author/vendor interests and transferability are discussed.

An experience report without assessable data may remain useful context but
cannot support a strong empirical effect claim.

## Secondary reviews and evidence maps

Assess:

- protocol/question and eligibility criteria are explicit;
- databases, dates and complete search strategies are reported;
- screening and extraction procedures are reproducible;
- primary and non-primary evidence are distinguished;
- quality appraisal is appropriate to the review purpose;
- synthesis does not exceed the included evidence; and
- included-study list and limitations are available.

Secondary reviews support landscape interpretation and citation chasing. Their
summary claims should not be double-counted alongside the same primary studies.

## Overall claim-level use

Do not assign a single numeric score across designs. For each claim, summarise:

- contributing sources and designs;
- directness to the review question;
- consistency or contradiction;
- main appraisal concerns;
- whether the evidence is causal, associational, descriptive or conceptual; and
- the strongest wording the evidence permits.
