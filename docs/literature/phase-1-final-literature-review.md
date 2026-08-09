# Phase 1 final literature review

**Project:** *An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments*
**Review design:** Scoping review and evidence map
**Protocol:** v1.0
**Close-out date:** 2026-08-09
**Intended branch:** `research/phase-1-literature-evidence`
**Status:** Complete for the accessible and source-verifiable corpus, with an explicit authenticated-database access limitation

## Executive summary

This review maps empirical and practice evidence about reliability-oriented
automation in continuous-delivery, cloud-native, microservice and large-scale
online-service settings. It separates technical system outcomes, operational
workflow evidence and direct evidence about engineers' experience or
decision-making.

The final auditable queue contains 27 provisional candidates, reduced to 26
canonical records after deduplication. Twenty-six records were screened at
title and abstract level: 24 were retained for full-text assessment and two
were excluded at that stage. All 24 full-text records have now been resolved.
Twenty-two records are included in the final evidence map: 19 primary studies,
two secondary reviews and one contextual practice/research article. Two records
(P03 and P22) could not be included because complete lawful full text remained
unavailable after documented retrieval attempts. They remain visible in the
audit trail and are not treated as methodological exclusions.

The evidence is heterogeneous. Technical studies cover fault injection,
resilience testing, incident characterisation, triage, aggregation, profiling,
root-cause analysis, query recommendation and self-healing. Practice studies
cover continuous-deployment barriers, architecture, incident response, expert
debugging, post-incident learning and controlled deployment. The accessible
corpus does not contain a controlled participant comparison of manual and
automated reliability recovery with validated measures of workload, trust,
understanding or decision quality.

The strongest implication for the PhD is a bounded mixed-methods comparison.
The first technical experiment should hold the application version, workload,
fault, detection rule and reset procedure constant while varying the
recovery-initiation condition. Detection, recovery initiation, recovery
completion, service recovery and failure impact should be recorded as separate
events. Any claim about workload, trust, understanding or decision-making must
come from a separate participant protocol and cannot be inferred from system
telemetry.

The named ACM Digital Library, IEEE Xplore and Scopus/Web of Science searches
were not executed with authenticated exports in this workspace. Public
publisher, author, institutional and open-access routes were used for known
record retrieval and citation chasing, but no web-result count is presented as
database coverage. This limitation is fully recorded in
`authenticated-database-access-closure-batch-07.csv` and bounds the review's
claim from “the accessible and source-verifiable corpus”, rather than the whole
published field.

## 1. Review purpose and questions

The review refines the proposed PhD design by mapping mechanisms, contexts,
technical outcomes, engineering practice and methodological requirements. It
does not produce a pooled effect estimate because the included designs,
interventions, units of analysis and outcomes are not sufficiently homogeneous.

**RQ-S1 — Mechanisms, contexts and technical outcomes.** What
reliability-automation mechanisms have been empirically studied in
continuous-delivery and closely related cloud-native operational contexts, and
how do their systems, fault or incident models, comparators and measures shape
reported technical outcomes?

**RQ-S2 — Engineering practice and human evidence.** What direct evidence
shows how reliability automation affects engineers' diagnosis, recovery and
escalation work, perceived workload, understanding and reliance on automation,
and how have those constructs been operationalised?

**RQ-S3 — Validity, reproducibility and design gaps.** Which methodological
limitations and evidence gaps constrain causal, transferable and reproducible
conclusions about the technical and human effects of reliability automation,
and what requirements follow for the proposed mixed-methods study?

## 2. Method

### 2.1 Scope and eligibility

The population included software engineers, operators, SRE/DevOps practitioners
and software teams, together with software systems, services, deployments,
incidents and operational artefacts where no humans were studied. The concept
was reliability-oriented automation that detects, diagnoses, prevents,
contains, mitigates or recovers from service failures. Fault injection was
eligible when it evaluated or informed reliability mechanisms or the evidence
required to design them. The context covered continuous delivery/deployment,
DevOps/SRE, cloud-native, microservice, distributed and large-scale
online-service environments.

Eligible primary designs included experiments, case and field studies,
operational-data studies, repository mining, interviews, surveys, tool
evaluations and mixed methods. Systematic, mapping and scoping reviews were
retained as secondary context and citation-chaining sources. Conceptual papers,
unevaluated tools, vendor material and generic CI/CD adoption work without a
reliability or operational-work connection were excluded.

### 2.2 Search architecture

The protocol specified three search families:

