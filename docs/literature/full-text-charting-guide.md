# Full-text charting guide

Use this guide for records that survive title/abstract screening. The goal is
to make every substantive statement in the literature map traceable to a
specific page, section, table or figure.

## Evidence-status rules

| Status | Permitted use |
|---|---|
| `abstract_only` | Candidate identification and cautious scope mapping only |
| `full_text_checked` | Extraction of reported methods, systems, measures and limitations |
| `secondary_context_only` | Terminology, citation chaining and landscape context; not a primary finding |
| `excluded_non_empirical` | Exclusion register and citation chasing only |
| `uncertain` | Requires adjudication or further retrieval before synthesis |

Never upgrade a record because a search snippet, review article or publisher
abstract appears to support a detail that was not checked in the primary full
text.

## Required extraction fields

For every included primary study, record:

1. bibliographic identity, DOI and full-text location;
2. software system, architecture and domain;
3. deployment and operational context;
4. reliability-automation mechanism and intervention point;
5. fault or incident model;
6. empirical design and unit of analysis;
7. data source and collection procedure;
8. participants or operational subjects;
9. technical outcomes and exact metric definitions;
10. engineering-practice or human-factor constructs and how they were measured;
11. reproducibility information, including versions, workload and reset;
12. findings stated conservatively and linked to the source location;
13. limitations and threats to validity; and
14. relevance to RQ-S1, RQ-S2 and RQ-S3.

Use `not_reported` where the paper does not provide a field. Do not infer a
participant population from an author biography or a system user population.

## Claim discipline

The claim register should contain one row for every claim that may appear in
the proposal or final review. A claim is ready for synthesis only when:

- the source is primary or explicitly labelled secondary;
- the full-text status is recorded;
- the extraction location is recorded;
- the claim distinguishes reported observation from the reviewer's inference;
- the study limitation is attached; and
- the wording does not exceed the design.

For example, a fault-injection study may support that a system was tested under
a defined delay condition. It does not automatically support that a general
automation strategy improves reliability, that the result transfers to
OrderFlow, or that engineers experienced a particular workload.

## Human-evidence boundary

Classify evidence separately as:

- direct participant/observational evidence;
- operational human-work evidence such as incident records or interviews;
- system telemetry;
- proxy or inferred human evidence; or
- no human evidence reported.

System telemetry must not be charted as workload, trust, understanding or
decision rationale unless the source collected and analysed those constructs
directly.
