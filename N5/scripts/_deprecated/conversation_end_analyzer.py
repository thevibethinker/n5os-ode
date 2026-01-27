#!/usr/bin/env python3
"""
Conversation End Analyzer v3.0

Analyzes conversation workspace to identify artifacts, deliverables, and 
files that need organization. Supports tiered analysis modes.

Usage:
    python3 conversation_end_analyzer.py --workspace <path> --convo-id <id> [--mode quick|standard|full]

Modes:
    --quick     Tier 1: Basic file listing, minimal analysis
    --standard  Tier 2: Detailed categorization, recommendations  
    --full      Tier 3: Full analysis with decision extraction (default for backwards compat)
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# File categorization
CATEGORY_MAP = {
    ".md": "documentation",
    ".py": "script",
    ".js": "script",
    ".ts": "script",
    ".json": "data",
    ".jsonl": "data",
    ".yaml": "config",
    ".yml": "config",
    ".txt": "text",
    ".log": "log",
    ".sql": "schema",
    ".sh": "script",
}

# Files to exclude from analysis
EXCLUDE_PATTERNS = [
    "SESSION_STATE.md",
    "DEBUG_LOG.jsonl",
    "__pycache__",
    ".pyc",
    ".git",
]

# Destination recommendations based on file type/content
DESTINATION_RULES = {
    "documentation": "/home/workspace/Documents",
    "script": "/home/workspace/N5/scripts",
    "data": "/home/workspace/N5/data",
    "config": "/home/workspace/N5/config",
    "schema": "/home/workspace/N5/schemas",
    "log": None,  # Leave in place or delete
}


def categorize_file(filepath: Path) -> str:
    """Categorize file based on extension and content."""
    suffix = filepath.suffix.lower()
    return CATEGORY_MAP.get(suffix, "other")


def should_exclude(filepath: Path) -> bool:
    """Check if file should be excluded from analysis."""
    path_str = str(filepath)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)


def analyze_quick(convo_path: Path, convo_id: str) -> dict:
    """
    Tier 1 Quick Analysis
    - List files
    - Basic counts
    - No deep content analysis
    """
    result = {
        "convo_id": convo_id,
        "mode": "quick",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "summary": {
            "total_files": 0,
            "by_category": {},
        },
        "files": [],
    }
    
    if not convo_path.exists():
        logger.warning(f"Conversation path does not exist: {convo_path}")
        return result
    
    for f in convo_path.rglob("*"):
        if not f.is_file() or should_exclude(f):
            continue
        
        category = categorize_file(f)
        rel_path = f.relative_to(convo_path)
        
        result["files"].append({
            "path": str(rel_path),
            "category": category,
            "size_bytes": f.stat().st_size,
        })
        
        result["summary"]["total_files"] += 1
        result["summary"]["by_category"][category] = \
            result["summary"]["by_category"].get(category, 0) + 1
    
    logger.info(f"Quick analysis complete: {result['summary']['total_files']} files")
    return result


def analyze_standard(convo_path: Path, convo_id: str) -> dict:
    """
    Tier 2 Standard Analysis
    - All quick analysis
    - Destination recommendations
    - File content preview (first 500 chars)
    """
    # Start with quick analysis
    result = analyze_quick(convo_path, convo_id)
    result["mode"] = "standard"
    result["recommendations"] = []
    
    # Add recommendations for each file
    for file_info in result["files"]:
        filepath = convo_path / file_info["path"]
        category = file_info["category"]
        
        # Add destination recommendation
        dest = DESTINATION_RULES.get(category)
        
        recommendation = {
            "file": file_info["path"],
            "action": "move" if dest else "review",
            "destination": dest,
            "reason": f"Standard location for {category} files" if dest else "Needs manual review",
        }
        
        # Add content preview for documentation
        if category == "documentation" and filepath.exists():
            try:
                content = filepath.read_text()[:500]
                file_info["preview"] = content
            except Exception as e:
                file_info["preview"] = f"Error reading: {e}"
        
        result["recommendations"].append(recommendation)
    
    # Summary of recommendations
    result["summary"]["files_to_move"] = len([r for r in result["recommendations"] if r["action"] == "move"])
    result["summary"]["files_to_review"] = len([r for r in result["recommendations"] if r["action"] == "review"])
    
    logger.info(f"Standard analysis complete: {result['summary']['files_to_move']} to move, {result['summary']['files_to_review']} to review")
    return result


def analyze_full(convo_path: Path, convo_id: str) -> dict:
    """
    Tier 3 Full Analysis
    - All standard analysis
    - Full content for documentation files
    - Decision/outcome markers detection
    - Artifact classification (deliverable vs scratch)
    """
    # Start with standard analysis
    result = analyze_standard(convo_path, convo_id)
    result["mode"] = "full"
    result["artifacts"] = {
        "deliverables": [],
        "scratch": [],
        "unknown": [],
    }
    result["markers"] = {
        "decisions": [],
        "outcomes": [],
        "todos": [],
    }
    
    # Deep analyze each file
    for file_info in result["files"]:
        filepath = convo_path / file_info["path"]
        
        if not filepath.exists():
            continue
        
        # Classify as deliverable or scratch
        is_deliverable = False
        reasons = []
        
        # Check filename patterns
        filename = filepath.name.lower()
        if any(pattern in filename for pattern in ["report", "summary", "plan", "spec", "design"]):
            is_deliverable = True
            reasons.append("filename_pattern")
        
        # Check file size (larger files more likely deliverables)
        if file_info["size_bytes"] > 5000:
            is_deliverable = True
            reasons.append("substantial_size")
        
        # Check content for markers
        if filepath.suffix in [".md", ".txt"]:
            try:
                content = filepath.read_text().lower()
                
                # Decision markers
                if "decision:" in content or "decided:" in content or "we agreed" in content:
                    result["markers"]["decisions"].append(file_info["path"])
                    is_deliverable = True
                    reasons.append("contains_decisions")
                
                # Outcome markers
                if "completed" in content or "built" in content or "implemented" in content:
                    result["markers"]["outcomes"].append(file_info["path"])
                    is_deliverable = True
                    reasons.append("contains_outcomes")
                
                # TODO markers
                if "todo:" in content or "- [ ]" in content:
                    result["markers"]["todos"].append(file_info["path"])
                
            except Exception:
                pass
        
        # Classify
        if is_deliverable:
            result["artifacts"]["deliverables"].append({
                "path": file_info["path"],
                "reasons": reasons,
            })
        elif file_info["category"] in ["log", "data"]:
            result["artifacts"]["scratch"].append(file_info["path"])
        else:
            result["artifacts"]["unknown"].append(file_info["path"])
    
    # Update summary
    result["summary"]["deliverables"] = len(result["artifacts"]["deliverables"])
    result["summary"]["scratch"] = len(result["artifacts"]["scratch"])
    result["summary"]["decisions_found"] = len(result["markers"]["decisions"])
    result["summary"]["todos_found"] = len(result["markers"]["todos"])
    
    logger.info(f"Full analysis complete: {result['summary']['deliverables']} deliverables, {result['summary']['decisions_found']} decisions")
    return result


def analyze_conversation(workspace_path: str, convo_id: str, mode: str = "full") -> dict:
    """
    Main entry point - analyze conversation based on mode.
    
    Args:
        workspace_path: Base path for conversation workspaces
        convo_id: Conversation ID (with or without con_ prefix)
        mode: Analysis mode - quick, standard, or full
    
    Returns:
        Analysis result dict
    """
    # Normalize convo_id
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    
    convo_path = Path(workspace_path) / convo_id
    
    logger.info(f"Analyzing conversation {convo_id} in {mode} mode")
    
    if mode == "quick":
        return analyze_quick(convo_path, convo_id)
    elif mode == "standard":
        return analyze_standard(convo_path, convo_id)
    else:
        return analyze_full(convo_path, convo_id)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze conversation workspace for end-of-conversation processing"
    )
    parser.add_argument(
        "--workspace",
        default="/home/.z/workspaces",
        help="Base workspace path (default: /home/.z/workspaces)"
    )
    parser.add_argument(
        "--convo-id",
        required=True,
        help="Conversation ID (with or without con_ prefix)"
    )
    parser.add_argument(
        "--mode",
        choices=["quick", "standard", "full"],
        default="full",
        help="Analysis mode (default: full)"
    )
    # Convenience aliases
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Shortcut for --mode quick"
    )
    parser.add_argument(
        "--standard",
        action="store_true",
        help="Shortcut for --mode standard"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Handle convenience flags
    mode = args.mode
    if args.quick:
        mode = "quick"
    elif args.standard:
        mode = "standard"
    
    result = analyze_conversation(args.workspace, args.convo_id, mode)
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Analysis written to: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()

