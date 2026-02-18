from __future__ import annotations

import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import Config
from .models import RoutingDecision


def _safe_path_fragment(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", (value or "").strip())
    return cleaned[:120] if cleaned else "evt_unknown"


def init_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agentmail_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                svix_id TEXT UNIQUE,
                event_id TEXT,
                event_type TEXT,
                inbox_role TEXT,
                route_queue TEXT,
                sender_email TEXT,
                sender_domain TEXT,
                security_risk TEXT,
                security_decision TEXT,
                payload_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_agentmail_events_created_at ON agentmail_events(created_at DESC)"
        )
        conn.commit()
    finally:
        conn.close()


def is_duplicate(db_path: Path, svix_id: str | None) -> bool:
    if not svix_id:
        return False
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT 1 FROM agentmail_events WHERE svix_id = ? LIMIT 1",
            (svix_id,),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def record_event(db_path: Path, *, svix_id: str | None, event_type: str, decision: RoutingDecision) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO agentmail_events (
                svix_id, event_id, event_type, inbox_role, route_queue,
                sender_email, sender_domain, security_risk, security_decision,
                payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                svix_id,
                decision.event_id,
                event_type,
                decision.inbox_role,
                decision.route_queue,
                decision.sender_email,
                decision.sender_domain,
                decision.security.risk_level,
                decision.security.decision,
                json.dumps(decision.payload, ensure_ascii=True),
                datetime.now(UTC).isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def write_queue_file(cfg: Config, decision: RoutingDecision) -> Path:
    stamp = decision.timestamp.strftime("%Y%m%dT%H%M%S.%fZ")
    event_part = _safe_path_fragment(decision.event_id)
    filename = f"{stamp}_{event_part}.json"

    target_dir = cfg.queue_root / decision.route_queue / decision.inbox_role
    target_dir.mkdir(parents=True, exist_ok=True)

    filepath = target_dir / filename
    payload = {
        "meta": {
            "received_at": decision.timestamp.isoformat(),
            "inbox_role": decision.inbox_role,
            "inbox_key": decision.inbox_key,
            "route_queue": decision.route_queue,
            "event_id": decision.event_id,
            "message_id": decision.message_id,
            "sender_email": decision.sender_email,
            "sender_domain": decision.sender_domain,
        },
        "security": {
            "risk_level": decision.security.risk_level,
            "decision": decision.security.decision,
            "sender_tier": decision.security.sender_tier,
            "confidence": decision.security.confidence,
            "flags": decision.security.flags,
            "rationale": decision.security.rationale,
        },
        "payload": decision.payload,
    }
    filepath.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return filepath


def append_audit(cfg: Config, entry: dict[str, Any]) -> None:
    cfg.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=True)
    with cfg.audit_log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
