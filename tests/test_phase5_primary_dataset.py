from __future__ import annotations

import json

import pytest

from analysis.phase_5.phase_5_primary_dataset import (
    EXPECTED_CELL_COUNTS,
    canonical_json_bytes,
    sha256_bytes,
    validate_attempt_corpus,
)


def _attempt(
    *,
    slot: int,
    run_order: int,
    scenario: str,
    condition: str,
    repetition: int,
    passed: bool = True,
    reserve: bool = False,
    reserve_ordinal: int | None = None,
) -> dict[str, object]:
    return {
        "primary_schedule_slot": slot,
        "run_order": run_order,
        "repetition": repetition,
        "scenario_id": scenario,
        "automation_condition": condition,
        "reserve": reserve,
        "reserve_ordinal": reserve_ordinal,
        "pilot_batch_id": "phase5-primary-16f9cefff0d6b017",
        "passed": passed,
    }


def test_canonical_json_is_stable() -> None:
    left = canonical_json_bytes({"b": 2, "a": 1})
    right = canonical_json_bytes({"a": 1, "b": 2})

    assert left == right
    assert left.endswith(b"\n")
    assert json.loads(left) == {"a": 1, "b": 2}


def test_sha256_bytes_is_deterministic() -> None:
    payload = b"phase-5\n"

    assert sha256_bytes(payload) == sha256_bytes(payload)
    assert len(sha256_bytes(payload)) == 64


def test_expected_cell_contract_is_balanced() -> None:
    assert EXPECTED_CELL_COUNTS == {
        "no-fault-v1|control": 10,
        "service-termination-v1|manual": 10,
        "service-termination-v1|automated": 10,
        "dependency-latency-v1|manual": 10,
        "dependency-latency-v1|automated": 10,
    }


def test_validation_rejects_incomplete_corpus() -> None:
    with pytest.raises(ValueError, match="unexpected attempt count"):
        validate_attempt_corpus([])


def test_validation_rejects_wrong_batch() -> None:
    attempts = [
        _attempt(
            slot=1,
            run_order=1,
            scenario="service-termination-v1",
            condition="manual",
            repetition=1,
        )
    ]

    attempts[0]["pilot_batch_id"] = "wrong"

    with pytest.raises(ValueError, match="unexpected attempt count"):
        validate_attempt_corpus(attempts)
