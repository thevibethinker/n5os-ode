#!/usr/bin/env python3
""" 
Notion Deal Sync — Worker 3 (Notion Bidirectional Sync)

Goal:
- Bidirectional sync between Notion databases and local `N5/data/deals.db`
- Notion is the human source of truth; local DB is the fast index + execution substrate
- Intelligence Summary updates are append/prepend-only (never overwrite history)

## TWO MODES OF OPERATION

### Mode 1: Direct API (requires NOTION_TOKEN)
Uses NotionClient class to call Notion API directly.
Supports property updates and read-modify-write patterns.
```bash
export NOTION_TOKEN=secret_...
python3 N5/scripts/notion_deal_sync.py push
```

### Mode 2: Pipedream Integration (via Zo's use_app_notion)
Uses Zo's connected Notion app for API calls.
BETTER for appending intel because notion-append-block works for page body.

**SOLUTION DISCOVERED (2026-01-18):**
- `notion-append-block` with `blockTypes: ["markdownContents"]` works for page body
- This is BETTER than property updates because it supports rich formatting
- Use `N5/scripts/notion_intel_prepend.py format-markdown` to generate content

CLI (high-level):
  python3 N5/scripts/notion_deal_sync.py pull --dry-run --cache-dir /path/to/notion_cache
  python3 N5/scripts/notion_deal_sync.py pull --dry-run   # requires NOTION_TOKEN
  python3 N5/scripts/notion_deal_sync.py compute-push --dry-run
  python3 N5/scripts/notion_deal_sync.py push --dry-run
  python3 N5/scripts/notion_deal_sync.py enqueue-intel --deal-id cs-acq-darwinbox --source-title "SMS" --source-type sms --key-fact "Ready to proceed"

Notes:
- This script deliberately keeps Notion schema coupling inside `N5/config/notion_field_mapping.json`.
- Sync safety: bidirectional fields only push when local is newer than the last pulled Notion edit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import requests
except Exception:
    requests = None  # type: ignore

# Add script dir to path for imports
_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# Import unified DB connection
try:
    from db_paths import get_db_connection as get_unified_db, N5_CORE_DB
    UNIFIED_DB_AVAILABLE = True
except ImportError:
    UNIFIED_DB_AVAILABLE = False
    N5_CORE_DB = None

# Legacy DB for outbox operations
DB_DEFAULT = "/home/workspace/N5/data/deals.db"
UNIFIED_DB_DEFAULT = str(N5_CORE_DB) if N5_CORE_DB else None
MAPPING_DEFAULT = "/home/workspace/N5/config/notion_field_mapping.json"
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(dt: Optional[str]) -> Optional[datetime]:
    if not dt:
        return None
    try:
        # Notion often returns ...Z
        if dt.endswith("Z"):
            dt = dt[:-1] + "+00:00"
        return datetime.fromisoformat(dt)
    except Exception:
        return None


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def _ensure_requests():
    if requests is None:
        raise RuntimeError("requests is required for live Notion sync. Install with: pip install requests")


class NotionClient:
    def __init__(self, token: str):
        _ensure_requests()
        self.token = token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def query_database(self, database_id: str, filter_obj: Optional[dict] = None) -> List[dict]:
        """Return all pages in a database (handles pagination)."""
        url = f"{NOTION_API_BASE}/databases/{database_id}/query"
        out: List[dict] = []
        payload: Dict[str, Any] = {}
        if filter_obj:
            payload["filter"] = filter_obj

        start_cursor: Optional[str] = None
        while True:
            p = dict(payload)
            if start_cursor:
                p["start_cursor"] = start_cursor

            resp = requests.post(url, headers=self._headers(), data=json.dumps(p), timeout=30)  # type: ignore
            if resp.status_code >= 400:
                raise RuntimeError(f"Notion query failed ({resp.status_code}): {resp.text[:400]}")
            data = resp.json()
            out.extend(data.get("results", []))

            if data.get("has_more"):
                start_cursor = data.get("next_cursor")
                continue
            break

        return out

    def retrieve_page(self, page_id: str) -> dict:
        url = f"{NOTION_API_BASE}/pages/{page_id}"
        resp = requests.get(url, headers=self._headers(), timeout=30)  # type: ignore
        if resp.status_code >= 400:
            raise RuntimeError(f"Notion retrieve page failed ({resp.status_code}): {resp.text[:400]}")
        return resp.json()

    def update_page_properties(self, page_id: str, properties: dict) -> None:
        url = f"{NOTION_API_BASE}/pages/{page_id}"
        payload = {"properties": properties}
        resp = requests.patch(url, headers=self._headers(), data=json.dumps(payload), timeout=30)  # type: ignore
        if resp.status_code >= 400:
            raise RuntimeError(f"Notion update failed ({resp.status_code}): {resp.text[:400]}")

    def create_page(self, database_id: str, properties: dict) -> dict:
        """Create a new page in a database. Returns the created page object."""
        url = f"{NOTION_API_BASE}/pages"
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        resp = requests.post(url, headers=self._headers(), data=json.dumps(payload), timeout=30)  # type: ignore
        if resp.status_code >= 400:
            raise RuntimeError(f"Notion create page failed ({resp.status_code}): {resp.text[:400]}")
        return resp.json()


def _rt_plain_text(rt: List[dict]) -> str:
    parts = []
    for r in rt or []:
        if not isinstance(r, dict):
            continue
        parts.append(r.get("plain_text") or r.get("text", {}).get("content") or "")
    return "".join(parts)


def extract_notion_property(page: dict, prop_name: str, prop_type: str) -> Any:
    props = page.get("properties", {}) or {}
    p = props.get(prop_name) or {}

    if prop_type == "title":
        return _rt_plain_text(p.get("title", []) or [])

    if prop_type == "rich_text":
        return _rt_plain_text(p.get("rich_text", []) or [])

    if prop_type == "select":
        sel = p.get("select")
        if isinstance(sel, dict):
            return sel.get("name")
        return None

    if prop_type == "multi_select":
        arr = p.get("multi_select") or []
        names = []
        for item in arr:
            if isinstance(item, dict) and item.get("name"):
                names.append(item["name"])
        return names

    if prop_type == "date":
        d = p.get("date")
        if isinstance(d, dict):
            return d.get("start")
        return None

    if prop_type == "url":
        return p.get("url")

    # Fallback: best-effort
    return None


def notion_property_payload(prop_type: str, value: Any) -> dict:
    if prop_type == "select":
        if value is None or value == "":
            return {"select": None}
        return {"select": {"name": str(value)}}

    if prop_type == "date":
        if value is None or value == "":
            return {"date": None}
        return {"date": {"start": str(value)}}

    if prop_type == "url":
        return {"url": None if value in (None, "") else str(value)}

    if prop_type == "title":
        txt = "" if value is None else str(value)
        return {"title": [{"type": "text", "text": {"content": txt}}]}

    if prop_type == "rich_text":
        txt = "" if value is None else str(value)
        return {"rich_text": [{"type": "text", "text": {"content": txt}}]}

    if prop_type == "multi_select":
        if not value:
            return {"multi_select": []}
        return {"multi_select": [{"name": str(v)} for v in value]}

    raise ValueError(f"Unsupported property type: {prop_type}")


def format_intel_entry(
    date: str,
    source_title: str,
    source_type: str,
    stage_before: Optional[str] = None,
    stage_after: Optional[str] = None,
    key_facts: Optional[List[str]] = None,
    next_action: Optional[str] = None,
    next_action_date: Optional[str] = None,
) -> str:
    lines = ["---", f"## [{date}] {source_title}", "", f"**Source:** {source_type}"]

    if stage_before and stage_after and stage_before != stage_after:
        lines.append(f"**Stage:** {stage_before} → {stage_after}")

    if key_facts:
        lines.append("")
        lines.append("**Key Intel:**")
        for f in key_facts:
            lines.append(f"- {f}")

    if next_action:
        lines.append("")
        if next_action_date:
            lines.append(f"**Next:** {next_action} (by {next_action_date})")
        else:
            lines.append(f"**Next:** {next_action}")

    return "\n".join(lines)


class DealDB:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self) -> None:
        conn = self.connect()
        c = conn.cursor()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS notion_sync_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS notion_entity_state (
                entity_type TEXT NOT NULL,   -- deal | contact
                entity_id TEXT NOT NULL,
                notion_page_id TEXT NOT NULL,
                notion_last_edited_time TEXT,
                last_pull_at TEXT,
                last_push_at TEXT,
                PRIMARY KEY (entity_type, entity_id)
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS notion_outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                notion_page_id TEXT NOT NULL,
                action_type TEXT NOT NULL,   -- update_page_properties | append_intel
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                synced_at TEXT,
                error TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    # -------------------------
    # Lookups
    # -------------------------

    def get_deal_by_notion_page(self, page_id: str) -> Optional[dict]:
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM deals
            WHERE external_source = 'notion' AND external_id = ?
            LIMIT 1
            """,
            (page_id,),
        )
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_contact_by_notion_page(self, page_id: str) -> Optional[dict]:
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM deal_contacts
            WHERE source_system = 'notion' AND source_id = ?
            LIMIT 1
            """,
            (page_id,),
        )
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def upsert_deal(self, record: dict, dry_run: bool) -> Tuple[str, str]:
        """Return (action, deal_id)."""
        now = _now_iso()
        conn = self.connect()
        c = conn.cursor()

        deal_id = record["id"]
        c.execute("SELECT id FROM deals WHERE id = ?", (deal_id,))
        exists = c.fetchone() is not None

        if dry_run:
            conn.close()
            return ("update" if exists else "insert", deal_id)

        if exists:
            cols = [k for k in record.keys() if k != "id"]
            set_clause = ", ".join([f"{k} = ?" for k in cols] + ["updated_at = ?"])
            params = [record[k] for k in cols] + [now, deal_id]
            c.execute(f"UPDATE deals SET {set_clause} WHERE id = ?", params)
            action = "update"
        else:
            cols = list(record.keys()) + ["created_at", "updated_at"]
            placeholders = ",".join(["?"] * len(cols))
            params = [record[k] for k in record.keys()] + [now, now]
            c.execute(
                f"INSERT INTO deals ({','.join(cols)}) VALUES ({placeholders})",
                params,
            )
            action = "insert"

        conn.commit()
        conn.close()
        return (action, deal_id)

    def upsert_contact(self, record: dict, dry_run: bool) -> Tuple[str, str]:
        now = _now_iso()
        conn = self.connect()
        c = conn.cursor()

        contact_id = record["id"]
        c.execute("SELECT id FROM deal_contacts WHERE id = ?", (contact_id,))
        exists = c.fetchone() is not None

        if dry_run:
            conn.close()
            return ("update" if exists else "insert", contact_id)

        if exists:
            cols = [k for k in record.keys() if k not in ("id", "created_at")]
            set_clause = ", ".join([f"{k} = ?" for k in cols] + ["updated_at = ?"])
            params = [record[k] for k in cols] + [now, contact_id]
            c.execute(f"UPDATE deal_contacts SET {set_clause} WHERE id = ?", params)
            action = "update"
        else:
            cols = list(record.keys())
            placeholders = ",".join(["?"] * len(cols))
            params = [record[k] for k in cols]
            c.execute(
                f"INSERT INTO deal_contacts ({','.join(cols)}) VALUES ({placeholders})",
                params,
            )
            action = "insert"

        conn.commit()
        conn.close()
        return (action, contact_id)

    def set_entity_state(self, entity_type: str, entity_id: str, notion_page_id: str, notion_last_edited_time: str, dry_run: bool) -> None:
        now = _now_iso()
        if dry_run:
            return
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO notion_entity_state (entity_type, entity_id, notion_page_id, notion_last_edited_time, last_pull_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(entity_type, entity_id) DO UPDATE SET
              notion_page_id=excluded.notion_page_id,
              notion_last_edited_time=excluded.notion_last_edited_time,
              last_pull_at=excluded.last_pull_at
            """,
            (entity_type, entity_id, notion_page_id, notion_last_edited_time, now),
        )
        conn.commit()
        conn.close()

    def get_entity_state(self, entity_type: str, entity_id: str) -> Optional[dict]:
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM notion_entity_state
            WHERE entity_type = ? AND entity_id = ?
            LIMIT 1
            """,
            (entity_type, entity_id),
        )
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def enqueue_outbox(self, entity_type: str, entity_id: str, notion_page_id: str, action_type: str, payload: dict, dry_run: bool) -> Optional[int]:
        if dry_run:
            return None
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO notion_outbox (entity_type, entity_id, notion_page_id, action_type, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (entity_type, entity_id, notion_page_id, action_type, json.dumps(payload, ensure_ascii=False), _now_iso()),
        )
        outbox_id = c.lastrowid
        conn.commit()
        conn.close()
        return int(outbox_id)

    def list_outbox(self, limit: int = 100) -> List[dict]:
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM notion_outbox
            WHERE status = 'pending'
            ORDER BY id ASC
            LIMIT ?
            """,
            (int(limit),),
        )
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def mark_outbox(self, outbox_id: int, status: str, error: Optional[str] = None) -> None:
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """
            UPDATE notion_outbox
            SET status = ?, synced_at = ?, error = ?
            WHERE id = ?
            """,
            (status, _now_iso(), error, int(outbox_id)),
        )
        conn.commit()
        conn.close()


