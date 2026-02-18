#!/usr/bin/env python3
"""
Normalize Inbox Folders

Brings all meeting folders to a consistent baseline:
1. Deletes failed recordings (waiting room timeouts, junk/test data)
2. Converts transcript.jsonl → transcript.md where .md is missing
3. Normalizes all manifests to clean v3 format
4. Removes backup files and stale artifacts

Usage:
    python3 normalize_inbox.py --dry-run     # Preview changes
    python3 normalize_inbox.py --execute     # Apply changes
"""

import json
import shutil
import argparse
from datetime import datetime, timezone
from pathlib import Path

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

# Folders to delete entirely — failed recordings (bot never admitted, 15min timeout)
DELETE_FAILED_RECORDINGS = [
    "2026-02-12_sov-zres-jhw-224241",
    "2026-02-12_wes-wpoh-fvx-214501",
    "2026-02-13_bab-ztpg-sat-161500",
    "2026-02-13_hin-oxzc-rrc-124503",
    "2026-02-13_mwf-fgzg-meu-212831",
    "2026-02-13_uvj-zjia-ykj-140003",
    "2026-02-13_vry-exuj-pkk-171501",
]

# Folders to delete — junk/test data
DELETE_JUNK = [
    "2026-02-12_ryu-bdvz-mea",          # 2-word "transcript" from dead call
    "2026-02-09_Unknownperson_Vrijenattawar",  # Fake test data for HITL queue
]

# Files to remove from every folder (stale artifacts, backups)
CLEANUP_FILES = [
    "manifest_v2_backup.json",
    "transcript.json",      # null files from failed Recall downloads
    "participants.json",    # redundant — participant data lives in manifest
]


def jsonl_to_markdown(jsonl_path: Path) -> str:
    """Convert a Recall transcript.jsonl to readable markdown."""
    lines = jsonl_path.read_text().strip().split("\n")

    md_parts = []
    current_speaker = None
    current_text_parts = []

    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        speaker = entry.get("speaker", "Unknown")
        text = entry.get("text", "").strip()

        if not text:
            continue

        if speaker != current_speaker:
            # Flush previous speaker's text
            if current_speaker is not None and current_text_parts:
                md_parts.append(f"**{current_speaker}:** {' '.join(current_text_parts)}\n")
            current_speaker = speaker
            current_text_parts = [text]
        else:
            current_text_parts.append(text)

    # Flush last speaker
    if current_speaker is not None and current_text_parts:
        md_parts.append(f"**{current_speaker}:** {' '.join(current_text_parts)}\n")

    return "\n".join(md_parts)


