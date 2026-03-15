import os
#!/usr/bin/env python3
"""
Intake Router — Moves classified items from Personal/Inbox/ to their destination.

Usage:
    python3 router.py route Personal/Inbox/<folder>/                  # Route one item
    python3 router.py route --batch Personal/Inbox/                   # Route all ready items
    python3 router.py route --dry-run Personal/Inbox/<folder>/        # Preview destination

Destinations:
    meeting    → Personal/Meetings/Inbox/<folder>/
    reflection → Personal/Reflections/YYYY/MM/<folder>/
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(os.environ.get("N5OS_WORKSPACE", Path(__file__).resolve().parents[2] if Path(__file__).resolve().parents[2].joinpath("N5").exists() else Path.cwd()))
MEETINGS_INBOX = WORKSPACE / "Personal" / "Meetings" / "Inbox"
REFLECTIONS_BASE = WORKSPACE / "Personal" / "Reflections"


def resolve_destination(manifest: dict, folder_name: str) -> tuple[Path, str]:
    """Determine destination path based on content type.

    Returns (destination_path, description).
    """
    content_type = manifest.get("content_type", "unclassified")

    if content_type == "meeting":
        return MEETINGS_INBOX / folder_name, "Personal/Meetings/Inbox/"

    elif content_type == "reflection":
        content_date = manifest.get("content", {}).get("date", "")
        if content_date:
            try:
                dt = datetime.strptime(content_date, "%Y-%m-%d")
                year = dt.strftime("%Y")
                month = dt.strftime("%m")
            except ValueError:
                year = datetime.now().strftime("%Y")
                month = datetime.now().strftime("%m")
        else:
            year = datetime.now().strftime("%Y")
            month = datetime.now().strftime("%m")

        dest = REFLECTIONS_BASE / year / month / folder_name
        return dest, f"Personal/Reflections/{year}/{month}/"

    else:
        return None, "unclassified — cannot route"


def resolve_name_conflict(dest: Path) -> Path:
    """If destination exists, auto-version with -v2, -v3, etc."""
    if not dest.exists():
        return dest

    base_name = dest.name
    parent = dest.parent
    version = 2
    while True:
        versioned = parent / f"{base_name}-v{version}"
        if not versioned.exists():
            return versioned
        version += 1


def _add_downstream_meeting_fields(manifest: dict) -> None:
    """Map intake-v1 fields to downstream meeting pipeline format.

    The downstream pipeline (identify → gate → process → archive) expects
    manifest-v3 style fields:  meeting.date, meeting.title, meeting.type,
    participants, timestamps.ingested_at, etc.

    This function ADDS those fields from intake-v1 equivalents without
    overwriting anything that already exists.  This is the compatibility
    bridge between intake-v1 and manifest-v3 consumers.
    """
    content = manifest.get("content", {})
    classification = manifest.get("classification", {})

    # meeting.* block
    meeting = manifest.setdefault("meeting", {})
    if not meeting.get("date") and content.get("date"):
        meeting["date"] = content["date"]
    if not meeting.get("title") and content.get("title"):
        meeting["title"] = content["title"]
    if not meeting.get("summary") and content.get("summary"):
        meeting["summary"] = content["summary"]
    if not meeting.get("type"):
        meeting["type"] = "external"  # safe default; CRM enrichment refines later
    if not meeting.get("duration_minutes") and classification.get("duration_seconds"):
        meeting["duration_minutes"] = max(1, classification["duration_seconds"] // 60)

    # schema marker so downstream knows origin
    manifest.setdefault("schema_version", "v3")  # downstream checks this

    # meeting_id — downstream expects this at top level
    if not manifest.get("meeting_id") and manifest.get("item_id"):
        manifest["meeting_id"] = manifest["item_id"]

    # timestamps compatibility
    ts = manifest.setdefault("timestamps", {})
    if not ts.get("ingested_at") and ts.get("landed_at"):
        ts["ingested_at"] = ts["landed_at"]
    if not ts.get("created_at") and ts.get("landed_at"):
        ts["created_at"] = ts["landed_at"]

    # status_history — ensure an "ingested" entry exists (tick expects it)
    history = manifest.setdefault("status_history", [])
    has_ingested = any(h.get("status") == "ingested" for h in history)
    if not has_ingested and ts.get("landed_at"):
        history.insert(0, {"status": "ingested", "at": ts["landed_at"]})


def route_folder(folder_path: Path, dry_run: bool = False) -> dict:
    """Route a single intake folder to its destination."""
    manifest_path = folder_path / "manifest.json"
    if not manifest_path.exists():
        return {"status": "error", "error": f"No manifest.json in {folder_path}"}

    manifest = json.loads(manifest_path.read_text())

    # Check status — must be at least classified
    status = manifest.get("status", "")
    if status not in ("classified", "heed_scanned"):
        if status == "routed":
            return {"status": "skipped", "reason": "Already routed", "folder": folder_path.name}
        if status == "landed":
            return {"status": "skipped", "reason": "Not yet classified — run classifier first", "folder": folder_path.name}
        return {"status": "skipped", "reason": f"Unexpected status '{status}'", "folder": folder_path.name}

    content_type = manifest.get("content_type", "unclassified")
    if content_type == "unclassified":
        print(f"WARNING: {folder_path.name} is unclassified — skipping. Classify first.")
        return {"status": "skipped", "reason": "Unclassified item", "folder": folder_path.name}

    dest, desc = resolve_destination(manifest, folder_path.name)
    if dest is None:
        return {"status": "error", "error": f"Cannot determine destination for {folder_path.name}"}

    # Check name conflict
    original_dest = dest
    dest = resolve_name_conflict(dest)
    name_conflict = dest != original_dest

    if dry_run:
        conflict_note = f" (renamed from {original_dest.name})" if name_conflict else ""
        print(f"[DRY RUN] {folder_path.name} → {desc}{dest.name}{conflict_note}")
        print(f"  Content type: {content_type}")
        if content_type == "meeting":
            print(f"  Next: python3 meeting_cli.py identify {dest}")
        else:
            print(f"  Next: Process with reflection pipeline")
        return {
            "status": "dry_run",
            "folder": folder_path.name,
            "destination": str(dest),
            "content_type": content_type,
            "name_conflict": name_conflict,
        }

    # Create destination parent directories
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Move folder
    shutil.move(str(folder_path), str(dest))

    # Update manifest at new location
    new_manifest_path = dest / "manifest.json"
    manifest["status"] = "routed"
    manifest.setdefault("timestamps", {})["routed_at"] = datetime.now(timezone.utc).isoformat()
    manifest["routing"] = {
        "destination": str(dest),
        "source_inbox_path": str(folder_path),
        "name_conflict_resolved": name_conflict,
    }

    # D4.2 Compatibility: Map intake-v1 fields to downstream-expected format
    if content_type == "meeting":
        _add_downstream_meeting_fields(manifest)

    new_manifest_path.write_text(json.dumps(manifest, indent=2))

    conflict_note = f" (renamed: {dest.name})" if name_conflict else ""
    print(f"Routed {folder_path.name} → {desc}{dest.name}{conflict_note}")

    # Post-route instructions
    if content_type == "meeting":
        print(f"  Next step: python3 meeting_cli.py identify {dest}")
    else:
        print(f"  Next step: Process with reflection pipeline at {dest}")

    return {
        "status": "routed",
        "folder": folder_path.name,
        "destination": str(dest),
        "content_type": content_type,
        "name_conflict": name_conflict,
    }


def batch_route(inbox_path: Path, dry_run: bool = False) -> dict:
    """Route all ready items in inbox."""
    if not inbox_path.exists():
        return {"status": "error", "error": f"Inbox not found: {inbox_path}"}

    routed = 0
    skipped = 0
    errors = 0

    # Collect folders first (since we'll be moving them)
    folders = sorted([
        item for item in inbox_path.iterdir()
        if item.is_dir() and not item.name.startswith((".", "_"))
        and (item / "manifest.json").exists()
    ])

    for folder in folders:
        result = route_folder(folder, dry_run=dry_run)
        if result["status"] in ("routed", "dry_run"):
            routed += 1
        elif result["status"] == "skipped":
            skipped += 1
        else:
            errors += 1

    print(f"\nBatch complete: {routed} routed, {skipped} skipped, {errors} errors")
    return {"routed": routed, "skipped": skipped, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description="Route intake items to meeting or reflection destinations")
    subparsers = parser.add_subparsers(dest="command")

    route_parser = subparsers.add_parser("route", help="Route items from inbox")
    route_parser.add_argument("path", type=Path, help="Inbox item folder or inbox directory (with --batch)")
    route_parser.add_argument("--batch", action="store_true", help="Route all ready items")
    route_parser.add_argument("--dry-run", action="store_true", help="Preview without moving")
    route_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.batch:
        result = batch_route(args.path, dry_run=args.dry_run)
    else:
        result = route_folder(args.path, dry_run=args.dry_run)

    if getattr(args, "json", False):
        print(json.dumps(result, indent=2))

    if result.get("status") == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