def load_mapping(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Mapping config not found: {path}")
    return json.loads(p.read_text())


def load_cached_pages(cache_dir: str, key: str) -> List[dict]:
    p = Path(cache_dir) / f"{key}.json"
    if not p.exists():
        raise FileNotFoundError(f"Cache file not found: {p}")
    data = json.loads(p.read_text())
    if isinstance(data, dict) and "results" in data:
        return data.get("results") or []
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported cache format: {p}")


def resolve_bidirectional(local_val: Any, notion_val: Any, local_updated_at: Optional[str], notion_last_edited_time: Optional[str]) -> Any:
    """Most recently modified wins (best-effort)."""
    ldt = _parse_iso(local_updated_at)
    ndt = _parse_iso(notion_last_edited_time)

    # If we can't compare, prefer Notion to avoid pushing stale local.
    if not ldt or not ndt:
        return notion_val

    if ndt > ldt:
        return notion_val
    return local_val


def pull_sync(db: DealDB, mapping: dict, notion: Optional[NotionClient], cache_dir: Optional[str], dry_run: bool) -> dict:
    db.ensure_schema()

    totals = {"insert": 0, "update": 0, "skipped": 0}

    for key, cfg in mapping.items():
        database_id = cfg["database_id"]
        local_cfg = cfg.get("local") or {}
        fields = cfg.get("fields") or {}

        if cache_dir:
            pages = load_cached_pages(cache_dir, key)
        else:
            if not notion:
                raise RuntimeError("No cache-dir and no NOTION_TOKEN provided. Use --cache-dir for dry-run.")
            pages = notion.query_database(database_id)

        for page in pages:
            page_id = page.get("id")
            notion_last_edited = page.get("last_edited_time")

            if local_cfg.get("table") == "deals":
                existing = db.get_deal_by_notion_page(page_id)

                company_prop = None
                # Use the first notion_to_local/title field as the identity anchor
                for fcfg in fields.values():
                    if fcfg.get("type") == "title":
                        company_prop = fcfg.get("notion")
                        break
                company = extract_notion_property(page, company_prop or "Company", "title")

                deal_id = None
                if existing:
                    deal_id = existing["id"]
                else:
                    prefix = local_cfg.get("id_prefix") or "deal"
                    deal_id = f"{prefix}-{_slugify(company)[:30]}" if company else f"{prefix}-{_slugify(page_id)[:16]}"

                record: Dict[str, Any] = {
                    "id": deal_id,
                    "deal_type": local_cfg.get("deal_type") or "careerspan_acquirer",
                    "pipeline": local_cfg.get("pipeline") or "careerspan",
                    "external_source": "notion",
                    "external_id": page_id,
                    "company": company or "(unknown)",
                    "last_touched": _now_iso(),
                }

                # Merge mapped fields
                local_updated_at = (existing or {}).get("updated_at") if existing else None
                for fkey, fcfg in fields.items():
                    direction = fcfg.get("direction")
                    prop_name = fcfg.get("notion")
                    local_col = fcfg.get("local")
                    ptype = fcfg.get("type")

                    notion_val = extract_notion_property(page, prop_name, ptype)

                    if direction == "notion_to_local":
                        if local_col:
                            record[local_col] = notion_val
                    elif direction == "bidirectional":
                        if local_col:
                            local_val = (existing or {}).get(local_col)
                            record[local_col] = resolve_bidirectional(local_val, notion_val, local_updated_at, notion_last_edited)
                    else:
                        # local_to_notion: ignore on pull
                        pass

                action, _ = db.upsert_deal(record, dry_run=dry_run)
                totals[action] += 1
                db.set_entity_state("deal", deal_id, page_id, notion_last_edited or "", dry_run=dry_run)

            elif local_cfg.get("table") == "deal_contacts":
                existing = db.get_contact_by_notion_page(page_id)

                name_prop = None
                for fcfg in fields.values():
                    if fcfg.get("type") == "title":
                        name_prop = fcfg.get("notion")
                        break
                full_name = extract_notion_property(page, name_prop or "Name", "title")

                contact_id = None
                if existing:
                    contact_id = existing["id"]
                else:
                    contact_id = f"{local_cfg.get('contact_type','contact')}-{_slugify(full_name)[:40]}" if full_name else f"contact-{_slugify(page_id)[:16]}"

                record = {
                    "id": contact_id,
                    "contact_type": local_cfg.get("contact_type") or "broker",
                    "pipeline": local_cfg.get("pipeline") or "careerspan",
                    "full_name": full_name or "(unknown)",
                    "source_system": "notion",
                    "source_id": page_id,
                    "created_at": _now_iso(),
                    "updated_at": _now_iso(),
                }

                local_updated_at = (existing or {}).get("updated_at") if existing else None
                for fkey, fcfg in fields.items():
                    direction = fcfg.get("direction")
                    prop_name = fcfg.get("notion")
                    local_col = fcfg.get("local")
                    ptype = fcfg.get("type")
                    notion_val = extract_notion_property(page, prop_name, ptype)

                    if direction == "notion_to_local":
                        if local_col:
                            record[local_col] = notion_val
                    elif direction == "bidirectional":
                        if local_col:
                            local_val = (existing or {}).get(local_col)
                            record[local_col] = resolve_bidirectional(local_val, notion_val, local_updated_at, notion_last_edited)

                action, _ = db.upsert_contact(record, dry_run=dry_run)
                totals[action] += 1
                db.set_entity_state("contact", contact_id, page_id, notion_last_edited or "", dry_run=dry_run)

            else:
                totals["skipped"] += 1

    return totals


def compute_push(db: DealDB, mapping: dict, dry_run: bool) -> dict:
    db.ensure_schema()

    planned = []

    conn = db.connect()
    c = conn.cursor()

    # Deals
    c.execute(
        """
        SELECT id, company, stage, temperature, next_action, last_touched, updated_at, external_id
        FROM deals
        WHERE external_source = 'notion' AND external_id IS NOT NULL AND external_id != ''
        """
    )
    deals = [dict(r) for r in c.fetchall()]

    # Contacts
    c.execute(
        """
        SELECT id, contact_type, full_name, blurb, angle_strategy, notes, second_degree_connects, updated_at, source_id
        FROM deal_contacts
        WHERE source_system = 'notion' AND source_id IS NOT NULL AND source_id != ''
        """
    )
    contacts = [dict(r) for r in c.fetchall()]
    conn.close()

    # Build inverse mapping by table
    cfg_by_table: Dict[str, List[Tuple[str, dict]]] = {}
    for key, cfg in mapping.items():
        local_cfg = cfg.get("local") or {}
        table = local_cfg.get("table")
        if not table:
            continue
        cfg_by_table.setdefault(table, []).append((key, cfg))

    # Deal pushes
    for d in deals:
        state = db.get_entity_state("deal", d["id"]) or {}
        notion_last = state.get("notion_last_edited_time")
        ldt = _parse_iso(d.get("updated_at"))
        ndt = _parse_iso(notion_last)

        # Only push if local is newer than last pulled Notion edit
        if not ldt or not ndt or ldt <= ndt:
            continue

        # Find mapping config for deals
        deal_cfg = None
        for key, cfg in cfg_by_table.get("deals", []):
            deal_cfg = cfg
            break
        if not deal_cfg:
            continue

        props: Dict[str, Any] = {}
        for fkey, fcfg in (deal_cfg.get("fields") or {}).items():
            direction = fcfg.get("direction")
            prop_name = fcfg.get("notion")
            local_col = fcfg.get("local")
            ptype = fcfg.get("type")

            if direction not in ("local_to_notion", "bidirectional"):
                continue
            if not prop_name:
                continue

            if local_col:
                val = d.get(local_col)
            else:
                # e.g., intelligence_summary is local->notion, but value comes from outbox for appends
                continue

            props[prop_name] = notion_property_payload(ptype, val)

        if props:
            planned.append({
                "entity_type": "deal",
                "entity_id": d["id"],
                "notion_page_id": d["external_id"],
                "action_type": "update_page_properties",
                "properties": props,
            })

    # Contact pushes
    for ct in contacts:
        state = db.get_entity_state("contact", ct["id"]) or {}
        notion_last = state.get("notion_last_edited_time")
        ldt = _parse_iso(ct.get("updated_at"))
        ndt = _parse_iso(notion_last)
        if not ldt or not ndt or ldt <= ndt:
            continue

        contact_cfg = None
        for key, cfg in cfg_by_table.get("deal_contacts", []):
            local_cfg = cfg.get("local") or {}
            if local_cfg.get("contact_type") == ct.get("contact_type"):
                contact_cfg = cfg
                break
        if not contact_cfg:
            continue

        props: Dict[str, Any] = {}
        for fkey, fcfg in (contact_cfg.get("fields") or {}).items():
            direction = fcfg.get("direction")
            if direction not in ("local_to_notion", "bidirectional"):
                continue
            prop_name = fcfg.get("notion")
            local_col = fcfg.get("local")
            ptype = fcfg.get("type")
            if not prop_name or not local_col:
                continue
            props[prop_name] = notion_property_payload(ptype, ct.get(local_col))

        if props:
            planned.append({
                "entity_type": "contact",
                "entity_id": ct["id"],
                "notion_page_id": ct["source_id"],
                "action_type": "update_page_properties",
                "properties": props,
            })

    # Enqueue outbox
    for item in planned:
        db.enqueue_outbox(
            entity_type=item["entity_type"],
            entity_id=item["entity_id"],
            notion_page_id=item["notion_page_id"],
            action_type=item["action_type"],
            payload={"properties": item["properties"]},
            dry_run=dry_run,
        )

    return {"planned": len(planned)}


def enqueue_intel(db: DealDB, deal_id: str, source_title: str, source_type: str, key_facts: List[str], next_action: Optional[str], next_action_date: Optional[str], dry_run: bool) -> dict:
    db.ensure_schema()

    conn = db.connect()
    c = conn.cursor()
    c.execute(
        """
        SELECT id, stage, external_id, updated_at
        FROM deals
        WHERE id = ?
        LIMIT 1
        """,
        (deal_id,),
    )
    row = c.fetchone()
    conn.close()

    if not row:
        raise RuntimeError(f"Deal not found: {deal_id}")

    d = dict(row)
    notion_page_id = d.get("external_id")
    if not notion_page_id:
        raise RuntimeError(f"Deal {deal_id} has no Notion external_id")

    entry = format_intel_entry(
        date=datetime.now().date().isoformat(),
        source_title=source_title,
        source_type=source_type,
        stage_before=None,
        stage_after=None,
        key_facts=key_facts,
        next_action=next_action,
        next_action_date=next_action_date,
    )

    payload = {
        "entry": entry,
        "next_action": next_action,
        "next_action_date": next_action_date,
    }

    db.enqueue_outbox(
        entity_type="deal",
        entity_id=deal_id,
        notion_page_id=notion_page_id,
        action_type="append_intel",
        payload=payload,
        dry_run=dry_run,
    )

    return {"queued": 1 if not dry_run else 0}


def push_outbox(db: DealDB, mapping: dict, notion: Optional[NotionClient], dry_run: bool, limit: int = 50) -> dict:
    db.ensure_schema()

    if not dry_run and not notion:
        raise RuntimeError("Live push requires NOTION_TOKEN")

    # Find property names for Intelligence Summary / Next Action / Last Meeting
    deal_cfg = None
    for key, cfg in mapping.items():
        if (cfg.get("local") or {}).get("table") == "deals":
            deal_cfg = cfg
            break

    intel_prop = None
    next_action_prop = None
    last_meeting_prop = None
    if deal_cfg:
        for fkey, fcfg in (deal_cfg.get("fields") or {}).items():
            if fkey == "intelligence_summary":
                intel_prop = fcfg.get("notion")
            if fkey == "next_action":
                next_action_prop = fcfg.get("notion")
            if fkey == "last_meeting":
                last_meeting_prop = fcfg.get("notion")

    processed = 0
    errors = 0

    for item in db.list_outbox(limit=limit):
        processed += 1
        outbox_id = item["id"]
        page_id = item["notion_page_id"]
        action_type = item["action_type"]
        payload = json.loads(item["payload_json"])

        if dry_run:
            continue

        try:
            if action_type == "update_page_properties":
                notion.update_page_properties(page_id, payload.get("properties") or {})
                db.mark_outbox(outbox_id, status="synced", error=None)
                continue

            if action_type == "append_intel":
                if not intel_prop:
                    raise RuntimeError("No intelligence_summary mapping configured")

                page = notion.retrieve_page(page_id)
                existing_text = extract_notion_property(page, intel_prop, "rich_text")

                entry = payload.get("entry") or ""
                updated_text = (entry + "\n\n" + existing_text).strip() if existing_text else entry

                props: Dict[str, Any] = {intel_prop: notion_property_payload("rich_text", updated_text)}

                if next_action_prop and payload.get("next_action") is not None:
                    props[next_action_prop] = notion_property_payload("rich_text", payload.get("next_action"))

                if last_meeting_prop:
                    props[last_meeting_prop] = notion_property_payload("date", datetime.now().date().isoformat())

                notion.update_page_properties(page_id, props)
                db.mark_outbox(outbox_id, status="synced", error=None)
                continue

            if action_type == "create":
                # Create a new page in a Notion database
                # payload should contain: database_id, properties
                entity_type = item.get("entity_type")
                
                # Handle broker creation
                if entity_type == "deal_broker":
                    broker_cfg = mapping.get("deal_brokers")
                    if not broker_cfg:
                        raise RuntimeError("No deal_brokers mapping configured")
                    
                    database_id = broker_cfg["database_id"]
                    fields = broker_cfg.get("fields", {})
                    
                    # Build properties from payload (BrokerCandidate.to_dict())
                    props: Dict[str, Any] = {}
                    
                    # Contact (title field)
                    contact_field = fields.get("contact", {})
                    if contact_field.get("notion"):
                        props[contact_field["notion"]] = notion_property_payload(
                            "title", payload.get("name", "Unknown")
                        )
                    
                    # Blurb (rich_text)
                    blurb_field = fields.get("blurb", {})
                    if blurb_field.get("notion"):
                        blurb_content = f"""🤝 Confidence: {int(payload.get('confidence', 0) * 100)}%
Relationship: {payload.get('relationship', 'Unknown')}
Signals: {', '.join(payload.get('signals', []))}
Source: {payload.get('source_meeting', 'Unknown')}"""
                        props[blurb_field["notion"]] = notion_property_payload("rich_text", blurb_content)
                    
                    # Angle/Strategy (rich_text) - network access info
                    angle_field = fields.get("angle_strategy", {})
                    if angle_field.get("notion") and payload.get("network_access"):
                        network_text = "Network access: " + ", ".join(payload.get("network_access", [])[:3])
                        props[angle_field["notion"]] = notion_property_payload("rich_text", network_text)
                    
                    created_page = notion.create_page(database_id, props)
                    
                    # Update entity state with the new Notion page ID
                    entity_id = item.get("entity_id")
                    if entity_id and created_page.get("id"):
                        db.upsert_entity_state(
                            entity_type="deal_broker",
                            entity_id=entity_id,
                            notion_page_id=created_page["id"],
                            notion_last_edited=created_page.get("last_edited_time"),
                            local_updated_at=_now_iso()
                        )
                    
                    db.mark_outbox(outbox_id, status="synced", error=None)
                    continue
                
                raise RuntimeError(f"Unknown entity_type for create action: {entity_type}")

            raise RuntimeError(f"Unknown outbox action_type: {action_type}")

        except Exception as e:
            errors += 1
            db.mark_outbox(outbox_id, status="error", error=str(e)[:400])

    return {"processed": processed, "errors": errors}


def _cmd_pull(args):
    mapping = load_mapping(args.mapping)
    token = os.environ.get("NOTION_TOKEN")
    notion = NotionClient(token) if token else None

    db = DealDB(args.db)
    res = pull_sync(db=db, mapping=mapping, notion=notion, cache_dir=args.cache_dir, dry_run=args.dry_run)
    print(json.dumps({"command": "pull", "dry_run": args.dry_run, "result": res}, indent=2))


def _cmd_compute_push(args):
    mapping = load_mapping(args.mapping)
    db = DealDB(args.db)
    res = compute_push(db=db, mapping=mapping, dry_run=args.dry_run)
    print(json.dumps({"command": "compute-push", "dry_run": args.dry_run, "result": res}, indent=2))


def _cmd_enqueue_intel(args):
    db = DealDB(args.db)
    res = enqueue_intel(
        db=db,
        deal_id=args.deal_id,
        source_title=args.source_title,
        source_type=args.source_type,
        key_facts=args.key_fact or [],
        next_action=args.next_action,
        next_action_date=args.next_action_date,
        dry_run=args.dry_run,
    )
    print(json.dumps({"command": "enqueue-intel", "dry_run": args.dry_run, "result": res}, indent=2))


def _cmd_push(args):
    mapping = load_mapping(args.mapping)
    token = os.environ.get("NOTION_TOKEN")
    notion = NotionClient(token) if token else None

    db = DealDB(args.db)
    res = push_outbox(db=db, mapping=mapping, notion=notion, dry_run=args.dry_run, limit=args.limit)
    print(json.dumps({"command": "push", "dry_run": args.dry_run, "result": res}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Notion bidirectional sync for deals")
    p.add_argument("--db", default=DB_DEFAULT)
    p.add_argument("--mapping", default=MAPPING_DEFAULT)

    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("pull", help="Pull changes from Notion → local DB")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--cache-dir", help="Directory containing <dbkey>.json files (acquirer_targets.json, deal_brokers.json, leadership_targets.json)")
    sp.set_defaults(func=_cmd_pull)

    sp = sub.add_parser("compute-push", help="Compute pending local changes → outbox")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=_cmd_compute_push)

    sp = sub.add_parser("enqueue-intel", help="Queue an Intelligence Summary append for a deal")
    sp.add_argument("--deal-id", required=True)
    sp.add_argument("--source-title", required=True)
    sp.add_argument("--source-type", required=True)
    sp.add_argument("--key-fact", action="append", help="Repeatable")
    sp.add_argument("--next-action")
    sp.add_argument("--next-action-date")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=_cmd_enqueue_intel)

    sp = sub.add_parser("push", help="Execute pending outbox changes → Notion")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=_cmd_push)

    return p


def main() -> int:
    args = build_parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
