# Phase 5 primary technical-pilot results

## Status

Phase 5 primary collection and descriptive analysis are complete.

The immutable descriptive-result anchor is:

`76396710e96088f79323039ae3a91aa3e53732c0`

The deterministic descriptive artifact has SHA-256:

`547aff9a56dc3fa4dac09929f68c5d57248338af0f317cc7951bca0a0e5170ed`

The analysis scope is:

`phase-5-technical-pilot-descriptive-only`

No inferential statistics, p-values or statistical-significance claims
are made.

## Collection outcome

The frozen experiment scheduled 50 valid planned observations across
five balanced design cells.

Collection required 53 attempts:

- 50 primary attempts;
- 3 reserve attempts;
- 50 valid resolving observations;
- 3 preserved invalid attempts.

All 50 planned slots were resolved.

The invalid run orders were 19, 21 and 22. The reserve run orders were
20, 22 and 23.

Invalid attempts are retained as execution-stability evidence and are
not imputed into valid metric summaries.

## Dependency-latency scenario

The dependency-latency scenario produced a small but directionally
consistent difference in recovery time.

Manual recovery time:

- mean: 521.898160 ms;
- median: 520.476800 ms.

Automated recovery time:

- mean: 501.876500 ms;
- median: 498.711050 ms.

For paired repetitions, where the difference is defined as
`automated - manual`:

- mean difference: -20.021660 ms;
- median difference: -19.467500 ms;
- automated recovery was lower in 9 of 10 pairs;
- manual recovery was lower in 1 of 10 pairs.

This is descriptive pilot evidence only.

Detection latency was also lower in the automated condition in 8 of
10 paired observations. Detection latency uses the same detector in
both recovery conditions and is therefore interpreted as a detector
fidelity and balance measure rather than an automation treatment
effect.

Consequently, the recovery-time difference cannot be attributed
entirely to recovery initiation without accounting for the observed
detector timing variability.

Failure impact was zero in every dependency-latency observation under
both recovery conditions.

All 20 valid dependency-latency observations achieved functional
recovery.

## Service-termination scenario

Service termination displayed substantially greater timing variability.

Manual recovery time:

- mean: 6377.945970 ms;
- median: 3328.693350 ms.

Automated recovery time:

- mean: 5248.712380 ms;
- median: 2369.414600 ms.

For paired repetitions:

- mean automated-minus-manual difference: -1129.233590 ms;
- median difference: -457.645050 ms;
- automated recovery was lower in 5 of 10 pairs;
- manual recovery was lower in 5 of 10 pairs.

The lower aggregate automated recovery-time summaries therefore do not
constitute a consistent paired directional advantage.

Detection timing was also highly variable in this scenario. Because
the detector is shared between conditions, these differences are not
interpreted as automation effects.

The service-termination recovery-time distribution should therefore be
treated as evidence of substantial experimental/system timing
variability rather than evidence of a stable automated-recovery
advantage.

Failure impact was 1.0 in every valid service-termination observation
under both conditions. Each valid trial contained three failed offered
requests during the measurement interval.

All 20 valid service-termination observations subsequently achieved
functional recovery.

## Failure-impact measurement finding

Failure impact did not discriminate between recovery conditions in
either fault model:

- dependency latency: failure-impact rate 0.0 throughout;
- service termination: failure-impact rate 1.0 throughout.

This is a methodological pilot finding.

Under the current workload, detector and fault-window definitions,
failure impact is effectively bounded by scenario behaviour rather
than recovery initiator.

Future experimental design should consider whether a longer or
higher-resolution workload window is required if failure impact is to
measure differences between recovery strategies.

No Phase 5 data are retrospectively altered in response to this
finding.

## Recovery mechanism fidelity

The recovery-condition implementation behaved as intended.

For every valid manual fault observation:

- manual intervention count = 1;
- automation decision count = 0.

For every valid automated fault observation:

- manual intervention count = 0;
- automation decision count = 1.

For every no-fault control:

- manual intervention count = 0;
- automation decision count = 0.

All 40 valid fault observations recorded successful functional
recovery.

## Execution stability

The pilot required three reserve attempts to resolve the complete
50-slot design.

All invalid attempts occurred in the service-termination scenario.

This is reported as execution-stability evidence rather than a
condition-effect outcome. The number of invalid attempts is too small
and the pilot was not designed to infer condition-specific differences
in invalid-run probability.

## Interpretation

The Phase 5 pilot does not support a general claim that automation
improves reliability.

Instead, it provides evidence that observed automation effects are
fault- and measurement-dependent.

Dependency-latency trials showed a small and directionally consistent
recovery-time advantage for the automated condition.

Service-termination trials showed substantial timing variability and
no consistent paired recovery-time advantage.

Failure impact did not distinguish the recovery conditions in either
fault scenario.

These findings motivate continued investigation of when, under which
fault characteristics, and according to which reliability measures
automation changes recovery behaviour.

## Claim boundary

These findings apply only to the controlled Phase 5 technical pilot.

They do not establish:

- statistical significance;
- production readiness;
- universal causal effects;
- developer workload effects;
- developer trust effects;
- developer understanding effects;
- human reaction-time differences.

Human and software-engineering-practice questions remain outside the
Phase 5 evidence boundary.
