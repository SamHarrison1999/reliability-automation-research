# Phase 1 protocol audit and research-question refinement

**Project:** PhD Preparation – Reliability Automation and Software Engineering Practice
**Working title:** *An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments*
**Audit date:** 2026-08-09
**Stage:** Protocol finalisation; database searches have not yet been executed

## 1. Audit conclusion

The existing Phase 1 package is a sound starting point, but it is not a completed
review. It already establishes:

- a scoping-review/evidence-mapping design;
- a PCC-based scope;
- explicit primary, secondary and non-empirical evidence labels;
- separate search, screening, evidence-charting and claim-provenance records;
- a nine-record seed map whose abstract-only records are not treated as verified
  findings; and
- a firm boundary between technical telemetry and direct evidence of workload,
  cognition, trust or decision quality.

The package still lacks executed database searches, deduplication, a completed
pilot screen, full-text assessment, design-sensitive quality appraisal and a
verified synthesis. The protocol must therefore remain prospective.

## 2. Decisions made in this audit

| Decision | Resolution | Reason |
|---|---|---|
| Review type | Retain a scoping review with systematic evidence mapping | The anticipated studies differ substantially in intervention, setting, method and outcome; a pooled effect estimate is not yet defensible. |
| Reporting guidance | Use PRISMA-ScR for the review report and PRISMA-S for search reporting | PRISMA-ScR covers scoping-review reporting; PRISMA-S strengthens reproducibility of the search record. |
| Substantive PhD questions | Retain two connected questions: technical outcomes and engineering practice | This preserves a coherent thesis while preventing a long, disconnected question list. |
| Reproducibility | Retain as a methodological objective, not a third substantive effect question | Reproducibility concerns the validity of the study design and evidence chain. |
| Review questions | Use three linked review questions | The review needs to map mechanisms/outcomes, direct human evidence and methodological limitations separately. |
| Search architecture | Use three complementary search families | A single `continuous delivery AND reliability AND human factors` query would miss operational-human studies and methodology papers that use different terminology. |
| Time boundary | 2010 through the final search date, with backward citation chasing for earlier seminal work | The period covers modern continuous-delivery/cloud-native practice while allowing justified earlier conceptual sources to enter through citation chasing. |
| Language | English-language full text | This is feasible for a solo review, but creates language bias that must be reported. |
| Evidence types | Primary empirical studies drive findings; secondary reviews support mapping/citation chasing; non-peer-reviewed sources are contextual only | This prevents conceptual or practitioner claims from being counted as equivalent to primary empirical evidence. |
| Quality appraisal | Use design-sensitive domains and narrative judgements, not one universal numeric score | Experiments, observational studies, qualitative studies, mixed-methods studies and reviews have different validity risks. |
| Human-evidence boundary | Direct measures and observed work are charted separately from telemetry and inferred proxies | System telemetry cannot establish cognitive workload, trust, understanding or decision rationale. |
| AI-assisted review work | AI may assist record handling or drafting, but every inclusion, extraction and claim remains reviewer-verified and auditable | This preserves accountability and prevents unverified citations or source claims entering the synthesis. |

## 3. Provisional and refined PhD questions

