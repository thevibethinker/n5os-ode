# Incantum System - User Guide

**Version:** 1.0  
**Date:** 2025-10-23  
**Purpose:** Natural language command interface for N5

---

## Quick Start

Just say **"N5"** followed by what you want:

```
"N5 checkpoint this"
"N5 end conversation"
"N5 update my timeline and commit"
"N5 export this thread"
```

The LLM will:
- Understand your intent
- Map it to the right N5 command(s)
- Execute automatically (single commands) or propose and confirm (multiple commands)

---

## Examples

### Simple Commands (Auto-Execute)

```
You: "N5 checkpoint this"
LLM: ✓ Checkpointing conversation...
     [Runs thread-export]
```

```
You: "N5 show my timeline"
LLM: [Loads careerspan-timeline]
```

### Multi-Step Commands (Propose First)

```
You: "N5 checkpoint and commit changes"
LLM: I'll:
     1. Checkpoint the conversation (thread-export)
     2. Commit changes (git-commit)
     Proceed?
You: Yes
LLM: [Executes both]
```

### Natural Variations

All of these work the same:
- "N5 checkpoint this"
- "N5 save a checkpoint"
- "N5 create a checkpoint"
- "N5 export current state"

The LLM understands synonyms and variations.

---

## Custom Shortcuts

Define your own shortcuts in `file 'N5/config/incantum_shortcuts.json'`:

```json
{
  "eod": ["conversation-end"],
  "morning": ["careerspan-timeline", "check-email"],
  "ship": ["git-commit", "git-push", "thread-export"]
}
```

Then use them:
```
You: "N5 eod"
LLM: [Runs conversation-end]

You: "N5 morning"
LLM: I'll run your morning routine:
     - View timeline
     - Check email
     Proceed?
```

---

## What Commands Are Available?

View all 121 commands:
```bash
python3 N5/scripts/incantum_parser.py load-registry --format list
```

Or ask:
```
You: "What N5 commands are there for threads?"
LLM: [Shows thread-related commands]
```

---

## Terminology Resolved

**Thread Checkpoint vs. Conversation End**

These are now clarified:

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `thread-checkpoint` / `thread-export` | Create AAR, archive conversation | Mid-project, want to continue later |
| `conversation-end` | Full cleanup, file org, lessons | Done with conversation, close it out |

**You can use natural language:**
- "checkpoint this" → thread-checkpoint
- "end conversation" → conversation-end
- "wrap up" → conversation-end
- "export thread" → thread-checkpoint

The LLM figures it out.

---

## How It Learns

Every time you use an incantum command successfully, the pattern is logged to:
```
N5/logs/incantum_patterns.jsonl
```

Format:
```json
{
  "timestamp": "2025-10-23T23:00:00Z",
  "natural_language": "checkpoint and commit",
  "commands": [
    {"name": "thread-export", "args": {}},
    {"name": "git-commit", "args": {}}
  ],
  "success": true,
  "user_feedback": null
}
```

The LLM can reference past patterns for similar future requests.

---

## Giving Feedback

If the LLM gets it wrong:

```
You: "N5 checkpoint this"
LLM: [Proposes wrong command]
You: "No, I meant create a thread checkpoint, not end the conversation"
LLM: Got it, running thread-export instead
     [Logs corrected pattern with your feedback]
```

Your corrections improve future parsing.

---

## Advanced Usage

### Context-Aware Commands

```
You: "N5 add this to my timeline"
LLM: [Knows "this" refers to current conversation context]
     [Runs careerspan-timeline-add with extracted details]
```

### Chained Workflows

```
You: "N5 checkpoint, commit, and email me the summary"
LLM: I'll:
     1. thread-export
     2. git-commit
     3. send-email-to-user with AAR
     Proceed?
```

### Asking for Clarification

```
You: "N5 clean up"
LLM: Do you want to:
     1. Run conversation-end (full formal cleanup)
     2. Clean temporary files only
     3. Organize workspace
```

---

## Troubleshooting

**"Command not found"**
- Check available commands: `python3 N5/scripts/incantum_parser.py load-registry --format list`
- Or ask: "What commands are available for [topic]?"

**"Wrong command executed"**
- Give feedback: "No, I meant [clarification]"
- LLM will correct and log the feedback

**"Need to define new command"**
- Either:
  1. Create formal command in `N5/commands/`
  2. Or define shortcut in `incantum_shortcuts.json`

---

## Under the Hood

**What happens when you say "N5 checkpoint":**

1. LLM detects "N5" trigger
2. Loads command registry (121 commands)
3. Loads your shortcuts (if any)
4. Uses language understanding to map "checkpoint" → "thread-export"
5. Single command → auto-executes
6. Logs pattern to `incantum_patterns.jsonl`

**No regex, no pattern matching, just natural language intelligence.**

---

## Philosophy

The incantum system treats N5 like an **operating system with a natural language interface**.

Instead of memorizing exact command names and syntax, just describe what you want. The LLM translates intent → commands → execution.

**It's conversational command-line.**

---

## Tips

✅ **Start simple:** Try single commands first  
✅ **Be natural:** Don't overthink the phrasing  
✅ **Define shortcuts:** For frequent workflows  
✅ **Give feedback:** Corrections improve the system  
✅ **Check patterns:** See what's been learned in `incantum_patterns.jsonl`  

---

## Related Documentation

- **Protocol:** `file 'N5/prefs/operations/incantum-protocol.md'`
- **Script:** `file 'N5/scripts/incantum_parser.py'`
- **Shortcuts:** `file 'N5/config/incantum_shortcuts.json'`
- **Commands:** `file 'Recipes/recipes.jsonl'`
- **Patterns:** `file 'N5/logs/incantum_patterns.jsonl'`

---

**Ready to use! Just say "N5" and describe what you want.**

