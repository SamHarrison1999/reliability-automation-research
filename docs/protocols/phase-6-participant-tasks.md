# Phase 6 participant task protocol

**Status:** Frozen synthetic task design for researcher-only validation

**Participant execution:** Prohibited until ethics approval

## Purpose

Create structured OrderFlow incident tasks that elicit diagnosis, recovery and
escalation decisions without giving participants unrestricted infrastructure
access.

## Task interface

Each task presents:

1. incident notification;
2. bounded observability evidence;
3. participant authority/role information;
4. permitted decision choices;
5. an automation recommendation only in condition `H-A`;
6. diagnosis submission;
7. recovery/escalation submission;
8. short retrospective explanation; and
9. workload ratings.

The interface simulates decisions.

It does not expose a real shell, Kubernetes API or production environment.

## Human conditions

### H-M

Manual decision baseline.

No automation recommendation is displayed.

### H-A

Automation-assisted decision condition.

A recommendation is displayed.

Participants are informed before the study that recommendations can be
incorrect and that they remain responsible for the decision.

## Fault families

Two task families are retained from the technical work:

- dependency latency;
- service termination.

Human-task timings are independent human measures and are not Phase 5
technical recovery timings.

## Task variants

Four variants are frozen:

- `DL-A`;
- `DL-B`;
- `ST-A`;
- `ST-B`.

Variants A allow direct recovery within participant authority.

Variants B represent observe-only authority and therefore make escalation the
appropriate operational decision even when the underlying fault can be
diagnosed.

## Automation recommendations

Recommendation correctness is deliberately balanced.

- `DL-A`: correct;
- `DL-B`: incorrect because direct remediation exceeds participant authority;
- `ST-A`: correct;
- `ST-B`: incorrect because direct remediation exceeds participant authority.

This is not deception because participants are told that recommendations may
be fallible.

## Counterbalancing

Four sequence groups are used.

Across the four sequences:

- every participant receives two H-M and two H-A tasks;
- every task variant appears equally under H-M and H-A;
- every participant receiving H-A receives one correct and one incorrect
  recommendation;
- order is reversed/balanced across sequence groups; and
- an individual participant never repeats an identical task variant.

Sequence allocation should rotate in order across enrolled participants unless
the approved protocol specifies another deterministic assignment rule.

## Researcher-only walkthrough

Before participant execution, a researcher walkthrough must verify:

- every evidence package supports its answer key;
- every displayed action maps to the manifest;
- H-M never reveals the automation recommendation;
- H-A always displays the correct manifest recommendation;
- authority restrictions are visible before the participant decides;
- timestamps can represent task exposure and decision submission;
- workload and explanation screens occur after the decision; and
- no real infrastructure mutation is possible.

A researcher walkthrough generates synthetic validation evidence only.

It is not participant data.
