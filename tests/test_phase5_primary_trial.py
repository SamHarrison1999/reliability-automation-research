from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "experiments" / "harness" / "phase_5_primary_trial.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase_5_primary_trial", MODULE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_order() -> dict[str, Any]:
    return {
        "slots": [
            {
                "schedule_slot": 1,
                "cell_id": "service-termination-manual",
                "scenario_id": "service-termination-v1",
                "automation_condition": "manual",
                "repetition": 1,
                "reserve": False,
            },
            {
                "schedule_slot": 2,
                "cell_id": "no-fault-control",
                "scenario_id": "no-fault-v1",
                "automation_condition": "control",
                "repetition": 1,
                "reserve": False,
            },
        ]
    }


def batch() -> dict[str, Any]:
    return {"pilot_batch_id": "batch-test"}


def attempt(
    trial_id: str,
    schedule_slot: int,
    passed: bool,
    *,
    reserve: bool = False,
    reserve_ordinal: int | None = None,
    cell_id: str = "service-termination-manual",
) -> dict[str, Any]:
    manifest = {
        "trial_id": trial_id,
        "primary_schedule_slot": schedule_slot,
        "reserve": reserve,
        "reserve_ordinal": reserve_ordinal,
        "cell_id": cell_id,
    }
    return {
        "manifest": manifest,
        "validity": {"passed": passed},
    }


def test_initial_action_is_primary_slot_one() -> None:
    module = load_module()

    action = module.next_action(batch(), run_order(), [])

    assert action["action"] == "primary"
    assert action["schedule_slot"] == 1
    assert action["attempt_sequence"] == 1


def test_valid_primary_advances_to_next_primary_slot() -> None:
    module = load_module()
    attempts = [attempt("primary-1", 1, True)]

    action = module.next_action(batch(), run_order(), attempts)

    assert action["action"] == "primary"
    assert action["schedule_slot"] == 2
    assert action["attempt_sequence"] == 2


def test_invalid_primary_requires_immediate_same_cell_reserve_one() -> None:
    module = load_module()
    attempts = [attempt("primary-1", 1, False)]

    action = module.next_action(batch(), run_order(), attempts)

    assert action["action"] == "reserve"
    assert action["schedule_slot"] == 1
    assert action["reserve_ordinal"] == 1
    assert action["source_invalid_trial_id"] == "primary-1"
    assert action["attempt_sequence"] == 2


def test_invalid_reserve_one_requires_reserve_two() -> None:
    module = load_module()
    attempts = [
        attempt("primary-1", 1, False),
        attempt("reserve-1", 1, False, reserve=True, reserve_ordinal=1),
    ]

    action = module.next_action(batch(), run_order(), attempts)

    assert action["action"] == "reserve"
    assert action["reserve_ordinal"] == 2
    assert action["source_invalid_trial_id"] == "reserve-1"
    assert action["attempt_sequence"] == 3


def test_two_invalid_reserves_pause_the_pilot() -> None:
    module = load_module()
    attempts = [
        attempt("primary-1", 1, False),
        attempt("reserve-1", 1, False, reserve=True, reserve_ordinal=1),
        attempt("reserve-2", 1, False, reserve=True, reserve_ordinal=2),
    ]

    action = module.next_action(batch(), run_order(), attempts)

    assert action["action"] == "pause"
    assert action["reason"] == "reserve-exhausted"
    assert action["schedule_slot"] == 1


def test_valid_reserve_resolves_repetition_and_advances() -> None:
    module = load_module()
    attempts = [
        attempt("primary-1", 1, False),
        attempt("reserve-1", 1, True, reserve=True, reserve_ordinal=1),
    ]

    action = module.next_action(batch(), run_order(), attempts)

    assert action["action"] == "primary"
    assert action["schedule_slot"] == 2
    assert action["attempt_sequence"] == 3


def test_completed_attempt_loader_refuses_incomplete_raw_directory(
    tmp_path: Path,
) -> None:
    module = load_module()
    directory = tmp_path / "trial-a"
    directory.mkdir()
    (directory / "trial-manifest.json").write_text(
        json.dumps(
            {
                "trial_id": "trial-a",
                "pilot_batch_id": "batch-test",
            }
        ),
        encoding="utf-8",
    )

    try:
        module.completed_attempts(tmp_path, "batch-test")
    except RuntimeError as exc:
        assert "no validity record" in str(exc)
    else:
        raise AssertionError("incomplete primary evidence was accepted")


def test_primary_executor_has_no_operator_slot_or_condition_arguments() -> None:
    source = MODULE.read_text(encoding="utf-8")

    assert '"--scenario"' not in source
    assert '"--condition"' not in source
    assert '"--primary-slot"' not in source
    assert '"--execute-next"' in source
    assert '"--confirm-frozen-primary"' in source
