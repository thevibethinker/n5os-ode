import json
import sqlite3
from pathlib import Path

import pytest

import sys
sys.path.insert(0, '/home/workspace/N5/scripts')

from notion_deal_sync import (
    DealDB,
    extract_notion_property,
    notion_property_payload,
    pull_sync,
    resolve_bidirectional,
)


def test_extract_notion_property_basic_types():
    page = {
        "properties": {
            "Company": {"title": [{"plain_text": "Darwinbox"}]},
            "Deal Temp": {"select": {"name": "hot"}},
            "Last Meeting": {"date": {"start": "2026-01-18"}},
            "Next Action": {"rich_text": [{"plain_text": "Send proposal"}]},
            "LinkedIn URL": {"url": "https://linkedin.com/in/x"},
        }
    }

    assert extract_notion_property(page, "Company", "title") == "Darwinbox"
    assert extract_notion_property(page, "Deal Temp", "select") == "hot"
    assert extract_notion_property(page, "Last Meeting", "date") == "2026-01-18"
    assert extract_notion_property(page, "Next Action", "rich_text") == "Send proposal"
    assert extract_notion_property(page, "LinkedIn URL", "url") == "https://linkedin.com/in/x"


def test_notion_property_payload_shapes():
    assert notion_property_payload("select", "hot") == {"select": {"name": "hot"}}
    assert notion_property_payload("select", "") == {"select": None}

    assert notion_property_payload("date", "2026-01-18") == {"date": {"start": "2026-01-18"}}
    assert notion_property_payload("date", None) == {"date": None}

    assert notion_property_payload("rich_text", "Hello") == {
        "rich_text": [{"type": "text", "text": {"content": "Hello"}}]
    }


def test_resolve_bidirectional_prefers_newer():
    # Notion newer -> notion wins
    v = resolve_bidirectional(
        local_val="A",
        notion_val="B",
        local_updated_at="2026-01-18T10:00:00+00:00",
        notion_last_edited_time="2026-01-18T11:00:00+00:00",
    )
    assert v == "B"

    # Local newer -> local wins
    v = resolve_bidirectional(
        local_val="A",
        notion_val="B",
        local_updated_at="2026-01-18T12:00:00+00:00",
        notion_last_edited_time="2026-01-18T11:00:00+00:00",
    )
    assert v == "A"


def _init_temp_db(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE deals (
            id TEXT PRIMARY KEY,
            deal_type TEXT,
            pipeline TEXT,
            external_source TEXT,
            external_id TEXT,
            company TEXT,
            category TEXT,
            proximity TEXT,
            temperature TEXT,
            stage TEXT,
            next_action TEXT,
            last_touched TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE deal_contacts (
            id TEXT PRIMARY KEY,
            contact_type TEXT,
            pipeline TEXT,
            full_name TEXT,
            linkedin_url TEXT,
            second_degree_connects TEXT,
            angle_strategy TEXT,
            blurb TEXT,
            notes TEXT,
            source_system TEXT,
            source_id TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def test_pull_sync_from_cache_inserts(tmp_path: Path):
    db_path = tmp_path / "deals.db"
    _init_temp_db(db_path)

    # Minimal mapping with only what pull_sync needs
    mapping = {
        "acquirer_targets": {
            "database_id": "dummy",
            "local": {"table": "deals", "deal_type": "careerspan_acquirer", "pipeline": "careerspan", "id_prefix": "cs-acq"},
            "fields": {
                "company": {"notion": "Company", "local": "company", "direction": "notion_to_local", "type": "title"},
                "deal_temp": {"notion": "Deal Temp", "local": "temperature", "direction": "bidirectional", "type": "select"},
                "status": {"notion": "Status", "local": "stage", "direction": "bidirectional", "type": "select"},
                "next_action": {"notion": "Next Action", "local": "next_action", "direction": "bidirectional", "type": "rich_text"},
            },
        }
    }

    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    page = {
        "id": "page-123",
        "last_edited_time": "2026-01-18T11:00:00Z",
        "properties": {
            "Company": {"title": [{"plain_text": "Darwinbox"}]},
            "Deal Temp": {"select": {"name": "hot"}},
            "Status": {"select": {"name": "engaged"}},
            "Next Action": {"rich_text": [{"plain_text": "Send proposal"}]},
        },
    }

    (cache_dir / "acquirer_targets.json").write_text(json.dumps([page]))

    db = DealDB(str(db_path))

    res = pull_sync(db=db, mapping=mapping, notion=None, cache_dir=str(cache_dir), dry_run=False)
    assert res["insert"] == 1

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT company, stage, temperature, external_source, external_id FROM deals")
    row = dict(c.fetchone())
    conn.close()

    assert row["company"] == "Darwinbox"
    assert row["stage"] == "engaged"
    assert row["temperature"] == "hot"
    assert row["external_source"] == "notion"
    assert row["external_id"] == "page-123"
