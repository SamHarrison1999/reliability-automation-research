# ADR 0009: Separate repository CI/CD from experiment execution

- **Status:** Accepted for Phase 2 close-out
- **Date:** 2026-08-09
- **Evidence:** `.github/workflows/quality.yml`, `scripts/run-quality-checks.sh`, `scripts/run-quality-checks.ps1`, Phase 2 fit-probe records

## Context

The project needs repeatable software validation and repeatable experiment
execution, but these are different methodological concerns. Making the
experiment depend on a hosted CI runner would make runner availability,
network state and CI scheduling part of the treatment and would make local
reproduction harder.

## Decision

Use the following boundary:

1. **GitHub Actions** is the repository CI/CD validation layer. It runs the
   pinned Python quality checks and infrastructure checks, including tests,
   typing, formatting, security, shell/YAML/Ansible validation and repository
   boundary checks.
2. The **portable experiment controller** is the execution interface for
   fit-probes and later technical trials. It must run from a declared commit
   and environment on a local workstation or an explicitly declared runner.
3. CI may validate the controller, manifests and analysis tooling, but CI
   success is not an experiment result and a CI runner is not an experimental
   condition.
4. Every technical run records the repository commit, manifest hashes,
   environment, target model and tool versions.

## Alternatives considered

| Alternative | Reason not selected |
|---|---|
| Run every experiment only inside GitHub Actions | Couples evidence to hosted-runner state and makes local reset/reproduction weaker |
| Use an undocumented local process | Cannot provide a reviewable, repeatable validation boundary |
| Use a vendor-specific deployment pipeline | Adds platform coupling before the research comparison is defined |

## Feasibility evidence

The repository workflow and cross-platform quality scripts provide the
validation boundary. The fit-probe controller has already produced repeatable
synthetic technical records in local-process and Docker Desktop Kubernetes
targets. These facts support feasibility of the separation; they do not show
that CI/CD automation improves reliability.

## Consequences and validation

The protocol must report the target environment separately from CI validation.
Before each technical pilot block, verify the commit, manifests, tool versions,
reset state and output location. If a run is executed by CI, its runner context
must be recorded and the result must not be pooled with another target without
a reviewed equivalence decision.

