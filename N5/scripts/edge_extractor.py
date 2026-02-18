#!/usr/bin/env python3
"""
Edge Extractor: Run B33 extraction on meeting transcripts, output to review queue.

Usage:
    # Extract from a specific meeting folder
    python3 edge_extractor.py --meeting "Personal/Meetings/Week-of-2025-12-30/2025-12-30_meeting-name"
    
    # Extract from meeting by ID
    python3 edge_extractor.py --meeting-id "mtg_2025-12-30_meeting-name"
    
    # Dry run (show what would be extracted, don't write)
    python3 edge_extractor.py --meeting "..." --dry-run
    
    # Process multiple meetings (batch mode)
    python3 edge_extractor.py --batch "Personal/Meetings/Week-of-2025-12-30"

Output: JSONL files in N5/review/edges/pending/
"""

import argparse
import json
import os
import sys
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

# Paths
WORKSPACE = Path("/home/workspace")
EDGES_DB = Path("/home/workspace/N5/cognition/brain.db")
CRM_DB = WORKSPACE / "N5/data/n5_core.db"
REVIEW_QUEUE = WORKSPACE / "N5/review/edges"
B33_PROMPT = WORKSPACE / "Prompts/Blocks/Generate_B33.prompt.md"
MEETINGS_ROOT = WORKSPACE / "Personal/Meetings"


def get_known_people() -> Dict[str, str]:
    """Load CRM people for name matching."""
    if not CRM_DB.exists():
        return {}
    
    conn = sqlite3.connect(CRM_DB)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT email, name FROM profiles")
        rows = cursor.fetchall()
        
        # Build name -> slug mapping
        people = {}
        for email, name in rows:
            # Generate slug from name
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            people[name.lower()] = slug
            # Also map first name
            first_name = name.split()[0].lower() if name else ""
            if first_name and first_name not in people:
                people[first_name] = slug
        
        return people
    except Exception as e:
        print(f"Warning: Could not load CRM people: {e}", file=sys.stderr)
        return {}
    finally:
        conn.close()


