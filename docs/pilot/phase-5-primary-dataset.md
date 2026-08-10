# Phase 5 primary processed dataset

## Status

Post-collection derivation only.

The immutable Phase 5 primary raw-corpus anchor is:

`b832c96c1dd3665f6025394447b35db58cd0e2a9`

The frozen batch identifier is:

`phase5-primary-16f9cefff0d6b017`

## Evidence boundary

The raw corpus contains 53 attempts:

- 50 planned primary attempts;
- 3 reserve attempts;
- 50 valid attempts;
- 3 preserved invalid attempts.

The invalid attempts are run orders 19, 21 and 22.

The reserve attempts are run orders 20, 22 and 23.

Exactly one valid resolving attempt is selected for each of the 50
planned schedule slots. Invalid attempts remain in the corpus index but
are never imputed or substituted outside the frozen reserve mechanism.

## Processed artifacts

Only these deterministic primary-pilot artifacts are versioned:

- `corpus-index.json`
- `observations.json`
- `provenance.json`
- `summary.json`

`corpus-index.json` inventories all 53 attempts and hashes the bytes
read directly from the immutable raw Git commit.

`observations.json` contains the 50 valid resolving observations in
ascending planned-slot order.

`provenance.json` binds the processed dataset to the immutable raw
corpus, derivation tooling and frozen measurement implementation.

`summary.json` contains structural collection counts only. It does not
contain substantive performance results.

## Measurement boundary

Primary elapsed durations retain the frozen
`phase-5-primary-timing-v1` contract and controller monotonic clock
semantics.

UTC timestamps remain audit metadata only.

There is no UTC fallback.

OpenTelemetry remains corroborative rather than the primary timing
source.

## Claim boundary

Generation of the processed dataset performs no inferential analysis,
hypothesis testing or generalized causal interpretation.

Substantive descriptive analysis begins only after the processed
dataset has been reproduced byte-for-byte and committed.