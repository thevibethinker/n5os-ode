import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from projection_store import ProjectionStore


def test_projection_store_creates_required_tables(tmp_path):
    store = ProjectionStore(tmp_path / "projections.db")

    assert store.table_exists("interactions")
    assert store.table_exists("contact_context")
    assert store.table_exists("company_context")
    assert store.table_exists("review_queue")
    assert store.table_exists("projection_ledger")


def test_interaction_replay_is_blocked_and_logged(tmp_path):
    store = ProjectionStore(tmp_path / "projections.db")
    interaction = {
        "id": "int_001",
        "candidate_id": "cand_001",
        "event_ids": ["evt_001", "evt_002"],
        "timestamp": "2026-04-09T18:05:00Z",
        "interaction_type": "introduction",
        "summary": "Alex introduced Dev and Primary over email.",
        "person_ids": ["person_dev", "person_v"],
        "company_ids": ["company_startupintros"],
        "confidence": "strong",
        "projection_key": "intro|cand_001",
        "rollback_data": {"interaction": None},
        "created_at": "2026-04-09T18:05:00Z",
    }

    first = store.insert_interaction(interaction)
    second = store.insert_interaction(interaction)

    assert first["status"] == "inserted"
    assert second["status"] == "blocked"
    assert store.interaction_exists("intro|cand_001") is True

    interactions = store.list_interactions()
    ledger_entries = store.list_ledger_entries(candidate_id="cand_001", destination="interactions")

    assert len(interactions) == 1
    assert interactions[0]["id"] == "int_001"
    assert len(ledger_entries) == 2
    assert [entry["outcome"] for entry in ledger_entries] == ["applied", "blocked"]


def test_context_review_and_ledger_apis_cover_each_table(tmp_path):
    store = ProjectionStore(tmp_path / "projections.db")

    contact_result = store.upsert_contact_context(
        {
            "person_id": "person_dev",
            "name": "Dev Chandra",
            "last_interaction_at": "2026-04-09T18:05:00Z",
            "interaction_count": 2,
            "context_notes": ["Warm intro via Alex", "Prefers in-person meetings"],
        }
    )
    company_result = store.upsert_company_context(
        {
            "company_id": "company_startupintros",
            "name": "Startup Intros",
            "last_seen_at": "2026-04-09T18:05:00Z",
            "mention_count": 3,
            "context_notes": ["Dev is founder and CEO"],
        }
    )
    review_result = store.enqueue_review_item(
        {
            "candidate_type": "new_contact",
            "candidate_data": {"name": "Alex Caveny"},
            "reason": "No exact identity match in local index",
            "suggested_action": "create_contact",
            "source_event_ids": ["evt_010"],
        }
    )
    ledger_id = store.record_ledger_entry(
        {
            "candidate_id": "cand_manual",
            "destination": "review_queue",
            "record_id": str(review_result["id"]),
            "write_type": "append",
            "confidence": "uncertain",
            "source_event_ids": ["evt_010"],
            "rollback_data": {},
            "outcome": "applied",
            "message": "queued for review",
        }
    )

    assert contact_result["status"] == "inserted"
    assert company_result["status"] == "inserted"
    assert store.contact_context_exists("person_dev") is True
    assert store.company_context_exists("company_startupintros") is True
    assert store.review_item_exists(review_result["id"]) is True
    assert store.ledger_entry_exists(ledger_id) is True
    assert store.get_contact_context("person_dev")["name"] == "Dev Chandra"
    assert store.get_company_context("company_startupintros")["name"] == "Startup Intros"
    assert store.get_review_item(review_result["id"])["candidate_type"] == "new_contact"
    assert len(store.list_contact_context()) == 1
    assert len(store.list_company_context()) == 1
    assert len(store.list_review_queue(status="pending")) == 1
