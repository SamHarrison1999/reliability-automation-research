from __future__ import annotations

from typing import Any

from analysis.phase_5.phase_5_primary_descriptive import (
    PRIMARY_METRIC_ROLES,
    binary_metric_summary,
    describe_numeric,
    paired_primary_metric,
    quantile_type7,
)


def test_type7_quantiles() -> None:
    values = [1.0, 2.0, 3.0, 4.0]

    assert quantile_type7(values, 0.25) == 1.75
    assert quantile_type7(values, 0.50) == 2.5
    assert quantile_type7(values, 0.95) == 3.8499999999999996


def test_describe_numeric_is_deterministic() -> None:
    result = describe_numeric([1.0, 2.0, 3.0, 4.0])

    assert result == {
        "n": 4,
        "mean": 2.5,
        "median": 2.5,
        "p25": 1.75,
        "p75": 3.25,
        "p95": 3.85,
        "min": 1.0,
        "max": 4.0,
    }


def _observation(
    repetition: int,
    condition: str,
    recovery: float,
) -> dict[str, object]:
    return {
        "repetition": repetition,
        "automation_condition": condition,
        "primary_metrics": {
            "recovery_time_ms": {
                "status": "observed",
                "value": recovery,
            }
        },
    }


def test_paired_difference_is_automated_minus_manual() -> None:
    observations: list[dict[str, object]] = []

    for repetition in range(1, 11):
        observations.append(
            _observation(
                repetition,
                "manual",
                100.0 + repetition,
            )
        )
        observations.append(
            _observation(
                repetition,
                "automated",
                80.0 + repetition,
            )
        )

    result = paired_primary_metric(
        observations,
        "recovery_time_ms",
    )

    assert result["pair_count"] == 10
    assert result["difference_definition"] == ("automated-minus-manual")

    paired = result["paired_difference"]

    assert paired["mean"] == -20.0
    assert paired["median"] == -20.0

    assert result["direction_counts"] == {
        "automated_lower": 10,
        "equal": 0,
        "automated_higher": 0,
    }


def test_detection_latency_role_is_balance_check() -> None:
    assert PRIMARY_METRIC_ROLES["detection_latency_ms"] == ("shared-detector-fidelity-and-balance-check")


def test_recovery_is_treatment_relevant() -> None:
    assert PRIMARY_METRIC_ROLES["recovery_time_ms"] == ("treatment-relevant-technical-outcome")


def test_failure_impact_is_treatment_relevant() -> None:
    assert PRIMARY_METRIC_ROLES["failure_impact_rate"] == ("treatment-relevant-technical-outcome")


def test_recovery_success_uses_frozen_binary_integer_contract() -> None:
    observations: list[dict[str, Any]] = [
        {
            "secondary_metrics": {
                "recovery_success": {
                    "status": "observed",
                    "value": 1,
                }
            }
        },
        {
            "secondary_metrics": {
                "recovery_success": {
                    "status": "observed",
                    "value": 0,
                }
            }
        },
        {
            "secondary_metrics": {
                "recovery_success": {
                    "status": "not_applicable",
                    "value": None,
                }
            }
        },
    ]

    result = binary_metric_summary(
        observations,
        "secondary_metrics",
        "recovery_success",
    )

    assert result == {
        "status_counts": {
            "not_applicable": 1,
            "observed": 2,
        },
        "representation": "integer-0-or-1",
        "observed_binary_counts": {
            "0": 1,
            "1": 1,
        },
    }
