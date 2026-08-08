# Reliability Automation and Software Engineering Practice

Research repository for the provisional PhD project:

> An Empirical Investigation of Reliability Automation and Human Decision-Making in Continuous Delivery Environments

This repository is currently in **Phase 1: scoping review and literature map**. It contains no experimental application and no empirical findings. The purpose of this stage is to make the research design, evidence boundaries and later implementation decisions explicit before application code is written.

## Research direction

The working design separates two evidence streams:

1. **Technical evidence** from controlled fault experiments: detection latency, recovery time, failure impact, failed requests, intervention counts and related system events.
2. **Human/engineering-practice evidence** from a separately designed participant study: diagnosis and recovery decisions, task outcomes, interaction logs, workload/trust measures and explanations of decisions.

Telemetry alone will not be treated as evidence of cognitive workload, understanding or the reasons for an engineer's decision.

## Provisional research questions

These questions are design hypotheses, not final questions. They will be refined through the literature review and pilot feasibility work.

**RQ1 - Technical reliability**

> Under controlled fault scenarios in a reproducible transactional service system, how do different reliability-automation strategies affect detection time, recovery time, failure impact and manual intervention?

**RQ2 - Engineering practice**

> How do different reliability-automation strategies influence software engineers' diagnosis, recovery and escalation decisions during structured continuous-delivery tasks?

Reproducibility is currently a methodological objective supporting both questions, rather than a third broad empirical question.

## Current scope boundary

- The candidate empirical object is a small, purpose-built transactional benchmark system, provisionally called **OrderFlow**.
- The first technical pilot should use a fixed workload, deterministic fault scenarios and at least two automation conditions.
- Manual recovery is the baseline. Automated rollback and monitoring-triggered recovery are candidate comparison conditions.
- Progressive/canary deployment is deferred until the literature review and initial pilot show that it can be added without making the design unmanageably broad.
- The system will not use real payments, personal data or production systems.
- Human-participant work requires a separate protocol, recruitment plan and ethics approval. This repository does not imply that approval has been obtained.

## Repository map

```text
docs/
  proposal/source/       Original proposal supplied for traceability
  research-design/       Phase-gated research decisions
  literature/            Review protocol and evidence matrix
  protocols/             Experiment and participant protocols
  ethics/                Ethics planning only; no approval implied
  diagrams/              Architecture and experimental-design diagrams
  adr/                   Architecture/research decision records
  templates/             Reusable research documentation templates
system/                  Reserved for the benchmark application (later phase)
infrastructure/          Reserved for reproducible environments (later phase)
experiments/              Scenarios, manifests and harness (later phase)
data/                    Raw/processed/external data boundaries
analysis/                 Reproducible analysis code (later phase)
scripts/                  Bootstrap and repository validation scripts
tests/                    Repository and later software tests
results/                  Generated outputs; not source data or findings
```

## Start from an empty directory

From the repository root:

```bash
bash scripts/bootstrap.sh --proposal /path/to/Sam_Harrison_PhD_Proposal.pdf
bash scripts/verify-repository.sh
```

On Windows PowerShell:

```powershell
.\scripts\bootstrap.ps1 -ProposalPath C:\path\to\Sam_Harrison_PhD_Proposal.pdf
.\scripts\verify-repository.ps1
```

The bootstrap scripts are intentionally idempotent and do not overwrite existing files. They create the Phase 0 structure and initialise Git only when the target directory is not already a Git repository.

## Working agreement

Work is phase-gated. Each phase must record its objective, rationale, deliverables, implementation tasks, validation criteria and threats to validity. Do not begin application implementation until the research design and technology choices justify it.

Phase 1 is currently in progress. See the [`Phase 1 review protocol`](docs/literature/phase-1-review-protocol.md), [`docs/roadmap.md`](docs/roadmap.md) and [`docs/progress-ledger.md`](docs/progress-ledger.md).
