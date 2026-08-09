# Phase 1E full-text assessment and evidence charting

**Project:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments
**Execution date:** 2026-08-09
**Branch:** `research/phase-1-literature-evidence`
**Stage:** Full-text eligibility and first structured evidence chart

## 1. Purpose

This batch advances the 24 records retained after title-and-abstract
screening. It separates records with traceable full-text evidence from records
that still require retrieval. It does not claim that the literature review is
complete: authenticated database searching, the remaining retrieval work,
quality appraisal and synthesis are still outstanding.

The extraction follows `full-text-charting-guide.md`. Where a paper does not
report a field, the chart uses `not_reported` or a bounded description rather
than inference. System telemetry, model deployment and operational records are
not treated as direct measures of workload, trust, understanding or decision
quality unless the source measured those constructs directly.

## 2. Full-text disposition

The batch assessed 15 records with a traceable publisher, repository or author
manuscript route:

- Primary empirical inclusions: P04, P06, P10, P12, P13, P14, P15,
  P16, P17, P18, P19, P23, P26 and P27.
- Secondary contextual inclusion: P09.
- Awaiting retrieval: P01, P02, P03, P05, P07, P11, P20, P22 and P24.
- Full-text exclusions in this batch: none.

The explicit correction in the list above is intentional: P11 has not been
upgraded from abstract-level status merely because a publisher record exists.

## 3. Eligibility decisions

The assessed primary studies provide an empirical basis through controlled
experiments, operational datasets, tool evaluations, case studies or
qualitative incident analysis. They cover fault injection, resilience
profiling, self-healing, incident triage, incident aggregation, root-cause
analysis, query recommendation, postmortem profiling, incident response and
controlled continuous deployment.

P09 is not used as a primary effect study. It is retained because a full-text
multivocal review and its replication-package trail can support terminology
and citation chaining. Its mixed academic/grey corpus is a limitation that
must remain attached to every review-level claim.

## 4. Evidence boundary established by this batch

The charted records support mapping mechanisms, systems, failure models,
operational artefacts and technical outcomes. They do not, as a group,
establish that reliability automation improves engineers' workload, trust,
understanding or decision quality. Several studies describe engineers as
operational users or analyse incident records, but that is operational
human-work evidence rather than direct participant evidence.

The human-practice records are especially important for the later PhD design:
P23 reports qualitative analysis of 30 incidents, P26 reports preliminary work
using incident reports and interviews, and P27 describes a case study of
controlled continuous deployment in three telecommunications RAN technologies.
These records should inform construct selection and context, not be presented
as controlled evidence for the proposed experiment.

## 5. Source traceability

Each chart row contains a DOI or stable full-text URL and a provenance note.
The primary source routes checked for this batch include publisher pages,
author manuscripts and institutional repositories. Representative traceable
full texts are:

- Chen et al., incident triage: `https://www.microsoft.com/en-us/research/wp-content/uploads/2019/03/incidenttriage_cameraReady.pdf`
- Meiklejohn et al., Filibuster: `https://christophermeiklejohn.com/publications/filibuster-socc-2021.pdf`
- Brogi et al., self-healing trans-cloud applications: `https://link.springer.com/article/10.1007/s00607-021-00977-z`
- Sillito and Kutomi, incident response: `https://arxiv.org/abs/2008.11192`
- Sillito and Pope, learning from failure: `https://arxiv.org/html/2402.09538v1`
- Dakkak et al., controlled continuous deployment: `https://dl.acm.org/doi/fullHtml/10.1145/3529320.3529323`

## 6. Remaining work

1. Retrieve and assess the nine pending records.
2. Complete design-sensitive quality appraisal for all eligible records.
3. Update the claim register only with claims tied to a source location and
   attached limitation.
4. Complete thematic synthesis and research-gap analysis.
5. Reconcile the PRISMA ledger after authenticated database exports are
   available. Do not enter invented ACM, IEEE, Scopus or Web of Science counts.

## 7. Validation

- CSV files use explicit `not_reported` or bounded evidence language.
- P09 is canonical; the earlier P21 duplicate mapping is preserved.
- P11 is not upgraded from abstract-only status.
- No full-text exclusion is counted without a full-text reason.
- No authenticated database result count is claimed.
