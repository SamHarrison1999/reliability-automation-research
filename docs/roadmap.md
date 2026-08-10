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

Phase 5 is complete.

The frozen technical pilot resolved all 50 planned schedule slots using
53 preserved attempts: 50 primary attempts and three reserve attempts.
The resulting 50 valid observations are balanced across five design
cells and have been processed and analysed through deterministic,
byte-for-byte reproduced tooling.

The immutable primary descriptive-result anchor is:

`76396710e96088f79323039ae3a91aa3e53732c0`

The Phase 5 exit criterion is satisfied:

> Repeated technical runs produce validated raw records and analysis
> from raw data.

The next gate is Phase 6: human-participant protocol and ethics.

Phase 5 authorises bounded descriptive technical-pilot findings only.
It does not authorise statistical-significance, production-readiness,
human-effect or universal causal claims. Participant-derived evidence
must remain separate and requires the relevant ethics process.
