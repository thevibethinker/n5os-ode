#!/usr/bin/env python3
"""Content library candidate detection."""

from pathlib import Path
from typing import List

def scan_conversation(convo_id: str) -> List[str]:
    """Scan conversation workspace for content library candidates."""
    workspace = Path(f"/home/.z/workspaces/{convo_id}")
    candidates = []
    
    # Look for POV documents
    for f in workspace.glob("**/V-POV-*.md"):
        candidates.append(f"POV: {f.name}")
    
    # Look for frameworks
    for f in workspace.glob("**/*framework*.md"):
        candidates.append(f"Framework: {f.name}")
    
    return candidates

def scan_build(slug: str) -> List[str]:
    """Scan build artifacts for content library candidates."""
    build_dir = Path(f"/home/workspace/N5/builds/{slug}/artifacts")
    candidates = []
    
    if build_dir.exists():
        for f in build_dir.glob("*.md"):
            candidates.append(f"Artifact: {f.name}")
    
    return candidates