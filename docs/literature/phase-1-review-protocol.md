# Phase 1 scoping-review and evidence-mapping protocol

**Project:** PhD Preparation – Reliability Automation and Software Engineering Practice  
**Working title:** *An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments*  
**Protocol status:** Finalised for search-platform smoke-testing; no database search has yet been counted as executed  
**Protocol version:** 1.0  
**Version date:** 2026-08-09  
**Planned coverage:** 2010 through the date on which each search is executed

## 1. Purpose

This scoping review will systematically map empirical evidence about
reliability-oriented automation in continuous-delivery and related cloud-native
operational environments. It will identify the automation mechanisms studied,
the systems and failure contexts used, the technical outcomes measured, and the
extent to which research directly examines engineers' diagnosis, recovery,
escalation, workload, understanding and reliance on automation.

The review will refine the proposed PhD design and identify defensible
experimental variables, measures and validity requirements. It will not infer
that one automation strategy is universally superior, treat feasibility probes
as empirical effect evidence, or use telemetry as a substitute for direct human
evidence.

## 2. Review design and reporting framework

The review uses a scoping-review design combined with systematic evidence
mapping. This is appropriate because the expected evidence includes controlled
experiments, field and case studies, operational datasets, interviews, surveys,
mixed-methods studies, experience reports and secondary reviews. These designs
cannot be treated as equivalent and are unlikely to support a meaningful pooled
effect estimate.

The review report will follow PRISMA-ScR. Search methods will be reported using
PRISMA-S. Software-engineering mapping guidance will inform classification and
the separation of primary and secondary evidence. Reporting guidance does not
replace critical appraisal or determine study quality.

No meta-analysis is planned. A later amendment would be required if a
sufficiently homogeneous subset justified quantitative synthesis.

## 3. Review objectives

1. Map reliability-automation mechanisms and intervention points.
2. Characterise software systems, domains, deployment contexts, fault/incident
   models, comparators, data sources and empirical designs.
3. Compare technical outcome definitions and identify where similar labels hide
   different operationalisations.
4. Identify direct and indirect evidence about engineering work and
   human–automation interaction.
5. Appraise design-specific evidence limitations without collapsing unlike
   methods into one score.
6. Translate evidence gaps into explicit requirements or cautions for the
   proposed technical and human-participant studies.

## 4. Review questions

### RQ-S1 — Mechanisms, contexts and technical outcomes

What reliability-automation mechanisms have been empirically studied in
continuous-delivery and closely related cloud-native operational contexts, and
how do their systems, fault or incident models, comparators and measures shape
the reported technical outcomes?

### RQ-S2 — Engineering practice and human evidence

What direct evidence shows how reliability automation affects engineers'
diagnosis, recovery and escalation work, perceived workload, understanding and
reliance on automation, and how have those constructs been operationalised?

### RQ-S3 — Validity, reproducibility and design gaps

Which methodological limitations and evidence gaps constrain causal,
transferable and reproducible conclusions about the technical and human effects
of reliability automation, and what requirements follow for the proposed
mixed-methods study?

## 5. Scope using PCC

| Element | Operational definition |
|---|---|
| Population / subjects | Software engineers, operators, SRE/DevOps practitioners and software teams; or software systems, services, deployments, incidents and operational artefacts when no humans are studied. |
| Concept | Automation that detects, diagnoses, prevents, contains, mitigates or recovers from software-service failures, including automated rollback, remediation, failover, self-healing, incident triage/support, resilience testing and monitoring-triggered response. Fault injection is eligible when it evaluates or validates such mechanisms or the reliability evidence used to design them. |
| Context | Continuous delivery/deployment, DevOps/SRE, cloud-native, microservice, distributed and large-scale online-service environments. Adjacent operational studies are eligible only when their mechanism or human evidence is transferable and the rationale is recorded. |

Continuous delivery and continuous deployment will be coded separately when
the source permits. A paper's terminology will be retained, but the reviewer
will not assume the two practices are equivalent.

## 6. Eligibility criteria

### 6.1 Inclusion criteria

A record is eligible for full-text assessment when it meets all applicable
criteria:

- published in English from 2010 through the search date, or identified as an
  earlier seminal source through documented citation chasing;
- peer-reviewed journal article, conference paper or empirically grounded
  experience report;
- primary empirical research using experiments, case/field studies,
  operational data, repository mining, interviews, surveys, tool evaluation or
  mixed methods; or a systematic/mapping/scoping review retained as secondary
  evidence;
- concerns a software-intensive operational setting within the PCC scope; and
- reports enough information to assess at least one automation mechanism,
  technical outcome, engineering-practice outcome, empirical design or
  methodological limitation relevant to the review questions.

Secondary reviews are eligible for terminology, landscape context and citation
chaining but will not be counted as primary empirical studies.

### 6.2 Exclusion criteria

Exclude and record one primary reason when the source is:

- unrelated to operational reliability automation or reliability-relevant
  engineering practice;
