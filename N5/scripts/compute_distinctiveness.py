#!/usr/bin/env python3
"""
Compute distinctiveness scores for voice primitives using Pangram API.

Distinctiveness = 1.0 - fraction_ai
- Score of 1.0 = completely human-sounding (highly distinctive)
- Score of 0.0 = completely AI-sounding (not distinctive)

Usage:
  python3 compute_distinctiveness.py score "Your text here"
  python3 compute_distinctiveness.py score-db [--limit N] [--min-length 10]
  python3 compute_distinctiveness.py batch --file candidates.jsonl
  
Per PLAN.md v2.0 Phase 1, Task 1.2
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Integrations" / "Pangram"))

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

# Constants
PANGRAM_API_URL = "https://text.api.pangram.com/v3"
DB_PATH = Path(__file__).parent.parent / "data" / "voice_library.db"
RATE_LIMIT_DELAY = 1.0  # seconds between API calls to respect rate limits
MIN_TEXT_LENGTH = 10  # minimum characters to score


def get_api_key() -> str:
    """Get Pangram API key from environment."""
    key = os.environ.get("PANGRAM_API_KEY")
    if not key:
        print("ERROR: PANGRAM_API_KEY environment variable not set")
        print("Set it in Zo Settings > Developers")
        sys.exit(1)
    return key


def compute_distinctiveness(text: str, api_key: str = None) -> dict:
    """
    Compute distinctiveness score for a piece of text.
    
    Returns:
        dict with keys:
        - distinctiveness: float 0.0-1.0 (1.0 = human, 0.0 = AI)
        - fraction_ai: float from Pangram
        - fraction_human: float from Pangram
        - error: str if failed, None otherwise
    """
    if not api_key:
        api_key = get_api_key()
    
    if len(text.strip()) < MIN_TEXT_LENGTH:
        return {
            "distinctiveness": None,
            "fraction_ai": None,
            "fraction_human": None,
            "error": f"Text too short (min {MIN_TEXT_LENGTH} chars)"
        }
    
    try:
        response = requests.post(
            PANGRAM_API_URL,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json"
            },
            json={"text": text},
            timeout=30
        )
        
        if response.status_code == 429:
            return {
                "distinctiveness": None,
                "fraction_ai": None,
                "fraction_human": None,
                "error": "Rate limited - try again later"
            }
        
        response.raise_for_status()
        data = response.json()
        
        fraction_ai = data.get("fraction_ai", data.get("fraction_ai_assisted_segments", 0))
        fraction_human = data.get("fraction_human", 1.0 - fraction_ai)
        
        return {
            "distinctiveness": round(1.0 - fraction_ai, 4),
            "fraction_ai": fraction_ai,
            "fraction_human": fraction_human,
            "error": None
        }
        
    except requests.exceptions.Timeout:
        return {
            "distinctiveness": None,
            "fraction_ai": None,
            "fraction_human": None,
            "error": "API timeout"
        }
    except requests.exceptions.RequestException as e:
        return {
            "distinctiveness": None,
            "fraction_ai": None,
            "fraction_human": None,
            "error": str(e)
        }


def score_single(text: str) -> None:
    """Score a single piece of text and print results."""
    print(f"Scoring text ({len(text)} chars)...")
    result = compute_distinctiveness(text)
    
    if result["error"]:
        print(f"ERROR: {result['error']}")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print(f"Distinctiveness: {result['distinctiveness']:.2%}")
    print(f"  (AI fraction: {result['fraction_ai']:.2%})")
    print(f"  (Human fraction: {result['fraction_human']:.2%})")
    print(f"{'='*50}")
    
    if result['distinctiveness'] >= 0.7:
        print("✓ HIGH distinctiveness - good candidate for Voice Library")
    elif result['distinctiveness'] >= 0.4:
        print("~ MEDIUM distinctiveness - may need review")
    else:
        print("✗ LOW distinctiveness - likely too generic/AI-sounding")


def score_database(limit: int = None, min_length: int = MIN_TEXT_LENGTH) -> None:
    """Score unscored primitives in the database."""
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get unscored primitives
    query = """
        SELECT id, exact_text 
        FROM primitives 
        WHERE distinctiveness_score IS NULL
          AND length(exact_text) >= ?
        ORDER BY created_at DESC
    """
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query, (min_length,))
    rows = cursor.fetchall()
    
    if not rows:
        print("No unscored primitives found.")
        conn.close()
        return
    
    print(f"Found {len(rows)} primitives to score...")
    api_key = get_api_key()
    
    scored = 0
    errors = 0
    
    for row in rows:
        primitive_id = row["id"]
        text = row["exact_text"]
        
        print(f"  Scoring {primitive_id}...", end=" ")
        result = compute_distinctiveness(text, api_key)
        
        if result["error"]:
            print(f"ERROR: {result['error']}")
            errors += 1
        else:
            cursor.execute(
                "UPDATE primitives SET distinctiveness_score = ? WHERE id = ?",
                (result["distinctiveness"], primitive_id)
            )
            conn.commit()
            print(f"{result['distinctiveness']:.2%}")
            scored += 1
        
        # Rate limit protection
        time.sleep(RATE_LIMIT_DELAY)
    
    conn.close()
    print(f"\nComplete: {scored} scored, {errors} errors")


def score_batch(file_path: str) -> None:
    """Score texts from a JSONL file. Each line: {"id": "...", "text": "..."}"""
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    
    api_key = get_api_key()
    results = []
    
    with open(path) as f:
        lines = f.readlines()
    
    print(f"Scoring {len(lines)} items...")
    
    for i, line in enumerate(lines):
        try:
            item = json.loads(line.strip())
            item_id = item.get("id", f"item-{i}")
            text = item.get("text", "")
            
            result = compute_distinctiveness(text, api_key)
            result["id"] = item_id
            results.append(result)
            
            status = f"{result['distinctiveness']:.2%}" if result["distinctiveness"] else result["error"]
            print(f"  {item_id}: {status}")
            
            time.sleep(RATE_LIMIT_DELAY)
            
        except json.JSONDecodeError:
            print(f"  Line {i}: Invalid JSON")
            continue
    
    # Output results
    output_path = path.with_suffix(".scored.jsonl")
    with open(output_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    
    print(f"\nResults saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Compute distinctiveness scores using Pangram API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s score "The talent cliff isn't about skill—it's about options."
  %(prog)s score-db --limit 10
  %(prog)s batch --file candidates.jsonl
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # score command
    score_parser = subparsers.add_parser("score", help="Score a single text")
    score_parser.add_argument("text", help="Text to score")
    
    # score-db command
    db_parser = subparsers.add_parser("score-db", help="Score unscored primitives in database")
    db_parser.add_argument("--limit", type=int, help="Max primitives to score")
    db_parser.add_argument("--min-length", type=int, default=MIN_TEXT_LENGTH,
                          help=f"Minimum text length (default: {MIN_TEXT_LENGTH})")
    
    # batch command
    batch_parser = subparsers.add_parser("batch", help="Score texts from JSONL file")
    batch_parser.add_argument("--file", required=True, help="Path to JSONL file")
    
    args = parser.parse_args()
    
    if args.command == "score":
        score_single(args.text)
    elif args.command == "score-db":
        score_database(args.limit, args.min_length)
    elif args.command == "batch":
        score_batch(args.file)


if __name__ == "__main__":
    main()



