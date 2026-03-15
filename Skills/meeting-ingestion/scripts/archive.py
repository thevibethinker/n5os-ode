#!/usr/bin/env python3
"""
Meeting Ingestion - Archive Script

Moves completed meetings from Inbox to weekly folders with internal/external routing.

Usage:
    python3 archive.py [--dry-run] [--execute]
"""

import argparse
import json
import logging
import re
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
INBOX = WORKSPACE / "Personal/Meetings/Inbox"
MEETINGS = WORKSPACE / "Personal/Meetings"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_week_folder(date_str: str) -> str:
    """Get Week-of-YYYY-MM-DD folder name (Monday of that week)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        monday = date - timedelta(days=date.weekday())
        return f"Week-of-{monday.strftime('%Y-%m-%d')}"
    except Exception:
        return "Week-of-Unknown"


def _extract_date_from_folder_name(folder_name: str) -> str:
    """Extract YYYY-MM-DD from a meeting folder name prefix when present."""
    match = re.match(r"^(\d{4}-\d{2}-\d{2})[_-]", folder_name)
    if match:
        return match.group(1)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", folder_name):
        return folder_name
    return "unknown"


def _normalize_meeting_date(raw_date: str, folder_name: str) -> str:
    """Return canonical YYYY-MM-DD when possible, else 'unknown'."""
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


def _resolve_meeting_type(manifest: dict) -> str:
    """Resolve canonical meeting type from known manifest locations."""
    crm_type = (manifest.get("crm_enrichment", {}) or {}).get("classification")
    if isinstance(crm_type, str) and crm_type.lower() in {"internal", "external"}:
        return crm_type.lower()

    nested_type = (manifest.get("meeting", {}) or {}).get("type")
    if isinstance(nested_type, str) and nested_type.lower() in {"internal", "external"}:
        return nested_type.lower()

    legacy_type = manifest.get("meeting_type")
    if isinstance(legacy_type, str) and legacy_type.lower() in {"internal", "external"}:
        return legacy_type.lower()

    return "external"


def clean_folder_name(name: str) -> str:
    """Clean a meeting folder name for archival."""
    for suffix in ["_[P]", "_[M]", "_[B]", "_[C]", "_[R]"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    name = name.replace("_", "-")
    name = "-".join(part for part in name.split("-") if part)

    return name


def find_complete_meetings() -> list[dict]:
    """Find meetings ready for archival in Inbox."""
    complete = []

    if not INBOX.exists():
        return complete

    for folder in INBOX.iterdir():
        if not folder.is_dir() or folder.name.startswith((".", "_")):
            continue

        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            manifest = json.loads(manifest_path.read_text())

            if manifest.get("status") == "processed":
                meeting_type = _resolve_meeting_type(manifest)
                date = manifest.get("meeting", {}).get("date", "unknown")
            elif manifest.get("status") == "complete":
                meeting_type = _resolve_meeting_type(manifest)
                date = manifest.get("date", manifest.get("meeting_date", "unknown"))
            else:
                continue

            complete.append(
                {
                    "path": folder,
                    "name": folder.name,
                    "date": _normalize_meeting_date(date, folder.name),
                    "meeting_type": meeting_type,
                    "manifest": manifest,
                }
            )
        except Exception as exc:
            logger.warning("Could not read manifest for %s: %s", folder.name, exc)

    return complete


def archive_meeting(meeting: dict, dry_run: bool = False) -> dict:
    """Archive a single meeting to its weekly folder."""
    folder = meeting["path"]
    week_name = get_week_folder(meeting["date"])
    subfolder = "internal" if meeting["meeting_type"] == "internal" else "external"
    target_path = MEETINGS / week_name / subfolder / clean_folder_name(folder.name)

    result = {
        "from": str(folder),
        "to": str(target_path),
        "week": week_name,
        "type": meeting["meeting_type"],
        "subfolder": subfolder,
    }

    if dry_run:
        result["dry_run"] = True
        logger.info("  Would move: %s", folder.name)
        logger.info("    → %s/%s/%s", week_name, subfolder, clean_folder_name(folder.name))
        return result

    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        logger.info("  Target exists, merging: %s", target_path.name)
        merged = 0
        for item in folder.iterdir():
            dest = target_path / item.name
            if not dest.exists():
                if item.is_file():
                    shutil.copy2(str(item), str(dest))
                else:
                    shutil.copytree(str(item), str(dest))
                merged += 1
            elif item.is_file() and dest.is_file() and item.stat().st_size > dest.stat().st_size:
                shutil.copy2(str(item), str(dest))
        shutil.rmtree(folder)
        result["merged"] = True
        result["merged_count"] = merged
    else:
        shutil.move(str(folder), str(target_path))

    manifest_path = target_path / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            if manifest.get("$schema") == "manifest-v3":
                manifest["status"] = "archived"
                manifest.setdefault("timestamps", {})["archived_at"] = datetime.utcnow().isoformat() + "Z"
                manifest.setdefault("status_history", []).append(
                    {"status": "archived", "at": datetime.utcnow().isoformat() + "Z"}
                )
            else:
                manifest["status"] = "archived"
                manifest["archived_at"] = datetime.utcnow().isoformat() + "Z"
            manifest_path.write_text(json.dumps(manifest, indent=2))
        except Exception as exc:
            logger.warning("Could not update manifest for %s: %s", target_path.name, exc)

    result["success"] = True
    return result


def archive_all(dry_run: bool = True) -> dict:
    """Archive all complete meetings."""
    print(f"\n{'=' * 60}")
    print(f"MEETING ARCHIVAL {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print(f"{'=' * 60}\n")

    complete = find_complete_meetings()
    print(f"Found {len(complete)} meetings ready for archival in Inbox\n")

    if not complete:
        return {"archived": 0, "failed": 0, "results": []}

    grouped = defaultdict(lambda: defaultdict(list))
    for meeting in complete:
        grouped[get_week_folder(meeting["date"])][meeting["meeting_type"]].append(meeting)

    results = []
    for week in sorted(grouped):
        week_groups = grouped[week]
        total = sum(len(items) for items in week_groups.values())
        print(f"--- {week} ({total} meetings) ---")
        for meeting_type in sorted(week_groups):
            meetings = week_groups[meeting_type]
            print(f"  {meeting_type.upper()}: {len(meetings)} meetings")
            for meeting in meetings:
                results.append(archive_meeting(meeting, dry_run=dry_run))
        print()

    succeeded = len([r for r in results if r.get("success") or r.get("dry_run")])
    failed = len([r for r in results if not r.get("success") and not r.get("dry_run")])

    print(f"{'=' * 60}")
    print("SUMMARY:")
    print(f"  Archived: {succeeded}")
    print(f"  Failed:   {failed}")
    print(f"{'=' * 60}\n")

    return {"archived": succeeded, "failed": failed, "results": results}


def main():
    parser = argparse.ArgumentParser(description="Archive completed meetings")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview without executing (default)")
    parser.add_argument("--execute", action="store_true", help="Actually perform archival")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = archive_all(dry_run=not args.execute)
    if args.json:
        print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
