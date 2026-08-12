# Reliability Automation and Software Engineering Practice

Research repository for the provisional PhD project:

> An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

Phase 8 application preparation is complete and internally validated. The
repository now contains a current 600-1000-word OU proposal, evidence/claim
traceability, methods and pilot-support dossiers, supervisor-facing materials
and an adversarial application review. Phase 7 participant execution remains
blocked pending the required ethics/institutional approvals, and the full Phase
1 scoping-review execution remains an explicit carry-forward item. Phase 8
completion does not imply that an application has been submitted, a supervisor
has agreed to supervise or admission has been offered.

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
- Manual recovery is the baseline. Rule-based automated recovery is the first comparison condition; automated rollback remains deferred until a faulty-deployment scenario is specified.
- Progressive/canary deployment is deferred until the literature review and initial pilot show that it can be added without making the design unmanageably broad.
- The system will not use real payments, personal data or production systems.
- The Phase 2 fit probe uses only synthetic orders and a minimal order/inventory slice.
- Human-participant work requires a separate protocol, recruitment plan and ethics approval. This repository does not imply that approval has been obtained.

## Repository map

```text
docs/
  proposal/source/       Original proposal supplied for traceability
  research-design/       Phase-gated research decisions
  fault-model/           Bounded fault taxonomy and scenario catalogue
  metrics/               Technical metric operationalisations
  literature/            Review protocol and evidence matrix
  protocols/             Experiment and participant protocols
  ethics/                Ethics planning only; no approval implied
  diagrams/              Architecture and experimental-design diagrams
  adr/                   Architecture/research decision records
  templates/             Reusable research documentation templates
system/                  Minimal versioned OrderFlow research prototype
infrastructure/          Fit-probe history plus reproducible Phase 4/5 deployment contracts
experiments/              Versioned fit-probe, Phase 3 protocol, Phase 4 validation and Phase 5 pilot harnesses
ansible/                  Deferred environment-automation boundary and validation scaffold
observability/            Optional OpenTelemetry compatibility-probe configuration
data/                    Raw/processed/external data boundaries
analysis/                 Deterministic Phase 5 metric, dataset and descriptive-analysis tooling
scripts/                  Bootstrap, quality, compliance and repository validation scripts
tests/                    Harness and service unit tests; later software tests
results/                  Versioned technical evidence bundles plus generated outputs
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

The Phase 2 technology close-out is recorded in [`docs/research-design/phase-2.md`](docs/research-design/phase-2.md) and [`docs/adr/0012-phase-2-technology-decision-closeout.md`](docs/adr/0012-phase-2-technology-decision-closeout.md). The fit-probe evidence is [`docs/fit-probe/phase-2-fit-probe-results.md`](docs/fit-probe/phase-2-fit-probe-results.md), and the real SDK/Collector result is [`docs/observability/phase-2-otel-compatibility-result.md`](docs/observability/phase-2-otel-compatibility-result.md). The Phase 3 package is [`docs/research-design/phase-3.md`](docs/research-design/phase-3.md), with the fault model in [`docs/fault-model/phase-3-fault-model.md`](docs/fault-model/phase-3-fault-model.md), metrics in [`docs/metrics/technical-metrics.md`](docs/metrics/technical-metrics.md) and the technical protocol in [`docs/protocols/phase-3-technical-experiment.md`](docs/protocols/phase-3-technical-experiment.md). Phase 4 is defined in [`docs/research-design/phase-4.md`](docs/research-design/phase-4.md), with inspected reproducibility evidence summarised in [`docs/reproducibility/phase-4-validation.md`](docs/reproducibility/phase-4-validation.md). See [`docs/roadmap.md`](docs/roadmap.md) and [`docs/progress-ledger.md`](docs/progress-ledger.md) for the current gate.

The Phase 5 technical pilot close-out is recorded in
[`docs/pilot/phase-5-closeout.md`](docs/pilot/phase-5-closeout.md), with
the committed descriptive findings in
[`docs/pilot/phase-5-primary-results.md`](docs/pilot/phase-5-primary-results.md).
The deterministic processed-data and descriptive-analysis contracts are
documented in
[`docs/pilot/phase-5-primary-dataset.md`](docs/pilot/phase-5-primary-dataset.md)
and
[`docs/pilot/phase-5-primary-descriptive-analysis.md`](docs/pilot/phase-5-primary-descriptive-analysis.md).
Phase 6 remains a separate human-participant and ethics gate; Phase 5
technical telemetry is not participant evidence.

The Phase 6 protocol-ready package is recorded in
[`docs/research-design/phase-6.md`](docs/research-design/phase-6.md) and
[`docs/ethics/phase-6-closeout.md`](docs/ethics/phase-6-closeout.md).
The package is preparation for future institutional review only. It does not
record a favourable ethics opinion and does not authorise recruitment.

The Phase 8 application package is recorded in
[`docs/application/phase-8-ou-proposal-final.md`](docs/application/phase-8-ou-proposal-final.md)
and
[`docs/application/phase-8-closeout.md`](docs/application/phase-8-closeout.md).

The package is ready for external supervisor/application review. The current
OU application route and requirements must still be re-verified immediately
before submission.

## Engineering quality

Create the local quality environment and run the checks with:

```bash
bash scripts/bootstrap-quality.sh --with-infrastructure
bash scripts/run-quality-checks.sh --strict-infrastructure
```

The tool boundary and rationale are documented in
[`docs/engineering-quality.md`](docs/engineering-quality.md). CLOC produces a
disposable report under `tmp/quality`; OpenTelemetry is validated only for the
pinned small-trace compatibility path and is not treated as production
infrastructure.
