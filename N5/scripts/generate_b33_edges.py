#!/usr/bin/env python3
"""
Generate B33 Decision Edges: Extract context graph edges from meeting intelligence.

This script integrates B33 edge extraction into the meeting processing pipeline.
It reads existing intelligence blocks (B01, B03, B32) from a meeting folder,
invokes the B33 extraction prompt via LLM, writes edges to JSONL, commits to
brain.db (meeting_edges table), and updates manifest.json.

Usage:
    # Process a single meeting
    python3 generate_b33_edges.py --meeting /path/to/meeting_folder
    
    # Dry run (don't commit to DB)
    python3 generate_b33_edges.py --meeting /path/to/meeting_folder --dry-run
    
    # Process and skip review queue (direct commit)
    python3 generate_b33_edges.py --meeting /path/to/meeting_folder --auto-commit

Output:
    - B33_DECISION_EDGES.jsonl in meeting folder
    - Edges committed to brain.db (meeting_edges table) (unless --dry-run)
    - manifest.json updated with B33 status
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

WORKSPACE = Path("/home/workspace")
sys.path.insert(0, str(WORKSPACE / "N5/scripts"))

try:
    from edge_writer import add_edge, register_entity
    from edge_reviewer import commit_from_jsonl
    EDGE_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import edge tools: {e}", file=sys.stderr)
    EDGE_TOOLS_AVAILABLE = False

# Phase 4.5: Position integration
try:
    from positions import find_similar as find_similar_positions, get_position
    POSITIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import positions module: {e}", file=sys.stderr)
    POSITIONS_AVAILABLE = False


def match_edge_to_positions(evidence: str, threshold: float = 0.75) -> List[Dict[str, Any]]:
    """
    Match edge evidence to existing positions.
    Returns list of position matches with relation type (supports/challenges).
    
    Phase 4.5: Position Integration
    """
    if not POSITIONS_AVAILABLE:
        return []
    
    try:
        matches = find_similar_positions(evidence, threshold=threshold)
        results = []
        for m in matches[:3]:  # Limit to top 3 matches
            results.append({
                "position_id": m["id"],
                "position_title": m["title"],
                "stability": m["stability"],
                "similarity": m["similarity"],
                # Default to supports - LLM will refine in prompt
                "suggested_relation": "supports_position"
            })
        return results
    except Exception as e:
        print(f"Warning: Position matching failed: {e}", file=sys.stderr)
        return []


def get_position_context_for_prompt() -> str:
    """
    Get position context to include in extraction prompt.
    Returns formatted string of high-stability positions.
    
    Phase 4.5: Position Integration
    """
    if not POSITIONS_AVAILABLE:
        return ""
    
    try:
        import sqlite3
        db_path = WORKSPACE / "N5/data/positions.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get stable and canonical positions for context
        cursor.execute("""
            SELECT id, domain, title, substr(insight, 1, 150) as insight_preview, stability
            FROM positions
            WHERE stability IN ('stable', 'canonical', 'working')
            ORDER BY 
                CASE stability 
                    WHEN 'canonical' THEN 1 
                    WHEN 'stable' THEN 2 
                    WHEN 'working' THEN 3 
                END,
                domain
            LIMIT 20
        """)
        positions = cursor.fetchall()
        conn.close()
        
        if not positions:
            return ""
        
        lines = [
            "",
            "## V's Known Positions (for position-linking edges)",
            "",
            "When ideas/decisions strongly align with or contradict these positions, create:",
            "- `supports_position`: idea/decision → position (evidence validates position)",
            "- `challenges_position`: idea/decision → position (evidence contradicts position)",
            "",
            "| ID | Domain | Title | Stability |",
            "|----|----|----|----|"
        ]
        
        for p in positions:
            lines.append(f"| `{p['id'][:40]}` | {p['domain']} | {p['title'][:50]} | {p['stability']} |")
        
        lines.append("")
        lines.append("Only create position edges when there's CLEAR alignment or contradiction. Don't force it.")
        lines.append("")
        
        return "\n".join(lines)
    
    except Exception as e:
        print(f"Warning: Could not get position context: {e}", file=sys.stderr)
        return ""


def extract_meeting_id(folder_path: Path) -> str:
    """Extract meeting ID from folder name."""
    name = folder_path.name
    for suffix in ['_[M]', '_[P]', '_[C]']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    return f"mtg_{name}"


def read_block(folder: Path, block_name: str) -> Optional[str]:
    """Read a block file from meeting folder."""
    for pattern in [f"{block_name}.md", f"{block_name.upper()}.md"]:
        path = folder / pattern
        if path.exists():
            return path.read_text()
    return None


def gather_meeting_context(folder: Path) -> Dict[str, Any]:
    """Gather context from meeting folder for B33 extraction."""
    context = {
        "meeting_id": extract_meeting_id(folder),
        "folder": str(folder),
        "blocks": {},
        "transcript": None,
        "manifest": None
    }
    
    b01 = read_block(folder, "B01_DETAILED_RECAP")
    if b01:
        context["blocks"]["B01_DETAILED_RECAP"] = b01
    
    b03_decisions = read_block(folder, "B03_DECISIONS")
    if b03_decisions:
        context["blocks"]["B03_DECISIONS"] = b03_decisions
    
    b03_stakeholder = read_block(folder, "B03_STAKEHOLDER_INTELLIGENCE")
    if b03_stakeholder:
        context["blocks"]["B03_STAKEHOLDER_INTELLIGENCE"] = b03_stakeholder
    
    b32 = read_block(folder, "B32_THOUGHT_PROVOKING_IDEAS")
    if b32:
        context["blocks"]["B32_THOUGHT_PROVOKING_IDEAS"] = b32
    
    transcript_path = folder / "transcript.jsonl"
    if transcript_path.exists():
        try:
            with open(transcript_path) as f:
                for line in f:
                    data = json.loads(line)
                    if "text" in data:
                        context["transcript"] = data["text"]
                        break
        except:
            pass
    
    manifest_path = folder / "manifest.json"
    if manifest_path.exists():
        try:
            context["manifest"] = json.loads(manifest_path.read_text())
        except:
            pass
    
    return context


def build_extraction_prompt(context: Dict[str, Any]) -> str:
    """Build the B33 extraction prompt from meeting context."""
    
    prompt_parts = [
        "# B33 Edge Extraction Task",
        "",
        f"Meeting ID: {context['meeting_id']}",
        "",
        "Extract edges (relationships) between ideas, decisions, people, and outcomes for the context graph system.",
        "",
        "## Edge Types Available",
        "- `originated_by`: Who first voiced this idea (idea/decision → person)",
        "- `supported_by`: Who endorsed after hearing (idea/decision → person)",
        "- `challenged_by`: Who pushed back or raised concerns (idea/decision → person)",
        "- `hoped_for`: Expected positive outcome (idea/decision → outcome)",
        "- `concerned_about`: Feared risk or downside (idea/decision → outcome)",
        "- `influenced_by`: Who shaped thinking on topic (idea/person → person)",
        "- `depends_on`: Logical dependency (idea/decision → idea/decision)",
        "",
        "### Position-Related Edge Types (Phase 4.5)",
        "- `supports_position`: Edge evidence supports V's documented position (idea/decision → position)",
        "- `challenges_position`: Edge evidence contradicts V's documented position (idea/decision → position)",
        "- `crystallized_from`: A new position emerged from this evidence (position → idea/decision)",
        "",
        "## Important Notes",
        "- V (Vrijen Attawar) is always `vrijen` as person ID",
        "- Be selective: 3-8 high-quality edges is better than 20 low-quality ones",
        "- Every edge MUST have evidence (quote or paraphrase)",
        "- Distinguish originator vs supporter carefully",
        "- For position edges: only create when alignment/contradiction is CLEAR",
        ""
    ]
    
    # Add position context if available
    position_context = get_position_context_for_prompt()
    if position_context:
        prompt_parts.append(position_context)
    
    prompt_parts.append("## Meeting Content")
    prompt_parts.append("")
    
    if context["blocks"].get("B01_DETAILED_RECAP"):
        prompt_parts.extend([
            "### B01: Detailed Recap",
            context["blocks"]["B01_DETAILED_RECAP"][:8000],
            ""
        ])
    
    if context["blocks"].get("B03_DECISIONS"):
        prompt_parts.extend([
            "### B03: Decisions",
            context["blocks"]["B03_DECISIONS"][:3000],
            ""
        ])
    
    if context["blocks"].get("B32_THOUGHT_PROVOKING_IDEAS"):
        prompt_parts.extend([
            "### B32: Thought-Provoking Ideas",
            context["blocks"]["B32_THOUGHT_PROVOKING_IDEAS"][:3000],
            ""
        ])
    
    if context["transcript"]:
        prompt_parts.extend([
            "### Transcript Excerpt",
            context["transcript"][:6000],
            ""
        ])
    
    prompt_parts.extend([
        "## Output Format",
        "",
        "Output ONLY valid JSONL (one JSON object per line). No markdown, no explanation.",
        "",
        "Each edge object must have these fields:",
        '```',
        '{',
        '  "source_type": "idea|decision|person|position",',
        '  "source_id": "slug-format-id",',
        '  "source_display": "Human readable name",',
        '  "relation": "originated_by|supported_by|challenged_by|hoped_for|concerned_about|influenced_by|depends_on|supports_position|challenges_position|crystallized_from",',
        '  "target_type": "person|idea|decision|outcome|position",',
        '  "target_id": "slug-format-id",',
        '  "target_display": "Human readable name",',
        '  "evidence": "Quote or paraphrase from meeting"',
        '}',
        '```',
        "",
        "Generate JSONL now. Output ONLY the JSON lines, nothing else."
    ])
    
    return "\n".join(prompt_parts)


def extract_jsonl_from_response(response: str) -> str:
    """Extract JSONL content from LLM response (handles markdown fences)."""
    lines = response.strip().split('\n')
    jsonl_lines = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('{') and line.endswith('}'):
            try:
                json.loads(line)
                jsonl_lines.append(line)
            except json.JSONDecodeError:
                pass
    
    return '\n'.join(jsonl_lines)


def write_b33_file(folder: Path, jsonl_content: str, meeting_id: str) -> Path:
    """Write B33_DECISION_EDGES.jsonl to meeting folder."""
    b33_path = folder / "B33_DECISION_EDGES.jsonl"
    
    meta_line = json.dumps({
        "_meta": True,
        "meeting_id": meeting_id,
        "generated_at": datetime.now().isoformat(),
        "generator": "generate_b33_edges.py"
    })
    
    with open(b33_path, 'w') as f:
        f.write(meta_line + '\n')
        f.write(jsonl_content + '\n')
    
    return b33_path


def update_manifest(folder: Path, success: bool, edge_count: int) -> None:
    """Update manifest.json with B33 status."""
    manifest_path = folder / "manifest.json"
    
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {}
    
    if "blocks_generated" not in manifest:
        manifest["blocks_generated"] = {}
    
    manifest["blocks_generated"]["b33_decision_edges"] = success
    manifest["b33_edge_count"] = edge_count
    manifest["b33_generated_at"] = datetime.now().isoformat()
    manifest["last_updated_by"] = "generate_b33_edges.py"
    
    manifest_path.write_text(json.dumps(manifest, indent=2))


def process_meeting(
    folder: Path,
    dry_run: bool = False,
    auto_commit: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Process a meeting folder for B33 edge extraction.
    
    Returns:
        Dict with status, edges extracted, and any errors
    """
    result = {
        "folder": str(folder),
        "meeting_id": None,
        "status": "pending",
        "edges_extracted": 0,
        "edges_committed": 0,
        "b33_file": None,
        "errors": []
    }
    
    if not folder.exists():
        result["status"] = "error"
        result["errors"].append(f"Folder not found: {folder}")
        return result
    
    context = gather_meeting_context(folder)
    result["meeting_id"] = context["meeting_id"]
    
    if not context["blocks"]:
        result["status"] = "skipped"
        result["errors"].append("No intelligence blocks found (B01, B03, B32)")
        return result
    
    b33_existing = folder / "B33_DECISION_EDGES.jsonl"
    if b33_existing.exists() and not dry_run:
        result["status"] = "exists"
        result["b33_file"] = str(b33_existing)
        return result
    
    prompt = build_extraction_prompt(context)
    
    if verbose:
        print(f"[DEBUG] Prompt length: {len(prompt)} chars")
        print(f"[DEBUG] Blocks available: {list(context['blocks'].keys())}")
    
    if dry_run:
        result["status"] = "dry_run"
        result["prompt_preview"] = prompt[:500] + "..."
        return result
    
    try:
        import requests
        
        api_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
        if not api_token:
            result["status"] = "error"
            result["errors"].append("ZO_CLIENT_IDENTITY_TOKEN not available")
            return result
        
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": api_token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=120
        )
        
        if response.status_code != 200:
            result["status"] = "error"
            result["errors"].append(f"API error: {response.status_code}")
            return result
        
        llm_output = response.json().get("output", "")
        jsonl_content = extract_jsonl_from_response(llm_output)
        
        if not jsonl_content.strip():
            result["status"] = "error"
            result["errors"].append("No valid JSONL extracted from LLM response")
            return result
        
        edge_count = len([l for l in jsonl_content.split('\n') if l.strip()])
        result["edges_extracted"] = edge_count
        
        b33_path = write_b33_file(folder, jsonl_content, context["meeting_id"])
        result["b33_file"] = str(b33_path)
        
        if auto_commit and EDGE_TOOLS_AVAILABLE:
            commit_result = commit_from_jsonl(jsonl_content, context["meeting_id"])
            result["edges_committed"] = commit_result.get("committed", 0)
            if commit_result.get("errors"):
                result["errors"].extend(commit_result["errors"])
        
        update_manifest(folder, True, edge_count)
        
        result["status"] = "success"
        
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate B33 Decision Edges from meeting intelligence"
    )
    parser.add_argument(
        "--meeting",
        required=True,
        help="Path to meeting folder"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Automatically commit edges to brain.db (meeting_edges table) (skip review queue)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed debug output"
    )
    
    args = parser.parse_args()
    
    folder = Path(args.meeting)
    
    result = process_meeting(
        folder=folder,
        dry_run=args.dry_run,
        auto_commit=args.auto_commit,
        verbose=args.verbose
    )
    
    print(json.dumps(result, indent=2))
    
    if result["status"] == "error":
        sys.exit(1)
    elif result["status"] == "success":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()


