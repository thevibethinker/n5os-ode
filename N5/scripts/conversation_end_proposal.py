#!/usr/bin/env python3
"""
Conversation End Proposal Generator
"""

import json
import argparse
from pathlib import Path

def generate_proposal(analysis_file, output_file):
    with open(analysis_file) as f:
        analysis = json.load(f)
    
    # Build proposal from analysis
    proposal = {
        "convo_id": analysis["convo_id"],
        "files_to_organize": [],
        "archive_location": None,
        "aar_required": True,
        "tasks_to_close": [],
        "git_changes": [],
        "thread_title": "Vibe Level Upper Creation and Integration"
    }
    
    # Identify permanent deliverables
    docs_path = Path("/home/workspace/Documents")
    for doc in analysis.get("documents", []):
        if doc.get("type") == "documentation":
            source = Path("/home/workspace") / doc["path"]
            if source.exists():
                # Keep in Documents as permanent reference
                proposal["files_to_organize"].append({
                    "source": str(source),
                    "target": str(source),  # Stay in Documents
                    "action": "keep"
                })
    
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
