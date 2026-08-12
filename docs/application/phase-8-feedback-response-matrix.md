# Phase 8 feedback-response matrix

## Source

Earlier proposal feedback from Dr Chris Douce is treated as a design input.

No statement in this document implies that Dr Douce has agreed to supervise the
project.

| Feedback | Phase 8 response | Evidence |
|---|---|---|
| Too many research questions | Freeze two connected RQs | `phase-8-rq-contribution-freeze.md` |
| Software focus unclear | Name OrderFlow and its `order-api`/`inventory` slice explicitly | Phase 2-5 design and implementation |
| Selection/gathering/construction unclear | Explain that OrderFlow is purpose-built and selected against explicit experimental criteria | Phase 2 candidate-system ADRs |
| Empirical data unclear | Name structured technical events/workload/provenance and direct participant responses | Phase 3-6 protocols |
| Software domain influences practices | Define the transactional-service domain and treat benchmark simplicity as an external-validity limitation | Phase 8 proposal |
| Human/software-engineering dimension should be stronger | Use direct diagnosis/recovery/escalation evidence in a separately ethics-reviewed participant study | Phase 6 |
| Candidate suitability should be explicit | Add a dedicated OU suitability section | Phase 8 proposal |

## Additional correction from the original proposal

The application no longer promises simultaneous investigation of:

- rollback;
- progressive/canary deployment;
- monitoring-triggered recovery;
- service crashes;
- network latency;
- resource exhaustion;
- configuration failure; and
- multiple human constructs

as if they are all one initial experiment.

The doctoral programme may extend the design, but the core empirical boundary
is intentionally narrower.
