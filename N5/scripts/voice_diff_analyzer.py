#!/usr/bin/env python3
"""
Voice Diff Analyzer - Categorize changes between original and improved text.

Usage:
  python3 N5/scripts/voice_diff_analyzer.py analyze \
    --original "text" --improved "text" [--output json|text]
  
  python3 N5/scripts/voice_diff_analyzer.py analyze-pair --id 5 [--output json|text]
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

import requests

DB_PATH = Path(__file__).parent.parent / "data" / "voice_library.db"

DIFF_PROMPT = """Analyze the differences between these two texts. The ORIGINAL was written by an AI assistant, and the IMPROVED version was edited by V (the human).

ORIGINAL:
{original}

IMPROVED:
{improved}

Categorize all changes into these categories:
- word_choice: Different vocabulary, register, word substitutions
- sentence_structure: Length, complexity, rhythm changes
- tone: Formal ↔ casual, warm ↔ direct shifts
- directness: Hedging removed, passive → active voice
- specificity: Vague → concrete, generic → particular
- length: Overall trimming or expansion
- opening_closing: Hook changes, CTA changes, first/last line changes
- structure: Reordering, section changes, paragraph reorganization

For each category that has changes, provide specific examples of what changed.

Respond with ONLY valid JSON in this exact format:
{{
  "categories": {{
    "word_choice": ["specific change 1", "specific change 2"],
    "sentence_structure": [],
    "tone": [],
    "directness": [],
    "specificity": [],
    "length": [],
    "opening_closing": [],
    "structure": []
  }},
  "significant_changes": [
    "Most notable change 1",
    "Most notable change 2",
    "Most notable change 3"
  ],
  "original_length": {orig_len},
  "improved_length": {improved_len},
  "summary": "One sentence summary of the overall transformation"
}}

Include only categories that have actual changes (non-empty arrays). The significant_changes should be the 3-5 most important transformations."""


def analyze_with_llm(original: str, improved: str) -> dict:
    """Call /zo/ask to analyze the diff."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    prompt = DIFF_PROMPT.format(
        original=original,
        improved=improved,
        orig_len=len(original),
        improved_len=len(improved)
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
    
    # Parse JSON from response (handle markdown code blocks)
    if "```json" in output:
        output = output.split("```json")[1].split("```")[0].strip()
    elif "```" in output:
        output = output.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        # Return raw output in error format
        return {
            "error": f"Failed to parse JSON: {e}",
            "raw_output": output,
            "original_length": len(original),
            "improved_length": len(improved)
        }


def analyze(args):
    """Analyze original vs improved text."""
    result = analyze_with_llm(args.original, args.improved)
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        # Text format
        if "error" in result:
            print(f"Error: {result['error']}")
            print(f"Raw: {result.get('raw_output', '')[:500]}")
            return 1
        
        print("=== DIFF ANALYSIS ===\n")
        print(f"Length: {result.get('original_length', '?')} → {result.get('improved_length', '?')} chars")
        print(f"\nSummary: {result.get('summary', 'N/A')}\n")
        
        print("--- Categories ---")
        categories = result.get("categories", {})
        for cat, changes in categories.items():
            if changes:
                print(f"\n{cat.upper()}:")
                for change in changes:
                    print(f"  • {change}")
        
        print("\n--- Significant Changes ---")
        for i, change in enumerate(result.get("significant_changes", []), 1):
            print(f"  {i}. {change}")
    
    return 0


def analyze_pair(args):
    """Analyze a pair from the database by ID."""
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
    
    result = analyze_with_llm(row["original_text"], row["improved_text"])
    
    # Add metadata
    result["pair_id"] = args.id
    result["content_type"] = row["content_type"]
    result["context"] = row["context"]
    
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"=== DIFF ANALYSIS (Pair #{args.id}) ===\n")
        print(f"Content Type: {row['content_type']}")
        print(f"Context: {row['context'] or 'N/A'}")
        print(f"Length: {result.get('original_length', '?')} → {result.get('improved_length', '?')} chars")
        print(f"\nSummary: {result.get('summary', 'N/A')}\n")
        
        print("--- Categories ---")
        categories = result.get("categories", {})
        for cat, changes in categories.items():
            if changes:
                print(f"\n{cat.upper()}:")
                for change in changes:
                    print(f"  • {change}")
        
        print("\n--- Significant Changes ---")
        for i, change in enumerate(result.get("significant_changes", []), 1):
            print(f"  {i}. {change}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Analyze diffs between original and improved text")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze original vs improved text")
    analyze_parser.add_argument("--original", required=True, help="Original text")
    analyze_parser.add_argument("--improved", required=True, help="Improved text")
    analyze_parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    
    # analyze-pair command
    pair_parser = subparsers.add_parser("analyze-pair", help="Analyze a pair from database")
    pair_parser.add_argument("--id", type=int, required=True, help="Pair ID")
    pair_parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        return analyze(args)
    elif args.command == "analyze-pair":
        return analyze_pair(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