1. **T — technical mechanisms and outcomes:** reliability automation, incident
   response automation, remediation, recovery, rollback, failover, AIOps,
   fault injection, chaos engineering and resilience testing.
2. **H — engineering practice and human–automation interaction:** incident
   response, triage, diagnosis, decision support, workload, trust, reliance,
   understanding and manual intervention.
3. **M — methods, measurement and reproducibility:** fault-injection design,
   controlled experiments, benchmarks, incident datasets, metrics, reset,
   provenance and mixed methods.

The exact Boolean families and database translations remain in
`phase-1-search-execution-plan.md`. The strategy was not silently modified to
force retrieval of the seed records.

### 2.3 Screening, retrieval and appraisal

The canonical queue was screened using the 20-record pilot specified by the
protocol. The pilot did not require a prospective amendment. Full-text
retrieval was attempted through DOI and publisher pages, institutional and
author repositories, open-access copies and public preprint routes. P03 and P22
reached the documented access boundary: their metadata and abstracts were
retained, but complete texts could not be verified.

Appraisal was design-sensitive rather than a single numerical score. Technical
experiments were considered for design fit, data adequacy, measurement validity,
reproducibility and transferability. Operational-data studies were additionally
considered for proprietary-data and causal-inference limitations. Practice and
qualitative studies were considered for sampling, analysis transparency and the
validity of their practice claims.

Source locators were transcribed at page-and-section level where stable PDF
pagination was available, and at section level for publisher or HTML routes.
The complete locator register is `source-location-transcription-batch-07.csv`.

## 3. Review flow and corpus

| Stage | Records | Final status |
|---|---:|---|
| Provisional candidate register | 27 | Closed |
| Canonical records after deduplication | 26 | Closed |
| Title/abstract screened | 26 | Closed |
| Title/abstract exclusions | 2 | P08 and P25 |
| Full-text records sought | 24 | Closed |
| Full-text records resolved | 24 | Closed |
| Included in final evidence map | 22 | Closed |
| Full text unavailable after documented retrieval | 2 | P03 and P22 |
| Authenticated database exports | 0 | Access limitation recorded |

P21 remains a source record mapped to canonical P09 and is not counted as a
second study. P08 was excluded because no empirical evaluation was evident at
title-and-abstract stage. P25 was retained as an audit correction but excluded
from the evidence queue as a contextual article without a sufficient primary
empirical basis for this review.

### 3.1 Included evidence map

| Evidence stream | Included records | Permitted use |
|---|---|---|
| Continuous-delivery architecture and practice | P01, P02, P27 | Descriptive evidence about deployment barriers, architecture, operations concerns and controlled deployment practice |
| Fault injection and resilience testing | P06, P07, P10, P15, P19, P20 | Mechanism, fault-model, metric and technical-feasibility claims |
| Incident characterisation and workflow automation | P04, P05, P11, P12, P17, P18 | Operational context, triage, aggregation, profiling and incident-information claims |
| Diagnosis and investigation support | P14, P16, P24 | Diagnostic collection, root-cause analysis, query recommendation and expert-debugging context |
| Self-healing and recovery | P13 | Bounded technical evidence about the evaluated self-healing prototype |
| Direct incident-response and learning practice | P23, P26 | Descriptive response and learning evidence; P26 remains preliminary |
| Secondary context | P09, P20 | Taxonomy, landscape context and citation chaining; not primary effect estimates |

The corpus contains no direct participant comparison of manual and automated
recovery. Operational users, incident records, query use, model accuracy,
deployment duration and recovery telemetry are not counted as validated
measures of workload, trust, understanding or decision quality.

## 4. Findings by evidence stream

### 4.1 Continuous delivery is not equivalent to continuous deployment

P01 distinguishes the ability to keep software releasable from automatic,
continuous production deployment. Its mixed-methods study combined 21
interviews from 19 organisations with a survey of 98 practitioners. It
identifies organisational and technical factors that limit movement from
continuous delivery to continuous deployment, including manual quality checks,
test coverage, business decisions and rollback capability (P01, pp. 1–7).

P02 combines 21 interviews from 19 organisations with a survey of 91
practitioners. It identifies architecture characteristics and strategies that
support continuous delivery, including deployability, testability, loggability,
monitorability, resilience and operations-friendly design (P02, pp. 1–6 and
§5). P27 adds an industrial telecommunications case in which deployment
controls and reliability constraints are socio-technical practices rather than
merely pipeline features.

Together, these records support retaining continuous delivery and continuous
deployment as distinct constructs. They also caution against treating a
technically automated pipeline as evidence that operational recovery is
automated.

