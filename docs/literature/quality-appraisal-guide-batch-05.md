# Phase 1F quality-appraisal supplement

**Project:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

**Review stage:** Design-sensitive quality appraisal

**Version:** 1.0

**Date:** 2026-08-09

This supplement applies the repository's prospective `quality-appraisal-guide.md`
to the 15 records with traceable full text in the Phase 1E chart. It does not
replace that guide and does not turn heterogeneous designs into a single
numerical quality score.

## Rating vocabulary

Each applicable domain uses the repository vocabulary:

- `low_concern` — adequately addressed for the claim being considered;
- `some_concern` — a limitation exists but does not make the evidence unusable;
- `high_concern` — the limitation substantially weakens the relevant inference;
- `insufficient_information` — the retained record does not permit judgement;
- `not_applicable` — the domain does not apply to the design.

The CSV also records a claim-scoped evidence interpretation. This is not a
league table or a pooled risk-of-bias score. A paper can have low concern for
its descriptive technical question and high concern for transfer to the
proposed system or for a human-outcome claim.

## Appraisal domains used in this batch

| Domain | Question |
|---|---|
| Design fit | Does the design answer the type of review claim being made? |
| Data/source adequacy | Are the data, cases, scenarios or participants appropriate and sufficiently described? |
| Analysis transparency | Are procedures, comparisons, coding, baselines or evaluation steps clear enough to interpret? |
| Measurement validity | Do the measures represent the stated technical or human construct? |
| Reproducibility | Are code, data, configurations, protocols or enough detail available for meaningful reproduction? |
| Transferability | Are context boundaries and likely limits of generalisation clear? |
| Human-evidence validity | Where human-practice claims are made, is there direct evidence rather than telemetry or user status alone? |

`not_applicable` is appropriate where a paper makes no human-participant
claim. It must not be read as evidence that a human construct was measured.
`insufficient_information` means that the record must not support a stronger
claim until the source location and method detail are checked.

## Human-measurement boundary

Engineers being described as users, incident counts, discussion counts,
reassignment rates, model accuracy, deployment reports, tool output and system
telemetry do not count as direct evidence of workload, trust, situation
awareness, understanding or decision quality unless the source explicitly
measured and analysed those constructs.

Direct interviews, observations and qualitative incident accounts are retained
as human-practice evidence. They are not treated as controlled automation
effects or as validated psychometric measures unless the source supports that
interpretation.

## Source-location rule

The repository guide requires each judgement to have a page, section, table or
figure reference. The current batch is explicitly marked
`chart_based_provisional` because the Phase 1E chart records the full-text
route and bounded finding but does not yet transcribe source locations for every
domain. The later synthesis-preparation pass must add those locators before
the appraisal is treated as final evidence for the proposal.

## Scope rules

1. Appraise the 15 charted records only.
2. Keep the nine retrieval-pending records outside the appraisal denominator.
3. Keep P09 as secondary context and citation chaining only.
4. Keep P23, P26 and P27 as descriptive practice/case evidence, not causal
   automation evidence.
5. Preserve uncertainty and limitations in every later claim.
6. Do not enter final synthesis claims during this stage.
