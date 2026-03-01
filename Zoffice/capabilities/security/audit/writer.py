"""
Security Capability — Audit Writer

Writes immutable audit entries to office.db with SHA-256 hash verification.
All capabilities MUST call log_audit() for every action they perform.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import duckdb

_DEFAULT_DB = str(Path(__file__).resolve().parents[2] / "data" / "office.db")
_conn_cache: dict[str, duckdb.DuckDBPyConnection] = {}


def _get_config() -> dict:
    """Load audit config from capability config.yaml."""
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    if config_path.exists():
        import yaml
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        return cfg.get("audit", {})
    return {}


def _get_conn(db_path: str | None = None) -> duckdb.DuckDBPyConnection:
    """Get or create a DuckDB connection."""
    if db_path is None:
        cfg = _get_config()
        db_path = cfg.get("db_path", _DEFAULT_DB)
    # Resolve relative paths from workspace root
    p = Path(db_path)
    if not p.is_absolute():
        p = Path(__file__).resolve().parents[4] / db_path
    db_path = str(p)
    if db_path not in _conn_cache:
        _conn_cache[db_path] = duckdb.connect(db_path)
    return _conn_cache[db_path]


def _compute_hash(action: str, metadata: dict | None) -> str:
    """SHA-256 hash of action + json(metadata) for tamper detection."""
    payload = action + json.dumps(metadata or {}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def log_audit(
    capability: str,
    employee: str | None,
    action: str,
    channel: str | None = None,
    counterparty: str | None = None,
    metadata: dict | None = None,
    parent_event_id: str | None = None,
    db_path: str | None = None,
) -> str:
    """
    Write an immutable audit entry.

    Args:
        capability: Name of the capability logging this event (e.g. "security", "memory").
        employee: Employee slug or None for system-level events.
        action: What happened (e.g. "inbound_gate_check", "contact_upsert").
        channel: Communication channel if applicable (email, voice, webhook, zo2zo).
        counterparty: External party involved, if any.
        metadata: Arbitrary JSON-serializable dict with event details.
        parent_event_id: UUID of a parent audit event for chaining.
        db_path: Override DB path (mainly for testing).

    Returns:
        UUID string of the created audit entry.
    """
    conn = _get_conn(db_path)
    entry_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc)
    content_hash = _compute_hash(action, metadata)
    meta_json = json.dumps(metadata, default=str) if metadata else None

    conn.execute(
        """
        INSERT INTO audit (id, timestamp, capability, employee, action,
                           channel, counterparty, content_hash, metadata, parent_event_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [entry_id, ts, capability, employee, action,
         channel, counterparty, content_hash, meta_json, parent_event_id],
    )
    return entry_id
