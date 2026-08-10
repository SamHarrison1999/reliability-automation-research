# Phase 5 primary descriptive analysis

## Purpose

This analysis consumes only the immutable Phase 5 primary processed
dataset anchored at:

`be3119d44842a8b737a86e0f40dca37b3aa4dbf7`

The analysis is deterministic and descriptive.

## Primary outcomes

The three primary metrics are:

- detection latency;
- recovery time;
- failure impact rate.

Detection latency is interpreted primarily as a shared-detector
fidelity and balance check because the manual and automated conditions
use the same detector.

Recovery time is the principal treatment-relevant technical timing
outcome.

Failure impact rate is a treatment-relevant technical impact outcome.

## Descriptive statistics

Observed numeric metrics are summarized using:

- sample count;
- mean;
- median;
- 25th percentile;
- 75th percentile;
- 95th percentile;
- minimum;
- maximum.

Percentiles use the Hyndman-Fan/R type-7 definition.

For each fault scenario, manual and automated observations are also
paired by frozen repetition number. Paired differences are defined as:

`automated - manual`

The analysis reports descriptive summaries and direction counts for
these paired differences.

## Invalid and reserve attempts

Invalid and reserve attempts remain part of the execution-stability
record but are not included in valid metric summaries.

The processed dataset already resolves exactly one valid observation
for each of the 50 planned slots.

Execution instability is therefore reported separately rather than
being imputed into timing or impact values.

## Claim boundary

The analysis performs no:

- p-values;
- null-hypothesis significance testing;
- statistical-significance claims;
- powered-study claims;
- human or developer-effect analysis;
- production-readiness claims;
- universal causal claims.

Results describe only the behaviour observed in this controlled
technical pilot.