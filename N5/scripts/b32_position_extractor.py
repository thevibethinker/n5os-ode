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
    python3 b32_position_extractor.py review-sheet-generate [--status pending|approved|all] [--limit N] [--output PATH]
    python3 b32_position_extractor.py review-sheet-ingest <review_sheet.md> [--dry-run]
    python3 b32_position_extractor.py promote-reviewed [--skip-dedup]

Workflow:
    1. scan: Find B32 files and extract candidates
    2. Triage via Position Triage prompt
    3. Approved candidates → positions.py add
    4. HITL review sheets: accept/amend/reject/hold; amend overwrites insight (traceably) and recomputes reasoning/stakes/conditions
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from N5.lib.paths import N5_DATA_DIR, N5_ROOT, MEETINGS_DIR


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_review_dir():
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)


def _next_review_sheet_path(date_str: str | None = None) -> Path:
    _ensure_review_dir()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    i = 1
    while True:
        p = REVIEW_DIR / f"{date_str}_positions-review_batch-{i:03d}.md"
        if not p.exists():
            return p
        i += 1


def _candidate_display_insight(cand: dict) -> str:
    return (cand.get("insight_amended") or cand.get("insight") or cand.get("claim") or "").strip()


def _build_review_sheet(candidates: list[dict], batch_path: Path) -> str:
    header = (
        f"# Positions Review Sheet\n\n"
        f"Batch: {batch_path.name}\n\n"
        "Decision grammar (required):\n"
        "- Decision: accept | amend | reject | hold\n"
        "- If amend: provide Amended insight (multiline allowed)\n\n"
        "Read-only fields (do not edit conceptually): domain, classification, speaker, source_excerpt\n\n"
        "---\n\n"
    )
    blocks = [header]
    for cand in candidates:
        cid = cand.get("id", "")
        blocks.append(f"## Candidate\n\nCandidate ID: {cid}\n")
        blocks.append(f"Current status: {cand.get('status','')}\n")
        blocks.append(f"Source meeting: {cand.get('source_meeting','')}\n")
        blocks.append(f"Speaker: {cand.get('speaker','V')}\n")
        blocks.append(f"Domain: {cand.get('domain') or cand.get('domain_suggestion','unknown')}\n")
        blocks.append(f"Classification: {cand.get('classification','V_POSITION')}\n")
        blocks.append("\n### Extracted insight (original)\n\n")
        blocks.append((cand.get("insight") or cand.get("claim") or "(missing)").strip() + "\n\n")
        if cand.get("insight_amended"):
            blocks.append("### Amended insight (current)\n\n")
            blocks.append(cand.get("insight_amended", "").strip() + "\n\n")

        if cand.get("reasoning"):
            blocks.append("### Reasoning\n\n" + cand.get("reasoning", "").strip() + "\n\n")
        if cand.get("stakes"):
            blocks.append("### Stakes\n\n" + cand.get("stakes", "").strip() + "\n\n")
        if cand.get("conditions"):
            blocks.append("### Conditions\n\n" + cand.get("conditions", "").strip() + "\n\n")

        if cand.get("source_excerpt"):
            blocks.append("### Source excerpt\n\n")
            blocks.append(cand.get("source_excerpt", "").strip() + "\n\n")

        blocks.append("### Your decision\n\n")
        blocks.append("Decision: hold\n\n")
        blocks.append("Amended insight:\n\n")
        blocks.append("(only if Decision: amend)\n\n")
        blocks.append("Attribution: \n\n")
        blocks.append("Credit: \n\n")
        blocks.append("Notes: \n\n")
        blocks.append("---\n\n")

    return "".join(blocks)


