# Phase 1 scoping-review protocol

**Project:** PhD Preparation – Reliability Automation and Software Engineering Practice

**Working title:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

**Protocol status:** Draft for review; searching and screening have not yet been completed in the named bibliographic databases.

**Protocol version:** 0.1

**Date prepared:** 2026-08-08

## 1. Purpose and rationale

This scoping review will map the empirical evidence surrounding reliability-oriented automation in continuous delivery and related cloud-native operational settings. It will identify the systems and software domains studied, the automation mechanisms evaluated, the technical outcomes measured, and the extent to which studies examine engineers' work, judgement or decision-making.

The review is intended to refine the PhD research questions and inform the later choice of an experimental software system. It is not intended to establish that one automation strategy is universally superior, and no causal claim will be made from the review alone. A scoping approach is appropriate because the anticipated evidence is heterogeneous: industrial interviews and surveys, operational datasets, controlled fault-injection experiments, tool evaluations and conceptual frameworks may all be relevant but cannot be treated as equivalent evidence.

The reporting plan will follow PRISMA-ScR. The PRISMA-ScR guidance describes 20 essential and two optional reporting items for scoping reviews and is maintained by the PRISMA Statement. The completed review should include a study-flow record, explicit eligibility criteria, data-charting fields, a narrative synthesis and limitations.

## 2. Review objectives

1. Map the reliability-oriented automation mechanisms investigated in continuous delivery, continuous deployment, cloud-native and online-service settings.
2. Characterise the software systems, domains, fault or incident types, empirical methods, data sources and technical outcomes used in that research.
3. Identify how software-engineering practice is evidenced, particularly diagnosis, recovery, escalation, trust, workload, understanding and human–automation decision-making.
4. Identify methodological gaps relevant to a reproducible mixed-methods study, including lack of controlled comparisons, unclear metric operationalisation, limited replication, proprietary data and absence of human-participant evidence.

## 3. Review questions

These are review questions, not replacements for the provisional PhD research questions.

### RQ-S1 — Automation and technical evidence

What reliability-oriented automation mechanisms have been empirically studied in continuous delivery or closely related cloud-native operational contexts, and what technical outcomes have been measured?

### RQ-S2 — Systems and experimental design

What software systems, domains, failure or incident models, deployment contexts and empirical designs are used to study those mechanisms?

### RQ-S3 — Human and engineering-practice evidence

What evidence exists about engineers' diagnosis, recovery, escalation, workload, trust, understanding or decision-making in interactions with reliability automation?

Reproducibility will be extracted as a cross-cutting methodological field rather than treated as a fourth broad review question.

## 4. Scope using PCC

| Element | Operational scope |
|---|---|
| Population | Software engineers, operators, SRE/DevOps practitioners, software teams, or software systems receiving operational and deployment work. Studies with no human participants remain eligible when they provide empirical evidence about systems or operational artefacts. |
| Concept | Reliability-oriented automation: automated deployment or rollback, monitoring-triggered response, self-healing or remediation, resilience testing, chaos/fault injection, incident detection/triage/recovery support, or related automation that changes failure handling. |
| Context | Continuous delivery, continuous deployment, DevOps, cloud-native, microservice, distributed or large-scale online-service environments. Adjacent studies may be included when their mechanism and evidence directly inform the proposed reliability experiment. |

The review will distinguish **continuous delivery** (software kept in a deployable state) from **continuous deployment** (automatic deployment to production). The distinction matters because the literature does not always use the terms consistently.

## 5. Eligibility criteria

### Include

- English-language papers published from 2010 through 2026-08-08, including online-first publication where the publication year is identifiable.
- Peer-reviewed journal articles, conference papers and experience reports with a defined empirical basis.
- Primary empirical studies using experiments, case studies, field studies, interviews, surveys, operational datasets, repository mining, tool evaluations or mixed methods.
- Systematic, mapping or scoping reviews for citation chaining and landscape context; these will be labelled as secondary evidence and will not be treated as primary findings.
- Studies reporting at least one of: automation mechanism, system/domain, failure/incident model, technical outcome, engineering-practice observation or human-factor measure.

### Exclude

- Vendor marketing, informal blog posts, product documentation and non-peer-reviewed commentary as evidence sources.
- Papers about generic CI/CD adoption with no reliability, incident, failure-handling or operational-practice relevance.
- Purely conceptual architectures, position papers or tool proposals with no empirical evaluation. These may remain in a separate exclusion log if they help locate primary studies.
- Studies concerned solely with security automation unless the paper also provides evidence directly relevant to reliability, incident response or human–automation interaction.
- Studies where the full text cannot be obtained after reasonable library and author-repository searching. Such records will remain in the search log with the reason for exclusion.

The eligibility boundary may be refined after a pilot screen of 20 records. Any change must be recorded in the protocol changelog and applied consistently to all records.

## 6. Information sources and search strategy

The planned sources are:

- ACM Digital Library;
- IEEE Xplore;
- Scopus or Web of Science, subject to access;
- Google Scholar for forward/backward citation chasing only; and
- author or institutional repositories for legally accessible full text.

The primary database searches will be run separately because syntax differs. The exact query, date, database, filters, result count and export filename will be recorded in search-log.csv. The current seed records were discovered through web-assisted source identification and are marked as seed candidates; they are not presented as a completed database search.

