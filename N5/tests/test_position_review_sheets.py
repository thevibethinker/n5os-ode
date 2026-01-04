import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from b32_position_extractor import _parse_review_sheet, _apply_review_decisions


def test_parse_review_sheet_accept():
    md = """
# Positions Review Sheet

## Candidate

Candidate ID: cand_1

### Your decision

Decision: accept

Attribution: mine

Credit: 

Notes: Looks right.

---
"""
    decisions = _parse_review_sheet(md)
    assert len(decisions) == 1
    assert decisions[0]["candidate_id"] == "cand_1"
    assert decisions[0]["decision"] == "accept"
    assert decisions[0]["amended_insight"] is None


def test_parse_review_sheet_amend_requires_amended_insight():
    md = """
## Candidate

Candidate ID: cand_2

Decision: amend

Amended insight:


Attribution: mine

Credit: 

Notes: 

---
"""
    with pytest.raises(ValueError):
        _parse_review_sheet(md)


def test_apply_review_decisions_amend_overwrite_traceable_and_recompute_only_wisdom():
    candidates = [
        {
            "id": "cand_3",
            "status": "pending",
            "insight": "original insight",
            "source_excerpt": "some excerpt",
            "speaker": "V",
            "domain": "worldview",
            "classification": "V_POSITION",
            "reasoning": "old reasoning",
            "stakes": "old stakes",
            "conditions": "old conditions",
        }
    ]
    decisions = [
        {
            "candidate_id": "cand_3",
            "decision": "amend",
            "amended_insight": "new amended insight",
            "attribution": "mine",
            "credit": "",
            "notes": "",
        }
    ]

    def fake_recompute_fn(*, source_excerpt: str, speaker: str, insight_final: str):
        assert source_excerpt == "some excerpt"
        assert speaker == "V"
        assert insight_final == "new amended insight"
        return {
            "reasoning": "new reasoning",
            "stakes": "new stakes",
            "conditions": "new conditions",
        }

    updated, stats = _apply_review_decisions(
        candidates,
        decisions,
        batch_path=Path("/tmp/batch.md"),
        dry_run=False,
        recompute_on_amend=True,
        recompute_fn=fake_recompute_fn,
    )

    c = updated[0]
    assert c["insight"] == "original insight"  # original immutable
    assert c["insight_amended"] == "new amended insight"  # overwrite stored
    assert c["reasoning"] == "new reasoning"
    assert c["stakes"] == "new stakes"
    assert c["conditions"] == "new conditions"
    assert c["domain"] == "worldview"  # read-only
    assert c["classification"] == "V_POSITION"  # read-only
    assert c["speaker"] == "V"  # read-only
    assert c["source_excerpt"] == "some excerpt"  # read-only

    assert stats["amend"] == 1
    assert stats["updated"] == 1


