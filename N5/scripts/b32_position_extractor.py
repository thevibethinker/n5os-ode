#!/usr/bin/env python3
"""
B32 Position Extractor

Extracts worldview position candidates from B32 Thought Provoking Ideas blocks.
Outputs to position_candidates.jsonl for triage.

Usage:
    python3 b32_position_extractor.py scan [--limit N] [--since YYYY-MM-DD]
    python3 b32_position_extractor.py extract <b32_file>
    python3 b32_position_extractor.py list-pending
    python3 b32_position_extractor.py stats

Workflow:
    1. scan: Find B32 files and extract candidates
    2. Triage via Position Triage prompt
    3. Approved candidates → positions.py add
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess

# Paths
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
CANDIDATES_FILE = Path("/home/workspace/N5/data/position_candidates.jsonl")
EXTRACTION_PROMPT = Path("/home/workspace/N5/prompts/extract_positions_from_b32.md")
PROCESSED_LOG = Path("/home/workspace/N5/data/b32_processed.jsonl")

def find_b32_files(since: str | None = None, limit: int | None = None) -> list[Path]:
    """Find all B32 files in the meetings directory."""
    b32_files = []
    
    for b32_path in MEETINGS_DIR.rglob("*B32*.md"):
        # Skip if already processed
        if is_processed(b32_path):
            continue
            
        # Apply date filter if specified
        if since:
            # Extract date from path (Week-of-YYYY-MM-DD or YYYY-MM-DD_meeting)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(b32_path))
            if date_match:
                file_date = date_match.group(1)
                if file_date < since:
                    continue
        
        b32_files.append(b32_path)
    
    # Sort by date (newest first) and apply limit
    b32_files.sort(key=lambda p: str(p), reverse=True)
    if limit:
        b32_files = b32_files[:limit]
    
    return b32_files


def is_processed(b32_path: Path) -> bool:
    """Check if a B32 file has already been processed."""
    if not PROCESSED_LOG.exists():
        return False
    
    with open(PROCESSED_LOG) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("file") == str(b32_path):
                    return True
            except json.JSONDecodeError:
                continue
    
    return False


def mark_processed(b32_path: Path, candidate_count: int):
    """Mark a B32 file as processed."""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "file": str(b32_path),
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "candidate_count": candidate_count
    }
    
    with open(PROCESSED_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def extract_meeting_id(b32_path: Path) -> str:
    """Extract meeting identifier from B32 path."""
    # Look for date_name pattern in parent directories
    for parent in b32_path.parents:
        match = re.search(r'(\d{4}-\d{2}-\d{2})[-_](.+?)(?:_\[.\])?$', parent.name)
        if match:
            return f"{match.group(1)}_{match.group(2)}"
    
    # Fallback to parent directory name
    return b32_path.parent.name


def extract_positions_llm(b32_content: str, meeting_id: str) -> list[dict]:
    """Use LLM to extract position candidates from B32 content."""
    # Load extraction prompt
    prompt_template = EXTRACTION_PROMPT.read_text()
    
    # Build the full prompt
    prompt = f"""You are extracting worldview positions from a B32 block.

{prompt_template}

---

## B32 Content to Analyze:

{b32_content}

---

