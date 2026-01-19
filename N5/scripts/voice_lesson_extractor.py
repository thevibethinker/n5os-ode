#!/usr/bin/env python3
"""
Voice Lesson Extractor - Extract actionable lessons from diff analysis.

Usage:
  python3 N5/scripts/voice_lesson_extractor.py extract \
    --diff-json '{"categories": ...}' \
    --content-type "cold_email" \
    [--context "Partnership outreach"]
  
  python3 N5/scripts/voice_lesson_extractor.py extract-from-pair --id 5
"""

import argparse
import json
import os
import sqlite3
import sys
import uuid
from pathlib import Path

import requests

DB_PATH = Path(__file__).parent.parent / "data" / "voice_library.db"

LESSON_PROMPT = """Based on this diff analysis, extract actionable lessons about V's writing preferences.

DIFF ANALYSIS:
{diff_json}

CONTENT TYPE: {content_type}
CONTEXT: {context}

Extract lessons that capture V's preferences. For each lesson:
1. Be specific and actionable - not vague principles
2. Include what to AVOID (anti_pattern) and what to DO INSTEAD (positive_pattern)
3. Consider if this might apply globally or only to this content type
4. Extract any reusable phrases or "moves" V introduced

Respond with ONLY valid JSON in this exact format:
{{
  "lessons": [
    {{
      "id": "lesson_<random_8_chars>",
      "content_type": "{content_type}",
      "lesson": "Clear statement of the preference, e.g., 'When writing cold emails, V prefers...'",
      "anti_pattern": "What to avoid, e.g., 'Opening with I wanted to...'",
      "positive_pattern": "What to do instead, e.g., 'Open with concrete action or artifact'",
      "confidence": "high|medium|low",
      "global_candidate": false,
      "source_changes": ["brief list of changes this lesson is based on"]
    }}
  ],
  "candidate_primitives": [
    {{
      "text": "exact phrase or structure V introduced",
      "type": "phrase|opener|closer|transition|structure",
      "function": "What this achieves, e.g., 'Establishes credibility through action'",
      "source": "v_edit"
    }}
  ]
}}

Guidelines:
- High confidence: Clear, repeated pattern or major deliberate change
- Medium confidence: Single instance but strong signal
- Low confidence: Might be context-specific
- global_candidate: true if this seems like a general V preference, not just for this content type
- Extract 2-5 lessons depending on richness of the diff
- Extract primitives only for distinctive phrases/structures V introduced"""


def extract_with_llm(diff_json: dict, content_type: str, context: str = None) -> dict:
    """Call /zo/ask to extract lessons."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    prompt = LESSON_PROMPT.format(
        diff_json=json.dumps(diff_json, indent=2),
        content_type=content_type,
        context=context or "Not specified"
    )
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json={"input": prompt},
        timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"API error: {response.status_code} - {response.text}")
    
    result = response.json()
    output = result.get("output", "")
    
    # Parse JSON from response
    if "```json" in output:
        output = output.split("```json")[1].split("```")[0].strip()
    elif "```" in output:
        output = output.split("```")[1].split("```")[0].strip()
    
    try:
        parsed = json.loads(output)
        # Ensure IDs are unique
        for lesson in parsed.get("lessons", []):
            if not lesson.get("id") or lesson["id"].startswith("lesson_<"):
                lesson["id"] = f"lesson_{uuid.uuid4().hex[:8]}"
        return parsed
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse JSON: {e}",
            "raw_output": output
        }


def extract(args):
    """Extract lessons from diff JSON."""
    try:
        diff_json = json.loads(args.diff_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing --diff-json: {e}")
        return 1
    
    result = extract_with_llm(diff_json, args.content_type, args.context)
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
            return 1
        
        print("=== EXTRACTED LESSONS ===\n")
        
        for lesson in result.get("lessons", []):
            print(f"[{lesson.get('id', 'N/A')}] ({lesson.get('confidence', '?')} confidence)")
            print(f"  {lesson.get('lesson', 'N/A')}")
            print(f"  ✗ Avoid: {lesson.get('anti_pattern', 'N/A')}")
            print(f"  ✓ Instead: {lesson.get('positive_pattern', 'N/A')}")
            if lesson.get("global_candidate"):
                print(f"  🌐 Global candidate")
            print()
        
        primitives = result.get("candidate_primitives", [])
        if primitives:
            print("--- Candidate Primitives ---")
            for prim in primitives:
                print(f"  \"{prim.get('text', '')}\"")
                print(f"    Type: {prim.get('type', '?')} | Function: {prim.get('function', '?')}")
                print()
    
    return 0


def extract_from_pair(args):
    """Extract lessons directly from a pair (runs diff first)."""
    # Import diff analyzer
    from voice_diff_analyzer import analyze_with_llm as diff_analyze
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT original_text, improved_text, content_type, context FROM feedback_pairs WHERE id = ?",
        (args.id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"Error: Pair #{args.id} not found")
        return 1
    
    # Run diff analysis first
    print(f"Analyzing pair #{args.id}...", file=sys.stderr)
    diff_result = diff_analyze(row["original_text"], row["improved_text"])
    
    if "error" in diff_result:
        print(f"Diff analysis failed: {diff_result['error']}")
        return 1
    
    # Extract lessons
    print(f"Extracting lessons...", file=sys.stderr)
    result = extract_with_llm(diff_result, row["content_type"], row["context"])
    
    # Add metadata
    result["pair_id"] = args.id
    result["diff_analysis"] = diff_result
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"=== LESSONS FROM PAIR #{args.id} ===\n")
        print(f"Content Type: {row['content_type']}")
        print(f"Context: {row['context'] or 'N/A'}\n")
        
        for lesson in result.get("lessons", []):
            print(f"[{lesson.get('id', 'N/A')}] ({lesson.get('confidence', '?')} confidence)")
            print(f"  {lesson.get('lesson', 'N/A')}")
            print(f"  ✗ Avoid: {lesson.get('anti_pattern', 'N/A')}")
            print(f"  ✓ Instead: {lesson.get('positive_pattern', 'N/A')}")
            if lesson.get("global_candidate"):
                print(f"  🌐 Global candidate")
            print()
        
        primitives = result.get("candidate_primitives", [])
        if primitives:
            print("--- Candidate Primitives ---")
            for prim in primitives:
                print(f"  \"{prim.get('text', '')}\"")
                print(f"    Type: {prim.get('type', '?')} | Function: {prim.get('function', '?')}")
                print()
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Extract lessons from diff analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # extract command
    extract_parser = subparsers.add_parser("extract", help="Extract lessons from diff JSON")
    extract_parser.add_argument("--diff-json", required=True, help="Diff analysis JSON")
    extract_parser.add_argument("--content-type", required=True, help="Content type (e.g., cold_email)")
    extract_parser.add_argument("--context", help="Additional context")
    extract_parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    
    # extract-from-pair command
    pair_parser = subparsers.add_parser("extract-from-pair", help="Extract lessons directly from a pair")
    pair_parser.add_argument("--id", type=int, required=True, help="Pair ID")
    pair_parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    if args.command == "extract":
        return extract(args)
    elif args.command == "extract-from-pair":
        return extract_from_pair(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
