#!/usr/bin/env python3
"""
Edge Reviewer: Process review queue, commit approved edges to edges.db.

Usage:
    # List pending edge files
    python3 edge_reviewer.py list
    
    # Show edges in a specific file
    python3 edge_reviewer.py show <filename>
    
    # Approve all edges in a file
    python3 edge_reviewer.py approve <filename>
    
    # Approve specific edges by line numbers
    python3 edge_reviewer.py approve <filename> --lines 2,3,5
    
    # Reject a file (moves to rejected/)
    python3 edge_reviewer.py reject <filename> --reason "Low quality extraction"
    
    # Generate review batch markdown for V
    python3 edge_reviewer.py batch --output "N5/review/edges/batch_2026-01-04.md"

Output: Moves files through pending/ → approved/ → committed/
"""

import argparse
import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Paths
WORKSPACE = Path("/home/workspace")
REVIEW_QUEUE = WORKSPACE / "N5/review/edges"
EDGES_DB = WORKSPACE / "N5/data/edges.db"

# Import edge writer
sys.path.insert(0, str(WORKSPACE / "N5/scripts"))
try:
    from edge_writer import add_edge, register_entity
    EDGE_WRITER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import edge_writer: {e}", file=sys.stderr)
    EDGE_WRITER_AVAILABLE = False


def list_pending() -> List[Dict]:
    """List all pending edge files."""
    pending_dir = REVIEW_QUEUE / "pending"
    if not pending_dir.exists():
        return []
    
    files = []
    for f in sorted(pending_dir.glob("*.jsonl")):
        # Read metadata
        meta = {"filename": f.name, "path": str(f), "edge_count": 0}
        with open(f) as fp:
            for line in fp:
                try:
                    data = json.loads(line)
                    if data.get("_meta"):
                        meta.update(data)
                    elif not data.get("_extraction_context"):
                        meta["edge_count"] += 1
                except json.JSONDecodeError:
                    pass
        files.append(meta)
    
    return files


def show_edges(filename: str) -> Dict[str, Any]:
    """Show edges in a pending file."""
    filepath = REVIEW_QUEUE / "pending" / filename
    if not filepath.exists():
        return {"error": f"File not found: {filename}"}
    
    result = {
        "filename": filename,
        "metadata": {},
        "edges": [],
        "extraction_context": None
    }
    
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                if data.get("_meta"):
                    result["metadata"] = data
                elif data.get("_extraction_context"):
                    result["extraction_context"] = data
                else:
                    data["_line_number"] = i
                    result["edges"].append(data)
            except json.JSONDecodeError as e:
                result["edges"].append({"_line_number": i, "_parse_error": str(e)})
    
    result["total_edges"] = len(result["edges"])
    return result


