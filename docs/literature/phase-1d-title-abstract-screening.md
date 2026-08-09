# Phase 1D — title-and-abstract screening

**Project:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments  
**Execution date:** 2026-08-09  
**Branch intended for:** `research/phase-1-literature-evidence`  
**Stage status:** pilot and batch title-and-abstract screening completed for the deduplicated provisional queue; full-text eligibility and charting remain outstanding

## 1. Scope of this stage

This stage applies the eligibility rules in `docs/literature/phase-1-review-protocol.md` to the deduplicated source queue produced by Phase 1C. It is a title-and-abstract decision, not a full-text eligibility decision. An `include` decision means that the record should proceed to full-text assessment; it does not mean that the study is finally included in the review synthesis.

The authenticated ACM Digital Library, IEEE Xplore and Scopus/Web of Science exports are still unavailable in this workspace. Therefore, the records screened here are the currently deduplicated seed and supplementary candidates. No database-level coverage or final PRISMA total is claimed.

## 2. Pilot procedure

The first 20 canonical records, P01–P20, were treated as the required pilot set. The pilot used the following operational rules:

- include primary empirical studies that examine reliability-oriented automation, fault/incident handling, resilience testing or relevant engineering practice in the stated context;
- include systematic, mapping or multivocal reviews for citation chaining and landscape context, while retaining their secondary status;
- exclude conceptual or framework-only records where no empirical evaluation is evident from the title/abstract-level material;
- exclude records with no reliability, failure, incident, recovery, resilience, deployment or relevant human-practice connection; and
- do not infer direct workload, trust, situation awareness or decision-quality evidence from operational telemetry or tool deployment alone.

The pilot produced 19 includes and one exclusion (P08). No change to the eligibility criteria was required. The same rules were then applied to P22–P27. P21 was not screened as a separate record because Phase 1C mapped it to the canonical duplicate P09.

## 3. Screening outcome

The deduplicated queue contains 26 canonical records: P01–P20 and P22–P27. Twenty-four proceed to full-text assessment. P08 and P25 are excluded at title-and-abstract stage. P25 is retained in the metadata and citation-chaining audit trail as contextual material, but is not treated as primary empirical evidence.

The included queue contains:

- primary technical and operational studies;
- direct human/practice studies involving incident response or learning from failure; and
- secondary reviews retained for citation chaining and taxonomy context.

This stage does not yet establish which of the 24 records meet final full-text eligibility.

## 4. Metadata correction

The candidate register recorded an incorrect DOI for P25. The ACM Queue record identifies the DOI as `10.1145/3380774.3380778`; `10.1145/3379987` is not retained as the source identifier. The correction is recorded in `metadata-correction-log-batch-03.csv`. Because P25 is excluded at title-and-abstract stage, the correction does not promote it into the evidence matrix.

## 5. Files in this batch

- `screening-log-append-batch-03.csv` — title-and-abstract decisions for the complete deduplicated queue;
- `screening-pilot-batch-03.csv` — explicit pilot subset and rule outcome for P01–P20;
- `full-text-retrieval-queue-batch-03.csv` — retrieval and full-text assessment queue;
- `metadata-correction-log-batch-03.csv` — P25 DOI correction;
- `prisma-flow-batch-03.csv` — incremental bookkeeping for this stage; and
- this stage record.

## 6. Outstanding work

1. Obtain and record authenticated ACM, IEEE and Scopus/Web of Science exports.
2. Re-run deduplication over those exports and screen any newly identified records.
3. Retrieve the outstanding full texts in the queue.
4. Complete full-text eligibility decisions with one primary exclusion reason per excluded record.
5. Chart included studies, appraise design-specific quality and update the claim register.

No thematic synthesis or research-design change is made by this screening batch.