def build_clean_manifest(folder: Path, existing_manifest: dict) -> dict:
    """Build a clean v3 manifest from existing data + folder contents."""
    now_iso = datetime.now(timezone.utc).isoformat()
    folder_name = folder.name

    # Extract date from folder name (first 10 chars should be YYYY-MM-DD)
    meeting_date = folder_name[:10] if len(folder_name) >= 10 and folder_name[4] == "-" else "unknown"

    # Preserve existing data where available
    meeting_id = existing_manifest.get("meeting_id", folder_name)

    # Get meeting title — try multiple sources
    title = None
    meeting_block = existing_manifest.get("meeting", {})
    if isinstance(meeting_block, dict):
        title = meeting_block.get("title")
    if not title:
        title = existing_manifest.get("title")
    if not title:
        # Derive from folder name
        name_part = folder_name[11:] if len(folder_name) > 11 else folder_name
        title = name_part.replace("-", " ").replace("_", " ").title()

    # Get meeting type
    meeting_type = "external"
    if isinstance(meeting_block, dict):
        meeting_type = meeting_block.get("type", "external")
    elif "meeting_type" in existing_manifest:
        meeting_type = existing_manifest["meeting_type"]

    # Get time_utc and duration from existing manifest
    time_utc = meeting_block.get("time_utc") if isinstance(meeting_block, dict) else None
    duration_minutes = meeting_block.get("duration_minutes") if isinstance(meeting_block, dict) else None

    # Get participants
    participants_block = existing_manifest.get("participants", {})
    if isinstance(participants_block, dict):
        v3_participants = participants_block.get("identified", [])
        confidence = participants_block.get("confidence", 0.5)
    elif isinstance(participants_block, list):
        # Legacy format
        v3_participants = []
        for p in participants_block:
            if isinstance(p, str):
                v3_participants.append({
                    "name": p, "email": None, "crm_id": None,
                    "role": "attendee", "confidence": 0.5,
                })
            elif isinstance(p, dict):
                v3_participants.append({
                    "name": p.get("name", "Unknown"),
                    "email": p.get("email"),
                    "crm_id": p.get("crm_id"),
                    "role": p.get("role", "attendee"),
                    "confidence": p.get("confidence", 0.5),
                })
        confidence = 0.5 if v3_participants else 0.0
    else:
        v3_participants = []
        confidence = 0.0

    # Try to enrich from metadata.json if available
    metadata_path = folder / "metadata.json"
    if metadata_path.exists():
        try:
            meta = json.loads(metadata_path.read_text())
            if not title or title == folder_name:
                meta_title = meta.get("title")
                if meta_title:
                    title = meta_title
            if not time_utc:
                meta_time = meta.get("start_time")
                if meta_time:
                    try:
                        dt = datetime.fromisoformat(meta_time.replace("Z", "+00:00"))
                        time_utc = dt.strftime("%H:%M:%S")
                    except ValueError:
                        pass
            if not v3_participants:
                meta_participants = meta.get("participants", [])
                for p in meta_participants:
                    if isinstance(p, dict):
                        v3_participants.append({
                            "name": p.get("name", "Unknown"),
                            "email": p.get("email"),
                            "crm_id": None,
                            "role": "attendee",
                            "confidence": 0.7,
                        })
                    elif isinstance(p, str):
                        v3_participants.append({
                            "name": p, "email": None, "crm_id": None,
                            "role": "attendee", "confidence": 0.5,
                        })
                confidence = 0.7 if v3_participants else 0.0
        except (json.JSONDecodeError, OSError):
            pass

    # Determine source type
    source_type = "direct_drop"
    recall_bot_id = None
    recall_meta = existing_manifest.get("recall_metadata", {})
    source_block = existing_manifest.get("source", {})

    if isinstance(recall_meta, dict) and recall_meta.get("bot_id"):
        source_type = "recall_ai"
        recall_bot_id = recall_meta["bot_id"]
    elif isinstance(source_block, dict) and source_block.get("type") == "recall_ai":
        source_type = "recall_ai"
        recall_bot_id = source_block.get("recall_bot_id")
    elif (folder / "metadata.json").exists() and (folder / "transcript.jsonl").exists():
        source_type = "recall_ingest"  # Came through Recall but was ingested, not deposited

    # Get timestamps
    ts_block = existing_manifest.get("timestamps", {})
    created_at = ts_block.get("created_at") if isinstance(ts_block, dict) else None
    ingested_at = ts_block.get("ingested_at") if isinstance(ts_block, dict) else None
    if not created_at:
        created_at = existing_manifest.get("staged_at", now_iso)
    if not ingested_at:
        ingested_at = now_iso

    # Catalog actual artifacts present in folder
    artifacts = {}
    for f in folder.iterdir():
        if f.name == "manifest.json" or f.name.startswith("."):
            continue
        artifacts[f.name] = f.name

    manifest = {
        "$schema": "manifest-v3",
        "schema_version": "v3",
        "meeting_id": meeting_id,
        "status": "ingested",
        "status_history": [
            {"status": "ingested", "at": ingested_at},
            {"status": "normalized", "at": now_iso, "note": "normalized by normalize_inbox.py"},
        ],
        "source": {
            "type": source_type,
            "ingested_at": ingested_at,
        },
        "meeting": {
            "date": meeting_date,
            "time_utc": time_utc,
            "duration_minutes": duration_minutes,
            "title": title,
            "type": meeting_type,
            "summary": meeting_block.get("summary") if isinstance(meeting_block, dict) else None,
        },
        "participants": {
            "identified": v3_participants,
            "unidentified": [],
            "confidence": confidence,
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
            "requested": [],
            "generated": [],
            "failed": [],
            "skipped": [],
        },
        "hitl": {
            "queue_id": None,
            "reason": None,
            "resolved_at": None,
        },
        "timestamps": {
            "created_at": created_at,
            "ingested_at": ingested_at,
            "identified_at": None,
            "gated_at": None,
            "processed_at": None,
            "archived_at": None,
        },
        "artifacts": artifacts,
    }

    # Add recall-specific metadata if applicable
    if source_type == "recall_ai" and recall_bot_id:
        manifest["source"]["recall_bot_id"] = recall_bot_id
        manifest["recall_metadata"] = recall_meta if isinstance(recall_meta, dict) else {"bot_id": recall_bot_id}

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Normalize Inbox folders to consistent baseline")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview changes")
    group.add_argument("--execute", action="store_true", help="Apply changes")
    args = parser.parse_args()
    dry_run = not args.execute

    print(f"{'[DRY RUN] ' if dry_run else ''}Normalizing Inbox folders")
    print("=" * 60)

    # --- Step 1: Delete failed recordings ---
    print("\n--- Step 1: Delete failed recordings (waiting room timeouts) ---")
    deleted = 0
    for name in DELETE_FAILED_RECORDINGS:
        path = INBOX / name
        if path.exists():
            if dry_run:
                print(f"  WOULD DELETE {name} (bot never admitted)")
            else:
                shutil.rmtree(path)
                print(f"  DELETED {name}")
            deleted += 1
        else:
            print(f"  SKIP {name} (not found)")
    print(f"  Failed recordings: {deleted}")

    # --- Step 2: Delete junk/test folders ---
    print("\n--- Step 2: Delete junk/test folders ---")
    junk_deleted = 0
    for name in DELETE_JUNK:
        path = INBOX / name
        if path.exists():
            if dry_run:
                print(f"  WOULD DELETE {name}")
            else:
                shutil.rmtree(path)
                print(f"  DELETED {name}")
            junk_deleted += 1
        else:
            print(f"  SKIP {name} (not found)")
    print(f"  Junk folders: {junk_deleted}")

    # --- Step 3: Convert jsonl → md where needed ---
    print("\n--- Step 3: Convert transcript.jsonl → transcript.md where missing ---")
    converted = 0
    for folder in sorted(INBOX.iterdir()):
        if not folder.is_dir() or folder.name.startswith((".", "_")):
            continue

        has_md = (folder / "transcript.md").exists()
        has_jsonl = (folder / "transcript.jsonl").exists()

        if has_jsonl and not has_md:
            if dry_run:
                # Count lines to show size
                lines = (folder / "transcript.jsonl").read_text().strip().split("\n")
                print(f"  WOULD CONVERT {folder.name}/transcript.jsonl ({len(lines)} lines → .md)")
            else:
                md_content = jsonl_to_markdown(folder / "transcript.jsonl")
                (folder / "transcript.md").write_text(md_content)
                print(f"  CONVERTED {folder.name}/transcript.jsonl → transcript.md ({len(md_content)} bytes)")
            converted += 1
    print(f"  Conversions: {converted}")

    # --- Step 4: Clean up stale files ---
    print("\n--- Step 4: Clean up stale artifacts ---")
    cleaned = 0
    for folder in sorted(INBOX.iterdir()):
        if not folder.is_dir() or folder.name.startswith((".", "_")):
            continue

        for filename in CLEANUP_FILES:
            filepath = folder / filename
            if filepath.exists():
                # For transcript.json, only delete if it's the null/empty one
                if filename == "transcript.json":
                    size = filepath.stat().st_size
                    if size > 10:  # Has real content
                        continue

                if dry_run:
                    print(f"  WOULD DELETE {folder.name}/{filename}")
                else:
                    filepath.unlink()
                    print(f"  DELETED {folder.name}/{filename}")
                cleaned += 1
    print(f"  Files cleaned: {cleaned}")

    # --- Step 5: Normalize all manifests ---
    print("\n--- Step 5: Normalize manifests ---")
    normalized = 0
    for folder in sorted(INBOX.iterdir()):
        if not folder.is_dir() or folder.name.startswith((".", "_")):
            continue

        manifest_path = folder / "manifest.json"

        # Read existing manifest
        existing = {}
        if manifest_path.exists():
            try:
                existing = json.loads(manifest_path.read_text())
            except json.JSONDecodeError:
                pass

        # Build clean manifest
        clean_manifest = build_clean_manifest(folder, existing)

        if dry_run:
            # Check what has transcript
            has_transcript = (folder / "transcript.md").exists()
            print(f"  WOULD NORMALIZE {folder.name} (transcript.md: {'YES' if has_transcript else 'NO'})")
        else:
            manifest_path.write_text(json.dumps(clean_manifest, indent=2))
            has_transcript = (folder / "transcript.md").exists()
            print(f"  NORMALIZED {folder.name} (transcript.md: {'YES' if has_transcript else 'NO'})")
        normalized += 1

    # --- Summary ---
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Deleted (failed):     {deleted}")
    print(f"  Deleted (junk):       {junk_deleted}")
    print(f"  Converted jsonl→md:   {converted}")
    print(f"  Files cleaned:        {cleaned}")
    print(f"  Manifests normalized: {normalized}")

    # Final folder count
    remaining = [
        f for f in sorted(INBOX.iterdir())
        if f.is_dir() and not f.name.startswith((".", "_"))
    ]
    print(f"\n  Remaining folders: {len(remaining)}")

    # Check transcript coverage
    missing_transcript = []
    for f in remaining:
        if not (f / "transcript.md").exists():
            missing_transcript.append(f.name)

    if missing_transcript:
        print(f"  ⚠️  Folders WITHOUT transcript.md: {len(missing_transcript)}")
        for name in missing_transcript:
            print(f"     - {name}")
    else:
        print(f"  ✓ All {len(remaining)} folders have transcript.md")


if __name__ == "__main__":
    main()
