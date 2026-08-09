# Phase 1G provisional synthesis and gap analysis

**Project:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments
**Execution date:** 2026-08-09
**Branch intended for:** `research/phase-1-literature-evidence`
**Status:** Provisional synthesis; Phase 1 exit criteria are not yet satisfied

## 1. Purpose

This stage integrates the evidence chart and design-sensitive appraisal into a
provisional narrative synthesis. It is an evidence-mapping output, not a claim
that the literature review is complete. The synthesis is restricted to the 15
records with traceable full text in Phase 1E: 14 primary studies and one
secondary review. Nine additional records remain in the retrieval queue.

The 15 appraisals remain `chart_based_provisional` because page, section, table
and figure locators have not yet been transcribed for every appraisal domain.
The named ACM Digital Library, IEEE Xplore and Scopus/Web of Science searches
also remain pending authentication and export. Neither limitation is hidden by
the narrative synthesis.

## 2. Corpus and evidence boundaries

| Evidence stream | Records | Permitted use |
|---|---:|---|
| Technical mechanism and outcome evidence | 12 primary records | Claim-scoped descriptive synthesis of mechanisms, systems, faults and reported technical outcomes |
| Direct human/practice evidence | 3 primary records: P23, P26, P27 | Descriptive synthesis of incident response, post-incident learning and controlled deployment practice |
| Secondary context | 1 record: P09 | Terminology, landscape context and citation chaining only |
| Retrieval-pending records | 9 records | Search/retrieval planning only; not evidence in the synthesis |

The technical and human streams must not be merged into a single effect claim.
Operational subjects, incident records and workflow artefacts are not
equivalent to direct measures of workload, trust, understanding or decision
rationale.

## 3. Provisional synthesis by mechanism

### 3.1 Resilience testing and fault injection

P06, P10, P15 and P19 show a recurring technical pattern: automation is used
to expose resilience weaknesses, propagate or inject faults, and make the
resulting behaviour observable. The reported outcomes concern exposed failure
paths, test-space or execution characteristics, resilience profiles,
degradation propagation and developer-facing visualisation.

These studies justify a Phase 3 fault model with explicit, repeatable fault
injection and measured system consequences. They do not establish that the
automation improves engineer workload, trust, decision quality or production
recovery. Tool evaluations and prototype demonstrations also do not by
themselves establish superiority over a manual recovery condition.

### 3.2 Incident characterisation, aggregation and triage

P04, P12, P17 and P18 examine automation around incident records, ticket
profiling, incident grouping or triage. This stream is closer to operational
practice than development-time fault injection because it uses industrial
incident or monitoring data. However, its reported outcomes remain primarily
classification, prioritisation, aggregation, assignment or workflow measures.

The evidence supports treating detection, context construction and triage as
distinct intervention points. It does not support treating triage or incident
aggregation as autonomous recovery, nor does it establish that better model
performance causes better engineer decisions or shorter service recovery.

### 3.3 Automated diagnosis and investigation support

P14 and P16 examine automated diagnostic-information collection, root-cause
analysis, explanation or query recommendation. These mechanisms can be mapped
to a decision-support condition in which the engineer receives additional
diagnostic material while retaining responsibility for the recovery decision.

The current evidence does not identify a controlled participant comparison of
automation conditions with validated workload, trust, understanding or
decision-quality measures. Reported model accuracy, query quality or
deployment exposure must therefore remain technical or operational evidence,
not human-effect evidence.

### 3.4 Automated recovery and self-healing

P13 provides the clearest charted example of an automated recovery mechanism:
monitoring, dependency-aware planning and orchestration are used to return a
trans-cloud application towards a target state under controlled and monkey
testing scenarios. It supports the feasibility of measuring detection,
recovery and instability outcomes in a technical system.

Its trans-cloud prototype context, application model and lack of human
participants limit direct transfer to the proposed transactional continuous
delivery system. It should inform the recovery event model, not determine the
experimental technology choice by itself.

### 3.5 Engineering practice and controlled deployment

P23, P26 and P27 provide the strongest direct practice evidence in the current
batch. P23 studies incident detection, investigation and mitigation accounts;
P26 examines preliminary post-incident learning using reports and interviews;
P27 describes controlled continuous deployment in a high-reliability
telecommunications setting.

