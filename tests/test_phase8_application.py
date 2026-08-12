from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATION = ROOT / "docs" / "application"
FINAL_PROPOSAL = APPLICATION / "phase-8-ou-proposal-final.md"


def proposal_text() -> str:
    return FINAL_PROPOSAL.read_text(encoding="utf-8")


def proposal_body() -> str:
    return proposal_text().split("## References", 1)[0]


def proposal_word_count() -> int:
    return len(re.findall(r"\b[\w?'-]+\b", proposal_body()))


def test_phase8_application_documents_exist() -> None:
    required = (
        "phase-8-application-requirements.md",
        "phase-8-evidence-audit.md",
        "phase-8-literature-boundary.md",
        "phase-8-rq-contribution-freeze.md",
        "phase-8-claim-evidence-matrix.csv",
        "phase-8-proposal-architecture.md",
        "phase-8-feedback-response-matrix.md",
        "phase-8-reference-shortlist.md",
        "phase-8-ou-proposal-v1.md",
        "phase-8-proposal-word-count.md",
        "phase-8-methods-dossier.md",
        "phase-8-technical-pilot-summary.md",
        "phase-8-doctoral-work-plan.md",
        "phase-8-supervisor-alignment.md",
        "phase-8-supervisor-briefing.md",
        "phase-8-initial-contact-email.md",
        "phase-8-cover-letter.md",
        "phase-8-cv-evidence-checklist.md",
        "phase-8-adversarial-review.md",
        "phase-8-ou-proposal-final.md",
        "phase-8-submission-readiness.md",
    )

    assert all((APPLICATION / name).is_file() for name in required)


def test_final_proposal_is_inside_ou_word_boundary() -> None:
    assert 600 <= proposal_word_count() <= 1000


def test_final_proposal_uses_required_structure() -> None:
    text = proposal_text()

    assert "## Background" in text
    assert "## Aim and Method" in text
    assert "## Relevance" in text
    assert "## Your suitability" in text
    assert "## References" in text


def test_final_proposal_has_exactly_two_primary_rqs() -> None:
    text = proposal_body()

    assert text.count("**RQ1:**") == 1
    assert text.count("**RQ2:**") == 1
    assert "RQ3" not in text
    assert "RQ4" not in text


def test_final_proposal_identifies_empirical_software() -> None:
    text = proposal_text()

    assert "OrderFlow" in text
    assert "`order-api`" in text
    assert "`inventory`" in text
    assert "purpose-built" in text


def test_final_proposal_preserves_pilot_boundary() -> None:
    text = proposal_text().lower()

    assert "50 planned technical slots" in text
    assert "53 preserved attempts" in text
    assert "50 valid observations" in text
    assert "descriptive pilot evidence only" in text


def test_final_proposal_does_not_make_disallowed_completion_claims() -> None:
    text = proposal_text().lower()

    forbidden = (
        "proves that",
        "production-ready",
        "ethics approval has been obtained",
        "participant feasibility has been completed",
        "automation universally improves",
    )

    assert all(phrase not in text for phrase in forbidden)


def test_phase1_full_review_is_not_falsely_closed() -> None:
    text = (APPLICATION / "phase-8-literature-boundary.md").read_text(encoding="utf-8").lower()

    assert "full phase 1 review remains open" in text

    normalized = " ".join(text.split())
    assert "have not been completed" in normalized


def test_source_proposal_is_retained() -> None:
    source = ROOT / "docs" / "proposal" / "source" / "Sam_Harrison_PhD_Proposal.pdf"

    assert source.is_file()


def test_no_phase6_participant_data_has_appeared() -> None:
    forbidden = (
        ROOT / "data" / "raw" / "phase-6",
        ROOT / "data" / "processed" / "phase-6",
        ROOT / "data" / "participants",
        ROOT / "results" / "phase-6" / "participants",
    )

    assert all(not path.exists() for path in forbidden)


def test_supervisor_alignment_does_not_claim_commitment() -> None:
    text = (APPLICATION / "phase-8-supervisor-alignment.md").read_text(encoding="utf-8").lower()

    normalized = " ".join(text.split())

    assert "no availability or willingness to supervise is implied" in normalized
    assert "not present him as an agreed primary supervisor" in normalized
