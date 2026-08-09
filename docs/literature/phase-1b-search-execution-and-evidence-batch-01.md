# Phase 1B — supplementary search execution and evidence batch 01

**Project:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments  
**Execution date:** 2026-08-09  
**Branch intended for:** `research/phase-1-literature-evidence`  
**Stage status:** supplementary discovery and first evidence-verification batch completed; primary database execution and the full review remain outstanding

## 1. What was executed

Five targeted web-assisted discovery searches were run across academic publisher,
author and repository pages. The exact search groups are recorded in
`supplementary-search-log.csv`. The searches were used to identify candidate
records and locate lawful publisher or author copies for verification.

This is not being counted as ACM Digital Library, IEEE Xplore, Scopus or Web of
Science coverage. The public search interface does not provide a stable,
reproducible database count or export hash, and the execution time was not
captured. Those limitations are recorded rather than hidden.

## 2. Candidate handling

Thirteen additional records were registered in `candidate-source-register.csv`.
Ten have a full text or author-hosted version that was inspected at a first-pass
level. Three are secondary or metadata/abstract candidates and remain outside
the substantive evidence synthesis until fully verified. The existing nine seed
records remain unchanged and are still subject to the original screening and
charting rules.

The new batch deliberately separates:

- technical automation evidence: fault injection, resilience profiling,
  self-healing, incident aggregation, fault profiling and RCA;
- operational-work evidence: incident triage and query recommendation, which
  reveal workflow and decision-support context but do not automatically measure
  human cognition or workload; and
- secondary evidence: systematic or multivocal reviews used for taxonomy and
  citation chasing only.

## 3. First-pass evidence observations

### Technical reliability and recovery

The verified batch contains controlled or operational evaluations of fault
injection, resilience profiling and self-healing. The studies show that the
intervention point matters: Gremlin and Filibuster exercise service-level or
application-level failure behaviour before or around deployment; MicroRes
profiles degradation propagation; and Brogi et al. evaluate automated recovery
of application and cloud-service components. These are complementary evidence
types, not interchangeable estimates of one reliability effect.

The strongest immediate design implication is to separate at least four
technical outcomes in the proposed experiment: detection latency, diagnosis
quality/accuracy, recovery latency, and recovery success/containment. A single
MTTR value would collapse distinct stages and make comparisons difficult.

### Incident diagnosis and operational work

The Microsoft and Huawei studies provide substantial operational-artefact
evidence about triage, aggregation, query use, fault profiling and RCA. The
incident-triage studies show that assignment and diagnosis are iterative and can
involve reassignment and discussion. RCACopilot, Xpert, FaultProfIT and GRLIA
evaluate automation against incident data or production deployment, but their
reported outcomes are primarily model or workflow outcomes.

These records should therefore be coded as `observed_operational_work` or
`decision_support`, not as direct participant evidence. They do not justify the
claim that automation reduced engineer workload, improved situation awareness,
increased trust, or improved decision quality unless a source reports a direct
measure of that construct.

### Human-practice gap

The targeted human-practice searches did not yet produce a verified primary
study that directly compares reliability-automation conditions using validated
workload, trust, situation-awareness or decision-quality measures in software
operations. This is a provisional gap observation, not a final claim of
absence: the authenticated database searches, citation chasing and full-text
screening still need to be completed.

## 4. Provisional design implications

The evidence batch supports the following requirements for the later empirical
design, subject to revision after the complete search:

1. Treat fault injection as a scenario-generation or resilience-evaluation
   technique, not automatically as the independent variable.
2. Define the automation intervention explicitly: detection only, diagnosis
   support, automated mitigation, rollback, or end-to-end recovery.
3. Keep technical telemetry separate from human measures. Technical logs can
   timestamp alerts, diagnoses, actions and service restoration; they cannot by
   themselves establish workload, trust, understanding or decision rationale.
4. Include fault and workload conditions explicitly because cloud-native studies
   show that delay and user load can expose nonlinear availability or
   dependability behaviour.
5. Record reproducibility details such as fault injection point, scenario seed,
   reset procedure, service versions, telemetry configuration and raw-event
   schema.
6. Avoid treating production deployment of an automation tool as a causal
   evaluation unless the source includes a valid comparison or longitudinal
   design that supports that inference.

## 5. Outstanding work

- Execute and export T, H and M in ACM Digital Library and IEEE Xplore.
- Select and execute Scopus or Web of Science, recording the exact platform,
  indexes and count.
- Preserve original exports and hashes outside the public repository where
  licensing requires it.
- Deduplicate database records against the nine seed records and this candidate
  register.
- Run the 20-record title/abstract pilot and record any protocol amendment.
- Retrieve and chart the remaining full texts.
- Complete design-specific appraisal, claim-register updates, citation chasing,
  synthesis and PRISMA flow counts.

## 6. Evidence boundary

This document does not claim that the literature review is complete. It does
not present web-search result ordering as database coverage, and it does not
claim participant, workload or causal reliability evidence from the prototype,
fit probes or telemetry.
