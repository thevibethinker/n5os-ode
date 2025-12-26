"""Forensics and logging helpers for Tutor sessions.

This is an initial skeleton; real implementations will add structured
JSONL logging and hash chaining for tamper detection.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


LOG_ROOT = Path("/home/workspace/Logs/tutor_sessions")

Direction = Literal["inbound", "outbound"]


@dataclass
class LogEntry:
    session_id: str
    direction: Direction
    message_type: str
    byte_count: int
    payload_sha256: str
    timestamp: datetime


def _ensure_log_dir() -> Path:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    return LOG_ROOT


def log_message(
    session_id: str,
    direction: Direction,
    message_type: str,
    payload: bytes,
    payload_sha256: str,
) -> None:
    """Append a simple line-based log entry for this message.

    This keeps the shape minimal for now; we can move to structured JSONL
    with hash chaining in a later iteration.
    """

    log_dir = _ensure_log_dir()
    log_path = log_dir / f"{session_id}.log"
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts}\t{direction}\t{message_type}\t{len(payload)}\t{payload_sha256}\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)