def _parse_review_sheet(md: str) -> list[dict]:
    """Parse review sheet markdown into a list of decisions.

    Returns list of:
      {candidate_id, decision, amended_insight?, attribution?, credit?, notes?}
    """
    blocks = re.split(r"(?m)^##\s+Candidate\s*$", md)
    out: list[dict] = []
    labels = {"Amended insight", "Attribution", "Credit", "Notes"}
    for block in blocks[1:]:
        lines = block.splitlines()

        candidate_id = None
        decision = None
        buf: dict[str, list[str]] = {k: [] for k in labels}
        current: str | None = None

        def _flush_line(line: str):
            nonlocal current
            m = re.match(r"^([A-Za-z ]+):\s*(.*)$", line)
            if not m:
                if current in labels:
                    buf[current].append(line)
                return
            key = m.group(1).strip()
            val = m.group(2)

            if key == "Candidate ID":
                nonlocal candidate_id
                candidate_id = val.strip()
                return candidate_id
            return None

        for raw in lines:
            line = raw.rstrip("\n")
            if line.strip() == "---":
                current = None
                continue
            m = re.match(r"^Candidate ID:\s*(.+?)\s*$", line)
            if m:
                candidate_id = m.group(1).strip().rstrip("\\")
                current = None
                continue
            m = re.match(r"^Decision:\s*(accept|amend|reject|hold)\s*$", line)
            if m:
                decision = m.group(1).strip()
                current = None
                continue
            m = re.match(r"^(Amended insight|Attribution|Credit|Notes):\s*(.*)$", line)
            if m:
                current = m.group(1)
                rest = m.group(2)
                if rest.strip():
                    buf[current].append(rest)
                continue

            if current in labels:
                buf[current].append(line)

        if not candidate_id:
            continue
        if not decision:
            raise ValueError(f"Missing or invalid Decision for {candidate_id}")

        def join_field(k: str) -> str | None:
            txt = "\n".join(buf[k]).strip()
            return txt if txt else None

        amended = join_field("Amended insight")
        attribution = join_field("Attribution")
        credit = join_field("Credit")
        notes = join_field("Notes")

        if decision == "amend" and not amended:
            raise ValueError(f"Decision=amend requires 'Amended insight' for {candidate_id}")

        out.append({
            "candidate_id": candidate_id,
            "decision": decision,
            "amended_insight": amended,
            "attribution": attribution,
            "credit": credit,
            "notes": notes,
        })

    return out


def _recompute_wisdom_from_context(*, source_excerpt: str, speaker: str, insight_final: str) -> dict:
    """Recompute reasoning/stakes/conditions using original context + amended insight.

    This keeps domain/classification/speaker/source_excerpt read-only; only returns new wisdom fields.
    """
    import requests

    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")

    prompt = f"""You are helping refine a position candidate.

You will be given:
1) a read-only SOURCE EXCERPT (original context)
2) a FINAL INSIGHT (may be amended by the human)

Your job is to compute ONLY these fields as JSON:
- reasoning (transferable principle; mechanism-level; not anchored to the anecdote)
- stakes (implications / why it matters)
- conditions (boundary conditions / when it applies or breaks)

Constraints:
- Do NOT change or restate domain/classification/speaker/source_excerpt.
- Use the SOURCE EXCERPT only as evidence/context.
- Keep each field concise but complete (3-8 sentences each).

Return ONLY JSON with keys: reasoning, stakes, conditions.

---
SPEAKER (read-only): {speaker}

SOURCE EXCERPT (read-only):
{source_excerpt}

FINAL INSIGHT:
{insight_final}
"""

    resp = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={"authorization": token, "content-type": "application/json"},
        json={"input": prompt},
        timeout=120,
    )
    data = resp.json()
    out = (data.get("output") or "{}").strip()
    if out.startswith("```"):
        lines = out.split("\n")
        out = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    
    # Extract first valid JSON object from output (in case there's trailing text)
    obj = None
    for line in out.split("\n"):
        try:
            obj = json.loads(line.strip())
            if isinstance(obj, dict):
                break
        except json.JSONDecodeError:
            continue
    
    if obj is None:
        # Try parsing the whole thing one more time
        obj = json.loads(out)
    
    for k in ("reasoning", "stakes", "conditions"):
        if k not in obj:
            raise ValueError(f"Missing key '{k}' in recompute output")
    return {"reasoning": obj["reasoning"], "stakes": obj["stakes"], "conditions": obj["conditions"]}


