#!/usr/bin/env python3
"""Fail-safe context validators for close skills."""

import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

BUILDS_DIR = Path("/home/workspace/N5/builds")
WORKSPACES_DIR = Path("/home/.z/workspaces")


def load_session_state(convo_id: str) -> dict:
    """Load SESSION_STATE.md frontmatter for a conversation."""
    state_path = Path(f"/home/.z/workspaces/{convo_id}/SESSION_STATE.md")
    if not state_path.exists():
        return {}
    
    content = state_path.read_text()
    if not content.startswith('---'):
        return {}
    
    # Extract YAML frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    try:
        return yaml.safe_load(parts[1]) or {}
    except:
        return {}


def detect_context(state: dict) -> str:
    """Detect conversation context type.
    
    Returns: "drop" | "build" | "thread"
    """
    # Pulse Drop (headless worker)
    if state.get('drop_id') or state.get('worker_id'):
        return "drop"
    
    # Build context (orchestrator or post-build)
    if state.get('build_slug') and not state.get('drop_id'):
        return "build"
    
    # Normal interactive thread
    return "thread"


def get_build_meta(build_slug: str) -> Optional[Dict[str, Any]]:
    """Load build meta.json if it exists."""
    meta_path = BUILDS_DIR / build_slug / "meta.json"
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text())
        except:
            return None
    return None


def detect_orchestrator_context(convo_id: str) -> Dict[str, Any]:
    """Detect if this thread has a parent orchestrator or is one.
    
    Returns dict with:
    - is_orchestrator: bool - True if this thread coordinates workers
    - is_worker: bool - True if this is a drop/worker thread
    - parent_convo_id: str or None - The orchestrator's conversation ID
    - parent_title: str or None - The orchestrator's title (if resolvable)
    - build_slug: str or None - Associated build slug
    - build_title: str or None - Build title from meta.json
    """
    state = load_session_state(convo_id)
    
    result = {
        'is_orchestrator': state.get('mode') == 'orchestrator',
        'is_worker': bool(state.get('drop_id') or state.get('worker_id')),
        'parent_convo_id': None,
        'parent_title': None,
        'build_slug': state.get('build_slug') or state.get('build'),
        'build_title': None,
    }
    
    # Direct parent reference
    parent_id = state.get('orchestrator_id') or state.get('parent_convo_id')
    if parent_id:
        result['parent_convo_id'] = parent_id
        # Try to get parent's title
        result['parent_title'] = _get_convo_title(parent_id)
    
    # Build context - look up orchestrator from meta.json
    if result['build_slug']:
        meta = get_build_meta(result['build_slug'])
        if meta:
            result['build_title'] = meta.get('title')
            # Check if meta tracks orchestrator conversation
            orch_id = meta.get('orchestrator_convo_id')
            if orch_id and not result['parent_convo_id']:
                result['parent_convo_id'] = orch_id
                result['parent_title'] = _get_convo_title(orch_id)
    
    return result


def _get_convo_title(convo_id: str) -> Optional[str]:
    """Get a conversation's title from CLOSE_OUTPUT.json or SESSION_STATE."""
    workspace = WORKSPACES_DIR / convo_id
    
    # Try CLOSE_OUTPUT.json first
    close_output = workspace / "CLOSE_OUTPUT.json"
    if close_output.exists():
        try:
            data = json.loads(close_output.read_text())
            return data.get('title')
        except:
            pass
    
    # Try SESSION_STATE.md
    state_path = workspace / "SESSION_STATE.md"
    if state_path.exists():
        try:
            content = state_path.read_text()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    state = yaml.safe_load(parts[1]) or {}
                    return state.get('focus') or state.get('title')
        except:
            pass
    
    return None


def find_build_for_conversation(convo_id: str) -> Optional[str]:
    """Search builds to find which one this conversation belongs to.
    
    Useful when SESSION_STATE doesn't have build_slug but the thread
    is actually part of a build (e.g., resuming work in a new thread).
    """
    if not BUILDS_DIR.exists():
        return None
    
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue
        meta_path = build_dir / "meta.json"
        if not meta_path.exists():
            continue
        
        try:
            meta = json.loads(meta_path.read_text())
            
            # Check if this is the orchestrator
            if meta.get('orchestrator_convo_id') == convo_id:
                return build_dir.name
            
            # Check if this is a drop conversation
            drops = meta.get('drops', {})
            for drop_id, drop_info in drops.items():
                if drop_info.get('conversation_id') == convo_id:
                    return build_dir.name
        except:
            continue
    
    return None


def warn_wrong_skill(called: str, suggested: str, reason: str) -> None:
    """Print warning about wrong skill being called."""
    print(f"""
⚠️  WRONG SKILL DETECTED

You called: {called}
Suggested:  {suggested}
Reason:     {reason}

Run the suggested skill instead, or use --force to override.
""", file=sys.stderr)


def validate_thread_context(state: dict) -> Tuple[bool, str]:
    """Validate context is appropriate for thread-close."""
    ctx = detect_context(state)
    
    if ctx == "drop":
        return False, "SESSION_STATE has drop_id — use drop-close instead"
    
    if ctx == "build":
        return False, "Build context detected — use build-close instead"
    
    return True, "OK"


def validate_drop_context(state: dict) -> Tuple[bool, str]:
    """Validate context is appropriate for drop-close."""
    ctx = detect_context(state)
    
    if ctx == "thread":
        return False, "No drop context — use thread-close instead"
    
    if ctx == "build" and not state.get('drop_id'):
        return False, "Build orchestrator context — use build-close instead"
    
    if not state.get('build_slug'):
        return False, "Missing build_slug in SESSION_STATE"
    
    return True, "OK"


def validate_build_context(slug: str) -> Tuple[bool, str]:
    """Validate context is appropriate for build-close."""
    build_dir = BUILDS_DIR / slug
    
    if not build_dir.exists():
        return False, f"Build not found: {slug}"
    
    meta_path = build_dir / "meta.json"
    if not meta_path.exists():
        return False, f"No meta.json in build: {slug}"
    
    meta = json.loads(meta_path.read_text())
    
    # Check build is in terminal state
    if meta.get('status') not in ('complete', 'closed', 'partial', 'failed'):
        return False, f"Build not finished (status: {meta.get('status')})"
    
    # Check there are deposits to synthesize
    deposits_dir = build_dir / "deposits"
    if not deposits_dir.exists() or not list(deposits_dir.glob("D*.json")):
        return False, "No deposits found to synthesize"
    
    return True, "OK"


def enrich_state_with_build_context(state: dict, convo_id: str) -> dict:
    """Enrich SESSION_STATE with build context if discoverable.
    
    Useful when a thread picks up an old build but doesn't have build_slug set.
    Returns enriched copy of state (doesn't modify original).
    """
    enriched = state.copy()
    
    # If we already have build context, nothing to do
    if enriched.get('build_slug'):
        return enriched
    
    # Try to find a build this conversation belongs to
    build_slug = find_build_for_conversation(convo_id)
    if build_slug:
        enriched['build_slug'] = build_slug
        meta = get_build_meta(build_slug)
        if meta:
            enriched['_build_title'] = meta.get('title')
            enriched['_orchestrator_convo_id'] = meta.get('orchestrator_convo_id')
    
    return enriched