### 4.2 Fault injection and resilience testing expose technical behaviour

P06 evaluates service-level fault injection through Filibuster. Its mechanism
systematically explores service failures while reducing redundant executions;
the outcome is technical coverage and resilience-issue discovery, not a human
effect. P10 similarly evaluates systematic resilience testing of microservices
through controlled experiments and an industrial case. P15 extends service-level
fault injection to unreliable databases and provides developer-facing
visualisation of fault locations and impacts.

P07 contributes a clear controlled technical design. It injects delay faults
into serverless and containerised cloud-native applications under different user
loads and measures performance and dependability. The article reports increased
latency under injected delay and scenario-specific availability problems; its
results justify explicit workload and fault parameters, not a general claim
that chaos engineering improves recovery (P07, §§3–6; pp. 2399–2423).

P19 operationalises resilience through a degradation-dissemination index. It
injects failures, collects system and user-aware metrics, and evaluates the
measure across two open-source and one industrial microservice system. P20, as
a secondary review, provides a taxonomy of fault-injection-testing design
components. It is useful for method design but cannot be used as a primary
empirical effect estimate.

The common finding is methodological: fault injection can expose failure paths,
degradation propagation and resilience weaknesses when fault, workload,
execution and reset procedures are explicit. The studies do not establish that
the same intervention improves engineers' decisions or production recovery.

### 4.3 Incident automation often operates before recovery

P04 characterises and prioritises incidents using industrial online-service
records. P05 describes Service Analysis Studio, an industrial software-analytics
system used by on-call engineers to analyse monitoring data and support
incident management. P11 studies incident triage across 20 large-scale
Microsoft online-service systems and evaluates automated triage techniques for
assigning incident reports. P12 studies continuous incident triage using
operational records and model evaluation.

P17 automates hierarchical profiling of incident-ticket fault patterns and
reports deployment across more than 10,000 incidents from more than 30 cloud
services. P18 applies graph representation learning to aggregate related
incidents using cascading-failure and KPI information, with an industrial
deployment context.

These studies demonstrate that automation can construct context, narrow the
incident space, assign responsibility, group related reports and profile
postmortem fault patterns. They also show why intervention points must be
separated. Detection, reporting, triage, diagnosis, mitigation and resolution
are different stages. Better triage or aggregation is not equivalent to
autonomous remediation, and workflow metrics do not directly measure the
engineer's reasoning or workload.

### 4.4 Diagnosis and investigation support are not recovery

P14 introduces RCACopilot, which collects diagnostic information, predicts root
cause categories and generates explanations for cloud incidents. Its public
paper reports evaluation on a real Microsoft incident dataset and operational
use of the diagnostic-information collection component. P16 studies KQL query
use and introduces Xpert, a query-recommendation framework evaluated offline and
in production. Both papers support a decision-support condition in which an
engineer receives additional information while retaining responsibility for
the recovery action.

P24 provides contextual evidence about how Google engineers debug complex
distributed-system incidents. It documents a research approach, engineering
pathways, processes, attitudes and examples of expert debugging. It is useful
for constructing realistic tasks and qualitative prompts, but its non-
intervention design prevents a causal claim about automation.

The evidence supports studying diagnostic automation as distinct from recovery
automation. Combining them in the first experiment would make it difficult to
determine whether an outcome arose from better information, a different
recovery policy or a change in human action.

### 4.5 Self-healing is technically promising but context-bound

P13 provides the clearest included example of automated recovery. It presents a
self-healing trans-cloud methodology involving monitoring, recovery planning
and component-level action across application and cloud-service failures. The
study supports measuring detection, recovery initiation, recovery completion and
instability as separate events.

However, the prototype and trans-cloud context differ from the proposed
transactional continuous-delivery system. The study does not include human
participants and does not compare engineer decisions under manual and
automated conditions. It informs the recovery event model and technical
feasibility boundary, not the choice of a universally superior recovery
technology.

### 4.6 Engineering practice is socio-technical and direct human evidence is sparse

P23 studies incident response using engineer interviews and public incident
reports, covering failure detection, investigation and mitigation. P26 studies
learning from failure using incident reports and interviews with engineers and
managers, but its results are explicitly preliminary. P01 and P02 show that
deployment practice and architecture are shaped by organisational decisions,
team responsibilities and operational concerns. P24 provides expert-debugging
context, and P27 shows how controlled deployment is embedded in reliability and
domain constraints.

