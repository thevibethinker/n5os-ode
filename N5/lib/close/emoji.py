#!/usr/bin/env python3
"""3-slot emoji system for thread titles.

Title Format: MMM DD | {state} {type} {content} [parent_context] Semantic Title

Parent context in square brackets when:
- Thread is a worker/drop in a build → [build_title]
- Thread continues work from a parent orchestrator → [orchestrator_title]
- Thread references an existing build → [build_title]
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Load emoji legend
EMOJI_LEGEND_PATH = Path("/home/workspace/N5/config/emoji-legend.json")
BUILDS_DIR = Path("/home/workspace/N5/builds")
WORKSPACES_DIR = Path("/home/.z/workspaces")

def load_legend() -> dict:
    """Load emoji legend from config."""
    if EMOJI_LEGEND_PATH.exists():
        return json.loads(EMOJI_LEGEND_PATH.read_text())
    return {}

# State emojis (slot 1)
STATE_EMOJIS = {
    'complete': '✅',
    'paused': '⏸️',
    'in_progress': '🚧',
    'failed': '❌',
    'critical': '‼️',
}

# Type emojis (slot 2)
TYPE_EMOJIS = {
    'normal': '📌',
    'orchestrator': '🐙',
    'worker': '👷🏽‍♂️',
    'linked': '🔗',
}

# Content emojis (slot 3)
CONTENT_EMOJIS = {
    'build': '🏗️',
    'research': '🔎',
    'repair': '🛠️',
    'site': '🕸️',
    'log': '🪵',
    'content': '✍️',
    'reflection': '🪞',
    'social': '🤳',
    'data': '📊',
    'comms': '💬',
    'organize': '🗂️',
    'planning': '📝',
}


def get_build_meta(build_slug: str) -> Optional[Dict[str, Any]]:
    """Load build meta.json if it exists."""
    meta_path = BUILDS_DIR / build_slug / "meta.json"
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text())
        except:
            return None
    return None


def get_conversation_title(convo_id: str) -> Optional[str]:
    """Try to get the title of a conversation from its CLOSE_OUTPUT.json or SESSION_STATE."""
    workspace = WORKSPACES_DIR / convo_id
    
    # Try CLOSE_OUTPUT.json first (already closed conversations)
    close_output = workspace / "CLOSE_OUTPUT.json"
    if close_output.exists():
        try:
            data = json.loads(close_output.read_text())
            return data.get('title')
        except:
            pass
    
    # Try SESSION_STATE.md focus field
    state_path = workspace / "SESSION_STATE.md"
    if state_path.exists():
        try:
            content = state_path.read_text()
            if content.startswith('---'):
                import yaml
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    state = yaml.safe_load(parts[1]) or {}
                    return state.get('focus') or state.get('title')
        except:
            pass
    
    return None


def resolve_parent_context(state: dict, convo_id: str) -> Optional[str]:
    """Resolve parent context to display in square brackets.
    
    Priority:
    1. If thread has orchestrator_id → get orchestrator's title
    2. If thread has build_slug → get build title from meta.json
    3. If thread has parent_convo_id → get parent's title
    4. If thread has drop_id → get build title
    
    Returns the parent context string (title or slug) or None if no parent.
    """
    # Check for explicit orchestrator reference
    orchestrator_id = state.get('orchestrator_id') or state.get('parent_convo_id')
    if orchestrator_id:
        title = get_conversation_title(orchestrator_id)
        if title:
            # Extract just the semantic part (after emojis) for cleaner display
            if '|' in title:
                # Format: "Jan 24 | ✅ 📌 🏗️ Semantic Title"
                semantic_part = title.split('|', 1)[1].strip()
                # Remove emoji prefix if present
                import re
                semantic_part = re.sub(r'^[\s✅⏸️🚧❌‼️📌🐙👷🏽‍♂️🔗🏗️🔎🛠️🕸️🪵✍️🪞🤳📊💬🗂️📝\s]+', '', semantic_part)
                return semantic_part.strip() if semantic_part.strip() else None
            return title
    
    # Check for build context
    build_slug = state.get('build_slug') or state.get('build')
    if build_slug:
        meta = get_build_meta(build_slug)
        if meta:
            # First try to get orchestrator conversation title
            orchestrator_convo = meta.get('orchestrator_convo_id')
            if orchestrator_convo:
                orch_title = get_conversation_title(orchestrator_convo)
                if orch_title and '|' in orch_title:
                    import re
                    semantic_part = orch_title.split('|', 1)[1].strip()
                    semantic_part = re.sub(r'^[\s✅⏸️🚧❌‼️📌🐙👷🏽‍♂️🔗🏗️🔎🛠️🕸️🪵✍️🪞🤳📊💬🗂️📝\s]+', '', semantic_part)
                    if semantic_part.strip():
                        return semantic_part.strip()
            
            # Fall back to build title
            return meta.get('title') or build_slug
        return build_slug
    
    # Check for drop context (worker thread)
    drop_id = state.get('drop_id') or state.get('worker_id')
    if drop_id:
        # Workers should have build_slug, but just in case
        build_slug = state.get('build_slug') or state.get('build')
        if build_slug:
            meta = get_build_meta(build_slug)
            return meta.get('title') if meta else build_slug
    
    return None


def detect_state(state: dict, convo_id: str) -> str:
    """Detect thread completion state."""
    status = state.get('status', 'unknown')
    if status in ('complete', 'closed'):
        return 'complete'
    if status in ('blocked', 'failed', 'error'):
        return 'failed'
    if status == 'paused':
        return 'paused'
    if status in ('active', 'in_progress'):
        return 'in_progress'
    return 'complete'  # Default assumption at close time


def detect_type(state: dict) -> str:
    """Detect thread type."""
    if state.get('drop_id') or state.get('worker_id'):
        return 'worker'
    if state.get('mode') == 'orchestrator':
        return 'orchestrator'
    if state.get('parent_convo_id') or state.get('orchestrator_id'):
        return 'linked'
    return 'normal'


def detect_content(state: dict, convo_id: str) -> str:
    """Detect primary content type from conversation."""
    conv_type = state.get('type', '')
    
    # Direct mapping from conversation type
    type_to_content = {
        'build': 'build',
        'research': 'research',
        'planning': 'planning',
        'discussion': 'reflection',
        'debug': 'repair',
        'site': 'site',
        'content': 'content',
        'data': 'data',
        'comms': 'comms',
        'organize': 'organize',
    }
    
    if conv_type in type_to_content:
        return type_to_content[conv_type]
    
    # Check focus field for hints
    focus = (state.get('focus') or '').lower()
    for content_type, keywords in [
        ('build', ['build', 'implement', 'create', 'feature']),
        ('research', ['research', 'search', 'find', 'investigate']),
        ('repair', ['fix', 'debug', 'repair', 'troubleshoot', 'bug']),
        ('site', ['site', 'website', 'web app', 'deploy']),
        ('content', ['write', 'draft', 'article', 'post']),
        ('planning', ['plan', 'roadmap', 'design', 'architecture']),
        ('organize', ['cleanup', 'organize', 'file', 'reconcile']),
    ]:
        if any(kw in focus for kw in keywords):
            return content_type
    
    return 'build'  # Default


def generate_title(
    state: dict, 
    convo_id: str, 
    semantic_title: Optional[str] = None,
    parent_context: Optional[str] = None,
    force_state: Optional[str] = None,
    force_type: Optional[str] = None,
    force_content: Optional[str] = None
) -> str:
    """Generate full title with 3-slot emoji prefix.
    
    Format: MMM DD | {state} {type} {content} [parent_context] Semantic Title
    
    Args:
        state: SESSION_STATE data
        convo_id: Conversation ID
        semantic_title: LLM-generated descriptive title
        parent_context: Override for parent context (otherwise auto-resolved)
        force_state: Override state detection
        force_type: Override type detection
        force_content: Override content detection
    
    Returns:
        Formatted title string
    """
    # Date prefix
    date_str = datetime.now().strftime("%b %d")
    
    # 3 emoji slots
    state_key = force_state or detect_state(state, convo_id)
    type_key = force_type or detect_type(state)
    content_key = force_content or detect_content(state, convo_id)
    
    state_emoji = STATE_EMOJIS.get(state_key, '✅')
    type_emoji = TYPE_EMOJIS.get(type_key, '📌')
    content_emoji = CONTENT_EMOJIS.get(content_key, '🏗️')
    emoji_trio = f"{state_emoji} {type_emoji} {content_emoji}"
    
    # Resolve parent context if not provided
    if parent_context is None:
        parent_context = resolve_parent_context(state, convo_id)
    
    # Semantic title
    title = semantic_title or state.get('focus', 'Untitled')
    
    # Build final title
    if parent_context:
        return f"{date_str} | {emoji_trio} [{parent_context}] {title}"
    else:
        return f"{date_str} | {emoji_trio} {title}"


def get_emoji_reference() -> str:
    """Return formatted emoji reference for LLM consumption."""
    return """