def _apply_review_decisions(
    candidates: list[dict],
    decisions: list[dict],
    batch_path: Path,
    *,
    dry_run: bool,
    recompute_on_amend: bool = True,
    recompute_fn=_recompute_wisdom_from_context,
) -> tuple[list[dict], dict]:
    by_id = {c.get("id"): c for c in candidates}
    stats = {"updated": 0, "accept": 0, "amend": 0, "reject": 0, "hold": 0, "missing": 0}

    for d in decisions:
        cid = d["candidate_id"]
        cand = by_id.get(cid)
        if not cand:
            stats["missing"] += 1
            continue

        decision = d["decision"]
        stats[decision] += 1

        review_obj = cand.get("review") or {}
        review_obj.update({
            "decision": decision,
            "reviewed_at": _utc_now_iso(),
            "review_batch": str(batch_path),
        })
        if d.get("notes"):
            review_obj["notes"] = d["notes"]
        if d.get("attribution"):
            review_obj["attribution"] = d["attribution"]
        if d.get("credit"):
            review_obj["credit"] = d["credit"]
        cand["review"] = review_obj

        if decision == "reject":
            cand["status"] = "rejected"
        elif decision in ("accept", "amend"):
            # Keep existing status if already approved/promoted; otherwise mark approved to enable promotion
            if cand.get("status") in (None, "pending"):
                cand["status"] = "approved"
        else:
            # hold: keep status as-is
            pass

        if decision == "amend":
            amended = d.get("amended_insight")
            # overwrite semantics: store amended insight separately, keep original insight intact
            if amended:
                cand["insight_amended"] = amended.strip()
            insight_final = _candidate_display_insight(cand)
            if recompute_on_amend and insight_final:
                # recompute reasoning/stakes/conditions from original context + amended insight
                source_excerpt = (cand.get("source_excerpt") or "").strip()
                speaker = (cand.get("speaker") or "V").strip()
                if source_excerpt:
                    if not dry_run:
                        wisdom = recompute_fn(source_excerpt=source_excerpt, speaker=speaker, insight_final=insight_final)
                        cand["reasoning"] = wisdom.get("reasoning")
                        cand["stakes"] = wisdom.get("stakes")
                        cand["conditions"] = wisdom.get("conditions")

        stats["updated"] += 1

    return candidates, stats

# Paths
REVIEW_DIR = N5_ROOT / "review" / "positions"
CANDIDATES_FILE = N5_DATA_DIR / "position_candidates.jsonl"
EXTRACTION_PROMPT = N5_ROOT / "prompts" / "extract_positions.md"
PROCESSED_LOG = N5_DATA_DIR / "b32_processed.jsonl"

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
    """Mark a B32 file as processed (with dedup check)."""
    # Skip if already processed (dedup)
    if is_processed(b32_path):
        return

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
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}", file=sys.stderr)
            print(f"First 200 chars: {output[:200]}...", file=sys.stderr)
            # Log full output to debug file
            debug_file = N5_DATA_DIR / "extraction_failures.jsonl"
            debug_file.parent.mkdir(parents=True, exist_ok=True)
            with open(debug_file, "a") as f:
                f.write(json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "meeting_id": meeting_id,
                    "error": str(e),
                    "output": output
                }) + "\n")
            print(f"Full output logged to: {debug_file}", file=sys.stderr)
            return []

        if not isinstance(candidates, list):
            print(f"Expected list, got {type(candidates).__name__}", file=sys.stderr)
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


def cmd_dedupe_log(args):
    """Remove duplicate entries from the processed log."""
    if not PROCESSED_LOG.exists():
        print("No processed log found.")
        return

    seen = set()
    unique_entries = []
    duplicate_count = 0

    with open(PROCESSED_LOG) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                file_path = entry.get("file", "")
                if file_path not in seen:
                    seen.add(file_path)
                    unique_entries.append(entry)
                else:
                    duplicate_count += 1
            except json.JSONDecodeError:
                continue

    if duplicate_count == 0:
        print("✅ No duplicates found in processed log.")
        return

    # Rewrite with unique entries only
    with open(PROCESSED_LOG, "w") as f:
        for entry in unique_entries:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Removed {duplicate_count} duplicate(s) from processed log.")
    print(f"   {len(unique_entries)} unique entries remaining.")


