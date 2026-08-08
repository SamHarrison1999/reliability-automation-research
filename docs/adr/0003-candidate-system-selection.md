# ADR 0003: Carry OrderFlow into the Phase 2 fit probe

- **Status:** Supported by local fit probe; final empirical-object acceptance remains open
- **Date:** 2026-08-08

## Context

The study requires a small system that exposes state, service dependencies, deployment changes and user-visible failure effects while remaining resettable and explainable. The original proposal names a transactional service system, but the domain and topology must be justified rather than assumed.

## Options considered

| Option | Evidence | Advantages | Risks/limitations |
|---|---|---|---|
| Purpose-built OrderFlow benchmark | Phase 0 design and Phase 2 criteria | Maximum control over state, faults, workload, versions and participant-facing tasks | Purpose-built domain may have limited external validity; implementation effort is non-trivial |
| Adapted open-source microservice benchmark | Phase 2 candidate comparison | Existing behaviour may improve ecological relevance and reduce initial build effort | Upstream assumptions, version drift and inherited complexity may confound the intervention |
| Single-service reference application | Phase 2 candidate comparison | Low cost, simple reset and strong control | Does not expose enough distributed dependency or deployment behaviour for the full research direction |

## Decision

Carry **OrderFlow** as the primary candidate into the fit probe. The candidate should initially contain only the smallest service and dependency boundaries needed to test the research design. It is not accepted as the final empirical object until the fit-probe validation criteria pass.

## Validation

- Define a minimal service map and state-reset contract.
- Run a fixed synthetic workload with no fault.
- Inject one service-termination and one dependency-latency/failure scenario.
- Verify that the scenario, service state, request outcomes and recovery events are distinguishable in raw records.
- Repeat from a clean reset and document resource use and contamination risks.
- Compare the result with the adapted-open-source alternative before Phase 2 closure.

## Consequences

The design prioritises experimental control and clear interpretation. Results from the eventual benchmark must not be presented as universal evidence about production systems. Real payments, personal data and production traffic remain excluded.

## Fit-probe result

The local OrderFlow slice passed the reset, workload, service-termination, dependency-latency, telemetry-contract and repeatability checks. This supports carrying OrderFlow into the next design stage. The probe did not compare the adapted open-source alternative and therefore does not resolve the external-validity trade-off.
