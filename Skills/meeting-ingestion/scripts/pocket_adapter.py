#!/usr/bin/env python3
import os
"""
Pocket Adapter (pocket_v1) — Normalizes HeyPocket webhook payloads into intake-v1 manifests.

Usage:
    python3 pocket_adapter.py --payload /path/to/payload.json [--dry-run]
    python3 pocket_adapter.py --payload /path/to/payload.json --output-dir /custom/path
    python3 pocket_adapter.py --help

The adapter:
1. Reads a Pocket webhook payload (transcription.completed event)
2. Normalizes transcript into transcript.md + transcript.jsonl
3. Classifies content type by speaker count (DP-2)
4. Creates an intake-v1 manifest in Personal/Inbox/
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ADAPTER_NAME = "pocket_v1"
ADAPTER_VERSION = "1.0.0"
DEFAULT_INBOX = Path(os.environ.get("N5OS_WORKSPACE", ".")) / "Personal/Inbox"


def classify_content_type(speaker_count: int, duration_seconds: int) -> dict:
    """Classify content type based on speaker count and duration (DP-2 rules).

    Rules:
    - 0-1 speakers → reflection (confidence: 0.9)
    - 2+ speakers AND duration > 300s → meeting (confidence: 0.85)
    - 2+ speakers AND duration <= 300s → reflection (confidence: 0.6)
    """
    if speaker_count <= 1:
        return {
            "content_type": "reflection",
            "confidence": 0.9,
            "method": "speaker_count",
            "signals": [f"{speaker_count} speaker(s) detected"],
        }
    elif duration_seconds > 300:
        return {
            "content_type": "meeting",
            "confidence": 0.85,
            "method": "speaker_count",
            "signals": [
                f"{speaker_count} distinct speakers",
                f"duration {duration_seconds}s > 300s threshold",
            ],
        }
    else:
        return {
            "content_type": "reflection",
            "confidence": 0.6,
            "method": "speaker_count",
            "signals": [
                f"{speaker_count} speakers but short duration ({duration_seconds}s <= 300s)",
                "flagged for review",
            ],
        }


def normalize_transcript_md(transcript_entries: list) -> str:
    """Convert Pocket transcript array to readable markdown."""
    lines = []
    current_speaker = None

    for entry in transcript_entries:
        speaker = entry.get("speaker", "Unknown")
        text = entry.get("text", "").strip()
        if not text:
            continue

        if speaker != current_speaker:
            if lines:
                lines.append("")
            lines.append(f"**{speaker}:**")
            current_speaker = speaker

        lines.append(text)

    return "\n".join(lines)


def normalize_transcript_jsonl(transcript_entries: list) -> str:
    """Convert Pocket transcript array to JSONL with timestamps."""
    lines = []
    for entry in transcript_entries:
        turn = {
            "speaker": entry.get("speaker", "Unknown"),
            "text": entry.get("text", "").strip(),
            "start": entry.get("start"),
            "end": entry.get("end"),
        }
        if turn["text"]:
            lines.append(json.dumps(turn))
    return "\n".join(lines)


def generate_slug(title: Optional[str], recording_id: str) -> str:
    """Generate a kebab-case slug from recording title."""
    if not title or not title.strip():
        short_id = recording_id[:8] if recording_id else "unknown"
        return f"Pocket-Recording-{short_id}"

    slug = re.sub(r"[^\w\s-]", "", title)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    if len(slug) > 50:
        slug = slug[:50].rstrip("-")
    return slug or f"Pocket-Recording-{recording_id[:8]}"


def process_payload(
    payload: dict,
    inbox_path: Path = DEFAULT_INBOX,
    dry_run: bool = False,
    json_output: bool = False,
) -> dict:
    """Process a Pocket webhook payload and create intake folder.

    Args:
        payload: Pocket webhook JSON payload
        inbox_path: Where to create the intake folder
        dry_run: Preview without writing

    Returns:
        dict with processing result
    """
    recording = payload.get("recording", {})
    transcript_entries = payload.get("transcript", [])

    if not recording:
        return {"status": "error", "error": "No recording object in payload"}
    if not transcript_entries:
        return {"status": "error", "error": "No transcript entries in payload"}

    # Extract metadata
    recording_id = recording.get("id", "unknown")
    title = recording.get("title", "")
    duration = recording.get("duration", 0)
    language = recording.get("language", "en")
    created_at = recording.get("createdAt", "")

    # Extract date
    content_date = datetime.now().strftime("%Y-%m-%d")
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            content_date = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass

    # Count unique speakers
    speakers = set()
    for entry in transcript_entries:
        speaker = entry.get("speaker", "").strip()
        if speaker:
            speakers.add(speaker)
    speaker_count = len(speakers)

    # Classify
    classification = classify_content_type(speaker_count, duration)
    classification["speaker_count"] = speaker_count
    classification["duration_seconds"] = duration

    # Generate folder name
    slug = generate_slug(title, recording_id)
    folder_name = f"{content_date}_{slug}"
    folder_path = inbox_path / folder_name

    # Word count
    all_text = " ".join(e.get("text", "") for e in transcript_entries)
    word_count = len(all_text.split())

    # Build manifest
    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "$schema": "intake-v1",
        "item_id": folder_name,
        "content_type": classification["content_type"],
        "status": "landed",
        "source": {
            "type": "pocket",
            "adapter": ADAPTER_NAME,
            "adapter_version": ADAPTER_VERSION,
            "original_filename": f"pocket_{recording_id}.json",
            "raw_id": recording_id,
            "ingested_at": now,
        },
        "classification": classification,
        "content": {
            "date": content_date,
            "title": None,
            "summary": None,
            "word_count": word_count,
            "language": language[:2].lower() if language else "en",
        },
        "zo_take_heed": {
            "scanned": False,
            "triggers_found": 0,
            "actions": [],
        },
        "timestamps": {
            "landed_at": now,
            "classified_at": None,
            "heed_scanned_at": None,
            "routed_at": None,
        },
        "provenance": {
            "conversation_id": None,
            "agent_id": None,
            "build": "unified-intake-redesign",
        },
    }

    # Normalize transcript
    transcript_md = normalize_transcript_md(transcript_entries)
    transcript_jsonl = normalize_transcript_jsonl(transcript_entries)

    if dry_run:
        if not json_output:
            print(f"[DRY RUN] Would create folder: {folder_path}")
            print(f"  Content type: {classification['content_type']} (confidence: {classification['confidence']})")
            print(f"  Speakers: {speaker_count} ({', '.join(sorted(speakers)) if speakers else 'none'})")
            print(f"  Duration: {duration}s")
            print(f"  Word count: {word_count}")
            print(f"  Files: manifest.json, transcript.md, transcript.jsonl, metadata.json")
        return {
            "status": "dry_run",
            "folder_path": str(folder_path),
            "classification": classification,
            "speaker_count": speaker_count,
        }

    # Create folder and write files
    folder_path.mkdir(parents=True, exist_ok=True)

    (folder_path / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (folder_path / "transcript.md").write_text(transcript_md)
    (folder_path / "transcript.jsonl").write_text(transcript_jsonl)
    (folder_path / "metadata.json").write_text(json.dumps(payload, indent=2))

    if not json_output:
        print(f"Created intake folder: {folder_path}")
        print(f"  Content type: {classification['content_type']} (confidence: {classification['confidence']})")
        print(f"  Speakers: {speaker_count}")
        print(f"  Word count: {word_count}")
        print(f"  Status: landed")

    return {
        "status": "completed",
        "folder_path": str(folder_path),
        "item_id": folder_name,
        "classification": classification,
        "speaker_count": speaker_count,
        "word_count": word_count,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Pocket Adapter — normalize HeyPocket payloads to intake-v1"
    )
    parser.add_argument("--payload", type=Path, required=True, help="Path to Pocket webhook payload JSON")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_INBOX, help="Output directory (default: Personal/Inbox)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    if not args.payload.exists():
        print(f"Error: Payload file not found: {args.payload}", file=sys.stderr)
        return 2

    try:
        payload = json.loads(args.payload.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in payload: {e}", file=sys.stderr)
        return 2

    result = process_payload(
        payload,
        inbox_path=args.output_dir,
        dry_run=args.dry_run,
        json_output=args.json,
    )

    if result["status"] == "error":
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
