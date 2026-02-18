#!/usr/bin/env python3
"""
Title Normalizer — Transcript-based title + speaker extraction

Reads the first ~2000 chars of a meeting transcript to:
1. Extract all speaker names
2. Generate a descriptive meeting title
3. Update the manifest with improved metadata
4. Optionally rename the folder to match

Usage:
    python3 title_normalizer.py <meeting_folder> [--dry-run] [--rename]
"""

import json
import os
import re
import logging
import requests
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ZO_API_URL = "https://api.zo.computer/zo/ask"


def slugify(text: str) -> str:
    """Convert text to folder-safe slug."""
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def call_zo_ask(prompt: str) -> str:
    """Call /zo/ask API."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")

    response = requests.post(
        ZO_API_URL,
        headers={"authorization": token, "content-type": "application/json"},
        json={"input": prompt},
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Zo API error: {response.status_code}")

    return response.json().get("output", "").strip()


def extract_speakers_from_transcript(transcript_text: str) -> List[str]:
    """Extract speaker names from transcript using regex patterns.

    Handles common formats:
    - **Speaker Name:** text
    - Speaker Name: text (at line start)
    - **Speaker Name [00:00:00]:** text
    """
    speakers = set()

    patterns = [
        r'^\*\*([A-Z][a-zA-Z\s\'-]+?)(?:\s*\[[\d:]+\])?\*\*\s*:',  # **Name [time]:**
        r'^\*\*([A-Z][a-zA-Z\s\'-]+?)\*\*\s*:',                       # **Name:**
        r'^([A-Z][a-zA-Z\s\'-]+?):\s',                                 # Name: (line start)
    ]

    for line in transcript_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                name = match.group(1).strip()
                # Filter out non-name patterns
                if (len(name) > 1
                    and len(name) < 50
                    and not name.lower().startswith(('unknown', 'speaker', 'transcript', 'summary', 'note'))
                    and not re.match(r'^\d', name)):
                    speakers.add(name)
                break

    return sorted(speakers)


def normalize_title(meeting_path: Path, dry_run: bool = False, rename: bool = False) -> Dict:
    """
    Normalize meeting title using transcript content.

    Reads transcript preview + manifest to generate improved title and extract speakers.

    Returns:
        {
            "original_title": str,
            "new_title": str,
            "speakers": list[str],
            "folder_renamed": bool,
            "new_folder_name": str | None,
        }
    """
    manifest_path = meeting_path / "manifest.json"
    if not manifest_path.exists():
        return {"error": "no manifest.json"}

    manifest = json.loads(manifest_path.read_text())

    # Find transcript
    transcript_path = None
    for fname in ["transcript.md", "transcript.txt"]:
        candidate = meeting_path / fname
        if candidate.exists():
            transcript_path = candidate
            break

    if not transcript_path:
        return {"error": "no transcript found"}

    transcript_text = transcript_path.read_text()
    if len(transcript_text) < 100:
        return {"error": "transcript too short"}

    # Get existing title
    meeting_block = manifest.get("meeting", {})
    original_title = meeting_block.get("title", meeting_path.name)

    # Step 1: Extract speakers from transcript (regex — fast, no LLM)
    speakers = extract_speakers_from_transcript(transcript_text[:5000])
    logger.info(f"  Extracted speakers: {speakers}")

    # Step 2: Generate improved title via LLM
    preview = transcript_text[:2000]
    participant_hint = ", ".join(speakers) if speakers else "unknown"

    prompt = f"""Analyze this meeting transcript excerpt and generate a better meeting title.

Current title: "{original_title}"
Speakers detected: {participant_hint}

Transcript excerpt:
---
{preview}
---

Generate a meeting title that:
- Is 3-8 words long
- Describes the main topic or purpose of the meeting
- Does NOT use generic words like "Meeting", "Call", "Discussion" by themselves
- Does NOT repeat participant names (those are tracked separately)
- Uses title case
- Examples of good titles: "Stanford Omics Lab Partnership", "Q1 Product Roadmap Review", "Careerspan Demo Walkthrough", "Investor Update Serum Institute"

If the current title already seems descriptive and specific (not generic like "Impromptu Zoom Meeting"), keep it.

