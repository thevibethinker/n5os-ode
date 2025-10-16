# Command Triggering & Natural Language System

**Version:** 1.0  
**Last Updated:** 2025-10-16  
**Purpose:** Understand how commands are triggered and the role of Incantum

---

## Overview

N5 has a **two-layer command system** that handles both formal command invocation and natural language triggering:

1. **Commands Registry** (`N5/config/commands.jsonl`) — Formal command definitions
2. **Incantum Triggers** (`N5/config/incantum_triggers.json`) — Natural language → command mappings

---

## How It Works

### Layer 1: Formal Commands

**Location:** `file 'N5/config/commands.jsonl'`

```json
{
  "command": "conversation-end",
  "file": "N5/commands/conversation-end.md",
  "description": "Formal conversation end-step with file organization",
  "category": "system",
  "workflow": "automation",
  "script": "/home/workspace/N5/scripts/n5_conversation_end.py"
}
```

**When to use:**
- Script invocation (`python3 /home/workspace/N5/scripts/n5_conversation_end.py`)
- Direct command calls by other systems
- Programmatic execution

**Contains:**
- Canonical command name
- Script location
- Description & metadata
- Optional formal aliases (for script-level aliasing only)

---

### Layer 2: Incantum Triggers (Natural Language)

**Location:** `file 'N5/config/incantum_triggers.json'`

```json
{
  "trigger": "end conversation",
  "command": "conversation-end",
  "aliases": [
    "close thread",
    "conversation end",
    "wrap up",
    "end step",
    "we're done"
  ],
  "confidence": "high"
}
```

**When to use:**
- User says natural language phrases
- AI interprets user intent
- Fuzzy matching needed

**Contains:**
- Primary trigger phrase
- Target command (maps to commands.jsonl)
- Natural language aliases
- Confidence level

---

## Critical Distinction

### ❌ DON'T: Add aliases to commands.jsonl for natural language

```json
// WRONG - Don't do this
{
  "command": "conversation-end",
  "aliases": ["close-thread"],  // ❌ Redundant!
  ...
}
```

### ✅ DO: Use Incantum triggers for natural language

```json
// RIGHT - Incantum handles natural language
{
  "trigger": "end conversation",
  "command": "conversation-end",
  "aliases": ["close thread", "wrap up", ...],
  ...
}
```

---

## Workflow for Adding Command Triggers

### When User Reports: "Command X didn't trigger"

**Step 1: Check Incantum Triggers First**
```bash
grep -i "command-name" /home/workspace/N5/config/incantum_triggers.json
```

**Step 2: Add/Update Incantum Trigger**

If missing or incomplete, add the natural language mapping:

```json
{
  "trigger": "primary phrase",
  "command": "target-command",
  "aliases": [
    "variation 1",
    "variation 2",
    "what user actually said"
  ],
  "confidence": "high"
}
```

**Step 3: Verify**
```bash
python3 /home/workspace/N5/scripts/n5_incantum.py "what user said"
```

**Step 4: DO NOT modify commands.jsonl**

Unless it's a formal script-level alias (rare), keep commands.jsonl clean.

---

## When to Use Each System

### Commands Registry (commands.jsonl)
✅ **Use for:**
- Script paths and metadata
- Formal command definitions
- System integration
- Docgen catalog generation

❌ **Don't use for:**
- Natural language variations
- User-facing aliases
- "What the user might say" mappings

### Incantum Triggers (incantum_triggers.json)
✅ **Use for:**
- Natural language mappings
- User intent variations
- "Close thread" → "conversation-end" mappings
- Multiple ways to say the same thing

❌ **Don't use for:**
- Script metadata
- File paths
- System configuration

---

## Fuzzy Matching with n5_incantum.py

For phrases NOT in incantum_triggers.json, the `n5_incantum.py` script uses **rapidfuzz** for fuzzy matching:

```bash
python3 /home/workspace/N5/scripts/n5_incantum.py "export thread"
# Finds "thread-export" with 85% confidence
# Prompts: "Run thread-export? (y/N)"
```

**Matching Algorithm:**
- Uses QRatio scoring (0-100%)
- Threshold: 55% minimum
- Top 3 candidates shown if ambiguous
- Confidence boost for exact substring matches

