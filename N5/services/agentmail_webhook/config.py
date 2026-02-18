from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_DIR = Path("/home/workspace")


@dataclass(frozen=True)
class Config:
    host: str = os.getenv("AGENTMAIL_WEBHOOK_HOST", "0.0.0.0")
    port: int = int(os.getenv("AGENTMAIL_WEBHOOK_PORT", "8791"))
    max_request_size_bytes: int = int(os.getenv("AGENTMAIL_MAX_REQUEST_SIZE_BYTES", str(1024 * 1024)))
    webhook_secret: str = os.getenv("AGENTMAIL_WEBHOOK_SECRET", "")
    allow_insecure: bool = os.getenv("AGENTMAIL_ALLOW_INSECURE", "0") in {"1", "true", "True"}
    unknown_senders_review: bool = os.getenv("AGENTMAIL_UNKNOWN_SENDERS_REVIEW", "1") in {"1", "true", "True"}

    data_db_path: Path = BASE_DIR / "N5/data/agentmail_webhooks.db"
    audit_log_path: Path = BASE_DIR / "N5/logs/agentmail_webhook_audit.jsonl"
    queue_root: Path = BASE_DIR / "N5/inbox/agentmail"

    @staticmethod
    def inbox_role_map() -> dict[str, str]:
        default_map: dict[str, str] = {
            "careerspan.n5os@agentmail.to": "careerspan",
            "hotline.n5os@agentmail.to": "hotline",
            "n5os@agentmail.to": "ops",
        }
        raw = os.getenv("AGENTMAIL_INBOX_ROLE_MAP")
        if not raw:
            return default_map
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                normalized: dict[str, str] = {}
                for key, value in parsed.items():
                    if isinstance(key, str) and isinstance(value, str):
                        normalized[key.strip().lower()] = value.strip().lower()
                return normalized or default_map
        except json.JSONDecodeError:
            return default_map
        return default_map

    @staticmethod
    def trusted_sender_domains() -> set[str]:
        raw = os.getenv("AGENTMAIL_TRUSTED_SENDER_DOMAINS", "")
        return {part.strip().lower() for part in raw.split(",") if part.strip()}

    @staticmethod
    def trusted_senders() -> set[str]:
        raw = os.getenv("AGENTMAIL_TRUSTED_SENDERS", "")
        return {part.strip().lower() for part in raw.split(",") if part.strip()}

    @classmethod
    def validate(cls) -> tuple[bool, str | None]:
        cfg = cls()
        if not cfg.allow_insecure and not cfg.webhook_secret:
            return False, "AGENTMAIL_WEBHOOK_SECRET is required unless AGENTMAIL_ALLOW_INSECURE=1"
        if cfg.webhook_secret and not cfg.webhook_secret.startswith("whsec_"):
            return False, "AGENTMAIL_WEBHOOK_SECRET must start with 'whsec_'"

        cfg.data_db_path.parent.mkdir(parents=True, exist_ok=True)
        cfg.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        cfg.queue_root.mkdir(parents=True, exist_ok=True)

        role_map = cls.inbox_role_map()
        if not role_map:
            return False, "AGENTMAIL_INBOX_ROLE_MAP resolved to empty mapping"

        return True, None


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
