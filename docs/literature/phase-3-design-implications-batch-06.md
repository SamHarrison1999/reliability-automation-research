# Phase 3 design implications from the provisional Phase 1 synthesis

**Status:** Design input only; not an approval to implement or collect participant data

## Supported boundary

The evidence supports a bounded comparison of recovery-initiation strategies,
not a broad comparison of reliability automation as a whole. The provisional
technical boundary remains:

- standardised manual recovery;
- rule-based automated recovery;
- fixed workload, software version, fault scenario, detection rule and reset;
- technical event capture for detection, recovery and failure impact; and
- separate human/practice evidence if and when an approved participant study is
  undertaken.

The literature does not justify adding a second major intervention such as
canary deployment, platform-level chaos tooling or autonomous diagnosis to the
first comparison.

## Trial and event requirements

Every trial should carry an immutable manifest identifying the scenario,
condition, application version, workload seed, fault start, detection rule,
recovery initiation and reset result. The event contract should distinguish:

1. fault injection or fault onset;
2. detection observation;
3. recovery decision or initiation;
4. recovery action completion;
5. service/application recovery;
6. failure-impact interval; and
7. exclusion or contamination reason.

This separation is required because the literature uses detection, triage,
diagnosis, mitigation and recovery inconsistently. A single end-to-end time
would conceal the mechanism being compared.

## Human/practice requirements

Technical telemetry must not be labelled as workload, trust, understanding or
decision quality. If the PhD retains a human-practice question, the study will
need a separate protocol specifying participant eligibility, task instructions,
measures, interview or think-aloud boundaries, data minimisation, consent and
ethics approval. The technical trial can provide the task context; it cannot
substitute for the human evidence.

Potential constructs should be selected after reviewing validated instruments
and the supervisor's methodological advice. The current literature map only
justifies keeping the constructs visible; it does not select an instrument or
make a human-effect prediction.

## Reproducibility requirements

The proposed experiment should compensate for limitations visible in the
industrial literature by publishing or preserving, subject to ethics and
security constraints:

- trial manifests and scenario definitions;
- software and configuration versions;
- workload and fault seeds;
- raw technical event records;
- metric derivation code;
- reset and exclusion logs; and
- a provenance link from each summary value to its source event records.

These requirements are design safeguards, not findings from the literature.

## Technology-selection implication

The evidence supports the existing provisional OrderFlow fit-probe direction
only as a feasible bounded test system. It does not prove that OrderFlow is the
most representative or generally superior experimental system. Phase 2
technology decisions must still be accepted against the explicit selection
criteria after the evidence and Phase 3 requirements are reviewed together.
