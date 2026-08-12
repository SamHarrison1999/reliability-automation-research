# Phase 8 application evidence audit

**Date:** 2026-08-12

## Purpose

Determine exactly which statements can be made in the revised PhD proposal
without converting preparation work, feasibility evidence or future study
plans into stronger claims than the evidence supports.

## Original proposal baseline

The retained source proposal is:

`docs/proposal/source/Sam_Harrison_PhD_Proposal.pdf`

The baseline proposal:

- used a broad reliability-automation/human-decision framing;
- contained multiple broad research questions;
- described the software generically as an e-commerce or API-based
  microservice application;
- named technologies before their empirical suitability had been validated;
- proposed several automation mechanisms and fault classes simultaneously;
- provided limited detail about recruitment and direct human evidence; and
- stated hypotheses before the intervention and measurement boundaries were
  sufficiently mature.

## Dr Chris Douce feedback carried into Phase 8

The revision must demonstrate that:

1. the research questions have been reduced and tightened;
2. the software being studied is explicitly identified;
3. the origin/selection/construction of that software is justified;
4. empirical-data sources and collection are explicit;
5. software-domain effects and external-validity limits are acknowledged; and
6. the human/software-engineering dimension is directly operationalised rather
   than inferred from telemetry.

## Completed preparation evidence

### Technical system

OrderFlow is now a purpose-built and explicitly selected transactional
benchmark rather than an unspecified example application.

The bounded technical slice uses:

- `order-api`;
- `inventory`;
- Docker/Kubernetes deployment;
- synthetic workload;
- deterministic fault boundaries;
- versioned recovery conditions; and
- structured technical evidence.

### Technical feasibility and pilot

Phase 4 established reproducible deployment/reset/observation of the bounded
system.

Phase 5 completed the frozen technical pilot.

Primary pilot facts that may be reported:

- 50 planned schedule slots;
- 53 preserved attempts;
- 50 valid resolving observations;
- three invalid attempts preserved rather than imputed;
- five balanced design cells with ten valid observations each.

These facts establish execution and measurement feasibility.

They do not establish:

- universal automation superiority;
- production readiness;
- general causal effects;
- statistical significance; or
- human effects.

Important provenance anchors remain:

- raw-corpus anchor:
  `b832c96c1dd3665f6025394447b35db58cd0e2a9`;
- processed-dataset anchor:
  `be3119d44842a8b737a86e0f40dca37b3aa4dbf7`;
- descriptive-result anchor:
  `76396710e96088f79323039ae3a91aa3e53732c0`.

### Human study

Phase 6 is protocol-ready.

It defines:

- participant population;
- recruitment;
- H-M/H-A conditions;
- four matched task variants;
- counterbalancing;
- human measures;
- workload and reliance measures;
- consent and withdrawal;
- risk/accessibility controls;
- data-management/privacy boundaries; and
- a descriptive feasibility-analysis plan.

Formal ethics approval has not been obtained.

No participant has been recruited.

No participant data exist.

## Application evidence hierarchy

Proposal statements should distinguish:

1. **completed empirical preparation** ? Phase 4/5 technical evidence;
2. **completed study design** ? Phase 6 participant protocol;
3. **planned doctoral work** ? broader literature synthesis, participant
   feasibility/main study and any extended technical comparison;
4. **external dependencies** ? ethics approval, participant recruitment and
   supervisor/institutional approval.

## Application claim rule

A proposal sentence must not silently move an item from a lower evidence state
to a higher one.

Examples:

- `The pilot demonstrated reproducible execution` is permitted.
- `The pilot proves automation improves reliability` is not permitted.
- `A participant study has been designed` is permitted.
- `Engineers responded better to automation` is not permitted because no
  participant observations exist.
