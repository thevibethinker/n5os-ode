#!/usr/bin/env python3
"""
Backfill Inbox to v3 Manifests

One-shot script to convert existing v2/legacy meeting manifests in the Inbox
to v3 format so they can flow through the v3 pipeline.

Usage:
    python3 backfill_inbox.py --dry-run     # Preview changes
    python3 backfill_inbox.py --execute     # Apply changes
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

# Add scripts dir for ingest module
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def convert_manifest_to_v3(manifest: dict, folder_name: str) -> dict:
    """Convert a v2/legacy manifest to v3 format, preserving existing data."""
    now_iso = datetime.now(timezone.utc).isoformat()

    # Preserve existing data
    meeting_id = manifest.get("meeting_id", folder_name)
    meeting_date = manifest.get("date", folder_name[:10] if len(folder_name) >= 10 else "unknown")
    meeting_type = manifest.get("meeting_type", "external")
    transcript_file = manifest.get("transcript_file")
    staged_at = manifest.get("staged_at", now_iso)

    # Convert participant list from legacy format (list of strings) to v3 format
    raw_participants = manifest.get("participants", [])
    v3_participants = []
    for p in raw_participants:
        if isinstance(p, str):
            v3_participants.append({
                "name": p,
                "email": None,
                "crm_id": None,
                "role": "attendee",
                "confidence": 0.5,
            })
        elif isinstance(p, dict):
            v3_participants.append({
                "name": p.get("name", "Unknown"),
                "email": p.get("email"),
                "crm_id": p.get("crm_id"),
                "role": p.get("role", "attendee"),
                "confidence": p.get("confidence", 0.5),
            })

    # Extract title from meeting_id slug
    title_part = meeting_id[11:] if len(meeting_id) > 11 else meeting_id
    title = title_part.replace("-", " ").title()

    # Determine source type
    source_type = "legacy_migration"
    recall_bot_id = manifest.get("recall_bot_id")
    if recall_bot_id:
        source_type = "recall_ai"

    v3_manifest = {
        "$schema": "manifest-v3",
        "schema_version": "v3",
        "meeting_id": meeting_id,
        "status": "ingested",
        "status_history": [
            {"status": "raw", "at": staged_at},
            {"status": "staged", "at": staged_at},
            {"status": "ingested", "at": now_iso, "note": "backfilled from v2"},
        ],
        "source": {
            "type": source_type,
            "original_filename": transcript_file,
            "ingested_at": now_iso,
        },
        "meeting": {
            "date": meeting_date,
            "time_utc": None,
            "duration_minutes": None,
            "title": title,
            "type": meeting_type,
            "summary": None,
        },
        "participants": {
            "identified": v3_participants,
            "unidentified": [],
            "confidence": 0.5 if v3_participants else 0.0,
        },
        "calendar_match": {
            "event_id": None,
            "confidence": 0.0,
            "method": "none",
        },
        "quality_gate": {
            "passed": False,
            "checks": {},
            "score": 0.0,
        },
        "blocks": {
            "policy": "internal_standard" if meeting_type == "internal" else "external_standard",
            "requested": manifest.get("blocks_requested", []),
            "generated": manifest.get("blocks_generated", []),
            "failed": manifest.get("blocks_failed", []),
            "skipped": [],
        },
        "hitl": {
            "queue_id": None,
            "reason": None,
            "resolved_at": None,
        },
        "timestamps": {
            "created_at": staged_at,
            "ingested_at": now_iso,
            "identified_at": None,
            "gated_at": None,
            "processed_at": manifest.get("processed_at"),
            "archived_at": manifest.get("archived_at"),
        },
    }

    # Preserve recall-specific data if present
    if recall_bot_id:
        v3_manifest["recall_metadata"] = {
            "bot_id": recall_bot_id,
            "recording_duration_seconds": manifest.get("recording_duration_seconds"),
            "video_retention_days": manifest.get("video_retention_days"),
            "video_expires_at": manifest.get("video_expires_at"),
            "participant_count": manifest.get("participant_count"),
        }
        v3_manifest["source"]["recall_bot_id"] = recall_bot_id

    # Preserve artifacts if present
    if "artifacts" in manifest:
        v3_manifest["artifacts"] = manifest["artifacts"]

    return v3_manifest


def backfill_folders(dry_run: bool = True):
    """Convert all v2/legacy manifests in Inbox folders to v3."""
    if not INBOX.exists():
        print(f"Inbox not found: {INBOX}")
        return

    converted = 0
    skipped = 0
    errors = 0

    for item in sorted(INBOX.iterdir()):
        if not item.is_dir() or item.name.startswith((".", "_")):
            continue

        manifest_path = item / "manifest.json"
        if not manifest_path.exists():
            print(f"  SKIP {item.name} — no manifest.json")
            skipped += 1
            continue

        try:
            manifest = json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ERROR {item.name} — cannot read manifest: {e}")
            errors += 1
            continue

        # Check if already v3
        schema = manifest.get("$schema", "")
        schema_version = manifest.get("schema_version", "")
        if schema == "manifest-v3" or schema_version == "v3":
            print(f"  SKIP {item.name} — already v3")
            skipped += 1
            continue

        # Convert
        v3_manifest = convert_manifest_to_v3(manifest, item.name)

        if dry_run:
            print(f"  WOULD CONVERT {item.name} (status: {manifest.get('status', '?')} → ingested)")
        else:
            # Backup original
            backup_path = item / "manifest_v2_backup.json"
            backup_path.write_text(json.dumps(manifest, indent=2))

            # Write v3 manifest
            manifest_path.write_text(json.dumps(v3_manifest, indent=2))
            print(f"  CONVERTED {item.name} (status: {manifest.get('status', '?')} → ingested)")

        converted += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Converted: {converted}")
    print(f"  Skipped:   {skipped}")
    print(f"  Errors:    {errors}")


def backfill_raw_files(dry_run: bool = True):
    """Ingest raw transcript files sitting in Inbox root."""
    if not INBOX.exists():
        return

    raw_files = [
        f for f in sorted(INBOX.iterdir())
        if f.is_file() and f.suffix in [".md", ".txt", ".jsonl"] and not f.name.startswith(".")
    ]

    if not raw_files:
        print("\nNo raw transcript files found in Inbox root")
        return

    print(f"\nFound {len(raw_files)} raw transcript file(s):")

    from ingest import TranscriptIngestor
    ingestor = TranscriptIngestor()

    ingested = 0
    for raw_file in raw_files:
        if dry_run:
            print(f"  WOULD INGEST {raw_file.name}")
            ingested += 1
        else:
            try:
                result = ingestor.ingest_file(str(raw_file), dry_run=False)
                status = result.get("status", "unknown")
                folder = result.get("meeting_folder", "unknown")
                print(f"  INGESTED {raw_file.name} → {folder} ({status})")
                ingested += 1
            except Exception as e:
                print(f"  ERROR {raw_file.name}: {e}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Raw files processed: {ingested}")


def main():
    parser = argparse.ArgumentParser(description="Backfill Inbox meetings to v3 manifest format")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    group.add_argument("--execute", action="store_true", help="Apply changes")
    args = parser.parse_args()

    dry_run = not args.execute

    print(f"{'[DRY RUN] ' if dry_run else ''}Backfilling Inbox to v3 manifests")
    print("=" * 50)

    print("\n--- Converting existing meeting folders ---")
    backfill_folders(dry_run=dry_run)

    print("\n--- Ingesting raw transcript files ---")
    backfill_raw_files(dry_run=dry_run)


if __name__ == "__main__":
    main()
