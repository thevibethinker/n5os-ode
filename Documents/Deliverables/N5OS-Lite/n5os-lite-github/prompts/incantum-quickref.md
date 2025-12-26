---
tool: true
description: Natural language command triggers - speak naturally to invoke workflows
tags: [incantum, commands, natural-language, shortcuts]
version: 1.0
created: 2025-11-03
---

# Incantum Quick Reference

Natural language phrases that trigger N5OS Lite workflows automatically.

**Philosophy:** Speak naturally → System understands intent → Workflow executes

---

## Quick Reference

### Lists

**Add to lists:**
- "add this to [list-name]"
- "save this to my tools list"
- "add to ideas"

**Query lists:**
- "find in lists"
- "search my tools for Python"
- "show me workflows tagged automation"

**Manage lists:**
- "export my lists"
- "check list health"
- "validate lists"

### Knowledge

**Add knowledge:**
- "add to knowledge"
- "save this as knowledge"
- "ingest this content"

**Find knowledge:**
- "find in knowledge"
- "search knowledge for [topic]"
- "what do I know about [topic]"

### Thread Management

**End conversation:**
- "close thread"
- "end conversation"
- "wrap this up"
- → Triggers close-conversation workflow

**Export thread:**
- "export this"
- "export thread"
- "save conversation"
- → Creates archive with summary

### Documentation

**Generate docs:**
- "generate docs"
- "rebuild documentation"
- "update docs"
- → Runs docgen workflow

**Update index:**
- "rebuild index"
- "update index"
- → Regenerates knowledge index

### Workers & Orchestration

**Spawn worker:**
- "spawn a worker"
- "create parallel worker"
- "delegate this task"
- → Creates independent AI worker thread

### System

**Health checks:**
- "check system health"
- "validate installation"
- "run diagnostics"

**Git operations:**
- "check git"
- "git status"
- "audit git"

---

## How It Works

**Traditional:** "Run the add-to-list prompt with these parameters..."  
**Incantum:** "Add this to my tools list"

**Behind the scenes:**
1. AI recognizes natural phrase
2. Maps to appropriate workflow/prompt
3. Executes with inferred parameters
4. Returns result

---

## Creating Custom Triggers

Want to add your own?

1. Create workflow prompt
2. Document natural phrases in frontmatter:
```yaml
incantum_triggers:
  - "check my calendar"
  - "what's on my schedule"
```
3. AI will recognize and route

---

## Tips

- **Be specific:** "add to tools" better than "save this"
- **Use context:** AI considers conversation context
- **Iterate:** If unclear, AI will ask for clarification

---

**Related:**
- Prompts: All workflow prompts can be invoked via incantum
- System: `preferences_system.md` - How AI routes requests

---

*Speak naturally. Let the system translate.*
