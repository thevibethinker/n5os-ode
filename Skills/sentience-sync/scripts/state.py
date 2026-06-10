"""
Shared state management for sentience-sync.
Atomic writes, per-stream seen ID tracking, append-only ledgers, and guardrail state.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"
CORRECTION_STATUSES = {"rolled_back", "review_rejected"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write(path: Path, data: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def build_projection_id(candidate_id: str, destination: str) -> str:
    return hashlib.sha256(f"{candidate_id}::{destination}".encode("utf-8")).hexdigest()[:24]


def build_queue_id(candidate: dict[str, Any], suggested_action: str | None = None) -> str:
    candidate_id = candidate.get("candidate_id") or candidate.get("id") or "unknown"
    candidate_type = candidate.get("candidate_type") or candidate.get("type") or "unknown"
    action = suggested_action or candidate.get("suggested_action") or "review"
    return hashlib.sha256(f"{candidate_id}::{candidate_type}::{action}".encode("utf-8")).hexdigest()[:24]


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    try:
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            entries.append(json.loads(line))
    except (json.JSONDecodeError, OSError):
        return []
    return entries


def _append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    line = json.dumps(entry, sort_keys=True)
    payload = f"{existing}{line}\n" if existing else f"{line}\n"
    atomic_write(path, payload)


def _coerce_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _matches_time_range(timestamp: Any, time_range: Any) -> bool:
    if time_range is None:
        return True
    dt = _coerce_datetime(timestamp)
    if dt is None:
        return False

    start: datetime | None = None
    end: datetime | None = None

    if isinstance(time_range, str):
        now = datetime.now(timezone.utc)
        if time_range.endswith("h"):
            start = now - timedelta(hours=float(time_range[:-1]))
            end = now
        elif time_range.endswith("d"):
            start = now - timedelta(days=float(time_range[:-1]))
            end = now
        else:
            start = _coerce_datetime(time_range)
    elif isinstance(time_range, dict):
        start = _coerce_datetime(time_range.get("start"))
        end = _coerce_datetime(time_range.get("end"))
    elif isinstance(time_range, (tuple, list)):
        if len(time_range) >= 1:
            start = _coerce_datetime(time_range[0])
        if len(time_range) >= 2:
            end = _coerce_datetime(time_range[1])
    else:
        start = _coerce_datetime(time_range)

    if start and dt < start:
        return False
    if end and dt > end:
        return False
    return True


def _latest_by_key(entries: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for entry in entries:
        entry_key = entry.get(key)
        if entry_key:
            latest[str(entry_key)] = entry
    return latest


class SeenStore:
    """Per-stream seen ID tracking with TTL-based retention."""

    def __init__(self, path: Path = DATA_DIR / "seen_store.json", ttl_days: int = 30):
        self.path = path
        self.ttl_days = ttl_days
        self._data = self._load()

    def _load(self) -> dict:
        data = _read_json(self.path, {"streams": {}})
        if not isinstance(data, dict):
            return {"streams": {}}
        data.setdefault("streams", {})
        return data

    def save(self):
        atomic_write(self.path, json.dumps(self._data, indent=2))

    def is_seen(self, stream: str, mem_id: str) -> bool:
        return mem_id in self._data.get("streams", {}).get(stream, {})

    def mark_seen(self, stream: str, mem_id: str):
        if stream not in self._data.setdefault("streams", {}):
            self._data["streams"][stream] = {}
        self._data["streams"][stream][mem_id] = utc_now_iso()

    def prune(self):
        cutoff = (datetime.now(timezone.utc) - timedelta(days=self.ttl_days)).isoformat()
        for stream in list(self._data.get("streams", {})):
            ids = self._data["streams"][stream]
            self._data["streams"][stream] = {
                k: v for k, v in ids.items() if v >= cutoff
            }
            if not self._data["streams"][stream]:
                del self._data["streams"][stream]

    def count(self, stream: str | None = None) -> int:
        if stream:
            return len(self._data.get("streams", {}).get(stream, {}))
        return sum(len(v) for v in self._data.get("streams", {}).values())


class WatermarkStore:
    """Per-stream high-water-mark timestamps."""

    def __init__(self, path: Path = DATA_DIR / "watermarks.json"):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        data = _read_json(self.path, {})
        return data if isinstance(data, dict) else {}

    def save(self):
        atomic_write(self.path, json.dumps(self._data, indent=2))

    def get(self, stream: str) -> str | None:
        return self._data.get(stream)

    def set(self, stream: str, ts: str):
        self._data[stream] = ts


class PushLedger:
    """Track what has been pushed to prevent duplicate pushes."""

    def __init__(self, path: Path = DATA_DIR / "push_ledger.json"):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        data = _read_json(self.path, {"pushed": {}})
        if not isinstance(data, dict):
            return {"pushed": {}}
        data.setdefault("pushed", {})
        return data

    def save(self):
        atomic_write(self.path, json.dumps(self._data, indent=2))

    def is_pushed(self, source_key: str) -> bool:
        return source_key in self._data.get("pushed", {})

    def mark_pushed(self, source_key: str, sentience_id: str):
        self._data.setdefault("pushed", {})[source_key] = {
            "sentience_id": sentience_id,
            "pushed_at": utc_now_iso(),
        }

    def count(self) -> int:
        return len(self._data.get("pushed", {}))


class GuardrailState:
    """Track circuit-breaker state for CRM auto-writes."""

    def __init__(self, path: Path = DATA_DIR / "guardrail_state.json"):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        default = {
            "auto_writes_paused": False,
            "pause_reason": None,
            "triggered_at": None,
            "last_resumed_at": None,
            "correction_threshold": 0.10,
            "correction_rate_threshold": 0.10,
            "correction_window_hours": 24,
            "auto_write_count": 0,
            "manual_correction_count": 0,
            "correction_count": 0,
            "correction_rate": 0.0,
            "last_checked_at": None,
            "alerts": [],
        }
        data = _read_json(self.path, default)
        if not isinstance(data, dict):
            return default
        for key, value in default.items():
            data.setdefault(key, value)
        return data

    def save(self):
        atomic_write(self.path, json.dumps(self._data, indent=2))

    def is_paused(self) -> bool:
        return bool(self._data.get("auto_writes_paused"))

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)

    def update_metrics(
        self,
        *,
        auto_write_count: int,
        correction_count: int,
        correction_rate: float,
        threshold: float,
        window_hours: int,
    ) -> dict[str, Any]:
        self._data["auto_write_count"] = auto_write_count
        self._data["manual_correction_count"] = correction_count
        self._data["correction_count"] = correction_count
        self._data["correction_threshold"] = threshold
        self._data["correction_rate_threshold"] = threshold
        self._data["correction_window_hours"] = window_hours
        self._data["correction_rate"] = correction_rate
        self._data["last_checked_at"] = utc_now_iso()
        self.save()
        return self.snapshot()

    def pause(
        self,
        reason: str,
        *,
        auto_write_count: int,
        correction_count: int,
        correction_rate: float,
        threshold: float,
        window_hours: int,
    ) -> dict[str, Any]:
        self.update_metrics(
            auto_write_count=auto_write_count,
            correction_count=correction_count,
            correction_rate=correction_rate,
            threshold=threshold,
            window_hours=window_hours,
        )
        last_alert = self._data.get("alerts", [])[-1] if self._data.get("alerts") else None
        duplicate_alert = (
            self._data.get("auto_writes_paused")
            and last_alert
            and last_alert.get("reason") == reason
            and last_alert.get("auto_write_count") == auto_write_count
            and last_alert.get("correction_count") == correction_count
            and last_alert.get("correction_rate") == correction_rate
            and last_alert.get("threshold") == threshold
            and last_alert.get("window_hours") == window_hours
        )
        self._data["auto_writes_paused"] = True
        self._data["pause_reason"] = reason
        if not duplicate_alert:
            self._data["triggered_at"] = utc_now_iso()
            self._data.setdefault("alerts", []).append(
                {
                    "triggered_at": self._data["triggered_at"],
                    "reason": reason,
                    "auto_write_count": auto_write_count,
                    "correction_count": correction_count,
                    "correction_rate": correction_rate,
                    "threshold": threshold,
                    "window_hours": window_hours,
                }
            )
        self.save()
        return self.snapshot()

    def resume(self, reason: str = "manual_resume") -> dict[str, Any]:
        self._data["auto_writes_paused"] = False
        self._data["pause_reason"] = reason
        self._data["last_resumed_at"] = utc_now_iso()
        self.save()
        return self.snapshot()


class ProjectionLedger:
    """Append-only projection ledger with replay-safe latest-state queries."""

    def __init__(
        self,
        path: Path = DATA_DIR / "projection_ledger.jsonl",
        guardrail_state: GuardrailState | None = None,
    ):
        self.path = path
        self.guardrail_state = guardrail_state or GuardrailState()

    def _entries(self) -> list[dict[str, Any]]:
        return _read_jsonl(self.path)

    def _latest(self) -> dict[str, dict[str, Any]]:
        return _latest_by_key(self._entries(), "projection_id")

    def _normalize_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        now = utc_now_iso()
        candidate_id = str(entry.get("candidate_id") or entry.get("id") or "unknown")
        destination = str(entry.get("destination") or "review_queue")
        status = str(entry.get("status") or "pending")
        action = str(entry.get("action") or "auto_write")

        if action == "queued_for_review" and status == "pending":
            status = "review_pending"

        normalized = {
            "projection_id": entry.get("projection_id") or build_projection_id(candidate_id, destination),
            "candidate_id": candidate_id,
            "candidate_type": str(entry.get("candidate_type") or entry.get("type") or "unknown"),
            "destination": destination,
            "action": action,
            "confidence_tier": str(entry.get("confidence_tier") or "unknown"),
            "source_event_ids": list(dict.fromkeys(entry.get("source_event_ids") or [])),
            "local_record_id": entry.get("local_record_id"),
            "local_write_type": entry.get("local_write_type"),
            "written_at": entry.get("written_at"),
            "rollback_data": entry.get("rollback_data"),
            "status": status,
            "queue_id": entry.get("queue_id"),
            "reason": entry.get("reason"),
            "audit_flag": bool(entry.get("audit_flag", False)),
            "created_at": entry.get("created_at") or now,
            "updated_at": entry.get("updated_at") or now,
            "status_changed_at": entry.get("status_changed_at") or now,
        }

        if normalized["status"] == "written" and not normalized["written_at"]:
            normalized["written_at"] = normalized["updated_at"]

        return normalized

    def count(self, latest_only: bool = True) -> int:
        return len(self._latest()) if latest_only else len(self._entries())

    def is_projected(self, candidate_id: str, destination: str) -> bool:
        projection_id = build_projection_id(candidate_id, destination)
        latest = self._latest().get(projection_id)
        if not latest:
            return False
        return latest.get("status") not in CORRECTION_STATUSES

    def get_projection_for_candidate(self, candidate_id: str, destination: str) -> dict[str, Any] | None:
        return self.get_projection(build_projection_id(candidate_id, destination))

    def detect_replay(self, candidate_id: str, destination: str) -> dict[str, Any]:
        existing = self.get_projection_for_candidate(candidate_id, destination)
        if existing is None:
            return {
                "replay_detected": False,
                "outcome": "new",
                "existing": None,
            }
        if existing.get("status") in CORRECTION_STATUSES:
            return {
                "replay_detected": False,
                "outcome": "replay_allowed_after_correction",
                "existing": existing,
            }
        status = existing.get("status")
        return {
            "replay_detected": True,
            "outcome": "already_written" if status == "written" else "already_recorded",
            "existing": existing,
        }

    def record_projection(self, entry: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_entry(entry)
        _append_jsonl(self.path, normalized)
        return normalized

    def record_projection_once(self, entry: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        normalized = self._normalize_entry(entry)
        replay = self.detect_replay(normalized["candidate_id"], normalized["destination"])
        if replay["replay_detected"]:
            return replay["existing"], False
        _append_jsonl(self.path, normalized)
        return normalized, True

    def get_projection(self, projection_id: str) -> dict[str, Any] | None:
        return self._latest().get(projection_id)

    def update_status(self, projection_id: str, status: str, **updates: Any) -> dict[str, Any]:
        latest = self.get_projection(projection_id)
        if latest is None:
            raise KeyError(f"Unknown projection_id: {projection_id}")

        now = utc_now_iso()
        next_entry = dict(latest)
        next_entry.update(updates)
        next_entry["status"] = status
        next_entry["updated_at"] = now
        next_entry["status_changed_at"] = now

        if status == "written" and not next_entry.get("written_at"):
            next_entry["written_at"] = now

        normalized = self._normalize_entry(next_entry)
        _append_jsonl(self.path, normalized)
        if status == "written" or status in CORRECTION_STATUSES:
            self.evaluate_circuit_breaker()
        return normalized

    def mark_written(
        self,
        projection_id: str,
        *,
        rollback_data: dict[str, Any],
        written_at: str | None = None,
        **updates: Any,
    ) -> dict[str, Any]:
        if rollback_data is None:
            raise ValueError("rollback_data is required for every write")
        return self.update_status(
            projection_id,
            "written",
            rollback_data=rollback_data,
            written_at=written_at or utc_now_iso(),
            **updates,
        )

    def mark_rolled_back(self, projection_id: str, rollback_data: dict[str, Any] | None = None, reason: str | None = None) -> dict[str, Any]:
        latest = self.get_projection(projection_id)
        if latest is None:
            raise KeyError(f"Unknown projection_id: {projection_id}")
        return self.update_status(
            projection_id,
            "rolled_back",
            rollback_data=rollback_data or latest.get("rollback_data"),
            reason=reason or latest.get("reason"),
        )

    def get_projections(
        self,
        time_range: Any = None,
        destination: str | None = None,
        status: str | list[str] | set[str] | None = None,
    ) -> list[dict[str, Any]]:
        entries = list(self._latest().values())
        if destination:
            entries = [entry for entry in entries if entry.get("destination") == destination]
        if status is not None:
            statuses = {status} if isinstance(status, str) else set(status)
            entries = [entry for entry in entries if entry.get("status") in statuses]
        if time_range is not None:
            entries = [
                entry for entry in entries
                if _matches_time_range(
                    entry.get("status_changed_at") or entry.get("updated_at") or entry.get("written_at") or entry.get("created_at"),
                    time_range,
                )
            ]
        entries.sort(
            key=lambda entry: _coerce_datetime(
                entry.get("status_changed_at") or entry.get("updated_at") or entry.get("written_at") or entry.get("created_at")
            ) or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return entries

    def correction_count(self, time_range: Any = "24h") -> int:
        return self.manual_correction_count(time_range=time_range)

    def auto_write_count(self, time_range: Any = "24h") -> int:
        return sum(
            1
            for entry in self._entries()
            if entry.get("action") == "auto_write"
            and entry.get("status") == "written"
            and _matches_time_range(
                entry.get("written_at") or entry.get("status_changed_at") or entry.get("updated_at") or entry.get("created_at"),
                time_range,
            )
        )

    def manual_correction_count(self, time_range: Any = "24h") -> int:
        return sum(
            1
            for entry in self._entries()
            if entry.get("action") == "auto_write"
            and entry.get("status") in CORRECTION_STATUSES
            and _matches_time_range(
                entry.get("status_changed_at") or entry.get("updated_at") or entry.get("created_at"),
                time_range,
            )
        )

    def evaluate_circuit_breaker(
        self,
        threshold: float | None = None,
        window_hours: int = 24,
        *,
        correction_rate_threshold: float | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        applied_threshold = correction_rate_threshold if correction_rate_threshold is not None else threshold
        if applied_threshold is None:
            applied_threshold = 0.10
        auto_write_count = self.auto_write_count(time_range=f"{window_hours}h")
        correction_count = self.manual_correction_count(time_range=f"{window_hours}h")
        correction_rate = (correction_count / auto_write_count) if auto_write_count else 0.0

        if auto_write_count and correction_rate > applied_threshold:
            reason = (
                "Circuit breaker tripped: "
                f"{correction_count} manual corrections / {auto_write_count} auto-writes "
                f"in the last {window_hours}h ({correction_rate:.1%} > {applied_threshold:.1%})."
            )
            snapshot = self.guardrail_state.pause(
                reason,
                auto_write_count=auto_write_count,
                correction_count=correction_count,
                correction_rate=correction_rate,
                threshold=applied_threshold,
                window_hours=window_hours,
            )
            return True, snapshot

        snapshot = self.guardrail_state.update_metrics(
            auto_write_count=auto_write_count,
            correction_count=correction_count,
            correction_rate=correction_rate,
            threshold=applied_threshold,
            window_hours=window_hours,
        )
        return False, snapshot


class ReviewQueue:
    """Append-only review queue with latest-state reads."""

    def __init__(self, path: Path = DATA_DIR / "review_queue.jsonl", ledger: ProjectionLedger | None = None):
        self.path = path
        self.ledger = ledger or ProjectionLedger()

    def _entries(self) -> list[dict[str, Any]]:
        return _read_jsonl(self.path)

    def _latest(self) -> dict[str, dict[str, Any]]:
        return _latest_by_key(self._entries(), "queue_id")

    def _normalize_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        now = utc_now_iso()
        candidate = dict(entry.get("candidate") or {})
        suggested_action = entry.get("suggested_action")
        return {
            "queue_id": entry.get("queue_id") or build_queue_id(candidate, suggested_action),
            "candidate": candidate,
            "suggested_action": suggested_action or self._suggested_action(candidate),
            "reason_queued": entry.get("reason_queued") or "manual_review_required",
            "alternative_matches": list(entry.get("alternative_matches") or []),
            "queued_at": entry.get("queued_at") or now,
            "updated_at": entry.get("updated_at") or now,
            "status": entry.get("status") or "pending",
            "review_notes": entry.get("review_notes"),
            "rejection_reason": entry.get("rejection_reason"),
        }

    def _suggested_action(self, candidate: dict[str, Any]) -> str:
        explicit = candidate.get("suggested_action")
        if explicit:
            return str(explicit)
        candidate_type = candidate.get("candidate_type") or candidate.get("type")
        if candidate_type == "new_contact":
            return "create_contact"
        if candidate_type in {"new_company", "company_enrichment"}:
            return "create_company"
        if candidate_type == "identity_mutation":
            target = candidate.get("merge_target_id")
            return f"merge_with_{target}" if target else "merge_review"
        return "add_note"

    def count(self, latest_only: bool = True) -> int:
        return len(self._latest()) if latest_only else len(self._entries())

    def enqueue(
        self,
        candidate: dict[str, Any],
        *,
        suggested_action: str | None = None,
        reason_queued: str | None = None,
        alternative_matches: list[Any] | None = None,
    ) -> dict[str, Any]:
        queue_id = candidate.get("queue_id") or build_queue_id(candidate, suggested_action)
        existing = self._latest().get(queue_id)
        if existing and existing.get("status") == "pending":
            return existing

        normalized = self._normalize_entry(
            {
                "queue_id": queue_id,
                "candidate": candidate,
                "suggested_action": suggested_action,
                "reason_queued": reason_queued,
                "alternative_matches": alternative_matches or candidate.get("alternative_matches") or [],
                "status": "pending",
            }
        )
        _append_jsonl(self.path, normalized)
        return normalized

    def get(self, queue_id: str) -> dict[str, Any] | None:
        return self._latest().get(queue_id)

    def list_entries(
        self,
        *,
        status: str | list[str] | set[str] | None = None,
        candidate_type: str | None = None,
        time_range: Any = None,
    ) -> list[dict[str, Any]]:
        entries = list(self._latest().values())
        if status is not None:
            statuses = {status} if isinstance(status, str) else set(status)
            entries = [entry for entry in entries if entry.get("status") in statuses]
        if candidate_type:
            entries = [
                entry for entry in entries
                if entry.get("candidate", {}).get("candidate_type") == candidate_type
            ]
        if time_range is not None:
            entries = [entry for entry in entries if _matches_time_range(entry.get("updated_at") or entry.get("queued_at"), time_range)]
        entries.sort(
            key=lambda entry: _coerce_datetime(entry.get("updated_at") or entry.get("queued_at")) or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return entries

    def update_status(self, queue_id: str, status: str, *, review_notes: str | None = None, rejection_reason: str | None = None) -> dict[str, Any]:
        latest = self.get(queue_id)
        if latest is None:
            raise KeyError(f"Unknown queue_id: {queue_id}")
        next_entry = dict(latest)
        next_entry["status"] = status
        next_entry["updated_at"] = utc_now_iso()
        if review_notes is not None:
            next_entry["review_notes"] = review_notes
        if rejection_reason is not None:
            next_entry["rejection_reason"] = rejection_reason
        normalized = self._normalize_entry(next_entry)
        _append_jsonl(self.path, normalized)
        return normalized

    def approve(self, queue_id: str, notes: str | None = None) -> dict[str, Any]:
        approved = self.update_status(queue_id, "approved", review_notes=notes)
        candidate = approved.get("candidate", {})
        projection_id = candidate.get("projection_id")
        if projection_id:
            self.ledger.update_status(projection_id, "review_approved", reason=notes)
        return approved

    def reject(self, queue_id: str, reason: str, notes: str | None = None) -> dict[str, Any]:
        rejected = self.update_status(queue_id, "rejected", review_notes=notes, rejection_reason=reason)
        candidate = rejected.get("candidate", {})
        projection_id = candidate.get("projection_id")
        if projection_id:
            self.ledger.update_status(projection_id, "review_rejected", reason=reason)
        return rejected
