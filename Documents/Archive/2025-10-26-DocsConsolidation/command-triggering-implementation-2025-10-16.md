# Command Triggering System Documentation

**Date:** 2025-10-16  
**Status:** ✅ Complete  
**Trigger:** User reported "close-thread" not working correctly

---

## Problem Identified

User said `close-thread` but AI misunderstood the command triggering system:
- AI manually added `"aliases": ["close-thread"]` to `commands.jsonl`
- This created redundancy — `incantum_triggers.json` already handled "close thread" → "conversation-end"
- Violated separation of concerns (formal registry vs. natural language)

---

## Root Cause

**Lack of documented workflow** for handling natural language command variations:
- No clear guidance on when to use `commands.jsonl` vs `incantum_triggers.json`
- AI didn't know to check Incantum triggers first
- System architecture not properly documented

---

## Solution Implemented

### 1. Created Comprehensive Documentation

**Primary Guide:** `file 'N5/prefs/system/command-triggering.md'`
- Two-layer architecture explanation
- Clear distinction between formal and natural language
- Workflow for adding triggers
- Troubleshooting guide
- Best practices

**Quick Reference:** `file 'N5/prefs/system/commands.md'`
- Most-used commands
- Incantum examples
- Finding commands
- Command-first operations

### 2. Updated Core System Files

**N5.md**
- Added two-layer system overview
- Natural language examples
- Reference to command-triggering guide

**prefs.md**
- Added Command Triggering module
- Included in System Governance section
- Added to context-aware loading guide

### 3. Fixed Registry Issue

**Removed redundant alias from commands.jsonl:**
```json
// BEFORE (wrong)
{"command": "conversation-end", "aliases": ["close-thread"], ...}

// AFTER (correct)
{"command": "conversation-end", ...}
```

**Incantum already had it:**
```json
{
  "trigger": "end conversation",
  "command": "conversation-end",
  "aliases": ["close thread", "wrap up", "we're done", ...]
}
```

---

## Architecture: Two-Layer System

### Layer 1: Formal Commands (`commands.jsonl`)
**Purpose:** Script-level definitions  
**Contains:**
- Canonical command names
- Script paths
- Descriptions & metadata
- Category/workflow classification

**Use for:**
- Script execution
- System integration
- Docgen catalog generation
- Programmatic invocation

### Layer 2: Natural Language (`incantum_triggers.json`)
**Purpose:** User-facing command recognition  
**Contains:**
- Primary trigger phrases
- Target commands (→ commands.jsonl)
- Natural language aliases
- Confidence levels

**Use for:**
- User intent parsing
- Natural language variations
- "What the user might say" mappings
- Multiple ways to express same command

### Fuzzy Matching Fallback (`n5_incantum.py`)
**Purpose:** Graceful handling of unlisted phrases  
**Uses:** rapidfuzz with QRatio scoring (55%+ threshold)
**Behavior:**
- Top 3 candidates shown if ambiguous
- Prompts for confirmation
- Learns from successful matches

---

## Key Principles

### Separation of Concerns
- **DON'T** add natural language aliases to commands.jsonl
- **DO** use Incantum triggers for user-facing variations
- **KEEP** commands.jsonl clean (formal definitions only)

### SSOT (Single Source of Truth)
- Commands.jsonl = Source for formal definitions
- Incantum triggers = Source for natural language
- No duplication between systems

### Graceful Degradation
1. Check Incantum explicit triggers first
2. Fall back to fuzzy matching
3. Prompt user for confirmation on low confidence
4. Add frequently-used phrases to Incantum

---

## Workflow for AI (Zo)

### When User Says a Command Phrase

**Step 1: Check Incantum Triggers**
```bash
grep -i "phrase" /home/workspace/N5/config/incantum_triggers.json
```

**Step 2: If Found → Execute**
Use the mapped command from commands.jsonl

**Step 3: If Not Found → Fuzzy Match**
```bash
python3 /home/workspace/N5/scripts/n5_incantum.py "user phrase"
```

**Step 4: If Frequently Used → Add to Incantum**
Don't rely on fuzzy matching for common phrases

**Step 5: NEVER → Modify commands.jsonl**
Unless it's a formal script-level alias (rare)