This is meaningful practice evidence, but it is not a controlled human-factor
study. The accessible corpus does not provide a validated participant
comparison of manual and automated recovery with direct measures of workload,
trust, understanding or decision quality. That absence is a gap in the
accessible corpus, not a universal claim about all software-engineering
research, because authenticated database coverage was unavailable.

## 5. Cross-cutting synthesis

### 5.1 Mechanism diversity prevents a single automation-effect claim

The corpus includes proactive testing, fault injection, incident context
construction, triage, diagnosis, query recommendation, profiling, aggregation
and self-healing. These mechanisms act at different points in the operational
sequence and have different units of analysis. Frequency of appearance is not a
sufficient basis for selecting the PhD intervention.

### 5.2 Technical outcomes are heterogeneous

Reported outcomes include latency, throughput, availability, degradation,
resilience indices, fault coverage, test execution, classification accuracy,
triage reassignment, incident grouping and recovery or instability. The same
label can refer to different event boundaries and denominators. A common metric
contract is needed before comparison.

### 5.3 Industrial data improve relevance but constrain reproducibility

Microsoft, Huawei and CloudA studies provide operational realism, but incident
records, configurations and deployment contexts are proprietary. Prototype
studies provide more controllable mechanisms but differ in workload, fault
models and environmental assumptions. The PhD should preserve both ecological
boundaries and reproducibility artefacts rather than claim that one context
represents the field.

### 5.4 Human evidence must remain separate from telemetry

Incident counts, reassignment, query use, model accuracy and recovery time can
describe systems or workflows. They cannot establish what an engineer
understood, trusted, intended or experienced without a direct human measure.
This is the central methodological boundary for RQ-S2.

## 6. Research gaps and implications for the PhD

The final gap analysis identifies six connected gaps:

1. **Controlled comparison:** the accessible evidence does not provide a clean
   comparison of equivalent manual and automated recovery conditions.
2. **Human measurement:** direct evidence about workload, trust, understanding
   and decision rationale is sparse and not paired with the technical studies.
3. **Metric alignment:** detection, diagnosis, mitigation, recovery and impact
   are operationalised inconsistently.
4. **Reproducibility:** proprietary data and incomplete environment reporting
   restrict independent replication.
5. **Continuous-delivery context:** much evidence is adjacent cloud operations
   rather than a controlled continuous-delivery recovery decision.
6. **Transferability:** prototypes, industrial services and high-reliability
   telecommunications contexts differ materially.

The resulting PhD design requirements are:

* retain a bounded comparison of standardised manual recovery and rule-based
  automated recovery;
* hold fault scenario, workload, application version, detection rule and reset
  procedure constant;
* record fault onset, detection, recovery decision/initiation, recovery action
  completion, service recovery, impact interval and contamination separately;
* preserve immutable trial manifests, seeds, configuration versions, raw event
  records, metric derivation and exclusion logs;
* treat diagnostic support, triage and recovery as separate intervention points;
  and
* define a separate participant protocol, validated measures and ethics process
  before making human-factor claims.

The current evidence supports the OrderFlow fit-probe direction only as a
bounded experimental test system. It does not prove that OrderFlow is the most
representative or generally superior system.

## 7. Limitations of this review

The most important limitation is database access. The protocol named ACM
Digital Library, IEEE Xplore and Scopus or Web of Science as primary sources,
but this workspace did not have authenticated sessions or export capability.
Public records and known-paper retrieval were available, but public page access
cannot reproduce a database result count or establish complete coverage. The
search-closure file records each planned search separately and does not merge
Scopus and Web of Science into one nominal search.

Two full texts remained unavailable. Their metadata and abstract-level relevance
are retained only in the retrieval audit. The final review does not use their
unverified methods, results or review-level counts.

The review is constrained by single-reviewer processing in this workspace. No
inter-reviewer agreement statistic is claimed. The appraisal is design-sensitive
and claim-scoped; it is not a pooled risk-of-bias score. The review maps
heterogeneous literature and does not support a meta-analysis.

## 8. Conclusion

The literature supports a clear PhD problem: reliability automation is
technically diverse, operationally situated and insufficiently connected to
direct evidence about engineers' decisions and experience. The contribution
should therefore be a reproducible mixed-methods study that isolates a bounded
recovery intervention, measures technical events with a stable contract, and
studies human interaction separately rather than inferring it from telemetry.

