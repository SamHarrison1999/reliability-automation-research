# Phase 3 design review against the Phase 1 evidence map

**Status:** Completed as a design check

**Date:** 2026-08-09

**Evidence basis:** Accessible and source-verifiable Phase 1 evidence map and design-implications record. The Phase 1 authenticated-database limitation remains in force and is not silently treated as resolved.

## Review outcome

The Phase 1 synthesis supports a bounded technical comparison of recovery initiation, but it does not support a broad claim about reliability automation or a claim that technical telemetry measures developer practice. The Phase 3 design has therefore been checked against the following implications:

| Phase 1 implication | Phase 3 response | Design location |
|---|---|---|
| Detection, triage, diagnosis, mitigation and recovery are distinct stages | The event contract separates fault injection, detection, recovery decision, recovery completion, post-recovery verification and cleanup | `docs/metrics/technical-metrics.md`; trial manifest event contract |
| Fault-injection studies require explicit fault, workload, execution and reset definitions | Each scenario declares its target, trigger, exposure, reversion, workload, expected signal and reset requirements | `docs/fault-model/phase-3-fault-model.md`; trial manifest |
| A first comparison should vary one major intervention dimension | Manual and automated conditions use the same fault, workload, detection rule, recovery action, versions and reset; only the initiator changes | ADR 0007; `docs/protocols/phase-3-technical-experiment.md` |
| Self-healing evidence is technically useful but context-bound | The design measures detection, recovery initiation, recovery completion and service recovery separately and limits inference to the OrderFlow pilot | ADR 0007; technical metric catalogue |
| Direct human evidence about workload, trust, understanding and decision-making is sparse | These constructs are specified separately and are not collected or inferred in the technical trial | `docs/metrics/developer-practice-metrics.md` |
| Reproducibility requires manifests, versions, raw records, reset logs and derivation provenance | The locked manifest requires trial identity, hashes, versions, event fields, validity checks and raw-bundle retention | Trial-manifest contract; technical protocol |
| The evidence is heterogeneous and does not justify a pooled effect estimate | The analysis is condition-by-scenario, reports individual trials and medians/IQRs, and does not pool no-fault and fault scenarios | Trial manifest; technical metrics |

## Changes required by the review

The review resulted in these design locks:

1. The first technical comparison is limited to service termination and dependency latency, with no-fault as a quality-control block.
2. The primary outcomes are `detection_latency_ms`, `recovery_time_ms` and `failure_impact_rate`.
3. Every fault trial requires explicit `fault_detected`, condition-labelled `recovery_started`, `recovery_completed`, `post_recovery_check`, cleanup and validity events.
4. The trial allocation is 10 valid trials per fault-condition cell and 10 no-fault controls, with two reserve slots per cell.
5. Developer-practice measures remain provisional and are reserved for a separate ethics-approved participant protocol.

## Remaining evidence limitation

This design check does not upgrade the Phase 1 review to a fully database-comprehensive review. ACM Digital Library, IEEE Xplore and Scopus/Web of Science authenticated exports remain outstanding and are a later literature-update task.
