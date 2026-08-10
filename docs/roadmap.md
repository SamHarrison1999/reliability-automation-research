# Phase-gated roadmap

This roadmap is a planning artifact. Completion of a phase requires the validation criteria to be met and the progress ledger to be updated. A later phase must not silently resolve an unresolved design decision from an earlier phase.

| Phase | Focus | Exit evidence |
|---|---|---|
| 0 | Research design and repository bootstrap | Questions, variables, evidence sources, scope, boundaries and repository validation are documented. |
| 1 | Scoping review and literature map | Search protocol, inclusion/exclusion criteria and evidence matrix are populated and reproducible. |
| 2 | Software-system and technology selection | Candidate systems and tools are compared against research criteria; ADRs record decisions. |
| 3 | Fault model, metrics and experiment protocol | Bounded fault catalogue, condition comparison, metric operationalisations, trial/reset procedure and validity risks are reviewed; protocol-supporting dry-run passes. |
| 4 | Reproducible technical prototype | The smallest benchmark system can be reset, deployed and observed reproducibly. |
| 5 | Experiment harness and technical pilot | Repeated technical runs produce validated raw records and analysis from raw data. |
| 6 | Human-participant protocol and ethics | Recruitment, tasks, consent, data handling and analysis plans are approved through the relevant process. |
| 7 | Participant feasibility study | Feasibility data is collected under the approved protocol; no claims exceed the sample and design. |
| 8 | Proposal revision and supervisor engagement | OU-length proposal, supporting dossier and supervisor-facing materials reflect the evidence and limitations. |

## Current gate

Phase 4 is complete. Two fresh full-telemetry reproducibility runs at
commit `207337f481f81e34d99bb9682ee2a642709e1fe4` passed all 16 declared
validity checks, reproduced the committed configuration/image invariants with
independent run IDs, and the repository-wide close-out quality gate passed.

The next gate is Phase 5: experiment harness and technical pilot. Phase 5
execution has not started. No reliability-effect, human-participant or
production-readiness claim is authorised by the Phase 4 evidence.