def cmd_promote(args):
    """Promote an approved candidate to a position."""
    # Import positions module
    import sys as sys_module
    sys_module.path.insert(0, str(Path(__file__).parent))
    from positions import promote_from_candidate, find_similar

    candidates = load_candidates()

    # Find the candidate
    candidate = None
    for c in candidates:
        if c["id"] == args.candidate_id:
            candidate = c
            break

    if not candidate:
        print(f"Candidate not found: {args.candidate_id}", file=sys.stderr)
        sys.exit(1)

    if candidate.get("status") != "approved":
        print(f"Candidate status is '{candidate.get('status')}', must be 'approved' to promote", file=sys.stderr)
        sys.exit(1)

    # Check for v2 format (has insight field)
    if "insight" not in candidate:
        print(f"Candidate is v1 format (too thin). Cannot promote.", file=sys.stderr)
        print(f"Consider reprocessing the source B32 with: python3 {sys.argv[0]} reprocess {candidate.get('source_meeting', '')}")
        sys.exit(1)

    # Check for duplicates
    if not args.skip_dedup:
        similar = find_similar(candidate["insight"], threshold=0.8)
        if similar:
            print(f"⚠️  Found {len(similar)} similar existing position(s):")
            for s in similar[:3]:
                print(f"   [{s['similarity']:.2f}] {s['id']} - {s['title']}")
            if not args.force:
                print(f"\nUse --force to promote anyway, or --skip-dedup to skip this check.")
                sys.exit(1)
            print(f"\n--force specified, promoting anyway...")

    # Promote
    try:
        position_id = promote_from_candidate(candidate)
        print(f"✓ Promoted to position: {position_id}")

        # Update candidate status
        candidate["status"] = "promoted"
        candidate["promoted_to"] = position_id
        candidate["promoted_at"] = datetime.now(timezone.utc).isoformat()

        # Rewrite candidates file
        with open(CANDIDATES_FILE, "w") as f:
            for c in candidates:
                f.write(json.dumps(c) + "\n")

    except Exception as e:
        print(f"Error promoting candidate: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_promote_all(args):
    """Promote all approved candidates to positions."""
    import sys as sys_module
    sys_module.path.insert(0, str(Path(__file__).parent))
    from positions import promote_from_candidate, find_similar

    candidates = load_candidates()

    # Find all approved candidates (not yet promoted)
    approved = [c for c in candidates if c.get("status") == "approved" and "insight" in c]

    if not approved:
        print("No approved v2 candidates to promote.")
        return

    print(f"Found {len(approved)} approved candidate(s) to promote\n")

    promoted_count = 0
    skipped_count = 0
    error_count = 0

    for candidate in approved:
        cand_id = candidate["id"]

        # Check for duplicates (with error handling)
        if not args.skip_dedup:
            try:
                similar = find_similar(candidate["insight"], threshold=0.8)
                if similar:
                    print(f"⏭️  Skipping {cand_id} - similar to existing position: {similar[0]['id']}")
                    skipped_count += 1
                    continue
            except Exception as e:
                print(f"⚠️  Dedup check failed for {cand_id}, proceeding: {e}", file=sys.stderr)

        try:
            position_id = promote_from_candidate(candidate)
            print(f"✓ {cand_id} → {position_id}")

            # Update candidate status
            candidate["status"] = "promoted"
            candidate["promoted_to"] = position_id
            candidate["promoted_at"] = datetime.now(timezone.utc).isoformat()
            promoted_count += 1

        except Exception as e:
            print(f"✗ {cand_id} - Error: {e}")
            error_count += 1

    # Rewrite candidates file
    with open(CANDIDATES_FILE, "w") as f:
        for c in candidates:
            f.write(json.dumps(c) + "\n")

    print(f"\n{'='*40}")
    print(f"Promoted: {promoted_count}")
    print(f"Skipped (duplicates): {skipped_count}")
    print(f"Errors: {error_count}")


def cmd_review_sheet_generate(args):
    """Generate a desktop-editable review sheet under N5/review/positions."""
    candidates = load_candidates()
    if args.status != "all":
        candidates = [c for c in candidates if c.get("status") == args.status]
    # Exclude already promoted
    candidates = [c for c in candidates if c.get("status") != "promoted"]
    candidates.sort(key=lambda c: c.get("extracted_at", ""), reverse=True)
    if args.limit:
        candidates = candidates[: args.limit]

    if not candidates:
        print("No candidates match the requested filters.")
        return

    batch_path = Path(args.output) if args.output else _next_review_sheet_path()
    md = _build_review_sheet(candidates, batch_path)
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    batch_path.write_text(md, encoding="utf-8")
    print(f"✓ Review sheet created: {batch_path}")
    print(f"  Candidates included: {len(candidates)}")


def cmd_review_sheet_ingest(args):
    """Ingest a completed review sheet and apply decisions to candidates."""
    sheet_path = Path(args.review_sheet)
    if not sheet_path.exists():
        print(f"Review sheet not found: {sheet_path}", file=sys.stderr)
        sys.exit(1)

    md = sheet_path.read_text(encoding="utf-8")
    decisions = _parse_review_sheet(md)

    candidates = load_candidates()
    updated, stats = _apply_review_decisions(
        candidates,
        decisions,
        sheet_path,
        dry_run=args.dry_run,
        recompute_on_amend=True,
    )

    if args.dry_run:
        print("DRY RUN — no files written")
    else:
        with open(CANDIDATES_FILE, "w", encoding="utf-8") as f:
            for c in updated:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"✓ Updated candidates file: {CANDIDATES_FILE}")

    print(json.dumps(stats, indent=2))