### Draft concept blocks

    ("continuous delivery" OR "continuous deployment" OR DevOps OR "continuous software engineering")
    AND
    (reliability OR resilience OR dependability OR incident OR failure OR recovery OR rollback OR "self-healing" OR "fault injection" OR "chaos engineering")
    AND
    (automation OR automated OR "human factors" OR engineer* OR operator* OR decision* OR workload OR trust OR diagnosis OR mitigation)

### Database-specific starting queries

**ACM Digital Library**

    :("continuous delivery" OR "continuous deployment" OR DevOps)
    AND
    :(reliability OR resilience OR incident OR recovery OR rollback OR "fault injection" OR "chaos engineering" OR "self-healing")

**IEEE Xplore**

    +("continuous delivery" OR "continuous deployment" OR DevOps)
    AND
    +(reliability OR resilience OR incident OR recovery OR rollback OR "fault injection" OR "chaos engineering" OR "self-healing")

**Scopus/Web of Science**

    TITLE-ABS-KEY(("continuous delivery" OR "continuous deployment" OR DevOps)
    AND
    (reliab* OR resilien* OR incident* OR recover* OR rollback OR "fault injection" OR "chaos engineering" OR "self-healing")
    AND
    (automat* OR engineer* OR operator* OR decision* OR workload OR trust OR diagnosis OR mitigation))

The first search will be intentionally broad. A second, human-factors-focused search will add terms such as "incident response", "human factors", "cognitive workload", "decision making", "operator" and "on-call". Search strings will be iterated only after the pilot search and documented rather than silently changed.

## 7. Record management and screening

Each record will receive a stable paper_id. DOI will be the preferred deduplication key, followed by a normalised title and first author/year. Search results, screening decisions and extracted evidence are separate from the project's experimental data directories.

The planned workflow is:

1. Export results from each named database in a durable format.
2. Record the search provenance before deduplication.
3. Deduplicate using DOI and then title/author checks.
4. Pilot title/abstract screening on 20 records and revise the decision rules if necessary.
5. Screen all titles/abstracts against the eligibility criteria.
6. Retrieve full texts for potentially eligible records.
7. Record one primary exclusion reason for every full-text exclusion.
8. Chart included studies using the fields in evidence-matrix.csv.
9. Verify every extracted claim against the full text, not just an abstract or search snippet.

Because this is currently a solo research-development project, the first pass may be conducted by one reviewer. That is a limitation. A later protocol should seek a second reviewer or supervisor check for a sample of screening and charting decisions, and report agreement or adjudication where available.

## 8. Data-charting fields

The matrix will capture:

- bibliographic identity and publication type;
- system studied and software domain;
- automation mechanism and intervention point;
- deployment/operational context;
- fault or incident model;
- empirical method and data source;
- participants or operational subjects;
- technical metrics/outcomes;
- human factors and engineering-practice evidence;
- reproducibility information;
- limitations and threats to validity;
- relevance to RQ-S1, RQ-S2 and RQ-S3; and
- provenance and extraction status.

The matrix must not contain invented values. If a field is not reported, use not_reported; if only an abstract has been checked, use abstract_only and do not describe the record as fully extracted.

## 9. Synthesis plan

The review will use descriptive mapping and narrative synthesis:

- counts by year, venue, method, domain, automation mechanism and evidence type;
- a system/domain taxonomy showing whether studies use production systems, industrial datasets, open-source systems, benchmarks or prototypes;
- a mechanism–outcome map distinguishing detection, diagnosis, mitigation, recovery and deployment outcomes;
- a human-evidence map distinguishing telemetry proxies from direct participant or observational evidence; and
- a gap and feasibility narrative tied to the proposed OrderFlow candidate, without selecting the system solely from frequency in the literature.

No meta-analysis is planned. Differences in interventions, systems, metrics and study designs are expected to make pooled effect estimates inappropriate at this stage.

## 10. Quality and validity handling

Scoping review reporting does not turn heterogeneous studies into equivalent evidence. The matrix will therefore record design and limitation information, even though a formal risk-of-bias assessment is not the primary purpose of this map.

The following threats will be monitored:

- database and language bias;
- terminology variation between continuous delivery, deployment, DevOps, SRE and chaos engineering;
- publication and positive-result bias;
- over-representation of large technology companies and proprietary datasets;
- abstract-only extraction;
- single-reviewer screening and charting;
- conflation of system telemetry with human cognition or workload; and
- transferability from production systems or benchmark applications to other domains.

## 11. Outputs and Phase 1 exit criteria

Phase 1 is complete only when the repository contains:

- this reviewed protocol with a recorded version and changelog;
- database-specific searches and provenance in search-log.csv;
- a screening log with inclusion/exclusion decisions;
- a populated evidence matrix with primary studies separated from secondary reviews;
- a preliminary literature map and explicit evidence gaps;
- a documented decision on whether the provisional PhD questions should be retained or revised; and
- a progress-ledger entry recording validation and unresolved limitations.

The current commit establishes the protocol and seed evidence map. It does not yet satisfy the Phase 1 exit criteria because the named bibliographic database searches and full-text charting remain outstanding.

## 12. Protocol changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-08 | Initial protocol aligned with Phase 0 questions, supervisor feedback and a seed source map. |

