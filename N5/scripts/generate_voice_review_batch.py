#!/usr/bin/env python3
"""
Generate voice primitive review batch from multiple meeting transcripts.

Part of Voice Library V2 (Phase 2.4: Generate review queue batches).

Processes meetings, extracts V's utterances, and uses LLM to extract
candidate primitives for human review.

Usage:
  python3 generate_voice_review_batch.py --count 5
  python3 generate_voice_review_batch.py --meetings "David" "Nira" "Ilse"
  python3 generate_voice_review_batch.py --since 2026-01-01
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"
REVIEW_DIR = WORKSPACE / "N5/review/voice"


def find_transcripts(count: int = 5, meeting_names: list = None, since: str = None) -> list[Path]:
    """Find transcript files from processed meetings."""
    transcripts = []
    
    for week_dir in sorted(MEETINGS_DIR.iterdir(), reverse=True):
        if not week_dir.is_dir() or not week_dir.name.startswith("Week-of-"):
            continue
        
        for meeting_dir in sorted(week_dir.iterdir(), reverse=True):
            if not meeting_dir.is_dir():
                continue
            
            # Filter by meeting name if specified
            if meeting_names:
                if not any(name.lower() in meeting_dir.name.lower() for name in meeting_names):
                    continue
            
            # Find transcript
            transcript = None
            for f in meeting_dir.glob("*.md"):
                if "transcript" in f.name.lower():
                    transcript = f
                    break
            if not transcript:
                transcript = meeting_dir / "transcript.md"
                if not transcript.exists():
                    continue
            
            if transcript.exists():
                # Check since date
                if since:
                    try:
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', meeting_dir.name)
                        if date_match:
                            meeting_date = date_match.group(1)
                            if meeting_date < since:
                                continue
                    except:
                        pass
                
                transcripts.append(transcript)
                if len(transcripts) >= count:
                    return transcripts
    
    return transcripts


def extract_v_utterances(transcript_text: str) -> str:
    """Extract only V's utterances from transcript."""
    lines = transcript_text.split('\n')
    v_lines = []
    
    for line in lines:
        # Match various speaker formats for V
        if re.match(r'.*Vrijen.*:', line, re.IGNORECASE):
            v_lines.append(line)
        elif re.match(r'^V:', line):
            v_lines.append(line)
        elif re.match(r'^Me:', line, re.IGNORECASE):
            # "Me:" format (common in Granola transcripts)
            v_lines.append(line)
        elif re.match(r'^\*\*Vrijen', line, re.IGNORECASE):
            # Bold markdown format
            v_lines.append(line)
    
    return '\n'.join(v_lines) if v_lines else ""


def generate_extraction_prompt(v_utterances: str, meeting_name: str) -> str:
    """Generate B35-style extraction prompt."""
    return f"""Extract linguistic primitives from V's meeting utterances.

MEETING: {meeting_name}

V's UTTERANCES:
{v_utterances[:12000]}

EXTRACT distinctive language patterns:
1. Analogies and metaphors (e.g., "X is like Y because...")
2. Conceptual frames (e.g., "think of it as...", "the way I see it...")
3. Signature phrases (distinctive word combinations V uses)
4. Capture signals (V endorsing someone else's phrase: "I'm stealing that", "that's a great way to put it")

For each primitive, output ONE JSON object per line:
{{"text": "exact phrase (50+ chars)", "type": "metaphor|analogy|signature_phrase|conceptual_frame|capture_signal", "domains": ["career", "tech"], "context": "brief usage context"}}

OUTPUT ONLY JSONL. No other text. Quality over quantity — only genuinely distinctive language."""


def generate_review_batch(transcripts: list[Path], output_path: Path):
    """Generate review batch file with extraction prompts."""
    
    batch_items = []
    
    for transcript in transcripts:
        meeting_name = transcript.parent.name
        content = transcript.read_text()
        v_utterances = extract_v_utterances(content)
        
        if len(v_utterances) < 500:
            print(f"Skipping {meeting_name}: insufficient V utterances ({len(v_utterances)} chars)")
            continue
        
        prompt = generate_extraction_prompt(v_utterances, meeting_name)
        
        batch_items.append({
            "meeting": meeting_name,
            "transcript_path": str(transcript),
            "v_utterance_chars": len(v_utterances),
            "extraction_prompt": prompt,
            "status": "pending",
            "extracted_at": None,
            "primitives": []
        })
    
    # Write batch file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for item in batch_items:
            f.write(json.dumps(item) + '\n')
    
    print(f"\n✅ Generated review batch: {output_path}")
    print(f"   Meetings: {len(batch_items)}")
    print(f"   Total V utterances: {sum(i['v_utterance_chars'] for i in batch_items):,} chars")
    
    # Also generate human-readable review sheet
    review_sheet = output_path.with_suffix('.md')
    generate_review_sheet(batch_items, review_sheet)
    
    return batch_items


def generate_review_sheet(batch_items: list, output_path: Path):
    """Generate human-readable review sheet."""
    
    content = f"""---
created: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
last_edited: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
version: 1.0
provenance: voice-library-v2
type: review_queue
status: pending
---

# Voice Primitives Review Batch

**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  
**Meetings:** {len(batch_items)}  
**Status:** Pending extraction + human review

---

## Instructions

1. For each meeting below, run the extraction prompt through LLM
2. Paste JSONL output into the corresponding section
3. Review each primitive:
   - `[x]` = approve for voice library
   - `[ ]` = reject (too generic / not distinctive)
4. Run import script on approved primitives

---

## Meetings

"""
    
    for i, item in enumerate(batch_items, 1):
        content += f"""### {i}. {item['meeting']}

**Transcript:** `{item['transcript_path']}`  
**V utterances:** {item['v_utterance_chars']:,} chars

<details>
<summary>Click to expand extraction prompt</summary>

```
{item['extraction_prompt'][:3000]}...
```

</details>

**Extracted Primitives:**

<!-- Paste JSONL output here, then convert to checkboxes -->

```jsonl
<!-- LLM output goes here -->
```

---

"""
    
    output_path.write_text(content)
    print(f"✅ Generated review sheet: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate voice primitive review batch")
    parser.add_argument("--count", type=int, default=5, help="Number of meetings to process")
    parser.add_argument("--meetings", nargs="+", help="Specific meeting names to include")
    parser.add_argument("--since", help="Only meetings since this date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output path (default: auto-generated)")
    
    args = parser.parse_args()
    
    # Find transcripts
    transcripts = find_transcripts(
        count=args.count,
        meeting_names=args.meetings,
        since=args.since
    )
    
    if not transcripts:
        print("No transcripts found matching criteria")
        sys.exit(1)
    
    print(f"Found {len(transcripts)} transcripts:")
    for t in transcripts:
        print(f"  - {t.parent.name}")
    
    # Generate output path
    if args.output:
        output_path = Path(args.output)
    else:
        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        output_path = REVIEW_DIR / f"{date_str}_voice-primitives_batch.jsonl"
    
    # Generate batch
    generate_review_batch(transcripts, output_path)


if __name__ == "__main__":
    main()


