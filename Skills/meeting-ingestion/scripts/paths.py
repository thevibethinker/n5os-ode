"""Canonical path helper for the meeting-ingestion pipeline.

Single source of truth for filesystem layout. All scripts in this skill (and
external callers like webhook processors) should import from this module
rather than hardcoding `/home/workspace/Personal/Meetings/...` strings.

Layout (post-D1 of meeting-pipeline-redesign):
    Personal/Meetings/
        Active/           <- unified in-flight queue (was Inbox + Needs-Review)
        archive/          <- terminal meetings, year/month/week structure
        Rejected/         <- D4-added lane for short/empty transcripts

The old `Inbox/` and `Needs-Review/` folders are retired; manifests encode
review state via `needs_review: bool` and terminal state via `status`.
"""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_WORKSPACE = "/home/workspace"
WORKSPACE = Path(os.environ.get("MEETINGS_WORKSPACE", _DEFAULT_WORKSPACE))

MEETINGS_ROOT: Path = WORKSPACE / "Personal" / "Meetings"

ACTIVE_DIR: Path = MEETINGS_ROOT / "Active"
ARCHIVE_DIR: Path = MEETINGS_ROOT / "archive"
REJECTED_DIR: Path = MEETINGS_ROOT / "Rejected"

LEGACY_INBOX_DIR: Path = MEETINGS_ROOT / "Inbox"
LEGACY_REVIEW_DIR: Path = MEETINGS_ROOT / "Needs-Review"


def ensure_active_dir() -> Path:
    """Ensure the Active queue folder exists and return it."""
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    return ACTIVE_DIR


def ensure_rejected_dir() -> Path:
    """Ensure the Rejected lane exists and return it."""
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    return REJECTED_DIR


def resolve_queue_dir() -> Path:
    """Return the live in-flight queue dir.

    After D1 completes and the legacy Inbox is gone, this always returns
    ACTIVE_DIR.
    """
    if ACTIVE_DIR.exists():
        return ACTIVE_DIR
    if LEGACY_INBOX_DIR.exists():
        return LEGACY_INBOX_DIR
    return ensure_active_dir()


def iter_archived_meetings():
    """Yield every archived meeting folder Path.

    Walks the real canonical layout:
        Personal/Meetings/YYYY/MM-Month/week-NN/<meeting>/
        Personal/Meetings/archive/pre-2026/<week>/<meeting>/

    Skips non-archive top-level entries (Active, archive, non-year names).
    """
    if not MEETINGS_ROOT.exists():
        return
    for year_dir in MEETINGS_ROOT.iterdir():
        if not year_dir.is_dir():
            continue
        if year_dir.name.isdigit() and len(year_dir.name) == 4:
            # YYYY/MM-Month/week-NN/<meeting>
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue
                for week_dir in month_dir.iterdir():
                    if not week_dir.is_dir() or not week_dir.name.startswith("week-"):
                        continue
                    for meeting in week_dir.iterdir():
                        if meeting.is_dir():
                            yield meeting
        elif year_dir.name == "archive":
            # archive/pre-2026/<week>/<meeting>
            for sub in year_dir.iterdir():
                if not sub.is_dir():
                    continue
                for week_dir in sub.iterdir():
                    if not week_dir.is_dir():
                        continue
                    for meeting in week_dir.iterdir():
                        if meeting.is_dir():
                            yield meeting


def find_existing_meeting(date_prefix: str, title_words: set[str]) -> Path | None:
    """Search Active + archive for a meeting matching (date_prefix, title_words).

    Match rule: folder name starts with date_prefix AND >=2 title words overlap
    with folder-name words (lowercase, hyphens split as spaces).

    Args:
        date_prefix: ``YYYY-MM-DD`` prefix; empty string disables dedup.
        title_words: set of lowercase alphanumeric words from the candidate title.

    Returns:
        The first matching meeting Path, or None.
    """
    if not date_prefix:
        return None

    def _match(folder: Path) -> bool:
        if not folder.is_dir():
            return False
        if not folder.name.startswith(date_prefix):
            return False
        existing = set(folder.name.lower().replace("-", " ").split())
        return len(existing & title_words) >= 2

    if ACTIVE_DIR.exists():
        for folder in ACTIVE_DIR.iterdir():
            if _match(folder):
                return folder

    for folder in iter_archived_meetings():
        if _match(folder):
            return folder

    return None


__all__ = [
    "WORKSPACE",
    "MEETINGS_ROOT",
    "ACTIVE_DIR",
    "ARCHIVE_DIR",
    "REJECTED_DIR",
    "LEGACY_INBOX_DIR",
    "LEGACY_REVIEW_DIR",
    "ensure_active_dir",
    "ensure_rejected_dir",
    "resolve_queue_dir",
    "iter_archived_meetings",
    "find_existing_meeting",
]