## Emoji Reference (3-Slot System)

**Format:** `MMM DD | {state} {type} {content} [parent] Title`

### Slot 1: State
- ✅ complete — Thread completed successfully
- ⏸️ paused — Action pending, thread paused
- 🚧 in_progress — Work in progress
- ❌ failed — Thread ended with unresolved errors
- ‼️ critical — Critical action pending

### Slot 2: Type
- 📌 normal — Normal standalone thread (default)
- 🐙 orchestrator — Orchestrator coordinating workers
- 👷🏽‍♂️ worker — Worker spawned by orchestrator
- 🔗 linked — Part of a series or continuation

### Slot 3: Content
- 🏗️ build — Building functionality, features
- 🔎 research — Search, investigation
- 🛠️ repair — Debug, fix, troubleshoot
- 🕸️ site — Site/web app work
- 🪵 log — Log entries, tracking
- ✍️ content — Content creation, writing
- 🪞 reflection — Reflection, strategizing
- 🤳 social — Social media work
- 📊 data — Data work, analytics
- 💬 comms — Communications, email
- 🗂️ organize — Organization, cleanup
- 📝 planning — Planning, roadmapping

### Parent Context [in brackets]
Include when thread relates to a parent:
- Build workers → [Build Title]
- Continuation threads → [Parent Thread Title]
- Build orchestrators → no brackets (they ARE the parent)
"""