def get_existing_edges() -> List[Dict]:
    """Load existing active edges for conflict detection."""
    if not EDGES_DB.exists():
        return []
    
    conn = sqlite3.connect(EDGES_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT source_type, source_id, relation, target_type, target_id
            FROM edges WHERE status = 'active'
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def find_transcript(meeting_path: Path) -> Optional[Path]:
    """Find transcript file in meeting folder."""
    # Common transcript patterns
    patterns = [
        "transcript.md",
        "*transcript*.md",
        "*_transcript.md",
        "*.transcript.md",
        "notes.md",  # Sometimes transcripts are in notes
    ]
    
    for pattern in patterns:
        matches = list(meeting_path.glob(pattern))
        if matches:
            # Prefer longer files (more content)
            matches.sort(key=lambda p: p.stat().st_size, reverse=True)
            return matches[0]
    
    # Look for any .md file with substantial content
    for md_file in meeting_path.glob("*.md"):
        if md_file.stat().st_size > 1000:  # At least 1KB
            return md_file
    
    return None


def find_manifest(meeting_path: Path) -> Optional[Dict]:
    """Load manifest.json if exists."""
    manifest_path = meeting_path / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return None


def generate_meeting_id(meeting_path: Path) -> str:
    """Generate meeting ID from path."""
    folder_name = meeting_path.name
    # Try to extract date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', folder_name)
    if date_match:
        date_str = date_match.group(1)
        # Get slug from rest of folder name
        slug = re.sub(r'\d{4}-\d{2}-\d{2}[_-]?', '', folder_name)
        slug = re.sub(r'[^a-z0-9]+', '-', slug.lower()).strip('-')
        return f"mtg_{date_str}_{slug}" if slug else f"mtg_{date_str}"
    
    # Fallback: hash the path
    return f"mtg_{hashlib.md5(str(meeting_path).encode()).hexdigest()[:8]}"


def check_conflicts(candidate: Dict, existing_edges: List[Dict]) -> Optional[str]:
    """Check if candidate edge conflicts with existing edges."""
    for existing in existing_edges:
        # Same source and relation, different target = potential conflict
        if (candidate.get('source_type') == existing['source_type'] and
            candidate.get('source_id') == existing['source_id'] and
            candidate.get('relation') == existing['relation'] and
            candidate.get('target_id') != existing['target_id']):
            
            # Some relations allow multiple targets (supported_by can have many supporters)
            multi_target_relations = ['supported_by', 'challenged_by', 'influenced_by']
            if candidate.get('relation') not in multi_target_relations:
                return f"Conflicts with existing edge: {existing['source_id']} --{existing['relation']}--> {existing['target_id']}"
    
    return None


def validate_edge(edge: Dict) -> List[str]:
    """Validate edge structure, return list of errors."""
    errors = []
    
    required_fields = ['source_type', 'source_id', 'relation', 'target_type', 'target_id', 'evidence']
    for field in required_fields:
        if field not in edge or not edge[field]:
            errors.append(f"Missing required field: {field}")
    
    valid_types = ['person', 'idea', 'decision', 'outcome', 'meeting']
    if edge.get('source_type') not in valid_types:
        errors.append(f"Invalid source_type: {edge.get('source_type')}")
    if edge.get('target_type') not in valid_types:
        errors.append(f"Invalid target_type: {edge.get('target_type')}")
    
    valid_relations = [
        'originated_by', 'supported_by', 'challenged_by',
        'hoped_for', 'concerned_about', 'influenced_by',
        'preceded_by', 'depends_on', 'supersedes'
    ]
    if edge.get('relation') not in valid_relations:
        errors.append(f"Invalid relation: {edge.get('relation')}")
    
    return errors


def extract_edges_from_transcript(
    transcript_text: str,
    meeting_id: str,
    metadata: Optional[Dict],
    known_people: Dict[str, str],
    existing_edges: List[Dict]
) -> List[Dict]:
    """
    Extract edges from transcript using B33 prompt.
    
    This is a placeholder that returns the structure needed.
    In production, this calls the LLM with the B33 prompt.
    """
    # For now, return empty - actual extraction happens via LLM
    # This function structures the input for LLM call
    
    extraction_context = {
        "transcript": transcript_text[:50000],  # Limit context
        "meeting_id": meeting_id,
        "metadata": metadata or {},
        "known_people": known_people,
        "instruction": "Extract edges following B33 prompt guidelines. Output JSONL only."
    }
    
    # In actual use, this would call:
    # response = llm.generate(B33_PROMPT, context=extraction_context)
    # edges = parse_jsonl(response)
    
    return extraction_context  # Return context for manual/LLM processing


def write_to_review_queue(
    edges: List[Dict],
    meeting_id: str,
    meeting_path: Path,
    dry_run: bool = False
) -> Path:
    """Write extracted edges to review queue."""
    
    # Generate filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_meeting_id = re.sub(r'[^a-z0-9_-]', '-', meeting_id.lower())
    filename = f"{date_str}_{safe_meeting_id}.jsonl"
    
    output_path = REVIEW_QUEUE / "pending" / filename
    
    if dry_run:
        print(f"[DRY RUN] Would write {len(edges)} edges to: {output_path}")
        for edge in edges:
            print(json.dumps(edge))
        return output_path
    
    # Write JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        # Write metadata header
        header = {
            "_meta": True,
            "meeting_id": meeting_id,
            "meeting_path": str(meeting_path),
            "extracted_at": datetime.now().isoformat(),
            "edge_count": len([e for e in edges if not e.get('_meta')])
        }
        f.write(json.dumps(header) + "\n")
        
        # Write edges
        for edge in edges:
            if not edge.get('_meta'):
                f.write(json.dumps(edge) + "\n")
    
    return output_path


def process_meeting(
    meeting_path: Path,
    dry_run: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """Process a single meeting folder."""
    
    result = {
        "meeting_path": str(meeting_path),
        "status": "pending",
        "edges_found": 0,
        "output_file": None,
        "errors": []
    }
    
    # Validate path
    if not meeting_path.exists():
        result["status"] = "error"
        result["errors"].append(f"Path does not exist: {meeting_path}")
        return result
    
    if not meeting_path.is_dir():
        result["status"] = "error"
        result["errors"].append(f"Path is not a directory: {meeting_path}")
        return result
    
    # Find transcript
    transcript_path = find_transcript(meeting_path)
    if not transcript_path:
        result["status"] = "skipped"
        result["errors"].append("No transcript found")
        return result
    
    if verbose:
        print(f"Found transcript: {transcript_path}")
    
    # Load transcript
    transcript_text = transcript_path.read_text()
    if len(transcript_text) < 500:
        result["status"] = "skipped"
        result["errors"].append(f"Transcript too short ({len(transcript_text)} chars)")
        return result
    
    # Generate meeting ID
    meeting_id = generate_meeting_id(meeting_path)
    result["meeting_id"] = meeting_id
    
    # Load metadata
    manifest = find_manifest(meeting_path)
    
    # Load known people
    known_people = get_known_people()
    
    # Load existing edges for conflict detection
    existing_edges = get_existing_edges()
    
    # Extract context (for LLM processing)
    extraction_context = extract_edges_from_transcript(
        transcript_text,
        meeting_id,
        manifest,
        known_people,
        existing_edges
    )
    
    # For now, output the extraction context so LLM can process it
    # In integrated mode, this would call the LLM directly
    
    context_output = {
        "_extraction_context": True,
        "meeting_id": meeting_id,
        "meeting_path": str(meeting_path),
        "transcript_path": str(transcript_path),
        "transcript_length": len(transcript_text),
        "known_people_count": len(known_people),
        "existing_edges_count": len(existing_edges),
        "ready_for_llm": True
    }
    
    # Write context to pending queue for LLM processing
    output_path = write_to_review_queue(
        [context_output],
        meeting_id,
        meeting_path,
        dry_run=dry_run
    )
    
    result["status"] = "context_prepared"
    result["output_file"] = str(output_path)
    result["message"] = "Extraction context prepared. Run B33 prompt on this meeting to generate edges."
    
    return result


def process_batch(batch_path: Path, dry_run: bool = False, verbose: bool = False) -> List[Dict]:
    """Process all meetings in a folder."""
    results = []
    
    if not batch_path.exists():
        return [{"error": f"Batch path does not exist: {batch_path}"}]
    
    # Find meeting folders (look for folders with dates or manifests)
    meeting_folders = []
    for item in batch_path.iterdir():
        if item.is_dir():
            # Check if it looks like a meeting folder
            if re.search(r'\d{4}-\d{2}-\d{2}', item.name) or (item / "manifest.json").exists():
                meeting_folders.append(item)
    
    print(f"Found {len(meeting_folders)} meeting folders in {batch_path}")
    
    for folder in sorted(meeting_folders):
        if verbose:
            print(f"\nProcessing: {folder.name}")
        result = process_meeting(folder, dry_run=dry_run, verbose=verbose)
        results.append(result)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Extract decision edges from meeting transcripts")
    parser.add_argument("--meeting", type=str, help="Path to meeting folder (relative to workspace)")
    parser.add_argument("--meeting-id", type=str, help="Meeting ID to find and process")
    parser.add_argument("--batch", type=str, help="Process all meetings in folder")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be extracted")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not any([args.meeting, args.meeting_id, args.batch]):
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.batch:
            batch_path = WORKSPACE / args.batch
            results = process_batch(batch_path, dry_run=args.dry_run, verbose=args.verbose)
            
            # Summary
            success = len([r for r in results if r.get('status') in ['context_prepared', 'extracted']])
            skipped = len([r for r in results if r.get('status') == 'skipped'])
            errors = len([r for r in results if r.get('status') == 'error'])
            
            print(f"\n=== Batch Summary ===")
            print(f"Processed: {success}")
            print(f"Skipped: {skipped}")
            print(f"Errors: {errors}")
            
            print(json.dumps({"batch_results": results}, indent=2))
            
        elif args.meeting:
            meeting_path = WORKSPACE / args.meeting
            result = process_meeting(meeting_path, dry_run=args.dry_run, verbose=args.verbose)
            print(json.dumps(result, indent=2))
            
        elif args.meeting_id:
            # Search for meeting by ID
            print(f"Searching for meeting: {args.meeting_id}")
            # TODO: Implement meeting search by ID
            print(json.dumps({"error": "Meeting ID search not yet implemented"}))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

