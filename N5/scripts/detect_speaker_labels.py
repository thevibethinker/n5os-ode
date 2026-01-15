#!/usr/bin/env python3
"""
Speaker Label Detection

Analyzes a transcript to determine if it has speaker labels.
Returns structured analysis for the LLM to use in speaker attribution.

Usage:
    python3 detect_speaker_labels.py --text "..."
    python3 detect_speaker_labels.py --file /path/to/transcript.txt
"""

import argparse
import re
import json
import sys
from pathlib import Path
from collections import Counter


def detect_speaker_patterns(text: str) -> dict:
    """
    Analyze text for speaker label patterns.
    Returns detection results and confidence.
    """
    lines = text.strip().split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    
    # Common speaker label patterns
    patterns = {
        # "Speaker Name: text" or "SPEAKER: text"
        "colon_prefix": re.compile(r'^([A-Z][a-zA-Z\s]{1,30}):\s+.+', re.MULTILINE),
        # "[Speaker Name] text" or "[00:00:00] Speaker: text
        "bracket_prefix": re.compile(r'^\[([^\]]+)\]\s*([A-Z][a-zA-Z]+)?:?\s*.+', re.MULTILINE),
        # "Speaker Name (00:00:00): text"
        "timestamp_speaker": re.compile(r'^([A-Z][a-zA-Z\s]+)\s*\(\d{1,2}:\d{2}(?::\d{2})?\):\s*.+', re.MULTILINE),
        # Just timestamps "[00:00:00] text" without speaker
        "timestamp_only": re.compile(r'^\[\d{1,2}:\d{2}(?::\d{2})?\]\s+[^A-Z:]', re.MULTILINE),
        # "Speaker 1:", "Speaker 2:" generic labels
        "generic_speaker": re.compile(r'^Speaker\s*\d+:\s+.+', re.MULTILINE),
    }
    
    matches = {}
    for name, pattern in patterns.items():
        found = pattern.findall(text)
        matches[name] = len(found)
    
    # Extract unique speaker names if found
    speakers_found = []
    if matches["colon_prefix"] > 2:
        raw_matches = patterns["colon_prefix"].findall(text)
        speakers_found = list(set(raw_matches))
    
    # Calculate coverage - what % of lines have speaker labels
    labeled_lines = 0
    for line in non_empty_lines:
        for pattern in [patterns["colon_prefix"], patterns["bracket_prefix"], 
                       patterns["timestamp_speaker"], patterns["generic_speaker"]]:
            if pattern.match(line):
                labeled_lines += 1
                break
    
    coverage = labeled_lines / len(non_empty_lines) if non_empty_lines else 0
    
    # Determine if transcript has labels
    has_labels = coverage > 0.5 or matches["colon_prefix"] > 5
    
    # Detect turn-taking signals in unlabeled text
    turn_signals = {
        "questions": len(re.findall(r'\?(?:\s|$)', text)),
        "responses": len(re.findall(r'^(?:Yes|No|Yeah|Sure|Right|Okay|I think|Well,|So,)', text, re.MULTILINE | re.IGNORECASE)),
        "agreements": len(re.findall(r'(?:I agree|That\'s right|Exactly|Makes sense)', text, re.IGNORECASE)),
        "transitions": len(re.findall(r'(?:Anyway|Moving on|Next|Also|Another thing)', text, re.IGNORECASE)),
    }
    
    # Estimate speaker count from unlabeled text
    estimated_speakers = 2  # Default assumption
    if len(speakers_found) > 0:
        estimated_speakers = len(speakers_found)
    elif turn_signals["questions"] > 3 and turn_signals["responses"] > 3:
        estimated_speakers = 2  # Q&A pattern suggests 2
    
    return {
        "has_speaker_labels": has_labels,
        "confidence": round(coverage, 2),
        "label_coverage_pct": round(coverage * 100, 1),
        "speakers_detected": speakers_found[:10],  # Cap at 10
        "speaker_count": len(speakers_found) if speakers_found else estimated_speakers,
        "pattern_matches": matches,
        "turn_signals": turn_signals,
        "total_lines": len(non_empty_lines),
        "labeled_lines": labeled_lines,
    }


def extract_segments_for_attribution(text: str, max_segments: int = 15) -> list:
    """
    Break unlabeled text into segments at likely speaker boundaries.
    Returns segments with context for LLM attribution.
    """
    # First, check if text is paragraph-separated (common in transcripts)
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    # If paragraphs are well-defined (3+ paragraphs), use them as segments
    if len(paragraphs) >= 3:
        segments = [p.strip() for p in paragraphs if p.strip()]
    else:
        # Fall back to line-by-line analysis
        lines = text.strip().split('\n')
        
        # Segment boundaries: questions, topic shifts, response indicators
        boundary_patterns = [
            r'\?$',  # Questions often end turns
            r'^(?:Yes|No|Yeah|Sure|Right|Okay|Well|So|I think|Actually)',  # Response starters
            r'^(?:Anyway|Moving on|Let me|Can you|What about|How about)',  # Topic shifts
        ]
        
        segments = []
        current_segment = []
        
        for line in lines:
            line = line.strip()
            if not line:
                # Empty line can be a segment boundary
                if current_segment:
                    segments.append(' '.join(current_segment))
                    current_segment = []
                continue
                
            # Check if this line starts a new segment
            is_boundary = False
            if current_segment:  # Don't break on first line
                for pattern in boundary_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        is_boundary = True
                        break
                # Also break on significant pause indicators
                if line.startswith(('...', '—', '–')):
                    is_boundary = True
            
            if is_boundary and current_segment:
                segments.append(' '.join(current_segment))
                current_segment = [line]
            else:
                current_segment.append(line)
        
        # Don't forget last segment
        if current_segment:
            segments.append(' '.join(current_segment))
    
    # If still too few segments, split more aggressively (every 2-3 sentences)
    if len(segments) < 5:
        all_text = ' '.join(segments) if segments else text
        sentences = re.split(r'(?<=[.!?])\s+', all_text)
        segments = []
        current = []
        for i, sent in enumerate(sentences):
            current.append(sent)
            if len(current) >= 2 and (i + 1) % 2 == 0:
                segments.append(' '.join(current))
                current = []
        if current:
            segments.append(' '.join(current))
    
    # Return up to max_segments, evenly distributed
    if len(segments) > max_segments:
        step = len(segments) / max_segments
        segments = [segments[int(i * step)] for i in range(max_segments)]
    
    # Add index and truncate long segments
    result = []
    for i, seg in enumerate(segments):
        truncated = seg[:200] + "..." if len(seg) > 200 else seg
        result.append({
            "index": i + 1,
            "text": truncated,
            "full_length": len(seg),
        })
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Detect speaker labels in transcript")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Raw transcript text")
    group.add_argument("--file", help="Path to transcript file")
    parser.add_argument("--segments", action="store_true", help="Also extract segments for attribution")
    
    args = parser.parse_args()
    
    if args.file:
        text = Path(args.file).read_text()
    else:
        text = args.text
    
    result = detect_speaker_patterns(text)
    
    if args.segments and not result["has_speaker_labels"]:
        result["segments_for_attribution"] = extract_segments_for_attribution(text)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()


