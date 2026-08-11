from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "manifests" / "phase-6-participant-task-manifest.json"


def load_manifest() -> dict[str, Any]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return cast(dict[str, Any], value)


def test_phase6_manifest_has_expected_boundary() -> None:
    manifest = load_manifest()

    assert manifest["schema_version"] == "1.0.0"
    assert manifest["protocol_id"] == "phase-6-human-participant-task-protocol-v1"
    assert manifest["participant_execution_authorised"] is False
    assert set(manifest["conditions"]) == {"H-M", "H-A"}


def test_phase6_task_catalogue_is_frozen_and_balanced() -> None:
    manifest = load_manifest()
    tasks = cast(list[dict[str, Any]], manifest["tasks"])

    assert {task["task_id"] for task in tasks} == {
        "DL-A",
        "DL-B",
        "ST-A",
        "ST-B",
    }

    assert sum(bool(task["automation_recommendation"]["correct"]) for task in tasks) == 2

    assert sum(bool(task["escalation_expected"]) for task in tasks) == 2


def test_phase6_sequences_balance_conditions_and_variants() -> None:
    manifest = load_manifest()
    sequences = cast(dict[str, list[dict[str, str]]], manifest["sequences"])

    assert set(sequences) == {"S1", "S2", "S3", "S4"}

    task_condition_counts: dict[tuple[str, str], int] = {}

    for sequence in sequences.values():
        assert len(sequence) == 4
        assert len({entry["task_id"] for entry in sequence}) == 4
        assert sum(entry["condition"] == "H-M" for entry in sequence) == 2
        assert sum(entry["condition"] == "H-A" for entry in sequence) == 2

        for entry in sequence:
            key = (entry["task_id"], entry["condition"])
            task_condition_counts[key] = task_condition_counts.get(key, 0) + 1

    for task_id in ("DL-A", "DL-B", "ST-A", "ST-B"):
        assert task_condition_counts[(task_id, "H-M")] == 2
        assert task_condition_counts[(task_id, "H-A")] == 2


def test_each_sequence_has_one_correct_and_one_incorrect_assisted_task() -> None:
    manifest = load_manifest()
    tasks = {task["task_id"]: task for task in cast(list[dict[str, Any]], manifest["tasks"])}

    for sequence in cast(
        dict[str, list[dict[str, str]]],
        manifest["sequences"],
    ).values():
        correctness = [
            bool(tasks[entry["task_id"]]["automation_recommendation"]["correct"])
            for entry in sequence
            if entry["condition"] == "H-A"
        ]
        assert sorted(correctness) == [False, True]


def test_no_phase6_participant_records_exist_in_repository() -> None:
    forbidden = (
        ROOT / "data" / "raw" / "phase-6",
        ROOT / "data" / "processed" / "phase-6",
        ROOT / "data" / "participants",
        ROOT / "results" / "phase-6" / "participants",
    )

    assert all(not path.exists() for path in forbidden)


def test_participant_materials_are_explicitly_not_approved_for_use() -> None:
    information = (ROOT / "docs" / "ethics" / "phase-6-participant-information-sheet.md").read_text(encoding="utf-8")

    consent = (ROOT / "docs" / "ethics" / "phase-6-consent-form.md").read_text(encoding="utf-8")

    assert "Do not distribute for recruitment." in information
    assert "Do not use to enrol participants." in consent
