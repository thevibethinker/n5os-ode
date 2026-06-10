#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import requests

from N5.lib.paths import N5_DATA_DIR, WORKSPACE_ROOT

DB_PATH = N5_DATA_DIR / "taskintake.db"
SCHEMA_PATH = WORKSPACE_ROOT / "Skills" / "google-tasks-bridge" / "references" / "schema.sql"
GOOGLE_TASKS_API_BASE = "https://tasks.googleapis.com/tasks/v1"
DEFAULT_LIST_TITLE = "Zo Commands"
DEFAULT_INBOUND_LIST_TITLE = "Zo Inbound Tasks"
DEFAULT_RECEIPTS_LIST_TITLE = "Zo Command Receipts"
TASK_OUTPUTS_ROOT = N5_DATA_DIR.parent / "task_system" / "outputs" / "zo-tasks"
ZO_ASK_URL = "https://api.zo.computer/zo/ask"
DEFAULT_MODEL = "openai:gpt-5.4-2026-03-05"
STALE_JOB_AFTER_MINUTES = 5
GOOGLE_TASKS_TOKEN_PATH = Path("/home/.z/google-oauth/token.json")
GOOGLE_TASKS_SCOPE = "https://www.googleapis.com/auth/tasks"
GOOGLE_OAUTH_FALLBACK_ENV = {
    "GOOGLE_TASKS_CLIENT_ID": "GOOGLE_OAUTH_CLIENT_ID",
    "GOOGLE_TASKS_CLIENT_SECRET": "GOOGLE_OAUTH_CLIENT_SECRET",
    "GOOGLE_TASKS_REFRESH_TOKEN": "GOOGLE_OAUTH_REFRESH_TOKEN",
}
INBOUND_META_START = "[Zo inbound meta]"
INBOUND_META_END = "[/Zo inbound meta]"
INBOUND_HIGH_CONFIDENCE = 0.75


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    ensure_parent_dir(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def initialize_db(db_path: Path = DB_PATH) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.executescript(schema)
        conn.commit()


def set_state(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO sync_state (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """,
        (key, value, utc_now_iso()),
    )


def get_state(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM sync_state WHERE key = ?", (key,)).fetchone()
    return str(row["value"]) if row else None


def _resolve_credential(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value
    fallback_name = GOOGLE_OAUTH_FALLBACK_ENV.get(name)
    if fallback_name:
        fallback_value = os.environ.get(fallback_name)
        if fallback_value:
            return fallback_value
    return None


def _load_token_store() -> dict[str, Any]:
    if not GOOGLE_TASKS_TOKEN_PATH.exists():
        return {}
    try:
        payload = json.loads(GOOGLE_TASKS_TOKEN_PATH.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def get_google_tasks_client() -> tuple[str, str, str, str | None]:
    client_id = _resolve_credential("GOOGLE_TASKS_CLIENT_ID")
    client_secret = _resolve_credential("GOOGLE_TASKS_CLIENT_SECRET")
    refresh_token = _resolve_credential("GOOGLE_TASKS_REFRESH_TOKEN")
    access_token = os.environ.get("GOOGLE_TASKS_ACCESS_TOKEN") or None
    if not access_token:
        payload = _load_token_store()
        if payload:
            token_access_token = str(payload.get("access_token") or "").strip()
            if token_access_token:
                access_token = token_access_token
    if client_id and client_secret and refresh_token:
        return client_id, client_secret, refresh_token, access_token

    payload = _load_token_store()
    if payload:
        scope_blob = payload.get("scope") or payload.get("scopes") or ""
        if isinstance(scope_blob, list):
            scopes = [str(item).strip() for item in scope_blob]
        else:
            scopes = [item.strip() for item in str(scope_blob).split() if item.strip()]
        if GOOGLE_TASKS_SCOPE in scopes:
            token_client_id = str(payload.get("client_id") or "").strip()
            token_client_secret = str(payload.get("client_secret") or "").strip()
            token_refresh_token = str(payload.get("refresh_token") or "").strip()
            token_access_token = str(payload.get("access_token") or "").strip() or None
            if token_client_id and token_client_secret and token_refresh_token:
                return token_client_id, token_client_secret, token_refresh_token, token_access_token

    missing = [
        name
        for name, value in [
            ("GOOGLE_TASKS_CLIENT_ID", client_id),
            ("GOOGLE_TASKS_CLIENT_SECRET", client_secret),
            ("GOOGLE_TASKS_REFRESH_TOKEN", refresh_token),
        ]
        if not value
    ]
    token_hint = f" or fallback token store {GOOGLE_TASKS_TOKEN_PATH}" if GOOGLE_TASKS_TOKEN_PATH else ""
    if missing:
        raise SystemExit("Missing required Google Tasks secrets: " + ", ".join(missing) + token_hint)
    return client_id or "", client_secret or "", refresh_token or "", access_token


class GoogleTasksClient:
    def __init__(self) -> None:
        self.client_id, self.client_secret, self.refresh_token, self._access_token = get_google_tasks_client()

    def _refresh_access_token(self) -> str:
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("access_token")
        if not token:
            raise RuntimeError("Google token refresh returned no access_token")
        self._access_token = token
        return token

    def _headers(self) -> dict[str, str]:
        token = self._access_token or self._refresh_access_token()
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def _request(self, method: str, path: str, *, params: dict[str, Any] | None = None, json_body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{GOOGLE_TASKS_API_BASE}{path}"
        resp = requests.request(method, url, headers=self._headers(), params=params, json=json_body, timeout=30)
        if resp.status_code == 401:
            self._refresh_access_token()
            resp = requests.request(method, url, headers=self._headers(), params=params, json=json_body, timeout=30)
        resp.raise_for_status()
        if not resp.text.strip():
            return {}
        return resp.json()

    def list_tasklists(self, max_results: int = 100) -> list[dict[str, Any]]:
        data = self._request("GET", "/users/@me/lists", params={"maxResults": max_results})
        return list(data.get("items", []) or [])

    def create_tasklist(self, title: str) -> dict[str, Any]:
        return self._request("POST", "/users/@me/lists", json_body={"title": title})

    def list_tasks(self, list_id: str, max_results: int = 100, show_completed: bool = True, show_hidden: bool = True) -> list[dict[str, Any]]:
        data = self._request(
            "GET",
            f"/lists/{list_id}/tasks",
            params={
                "maxResults": max_results,
                "showCompleted": str(show_completed).lower(),
                "showHidden": str(show_hidden).lower(),
                "showDeleted": "false",
            },
        )
        return list(data.get("items", []) or [])

    def create_task(self, list_id: str, title: str, notes: str = "", due: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"title": title}
        if notes:
            body["notes"] = notes
        if due:
            body["due"] = normalize_google_due_timestamp(due)
        return self._request("POST", f"/lists/{list_id}/tasks", json_body=body)


def normalize_title(title: str) -> str:
    text = " ".join((title or "").split())
    for suffix in ("@run", "@N5"):
        text = text.replace(suffix, "")
    return " ".join(text.split()).strip()


def canonical_task_key(title: str) -> str:
    lowered = normalize_title(title).lower()
    compact = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(compact.split()).strip()


def parse_isoish_datetime(value: str | None) -> tuple[datetime | None, int]:
    text = str(value or "").strip()
    if not text:
        return None, 0
    try:
        if len(text) == 10 and re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return datetime.fromisoformat(f"{text}T00:00:00+00:00"), 1
        normalized = text.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        precision = 2 if "T" in text else 1
        return dt.astimezone(timezone.utc), precision
    except ValueError:
        return None, 0


def normalize_google_due_timestamp(value: str | None) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return f"{text}T00:00:00.000Z"
    return text


def should_replace_due_date(existing_due: str | None, incoming_due: str | None) -> bool:
    if not incoming_due:
        return False
    if not existing_due:
        return True
    existing_dt, existing_precision = parse_isoish_datetime(existing_due)
    incoming_dt, incoming_precision = parse_isoish_datetime(incoming_due)
    if incoming_dt is None:
        return False
    if existing_dt is None:
        return True
    if incoming_precision > existing_precision:
        return incoming_dt >= existing_dt
    if incoming_precision == existing_precision:
        return incoming_dt > existing_dt
    return False


def first_sentence(text: str) -> str:
    clean = re.sub(r"\s+", " ", str(text or "").strip())
    if not clean:
        return ""
    match = re.match(r"(.+?[.!?])(?:\s|$)", clean)
    if match:
        return match.group(1).strip()
    return clean


def normalize_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").strip().lower()).strip()


def split_markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in str(text or "").splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", raw_line.strip())
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(raw_line.rstrip())
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def bullet_blocks(section_text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for raw_line in str(section_text or "").splitlines():
        if re.match(r"^\s*-\s+", raw_line):
            if current:
                blocks.append("\n".join(current).strip())
            current = [re.sub(r"^\s*-\s+", "", raw_line).strip()]
            continue
        if current and (raw_line.startswith("  ") or raw_line.startswith("\t") or raw_line.strip()):
            current.append(raw_line.strip())
    if current:
        blocks.append("\n".join(current).strip())
    return [block for block in blocks if block]


def extract_labeled_fields(block_text: str, labels: list[str]) -> dict[str, str]:
    pattern = re.compile(
        r"(?:\*\*|`)?(" + "|".join(re.escape(label) for label in labels) + r")(?:\*\*|`)?\s*:\s*",
        flags=re.IGNORECASE,
    )
    matches = list(pattern.finditer(block_text))
    if not matches:
        return {}
    fields: dict[str, str] = {}
    for idx, match in enumerate(matches):
        raw_label = match.group(1)
        label = next((candidate for candidate in labels if candidate.lower() == raw_label.lower()), raw_label)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block_text)
        value = block_text[start:end].strip(" \n\t`*")
        fields[label] = re.sub(r"\s+", " ", value).strip()
    return fields


def resolve_deadline_to_due(deadline: str | None, meeting_date: str | None) -> str | None:
    text = str(deadline or "").strip()
    base = str(meeting_date or "").strip()
    if not text or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", base):
        return None
    lowered = text.lower()
    explicit = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", lowered)
    if explicit:
        return explicit.group(1)
    try:
        meeting_dt = datetime.fromisoformat(f"{base}T00:00:00+00:00")
    except ValueError:
        return None
    if "tomorrow" in lowered:
        return (meeting_dt + timedelta(days=1)).date().isoformat()
    if "today" in lowered or "tonight" in lowered or "right away" in lowered:
        return meeting_dt.date().isoformat()
    if re.search(r"\bby the morning\b", lowered):
        return (meeting_dt + timedelta(days=1)).date().isoformat()
    return None


def build_s02_task_title(task_text: str | None, first_step: str | None) -> tuple[str, str | None]:
    task = re.sub(r"\s+", " ", str(task_text or "").strip()).strip("`* ")
    if task:
        return task.rstrip("."), None
    fallback = first_sentence(str(first_step or "")).rstrip(".")
    if fallback:
        return fallback[:180], "Missing explicit `Task:` field in S02 item; title inferred from first step."
    return "", "S02 item is missing both `Task:` and `First step:` fields."


def parse_s02_v_owned_items(s02_content: str, meeting_date: str | None = None) -> list[dict[str, Any]]:
    sections = split_markdown_sections(s02_content)
    section_text = next(
        (value for heading, value in sections.items() if normalize_heading(heading) == "v owned next moves"),
        "",
    )
    if not section_text:
        return []

    items: list[dict[str, Any]] = []
    labels = ["Task", "Owner", "Why V owns it", "First step", "Deadline/check-in", "Deadline", "Check-in"]
    for block in bullet_blocks(section_text):
        fields = extract_labeled_fields(block, labels)
        title, title_reason = build_s02_task_title(fields.get("Task"), fields.get("First step"))
        if not title:
            items.append(
                {
                    "status": "skipped",
                    "reason": title_reason or "Missing usable task title.",
                    "raw_text": block,
                }
            )
            continue

        deadline_text = (
            fields.get("Deadline/check-in")
            or fields.get("Deadline")
            or fields.get("Check-in")
            or ""
        ).strip()
        due = resolve_deadline_to_due(deadline_text, meeting_date)
        confidence = 0.92
        reasons: list[str] = []
        owner = str(fields.get("Owner") or "").strip()
        normalized_owner = re.sub(r"[^a-z]+", "", owner.lower())
        why_owned = str(fields.get("Why V owns it") or "").strip()
        first_step = str(fields.get("First step") or "").strip()
        if title_reason:
            confidence = min(confidence, 0.74)
            reasons.append(title_reason)
        if owner and normalized_owner not in {"v", "<YOUR_NAME>", "<YOUR_GITHUB>", "va"}:
            confidence = min(confidence, 0.68)
            reasons.append(f"S02 owner field was `{owner}`, not a clean V label.")
        if not why_owned:
            confidence = min(confidence, 0.78)
            reasons.append("Missing `Why V owns it:` support in S02 item.")
        if not first_step:
            confidence = min(confidence, 0.7)
            reasons.append("Missing `First step:` detail in S02 item.")

        normalized_block = re.sub(r"\s+", " ", block).strip()
        notes_lines = [
            f"Meeting: {meeting_date or 'Unknown date'} / {title}",
            "Source block: S02_ACTIONS.md",
        ]
        if why_owned:
            notes_lines.append(f"Why V owns it: {why_owned}")
        if first_step:
            notes_lines.append(f"First step: {first_step}")
        if deadline_text:
            notes_lines.append(f"Deadline/check-in: {deadline_text}")
        notes_lines.append(f"Raw S02 item: {normalized_block}")

        items.append(
            {
                "status": "ready",
                "title": title,
                "notes": "\n".join(notes_lines).strip(),
                "due": due,
                "confidence": round(confidence, 4),
                "low_confidence_reason": "; ".join(reasons) if reasons else None,
                "raw_text": block,
            }
        )
    return items


def extract_inbound_meta(notes: str | None) -> tuple[dict[str, Any], str]:
    text = str(notes or "")
    if INBOUND_META_START not in text or INBOUND_META_END not in text:
        return {}, text.strip()
    before, _, rest = text.partition(INBOUND_META_START)
    meta_block, _, _ = rest.partition(INBOUND_META_END)
    try:
        metadata = json.loads(meta_block.strip())
        if not isinstance(metadata, dict):
            metadata = {}
    except json.JSONDecodeError:
        metadata = {}
    return metadata, before.strip()


def render_inbound_notes(metadata: dict[str, Any]) -> str:
    confidence = metadata.get("confidence")
    low_confidence_reason = str(metadata.get("low_confidence_reason") or "").strip()
    recommit_count = int(metadata.get("recommit_count") or 1)
    source_events = metadata.get("source_events") if isinstance(metadata.get("source_events"), list) else []

    lines: list[str] = []
    if isinstance(confidence, (int, float)) and float(confidence) < INBOUND_HIGH_CONFIDENCE:
        reason = low_confidence_reason or "Ownership or extraction confidence is ambiguous."
        lines.append(f"Low confidence capture ({float(confidence):.2f}): {reason}")
    if recommit_count > 1:
        lines.append(f"Recommitted {recommit_count}x.")
    linked_prior = str(metadata.get("linked_prior_completed_task_id") or "").strip()
    if linked_prior:
        lines.append(f"Linked prior completed equivalent: {linked_prior}")
    if metadata.get("due_status_note"):
        lines.append(str(metadata["due_status_note"]))
    if source_events:
        lines.append("")
        lines.append("Source log:")
        for event in source_events[-5:]:
            source_type = str(event.get("source_type") or "unknown").strip() or "unknown"
            source_id = str(event.get("source_id") or "unknown").strip() or "unknown"
            source_line = f"- {source_type}:{source_id}"
            event_confidence = event.get("confidence")
            if isinstance(event_confidence, (int, float)):
                source_line += f" (confidence {float(event_confidence):.2f})"
            if event.get("due"):
                source_line += f", due {event['due']}"
            lines.append(source_line)
            summary = str(event.get("summary") or "").strip()
            if summary:
                lines.append(summary)
    lines.extend(["", INBOUND_META_START, json.dumps(metadata, sort_keys=True), INBOUND_META_END])
    return "\n".join(lines).strip()


def record_google_task_event(
    conn: sqlite3.Connection,
    task_id: str,
    list_id: str,
    *,
    event_type: str,
    summary: str,
    payload: dict[str, Any],
    dedupe_key: str,
    event_at: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO google_task_events (
            task_id, list_id, event_type, event_at, summary, payload_json, dedupe_key
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            list_id,
            event_type,
            event_at or utc_now_iso(),
            summary,
            json.dumps(payload, sort_keys=True),
            dedupe_key,
        ),
    )


def sync_inbound_task_to_ledger(
    conn: sqlite3.Connection,
    list_item: dict[str, Any],
    task: dict[str, Any],
    *,
    metadata: dict[str, Any],
    event_type: str,
    summary: str,
) -> None:
    observed_at = utc_now_iso()
    upsert_list(conn, list_item, observed_at)
    upsert_task(conn, task, str(list_item["id"]), observed_at, None)
    conn.execute(
        """
        UPDATE intake_candidates
        SET parser_confidence = ?,
            classifier_confidence = ?,
            functional_area = ?,
            intent_class = ?,
            candidate_status = ?,
            notes = ?,
            classification_json = ?
        WHERE task_id = ?
        """,
        (
            metadata.get("confidence"),
            metadata.get("confidence"),
            "personal_inbound",
            "inbound_task",
            "observed",
            task.get("notes") or "",
            json.dumps({"channel": "zo_inbound", **metadata}, sort_keys=True),
            task.get("id"),
        ),
    )
    event_key = ""
    source_events = metadata.get("source_events")
    if isinstance(source_events, list) and source_events:
        event_key = str(source_events[-1].get("event_key") or "")
    record_google_task_event(
        conn,
        str(task["id"]),
        str(list_item["id"]),
        event_type=event_type,
        summary=summary,
        payload={"task": task, "metadata": metadata},
        dedupe_key=f"{task['id']}:{event_type}:{event_key or metadata.get('canonical_key') or task.get('id')}",
        event_at=observed_at,
    )


def upsert_inbound_task(
    client: GoogleTasksClient,
    *,
    title: str,
    notes: str = "",
    due: str | None = None,
    confidence: float = 1.0,
    source_type: str,
    source_id: str,
    source_event_key: str,
    list_title: str = DEFAULT_INBOUND_LIST_TITLE,
    low_confidence_reason: str | None = None,
    db_path: Path = DB_PATH,
) -> dict[str, Any]:
    canonical_key = canonical_task_key(title)
    list_item, _ = ensure_task_list(client, list_title)
    try:
        items = client.list_tasks(list_item["id"], max_results=200, show_completed=True, show_hidden=True)
    except TypeError:
        items = client.list_tasks(list_item["id"], max_results=200)
    equivalents = [
        item for item in items
        if canonical_task_key(str(item.get("title") or "")) == canonical_key and not item.get("deleted")
    ]
    active_equivalent = next((item for item in equivalents if item.get("status") != "completed" and not item.get("hidden")), None)
    completed_equivalent = next((item for item in equivalents if item.get("status") == "completed"), None)

    source_event = {
        "event_key": source_event_key,
        "source_type": source_type,
        "source_id": source_id,
        "captured_at": utc_now_iso(),
        "confidence": round(float(confidence), 4),
        "due": due,
        "summary": notes.strip(),
    }
    if low_confidence_reason:
        source_event["low_confidence_reason"] = low_confidence_reason

    action = "created"
    due_status_note = ""

    if active_equivalent is not None:
        metadata, _ = extract_inbound_meta(active_equivalent.get("notes"))
        existing_events = metadata.get("source_events") if isinstance(metadata.get("source_events"), list) else []
        existing_ids = {str(event.get("event_key") or "") for event in existing_events}
        is_new_event = source_event_key not in existing_ids
        if is_new_event:
            existing_events.append(source_event)
        metadata["source_events"] = existing_events
        metadata["canonical_key"] = canonical_key
        metadata["recommit_count"] = max(int(metadata.get("recommit_count") or 1), len(existing_events))
        metadata["confidence"] = min(float(metadata.get("confidence") or confidence), float(confidence))
        if low_confidence_reason:
            metadata["low_confidence_reason"] = low_confidence_reason
        if should_replace_due_date(active_equivalent.get("due"), due):
            task_due = due
            due_status_note = "Due date updated from newer or more specific source."
        else:
            task_due = active_equivalent.get("due")
            if is_new_event and due and active_equivalent.get("due"):
                due_status_note = "Due date preserved because incoming date was not newer and more specific."
            else:
                due_status_note = str(metadata.get("due_status_note") or "")
        metadata["due_status_note"] = due_status_note
        updated_notes = render_inbound_notes(metadata)
        if (
            updated_notes == (active_equivalent.get("notes") or "").strip()
            and task_due == active_equivalent.get("due")
        ):
            action = "noop_existing_event"
            task_payload = dict(active_equivalent)
        else:
            action = "updated_existing"
            task_payload = update_task_on_google(
                client,
                str(list_item["id"]),
                str(active_equivalent["id"]),
                title=str(active_equivalent.get("title") or title).strip(),
                notes=updated_notes,
                due=task_due,
            )
    else:
        prior_metadata, _ = extract_inbound_meta((completed_equivalent or {}).get("notes"))
        prior_events = prior_metadata.get("source_events") if isinstance(prior_metadata.get("source_events"), list) else []
        source_events = [*prior_events, source_event]
        recommit_count = max(int(prior_metadata.get("recommit_count") or 0) + 1, len(source_events), 1)
        metadata = {
            "canonical_key": canonical_key,
            "confidence": round(float(confidence), 4),
            "low_confidence_reason": low_confidence_reason or "",
            "source_events": source_events,
            "recommit_count": recommit_count,
            "linked_prior_completed_task_id": str((completed_equivalent or {}).get("id") or ""),
            "due_status_note": "",
        }
        rendered_notes = render_inbound_notes(metadata)
        task_payload = client.create_task(str(list_item["id"]), normalize_title(title), notes=rendered_notes, due=due)
        if completed_equivalent is not None:
            action = "created_linked_recommit"

    task_payload.setdefault("notes", task_payload.get("notes") or render_inbound_notes(metadata))
    task_payload.setdefault("title", normalize_title(title))
    with get_connection(db_path) as conn:
        sync_inbound_task_to_ledger(
            conn,
            list_item,
            task_payload,
            metadata=metadata,
            event_type=f"inbound_{action}",
            summary=f"{action}: {normalize_title(title)}",
        )
        conn.commit()

    return {
        "action": action,
        "list_id": list_item["id"],
        "list_title": list_item.get("title", list_title),
        "task": task_payload,
        "metadata": metadata,
    }


def task_snapshot_hash(task: dict[str, Any]) -> str:
    canonical = {
        "id": task.get("id"),
        "title": task.get("title"),
        "notes": task.get("notes"),
        "status": task.get("status"),
        "due": task.get("due"),
        "completed": task.get("completed"),
        "updated": task.get("updated"),
        "deleted": task.get("deleted"),
        "hidden": task.get("hidden"),
        "parent": task.get("parent"),
        "position": task.get("position"),
    }
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def upsert_list(conn: sqlite3.Connection, item: dict[str, Any], observed_at: str) -> None:
    conn.execute(
        """
        INSERT INTO google_task_lists (list_id, title, etag, updated_at, self_link, first_seen_at, last_seen_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(list_id) DO UPDATE SET
            title = excluded.title,
            etag = excluded.etag,
            updated_at = excluded.updated_at,
            self_link = excluded.self_link,
            last_seen_at = excluded.last_seen_at,
            raw_json = excluded.raw_json
        """,
        (
            item.get("id"),
            item.get("title") or "Untitled",
            item.get("etag"),
            item.get("updated"),
            item.get("selfLink"),
            observed_at,
            observed_at,
            json.dumps(item, sort_keys=True),
        ),
    )


def upsert_task(conn: sqlite3.Connection, task: dict[str, Any], list_id: str, observed_at: str, run_id: int) -> bool:
    task_id = task.get("id")
    title = task.get("title") or ""
    notes = task.get("notes")
    status = task.get("status") or "needsAction"
    due_date = task.get("due")
    completed_at = task.get("completed")
    deleted = 1 if task.get("deleted") else 0
    hidden = 1 if task.get("hidden") else 0
    parent_id = task.get("parent")
    position = task.get("position")
    updated_at = task.get("updated")
    etag = task.get("etag")
    web_view_link = task.get("webViewLink")
    normalized_title = normalize_title(title)
    execution_requested = 1 if ("@run" in title or "@N5" in title) else 0
    execution_suffix = "@run" if "@run" in title else ("@N5" if "@N5" in title else None)
    snapshot_hash = task_snapshot_hash(task)
    raw_json = json.dumps(task, sort_keys=True)

    previous = conn.execute(
        "SELECT snapshot_hash, title, notes, status, due_date, completed_at, deleted, hidden FROM google_tasks_current WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    changed = previous is None or previous["snapshot_hash"] != snapshot_hash

    conn.execute(
        """
        INSERT INTO google_tasks_current (
            task_id, list_id, title, normalized_title, notes, status, due_date, completed_at,
            deleted, hidden, parent_id, position, updated_at, etag, web_view_link,
            execution_requested, execution_suffix, snapshot_hash, raw_json,
            first_seen_at, last_seen_at, last_run_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
            list_id = excluded.list_id,
            title = excluded.title,
            normalized_title = excluded.normalized_title,
            notes = excluded.notes,
            status = excluded.status,
            due_date = excluded.due_date,
            completed_at = excluded.completed_at,
            deleted = excluded.deleted,
            hidden = excluded.hidden,
            parent_id = excluded.parent_id,
            position = excluded.position,
            updated_at = excluded.updated_at,
            etag = excluded.etag,
            web_view_link = excluded.web_view_link,
            execution_requested = excluded.execution_requested,
            execution_suffix = excluded.execution_suffix,
            snapshot_hash = excluded.snapshot_hash,
            raw_json = excluded.raw_json,
            last_seen_at = excluded.last_seen_at,
            last_run_id = excluded.last_run_id
        """,
        (
            task_id,
            list_id,
            title,
            normalized_title,
            notes,
            status,
            due_date,
            completed_at,
            deleted,
            hidden,
            parent_id,
            position,
            updated_at,
            etag,
            web_view_link,
            execution_requested,
            execution_suffix,
            snapshot_hash,
            raw_json,
            observed_at,
            observed_at,
            run_id,
        ),
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO google_task_versions (
            task_id, list_id, observed_at, source_updated_at, snapshot_hash, state_status, raw_json, run_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (task_id, list_id, observed_at, updated_at, snapshot_hash, status, raw_json, run_id),
    )

    if changed:
        event_type = "created" if previous is None else "updated"
        summary = f"{event_type}: {title}".strip()
        dedupe_key = f"{task_id}:{snapshot_hash}:{event_type}"
        conn.execute(
            """
            INSERT OR IGNORE INTO google_task_events (
                task_id, list_id, event_type, event_at, run_id, summary, payload_json, dedupe_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (task_id, list_id, event_type, observed_at, run_id, summary, raw_json, dedupe_key),
        )

    conn.execute(
        """
        INSERT INTO intake_candidates (
            task_id, list_id, canonical_title, execution_requested, candidate_status, execution_target,
            last_routed_at, notes, classification_json
        ) VALUES (?, ?, ?, ?, 'observed', ?, ?, ?, '{}')
        ON CONFLICT(task_id) DO UPDATE SET
            list_id = excluded.list_id,
            canonical_title = excluded.canonical_title,
            execution_requested = excluded.execution_requested,
            last_routed_at = excluded.last_routed_at,
            notes = excluded.notes
        """,
        (task_id, list_id, normalized_title or title, execution_requested, "zo_worker" if execution_requested else None, observed_at, notes),
    )

    return changed


def row_value(row: sqlite3.Row | dict[str, Any], key: str, default: Any = None) -> Any:
    try:
        if hasattr(row, 'keys') and key in row.keys():
            return row[key]
    except Exception:
        pass
    getter = getattr(row, 'get', None)
    if callable(getter):
        return getter(key, default)
    return default


def db_path_for_connection(conn: sqlite3.Connection) -> str:
    row = conn.execute("PRAGMA database_list").fetchone()
    return str(row[2]) if row and len(row) > 2 else str(DB_PATH)


def slugify(value: str, max_words: int = 8, max_len: int = 72) -> str:
    text = (value or "").lower()
    out = []
    prev_dash = False
    for ch in text:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                out.append('-')
                prev_dash = True
    slug = ''.join(out).strip('-')
    words = [w for w in slug.split('-') if w]
    slug = '-'.join(words[:max_words])
    return (slug[:max_len].rstrip('-') or 'task')


def normalize_job_timestamp(value: str | None) -> str:
    text = str(value or utc_now_iso())
    try:
        dt = datetime.fromisoformat(text.replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z').replace(':', '-')
    except ValueError:
        normalized = text.replace(':', '-')
        return normalized.replace('+00-00', 'Z').replace('+00:00', 'Z')


def infer_action_type(title: str, notes: str | None = None) -> str:
    text = f"{title} {notes or ''}".lower()
    if 'email' in text or 'mail ' in text or 'send ' in text:
        return 'send-email'
    if 'report' in text or 'summar' in text or 'research' in text:
        return 'research'
    if 'draft' in text or 'write' in text:
        return 'draft'
    if 'review' in text:
        return 'review'
    return 'task'


def primary_action_type(job: sqlite3.Row | dict[str, Any]) -> str:
    inferred = infer_action_type(
        str(row_value(job, 'normalized_title') or row_value(job, 'canonical_title') or row_value(job, 'title') or ''),
        row_value(job, 'notes'),
    )
    explicit = str(row_value(job, 'action_type') or '').strip().lower()
    return inferred if inferred != 'task' else (explicit or 'task')


def build_job_detail_slug(job: sqlite3.Row | dict[str, Any], primary_action: str) -> str:
    normalized_title = str(row_value(job, 'normalized_title') or row_value(job, 'canonical_title') or row_value(job, 'title') or '')
    notes = str(row_value(job, 'notes') or '')
    detail_slug = ""
    lowered_title = normalized_title.lower()
    if "send an email " in lowered_title:
        tail = normalized_title[lowered_title.index("send an email ") + len("send an email "):]
        detail_slug = slugify(f"email {tail}", max_words=10, max_len=96)
    elif "send email " in lowered_title:
        tail = normalized_title[lowered_title.index("send email ") + len("send email "):]
        detail_slug = slugify(f"email {tail}", max_words=10, max_len=96)
    elif lowered_title.startswith("email "):
        detail_slug = slugify(normalized_title, max_words=10, max_len=96)
    if not detail_slug:
        detail_slug = slugify(normalized_title, max_words=10, max_len=96)
    if detail_slug == primary_action or not detail_slug:
        detail_slug = slugify(notes or normalized_title, max_words=10, max_len=96)
    return detail_slug or 'task'


def build_job_run_slug(job: sqlite3.Row | dict[str, Any]) -> str:
    job_id = int(job['job_id'])
    queued_at = normalize_job_timestamp(row_value(job, 'queued_at'))
    action_type = primary_action_type(job)
    title_slug = build_job_detail_slug(job, action_type)
    execution_target = slugify(str(row_value(job, 'execution_target') or 'zo_worker'), max_words=3, max_len=24)
    return f"{job_id:03d}__{action_type}__{title_slug}__{execution_target}__{queued_at}"


def get_job_output_dir(job: sqlite3.Row | dict[str, Any]) -> Path:
    return TASK_OUTPUTS_ROOT / build_job_run_slug(job)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent_dir(path)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')


def write_text(path: Path, text: str) -> None:
    ensure_parent_dir(path)
    path.write_text(text, encoding='utf-8')


def normalize_worker_output(raw_output: Any) -> dict[str, Any]:
    if isinstance(raw_output, dict):
        actions = raw_output.get('actions_taken')
        remaining = raw_output.get('remaining')
        return {
            'executed': bool(raw_output.get('executed', True)),
            'summary': str(raw_output.get('summary') or ''),
            'actions_taken': [str(item) for item in actions] if isinstance(actions, list) else [],
            'remaining': [str(item) for item in remaining] if isinstance(remaining, list) else [],
        }
    summary = str(raw_output or '')
    return {
        'executed': True,
        'summary': summary,
        'actions_taken': ['Worker returned non-JSON text output; normalized by bridge.'],
        'remaining': [],
    }


def append_receipt_annotation(existing_notes: str, annotation: str) -> str:
    base = (existing_notes or '').strip()
    if annotation in base:
        return base
    return f"{base}\n\n{annotation}".strip()


def build_receipt_annotation(job: sqlite3.Row | dict[str, Any], output: dict[str, Any], completed_at: str | None = None) -> str:
    lines = ['[Zo receipt]', f"job_id: {job['job_id']}"]
    if completed_at:
        lines.append(f"completed_at: {completed_at}")
    if output.get('summary'):
        lines.append(f"summary: {output['summary']}")
    return '\n'.join(lines)


def ensure_task_list(client: GoogleTasksClient, list_title: str) -> tuple[dict[str, Any], bool]:
    for item in client.list_tasklists():
        if (item.get('title') or '').strip().lower() == list_title.strip().lower():
            return item, False
    return client.create_tasklist(list_title), True


def find_task_by_note_substring(client: GoogleTasksClient, list_id: str, needle: str) -> dict[str, Any] | None:
    try:
        items = client.list_tasks(list_id, max_results=100, show_completed=True, show_hidden=True)
    except TypeError:
        items = client.list_tasks(list_id, max_results=100)
    for item in items:
        if needle in (item.get('notes') or ''):
            return item
    return None


def update_task_on_google(client: GoogleTasksClient, list_id: str, task_id: str, *, title: str, notes: str = '', completed: bool = False, due: str | None = None) -> dict[str, Any]:
    if hasattr(client, 'update_task'):
        return client.update_task(list_id, task_id, title=title, notes=notes, completed=completed, due=due)
    body: dict[str, Any] = {'title': title, 'notes': notes, 'status': 'completed' if completed else 'needsAction'}
    if due:
        body['due'] = normalize_google_due_timestamp(due)
    return client._request('PATCH', f'/lists/{list_id}/tasks/{task_id}', json_body=body)


def parse_b05_action_items(b05_content: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    checkbox_pattern = re.compile(r'^\s*-\s*\[[ xX]\]\s*\*\*([^*]+)\*\*\s*:\s*(.+)$')

    in_table = False
    headers: list[str] = []

    def is_formatting_row(cells: list[str]) -> bool:
        if not cells:
            return True
        for cell in cells:
            stripped = cell.strip()
            if stripped and not re.match(r'^[:\-]+$', stripped):
                return False
        return True

    for raw_line in b05_content.splitlines():
        line = raw_line.strip()
        if not line:
            in_table = False
            headers = []
            continue

        match = checkbox_pattern.match(line)
        if match:
            items.append(
                {
                    "title": match.group(2).strip(),
                    "assignee": match.group(1).strip(),
                    "raw_text": line,
                }
            )
            continue

        if "|" not in line or not line.startswith("|") or not line.endswith("|"):
            continue

        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if is_formatting_row(cells):
            in_table = True
            continue
        if not in_table and not headers and len(cells) > 1:
            headers = [cell.lower() for cell in cells]
            in_table = True
            continue
        if not in_table or not headers or len(cells) < len(headers):
            continue

        row = dict(zip(headers, cells[:len(headers)]))
        owner = ""
        for key in ("owner", "assignee", "who", "person"):
            if row.get(key):
                owner = str(row[key]).strip()
                break
        task = ""
        for key in ("task", "description", "action", "what"):
            if row.get(key):
                task = str(row[key]).strip()
                break
        if not task:
            continue
        items.append({"title": task, "assignee": owner, "raw_text": line})

    return items


def classify_b05_ownership(assignee: str | None) -> tuple[bool, float, str | None]:
    normalized = re.sub(r"\s+", " ", str(assignee or "").strip().lower())
    if not normalized:
        return True, 0.6, "No explicit assignee in B05 item."
    if normalized in {"v", "<your_name>", "<your_github>", "va", "me", "myself", "you"}:
        return True, 0.95, None
    if normalized in {"all", "everyone", "team", "group", "unassigned", "tbd", "unknown"}:
        return True, 0.6, f"Assignee '{assignee}' is shared or ambiguous."
    if normalized in {"system", "zo", "assistant"}:
        return False, 0.1, f"Assignee '{assignee}' appears system-owned, not V-owned."
    return False, 0.1, f"Assignee '{assignee}' appears to be someone else."


def sync_meeting_b05_to_inbound(
    meeting_path: Path,
    *,
    list_title: str = DEFAULT_INBOUND_LIST_TITLE,
    client: GoogleTasksClient | None = None,
    db_path: Path = DB_PATH,
) -> dict[str, Any]:
    manifest_path = meeting_path / "manifest.json"
    b05_path = meeting_path / "B05_ACTION_ITEMS.md"
    if not manifest_path.exists() or not b05_path.exists():
        return {"meeting_path": str(meeting_path), "synced": 0, "skipped": 0, "details": []}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    meeting_id = str(manifest.get("meeting_id") or meeting_path.name)
    content = b05_path.read_text(encoding="utf-8")
    items = parse_b05_action_items(content)
    if not items:
        return {"meeting_path": str(meeting_path), "synced": 0, "skipped": 0, "details": []}

    task_client = client or GoogleTasksClient()
    synced = 0
    skipped = 0
    details: list[dict[str, Any]] = []

    for index, item in enumerate(items, start=1):
        should_capture, confidence, reason = classify_b05_ownership(item.get("assignee"))
        if not should_capture:
            skipped += 1
            details.append(
                {
                    "title": item.get("title"),
                    "status": "skipped",
                    "reason": reason,
                    "assignee": item.get("assignee"),
                }
            )
            continue
        event_key = hashlib.sha256(
            f"{meeting_id}:{index}:{item.get('raw_text') or item.get('title')}".encode("utf-8")
        ).hexdigest()[:16]
        result = upsert_inbound_task(
            task_client,
            title=str(item.get("title") or "").strip(),
            notes=f"Meeting: {meeting_id}\nAssignee: {item.get('assignee') or 'unspecified'}\n{item.get('raw_text') or ''}".strip(),
            confidence=confidence,
            source_type="meeting",
            source_id=meeting_id,
            source_event_key=f"meeting:{meeting_id}:{event_key}",
            list_title=list_title,
            low_confidence_reason=reason,
            db_path=db_path,
        )
        synced += 1
        details.append(
            {
                "title": item.get("title"),
                "status": result["action"],
                "assignee": item.get("assignee"),
                "confidence": confidence,
            }
        )

    return {
        "meeting_path": str(meeting_path),
        "meeting_id": meeting_id,
        "source_block": "B05_ACTION_ITEMS.md",
        "synced": synced,
        "skipped": skipped,
        "details": details,
    }


def sync_meeting_s02_to_inbound(
    meeting_path: Path,
    *,
    list_title: str = DEFAULT_INBOUND_LIST_TITLE,
    client: GoogleTasksClient | None = None,
    db_path: Path = DB_PATH,
) -> dict[str, Any]:
    manifest_path = meeting_path / "manifest.json"
    s02_path = meeting_path / "S02_ACTIONS.md"
    if not manifest_path.exists() or not s02_path.exists():
        return {
            "meeting_path": str(meeting_path),
            "source_block": "S02_ACTIONS.md",
            "source_exists": False,
            "synced": 0,
            "skipped": 0,
            "details": [],
        }

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    meeting_id = str(manifest.get("meeting_id") or meeting_path.name)
    meeting_date = str((manifest.get("meeting") or {}).get("date") or manifest.get("date") or "").strip() or None
    items = parse_s02_v_owned_items(s02_path.read_text(encoding="utf-8"), meeting_date=meeting_date)
    if not items:
        return {
            "meeting_path": str(meeting_path),
            "meeting_id": meeting_id,
            "source_block": "S02_ACTIONS.md",
            "source_exists": True,
            "synced": 0,
            "skipped": 0,
            "details": [],
        }

    task_client = client or GoogleTasksClient()
    synced = 0
    skipped = 0
    details: list[dict[str, Any]] = []

    for index, item in enumerate(items, start=1):
        if item.get("status") != "ready":
            skipped += 1
            details.append(
                {
                    "title": item.get("title") or "",
                    "status": "skipped",
                    "reason": item.get("reason") or "Unusable S02 item.",
                }
            )
            continue
        event_key = hashlib.sha256(
            f"{meeting_id}:S02:{index}:{item.get('raw_text') or item.get('title')}".encode("utf-8")
        ).hexdigest()[:16]
        result = upsert_inbound_task(
            task_client,
            title=str(item.get("title") or "").strip(),
            notes=str(item.get("notes") or "").strip(),
            due=item.get("due"),
            confidence=float(item.get("confidence") or 0.92),
            source_type="meeting",
            source_id=meeting_id,
            source_event_key=f"meeting:{meeting_id}:S02:{event_key}",
            list_title=list_title,
            low_confidence_reason=item.get("low_confidence_reason"),
            db_path=db_path,
        )
        synced += 1
        details.append(
            {
                "title": item.get("title"),
                "status": result["action"],
                "confidence": item.get("confidence"),
                "due": item.get("due"),
                "source_block": "S02_ACTIONS.md",
            }
        )

    return {
        "meeting_path": str(meeting_path),
        "meeting_id": meeting_id,
        "source_block": "S02_ACTIONS.md",
        "source_exists": True,
        "synced": synced,
        "skipped": skipped,
        "details": details,
    }


def sync_meeting_to_inbound(
    meeting_path: Path,
    *,
    list_title: str = DEFAULT_INBOUND_LIST_TITLE,
    client: GoogleTasksClient | None = None,
    db_path: Path = DB_PATH,
) -> dict[str, Any]:
    s02_result = sync_meeting_s02_to_inbound(
        meeting_path,
        list_title=list_title,
        client=client,
        db_path=db_path,
    )
    if s02_result.get("source_exists"):
        return s02_result
    return sync_meeting_b05_to_inbound(
        meeting_path,
        list_title=list_title,
        client=client,
        db_path=db_path,
    )


def mark_google_task_processed(client: GoogleTasksClient, job: sqlite3.Row | dict[str, Any], output: dict[str, Any], completed_at: str | None = None) -> dict[str, Any]:
    annotation = build_receipt_annotation(job, output, completed_at=completed_at)
    updated_notes = append_receipt_annotation(str(row_value(job, 'notes') or ''), annotation)
    original_task = update_task_on_google(
        client,
        str(job['list_id']),
        str(job['task_id']),
        title=str(row_value(job, 'title') or row_value(job, 'normalized_title') or 'Task'),
        notes=updated_notes,
        completed=True,
        due=row_value(job, 'due_date'),
    )
    receipts_list, _ = ensure_task_list(client, DEFAULT_RECEIPTS_LIST_TITLE)
    receipt_marker = f"job_id: {job['job_id']}"
    receipt_task = find_task_by_note_substring(client, receipts_list['id'], receipt_marker)
    if receipt_task is None:
        receipt_task = client.create_task(
            receipts_list['id'],
            f"Processed: {str(row_value(job, 'normalized_title') or row_value(job, 'title') or 'Task')[:120]}",
            notes=annotation,
        )
    return {
        'original_task': {
            'task_id': original_task.get('id', job['task_id']),
            'status': original_task.get('status', 'completed'),
            'completed': original_task.get('completed'),
        },
        'receipt_task': {
            'list_id': receipts_list['id'],
            'list_title': receipts_list.get('title', DEFAULT_RECEIPTS_LIST_TITLE),
            'task_id': receipt_task.get('id'),
            'title': receipt_task.get('title'),
            'status': receipt_task.get('status'),
        },
        'annotation': annotation,
    }


def write_job_output_files(job: sqlite3.Row | dict[str, Any], status: str, payload: dict[str, Any]) -> Path:
    outdir = get_job_output_dir(job)
    outdir.mkdir(parents=True, exist_ok=True)
    input_payload = {
        'job_id': job['job_id'],
        'task_id': job['task_id'],
        'list_id': job['list_id'],
        'execution_target': row_value(job, 'execution_target'),
        'model_name': row_value(job, 'model_name'),
        'queued_at': row_value(job, 'queued_at'),
        'task_title': row_value(job, 'title'),
        'normalized_title': row_value(job, 'normalized_title'),
        'notes': row_value(job, 'notes'),
        'action_type': row_value(job, 'action_type'),
    }
    write_json(outdir / 'TASK_INPUT.json', input_payload)
    write_json(outdir / 'TASK_OUTPUT.json', payload)
    write_json(outdir / 'TASK_STATUS.json', {'status': status})
    lines = [f"# Task Run {job['job_id']}", '', f"Status: {status}", '']
    if payload.get('summary'):
        lines.extend(['## Summary', '', payload['summary'], ''])
    if payload.get('actions_taken'):
        lines.extend(['## Actions Taken', ''] + [f"- {item}" for item in payload['actions_taken']] + [''])
    if payload.get('remaining'):
        lines.extend(['## Remaining', ''] + [f"- {item}" for item in payload['remaining']] + [''])
    write_text(outdir / 'TASK_OUTPUT.md', '\n'.join(lines))
    write_json(TASK_OUTPUTS_ROOT / 'LATEST.json', {'job_id': job['job_id'], 'status': status, 'path': str(outdir), 'summary': payload.get('summary', '')})
    write_text(TASK_OUTPUTS_ROOT / 'LATEST.md', '\n'.join(lines + [f"Path: {outdir}"]))
    return outdir


def build_dispatch_prompt(task_row: sqlite3.Row | dict[str, Any], candidate: sqlite3.Row | dict[str, Any], model_name: str) -> str:
    return (
        "Execute the following task from Google Tasks. Use the workspace, perform the work if feasible, and respond with JSON "
        "or plain text summarizing what you did. Respect explicit user permissions inside the task text.\n\n"
        f"Model: {model_name}\n"
        f"Action type: {row_value(candidate, 'action_type') or primary_action_type(task_row)}\n"
        f"Title: {row_value(task_row, 'normalized_title') or row_value(task_row, 'title')}\n"
        f"Original title: {row_value(task_row, 'title')}\n"
        f"Notes: {row_value(task_row, 'notes') or row_value(candidate, 'candidate_notes') or ''}\n"
    )


def find_completed_equivalent_job(conn: sqlite3.Connection, task_row: sqlite3.Row | dict[str, Any]) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT j.job_id, j.completed_at
        FROM execution_jobs j
        JOIN google_tasks_current g ON g.task_id = j.task_id
        WHERE j.status = 'completed'
          AND g.task_id != ?
          AND g.normalized_title = ?
          AND COALESCE(g.notes, '') = COALESCE(?, '')
        ORDER BY j.job_id DESC
        LIMIT 1
        """,
        (
            task_row['task_id'],
            str(row_value(task_row, 'normalized_title') or row_value(task_row, 'title') or ''),
            str(row_value(task_row, 'notes') or ''),
        ),
    ).fetchone()


def create_execution_job(conn: sqlite3.Connection, task_row: sqlite3.Row, candidate: sqlite3.Row, model_name: str) -> bool:
    completed_existing = conn.execute(
        "SELECT job_id FROM execution_jobs WHERE task_id = ? AND status = 'completed' ORDER BY job_id DESC LIMIT 1",
        (task_row['task_id'],),
    ).fetchone()
    if completed_existing:
        return False
    existing = conn.execute(
        "SELECT job_id FROM execution_jobs WHERE task_id = ? AND status IN ('queued','launching','running') LIMIT 1",
        (task_row['task_id'],),
    ).fetchone()
    if existing:
        return False
    duplicate_of = find_completed_equivalent_job(conn, task_row)
    if duplicate_of:
        conn.execute(
            """
            INSERT INTO execution_jobs (
                task_id, list_id, execution_target, model_name, prompt_text, status, queued_at, completed_at, error_text
            ) VALUES (?, ?, ?, ?, ?, 'canceled', ?, ?, ?)
            """,
            (
                task_row['task_id'],
                task_row['list_id'],
                row_value(candidate, 'execution_target') or 'zo_worker',
                model_name,
                build_dispatch_prompt(task_row, candidate, model_name),
                utc_now_iso(),
                utc_now_iso(),
                f"Canceled as duplicate of completed equivalent job {duplicate_of['job_id']}",
            ),
        )
        return False
    prompt_text = build_dispatch_prompt(task_row, candidate, model_name)
    conn.execute(
        """
        INSERT INTO execution_jobs (task_id, list_id, execution_target, model_name, prompt_text, status, queued_at, retry_count, max_retries, writeback_done)
        VALUES (?, ?, ?, ?, ?, 'queued', ?, 0, 1, 0)
        """,
        (
            task_row['task_id'],
            task_row['list_id'],
            row_value(candidate, 'execution_target') or 'zo_worker',
            model_name,
            prompt_text,
            utc_now_iso(),
        ),
    )
    return True


def should_skip_writeback(job: sqlite3.Row | dict[str, Any]) -> bool:
    return bool(row_value(job, 'writeback_done')) or str(row_value(job, 'status') or '') == 'completed'


def recover_stale_jobs(conn: sqlite3.Connection, stale_after_minutes: int = STALE_JOB_AFTER_MINUTES) -> dict[str, int]:
    stale_before = (datetime.now(timezone.utc) - timedelta(minutes=stale_after_minutes)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows = conn.execute(
        """
        SELECT job_id, status, retry_count, max_retries, started_at, lease_expires_at, last_heartbeat_at
        FROM execution_jobs
        WHERE status = 'running'
        """
    ).fetchall()
    requeued = 0
    failed = 0
    for row in rows:
        lease_expires_at = row_value(row, 'lease_expires_at')
        started_at = row_value(row, 'started_at')
        last_heartbeat_at = row_value(row, 'last_heartbeat_at')
        is_stale = False
        if lease_expires_at and str(lease_expires_at) < utc_now_iso():
            is_stale = True
        elif last_heartbeat_at and str(last_heartbeat_at) < stale_before:
            is_stale = True
        elif started_at and str(started_at) < stale_before:
            is_stale = True
        if not is_stale:
            continue
        if int(row['retry_count']) < int(row['max_retries']):
            conn.execute(
                """
                UPDATE execution_jobs
                SET status = 'queued',
                    retry_count = retry_count + 1,
                    started_at = NULL,
                    attempt_token = NULL,
                    lease_expires_at = NULL,
                    last_heartbeat_at = NULL,
                    worker_pid = NULL,
                    error_text = 'Recovered stale running job for retry'
                WHERE job_id = ?
                """,
                (row['job_id'],),
            )
            requeued += 1
        else:
            conn.execute(
                """
                UPDATE execution_jobs
                SET status = 'failed',
                    completed_at = ?,
                    error_text = 'Job exceeded retry budget after stale recovery'
                WHERE job_id = ?
                """,
                (utc_now_iso(), row['job_id']),
            )
            failed += 1
    return {'requeued': requeued, 'failed': failed}


def route_command(args: argparse.Namespace) -> None:
    with get_connection(Path(args.db)) as conn:
        rows = conn.execute(
            """
            SELECT g.task_id, g.list_id, g.title, g.normalized_title, g.notes, g.status, g.due_date,
                   c.execution_requested, c.execution_target, c.canonical_title, c.action_type
            FROM google_tasks_current g
            JOIN intake_candidates c ON c.task_id = g.task_id
            WHERE g.deleted = 0 AND g.hidden = 0 AND g.status != 'completed'
            ORDER BY g.last_seen_at DESC
            """
        ).fetchall()
        routed = 0
        for row in rows:
            if row['execution_requested']:
                action_type = row['action_type'] or infer_action_type(str(row['normalized_title'] or row['title']), row['notes'])
                conn.execute(
                    "UPDATE intake_candidates SET candidate_status = 'staged', execution_target = ?, action_type = ?, last_routed_at = ? WHERE task_id = ?",
                    ('zo_worker', action_type, utc_now_iso(), row['task_id']),
                )
                routed += 1
            else:
                conn.execute(
                    "UPDATE intake_candidates SET candidate_status = 'observed', action_type = ?, last_routed_at = ? WHERE task_id = ?",
                    (infer_action_type(str(row['normalized_title'] or row['title']), row['notes']), utc_now_iso(), row['task_id']),
                )
        conn.commit()
    print(json.dumps({'routed': routed}, indent=2) if args.json else f"Routed {routed} execution-requested tasks")


def dispatch_command(args: argparse.Namespace) -> None:
    with get_connection(Path(args.db)) as conn:
        recovery = recover_stale_jobs(conn)
        rows = conn.execute(
            """
            SELECT g.*, c.canonical_title, c.execution_requested, c.execution_target, c.action_type, c.notes as candidate_notes
            FROM google_tasks_current g
            JOIN intake_candidates c ON c.task_id = g.task_id
            WHERE g.deleted = 0 AND g.hidden = 0 AND g.status != 'completed' AND c.execution_requested = 1
            ORDER BY g.last_seen_at ASC
            LIMIT ?
            """,
            (args.limit,),
        ).fetchall()
        queued = 0
        for row in rows:
            if create_execution_job(conn, row, row, args.model):
                queued += 1
        conn.commit()
    with get_connection(Path(args.db)) as conn:
        jobs = conn.execute(
            """
            SELECT job_id
            FROM execution_jobs
            WHERE status = 'queued'
            ORDER BY queued_at ASC, job_id ASC
            LIMIT ?
            """,
            (args.limit,),
        ).fetchall()
    executed = 0
    failed = 0
    for job in jobs:
        result = run_job(job['job_id'], Path(args.db), args.model)
        if result['status'] == 'completed':
            executed += 1
        elif result['status'] == 'failed':
            failed += 1
    payload = {'queued': queued, 'executed': executed, 'failed': failed, **recovery}
    print(json.dumps(payload, indent=2) if args.json else f"Queued {queued} execution jobs; executed {executed}; failed {failed}; recovered {recovery['requeued']} stale jobs")


def run_job(job_id: int, db_path: Path, model_name: str) -> dict[str, Any]:
    with get_connection(db_path) as conn:
        job = conn.execute(
            """
            SELECT j.*, g.title, g.normalized_title, g.notes, g.due_date, c.action_type, c.canonical_title
            FROM execution_jobs j
            JOIN google_tasks_current g ON g.task_id = j.task_id
            LEFT JOIN intake_candidates c ON c.task_id = j.task_id
            WHERE j.job_id = ?
            """,
            (job_id,),
        ).fetchone()
        if not job:
            return {'status': 'missing', 'job_id': job_id}
        if should_skip_writeback(job):
            return {'status': str(row_value(job, 'status') or 'completed'), 'job_id': job_id}
        conn.execute("UPDATE execution_jobs SET status = 'running', started_at = ?, completed_at = NULL WHERE job_id = ?", (utc_now_iso(), job_id))
        conn.commit()
    token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
    if not token:
        with get_connection(db_path) as conn:
            conn.execute("UPDATE execution_jobs SET status = 'failed', completed_at = ?, error_text = ? WHERE job_id = ?", (utc_now_iso(), 'Missing ZO_CLIENT_IDENTITY_TOKEN for worker dispatch', job_id))
            conn.commit()
        return {'status': 'failed', 'job_id': job_id, 'error': 'Missing ZO_CLIENT_IDENTITY_TOKEN for worker dispatch'}
    try:
        resp = requests.post(
            ZO_ASK_URL,
            headers={'authorization': token, 'content-type': 'application/json'},
            json={'input': job['prompt_text'], 'model_name': model_name or DEFAULT_MODEL},
            timeout=180,
        )
        resp.raise_for_status()
        raw_output = resp.json().get('output')
        payload = normalize_worker_output(raw_output)
        completed_at = utc_now_iso()
        outdir = write_job_output_files(job, 'completed', payload)
        client = GoogleTasksClient()
        receipt = mark_google_task_processed(client, job, payload, completed_at=completed_at)
        with get_connection(db_path) as conn:
            conn.execute(
                "UPDATE execution_jobs SET status = 'completed', completed_at = ?, response_json = ?, writeback_done = 1, error_text = NULL WHERE job_id = ?",
                (completed_at, json.dumps({'payload': payload, 'receipt': receipt, 'output_dir': str(outdir)}), job_id),
            )
            conn.execute(
                """
                UPDATE google_tasks_current
                SET status = 'completed',
                    completed_at = ?,
                    last_seen_at = ?,
                    notes = ?
                WHERE task_id = ?
                """,
                (completed_at, completed_at, receipt['annotation'], job['task_id']),
            )
            conn.execute(
                "UPDATE intake_candidates SET candidate_status = 'completed', last_routed_at = ? WHERE task_id = ?",
                (completed_at, job['task_id']),
            )
            conn.commit()
        return {'status': 'completed', 'job_id': job_id, 'output_dir': str(outdir)}
    except requests.Timeout:
        with get_connection(db_path) as conn:
            conn.execute("UPDATE execution_jobs SET status = 'failed', completed_at = ?, error_text = ? WHERE job_id = ?", (utc_now_iso(), f'Timed out after 180 seconds', job_id))
            conn.commit()
        return {'status': 'failed', 'job_id': job_id, 'error': 'Timed out after 180 seconds'}
    except Exception as e:
        with get_connection(db_path) as conn:
            conn.execute("UPDATE execution_jobs SET status = 'failed', completed_at = ?, error_text = ? WHERE job_id = ?", (utc_now_iso(), str(e), job_id))
            conn.commit()
        return {'status': 'failed', 'job_id': job_id, 'error': str(e)}


def run_job_command(args: argparse.Namespace) -> None:
    result = run_job(args.job_id, Path(args.db), args.model)
    if getattr(args, 'json', False):
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Job {result['job_id']}: {result['status']}")


def backfill_outputs_command(args: argparse.Namespace) -> None:
    TASK_OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
    with get_connection(Path(args.db)) as conn:
        jobs = conn.execute(
            """
            SELECT j.*, g.title, g.normalized_title, g.notes, c.action_type, c.canonical_title
            FROM execution_jobs j
            JOIN google_tasks_current g ON g.task_id = j.task_id
            LEFT JOIN intake_candidates c ON c.task_id = j.task_id
            WHERE j.status = 'completed'
            ORDER BY j.job_id ASC
            """
        ).fetchall()
        renamed = 0
        for job in jobs:
            legacy = TASK_OUTPUTS_ROOT / f"job-{job['job_id']}-{str(job['queued_at']).replace(':','-').replace('+00:00','+00-00')}"
            target = get_job_output_dir(job)
            if legacy.exists() and not target.exists():
                legacy.rename(target)
                renamed += 1
    print(json.dumps({'renamed': renamed}, indent=2) if getattr(args, 'json', False) else f"Renamed {renamed} legacy output directories")


def collect_status_payload(conn: sqlite3.Connection) -> dict[str, Any]:
    list_count = conn.execute("SELECT COUNT(*) FROM google_task_lists").fetchone()[0]
    active_count = conn.execute("SELECT COUNT(*) FROM google_tasks_current WHERE deleted = 0 AND hidden = 0").fetchone()[0]
    execution_requested = conn.execute("SELECT COUNT(*) FROM google_tasks_current WHERE deleted = 0 AND hidden = 0 AND execution_requested = 1").fetchone()[0]
    completed_jobs = conn.execute("SELECT COUNT(*) FROM execution_jobs WHERE status = 'completed'").fetchone()[0]
    queued_jobs = conn.execute("SELECT COUNT(*) FROM execution_jobs WHERE status IN ('queued', 'launching', 'running')").fetchone()[0]
    last_poll = conn.execute(
        "SELECT id, source_system, list_id, list_title, started_at, completed_at, status, fetched_count, changed_count, error_text FROM poll_runs ORDER BY id DESC LIMIT 1"
    ).fetchone()
    last_job = conn.execute(
        """
        SELECT j.job_id, j.status, j.queued_at, j.started_at, j.completed_at, g.normalized_title
        FROM execution_jobs j
        LEFT JOIN google_tasks_current g ON g.task_id = j.task_id
        ORDER BY j.job_id DESC
        LIMIT 1
        """
    ).fetchone()
    return {
        "db_path": db_path_for_connection(conn),
        "list_count": list_count,
        "active_tasks": active_count,
        "execution_requested": execution_requested,
        "completed_jobs": completed_jobs,
        "queued_jobs": queued_jobs,
        "cursor_next": get_state(conn, "google_tasks.cursor_next"),
        "last_poll": dict(last_poll) if last_poll else None,
        "last_job": dict(last_job) if last_job else None,
    }


def render_human_report(payload: dict[str, Any]) -> str:
    lines = [
        "Google Tasks Bridge Report",
        "",
        f"DB: {payload['db_path']}",
        f"Lists tracked: {payload['list_count']}",
        f"Active tasks: {payload['active_tasks']}",
        f"Execution requested: {payload['execution_requested']}",
        f"Queued/running jobs: {payload['queued_jobs']}",
        f"Completed jobs: {payload['completed_jobs']}",
    ]
    if payload.get("cursor_next"):
        lines.append(f"Cursor: {payload['cursor_next']}")
    last_poll = payload.get("last_poll")
    if last_poll:
        lines.extend(
            [
                "",
                "Last poll",
                f"- status: {last_poll.get('status')}",
                f"- list: {last_poll.get('list_title') or last_poll.get('list_id')}",
                f"- fetched: {last_poll.get('fetched_count')}",
                f"- changed: {last_poll.get('changed_count')}",
                f"- started: {last_poll.get('started_at')}",
                f"- completed: {last_poll.get('completed_at')}",
            ]
        )
        if last_poll.get("error_text"):
            lines.append(f"- error: {last_poll['error_text']}")
    last_job = payload.get("last_job")
    if last_job:
        lines.extend(
            [
                "",
                "Last job",
                f"- id: {last_job.get('job_id')}",
                f"- status: {last_job.get('status')}",
                f"- task: {last_job.get('normalized_title')}",
                f"- queued: {last_job.get('queued_at')}",
                f"- completed: {last_job.get('completed_at')}",
            ]
        )
    return "\n".join(lines)


def report_command(args: argparse.Namespace) -> None:
    status_command(args)


def init_db_command(args: argparse.Namespace) -> None:
    initialize_db(Path(args.db))
    print(f"Initialized DB at {args.db}")


def status_command(args: argparse.Namespace) -> None:
    with get_connection(Path(args.db)) as conn:
        payload = collect_status_payload(conn)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_human_report(payload))


def lists_command(args: argparse.Namespace) -> None:
    client = GoogleTasksClient()
    items = client.list_tasklists()
    print(json.dumps(items, indent=2, sort_keys=True) if args.json else "\n".join(f"{item.get('id')}\t{item.get('title')}" for item in items))


def ensure_list_command(args: argparse.Namespace) -> None:
    client = GoogleTasksClient()
    item, created = ensure_task_list(client, args.list_title)
    payload = {"created": created, "list": item}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"{'Created' if created else 'Exists'}: {item.get('title')} ({item.get('id')})")


def create_task_command(args: argparse.Namespace) -> None:
    client = GoogleTasksClient()
    item, _ = ensure_task_list(client, args.list_title)
    task = client.create_task(item["id"], args.title, notes=args.notes or "", due=args.due)
    print(json.dumps(task, indent=2, sort_keys=True) if args.json else f"Created task: {task.get('title')} ({task.get('id')})")


def upsert_inbound_command(args: argparse.Namespace) -> None:
    client = GoogleTasksClient()
    payload = upsert_inbound_task(
        client,
        title=args.title,
        notes=args.notes or "",
        due=args.due,
        confidence=args.confidence,
        source_type=args.source_type,
        source_id=args.source_id,
        source_event_key=args.source_event_key,
        list_title=args.list_title,
        low_confidence_reason=args.low_confidence_reason,
        db_path=Path(args.db),
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        task = payload["task"]
        print(f"{payload['action']}: {task.get('title')} ({task.get('id')}) in {payload['list_title']}")


def sync_meeting_command(args: argparse.Namespace) -> None:
    client = GoogleTasksClient()
    payload = sync_meeting_to_inbound(
        Path(args.meeting_path),
        list_title=args.list_title,
        client=client,
        db_path=Path(args.db),
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"Meeting sync via {payload.get('source_block')}: "
            f"synced={payload.get('synced', 0)} skipped={payload.get('skipped', 0)}"
        )


def sync_command(args: argparse.Namespace) -> None:
    db_path = Path(args.db)
    initialize_db(db_path)
    client = GoogleTasksClient()
    with get_connection(db_path) as conn:
        observed_at = utc_now_iso()
        list_item, _ = ensure_task_list(client, args.list_title)
        upsert_list(conn, list_item, observed_at)
        cursor = get_state(conn, "google_tasks.cursor_next")
        conn.execute(
            "INSERT INTO poll_runs (source_system, list_id, list_title, started_at, status, cursor_used) VALUES (?, ?, ?, ?, 'running', ?)",
            ("google_tasks", list_item.get("id"), list_item.get("title"), observed_at, cursor),
        )
        run_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        try:
            tasks = client.list_tasks(list_item["id"], max_results=args.max_results, show_completed=args.show_completed, show_hidden=args.show_hidden)
            changed = 0
            latest_updated = cursor
            for task in tasks:
                if upsert_task(conn, task, list_item["id"], observed_at, run_id):
                    changed += 1
                updated = task.get("updated")
                if updated and (latest_updated is None or updated > latest_updated):
                    latest_updated = updated
            if latest_updated:
                set_state(conn, "google_tasks.cursor_next", latest_updated)
            conn.execute(
                "UPDATE poll_runs SET completed_at = ?, status = 'complete', fetched_count = ?, changed_count = ?, cursor_next = ? WHERE id = ?",
                (utc_now_iso(), len(tasks), changed, latest_updated, run_id),
            )
            conn.commit()
            payload = {
                "run_id": run_id,
                "list_id": list_item.get("id"),
                "list_title": list_item.get("title"),
                "fetched_count": len(tasks),
                "changed_count": changed,
                "cursor_next": latest_updated,
            }
            print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"Synced {len(tasks)} tasks from {list_item.get('title')} (changed: {changed})")
        except Exception as e:
            conn.execute(
                "UPDATE poll_runs SET completed_at = ?, status = 'failed', error_text = ? WHERE id = ?",
                (utc_now_iso(), str(e), run_id),
            )
            conn.commit()
            raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Google Tasks Bridge")
    parser.set_defaults(func=None)
    parser.add_argument("--db", default=str(DB_PATH), help="Path to the SQLite intake DB")
    subparsers = parser.add_subparsers(dest="command")

    init_db = subparsers.add_parser("init-db")
    init_db.set_defaults(func=init_db_command)

    status = subparsers.add_parser("status")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=status_command)

    lists = subparsers.add_parser("lists")
    lists.add_argument("--json", action="store_true")
    lists.set_defaults(func=lists_command)

    ensure_list = subparsers.add_parser("ensure-list")
    ensure_list.add_argument("--list-title", default=DEFAULT_LIST_TITLE)
    ensure_list.add_argument("--json", action="store_true")
    ensure_list.set_defaults(func=ensure_list_command)

    create_task = subparsers.add_parser("create-task")
    create_task.add_argument("--list-title", default=DEFAULT_LIST_TITLE)
    create_task.add_argument("--title", required=True)
    create_task.add_argument("--notes", default="")
    create_task.add_argument("--due", default=None)
    create_task.add_argument("--json", action="store_true")
    create_task.set_defaults(func=create_task_command)

    upsert_inbound = subparsers.add_parser("upsert-inbound")
    upsert_inbound.add_argument("--list-title", default=DEFAULT_INBOUND_LIST_TITLE)
    upsert_inbound.add_argument("--title", required=True)
    upsert_inbound.add_argument("--notes", default="")
    upsert_inbound.add_argument("--due", default=None)
    upsert_inbound.add_argument("--confidence", type=float, default=1.0)
    upsert_inbound.add_argument("--source-type", required=True)
    upsert_inbound.add_argument("--source-id", required=True)
    upsert_inbound.add_argument("--source-event-key", required=True)
    upsert_inbound.add_argument("--low-confidence-reason", default=None)
    upsert_inbound.add_argument("--json", action="store_true")
    upsert_inbound.set_defaults(func=upsert_inbound_command)

    sync_meeting = subparsers.add_parser("sync-meeting")
    sync_meeting.add_argument("--meeting-path", required=True)
    sync_meeting.add_argument("--list-title", default=DEFAULT_INBOUND_LIST_TITLE)
    sync_meeting.add_argument("--json", action="store_true")
    sync_meeting.set_defaults(func=sync_meeting_command)

    sync = subparsers.add_parser("sync")
    sync.add_argument("--list-title", default=DEFAULT_LIST_TITLE)
    sync.add_argument("--max-results", type=int, default=100)
    sync.add_argument("--show-completed", action="store_true")
    sync.add_argument("--show-hidden", action="store_true")
    sync.add_argument("--json", action="store_true")
    sync.set_defaults(func=sync_command)

    route = subparsers.add_parser("route")
    route.add_argument("--list-title", default=DEFAULT_LIST_TITLE)
    route.add_argument("--json", action="store_true")
    route.set_defaults(func=route_command)

    dispatch = subparsers.add_parser("dispatch")
    dispatch.add_argument("--list-title", default=DEFAULT_LIST_TITLE)
    dispatch.add_argument("--limit", type=int, default=5)
    dispatch.add_argument("--model", default=DEFAULT_MODEL)
    dispatch.add_argument("--json", action="store_true")
    dispatch.set_defaults(func=dispatch_command)

    run_job = subparsers.add_parser("run-job")
    run_job.add_argument("--job-id", type=int, required=True)
    run_job.add_argument("--model", default=DEFAULT_MODEL)
    run_job.add_argument("--json", action="store_true")
    run_job.set_defaults(func=run_job_command)

    report = subparsers.add_parser("report")
    report.add_argument("--json", action="store_true")
    report.set_defaults(func=report_command)

    backfill = subparsers.add_parser("backfill-outputs")
    backfill.add_argument("--json", action="store_true")
    backfill.set_defaults(func=backfill_outputs_command)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "func", None) is None:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
