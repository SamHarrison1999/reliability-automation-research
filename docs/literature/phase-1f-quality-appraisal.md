# Phase 1F quality appraisal

**Project:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

**Execution date:** 2026-08-09

**Branch intended for:** `research/phase-1-literature-evidence`

**Stage:** Design-sensitive appraisal of charted full texts

## 1. Purpose

This stage appraises the 15 records assessed and charted in Phase 1E. It is a
separate appraisal stage and does not yet constitute the final literature
synthesis. The nine records still awaiting retrieval remain outside this
appraisal batch.

The appraisal is claim-scoped. It distinguishes technical feasibility and
descriptive operational evidence from causal evidence, direct human-practice
evidence, and secondary contextual evidence. It does not collapse
heterogeneous study designs into one numerical quality score.

## 2. Batch coverage

| Category | Count | Treatment |
|---|---:|---|
| Primary empirical/technical records appraised | 14 | Eligible for later synthesis with the recorded scope limits |
| Secondary multivocal review appraised | 1 | Context and citation chaining only |
| Retrieval-pending records | 9 | Not appraised; remain unresolved |
| Full-text exclusions in this stage | 0 | No new exclusion made |

The 15 appraised records are P04, P06, P09, P10, P12, P13, P14, P15, P16,
P17, P18, P19, P23, P26 and P27.

## 3. Main appraisal findings

### Technical evidence

The strongest usable contribution of this batch is descriptive technical and
operational evidence: fault injection, resilience testing, self-healing,
incident triage, root-cause analysis, query recommendation, incident
aggregation, fault profiling and resilience measurement. These sources can
inform mechanism, fault-model, system-context and metric selection.

The evidence is not a homogeneous causal body. Most technical studies use a
prototype, operational dataset, model evaluation or deployment report. The
common limitations are proprietary data, limited configuration disclosure,
single-organisation context, restricted scenarios and lack of controlled
comparisons against engineer or service-recovery outcomes.

### Human and practice evidence

P23 provides direct qualitative incident-response evidence through interviews
and public incident reports. P26 provides preliminary evidence about learning
from failure through reports and interviews. P27 provides an industrial case
study of controlled continuous deployment in a high-reliability embedded
telecommunications context. These sources are valuable for construct and
context selection, but they do not demonstrate an automation effect.

For the remaining technical records, engineers are generally operational users
or subjects of workflow records. That is not direct evidence of workload,
trust, situation awareness, understanding or decision quality. System
telemetry, model accuracy, incident counts, reassignment measures and
deployment reports must remain separate from human-factor measures.

### Secondary evidence

P09 is retained as a multivocal literature review for terminology, landscape
mapping and citation chaining. Its mixed academic and grey corpus means that
review-level counts or conclusions require method-level verification before
they are used as findings of this review.

## 4. Appraisal implications for the PhD study

The batch supports a focused design in which technical outcomes and
engineering-practice outcomes are measured separately. The later experiment
should not infer human benefit from system reliability telemetry alone. It
should define direct human or task-level measures for the relevant constructs,
alongside technical detection, diagnosis, containment, recovery and rollback
measures.

The literature also supports preserving explicit boundaries between:

- decision support and autonomous remediation;
- resilience testing and production recovery;
- incident aggregation or profiling and successful diagnosis;
- descriptive case evidence and causal comparison; and
- direct human-practice evidence and telemetry proxies.

## 5. Limitations of this appraisal batch

- The appraisal is based on the retained full-text chart and source routes;
  page-level quotations, extraction locations and detailed method fields still
  need to be added during synthesis preparation.
- Authenticated ACM Digital Library, IEEE Xplore, Scopus and Web of Science
  exports remain unavailable in the current repository workflow. No database
  totals are inferred.
- Nine eligible title-and-abstract records remain retrieval-pending.
- Appraisal was conducted by a single reviewer and has not received a second
  reviewer or supervisor check.
- The appraisal labels are claim-scoped and must not be interpreted as pooled
  effect estimates.

## 6. Files updated in this stage

- `quality-appraisal-guide-batch-05.md`
- `quality-appraisal-batch-05.csv`
- `phase-1f-quality-appraisal.md`
- `prisma-flow-batch-05.csv`

## 7. Stage outcome

Quality appraisal is complete for the currently charted full-text batch. Phase
1 remains open. The next work is to retrieve and appraise P01, P02, P03, P05,
P07, P11, P20, P22 and P24, then perform source-located synthesis, claim
checking, gap analysis and Phase 1 close-out.