| Status | Research question or objective | Literature strand | Key concepts | Evidence required | Potential measures | Relevance to proposed study | Known limitations or threats |
|---|---|---|---|---|---|---|---|
| Provisional RQ1 | Under controlled fault scenarios in a reproducible transactional service system, how do different reliability-automation strategies affect detection time, recovery time, failure impact and manual intervention? | Reliability mechanisms; technical outcomes | Automation strategy, controlled fault, detection, recovery, containment | Controlled or quasi-controlled technical comparisons; clearly defined fault/workload and comparator | Detection latency; recovery time; failed-request count/rate; failure-impact integral; recovery success; intervention count | Directly motivates the technical experimental stream | Benchmark realism, metric inconsistency, unequal conditions, contamination, small-run inference and limited transferability |
| **Refined PhD-RQ1** | **Under matched fault, workload and reset conditions, how do reliability-automation strategies affect failure detection, recovery performance, service impact and the need for external intervention in continuous-delivery environments?** | Reliability mechanisms; technical outcomes; reproducibility | Matched conditions, recovery initiation, recovery quality, service impact | Full-text empirical studies plus later controlled technical trials | Pre-specified detection latency; recovery time; recovery success; request failures; service-impact measure; external interventions | Preserves the intended comparison without prematurely fixing one platform or tool | Published studies may use non-equivalent definitions; a purpose-built benchmark may reduce ecological validity; later trials establish only bounded causal effects |
| Provisional RQ2 | How do different reliability-automation strategies influence software engineers' diagnosis, recovery and escalation decisions during structured continuous-delivery tasks? | Human and engineering decision-making | Diagnosis, recovery, escalation, workload, trust, understanding | Direct participant, observational, interview, survey or operational-work evidence | Diagnosis accuracy; action sequence; decision outcome; escalation; task time; validated workload/trust measures; qualitative explanations | Directly motivates a separate human-participant stream | Sampling and expertise effects, artificial tasks, learning/order effects, self-report bias, ethics and recruitment feasibility |
| **Refined PhD-RQ2** | **How, and under what operational conditions, do reliability-automation strategies influence software engineers' diagnosis, recovery and escalation decisions, perceived workload, and calibrated reliance on automation?** | Human and engineering decision-making | Decision process, workload, reliance, oversight, explanations, context | Direct human evidence; telemetry may provide task context but not measure cognition by itself | Decision accuracy/appropriateness; escalation choice; action sequence; time; validated workload scale; reliance/calibration measure; interviews or retrospective explanation | Defines constructs that require participant evidence and prevents telemetry-only claims | Construct validity, participant heterogeneity, observer effects, limited sample size, task realism and causal attribution |
| Provisional methodological objective | Develop and evaluate a reproducible experimental environment capable of producing trustworthy comparisons across repeated runs. | Reproducibility and methodology | Provenance, reset, repeatability, metric validity | Methods papers plus complete trial manifests and raw-to-derived evidence | Reset checks; event completeness; version/configuration hashes; missing-data and exclusion records | Governs both technical and later human streams | Reproducibility does not by itself provide external validity or prove reliability effects |
| **Refined methodological objective** | **Develop and evaluate an auditable mixed-methods experimental environment that links technical events to separately collected human evidence while preserving provenance, repeatability and construct validity.** | Reproducibility and methodology | Auditability, linkage, separation of evidence, construct validity | Methodological literature, dry-runs, protocol adherence and transparent evidence transformations | Manifest completeness; traceable event boundaries; reset/contamination checks; direct-source links for human constructs | Converts the literature-derived validity requirements into Phase 3–6 design constraints | A reproducible artificial task can still be unrepresentative; linkage can create privacy and analysis risks |

## 4. Final review questions

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

These review questions support the two substantive PhD questions; they do not
create three independent empirical studies.

## 5. Unresolved decisions before search execution

Only decisions that depend on the reviewer's actual access remain open:

1. Whether the multidisciplinary citation index will be Scopus, Web of Science,
   or both. The source and platform must be named exactly in the search log.
2. Whether a supervisor or second reviewer can independently check a sample of
   title/abstract decisions, full-text decisions and extracted records.
3. Whether the protocol will be registered publicly (for example, on OSF)
   before the first database search. If registered, the URL and version must be
   recorded without rewriting the earlier protocol history.

The absence of a second reviewer does not prevent execution, but it must be
reported as a limitation and partially mitigated through a decision-rule pilot,
duplicate self-checking of a sample after a time interval, and supervisor audit
where available.

## 6. Gate decision

The protocol and planned searches may proceed to platform smoke-testing. The
review must not proceed to synthesis until search execution, deduplication,
screening, full-text charting and quality appraisal have produced an auditable
evidence base.
