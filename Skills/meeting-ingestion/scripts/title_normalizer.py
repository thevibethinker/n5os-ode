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
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from identity import canonical_short_name, is_v

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ZO_API_URL = "https://api.zo.computer/zo/ask"


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


GENERIC_SPEAKER_LABELS = {
    'me', 'them', 'you', 'us', 'they', 'he', 'she', 'it', 'we',
    'date', 'participants', 'participant', 'host', 'guest',
    'unknown', 'speaker', 'transcript', 'summary', 'note',
    'title', 'meeting', 'agenda', 'description', 'duration',
}


GENERIC_TITLE_PATTERNS = [
    r'^Impromptu\s+(Google\s+Meet|Zoom)\s+Meeting$',
    r'^Meeting\s+with\s+.+$',
    r'^(Google\s+Meet|Zoom)\s+(Meeting|Call)$',
    r'^Untitled\s+Meeting$',
    r'^New\s+Meeting$',
    r'^\d{4}-\d{2}-\d{2}\s+Meeting$',
]


def is_generic_title(title: str) -> bool:
    """Check if a title is auto-generated / generic and should be renamed.
    
    Handles both display titles ('Impromptu Google Meet Meeting') and
    folder-name formats ('2025-12-15_Impromptu-Google-Meet-Meeting').
    """
    normalized = title.strip()
    normalized = re.sub(r'^\d{4}-\d{2}-\d{2}[_\s]', '', normalized)
    normalized = normalized.replace('-', ' ')
    
    for pattern in GENERIC_TITLE_PATTERNS:
        if re.match(pattern, normalized, re.IGNORECASE):
            return True
    return False


def generate_folder_slug(date_str: str, speakers: List[str], new_title: str) -> str:
    """Build a canonical folder name: YYYY-MM-DD_Descriptive-Slug.

    Prioritizes speakers + topic. Falls back to title slug if no speakers.
    """
    import unicodedata

    def slugify(text: str) -> str:
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        text = re.sub(r"[^\w\s-]", "", text).strip()
        return re.sub(r"[\s_]+", "-", text)

    other_speakers = [s for s in speakers if not is_v(s)]

    if other_speakers:
        names_part = "-x-".join(slugify(n) for n in other_speakers[:2])
        if any(is_v(s) for s in speakers):
            names_part += f"-x-{slugify(canonical_short_name())}"
        title_slug = slugify(new_title)
        slug = f"{names_part}-{title_slug}" if title_slug else names_part
    else:
        slug = slugify(new_title) or "Meeting"

    slug = slug[:80]
    return f"{date_str}_{slug}"


