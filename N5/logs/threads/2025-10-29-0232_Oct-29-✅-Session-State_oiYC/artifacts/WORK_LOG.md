# Title Generator Fix - Work Log

**Conversation:** con_KpEu4ns6CS58oiYC  
**Date:** 2025-10-29 02:30 ET

---

## Problem

Title generator producing generic, useless titles like "Oct 29 | 🎨 System Work Build" instead of specific, contextual titles that describe actual conversation content.

**Root Cause:** Script used keyword matching and regex heuristics instead of LLM-based understanding.

---

## Solution

Completely rewrote `/home/workspace/N5/scripts/n5_title_generator.py` to:

1. **Use LLM directly** - Calls `zo chat` CLI to generate titles based on actual conversation understanding
2. **Pass full context** - Sends AAR objective, summary, key events, and artifacts to LLM
3. **Enforce specificity** - Prompt explicitly requires specific component names, not generic terms
4. **Length constraints** - Strict 15-30 character limit for readability
5. **Fallback handling** - If LLM call fails, uses basic extraction from artifacts

---

## Key Changes

### Before (Keyword Matching)
```python
def _extract_primary_entity(self, text: str, aar_data: Dict) -> str:
    """Extract main subject/entity using regex patterns"""
    entity_patterns = [
        (r'\b(vibe debugger|vibe-debugger)', "Vibe Debugger"),
        (r'\b(close conversation|conversation[-\s]close)', "Close Conversation Recipe"),
        # ... 30+ more regex patterns
    ]
    # Falls back to "System Work"
```

### After (LLM-Based)
```python
def _call_llm_for_title(self, aar_data: Dict, artifacts: List[Dict], emoji_options: str) -> Dict:
    """Call LLM to generate contextual title based on conversation content"""
    prompt = f"""Generate a specific, contextual title for this conversation thread.
    
    CONVERSATION CONTEXT:
    Objective: {objective}
    Summary: {summary}
    Key Events: {events}
    Artifacts: {artifacts}
    
    REQUIREMENTS:
    1. Be SPECIFIC - mention actual system/component names
    2. NO generic titles like "System Work Build"
    """
    # Calls zo chat CLI
```

---

## Testing Required

1. **Normal conversations** - Should produce specific titles
2. **Generic discussions** - Should still be better than "System Work"
3. **LLM failure** - Fallback should work gracefully
4. **Title length** - Should stay within 15-30 chars

---

## Files Modified

- `/home/workspace/N5/scripts/n5_title_generator.py` - Complete rewrite (602 → 315 lines)

---

## Impact

- **Immediate:** Next conversation close will use LLM-based title generation
- **Future:** All new conversations get contextual, specific titles
- **Performance:** Slightly slower due to LLM call, but worth it for quality

---

*Fixed: 2025-10-29 02:30 ET*
