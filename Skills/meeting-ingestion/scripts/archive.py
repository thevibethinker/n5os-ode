#!/usr/bin/env python3
"""
Meeting Ingestion - Archive Script (v2: D2.1 Archival Contract)

Moves completed meetings from Inbox to canonical archive structure:
  Personal/Meetings/YYYY/MM-Month/week-NN/<meeting-folder>

Folder names are preserved as-is (no renaming during archive).
Rename must happen before archive; after move, rename_locked = true.

Usage:
    python3 archive.py [--dry-run] [--execute]
    python3 archive.py --path <meeting_folder> [--dry-run] [--execute]
"""

import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict
import re

# --- D1 sys.path injection for paths.py ---
from pathlib import Path as _D1Path
sys.path.insert(0, str(_D1Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

from paths import ACTIVE_DIR as INBOX, REJECTED_DIR, ensure_rejected_dir

# D6: terminal statuses — anything here is eligible for archival.
# completed/archived flow to year/month/week; rejected/rejected_intake flow to REJECTED_DIR flat.
TERMINAL_STATUSES = {"completed", "complete", "processed", "archived", "rejected", "rejected_intake"}
REJECTED_STATUSES = {"rejected", "rejected_intake"}  # noqa: E402
MEETINGS = Path("/home/workspace/Personal/Meetings")
ARCHIVE_VERSION = "2.0"


def _extract_date_from_folder_name(folder_name: str) -> str:
    match = re.match(r"^(\d{4}-\d{2}-\d{2})[_-]", folder_name)
    if match:
        return match.group(1)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", folder_name):
        return folder_name
    return "unknown"


def _normalize_meeting_date(raw_date, folder_name: str) -> str:
    if isinstance(raw_date, str) and raw_date:
        candidate = raw_date.strip()
        if "T" in candidate:
            candidate = candidate.split("T", 1)[0]
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
            return candidate
        except Exception:
            pass

    fallback = _extract_date_from_folder_name(folder_name)
    if fallback != "unknown":
        return fallback
    return "unknown"


def compute_archive_path(date_str: str, folder_name: str) -> tuple[Path, dict]:
    """Compute deterministic archive path per D2.1 contract.

    Returns (archive_dir, path_metadata) where archive_dir is the parent
    directory (not including the meeting folder itself).

    Path format: Personal/Meetings/YYYY/MM-Month/week-NN/
    """
    if date_str == "unknown":
        return None, {"error": "missing_meeting_date"}

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None, {"error": f"invalid_date: {date_str}"}

    year = str(dt.year)
    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month_folder = f"{dt.month:02d}-{month_names[dt.month]}"
    iso_week = f"week-{dt.isocalendar()[1]:02d}"

    archive_dir = MEETINGS / year / month_folder / iso_week
    metadata = {
        "year": dt.year,
        "month_folder": month_folder,
        "iso_week": iso_week,
    }
    return archive_dir, metadata


def _meeting_is_already_archived(folder: Path, manifest: dict) -> bool:
    # D6: REJECTED_DIR is terminal; anything under it is already in its resting place.
    try:
        if REJECTED_DIR in folder.parents or folder.parent == REJECTED_DIR:
            return True
    except Exception:
        pass
    archive_section = manifest.get("archive", {})
    if archive_section.get("state") == "archived":
        return True
    if manifest.get("status") in {"archived", "ready"}:
        return True
    if (manifest.get("timestamps", {}) or {}).get("archived_at"):
        return True
    return INBOX not in folder.parents and folder.parent != INBOX


def _check_archive_preconditions(folder: Path, manifest: dict) -> list[str]:
    """Check D2.1 move preconditions. Returns list of blocking reasons."""
    reasons = []

    status = manifest.get("status", "")
    # D6: accept any terminal status for archival.
    if status not in TERMINAL_STATUSES:
        reasons.append(f"status_not_terminal (status={status})")

    if manifest.get("status") == "partial":
        reasons.append("partial_meeting")

    if folder.parent != INBOX:
        reasons.append("not_in_inbox")

    return reasons


def _resolve_collision(target_path: Path, source_manifest: dict) -> Path:
    """Resolve destination collision per D2.1: idempotent for same meeting, suffix for different."""
    if not target_path.exists():
        return target_path

    existing_manifest_path = target_path / "manifest.json"
    if existing_manifest_path.exists():
        try:
            existing = json.loads(existing_manifest_path.read_text())
            existing_id = existing.get("meeting_id") or existing.get("meeting", {}).get("id")
            source_id = source_manifest.get("meeting_id") or source_manifest.get("meeting", {}).get("id")
            if existing_id and source_id and existing_id == source_id:
                return target_path  # idempotent — same meeting
        except Exception:
            pass

    for attempt in range(1, 10):
        suffixed = target_path.parent / f"{target_path.name}--retry-{attempt:02d}"
        if not suffixed.exists():
            return suffixed

    raise RuntimeError(f"Too many collisions at {target_path}")


def archive_meeting(meeting: dict, dry_run: bool = False) -> dict:
    """Archive a single meeting per D2.1 contract."""
    folder = meeting["path"]
    date_str = meeting["date"]
    manifest = meeting.get("manifest", {}) or {}

    if _meeting_is_already_archived(folder, manifest):
        logger.info(f"  Already archived, skipping: {folder.name}")
        return {
            "success": True,
            "skipped": "already_archived",
            "path": str(folder),
        }

    # D6: rejected/rejected_intake folders go FLAT into REJECTED_DIR (no year/month/week).
    if manifest.get("status") in REJECTED_STATUSES:
        rejected_root = ensure_rejected_dir()
        target = rejected_root / folder.name
        if folder.parent == rejected_root:
            return {"success": True, "skipped": "already_rejected", "path": str(folder)}
        if dry_run:
            return {"success": True, "dry_run": True, "from": str(folder), "to": str(target), "route": "rejected_flat"}
        import shutil as _sh
        if target.exists():
            # Suffix collision defensively
            for i in range(1, 10):
                alt = rejected_root / f"{folder.name}--{i:02d}"
                if not alt.exists():
                    target = alt
                    break
        _sh.move(str(folder), str(target))
        return {"success": True, "from": str(folder), "to": str(target), "route": "rejected_flat"}

    precondition_failures = _check_archive_preconditions(folder, manifest)
    if precondition_failures:
        logger.warning(f"  Archive blocked for {folder.name}: {precondition_failures}")
        return {
            "success": False,
            "error": "preconditions_failed",
            "reasons": precondition_failures,
            "path": str(folder),
        }

    archive_dir, path_meta = compute_archive_path(date_str, folder.name)
    if archive_dir is None:
        logger.warning(f"  Cannot compute archive path for {folder.name}: {path_meta.get('error')}")
        return {
            "success": False,
            "error": path_meta.get("error", "path_computation_failed"),
            "path": str(folder),
        }

    # Folder name preserved as-is — no clean_folder_name, no renaming
    canonical_name = folder.name
    target_path = archive_dir / canonical_name

    source_path_rel = str(folder.relative_to(MEETINGS.parent.parent))
    dest_path_rel_expected = str((archive_dir / canonical_name).relative_to(MEETINGS.parent.parent))

    result = {
        "from": str(folder),
        "to": str(target_path),
        "year": path_meta.get("year"),
        "month_folder": path_meta.get("month_folder"),
        "iso_week": path_meta.get("iso_week"),
        "canonical_folder_name": canonical_name,
    }

    if dry_run:
        result["dry_run"] = True
        logger.info(f"  Would move: {folder.name}")
        logger.info(f"    → {path_meta['month_folder']}/{path_meta['iso_week']}/{canonical_name}")
        return result

    archive_dir.mkdir(parents=True, exist_ok=True)

    collision_attempt = 0
    resolved_target = _resolve_collision(target_path, manifest)
    if resolved_target != target_path:
        collision_attempt = 1
        logger.info(f"  Collision resolved: {target_path.name} → {resolved_target.name}")
        target_path = resolved_target

    shutil.move(str(folder), str(target_path))
    logger.info(f"  Moved to: {target_path}")

    archived_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    # Write archive manifest section
    manifest_path = target_path / "manifest.json"
    if manifest_path.exists():
        try:
            m = json.loads(manifest_path.read_text())
            m["status"] = "ready" if m.get("$schema") == "manifest-v3" else "archived"
            m.setdefault("timestamps", {})["archived_at"] = archived_at
            m.setdefault("status_history", []).append({
                "status": m["status"],
                "at": archived_at,
            })
            m["archive"] = {
                "state": "archived",
                "eligible": True,
                "archived_at": archived_at,
                "archive_version": ARCHIVE_VERSION,
                "source_path": source_path_rel,
                "destination_path": str(target_path.relative_to(MEETINGS.parent.parent)),
                "year": path_meta.get("year"),
                "month_folder": path_meta.get("month_folder"),
                "iso_week": path_meta.get("iso_week"),
                "canonical_folder_name": canonical_name,
                "archived_folder_name": target_path.name,
                "rename_locked": True,
                "moved_from_inbox": True,
                "memory_routing_outcome_required": "succeeded",
                "collision_policy": "suffix-retry-with-provenance",
                "collision_attempt": collision_attempt,
                "errors": [],
            }
            manifest_path.write_text(json.dumps(m, indent=2))
        except Exception as e:
            logger.warning(f"  Could not update manifest for {target_path.name}: {e}")

    # Write archive audit sidecar
    try:
        audit = {
            "meeting_id": canonical_name,
            "archived_at": archived_at,
            "source_path": source_path_rel,
            "destination_path": str(target_path.relative_to(MEETINGS.parent.parent)),
            "canonical_folder_name": canonical_name,
            "rename_locked": True,
            "memory_routing_outcome": "succeeded",
            "collision_policy": "suffix-retry-with-provenance",
            "collision_attempt": collision_attempt,
            "errors": [],
        }
        (target_path / "archive-audit.json").write_text(json.dumps(audit, indent=2))
    except Exception as e:
        logger.warning(f"  Could not write archive audit: {e}")

    result["success"] = True
    result["archived_path"] = str(target_path)
    result["collision_attempt"] = collision_attempt
    return result


def archive_meeting_path(meeting_path: Path, dry_run: bool = False) -> dict:
    """Archive one meeting folder by path."""
    manifest_path = meeting_path / "manifest.json"
    if not manifest_path.exists():
        return {"success": False, "error": "manifest_missing", "path": str(meeting_path)}

    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as e:
        return {"success": False, "error": f"manifest_unreadable: {e}", "path": str(meeting_path)}

    meeting = {
        "path": meeting_path,
        "name": meeting_path.name,
        "date": _normalize_meeting_date(
            (manifest.get("meeting", {}) or {}).get("date") or manifest.get("date") or manifest.get("meeting_date", "unknown"),
            meeting_path.name,
        ),
        "manifest": manifest,
    }
    return archive_meeting(meeting, dry_run=dry_run)


def find_complete_meetings() -> list[dict]:
    """Find all meetings in Inbox ready for archival."""
    complete = []

    if not INBOX.exists():
        return complete

    for folder in sorted(INBOX.iterdir()):
        if not folder.is_dir() or folder.name.startswith((".", "_")):
            continue

        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            manifest = json.loads(manifest_path.read_text())

            # D6: accept all terminal statuses for archival sweep.
            if manifest.get("status") not in TERMINAL_STATUSES:
                continue

            date = (
                (manifest.get("meeting", {}) or {}).get("date")
                or manifest.get("date")
                or manifest.get("meeting_date", "unknown")
            )
            date = _normalize_meeting_date(date, folder.name)

            complete.append({
                "path": folder,
                "name": folder.name,
                "date": date,
                "manifest": manifest,
            })
        except Exception as e:
            logger.warning(f"Could not read manifest for {folder.name}: {e}")

    return complete


def archive_all(dry_run: bool = True) -> dict:
    """Archive all eligible meetings from Inbox."""
    print(f"\n{'='*60}")
    print(f"MEETING ARCHIVAL {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print(f"{'='*60}\n")

    complete = find_complete_meetings()

    print(f"Found {len(complete)} meetings ready for archival in Inbox\n")

    if not complete:
        return {"archived": 0, "results": []}

    results = []

    for meeting in complete:
        result = archive_meeting(meeting, dry_run=dry_run)
        results.append(result)
        status_icon = "✓" if result.get("success") else ("⊘" if result.get("dry_run") else "✗")
        print(f"  {status_icon} {meeting['name']}")
        if result.get("to"):
            print(f"    → {result['to']}")
        if result.get("reasons"):
            print(f"    blocked: {', '.join(result['reasons'])}")

    succeeded = len([r for r in results if r.get("success") or r.get("dry_run")])
    failed = len([r for r in results if not r.get("success") and not r.get("dry_run")])
    skipped = len([r for r in results if r.get("skipped")])

    print(f"\n{'='*60}")
    print(f"SUMMARY: {succeeded} archived, {failed} failed, {skipped} skipped")
    print(f"{'='*60}\n")

    return {
        "archived": succeeded,
        "failed": failed,
        "skipped": skipped,
        "results": results,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Archive completed meetings (D2.1 contract)")
    parser.add_argument("--path", type=str, help="Archive a single meeting folder")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Preview without executing (default)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform archival")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    dry_run = not args.execute

    if args.path:
        results = archive_meeting_path(Path(args.path), dry_run=dry_run)
    else:
        results = archive_all(dry_run=dry_run)

    if args.json:
        print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