Extract all qualifying positions as a JSON array. If none qualify, return [].
Return ONLY the JSON array, no markdown fences, no explanation.
"""
    
    # Call the /zo/ask API
    import requests
    
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print("Error: ZO_CLIENT_IDENTITY_TOKEN not set", file=sys.stderr)
        return []
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=120
        )
        
        result = response.json()
        output = result.get("output", "[]")
        
        # Parse JSON from response (handle potential markdown fences)
        output = output.strip()
        if output.startswith("```"):
            # Remove markdown code fences
            lines = output.split("\n")
            output = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        
        try:
            candidates = json.loads(output)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {output[:200]}...", file=sys.stderr)
            return []
        
        if not isinstance(candidates, list):
            return []
        
        # Add metadata to each candidate
        for i, cand in enumerate(candidates):
            cand["id"] = f"cand_{datetime.now().strftime('%Y%m%d')}_{meeting_id}_{i+1:03d}"
            cand["source_meeting"] = meeting_id
            cand["extracted_at"] = datetime.now(timezone.utc).isoformat()
            cand["status"] = "pending"
        
        return candidates
        
    except Exception as e:
        print(f"Error calling LLM: {e}", file=sys.stderr)
        return []


def append_candidates(candidates: list[dict]):
    """Append candidates to the JSONL file."""
    CANDIDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CANDIDATES_FILE, "a") as f:
        for cand in candidates:
            f.write(json.dumps(cand) + "\n")


def load_candidates(status_filter: str | None = None) -> list[dict]:
    """Load all candidates from JSONL file."""
    if not CANDIDATES_FILE.exists():
        return []
    
    candidates = []
    with open(CANDIDATES_FILE) as f:
        for line in f:
            try:
                cand = json.loads(line.strip())
                if status_filter is None or cand.get("status") == status_filter:
                    candidates.append(cand)
            except json.JSONDecodeError:
                continue
    
    return candidates


def cmd_scan(args):
    """Scan for B32 files and extract candidates."""
    b32_files = find_b32_files(since=args.since, limit=args.limit)
    
    if not b32_files:
        print("No unprocessed B32 files found.")
        return
    
    print(f"Found {len(b32_files)} B32 files to process")
    
    total_candidates = 0
    for b32_path in b32_files:
        print(f"\nProcessing: {b32_path.name}")
        
        content = b32_path.read_text()
        meeting_id = extract_meeting_id(b32_path)
        
        candidates = extract_positions_llm(content, meeting_id)
        
        if candidates:
            append_candidates(candidates)
            print(f"  → Extracted {len(candidates)} candidates")
            total_candidates += len(candidates)
        else:
            print(f"  → No candidates extracted")
        
        mark_processed(b32_path, len(candidates))
    
    print(f"\n✓ Total: {total_candidates} candidates extracted from {len(b32_files)} files")
    print(f"  Candidates saved to: {CANDIDATES_FILE}")


def cmd_extract(args):
    """Extract candidates from a single B32 file."""
    b32_path = Path(args.file)
    
    if not b32_path.exists():
        print(f"Error: File not found: {b32_path}", file=sys.stderr)
        sys.exit(1)
    
    content = b32_path.read_text()
    meeting_id = extract_meeting_id(b32_path)
    
    print(f"Extracting from: {b32_path.name}")
    candidates = extract_positions_llm(content, meeting_id)
    
    if candidates:
        append_candidates(candidates)
        print(f"✓ Extracted {len(candidates)} candidates")
        for cand in candidates:
            # Handle v2 format with insight field
            display_text = cand.get('insight', cand.get('claim', 'No content'))[:80]
            print(f"  - [{cand['classification']}] {display_text}...")
    else:
        print("No candidates extracted")


def cmd_list_pending(args):
    """List pending candidates for triage."""
    candidates = load_candidates(status_filter="pending")
    
    if not candidates:
        print("No pending candidates.")
        return
    
    print(f"Pending candidates: {len(candidates)}\n")
    
    for cand in candidates:
        print(f"[{cand['id']}]")
        print(f"  Source: {cand['source_meeting']}")
        print(f"  Speaker: {cand.get('speaker', 'V')} | Stance: {cand.get('v_stance', 'endorsed')}")
        print(f"  Domain: {cand.get('domain', cand.get('domain_suggestion', 'unknown'))}")
        print(f"  Classification: {cand.get('classification', 'V_POSITION')}")
        print()
        
        # Handle v1 (claim only) vs v2 (full wisdom) format
        if 'insight' in cand:
            # v2 format - show full wisdom
            print(f"  INSIGHT:")
            for line in cand['insight'].split('. '):
                print(f"    {line.strip()}.")
            print()
            
            if cand.get('reasoning'):
                print(f"  REASONING (principle):")
                for line in cand['reasoning'].split('. '):
                    if line.strip():
                        print(f"    {line.strip()}.")
                print()
            
            if cand.get('stakes'):
                print(f"  STAKES:")
                for line in cand['stakes'].split('. '):
                    if line.strip():
                        print(f"    {line.strip()}.")
                print()
            
            if cand.get('conditions'):
                print(f"  CONDITIONS:")
                for line in cand['conditions'].split('. '):
                    if line.strip():
                        print(f"    {line.strip()}.")
                print()
        else:
            # v1 format - show claim (backward compat)
            print(f"  CLAIM (v1 - thin):")
            print(f"    {cand.get('claim', 'No claim')}")
            print()
            print(f"  ⚠️  This is a v1 candidate (too thin). Consider reprocessing.")
            print()
        
        if cand.get('source_excerpt'):
            excerpt = cand['source_excerpt'][:150] + "..." if len(cand.get('source_excerpt', '')) > 150 else cand.get('source_excerpt', '')
            print(f"  Source excerpt: \"{excerpt}\"")
        
        print("-" * 60)
        print()


def cmd_stats(args):
    """Show statistics about extracted candidates."""
    all_candidates = load_candidates()
    pending = [c for c in all_candidates if c.get("status") == "pending"]
    approved = [c for c in all_candidates if c.get("status") == "approved"]
    rejected = [c for c in all_candidates if c.get("status") == "rejected"]
    
    print("Position Candidate Statistics")
    print("=" * 40)
    print(f"Total candidates: {len(all_candidates)}")
    print(f"  Pending: {len(pending)}")
    print(f"  Approved: {len(approved)}")
    print(f"  Rejected: {len(rejected)}")
    
    if all_candidates:
        # Domain breakdown (support both old and new field names)
        domains = {}
        for c in all_candidates:
            d = c.get("domain") or c.get("domain_suggestion", "unknown")
            domains[d] = domains.get(d, 0) + 1
        
        print(f"\nBy domain:")
        for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"  {domain}: {count}")
        
        # Classification breakdown
        classifications = {}
        for c in all_candidates:
            cl = c.get("classification", "unknown")
            classifications[cl] = classifications.get(cl, 0) + 1
        
        print(f"\nBy classification:")
        for cl, count in sorted(classifications.items(), key=lambda x: -x[1]):
            print(f"  {cl}: {count}")


def cmd_mark(args):
    """Mark a candidate as approved or rejected."""
    candidates = load_candidates()
    
    found = False
    for c in candidates:
        if c["id"] == args.candidate_id:
            c["status"] = args.status
            found = True
            break
    
    if not found:
        print(f"Candidate not found: {args.candidate_id}", file=sys.stderr)
        sys.exit(1)
    
    # Rewrite the file
    with open(CANDIDATES_FILE, "w") as f:
        for c in candidates:
            f.write(json.dumps(c) + "\n")
    
    print(f"✓ Marked {args.candidate_id} as {args.status}")


def cmd_reprocess(args):
    """Clear processed log for specific meetings to allow re-extraction."""
    if not PROCESSED_LOG.exists():
        print("No processed log found.")
        return
    
    pattern = args.pattern if args.pattern else None
    
    # Read all entries
    entries = []
    cleared = []
    with open(PROCESSED_LOG) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if pattern and pattern in entry.get("file", ""):
                    cleared.append(entry)
                else:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    
    if not cleared:
        print(f"No entries matching pattern: {pattern}")
        return
    
    # Write back without cleared entries
    with open(PROCESSED_LOG, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Cleared {len(cleared)} entries from processed log:")
    for entry in cleared:
        print(f"  - {entry.get('file', 'unknown')}")
    print(f"\nThese B32 files can now be re-scanned with: python3 {sys.argv[0]} scan")


def cmd_reject_all_pending(args):
    """Reject all pending candidates (for bulk re-extraction)."""
    if not CANDIDATES_FILE.exists():
        print("No candidates file found.")
        return
    
    # Read all candidates
    all_candidates = []
    pending_count = 0
    with open(CANDIDATES_FILE) as f:
        for line in f:
            try:
                cand = json.loads(line.strip())
                if cand.get("status") == "pending":
                    cand["status"] = "rejected"
                    cand["rejection_reason"] = "v1_too_thin"
                    pending_count += 1
                all_candidates.append(cand)
            except json.JSONDecodeError:
                continue
    
    # Write back
    with open(CANDIDATES_FILE, "w") as f:
        for cand in all_candidates:
            f.write(json.dumps(cand) + "\n")
    
    print(f"✓ Rejected {pending_count} pending candidates (reason: v1_too_thin)")


def main():
    parser = argparse.ArgumentParser(
        description="Extract worldview positions from B32 blocks"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan B32 files and extract candidates")
    scan_parser.add_argument("--limit", type=int, help="Limit number of files to process")
    scan_parser.add_argument("--since", help="Only process files since date (YYYY-MM-DD)")
    scan_parser.set_defaults(func=cmd_scan)
    
    # extract command
    extract_parser = subparsers.add_parser("extract", help="Extract from a single B32 file")
    extract_parser.add_argument("file", help="Path to B32 file")
    extract_parser.set_defaults(func=cmd_extract)
    
    # list-pending command
    pending_parser = subparsers.add_parser("list-pending", help="List pending candidates")
    pending_parser.set_defaults(func=cmd_list_pending)
    
    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show extraction statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    # mark command
    mark_parser = subparsers.add_parser("mark", help="Mark a candidate as approved or rejected")
    mark_parser.add_argument("candidate_id", help="Candidate ID")
    mark_parser.add_argument("status", choices=["approved", "rejected"], help="New status")
    mark_parser.set_defaults(func=cmd_mark)
    
    # reprocess command
    reprocess_parser = subparsers.add_parser("reprocess", help="Clear processed log for specific meetings")
    reprocess_parser.add_argument("pattern", nargs="?", help="Pattern to match in file paths")
    reprocess_parser.set_defaults(func=cmd_reprocess)
    
    # reject-all command
    reject_all_parser = subparsers.add_parser("reject-all", help="Reject all pending candidates")
    reject_all_parser.set_defaults(func=cmd_reject_all_pending)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()