def approve_edges(
    filename: str,
    line_numbers: Optional[List[int]] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Approve edges and commit to database."""
    
    if not EDGE_WRITER_AVAILABLE:
        return {"error": "edge_writer module not available"}
    
    filepath = REVIEW_QUEUE / "pending" / filename
    if not filepath.exists():
        return {"error": f"File not found: {filename}"}
    
    # Load edges
    edges_data = show_edges(filename)
    if "error" in edges_data:
        return edges_data
    
    edges = edges_data["edges"]
    metadata = edges_data.get("metadata", {})
    meeting_id = metadata.get("meeting_id", "unknown")
    
    # Filter to specific lines if provided
    if line_numbers:
        edges = [e for e in edges if e.get("_line_number") in line_numbers]
    
    if not edges:
        return {"error": "No edges to approve"}
    
    result = {
        "filename": filename,
        "meeting_id": meeting_id,
        "total_edges": len(edges),
        "committed": 0,
        "skipped": 0,
        "errors": []
    }
    
    if dry_run:
        result["dry_run"] = True
        result["would_commit"] = len(edges)
        return result
    
    # Commit edges
    for edge in edges:
        try:
            # Skip metadata lines
            if edge.get("_parse_error") or edge.get("_meta") or edge.get("_extraction_context"):
                result["skipped"] += 1
                continue
            
            # Register entities
            source_display = edge.get("source_display", edge["source_id"])
            target_display = edge.get("target_display", edge["target_id"])
            
            register_entity(edge["source_type"], edge["source_id"], source_display)
            register_entity(edge["target_type"], edge["target_id"], target_display)
            
            # Add edge
            source_ref = f"{edge['source_type']}:{edge['source_id']}"
            target_ref = f"{edge['target_type']}:{edge['target_id']}"
            
            edge_result = add_edge(
                source=source_ref,
                relation=edge["relation"],
                target=target_ref,
                meeting=meeting_id,
                evidence=edge.get("evidence", "")
            )
            
            if edge_result.get("status") in ["created", "duplicate"]:
                result["committed"] += 1
            else:
                result["errors"].append(f"Line {edge.get('_line_number')}: {edge_result}")
                
        except Exception as e:
            result["errors"].append(f"Line {edge.get('_line_number')}: {str(e)}")
    
    # Move file to committed/
    if result["committed"] > 0:
        committed_path = REVIEW_QUEUE / "committed" / filename
        committed_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(filepath), str(committed_path))
        result["moved_to"] = str(committed_path)
    
    return result


def reject_file(filename: str, reason: str) -> Dict[str, Any]:
    """Reject a file and move to rejected/."""
    filepath = REVIEW_QUEUE / "pending" / filename
    if not filepath.exists():
        return {"error": f"File not found: {filename}"}
    
    # Add rejection metadata
    rejected_path = REVIEW_QUEUE / "rejected" / filename
    rejected_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read original content
    with open(filepath) as f:
        lines = f.readlines()
    
    # Add rejection metadata
    rejection_meta = {
        "_rejection": True,
        "rejected_at": datetime.now().isoformat(),
        "reason": reason
    }
    
    with open(rejected_path, 'w') as f:
        f.write(json.dumps(rejection_meta) + "\n")
        f.writelines(lines)
    
    # Remove original
    filepath.unlink()
    
    return {
        "status": "rejected",
        "filename": filename,
        "reason": reason,
        "moved_to": str(rejected_path)
    }


def generate_review_batch(output_path: Optional[str] = None) -> str:
    """Generate a markdown review batch for V."""
    
    pending = list_pending()
    if not pending:
        return "No pending edge files to review."
    
    lines = [
        "---",
        f"created: {datetime.now().strftime('%Y-%m-%d')}",
        "type: edge_review_batch",
        "---",
        "",
        "# Edge Review Batch",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Files to review:** {len(pending)}",
        "",
        "## Instructions",
        "",
        "For each edge below, mark:",
        "- ☑ APPROVE — Edge is accurate and valuable",
        "- ☐ REJECT — Edge is wrong, noise, or low quality",
        "- ☐ MODIFY — Edge needs adjustment (note changes)",
        "",
        "---",
        ""
    ]
    
    edge_num = 1
    for file_meta in pending:
        filename = file_meta["filename"]
        edges_data = show_edges(filename)
        
        lines.append(f"## File: `{filename}`")
        lines.append(f"**Meeting:** {file_meta.get('meeting_id', 'Unknown')}")
        lines.append(f"**Edges:** {len(edges_data.get('edges', []))}")
        lines.append("")
        
        for edge in edges_data.get("edges", []):
            if edge.get("_parse_error") or edge.get("_extraction_context"):
                continue
                
            source = f"{edge.get('source_type', '?')}:{edge.get('source_id', '?')}"
            target = f"{edge.get('target_type', '?')}:{edge.get('target_id', '?')}"
            relation = edge.get('relation', '?')
            evidence = edge.get('evidence', 'No evidence provided')[:200]
            
            lines.append(f"### {edge_num}. ☐ APPROVE / ☐ REJECT / ☐ MODIFY")
            lines.append(f"- **Edge:** `{source}` --`{relation}`--> `{target}`")
            if edge.get('source_display'):
                lines.append(f"- **Source:** {edge['source_display']}")
            if edge.get('target_display'):
                lines.append(f"- **Target:** {edge['target_display']}")
            lines.append(f"- **Evidence:** \"{evidence}\"")
            if edge.get('conflict_flag'):
                lines.append(f"- **⚠️ Conflict:** {edge['conflict_flag']}")
            lines.append("")
            edge_num += 1
        
        lines.append("---")
        lines.append("")
    
    content = "\n".join(lines)
    
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)
        return f"Review batch written to: {output_path}"
    
    return content


def commit_from_jsonl(jsonl_content: str, meeting_id: str) -> Dict[str, Any]:
    """
    Commit edges directly from JSONL string (for LLM-generated output).
    
    Usage:
        result = commit_from_jsonl(llm_output, "mtg_2026-01-04")
    """
    if not EDGE_WRITER_AVAILABLE:
        return {"error": "edge_writer module not available"}
    
    result = {
        "meeting_id": meeting_id,
        "committed": 0,
        "skipped": 0,
        "errors": []
    }
    
    for i, line in enumerate(jsonl_content.strip().split("\n"), 1):
        if not line.strip():
            continue
            
        try:
            edge = json.loads(line)
            
            # Skip metadata
            if edge.get("_meta") or edge.get("_extraction_context"):
                result["skipped"] += 1
                continue
            
            # Validate required fields
            required = ['source_type', 'source_id', 'relation', 'target_type', 'target_id']
            missing = [f for f in required if f not in edge]
            if missing:
                result["errors"].append(f"Line {i}: Missing fields: {missing}")
                continue
            
            # Register entities
            register_entity(
                edge["source_type"], 
                edge["source_id"], 
                edge.get("source_display", edge["source_id"])
            )
            register_entity(
                edge["target_type"], 
                edge["target_id"], 
                edge.get("target_display", edge["target_id"])
            )
            
            # Add edge
            source_ref = f"{edge['source_type']}:{edge['source_id']}"
            target_ref = f"{edge['target_type']}:{edge['target_id']}"
            
            add_result = add_edge(
                source=source_ref,
                relation=edge["relation"],
                target=target_ref,
                meeting=meeting_id,
                evidence=edge.get("evidence", "")
            )
            
            if add_result.get("status") in ["created", "duplicate"]:
                result["committed"] += 1
            else:
                result["errors"].append(f"Line {i}: {add_result}")
                
        except json.JSONDecodeError as e:
            result["errors"].append(f"Line {i}: JSON parse error: {e}")
        except Exception as e:
            result["errors"].append(f"Line {i}: {e}")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Review and commit edges from review queue")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List pending files")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show edges in a file")
    show_parser.add_argument("filename", help="File to show")
    
    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve and commit edges")
    approve_parser.add_argument("filename", help="File to approve")
    approve_parser.add_argument("--lines", type=str, help="Specific line numbers (e.g., 2,3,5)")
    approve_parser.add_argument("--dry-run", action="store_true", help="Show what would be committed")
    
    # Reject command
    reject_parser = subparsers.add_parser("reject", help="Reject a file")
    reject_parser.add_argument("filename", help="File to reject")
    reject_parser.add_argument("--reason", type=str, required=True, help="Reason for rejection")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Generate review batch markdown")
    batch_parser.add_argument("--output", type=str, help="Output file path")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show queue statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "list":
            pending = list_pending()
            print(json.dumps({"pending_files": pending, "count": len(pending)}, indent=2))
            
        elif args.command == "show":
            result = show_edges(args.filename)
            print(json.dumps(result, indent=2, default=str))
            
        elif args.command == "approve":
            line_numbers = None
            if args.lines:
                line_numbers = [int(x.strip()) for x in args.lines.split(",")]
            result = approve_edges(args.filename, line_numbers, dry_run=args.dry_run)
            print(json.dumps(result, indent=2))
            
        elif args.command == "reject":
            result = reject_file(args.filename, args.reason)
            print(json.dumps(result, indent=2))
            
        elif args.command == "batch":
            result = generate_review_batch(args.output)
            print(result)
            
        elif args.command == "stats":
            pending = list(( REVIEW_QUEUE / "pending").glob("*.jsonl")) if (REVIEW_QUEUE / "pending").exists() else []
            approved = list((REVIEW_QUEUE / "approved").glob("*.jsonl")) if (REVIEW_QUEUE / "approved").exists() else []
            rejected = list((REVIEW_QUEUE / "rejected").glob("*.jsonl")) if (REVIEW_QUEUE / "rejected").exists() else []
            committed = list((REVIEW_QUEUE / "committed").glob("*.jsonl")) if (REVIEW_QUEUE / "committed").exists() else []
            
            print(json.dumps({
                "pending": len(pending),
                "approved": len(approved),
                "rejected": len(rejected),
                "committed": len(committed)
            }, indent=2))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()



