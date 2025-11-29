#!/usr/bin/env python3
"""
Conversation End Proposal Generator
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def generate_proposal(analysis_file, output_file):
    with open(analysis_file) as f:
        analysis = json.load(f)

    convo_id = analysis["convo_id"]

    # Derive a generic but conversation-specific title; analyzer may later populate summary
    title = analysis.get("summary") or f"Conversation {convo_id} Closure Proposal"

    # Archive root follows Documents/Archive/YYYY-MM-DD_con_XXXXX/ pattern
    today_str = datetime.now().date().isoformat()
    archive_root = Path("/home/workspace/Documents/Archive") / f"{today_str}_con_{convo_id}"

    # Build proposal from analysis
    proposal = {
        # Legacy field used by earlier tools
        "convo_id": convo_id,
        # Fields required by ConversationEndExecutor
        "conversation_id": convo_id,
        "title": title,
        "actions": [],
        # Execution control fields consumed by executor
        "requires_resolution": False,
        "conflicts": [],
        # Additional metadata used by higher-level workflows
        "files_to_organize": [],
        "archive_location": str(archive_root),
        "aar_required": True,
        "tasks_to_close": [],
        "git_changes": [],
        "thread_title": title,
    }

    # Identify permanent deliverables
    docs_path = Path("/home/workspace/Documents")
    for doc in analysis.get("documents", []):
        if doc.get("type") == "documentation":
            source = Path("/home/workspace") / doc["path"]
            if source.exists():
                # Keep in Documents as permanent reference (auxiliary metadata only)
                proposal["files_to_organize"].append({
                    "source": str(source),
                    "target": str(source),  # Stay in Documents
                    "action": "keep",
                })

    # Generate archive actions for conversation artifacts
    convo_workspace = Path("/home/.z/workspaces") / f"con_{convo_id}"
    actions = []

    for artifact in analysis.get("artifacts", []):
        rel_path = artifact.get("path")
        if not rel_path:
            continue

        source_path = convo_workspace / rel_path
        dest_path = archive_root / rel_path

        actions.append(
            {
                "action_type": "archive",
                "source": str(source_path),
                "destination": str(dest_path),
                "approved": True,
                "reason": "Archive conversation artifact from workspace",
                "confidence": "high",
            }
        )

    proposal["actions"] = actions

    # If archive root already exists, require human resolution before execution
    if archive_root.exists():
        proposal["requires_resolution"] = True
        proposal["conflicts"].append(
            {
                "type": "archive_path_exists",
                "description": f"Archive path already exists: {archive_root}",
            }
        )

    # Write output
    with open(output_file, "w") as f:
        json.dump(proposal, f, indent=2)

    print(f"Proposal generated: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()
    generate_proposal(args.analysis, args.output)