- generic CI/CD adoption research with no failure, resilience, incident,
  recovery or operational-work relevance;
- exclusively about security automation without a transferable reliability or
  incident-response component;
- a conceptual architecture, position paper or unevaluated tool proposal;
- vendor marketing, product documentation, an informal blog or other
  non-peer-reviewed material offered as empirical evidence;
- a duplicate or superseded report that adds no relevant evidence;
- a non-English record for which eligible English full text is unavailable; or
- inaccessible in full text after the documented retrieval process.

Practitioner and standards material may be placed in a separate contextual
register. It cannot support an empirical effect claim.

### 6.3 Full-text retrieval rule

An apparently eligible record is not excluded for access on the first failed
attempt. Record attempts through the publisher, institutional library,
author/institutional repository and a lawful author contact or preprint route
where feasible. Only then apply `full_text_unavailable`, retaining the metadata
and access history for transparency.

### 6.4 Pilot amendment rule

Pilot the criteria on 20 deduplicated records. Any boundary change must be
dated in the changelog, justified, and applied retrospectively to all records.
Search terms may be adjusted after smoke-testing or the pilot only through a
new logged query/version; an earlier search record must never be overwritten.

## 7. Information sources

Primary database coverage:

- ACM Digital Library;
- IEEE Xplore; and
- Scopus or Web of Science, depending on documented institutional access (both
  may be used if available).

Supplementary identification:

- backward and forward citation chasing from included studies and eligible
  secondary reviews;
- publisher, DOI and author/institutional repository pages for verification and
  lawful full-text retrieval; and
- Google Scholar only for documented citation chasing or locating a known
  record, not as the sole reproducible database search.

Every database and platform must be named. The search log will preserve the
exact query, interface, date/time, filters, coverage statement where available,
result count and export filename before deduplication.

## 8. Search strategy

Three complementary search families will be executed. Family T maps technical
mechanisms/outcomes; Family H targets human and engineering-practice evidence;
Family M targets methodological and reproducibility evidence. The full strings
and database translations are versioned in
`phase-1-search-execution-plan.md`.

The three families are deliberately overlapping. Deduplication occurs after
all exports are retained. Human terms are not added as a mandatory block to the
technical search because that would reduce recall for system-only studies.

Before counting a search as executed, smoke-test the database translation using
known seed records. A valid translation should retrieve relevant known records
without being tailored only to those titles. Record failures and amendments.

## 9. Record management and deduplication

1. Export complete metadata and abstracts where licensing permits, preferably
   RIS or BibTeX plus CSV when available.
2. Preserve the unmodified export filename and a SHA-256 hash or equivalent
   immutable identifier.
3. Assign each imported record a source-specific identifier and later a stable
   review `paper_id`.
4. Deduplicate first by normalised DOI, then exact normalised title, then
   title/first-author/year inspection.
5. Retain a duplicate log linking removed records to the kept record and the
   deduplication rule.
6. Link multiple reports of the same underlying study rather than silently
   discarding evidence-bearing companion reports.

Database exports and copyrighted full texts must not be committed publicly when
their licence prohibits it. The repository should retain permitted metadata,
hashes, provenance and extraction records.

## 10. Screening

### 10.1 Title and abstract

The decision sequence is:

1. Is the record about software-intensive operational or delivery work?
2. Does it address reliability, resilience, incidents, failure handling,
   recovery or directly relevant operational decision-making?
3. Does it concern automation, automation interaction, or empirical methods
   that directly inform the proposed comparison?
4. Is there an empirical basis, or is it an eligible secondary review?

Use `include`, `exclude` or `uncertain`. Uncertainty advances to full text. Do
not infer empirical status from venue or title alone.

### 10.2 Full text

Apply all eligibility criteria and record exactly one primary exclusion reason:

- wrong context/domain;
- no reliability/failure-handling relevance;
- no relevant automation or engineering-practice evidence;
- non-empirical/conceptual only;
- secondary source not retained for context;
- duplicate/superseded report;
- full text unavailable after documented attempts; or
- other, with a specific explanation.

Where several publications report one study, link them and define the unit of
analysis explicitly.

### 10.3 Reviewer reliability

The primary reviewer will apply all decisions. If a second reviewer or
supervisor is available, independently check at least a documented sample of
title/abstract exclusions, full-text decisions and charted studies. Record the
sample, disagreements and resolution. If unavailable, repeat a random sample
after a time interval and report the limitation; do not call this independent
inter-reviewer agreement.

## 11. Data charting

For each included source, record:

- full citation, DOI/stable URL, publication type, venue and year;
- system, architecture, domain and operational/deployment context;
- automation mechanism, intervention point and comparator;
- fault/incident model and workload;
- research method, unit of analysis and data source;
- participants or operational subjects and sampling;
- technical outcomes with exact definitions and units;
- human/engineering-practice constructs and their instruments or observation
  method;
- main findings, source location and whether the wording is reported or
  reviewer-inferred;
