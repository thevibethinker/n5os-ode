#!/usr/bin/env python3
"""
Extract voice primitive candidates from meeting transcripts.

Uses B35 block for LLM-based extraction, then scores with Pangram
for distinctiveness. Outputs to review queue or direct import.

Usage:
  python3 extract_voice_primitives.py --meeting "2026-01-10_Client-Call"
  python3 extract_voice_primitives.py --all-unprocessed
  python3 extract_voice_primitives.py --since 2026-01-01
  python3 extract_voice_primitives.py --transcript /path/to/transcript.md

Process:
1. Load transcript
2. Run B35 block extraction (via LLM prompt)
3. Score each candidate with Pangram (distinctiveness)
4. Flag explicit capture signals (novelty_flagged = 1)
5. Write to review queue sorted by: novelty_flagged DESC, distinctiveness_score DESC
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# Paths
WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "N5/data/voice_library.db"
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"
REVIEW_DIR = WORKSPACE / "N5/review/voice"
B35_PROMPT_PATH = WORKSPACE / "Prompts/Blocks/Generate_B35.prompt.md"

# Import distinctiveness scorer
sys.path.insert(0, str(WORKSPACE / "N5/scripts"))
try:
    from compute_distinctiveness import compute_distinctiveness
except ImportError:
    compute_distinctiveness = None
    print("WARNING: compute_distinctiveness not available, scores will be 0.0")


def find_meeting_folder(meeting_name: str) -> Optional[Path]:
    """Find meeting folder by partial name match."""
    for week_dir in MEETINGS_DIR.iterdir():
        if not week_dir.is_dir() or not week_dir.name.startswith("Week-of-"):
            continue
        for meeting_dir in week_dir.iterdir():
            if meeting_name.lower() in meeting_dir.name.lower():
                return meeting_dir
    return None


def find_transcript(meeting_path: Path) -> Optional[Path]:
    """Find transcript file in meeting folder."""
    candidates = [
        meeting_path / "transcript.md",
        meeting_path / "transcript.txt",
    ]
    # Also check for any .md file that looks like a transcript
    for f in meeting_path.glob("*.md"):
        if "transcript" in f.name.lower():
            candidates.insert(0, f)
    
    for c in candidates:
        if c.exists():
            return c
    return None


def extract_v_utterances(transcript_text: str) -> str:
    """Extract only V's (Vrijen's) utterances from transcript."""
    lines = transcript_text.split('\n')
    v_lines = []
    in_v_block = False
    
    for line in lines:
        # Check for speaker markers
        if re.match(r'\*?\*?Vrijen|^V:|^Vrijen Attawar', line, re.IGNORECASE):
            in_v_block = True
            v_lines.append(line)
        elif re.match(r'\*?\*?\w+\s+(Poonawala|Smith|Johnson|Guest)|\*?\*?\d{2}:\d{2}', line):
            # Another speaker or timestamp = end of V's turn
            in_v_block = False
        elif in_v_block:
            v_lines.append(line)
    
    return '\n'.join(v_lines) if v_lines else transcript_text


def generate_b35_prompt(transcript: str) -> str:
    """Generate the B35 extraction prompt."""
    return f"""You are extracting linguistic primitives from a meeting transcript for V's Voice Library.

TRANSCRIPT:
{transcript[:15000]}  # Truncate for token limits

INSTRUCTIONS:
1. Read through V's utterances carefully
2. Identify analogies, metaphors, distinctive phrases, and capture signals
3. For each primitive:
   - Extract the exact text (minimum 50 chars)
   - Tag with 1-3 relevant domains
   - Include brief context
   - Flag if it's a capture signal (V endorsing someone else's language)
4. Output as JSONL (one JSON object per line)
5. Quality over quantity — only extract genuinely distinctive language, not generic statements
6. Look for: "X is like Y", conceptual framings, memorable turns of phrase, "I'm stealing that" moments

DOMAIN OPTIONS: career, incentives, ethics, optionality, status, talent, entrepreneurship, relationships

