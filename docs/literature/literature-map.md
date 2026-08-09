# Provisional literature map

**Status:** Seed-map synthesis; not a completed scoping review  
**Date:** 2026-08-09

## What this map can support

The current repository contains nine seed records. They are useful for testing
the extraction schema, identifying terminology and selecting citation-chasing
seeds. They cannot provide database coverage or establish the final pattern of
evidence because the named searches and most full-text checks remain pending.

The seed records currently cover four broad evidence families:

| Evidence family | Seed examples | What to extract next |
|---|---|---|
| Continuous-delivery practice and adoption | P01, P02 | Intervention boundaries, practitioner evidence, deployment/reliability outcomes |
| Online-service incident and operational analytics | P04, P05 | Data provenance, incident definitions, detection/triage/recovery measures |
| Fault injection and chaos/resilience experiments | P03, P06, P07 | Fault model, workload, reset, timing, outcome definitions and reproducibility |
| Self-healing and review-level framing | P08, P09 | Separate empirical evaluations from conceptual or secondary evidence |

## Working gaps

The seed map currently leaves the following questions open:

- how often studies compare recovery strategies under matched faults and
  workloads;
- whether detection, recovery and failure-impact metrics are operationalised
  consistently;
- how frequently software-engineer diagnosis, escalation, trust or workload is
  measured directly rather than inferred from telemetry;
- how reproducible the reported systems, faults, versions and reset procedures
  are; and
- whether a small transactional benchmark can represent the mechanisms without
  importing uncontrolled production complexity.

These are review tasks, not findings. They must be updated only after the
search log, full-text chart and claim register provide supporting evidence.

## Relevance to the PhD design

The seed map supports retaining a provisional two-stream design:

1. a technical stream measuring system events under controlled faults and
   recovery conditions; and
2. a separate human/engineering-practice stream requiring direct evidence and
   ethics review.

This separation is a repository design constraint, not a conclusion that the
external literature has already been fully reviewed. The map must be revised
after the completed search and charting work.
