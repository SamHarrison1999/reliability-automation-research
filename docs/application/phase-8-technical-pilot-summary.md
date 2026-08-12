# Phase 8 technical-pilot summary for application support

## Purpose

Provide an application-facing account of Phase 5 without overstating the pilot.

## Execution

The frozen pilot contained:

- 50 planned resolving schedule slots;
- 53 preserved execution attempts;
- 50 valid resolving observations;
- three invalid attempts retained;
- five balanced cells;
- ten valid observations per cell.

## Dependency-latency observations

Descriptively:

- automated recovery had lower recovery time in 9 of 10 matched pairs;
- the paired mean automated-minus-manual recovery-time difference was
  approximately -20 ms;
- failure impact was zero in all valid observations.

The shared detector also varied between paired runs.

The result therefore does not justify attributing the entire observed timing
difference solely to the recovery initiator.

## Service-termination observations

Descriptively:

- aggregate automated recovery time was lower;
- five matched pairs favoured automated recovery;
- five matched pairs favoured manual recovery;
- failure impact was one failed-impact unit under the declared design in both
  recovery conditions;
- three invalid attempts occurred in this scenario family and were preserved.

There is no consistent paired directional recovery-time advantage.

## Recovery

All 40 valid fault observations met the frozen recovery-success criterion.

## Application interpretation

The pilot supports:

- feasibility;
- reproducible collection;
- metric derivation;
- matched-condition execution;
- the need for fault-specific interpretation.

It does not support:

- universal automation superiority;
- production readiness;
- confirmatory significance claims;
- human-effect claims.

## Value to the PhD application

The pilot demonstrates that the proposed technical method is executable and
provides concrete evidence for refining the doctoral design.

Its strongest contribution to the application is methodological credibility,
not a headline effect result.
