# Incantum Command Protocol

**Purpose:** Natural language command parsing for N5 system  
**Version:** 1.0  
**Updated:** 2025-10-23

---

## Overview

The **incantum system** allows V to invoke N5 commands using natural language by prefixing messages with **"N5"** or **"incantum"**.

Instead of remembering exact command names, V can say things like:
- "N5 checkpoint this"
- "N5 end conversation"
- "N5 update my timeline and commit"

You (the LLM) parse the intent and map to appropriate commands.

---

## Detection & Parsing

### 1. Trigger Detection

**When user message starts with "N5" or "incantum" (case-insensitive):**

Extract the instruction by removing the prefix:
```
"N5 checkpoint and commit" → "checkpoint and commit"
"incantum update timeline" → "update timeline"
```

### 2. Load Context

Before parsing, load:

**Commands Registry:**
```bash
python3 /home/workspace/N5/scripts/incantum_parser.py load-registry
```

**User Shortcuts:**
```bash
python3 /home/workspace/N5/scripts/incantum_parser.py load-shortcuts
```

**Historical Patterns (if helpful):**
```bash
python3 /home/workspace/N5/scripts/incantum_parser.py search "<query>"
```

### 3. Parse Intent (YOU do this, not regex)

Use your language understanding to map the instruction to command(s):

**Examples:**
- "checkpoint this" → `thread-export`
- "end conversation" → `conversation-end`
- "update timeline and commit" → `careerspan-timeline-add`, `git-commit`
- "eod" (if shortcut defined) → whatever V mapped it to

**If unclear:** Ask clarifying questions before proceeding.

### 4. Execution Rules

**Single command:**
- Auto-execute without confirmation
- Inform V what you're doing

**Multiple commands (2+):**
- Propose the sequence
- Wait for V's confirmation
- Then execute

**Uncertain/Low confidence:**
- Ask clarifying questions
- Show what you think V means
- Get confirmation

---

## After Execution

**If successful**, log the pattern for future reference:

```bash
python3 /home/workspace/N5/scripts/incantum_parser.py log \
  "checkpoint and commit" \
  --commands '[{"name": "thread-export", "args": {}}, {"name": "git-commit", "args": {}}]' \
  --context '{"conversation_id": "con_xyz"}'
```

**If V provides feedback**, include it:
```bash
--feedback "Actually meant just checkpoint, not commit"
```

**If it failed**, mark it:
```bash
--failed
```

---

## Command Registry Structure

Commands in `file 'Recipes/recipes.jsonl'` have:

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

Use `description` and command name to understand what each does.

---

## User Shortcuts

V can define custom shortcuts in `file 'N5/config/incantum_shortcuts.json'`:

```json
{
  "eod": ["conversation-end"],
  "daily": ["careerspan-timeline", "daily-report-generate"]
}
```

Check this file first when parsing.

---

## Examples

### Example 1: Simple Command
```
V: "N5 checkpoint this"

You:
1. Detect trigger "N5"
2. Extract instruction "checkpoint this"
3. Load registry → see "thread-export" command
4. Single command → auto-execute
5. Execute: python3 /home/workspace/N5/scripts/n5_thread_export.py
6. Log pattern for future
```

### Example 2: Multi-Command
```
V: "N5 checkpoint and commit changes"

You:
1. Detect trigger "N5"
2. Extract "checkpoint and commit changes"
3. Parse → thread-export + git-commit
4. Multiple commands → propose first
5. Say: "I'll checkpoint the conversation (thread-export) and commit changes (git-commit). Proceed?"
6. Wait for confirmation
7. Execute both
8. Log pattern
```

### Example 3: Unclear Intent
```
V: "N5 clean up"

You:
1. Detect trigger
2. Extract "clean up"
3. Multiple possible interpretations:
   - conversation-end (formal cleanup)?
   - Clean temp files?
   - Organize workspace?
4. Ask: "Do you want to run conversation-end (full cleanup), or just organize temp files?"
5. V clarifies
6. Execute
```

### Example 4: Custom Shortcut
```
V defines in shortcuts.json:
{"morning": ["careerspan-timeline", "check-email", "generate-daily-plan"]}

V: "N5 morning"

You:
1. Load shortcuts
2. See "morning" → 3 commands
3. Multiple commands → propose
4. Say: "I'll run your morning routine: timeline, check email, generate plan. Proceed?"
5. Execute sequence
```

---

## Integration Checklist

When you see "N5" or "incantum" prefix:

- [ ] Strip prefix and extract instruction
- [ ] Load commands registry
- [ ] Load user shortcuts (if exist)
- [ ] Parse intent using language understanding
- [ ] Follow execution rules (single auto, multi propose)
- [ ] Execute command(s)
- [ ] Log successful pattern
- [ ] Handle errors gracefully

---

## Troubleshooting

**No matching command:**
- Search historical patterns for similar
- Ask V what they meant
- Suggest closest matches

**Command execution fails:**
- Log as failed attempt
- Report error to V
- Suggest alternatives

**Ambiguous instruction:**
- Always ask for clarification
- Show your interpretation
- Get explicit confirmation

---

## Notes

- The **LLM does the parsing**, not regex/pattern matching
- Keep patterns simple and logged
- User shortcuts override defaults
- Always err on side of asking vs. guessing wrong

---

**Related Files:**
- `file 'N5/scripts/incantum_parser.py'` - Helper utilities
- `file 'Recipes/recipes.jsonl'` - Command registry
- `file 'N5/config/incantum_shortcuts.json'` - User shortcuts
- `file 'N5/logs/incantum_patterns.jsonl'` - Historical patterns