**When to rely on fuzzy matching:**
- One-off user phrases
- Exploratory commands
- When explicit trigger doesn't exist

**When to add explicit trigger:**
- User repeats the same phrase
- Common variation not recognized
- False matches occur

---

## Best Practices

### For AI (Zo) When User Says Something

1. **Check Incantum triggers first** — Look for natural language mapping
2. **Use fuzzy matching as fallback** — If no explicit trigger exists
3. **Never add aliases to commands.jsonl** — Unless it's a formal script alias
4. **Document common patterns** — Add frequently-used phrases to Incantum

### For Command Authors

1. **Define formal command in commands.jsonl**
2. **Add natural language triggers to incantum_triggers.json**
3. **Include common variations** — "export", "save", "archive", etc.
4. **Test with n5_incantum.py** — Verify matching works

### For System Maintenance

1. **Keep commands.jsonl clean** — Only formal definitions
2. **Keep incantum_triggers.json rich** — Many aliases per command
3. **Monitor false positives** — Adjust confidence levels
4. **Periodic review** — Check for missing common phrases

---

## Example: "close-thread" Resolution

### What Happened
User said: `close-thread`

### How It Should Work
1. Zo checks `incantum_triggers.json`
2. Finds trigger: "end conversation"
3. Sees alias: "close thread"
4. Executes: `conversation-end` command
5. No need to modify `commands.jsonl`

### What Went Wrong (Previously)
- AI manually added `"aliases": ["close-thread"]` to `commands.jsonl`
- This created redundancy with Incantum system
- Violated separation of concerns (formal vs. natural language)

### Corrected Approach
- ✅ Incantum trigger already existed with "close thread" alias
- ✅ Removed redundant alias from commands.jsonl
- ✅ System now follows proper architecture

---

## Integration with Search

### search-commands
Uses commands.jsonl for formal search:
```bash
python3 /home/workspace/N5/scripts/n5_search_commands.py "export"
```

Returns formal command matches from registry.

### n5_incantum.py
Uses both incantum_triggers.json AND fuzzy matching:
```bash
python3 /home/workspace/N5/scripts/n5_incantum.py "save this conversation"
```

Returns best natural language match with confidence score.

---

## Troubleshooting

### Command not triggering?
1. Check `incantum_triggers.json` for explicit mapping
2. Test with `n5_incantum.py "user phrase"`
3. Check fuzzy match score (should be >55%)
4. Add explicit trigger if needed

### Wrong command triggered?
1. Check for competing triggers with similar aliases
2. Adjust confidence levels
3. Make primary trigger more specific
4. Remove ambiguous aliases

### Multiple commands match?
1. Incantum will prompt user to choose
2. Consider making triggers more distinct
3. Add context-specific keywords to aliases

---

## Files Reference

**Command Definitions:**
- `file 'N5/config/commands.jsonl'` — Formal registry (83 commands)
- `file 'N5/commands.md'` — Generated catalog (from docgen)

**Natural Language:**
- `file 'N5/config/incantum_triggers.json'` — Explicit mappings
- `file 'N5/commands/incantum-quickref.md'` — User-facing reference

**Scripts:**
- `file 'N5/scripts/n5_incantum.py'` — Fuzzy matching engine
- `file 'N5/scripts/incantum_engine.py'` — Legacy engine (prototype)
- `file 'N5/scripts/n5_search_commands.py'` — Formal command search

**Schemas:**
- `file 'N5/schemas/incantum_triggers.json'` — Schema definition
- `file 'N5/schemas/commands.schema.json'` — Command registry schema

---

## Summary

**Two-Layer Architecture:**
- **Commands Registry** = Formal, script-level definitions
- **Incantum Triggers** = Natural language, user-facing mappings

**Separation of Concerns:**
- DON'T mix natural language aliases into commands.jsonl
- DO keep Incantum triggers rich with variations
- USE fuzzy matching as graceful fallback

**When in Doubt:**
- Natural language variation? → Incantum
- Script-level alias? → Commands.jsonl (rare)
- User phrase not working? → Check Incantum first

---

*For command authoring workflow, see `file 'N5/commands/grep-search-command-creation.md'`*  
*For Incantum user guide, see `file 'N5/commands/incantum-quickref.md'`*