Respond with ONLY the title text, nothing else. No quotes, no explanation."""

    try:
        new_title = call_zo_ask(prompt)
        # Clean up response
        new_title = new_title.strip().strip('"').strip("'").strip()
        # Validate — must be reasonable length
        if len(new_title) < 3 or len(new_title) > 100:
            new_title = original_title
    except Exception as e:
        logger.warning(f"  LLM title generation failed: {e}, keeping original")
        new_title = original_title

    logger.info(f"  Title: '{original_title}' → '{new_title}'")

    # Step 3: Merge speakers into manifest participants
    existing_participants = manifest.get("participants", {})
    if isinstance(existing_participants, dict):
        identified = existing_participants.get("identified", [])
    else:
        identified = []

    existing_names = {p.get("name", "").lower() for p in identified if isinstance(p, dict)}

    new_participants = []
    for speaker in speakers:
        if speaker.lower() not in existing_names:
            new_participants.append({
                "name": speaker,
                "email": None,
                "crm_id": None,
                "role": "attendee",
                "confidence": 0.9,  # High confidence — extracted from transcript text
            })

    # Step 4: Determine new folder name
    folder_name = meeting_path.name
    date_prefix = folder_name[:10] if len(folder_name) >= 10 and folder_name[4] == "-" else ""
    new_folder_name = None

    if rename and new_title != original_title and date_prefix:
        title_slug = slugify(new_title)
        speaker_slug = "-".join(slugify(s) for s in speakers[:2]) if speakers else ""
        if speaker_slug:
            new_folder_name = f"{date_prefix}_{speaker_slug}_{title_slug}"
        else:
            new_folder_name = f"{date_prefix}_{title_slug}"
        # Truncate if too long
        if len(new_folder_name) > 80:
            new_folder_name = new_folder_name[:80].rstrip("-")

    result = {
        "original_title": original_title,
        "new_title": new_title,
        "speakers": speakers,
        "new_participants": len(new_participants),
        "folder_renamed": False,
        "new_folder_name": new_folder_name,
    }

    if dry_run:
        result["dry_run"] = True
        return result

    # Step 5: Update manifest
    manifest.setdefault("meeting", {})["title"] = new_title
    manifest["meeting"]["original_title"] = original_title

    # Merge new participants
    if new_participants:
        if isinstance(manifest.get("participants"), dict):
            manifest["participants"]["identified"].extend(new_participants)
            # Recalculate confidence
            all_identified = manifest["participants"]["identified"]
            if all_identified:
                avg_conf = sum(p.get("confidence", 0.5) for p in all_identified) / len(all_identified)
                manifest["participants"]["confidence"] = round(avg_conf, 2)
        else:
            manifest["participants"] = {
                "identified": new_participants,
                "unidentified": [],
                "confidence": 0.9,
            }

    # Add normalization record to status_history
    history = manifest.get("status_history", [])
    history.append({
        "status": "title_normalized",
        "at": datetime.now(timezone.utc).isoformat(),
        "note": f"'{original_title}' → '{new_title}', {len(speakers)} speakers extracted",
    })
    manifest["status_history"] = history

    manifest_path.write_text(json.dumps(manifest, indent=2))
    logger.info(f"  Manifest updated")

    # Step 6: Rename folder if requested
    if rename and new_folder_name and new_folder_name != folder_name:
        new_path = meeting_path.parent / new_folder_name
        if not new_path.exists():
            shutil.move(str(meeting_path), str(new_path))
            # Update meeting_id in manifest
            new_manifest_path = new_path / "manifest.json"
            m = json.loads(new_manifest_path.read_text())
            m["meeting_id"] = new_folder_name
            new_manifest_path.write_text(json.dumps(m, indent=2))
            result["folder_renamed"] = True
            logger.info(f"  Folder renamed: {folder_name} → {new_folder_name}")
        else:
            logger.warning(f"  Cannot rename: {new_folder_name} already exists")

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Normalize meeting titles using transcript content")
    parser.add_argument("meeting", help="Meeting folder path")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--rename", action="store_true", help="Also rename folder")

    args = parser.parse_args()
    meeting_path = Path(args.meeting)

    if not meeting_path.is_dir():
        print(f"Error: {meeting_path} is not a directory")
        return 1

    result = normalize_title(meeting_path, dry_run=args.dry_run, rename=args.rename)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
