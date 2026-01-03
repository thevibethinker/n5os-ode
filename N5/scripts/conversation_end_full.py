#!/usr/bin/env python3
"""
Conversation End - Tier 3 (Full Build Close) v3.0

Complete conversation close for build/orchestrator sessions.
Includes AAR generation, lesson extraction, capability registry,
and build tracker archival.

Cost target: <$0.15 | Time target: <180 seconds

Builds on Tier 2, adding:
- After-Action Report (AAR) generation
- Lesson extraction to project_log.jsonl
- Capability registry check (prompts LLM)
- Build workspace archival
- Thread export

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


def extract_lessons_from_session(session_state: Dict, convo_path: Path) -> List[Dict]:
    """Extract potential lessons from conversation artifacts."""
    lessons = []
    
    # Check for debug patterns (indicates troubleshooting = potential lesson)
    debug_log = find_debug_log(convo_path)
    if debug_log:
        try:
            with open(debug_log) as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if entry.get("outcome") == "success":
                        lessons.append({
                            "type": "process",
                            "source": "debug_log",
                            "lesson": f"Fixed: {entry.get('problem', 'unknown issue')}",
                            "context": entry.get("actions", [])
                        })
        except Exception as e:
            logger.warning(f"Could not parse debug log: {e}")
    
    # Check session state for architectural decisions
    if session_state.get("type") in ["build", "orchestrator"]:
        focus = session_state.get("focus", "")
        if any(kw in focus.lower() for kw in ["architecture", "design", "system", "refactor"]):
            lessons.append({
                "type": "architecture",
                "source": "session_state",
                "lesson": f"Architectural work: {focus}",
                "context": session_state.get("progress", [])
            })
    
    return lessons


def generate_aar_structure(
    convo_id: str,
    session_state: Dict,
    tier2_result: Dict,
    build_workspace: Optional[Path],
    lessons: List[Dict]
) -> Dict:
    """Generate AAR data structure for LLM enhancement."""
    
    aar = {
        "metadata": {
            "convo_id": convo_id,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "type": session_state.get("type", "build"),
            "focus": session_state.get("focus", "Unknown"),
        },
        "summary": {
            "objective": session_state.get("objective", "Not specified"),
            "outcome": "Completed" if tier2_result.get("success") else "Incomplete",
            "duration": tier2_result.get("duration_seconds", 0),
        },
        "what_happened": {
            "progress": session_state.get("progress", []),
            "decisions": tier2_result.get("content_analysis", {}).get("decisions", []),
            "artifacts_created": tier2_result.get("files", []),
        },
        "lessons_learned": lessons,
        "build_info": None,
        "next_steps": session_state.get("open_items", []),
    }
    
    # Add build workspace info if present
    if build_workspace:
        plan_file = build_workspace / "PLAN.md"
        aar["build_info"] = {
            "build_slug": build_workspace.name,
            "plan_exists": plan_file.exists(),
            "path": str(build_workspace),
        }
    
    return aar


def format_aar_markdown(aar: Dict) -> str:
    """Format AAR as markdown for human review."""
    lines = [
        "---",
        f"created: {aar['metadata']['date']}",
        f"last_edited: {aar['metadata']['date']}",
        "version: 1.0",
        f"provenance: {aar['metadata']['convo_id']}",
        "---",
        "",
        f"# After-Action Report: {aar['metadata']['focus']}",
        "",
        f"**Date:** {aar['metadata']['date']}",
        f"**Type:** {aar['metadata']['type']}",
        f"**Conversation:** {aar['metadata']['convo_id']}",
        "",
        "## Objective",
        "",
        aar['summary']['objective'] or "Not specified",
        "",
        "## What Happened",
        "",
    ]
    
    # Progress
    if aar['what_happened']['progress']:
        lines.append("### Progress")
        for item in aar['what_happened']['progress']:
            lines.append(f"- {item}")
        lines.append("")
    
    # Decisions
    if aar['what_happened']['decisions']:
        lines.append("### Key Decisions")
        for decision in aar['what_happened']['decisions']:
            lines.append(f"- {decision}")
        lines.append("")
    
    # Artifacts
    if aar['what_happened']['artifacts_created']:
        lines.append("### Artifacts Created")
        for artifact in aar['what_happened']['artifacts_created']:
            if isinstance(artifact, dict):
                lines.append(f"- `{artifact.get('name', 'unknown')}`")
            else:
                lines.append(f"- `{artifact}`")
        lines.append("")
    
    # Lessons
    lines.append("## Lessons Learned")
    lines.append("")
    if aar['lessons_learned']:
        for lesson in aar['lessons_learned']:
            lines.append(f"### {lesson.get('type', 'General').title()}")
            lines.append(f"- {lesson.get('lesson', 'No lesson captured')}")
            lines.append("")
    else:
        lines.append("- No specific lessons extracted (LLM should analyze)")
        lines.append("")
    
    # Build info
    if aar['build_info']:
        lines.extend([
            "## Build Information",
            "",
            f"- **Build:** `{aar['build_info']['build_slug']}`",
            f"- **Plan:** {'✓ Exists' if aar['build_info']['plan_exists'] else '✗ Missing'}",
            f"- **Path:** `{aar['build_info']['path']}`",
            "",
        ])
    
    # Next steps
    lines.append("## Next Steps")
    lines.append("")
    if aar['next_steps']:
        for item in aar['next_steps']:
            lines.append(f"- {item}")
    else:
        lines.append("- None identified")
    lines.append("")
    
    # Outcome
    lines.extend([
        "## Outcome",
        "",
        f"**Status:** {aar['summary']['outcome']}",
        "",
    ])
    
    return "\n".join(lines)


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
    """Execute Tier 3 full build close."""
    start_time = datetime.now(timezone.utc)
    result = {
        "tier": 3,
        "convo_id": convo_id,
        "success": False,
        "errors": [],
        "warnings": [],
        "aar": None,
        "lessons": [],
        "build_archive": None,
        "capability_check": "pending_llm",  # LLM will handle this
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
    
    # Get session state
    session_state = tier2_result.get("session_state", {})
    
    # Find build workspace
    logger.info("Checking for build workspace...")
    build_workspace = find_build_workspace(convo_id.replace("con_", ""))
    if build_workspace:
        logger.info(f"Found build workspace: {build_workspace.name}")
    
    # Extract lessons
    logger.info("Extracting lessons...")
    lessons = extract_lessons_from_session(session_state, convo_path)
    result["lessons"] = lessons

    # Record lessons to registry
    if lessons and not dry_run:
        try:
            from conversation_registry import ConversationRegistry
            registry = ConversationRegistry()
            for idx, lesson in enumerate(lessons):
                lesson_data = {
                    "lesson_id": f"L_{convo_id}_{lesson.get('type', 'general')}_{idx}_{int(start_time.timestamp())}",
                    "timestamp": start_time.isoformat(),
                    "type": lesson.get("type", "process"),
                    "title": lesson.get("lesson", "Untitled lesson")[:100],
                    "description": lesson.get("lesson", ""),
                    "principle_refs": [],
                    "status": "pending"
                }
                registry.import_learning(convo_id, lesson_data)
            logger.info(f"Recorded {len(lessons)} lessons to registry")
        except Exception as e:
            logger.warning(f"Registry learning recording skipped: {e}")

    # Generate AAR
    logger.info("Generating AAR structure...")
    aar = generate_aar_structure(
        convo_id,
        session_state,
        tier2_result,
        build_workspace,
        lessons
    )
    result["aar"] = aar
    
    # Archive build workspace
    if build_workspace:
        logger.info("Archiving build workspace...")
        archive_result = archive_build_workspace(build_workspace, convo_id, dry_run)
        result["build_archive"] = archive_result
    
    # Save AAR if not dry run
    aar_markdown = format_aar_markdown(aar)
    if not dry_run:
        AAR_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        focus_slug = re.sub(r'[^a-zA-Z0-9]+', '_', aar['metadata']['focus'])[:30]
        aar_filename = f"{date_str}_{focus_slug}.md"
        aar_path = AAR_DIR / aar_filename
        aar_path.write_text(aar_markdown)
        result["aar_path"] = str(aar_path)
        logger.info(f"AAR saved to: {aar_path}")
    
    # Calculate duration
    end_time = datetime.now(timezone.utc)
    result["duration_seconds"] = (end_time - start_time).total_seconds()
    
    # Format output
    result["output"] = format_full_output(result, tier2_result, aar_markdown)
    result["success"] = True
    
    logger.info(f"Full close complete in {result['duration_seconds']:.2f}s")
    return result


def format_full_output(result: Dict, tier2_result: Dict, aar_markdown: str) -> str:
    """Format complete Tier 3 output."""
    lines = [
        "## Build Conversation Closed",
        "",
        f"**Title:** {tier2_result.get('title', 'Unknown')}",
        f"**Type:** {result['aar']['metadata']['type']}",
        f"**Duration:** {result['duration_seconds']:.1f}s",
        "",
    ]
    
    # Include AAR - strip YAML frontmatter for inline display
    aar_display = aar_markdown
    # Remove YAML frontmatter (everything between first --- and second ---)
    if aar_display.startswith("---"):
        parts = aar_display.split("---", 2)
        if len(parts) >= 3:
            aar_display = parts[2].strip()
    
    lines.append(aar_display)
    lines.append("")
    
    # Lessons
    if result["lessons"]:
        lines.append("### Extracted Lessons")
        for lesson in result["lessons"]:
            lines.append(f"- **{lesson['type']}:** {lesson['lesson']}")
        lines.append("")
    
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
    
    # Capability registry reminder
    lines.extend([
        "### Capability Registry",
        "",
        "**LLM Action Required:** Review if this conversation created or modified N5 capabilities.",
        "- If yes: Update capability registry",
        "- If no: Note 'No capability changes'",
        "",
    ])
    
    # Git status from Tier 2
    git_status = tier2_result.get("git_status", {})
    if git_status.get("has_changes"):
        lines.append(f"### Git Status")
        lines.append(f"⚠️ {git_status.get('summary', 'Changes detected')}")
        lines.append("→ Consider committing before closing")
        lines.append("")
    
    lines.append("✅ Full build close complete")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Tier 3 Full Build Close")
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




