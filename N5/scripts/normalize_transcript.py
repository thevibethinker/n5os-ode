#!/usr/bin/env python3
"""
Normalize Meeting Transcript

Converts formatted transcripts (timestamps, bold formatting) to clean markdown
with speaker turns. Reusable component for meeting ingestion pipelines.

Usage:
    python3 normalize_transcript.py <input.md> [output.md]
    
    If output not specified, writes to: <input>_normalized.md
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def parse_speaker_turns(content: str) -> List[Tuple[str, str]]:
    """
    Parse transcript content into (speaker, text) tuples.
    
    Handles formats:
    - **\\n00:00**\\nSpeaker Name\\nText
    - **Timestamp**\\nSpeaker\\nText
    """
    # Remove escaped characters
    content = content.replace("\\\\", "").replace("\\'", "'")
    
    # Pattern: **timestamp**\nSpeaker\nText
    pattern = r'\*\*[^*]+\*\*\s*\n([^\n]+)\s*\n([^\*]+?)(?=\*\*|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    turns = []
    for speaker, text in matches:
        speaker = speaker.strip()
        text = text.strip()
        if speaker and text:
            turns.append((speaker, text))
    
    return turns


def merge_consecutive_turns(turns: List[Tuple[str, str]]) -> List[Tuple[str, List[str]]]:
    """
    Merge consecutive turns from same speaker.
    Returns: [(speaker, [utterances])]
    """
    if not turns:
        return []
    
    merged = []
    current_speaker = turns[0][0]
    current_utterances = [turns[0][1]]
    
    for speaker, text in turns[1:]:
        if speaker == current_speaker:
            current_utterances.append(text)
        else:
            merged.append((current_speaker, current_utterances))
            current_speaker = speaker
            current_utterances = [text]
    
    # Add final speaker
    merged.append((current_speaker, current_utterances))
    return merged


def format_transcript(turns: List[Tuple[str, List[str]]]) -> str:
    """Format merged turns as clean markdown."""
    output = []
    
    for speaker, utterances in turns:
        output.append(f"**{speaker}:**")
        output.append(" ".join(utterances))
        output.append("")  # Blank line between speakers
    
    return "\n".join(output)


def normalize_transcript(input_path: Path, output_path: Path = None) -> int:
    """
    Normalize transcript file.
    
    Returns: Number of speaker turns in output
    """
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return -1
    
    # Read input
    content = input_path.read_text()
    
    # Parse and merge
    turns = parse_speaker_turns(content)
    merged = merge_consecutive_turns(turns)
    
    # Format output
    normalized = format_transcript(merged)
    
    # Write
    if output_path is None:
        stem = input_path.stem
        if stem.endswith("_raw"):
            stem = stem[:-4]
        output_path = input_path.parent / f"{stem}.transcript.md"
    
    output_path.write_text(normalized)
    
    print(f"✓ Normalized: {output_path}")
    print(f"  Turns: {len(merged)}")
    print(f"  Size: {len(normalized)} bytes")
    
    return len(merged)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    result = normalize_transcript(input_path, output_path)
    sys.exit(0 if result > 0 else 1)


if __name__ == "__main__":
    main()