- reproducibility information, including artefacts, versions, configuration,
  reset and raw-data availability;
- limitations and threats to validity;
- relevance to RQ-S1, RQ-S2 and RQ-S3; and
- extraction status and evidence strength.

Use `not_reported`, not an inferred value. `abstract_only` records cannot enter
the substantive synthesis.

## 12. Critical appraisal

Critical appraisal is required because the review will inform an empirical PhD
design. Apply the design-specific domains in `quality-appraisal-guide.md`:

- controlled/technical experiments;
- observational, field and operational-data studies;
- qualitative studies;
- mixed-methods studies;
- empirically grounded experience reports; and
- systematic, mapping or scoping reviews.

Each domain receives `low concern`, `some concern`, `high concern` or
`insufficient information`, with a source-linked rationale. Do not convert
these judgements into one cross-design numeric ranking. Appraisal informs the
weight and wording of synthesis; it is not an automatic exclusion rule unless
the empirical basis cannot be established.

## 13. Synthesis

Only full-text-verified included studies enter the evidence synthesis.

The review will produce:

- descriptive counts by year, venue, study design, domain, system type and
  evidence type;
- a mechanism–intervention–outcome map;
- a context–fault/workload–comparator map;
- a metric-definition comparison for detection, diagnosis, recovery, service
  impact, containment, rollback and intervention;
- a human-evidence map separating direct participant evidence, observed
  operational work, telemetry, inferred proxies and no human evidence;
- a design-sensitive comparison of findings, contradictions and uncertainty;
  and
- a gap-to-design table identifying which proposed variables, measures,
  technologies or protocol rules are supported, challenged or unresolved.

For every synthesis claim, identify the supporting studies, evidence type,
appraisal concerns and contradictory evidence. Describe evidence as causal only
when the design and analysis warrant that language.

## 14. Evidence and inference boundaries

- Technology compatibility establishes feasibility, not reliability effects.
- System telemetry measures system events; it does not directly measure
  workload, trust, understanding or decision rationale.
- Incident records may evidence operational work but are not automatically
  participant measures.
- Self-report measures require construct and instrument scrutiny.
- A controlled benchmark can support bounded causal inference while still
  having limited ecological validity.
- Secondary and practitioner sources may frame concepts but cannot be silently
  counted as primary empirical evidence.
- Unverified or inaccessible claims remain excluded from synthesis.

## 15. Ethics, data management and AI assistance

The review uses published records and does not collect participant data. The
later human-participant study remains subject to ethics approval.

The review repository will store permitted bibliographic metadata, decisions,
extractions, hashes and derived tables. Restricted full texts or database
exports will not be published contrary to their licence.

AI assistance, if used, must be logged by task and version. It may help format,
deduplicate or prioritise records, but the named reviewer remains responsible
for every eligibility decision, extraction, quality judgement, citation and
claim. No AI-generated bibliographic fact may enter the review without source
verification.

## 16. Phase 1 exit criteria

Phase 1 is complete only when:

- protocol v1.0 and later amendments are retained;
- all database searches and supplementary methods are logged reproducibly;
- source exports have been deduplicated with a preserved duplicate trail;
- title/abstract and full-text decisions are complete with reasons;
- included studies are full-text charted;
- design-sensitive critical appraisal is complete;
- the claim register, PRISMA flow and literature map are updated from verified
  evidence;
- the synthesis, research-gap analysis and design mapping are written; and
- the refined PhD questions and Phase 2/3 design decisions are reviewed against
  the evidence.

The current stage satisfies protocol finalisation only.

## 17. Protocol amendments

| Version | Date | Change | Prospective/retrospective |
|---|---|---|---|
| 0.1 | 2026-08-08 | Initial protocol and nine-record seed map | Prospective |
| 1.0 | 2026-08-09 | Refined review questions; separated technical, human and methods searches; added deduplication, retrieval, appraisal, AI-use and amendment rules | Prospective; before named database searches |

## 18. Methodological references

- Tricco AC et al. PRISMA Extension for Scoping Reviews (PRISMA-ScR):
  Checklist and Explanation. *Annals of Internal Medicine*. 2018;169(7):467–473.
  https://doi.org/10.7326/M18-0850
- Rethlefsen ML et al. PRISMA-S: an extension to the PRISMA Statement for
  Reporting Literature Searches in Systematic Reviews. *Systematic Reviews*.
  2021;10:39. https://doi.org/10.1186/s13643-020-01542-z
- Petersen K, Vakkalanka S, Kuzniarz L. Guidelines for conducting systematic
  mapping studies in software engineering: An update. *Information and Software
  Technology*. 2015;64:1–18. https://doi.org/10.1016/j.infsof.2015.03.007
- Kitchenham B et al. Systematic literature reviews in software engineering – A
  systematic literature review. *Information and Software Technology*.
  2009;51(1):7–15. https://doi.org/10.1016/j.infsof.2008.09.009