def extract_speakers_from_transcript(transcript_text: str) -> List[str]:
    """Extract speaker names from transcript using regex patterns.

    Handles common formats:
    - **Speaker Name:** text
    - Speaker Name: text (at line start)
    - **Speaker Name [00:00:00]:** text

    Filters out generic labels (Me, Them, Date, etc.) that are not real names.
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
                # Filter out non-name patterns and generic labels
                if (len(name) > 1
                    and len(name) < 50
                    and name.lower() not in GENERIC_SPEAKER_LABELS
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
- Examples of good titles: "Stanford Omics Lab Partnership", "Q1 Product Roadmap Review", "Customer Demo Walkthrough", "Investor Update Serum Institute"

IMPORTANT: If the current title already names specific people, companies, or topics (not generic like "Impromptu Zoom Meeting" or "Impromptu Google Meet Meeting"), KEEP the current title exactly as-is. Only replace titles that are clearly generic or auto-generated.

Respond with ONLY the title text, nothing else. No quotes, no explanation."""

    try:
        new_title = call_zo_ask(prompt)
        # Clean up response
        new_title = new_title.strip().strip('"').strip("'").strip()
        new_title = re.sub(r"\s*\*?(?:\d{4}-\d{2}-\d{2}|[A-Z][a-z]{2,8}\s+\d{1,2})(?:\s+\d{1,2}:\d{2}\s*(?:AM|PM))?\s+ET\*?\s*$", "", new_title)
        new_title = re.sub(r"\*+$", "", new_title).strip()
        new_title = ' '.join(new_title.split())
        # Validate — must be reasonable length
        if len(new_title) < 3 or len(new_title) > 100:
            new_title = original_title
    except Exception as e:
        logger.warning(f"  LLM title generation failed: {e}, keeping original")
        new_title = original_title

    # D-post: compose `<Names> — <Topic>` delineation so titles show who + what clearly
    try:
        existing_participants = manifest.get("participants", {})
        if isinstance(existing_participants, dict):
            identified_raw = existing_participants.get("identified", []) or []
        else:
            identified_raw = []
        # Prefer structured manifest names first, then any speakers detected from transcript
        existing_names_ordered = []
        seen_lower = set()
        for p in identified_raw:
            if isinstance(p, dict):
                nm = (p.get("name") or "").strip()
                if nm and nm.lower() not in seen_lower:
                    existing_names_ordered.append(nm)
                    seen_lower.add(nm.lower())
        for sp in speakers:
            if sp and sp.lower() not in seen_lower and sp.lower() not in GENERIC_SPEAKER_LABELS:
                existing_names_ordered.append(sp)
                seen_lower.add(sp.lower())

        external_names = [n for n in existing_names_ordered if not is_v(n)]
        has_v = any(is_v(n) for n in existing_names_ordered)
        # Collapse each external name to its first token (for compactness) unless it's already short
        def _short(n: str) -> str:
            n = n.strip()
            # Drop bracketed honorifics / email fragments
            n = re.sub(r"\s*\(.*?\)\s*", "", n)
            n = re.sub(r"\s+phd\b", "", n, flags=re.IGNORECASE)
            tokens = [t for t in re.split(r"\s+", n) if t]
            if not tokens:
                return n
            if len(tokens) <= 2 and all(len(t) <= 12 for t in tokens):
                return " ".join(tokens)
            return tokens[0]

        short_external = [_short(n) for n in external_names if _short(n)]
        short_external = [n for n in short_external if n]
        # Dedup after shortening
        seen2 = set()
        short_external_dedup = []
        for n in short_external:
            if n.lower() not in seen2:
                short_external_dedup.append(n)
                seen2.add(n.lower())

        topic = new_title.strip()
        # If the LLM accidentally produced a names-heavy string that matches the original, try to strip common name tokens
        topic_l = topic.lower()
        for nm in short_external_dedup + ([canonical_short_name()] if has_v else []):
            # Strip leading / trailing "x Name" or "Name x"
            topic = re.sub(rf"(?i)\b{re.escape(nm)}\b(\s*[x×]\s*)?", " ", topic)
        topic = re.sub(r"\s+", " ", topic).strip(" -—:")
        if len(topic) < 3:
            topic = new_title.strip()  # fallback — don't over-strip

        if short_external_dedup:
            name_part = " x ".join(short_external_dedup + ([canonical_short_name()] if has_v else []))
            composed = f"{name_part} — {topic}" if topic else name_part
        else:
            composed = topic or new_title

        # Guardrail on composed length
        if 3 <= len(composed) <= 120:
            new_title = composed
    except Exception as e:
        logger.warning(f"  Title delineation synthesis failed (non-fatal): {e}")

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
        if (speaker.lower() not in existing_names
                and speaker.lower() not in GENERIC_SPEAKER_LABELS):
            new_participants.append({
                "name": speaker,
                "email": None,
                "crm_id": None,
                "role": "attendee",
                "confidence": 0.9,  # High confidence — extracted from transcript text
            })

    # Step 4: Folder rename — only for generic auto-generated titles
    import shutil
    folder_name = meeting_path.name
    new_folder_name = folder_name
    folder_renamed = False
    rename_skipped = None

    date_prefix = folder_name[:10] if re.match(r'^\d{4}-\d{2}-\d{2}', folder_name) else None

    if rename and is_generic_title(original_title) and date_prefix:
        new_folder_name = generate_folder_slug(date_prefix, speakers, new_title)
        if new_folder_name != folder_name:
            new_path = meeting_path.parent / new_folder_name
            if not new_path.exists():
                if not dry_run:
                    shutil.move(str(meeting_path), str(new_path))
                    meeting_path = new_path
                    manifest_path = new_path / "manifest.json"
                    folder_renamed = True
                    logger.info(f"  Renamed: {folder_name} → {new_folder_name}")
                else:
                    logger.info(f"  [DRY RUN] Would rename: {folder_name} → {new_folder_name}")
            else:
                rename_skipped = f"target_exists:{new_folder_name}"
        else:
            rename_skipped = "slug_unchanged"
    elif rename and not is_generic_title(original_title):
        rename_skipped = "title_not_generic"
    elif rename and not date_prefix:
        rename_skipped = "no_date_prefix"

    result = {
        "original_title": original_title,
        "new_title": new_title,
        "speakers": speakers,
        "new_participants": len(new_participants),
        "folder_renamed": folder_renamed,
        "new_folder_name": new_folder_name,
        "locked_name": folder_name if not folder_renamed else None,
        "rename_skipped": rename_skipped,
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

    # Update meeting_id if folder was renamed
    if folder_renamed:
        manifest["meeting_id"] = new_folder_name
        manifest["meeting"]["original_folder"] = folder_name
        if "archive_path" in manifest:
            manifest["archive_path"] = manifest["archive_path"].replace(folder_name, new_folder_name)

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

    if rename_skipped:
        logger.info(f"  Folder rename skipped: {folder_name} (stable meeting_id lock)")

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
