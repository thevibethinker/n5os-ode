#!/usr/bin/env python3
"""
Tension Detector - Find contradictions between positions.

Uses semantic search to find po
[truncated]
lar)
- Logs tensions to _tensions.jsonl with resolution_status

Usage:
    python3 tension_detector.py scan                    # Scan all positions for tensions
    python3 tension_detector.py check <position_id>     # Check one position against others
    python3 tension_detector.py list                    # List unresolved tensions
    python3 tension_detector.py resolve <tension_id>    # Mark tension as resolved
    python3 tension_detector.py stats                   # Show tension statistics
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, "/home/workspace")

# Paths
POSITIONS_DB = Path("/home/workspace/N5/data/positions.db")
TENSIONS_FILE = Path("/home/workspace/Knowledge/positions/_tensions.jsonl")
BRAIN_DB = Path("/home/workspace/N5/cognition/brain.db")

# Thresholds
SEMANTIC_SIMILARITY_THRESHOLD = 0.35  # Positions must be related
TENSION_CONFIDENCE_THRESHOLD = 0.6    # LLM confidence for contradiction


def get_all_positions() -> list[dict]:
    """Load all positions from DB."""
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT id, domain, title, insight, reasoning, stakes, conditions
        FROM positions
        ORDER BY domain, id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_position(position_id: str) -> Optional[dict]:
    """Load a single position."""
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT id, domain, title, insight, reasoning, stakes, conditions
        FROM positions WHERE id = ?
    """, (position_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def load_tensions() -> list[dict]:
    """Load existing tensions."""
    if not TENSIONS_FILE.exists():
        return []
    tensions = []
    with open(TENSIONS_FILE) as f:
        for line in f:
            if line.strip():
                tensions.append(json.loads(line.strip()))
    return tensions


def save_tension(tension: dict):
    """Append a tension to the file."""
    with open(TENSIONS_FILE, "a") as f:
        f.write(json.dumps(tension) + "\n")


def tension_exists(pos1_id: str, pos2_id: str) -> bool:
    """Check if tension between these positions already logged."""
    tensions = load_tensions()
    for t in tensions:
        pair = {t.get("position_1_id"), t.get("position_2_id")}
        if pair == {pos1_id, pos2_id}:
            return True
    return False


def find_semantically_similar(position: dict, all_positions: list[dict], threshold: float = 0.35) -> list[dict]:
    """Find positions that are semantically related (potential tension candidates)."""
    from N5.cognition.n5_memory_client import N5MemoryClient
    
    client = N5MemoryClient()
    query = f"{position.get('insight', '')} {position.get('reasoning', '')}"
    
    # Search brain.db for related positions
    results = client.search(query, limit=20, tag_filter="position")
    
    similar = []
    for r in results:
        # Extract position ID from path (positions://domain/id)
        path = r.get("path", "")
        if not path.startswith("positions://"):
            continue
        
        pos_id = path.split("/")[-1]
        
        # Skip self
        if pos_id == position["id"]:
            continue
            
        # Check score threshold
        if r.get("score", 0) >= threshold:
            # Find full position data
            for p in all_positions:
                if p["id"] == pos_id:
                    similar.append({**p, "_similarity_score": r.get("score", 0)})
                    break
    
    return similar


def detect_tension_llm(pos1: dict, pos2: dict) -> dict:
    """Use LLM to detect if two positions are in tension."""
    import requests
    import time
    
    prompt = f"""Analyze whether these two positions are in TENSION (contradiction, conflict, or incompatibility).

POSITION A:
Domain: {pos1.get('domain', 'unknown')}
Insight: {pos1.get('insight', '')}
Reasoning: {pos1.get('reasoning', '')}

POSITION B:
Domain: {pos2.get('domain', 'unknown')}
Insight: {pos2.get('insight', '')}
Reasoning: {pos2.get('reasoning', '')}

Respond with a JSON object:
{{
  "is_tension": true/false,
  "confidence": 0.0-1.0,
  "tension_type": "contradicts" | "qualifies" | "supersedes" | "none",
  "explanation": "Brief explanation of the tension or why there is none",
  "synthesis_hint": "If tension exists, how might these be reconciled?"
}}

Only mark is_tension=true if there is a genuine logical conflict or incompatibility.
Positions can both be true without tension if they apply to different contexts.
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", ""),
                    "content-type": "application/json"
                },
                json={
                    "input": prompt,
                    "output_format": {
                        "type": "object",
                        "properties": {
                            "is_tension": {"type": "boolean"},
                            "confidence": {"type": "number"},
                            "tension_type": {"type": "string"},
                            "explanation": {"type": "string"},
                            "synthesis_hint": {"type": "string"}
                        },
                        "required": ["is_tension", "confidence", "tension_type", "explanation"]
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("output", {})
            elif response.status_code == 429:
                time.sleep(5 * (attempt + 1))
            else:
                return {"is_tension": False, "confidence": 0, "tension_type": "error", "explanation": f"API error: {response.status_code}"}
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            return {"is_tension": False, "confidence": 0, "tension_type": "timeout", "explanation": "API timeout after retries"}
        except Exception as e:
            return {"is_tension": False, "confidence": 0, "tension_type": "error", "explanation": str(e)}
    
    return {"is_tension": False, "confidence": 0, "tension_type": "error", "explanation": "Max retries reached"}


def cmd_scan(args):
    """Scan all positions for tensions."""
    positions = get_all_positions()
    print(f"Scanning {len(positions)} positions for tensions...\n")
    
    new_tensions = 0
    checked = 0
    
    for i, pos1 in enumerate(positions):
        if args.limit and checked >= args.limit:
            break
            
        # Find semantically similar positions
        similar = find_semantically_similar(pos1, positions)
        
        for pos2 in similar:
            # Skip if already checked
            if tension_exists(pos1["id"], pos2["id"]):
                continue
            
            # Skip if same position
            if pos1["id"] >= pos2["id"]:  # Only check each pair once
                continue
            
            checked += 1
            print(f"Checking: {pos1['id'][:40]} vs {pos2['id'][:40]}...", end=" ")
            
            # Use LLM to detect tension
            result = detect_tension_llm(pos1, pos2)
            
            if result.get("is_tension") and result.get("confidence", 0) >= TENSION_CONFIDENCE_THRESHOLD:
                tension = {
                    "id": f"tension_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{new_tensions:03d}",
                    "position_1_id": pos1["id"],
                    "position_2_id": pos2["id"],
                    "tension_type": result.get("tension_type", "unknown"),
                    "confidence": result.get("confidence", 0),
                    "explanation": result.get("explanation", ""),
                    "synthesis_hint": result.get("synthesis_hint", ""),
                    "resolution_status": "unresolved",
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                }
                save_tension(tension)
                new_tensions += 1
                print(f"⚡ TENSION ({result.get('tension_type')})")
            else:
                print("✓ compatible")
            
            if args.limit and checked >= args.limit:
                break
    
    print(f"\n{'='*50}")
    print(f"✓ Checked {checked} position pairs")
    print(f"⚡ Found {new_tensions} new tensions")


def cmd_check(args):
    """Check one position against others."""
    position = get_position(args.position_id)
    if not position:
        print(f"Position not found: {args.position_id}")
        return
    
    all_positions = get_all_positions()
    similar = find_semantically_similar(position, all_positions)
    
    print(f"Checking position: {position['id']}")
    print(f"Insight: {position.get('insight', '')[:100]}...\n")
    print(f"Found {len(similar)} semantically related positions\n")
    
    tensions_found = 0
    for pos2 in similar:
        if tension_exists(position["id"], pos2["id"]):
            print(f"  [already checked] {pos2['id'][:50]}")
            continue
        
        print(f"  Checking: {pos2['id'][:50]}...", end=" ")
        result = detect_tension_llm(position, pos2)
        
        if result.get("is_tension") and result.get("confidence", 0) >= TENSION_CONFIDENCE_THRESHOLD:
            tension = {
                "id": f"tension_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{tensions_found:03d}",
                "position_1_id": position["id"],
                "position_2_id": pos2["id"],
                "tension_type": result.get("tension_type", "unknown"),
                "confidence": result.get("confidence", 0),
                "explanation": result.get("explanation", ""),
                "synthesis_hint": result.get("synthesis_hint", ""),
                "resolution_status": "unresolved",
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }
            save_tension(tension)
            tensions_found += 1
            print(f"⚡ TENSION")
            print(f"    Type: {result.get('tension_type')}")
            print(f"    Explanation: {result.get('explanation', '')[:100]}")
        else:
            print("✓")
    
    print(f"\n⚡ Found {tensions_found} new tensions")


def cmd_list(args):
    """List tensions."""
    tensions = load_tensions()
    
    if args.unresolved:
        tensions = [t for t in tensions if t.get("resolution_status") == "unresolved"]
    
    if not tensions:
        print("No tensions found." if not args.unresolved else "No unresolved tensions.")
        return
    
    print(f"{'Unresolved t' if args.unresolved else 'T'}ensions: {len(tensions)}\n")
    
    for t in tensions:
        status_icon = "⚡" if t.get("resolution_status") == "unresolved" else "✓"
        print(f"{status_icon} [{t.get('id', 'unknown')}]")
        print(f"  Type: {t.get('tension_type', 'unknown')} (confidence: {t.get('confidence', 0):.0%})")
        print(f"  Position 1: {t.get('position_1_id', '')[:50]}")
        print(f"  Position 2: {t.get('position_2_id', '')[:50]}")
        print(f"  Explanation: {t.get('explanation', '')[:100]}")
        if t.get("synthesis_hint"):
            print(f"  Synthesis hint: {t.get('synthesis_hint', '')[:100]}")
        print(f"  Status: {t.get('resolution_status', 'unknown')}")
        print()


def cmd_resolve(args):
    """Mark a tension as resolved."""
    tensions = load_tensions()
    updated = False
    
    for t in tensions:
        if t.get("id") == args.tension_id:
            t["resolution_status"] = "resolved"
            t["resolved_at"] = datetime.now(timezone.utc).isoformat()
            t["resolution_note"] = args.note or ""
            updated = True
            break
    
    if not updated:
        print(f"Tension not found: {args.tension_id}")
        return
    
    # Rewrite file
    with open(TENSIONS_FILE, "w") as f:
        for t in tensions:
            f.write(json.dumps(t) + "\n")
    
    print(f"✓ Marked tension {args.tension_id} as resolved")


def cmd_stats(args):
    """Show tension statistics."""
    tensions = load_tensions()
    
    if not tensions:
        print("No tensions recorded yet.")
        return
    
    unresolved = [t for t in tensions if t.get("resolution_status") == "unresolved"]
    resolved = [t for t in tensions if t.get("resolution_status") == "resolved"]
    
    print("Tension Statistics")
    print("=" * 40)
    print(f"Total tensions: {len(tensions)}")
    print(f"  Unresolved: {len(unresolved)}")
    print(f"  Resolved: {len(resolved)}")
    
    # By type
    types = {}
    for t in tensions:
        tt = t.get("tension_type", "unknown")
        types[tt] = types.get(tt, 0) + 1
    
    print(f"\nBy type:")
    for tt, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {tt}: {count}")
    
    # By domain
    positions = {p["id"]: p for p in get_all_positions()}
    domains = {}
    for t in tensions:
        p1 = positions.get(t.get("position_1_id"), {})
        p2 = positions.get(t.get("position_2_id"), {})
        d1 = p1.get("domain", "unknown")
        d2 = p2.get("domain", "unknown")
        pair = tuple(sorted([d1, d2]))
        domains[pair] = domains.get(pair, 0) + 1
    
    print(f"\nBy domain pair:")
    for pair, count in sorted(domains.items(), key=lambda x: -x[1])[:5]:
        print(f"  {pair[0]} ↔ {pair[1]}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Detect tensions between positions")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan all positions for tensions")
    scan_parser.add_argument("--limit", type=int, help="Max pairs to check")
    scan_parser.set_defaults(func=cmd_scan)
    
    # check
    check_parser = subparsers.add_parser("check", help="Check one position against others")
    check_parser.add_argument("position_id", help="Position ID to check")
    check_parser.set_defaults(func=cmd_check)
    
    # list
    list_parser = subparsers.add_parser("list", help="List tensions")
    list_parser.add_argument("--unresolved", "-u", action="store_true", help="Only unresolved")
    list_parser.set_defaults(func=cmd_list)
    
    # resolve
    resolve_parser = subparsers.add_parser("resolve", help="Mark tension as resolved")
    resolve_parser.add_argument("tension_id", help="Tension ID to resolve")
    resolve_parser.add_argument("--note", "-n", help="Resolution note")
    resolve_parser.set_defaults(func=cmd_resolve)
    
    # stats
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

