# Phase 6 pseudonymisation boundary

## Study identifier

Format concept:

`P` + randomly generated non-semantic identifier

The identifier must not encode personal attributes.

## Identity mapping

A separate restricted mapping links:

`contact/consent identity <-> study participant ID`

The mapping is not part of the research dataset.

## Research record

Research records contain only the study ID plus protocol/task data.

## Withdrawal

The mapping supports withdrawal during the approved withdrawal period.

## Anonymisation

After the permitted withdrawal/administrative period, the mapping may be
destroyed according to the approved DMP.

Researchers must then check that remaining free text/context does not itself
allow reasonably likely re-identification before calling data anonymous.

## Public repository

Neither the mapping nor participant-level pseudonymised records may be
committed.

Synthetic examples must use clearly artificial identifiers and contain no
participant-derived content.
