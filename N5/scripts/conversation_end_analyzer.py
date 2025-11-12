#!/usr/bin/env python3
"""
Conversation End Analyzer - Analyzes conversation to identify built artifacts and discussion content
"""

import json
import sys
from pathlib import Path
import argparse

def analyze_conversation(workspace_path, convo_id):
    """Analyze conversation workspace to identify deliverables"""
    
    analysis = {
        "convo_id": convo_id,
        "artifacts": [],
        "personas": [],
        "rules": [],
        "documents": [],
        "summary": ""
    }
    
    # Analyze conversation workspace
    convo_path = Path(workspace_path) / f"con_{convo_id}"
    if convo_path.exists():
        # List all files
        files = list(convo_path.rglob("*"))
        for f in files:
            if f.is_file():
                rel_path = f.relative_to(convo_path)
                analysis["artifacts"].append({
                    "path": str(rel_path),
                    "type": f.suffix or "text",
                    "size": f.stat().st_size
                })
    
    # Analyze user workspace for persistent deliverables
    user_docs = Path("/home/workspace/Documents")
    if user_docs.exists():
        docs = list(user_docs.glob("*Level_Upper*"))
        for doc in docs:
            analysis["documents"].append({
                "path": str(doc.relative_to("/home/workspace")),
                "type": "documentation",
                "created": True
            })
    
    return analysis

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--convo-id", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    result = analyze_conversation(args.workspace, args.convo_id)
    
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Analysis complete: {args.output}")