def cmd_promote_reviewed(args):
    """Promote candidates that have been reviewed as accept/amend.

    Near-dupes are allowed by default (skip-dedup). Use --dedupe to re-enable dedup checks.
    """
    import sys as sys_module
    sys_module.path.insert(0, str(Path(__file__).parent))
    from positions import promote_from_candidate, find_similar

    candidates = load_candidates()
    promotable = []
    for c in candidates:
        if c.get("status") != "approved":
            continue
        rev = c.get("review") or {}
        if rev.get("decision") not in ("accept", "amend"):
            continue
        if c.get("status") == "promoted":
            continue
        if "insight" not in c:
            continue
        promotable.append(c)

    if not promotable:
        print("No reviewed (accept/amend) approved v2 candidates to promote.")
        return

    print(f"Found {len(promotable)} reviewed candidate(s) to promote\n")

    promoted = 0
    skipped = 0
    errors = 0
    for candidate in promotable:
        cand_id = candidate["id"]

        insight_text = _candidate_display_insight(candidate)
        if not insight_text:
            print(f"⏭️  Skipping {cand_id} - missing insight text")
            skipped += 1
            continue

        if args.dedupe:
            try:
                similar = find_similar(insight_text, threshold=0.8)
                if similar:
                    print(f"⏭️  Skipping {cand_id} - similar to existing position: {similar[0]['id']}")
                    skipped += 1
                    continue
            except Exception as e:
                print(f"⚠️  Dedup check failed for {cand_id}, proceeding: {e}", file=sys.stderr)

        try:
            # Ensure the candidate handed to positions uses amended insight for title/text generation
            candidate_for_promotion = dict(candidate)
            if candidate_for_promotion.get("insight_amended"):
                candidate_for_promotion["insight"] = candidate_for_promotion["insight_amended"]

            position_id = promote_from_candidate(candidate_for_promotion)
            print(f"✓ {cand_id} → {position_id}")

            candidate["status"] = "promoted"
            candidate["promoted_to"] = position_id
            candidate["promoted_at"] = datetime.now(timezone.utc).isoformat()
            promoted += 1
        except Exception as e:
            print(f"✗ {cand_id} - Error: {e}")
            errors += 1

    with open(CANDIDATES_FILE, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"\n{'='*40}")
    print(f"Promoted: {promoted}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")


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

    # dedupe-log command
    dedupe_parser = subparsers.add_parser("dedupe-log", help="Remove duplicates from processed log")
    dedupe_parser.set_defaults(func=cmd_dedupe_log)

    # promote command
    promote_parser = subparsers.add_parser("promote", help="Promote an approved candidate to a position")
    promote_parser.add_argument("candidate_id", help="Candidate ID to promote")
    promote_parser.add_argument("--force", action="store_true", help="Promote even if similar position exists")
    promote_parser.add_argument("--skip-dedup", action="store_true", help="Skip duplicate check entirely")
    promote_parser.set_defaults(func=cmd_promote)

    # promote-all command
    promote_all_parser = subparsers.add_parser("promote-all", help="Promote all approved candidates")
    promote_all_parser.add_argument("--skip-dedup", action="store_true", help="Skip duplicate check (promote all)")
    promote_all_parser.set_defaults(func=cmd_promote_all)

    # review-sheet-generate command
    gen_parser = subparsers.add_parser("review-sheet-generate", help="Generate a positions review sheet (desktop-editable)")
    gen_parser.add_argument("--status", choices=["pending", "approved", "all"], default="pending", help="Which candidate statuses to include")
    gen_parser.add_argument("--limit", type=int, help="Limit number of candidates")
    gen_parser.add_argument("--output", help="Output path for review sheet (defaults to N5/review/positions)")
    gen_parser.set_defaults(func=cmd_review_sheet_generate)

    # review-sheet-ingest command
    ingest_parser = subparsers.add_parser("review-sheet-ingest", help="Ingest a completed review sheet and apply decisions")
    ingest_parser.add_argument("review_sheet", help="Path to review sheet markdown")
    ingest_parser.add_argument("--dry-run", action="store_true", help="Parse and report stats without writing changes")
    ingest_parser.set_defaults(func=cmd_review_sheet_ingest)

    # promote-reviewed command
    promote_rev_parser = subparsers.add_parser("promote-reviewed", help="Promote reviewed candidates (accept/amend)")
    promote_rev_parser.add_argument("--dedupe", action="store_true", help="Enable dedupe checks (default: allow near-dupes)")
    promote_rev_parser.set_defaults(func=cmd_promote_reviewed)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()