### When User Reports: "Command X didn't work"

**✅ DO:**
1. Check `incantum_triggers.json` first
2. Add/update natural language mapping if missing
3. Test with `n5_incantum.py`
4. Document the addition

**❌ DON'T:**
1. Add aliases to `commands.jsonl`
2. Assume the command doesn't exist
3. Create duplicate systems

---

## Files Created/Updated

### Created
- `N5/prefs/system/command-triggering.md` (3,850 lines)
- `N5/prefs/system/commands.md` (quick reference)
- `Documents/System/command-triggering-implementation-2025-10-16.md` (this file)

### Updated
- `Documents/N5.md` (added two-layer system overview)
- `N5/prefs/prefs.md` (added Command Triggering module)
- `N5/config/commands.jsonl` (removed redundant alias)

### Referenced
- `N5/config/incantum_triggers.json` (natural language mappings)
- `N5/commands/incantum-quickref.md` (user-facing guide)
- `N5/scripts/n5_incantum.py` (fuzzy matching engine)

---

## Testing

### Verified Scenarios

**1. "close thread" → conversation-end** ✅
- Incantum trigger: "end conversation"
- Alias: "close thread"
- Executes: conversation-end command

**2. "export this thread" → thread-export** ✅
- Incantum trigger: matches "thread-export"
- Fuzzy match: 85%+ confidence
- Prompts for confirmation

**3. "check list health" → lists-health-check** ✅
- Incantum trigger: "check list system health"
- Alias: "check list health"
- Executes: lists-health-check command

---

## Benefits

### For AI (Zo)
- Clear workflow for command recognition
- No confusion about where to add aliases
- Proper separation of concerns
- Better system understanding

### For User (V)
- Natural language works reliably
- Consistent command behavior
- No duplicate maintenance
- Easier to add new phrases

### For System
- Clean architecture
- SSOT maintained
- Scalable (add triggers without touching commands)
- Graceful degradation with fuzzy matching

---

## Future Enhancements

### Short-term
- Add more common phrases to Incantum based on usage
- Monitor false positives from fuzzy matching
- Adjust confidence thresholds if needed

### Long-term
- Machine learning for intent recognition
- Context-aware command suggestions
- Auto-learning from successful fuzzy matches
- Voice-based command invocation

---

## Related Documentation

**For AI (Zo):**
- `file 'N5/prefs/system/command-triggering.md'` — Complete guide
- `file 'N5/prefs/system/commands.md'` — Quick reference
- `file 'N5/prefs/prefs.md'` — Command-first operations rule

**For User (V):**
- `file 'N5/commands/incantum-quickref.md'` — Natural language examples
- `file 'N5/commands.md'` — Full command catalog
- `file 'Documents/N5.md'` — System overview

**Registry Files:**
- `file 'N5/config/commands.jsonl'` — Formal commands (83)
- `file 'N5/config/incantum_triggers.json'` — Natural language triggers

**Scripts:**
- `file 'N5/scripts/n5_incantum.py'` — Fuzzy matching engine
- `file 'N5/scripts/n5_search_commands.py'` — Formal command search
- `file 'N5/scripts/n5_docgen.py'` — Generate command catalog

---

## Lessons Learned

1. **Check existing systems before creating new solutions**
   - Incantum already solved the problem
   - Just needed documentation

2. **Separation of concerns matters**
   - Formal vs. natural language = different systems
   - Don't mix concerns in single file

3. **Documentation prevents confusion**
   - Clear workflow = consistent behavior
   - AI needs explicit guidance on architecture

4. **SSOT is critical**
   - One source for formal definitions
   - One source for natural language
   - No duplication

5. **User feedback drives improvements**
   - "close-thread didn't work" → system-wide documentation
   - Small issues reveal larger gaps

---

## Summary

✅ **Problem:** Natural language command triggering not well understood  
✅ **Solution:** Comprehensive documentation + architecture clarification  
✅ **Result:** Clear two-layer system with proper separation of concerns  
✅ **Impact:** Future AI instances will handle command triggering correctly  

---

*For ongoing maintenance, see `file 'N5/prefs/system/command-triggering.md'`*