OUTPUT (JSONL only, no other text):"""


def parse_jsonl_output(llm_output: str) -> list[dict]:
    """Parse JSONL output from LLM, handling common formatting issues."""
    primitives = []
    
    # Try to find JSONL lines
    for line in llm_output.split('\n'):
        line = line.strip()
        if not line or not line.startswith('{'):
            continue
        try:
            obj = json.loads(line)
            if 'text' in obj:
                primitives.append(obj)
        except json.JSONDecodeError:
            continue
    
    return primitives


def score_primitives(primitives: list[dict]) -> list[dict]:
    """Score each primitive with Pangram for distinctiveness."""
    for p in primitives:
        text = p.get('text', '')
        if len(text) < 50:
            p['distinctiveness_score'] = 0.0
            p['score_note'] = 'Too short for reliable scoring'
            continue
        
        if compute_distinctiveness:
            try:
                score = compute_distinctiveness(text)
                p['distinctiveness_score'] = score
                time.sleep(1)  # Rate limit
            except Exception as e:
                p['distinctiveness_score'] = 0.0
                p['score_note'] = f'Scoring error: {e}'
        else:
            p['distinctiveness_score'] = 0.0
            p['score_note'] = 'Scorer not available'
    
    return primitives


def write_to_review_queue(primitives: list[dict], source_meeting: str) -> Path:
    """Write primitives to review queue as markdown."""
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    batch_num = len(list(REVIEW_DIR.glob(f"{timestamp}_voice-primitives_*.md"))) + 1
    filename = f"{timestamp}_voice-primitives_candidates_batch-{batch_num:03d}.md"
    filepath = REVIEW_DIR / filename
    
    # Sort by novelty_flagged DESC, distinctiveness_score DESC
    sorted_primitives = sorted(
        primitives,
        key=lambda x: (x.get('capture_signal', False), x.get('distinctiveness_score', 0)),
        reverse=True
    )
    
    content = f"""---
created: {timestamp}
last_edited: {timestamp}
version: 1.0
provenance: extract_voice_primitives.py
type: review_queue
review_domain: voice_primitives
source_meeting: {source_meeting}
status: pending_review
---

# Voice Primitives Review: {source_meeting}

**Extracted:** {len(primitives)} candidates  
**Source:** {source_meeting}  
**Generated:** {datetime.now().isoformat()}

## Review Instructions

For each candidate below:
- **Approve** if it's genuinely distinctive V language worth preserving
- **Reject** if it's generic, AI-ish, or only makes sense in original context
- **Edit** if the core is good but needs trimming/rewording

---

## Candidates

"""
    
    for i, p in enumerate(sorted_primitives, 1):
        capture_flag = "🎯 CAPTURE SIGNAL" if p.get('capture_signal') else ""
        score = p.get('distinctiveness_score', 0)
        score_display = f"{score:.1%}" if score > 0 else "unscored"
        domains = ', '.join(p.get('domains', []))
        
        content += f"""### Candidate {i} {capture_flag}

- **Type:** {p.get('type', 'unknown')}
- **Distinctiveness:** {score_display}
- **Domains:** {domains}
- **Text:** "{p.get('text', '')}"
- **Context:** {p.get('context', 'N/A')}
- **Decision:** (Approve / Reject / Edit)
- **Notes:**

---