Phase 1 is closed as an auditable review package for the accessible,
source-verifiable corpus. The authenticated-database limitation remains part of
the review's findings and must be disclosed in the proposal. If ACM, IEEE and a
multidisciplinary index become accessible later, their exports should be added
as a documented search update rather than silently overwriting this close-out.

## References

The canonical bibliographic register remains in `docs/literature/references.bib`.
The locator register supplies the source route and claim-level location.

P01. Shahin, M., Babar, M. A., Zahedi, M. and Zhu, L. (2017). *Beyond
Continuous Delivery: An Empirical Investigation of Continuous Deployment
Challenges*. https://doi.org/10.1109/ESEM.2017.18

P02. Shahin, M., Zahedi, M., Babar, M. A. and Zhu, L. (2019). *An Empirical
Study of Architecting for Continuous Delivery and Deployment*.
https://doi.org/10.1007/s10664-018-9651-4

P04. Chen, J. et al. (2020). *How Incidental are the Incidents? Characterizing
and Prioritizing Incidents for Large-Scale Online Service Systems*.
https://doi.org/10.1145/3324884.3416624

P05. Lou, J.-G. et al. (2013). *Software Analytics for Incident Management of
Online Services: An Experience Report*. https://doi.org/10.1109/ASE.2013.6693105

P06. Meiklejohn, C. S. et al. (2021). *Service-Level Fault Injection Testing*.
https://doi.org/10.1145/3472883.3487005

P07. Al-Said Ahmad, A., Al-Qora’n, L. F. and Zayed, A. (2024). *Exploring the
Impact of Chaos Engineering with Various User Loads on Cloud-Native
Applications*. https://doi.org/10.1007/s00607-024-01292-z

P09. Owotogbe, J. et al. (2025/2026). *Chaos Engineering: A Multi-Vocal
Literature Review*. https://doi.org/10.1145/3777375

P10. Heorhiadi, V. et al. (2016). *Gremlin: Systematic Resilience Testing of
Microservices*. https://doi.org/10.1109/ICDCS.2016.11

P11. Chen, J. et al. (2019). *An Empirical Investigation of Incident Triage for
Online Service Systems*. https://doi.org/10.1109/ICSE-SEIP.2019.00020

P12. Chen, J. et al. (2019). *Continuous Incident Triage for Large-Scale Online
Service Systems*. https://doi.org/10.1109/ASE.2019.00042

P13. Brogi, A. et al. (2022). *Self-Healing Trans-Cloud Applications*.
https://doi.org/10.1007/s00607-021-00977-z

P14. Chen, Y. et al. (2024). *Automatic Root Cause Analysis via Large Language
Models for Cloud Incidents*. https://doi.org/10.1145/3627703.3629553

P15. Assad, M. et al. (2024). *Can My Microservice Tolerate an Unreliable
Database? Resilience Testing with Fault Injection and Visualization*.
https://doi.org/10.1145/3639478.3640021

P16. Jiang, Y. et al. (2024). *Xpert: Empowering Incident Management with Query
Recommendations via Large Language Models*. https://doi.org/10.1145/3597503.3639081

P17. Huang, J. et al. (2024). *FaultProfIT: Hierarchical Fault Profiling of
Incident Tickets in Large-Scale Cloud Systems*.
https://doi.org/10.1145/3639477.3639754

P18. Chen, Z. et al. (2021). *Graph-Based Incident Aggregation for Large-Scale
Online Service Systems*. https://doi.org/10.1109/ASE51524.2021.9678746

P19. Yang, T. et al. (2024). *MicroRes: Versatile Resilience Profiling in
Microservices via Degradation Dissemination Indexing*.
https://doi.org/10.1145/3650212.3652131

P20. Yu, S. et al. (2025). *A Systematic Literature Review on Fault Injection
Testing of Microservice Systems*. https://doi.org/10.1109/TSC.2025.3621564

P23. Sillito, J. and Kutomi, K. (2020). *Failures and Fixes: A Study of Software
System Incident Response*. https://doi.org/10.1109/ICSME46990.2020.00027

P24. Chan, C. and Cooper, B. (2020). *Debugging Incidents in Google's
Distributed Systems*. https://doi.org/10.1145/3397880

P26. Pope, A. and Sillito, J. (2024). *Learning From Lessons Learned:
Preliminary Findings From a Study of Learning From Failure*.
https://doi.org/10.1145/3641822.3641867

P27. Dakkak, A., Bosch, J. and Holmström Olsson, H. (2022). *Controlled
Continuous Deployment: A Case Study From The Telecommunications Domain*.
https://doi.org/10.1145/3529320.3529323