These records establish that incident response, learning, deployment controls
and reliability constraints are socio-technical practices. They do not provide
a controlled comparison of manual and automated recovery, and P26 must retain
its preliminary status in every downstream claim.

## 4. Cross-cutting findings

1. **Mechanism diversity is high.** The batch covers testing, fault injection,
   incident context construction, triage, diagnosis, investigation support,
   self-healing and controlled deployment. Frequency of appearance is not a
   sufficient basis for selecting the PhD intervention.
2. **Technical outcome definitions are heterogeneous.** Studies report
   resilience exposure, degradation, model performance, incident grouping,
   recovery or instability outcomes using different units, baselines and event
   boundaries. A common metric contract is required before any comparison.
3. **Industrial data improve ecological relevance but restrict replication.**
   Several operational studies use proprietary incident, ticket or monitoring
   data and do not expose the configuration needed for independent replication.
4. **Direct human evidence is sparse and separate.** The current batch contains
   direct qualitative/practice evidence, but it does not contain a controlled
   human-participant study of reliability automation with validated workload,
   trust, understanding or decision-quality measures.
5. **Telemetry is not a human-factor measure.** Incident counts, reassignment,
   query use, model accuracy and recovery time can describe system or workflow
   behaviour; they cannot, without additional evidence, establish what an
   engineer understood, trusted, intended or experienced.
6. **Continuous-delivery evidence is narrower than adjacent operational
   evidence.** Much of the charted technical work concerns cloud operations,
   microservices or incident management rather than a controlled continuous
   delivery intervention. This supports the proposed study's focus but limits
   direct generalisation.

## 5. Research-gap interpretation

The main gap is not simply that more automation tools are needed. It is the
absence of a reproducible, mixed-methods comparison that holds the fault,
workload, detection rule, software version and reset procedure constant while
varying the recovery-initiation condition and observing both technical outcomes
and engineers' interaction with the automation.

The gap register in `evidence-gap-register-batch-06.csv` records the following
gaps separately:

- controlled comparison gap;
- human-measurement gap;
- metric and event-boundary gap;
- reproducibility and proprietary-data gap;
- continuous-delivery context gap; and
- transferability gap between prototypes, industrial datasets and the proposed
  transactional system.

These are gaps in the current evidence map, not universal claims about every
paper in the field. The nine retrieval-pending records and authenticated
database exports could modify their scope.

## 6. Consequence for the review questions

The review questions RQ-S1, RQ-S2 and RQ-S3 should be retained for the next
retrieval pass. The evidence does not justify collapsing RQ-S3 into RQ-S1 or
treating operational telemetry as a substitute for human evidence. A later
protocol revision may sharpen RQ-S3 around direct versus indirect evidence, but
that decision should follow retrieval of P01, P02, P03, P05, P07, P11, P20,
P22 and P24 and execution of the named database searches.

## 7. Phase 3 design implications

The design implications are recorded separately in
`phase-3-design-implications-batch-06.md`. The current evidence supports:

- retaining a bounded comparison of standardised manual recovery and
  rule-based automated recovery;
- preserving explicit no-fault, service-termination and dependency-latency
  scenarios until the evidence and dry-runs justify expansion;
- defining detection, recovery initiation, recovery completion and failure
  impact as separate timestamped events;
- recording technical outcomes and human/practice observations as separate
  evidence streams;
- requiring a participant protocol and ethics process before making claims
  about workload, trust, understanding or decision-making; and
- keeping the technology decision subordinate to the intervention and
  measurement requirements.

## 8. Open gates before Phase 1 close-out

Phase 1 remains open until the project has, at minimum:

1. authenticated exports and provenance for the named bibliographic databases,
   or a documented access limitation and bounded alternative;
2. retrieval and assessment of the nine pending records;
3. page/section/table/figure locators for final claim support;
4. a checked final literature map and claim register;
5. a completed PRISMA-ScR accounting record; and
6. a progress-ledger entry recording the final limitations and the decision on
   whether the provisional PhD questions are retained or refined.

Until then, this package is a provisional synthesis and design-input stage,
not a completed literature review.
