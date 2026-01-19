#!/usr/bin/env python3
"""
Voice Analyze Pair - Combined pipeline: diff → extract → store.

Usage:
  python3 N5/scripts/voice_analyze_pair.py --id 5 [--output json|text] [--store]

With --store:
  1. Run diff analysis
  2. Extract lessons
  3. Store lessons to semantic memory
  4. Add candidate primitives (unapproved)
  5. Update voice-lessons.md
  6. Mark pair as analyzed
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import requests

DB_PATH = Path(__file__).parent.parent / "data" / "voice_library.db"

# Import the analysis functions
sys.path.insert(0, str(Path(__file__).parent))
from voice_diff_analyzer import analyze_with_llm as diff_analyze


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
      "lesson": "Clear statement of the preference",
      "anti_pattern": "What to avoid",
      "positive_pattern": "What to do instead",
      "confidence": "high|medium|low",
      "global_candidate": false,
      "source_changes": ["brief list of changes this lesson is based on"]
    }}
  ],
  "candidate_primitives": [
    {{
      "text": "exact phrase or structure V introduced",
      "type": "phrase|opener|closer|transition|structure",
      "function": "What this achieves",
      "source": "v_edit"
    }}
  ]
}}"""


def extract_lessons(diff_json: dict, content_type: str, context: str = None) -> dict:
    """Extract lessons from diff analysis."""
    import uuid
    
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
    
    # Parse JSON
    if "```json" in output:
        output = output.split("```json")[1].split("```")[0].strip()
    elif "```" in output:
        output = output.split("```")[1].split("```")[0].strip()
    
    try:
        parsed = json.loads(output)
        for lesson in parsed.get("lessons", []):
            if not lesson.get("id") or "<" in lesson.get("id", ""):
                lesson["id"] = f"lesson_{uuid.uuid4().hex[:8]}"
        return parsed
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}", "raw_output": output}


def store_results(lesson_data: dict, pair_id: int) -> bool:
    """Store lessons and primitives using voice_lesson_store.py."""
    lesson_json = json.dumps({
        "lessons": lesson_data.get("lessons", []),
        "candidate_primitives": lesson_data.get("candidate_primitives", [])
    })
    
    # Call the storage script
    script_path = Path(__file__).parent / "voice_lesson_store.py"
    result = subprocess.run(
        [
            sys.executable, str(script_path),
            "store",
            "--lesson-json", lesson_json,
            "--pair-id", str(pair_id)
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Storage error: {result.stderr}", file=sys.stderr)
        return False
    
    print(result.stdout)
    return True


def analyze_pair(args):
    """Full pipeline: diff → lessons → store."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT original_text, improved_text, content_type, context, analyzed FROM feedback_pairs WHERE id = ?",
        (args.id,)
    )
    row = cursor.fetchone()
    
    if not row:
        print(f"Error: Pair #{args.id} not found")
        conn.close()
        return 1
    
    original = row["original_text"]
    improved = row["improved_text"]
    content_type = row["content_type"]
    context = row["context"]
    
    step_count = 3 if args.store else 2
    
    # Step 1: Diff analysis
    print(f"[1/{step_count}] Analyzing diff for pair #{args.id}...", file=sys.stderr)
    diff_result = diff_analyze(original, improved)
    
    if "error" in diff_result:
        print(f"Diff analysis failed: {diff_result['error']}")
        conn.close()
        return 1
    
    # Step 2: Lesson extraction
    print(f"[2/{step_count}] Extracting lessons...", file=sys.stderr)
    lesson_result = extract_lessons(diff_result, content_type, context)
    
    # Combine results
    combined = {
        "pair_id": args.id,
        "content_type": content_type,
        "context": context,
        "original_text": original,
        "improved_text": improved,
        "diff_analysis": diff_result,
        "lessons": lesson_result.get("lessons", []),
        "candidate_primitives": lesson_result.get("candidate_primitives", [])
    }
    
    if "error" in lesson_result:
        combined["lesson_extraction_error"] = lesson_result["error"]
    
    # Step 3: Storage (if --store)
    if args.store:
        print(f"[3/{step_count}] Storing results...", file=sys.stderr)
        if store_results(lesson_result, args.id):
            combined["stored"] = True
        else:
            combined["store_error"] = "Failed to store results"
    
    conn.close()
    
    if args.output == "json":
        print(json.dumps(combined, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"VOICE ANALYSIS: Pair #{args.id}")
        print(f"{'='*60}\n")
        
        print(f"Content Type: {content_type}")
        print(f"Context: {context or 'N/A'}")
        print(f"Length: {diff_result.get('original_length', '?')} → {diff_result.get('improved_length', '?')} chars\n")
        
        print("--- ORIGINAL ---")
        print(original[:500] + ("..." if len(original) > 500 else ""))
        print("\n--- IMPROVED ---")
        print(improved[:500] + ("..." if len(improved) > 500 else ""))
        
        print(f"\n{'─'*60}")
        print("DIFF SUMMARY")
        print(f"{'─'*60}")
        print(f"\n{diff_result.get('summary', 'N/A')}\n")
        
        print("Significant Changes:")
        for i, change in enumerate(diff_result.get("significant_changes", []), 1):
            print(f"  {i}. {change}")
        
        print(f"\n{'─'*60}")
        print("EXTRACTED LESSONS")
        print(f"{'─'*60}\n")
        
        lessons = combined.get("lessons", [])
        if not lessons:
            print("  No lessons extracted.")
        else:
            for lesson in lessons:
                conf = lesson.get("confidence", "?")
                glob = " 🌐" if lesson.get("global_candidate") else ""
                print(f"[{lesson.get('id', 'N/A')}] ({conf} confidence){glob}")
                print(f"  {lesson.get('lesson', 'N/A')}")
                print(f"  ✗ Avoid: {lesson.get('anti_pattern', 'N/A')}")
                print(f"  ✓ Instead: {lesson.get('positive_pattern', 'N/A')}")
                print()
        
        primitives = combined.get("candidate_primitives", [])
        if primitives:
            print(f"{'─'*60}")
            print("CANDIDATE PRIMITIVES")
            print(f"{'─'*60}\n")
            for prim in primitives:
                print(f"  \"{prim.get('text', '')}\"")
                print(f"    Type: {prim.get('type', '?')} | {prim.get('function', '?')}")
                print()
        
        if args.store:
            if combined.get("stored"):
                print(f"\n✓ Results stored successfully")
            elif combined.get("store_error"):
                print(f"\n✗ Storage failed: {combined['store_error']}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Analyze a feedback pair end-to-end")
    parser.add_argument("--id", type=int, required=True, help="Pair ID to analyze")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--store", action="store_true", 
                       help="Store lessons to semantic memory, primitives to voice library, update voice-lessons.md")
    # Keep old flag for backward compatibility
    parser.add_argument("--mark-analyzed", action="store_true", 
                       help="(deprecated: use --store) Mark pair as analyzed after processing")
    
    args = parser.parse_args()
    
    # Handle deprecated flag
    if args.mark_analyzed and not args.store:
        print("Warning: --mark-analyzed is deprecated, use --store instead", file=sys.stderr)
    
    return analyze_pair(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