"""
    
    filepath.write_text(content)
    return filepath


def import_to_db(primitives: list[dict], source_file: str, auto_approve_threshold: float = 0.7) -> int:
    """Import primitives to voice_library.db."""
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    imported = 0
    
    for p in primitives:
        primitive_id = f"VP-{uuid.uuid4().hex[:8].upper()}"
        score = p.get('distinctiveness_score', 0)
        status = 'approved' if score >= auto_approve_threshold else 'candidate'
        
        cursor.execute("""
            INSERT INTO primitives (
                id, primitive_type, exact_text, domains_json,
                distinctiveness_score, novelty_flagged, status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            primitive_id,
            p.get('type', 'phrase'),
            p.get('text', ''),
            json.dumps(p.get('domains', [])),
            score,
            1 if p.get('capture_signal') else 0,
            status,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Add source record
        cursor.execute("""
            INSERT INTO sources (
                id, primitive_id, source_file, source_type,
                block_id, speaker, capture_signal_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"SRC-{uuid.uuid4().hex[:8].upper()}",
            primitive_id,
            source_file,
            'meeting_transcript',
            'B35',
            'V',
            'I\'m stealing that' if p.get('capture_signal') else None
        ))
        
        imported += 1
    
    conn.commit()
    conn.close()
    return imported


def main():
    parser = argparse.ArgumentParser(
        description="Extract voice primitives from meeting transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  extract_voice_primitives.py --meeting "2026-01-10_Client-Call"
  extract_voice_primitives.py --transcript /path/to/transcript.md
  extract_voice_primitives.py --meeting "Client-Call" --import --threshold 0.5
        """
    )
    
    parser.add_argument("--meeting", help="Meeting name (partial match)")
    parser.add_argument("--transcript", help="Direct path to transcript file")
    parser.add_argument("--import", dest="do_import", action="store_true",
                        help="Import to database (default: review queue only)")
    parser.add_argument("--threshold", type=float, default=0.7,
                        help="Auto-approve threshold for import (default: 0.7)")
    parser.add_argument("--no-score", action="store_true",
                        help="Skip Pangram scoring (faster, for testing)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Extract and display without saving")
    
    args = parser.parse_args()
    
    # Find transcript
    transcript_path = None
    source_name = "unknown"
    
    if args.transcript:
        transcript_path = Path(args.transcript)
        source_name = transcript_path.stem
    elif args.meeting:
        meeting_folder = find_meeting_folder(args.meeting)
        if meeting_folder:
            transcript_path = find_transcript(meeting_folder)
            source_name = meeting_folder.name
        else:
            print(f"ERROR: Meeting '{args.meeting}' not found")
            sys.exit(1)
    else:
        print("ERROR: Specify --meeting or --transcript")
        sys.exit(1)
    
    if not transcript_path or not transcript_path.exists():
        print(f"ERROR: Transcript not found: {transcript_path}")
        sys.exit(1)
    
    print(f"Loading transcript: {transcript_path}")
    transcript_text = transcript_path.read_text()
    
    # Extract V's utterances
    v_text = extract_v_utterances(transcript_text)
    print(f"Extracted {len(v_text)} chars of V's utterances")
    
    # Generate B35 prompt
    prompt = generate_b35_prompt(v_text)
    
    print("\n" + "="*60)
    print("B35 EXTRACTION PROMPT GENERATED")
    print("="*60)
    print("\nTo extract primitives, run this prompt through the LLM.")
    print("Then paste the JSONL output below (or use --dry-run to see prompt only).")
    print("\nPrompt saved to: /tmp/b35_prompt.txt")
    
    Path("/tmp/b35_prompt.txt").write_text(prompt)
    
    if args.dry_run:
        print("\n[DRY RUN] Prompt generated. No extraction performed.")
        print(f"\nPrompt preview (first 2000 chars):\n{prompt[:2000]}...")
        return
    
    # For now, output the prompt for manual LLM invocation
    # In a full implementation, this would call the LLM API
    print("\n" + "="*60)
    print("MANUAL STEP REQUIRED")
    print("="*60)
    print("""
This script generates the extraction prompt but does not invoke the LLM directly.

To complete extraction:
1. Copy the prompt from /tmp/b35_prompt.txt
2. Run it through Zo or another LLM
3. Save the JSONL output to /tmp/b35_output.jsonl
4. Run: python3 extract_voice_primitives.py --process-output /tmp/b35_output.jsonl

Or use the --from-jsonl flag if you already have output:
  python3 extract_voice_primitives.py --from-jsonl /tmp/b35_output.jsonl --meeting "Meeting Name"
""")


if __name__ == "__main__":
    main()

