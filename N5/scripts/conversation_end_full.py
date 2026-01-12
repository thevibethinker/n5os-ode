#!/usr/bin/env python3
"""
Conversation End - Tier 3 (Full Build Close) v4.0

Gathers mechanical context for build/orchestrator sessions.
AAR GENERATION IS OWNED BY LIBRARIAN (LLM), NOT THIS SCRIPT.

This script provides:
- Build workspace detection
- Debug log analysis
- Git status
- File lists
- Raw SESSION_STATE content

The LLM (Librarian) then:
- Semantically analyzes the conversation
- Writes the AAR with real understanding
- Extracts lessons through reasoning, not regex

Cost target: <$0.15 | Time target: <180 seconds

Usage:
    python3 conversation_end_full.py --convo-id <id> [--dry-run] [--json]
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Import Tier 2 functionality
sys.path.insert(0, str(Path(__file__).parent))
from conversation_end_standard import run_standard_close, get_git_status

WORKSPACE_ROOT = Path("/home/workspace")
CONVO_WORKSPACE_ROOT = Path("/home/.z/workspaces")
N5_ROOT = WORKSPACE_ROOT / "N5"
BUILDS_DIR = N5_ROOT / "builds"
THREADS_DIR = N5_ROOT / "logs" / "threads"
AAR_DIR = WORKSPACE_ROOT / "Records" / "AARs"


def find_build_workspace(convo_id: str) -> Optional[Path]:
    """Find build workspace associated with this conversation."""
    # Check if conversation created a build
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue
        
        plan_file = build_dir / "PLAN.md"
        status_file = build_dir / "STATUS.md"
        
        for check_file in [plan_file, status_file]:
            if check_file.exists():
                content = check_file.read_text()
                if convo_id in content:
                    return build_dir
    
    return None


def find_debug_log(convo_path: Path) -> Optional[Path]:
    """Find DEBUG_LOG.jsonl if present."""
    debug_log = convo_path / "DEBUG_LOG.jsonl"
    if debug_log.exists():
        return debug_log
    return None


def read_debug_log_entries(debug_log_path: Path) -> List[Dict]:
    """Read debug log entries for context."""
    entries = []
    try:
        with open(debug_log_path) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    except Exception as e:
        logger.warning(f"Could not parse debug log: {e}")
    return entries


def read_session_state_raw(convo_path: Path) -> Optional[str]:
    """Read raw SESSION_STATE.md content for LLM analysis."""
    session_file = convo_path / "SESSION_STATE.md"
    if session_file.exists():
        return session_file.read_text()
    return None


def read_build_context(build_workspace: Optional[Path]) -> Dict:
    """Read build workspace files for context."""
    if not build_workspace or not build_workspace.exists():
        return {"exists": False}
    
    context = {
        "exists": True,
        "slug": build_workspace.name,
        "path": str(build_workspace),
        "plan_content": None,
        "status_content": None,
    }
    
    plan_file = build_workspace / "PLAN.md"
    if plan_file.exists():
        context["plan_content"] = plan_file.read_text()
    
    status_file = build_workspace / "STATUS.md"
    if status_file.exists():
        context["status_content"] = status_file.read_text()
    
    return context


def generate_context_bundle(
    convo_id: str,
    convo_path: Path,
    tier2_result: Dict,
    build_workspace: Optional[Path],
    debug_log_path: Optional[Path]
) -> Dict:
    """
    Generate context bundle for LLM to write AAR.
    
    This is MECHANICAL GATHERING only. No semantic analysis.
    The LLM will do the actual reasoning.
    """
    bundle = {
        "metadata": {
            "convo_id": convo_id,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "convo_workspace": str(convo_path),
            "aar_output_dir": str(AAR_DIR),
        },
        "session_state_raw": read_session_state_raw(convo_path),
        "files": tier2_result.get("files", []),
        "git_status": tier2_result.get("git_status", {}),
        "build_context": read_build_context(build_workspace),
        "debug_log_entries": [],
    }
    
    # Read debug log if present
    if debug_log_path:
        bundle["debug_log_entries"] = read_debug_log_entries(debug_log_path)
    
    return bundle


def archive_build_workspace(build_workspace: Path, convo_id: str, dry_run: bool = False) -> Dict:
    """Archive build workspace to threads directory."""
    if not build_workspace or not build_workspace.exists():
        return {"archived": False, "reason": "No build workspace"}
    
    # Create thread archive directory
    date_str = datetime.now().strftime("%Y-%m-%d")
    thread_name = f"{date_str}_{build_workspace.name}_{convo_id[:8]}"
    archive_dir = THREADS_DIR / thread_name
    
    if dry_run:
        return {
            "archived": False,
            "dry_run": True,
            "would_archive_to": str(archive_dir),
            "source": str(build_workspace),
        }
    
    # Create archive
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy PLAN.md and STATUS.md
    for filename in ["PLAN.md", "STATUS.md", "DEBUG_LOG.jsonl"]:
        src = build_workspace / filename
        if src.exists():
            dst = archive_dir / filename
            dst.write_text(src.read_text())
    
    return {
        "archived": True,
        "archive_path": str(archive_dir),
        "source": str(build_workspace),
    }


def run_full_close(convo_id: str, dry_run: bool = False) -> Dict:
    """Execute Tier 3 full build close - gather context for LLM."""
    start_time = datetime.now(timezone.utc)
    result = {
        "tier": 3,
        "convo_id": convo_id,
        "success": False,
        "errors": [],
        "warnings": [],
        "context_bundle": None,  # For LLM to write AAR
        "build_archive": None,
        "capability_check": "pending_llm",
        "output": "",
    }
    
    # Normalize convo_id
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    
    convo_path = CONVO_WORKSPACE_ROOT / convo_id
    
    # Run Tier 2 first to get base analysis
    logger.info("Running Tier 2 analysis...")
    tier2_result = run_standard_close(convo_id.replace("con_", ""), dry_run=True)
    
    if not tier2_result.get("success"):
        result["errors"].append(f"Tier 2 failed: {tier2_result.get('errors')}")
        return result
    
    # Find build workspace
    logger.info("Checking for build workspace...")
    build_workspace = find_build_workspace(convo_id.replace("con_", ""))
    if build_workspace:
        logger.info(f"Found build workspace: {build_workspace.name}")
    
    # Find debug log
    debug_log_path = find_debug_log(convo_path)
    if debug_log_path:
        logger.info(f"Found debug log: {debug_log_path}")
    
    # Generate context bundle for LLM
    logger.info("Generating context bundle for LLM...")
    context_bundle = generate_context_bundle(
        convo_id,
        convo_path,
        tier2_result,
        build_workspace,
        debug_log_path
    )
    result["context_bundle"] = context_bundle
    
    # Archive build workspace
    if build_workspace:
        logger.info("Archiving build workspace...")
        archive_result = archive_build_workspace(build_workspace, convo_id, dry_run)
        result["build_archive"] = archive_result
    
    # Calculate duration
    end_time = datetime.now(timezone.utc)
    result["duration_seconds"] = (end_time - start_time).total_seconds()
    
    # Format output for LLM
    result["output"] = format_full_output(result, tier2_result, context_bundle)
    result["success"] = True
    
    logger.info(f"Full close context gathering complete in {result['duration_seconds']:.2f}s")
    return result


def format_full_output(result: Dict, tier2_result: Dict, context_bundle: Dict) -> str:
    """Format output with context bundle for LLM to process."""
    lines = [
        "## Build Conversation Close - Context Gathered",
        "",
        f"**Conversation:** {result['convo_id']}",
        f"**Date:** {context_bundle['metadata']['date']}",
        f"**Duration:** {result['duration_seconds']:.1f}s",
        "",
        "---",
        "",
        "### ⚠️ AAR GENERATION REQUIRED (LLM Task)",
        "",
        "The mechanical context has been gathered. **Librarian must now:**",
        "",
        "1. **Read SESSION_STATE.md** from the conversation workspace",
        "2. **Semantically analyze** what was accomplished, decided, and learned",
        "3. **Write the AAR** with real understanding (not template-filling)",
        f"4. **Save to:** `{context_bundle['metadata']['aar_output_dir']}/`",
        "",
        "---",
        "",
        "### Context Bundle (for LLM analysis)",
        "",
        "```json",
        json.dumps(context_bundle, indent=2, default=str),
        "```",
        "",
    ]
    
    # Build archive status
    if result["build_archive"]:
        archive = result["build_archive"]
        if archive.get("archived"):
            lines.append(f"✅ Build archived to: `{archive['archive_path']}`")
        elif archive.get("dry_run"):
            lines.append(f"📦 Would archive to: `{archive['would_archive_to']}`")
        else:
            lines.append(f"⚠️ Build not archived: {archive.get('reason', 'unknown')}")
        lines.append("")
    
    # Git status from Tier 2
    git_status = tier2_result.get("git_status", {})
    if git_status.get("has_changes"):
        lines.append("### Git Status")
        lines.append(f"⚠️ {git_status.get('summary', 'Changes detected')}")
        lines.append("→ Consider committing before closing")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("**Next:** Invoke Librarian to write AAR with semantic analysis.")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Tier 3 Full Build Close - Context Gathering")
    parser.add_argument("--convo-id", required=True, help="Conversation ID")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Write output to file")
    
    args = parser.parse_args()
    
    result = run_full_close(args.convo_id, args.dry_run)
    
    if args.json:
        output = json.dumps(result, indent=2, default=str)
    else:
        output = result["output"] if result["success"] else f"Error: {result['errors']}"
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to: {args.output}")
    else:
        print(output)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()





