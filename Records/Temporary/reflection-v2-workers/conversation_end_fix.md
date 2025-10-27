# Conversation End Script - Title Generation Fix

**Issue:** `save_proposed_title()` uses "most recent AAR" instead of conversation-specific AAR

**Root Cause:** Lines 651-661 in `n5_conversation_end.py`

```python
# BUG: Gets most recent directory (could be from different conversation)
archives = sorted([d for d in threads_dir.iterdir() if d.is_dir()], 
                 key=lambda x: x.stat().st_mtime, reverse=True)
latest_archive = archives[0]  # ← Takes first (most recent), not conversation-specific
```

---

## Proposed Fix

### Option 1: Match by Conversation ID (Recommended)

Extract conversation ID from CONVERSATION_WS path and find matching thread archive:

```python
def save_proposed_title():
    """
    Phase 0.5: Extract generated title and save to conversation workspace
    """
    try:
        from n5_title_generator import TitleGenerator
        
        # Extract conversation ID from workspace path
        if not CONVERSATION_WS:
            logger.debug("No conversation workspace available")
            return
            
        convo_id = CONVERSATION_WS.name  # e.g., "con_W9jH5cVRjYPHve2j"
        
        # Find thread archive for THIS conversation
        threads_dir = WORKSPACE / "N5/logs/threads"
        if not threads_dir.exists():
            logger.debug("No threads directory found")
            return
        
        # Look for directory containing this conversation ID
        matching_archives = [
            d for d in threads_dir.iterdir() 
            if d.is_dir() and convo_id in d.name
        ]
        
        if not matching_archives:
            logger.debug(f"No thread archive found for conversation {convo_id}")
            # Fallback: generate from SESSION_STATE.md instead
            return generate_title_from_session_state()
        
        # Use the most recent match (in case there are multiple)
        latest_archive = max(matching_archives, key=lambda x: x.stat().st_mtime)
        
        # Rest of the function continues as before...
```

### Option 2: Generate from SESSION_STATE.md

If no AAR exists yet, generate title from the conversation workspace:

```python
def generate_title_from_session_state():
    """
    Generate title from SESSION_STATE.md when no AAR exists yet
    """
    session_state = CONVERSATION_WS / "SESSION_STATE.md"
    if not session_state.exists():
        logger.debug("No SESSION_STATE.md found")
        return
    
    # Parse SESSION_STATE.md for:
    # - Focus field
    # - Objective field
    # - Files being worked on
    # - Outputs section
    
    content = session_state.read_text()
    
    # Extract key fields (simple parsing)
    focus = extract_field(content, "Focus:")
    objective = extract_field(content, "Objective:")
    phase = extract_field(content, "Current Phase:")
    
    # Generate title from session state data
    generator = TitleGenerator()
    title_data = {
        "primary_objective": objective or focus or "Session work",
        "final_state": {"summary": f"Build session: {phase}"},
        "key_events": []
    }
    
    titles = generator.generate_titles(title_data, [])
    # ... rest of title generation logic
```

---

## Implementation Plan

1. **Immediate Fix:** Modify `save_proposed_title()` to use conversation ID matching
2. **Fallback:** Add `generate_title_from_session_state()` for when no AAR exists
3. **Testing:** Test with multiple conversations to ensure isolation
4. **Documentation:** Update conversation-end protocol

---

## Key Principles Violated

- **P18 (Verify State):** Should verify we're looking at the CORRECT conversation's AAR
- **P11 (Failure Modes):** Should handle case where multiple conversations are closing
- **P2 (SSOT):** Conversation ID should be the single source of truth for identification

---

**Status:** Ready for implementation  
**Priority:** High (affects all conversation-end operations)

**2025-10-26 22:07 ET**
