---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_nXKLrpy6lsnJm0dz
---

# Conversation End - Tier 1 (Quick Close) Template

## When This Tier Applies

Tier 1 is the **default** for:
- Quick Q&A sessions
- Simple discussions
- Brief research queries
- Any conversation without build/orchestrator markers

## LLM Responsibilities

The script (`conversation_end_quick.py`) handles:
- ✅ File scanning and categorization
- ✅ SESSION_STATE parsing
- ✅ Pattern-based title generation
- ✅ Output formatting

**You (LLM) must provide:**
1. **Enhanced Summary** - Read the conversation and write 2-3 sentences capturing what was discussed/accomplished
2. **Title Refinement** - If the auto-generated title is poor, suggest a better one
3. **Git Check** - If there are uncommitted changes, prompt user

## Output Format

```markdown
## Conversation Closed

**Title:** [Title from script OR your refined title]
**Type:** [From SESSION_STATE or inferred]
**Duration:** [If known]

### Summary
[YOUR 2-3 SENTENCE SUMMARY - must be based on actual conversation content]

### Files in Workspace
[From script output]

### Git Status
[If changes detected, show: "⚠️ X uncommitted changes - commit recommended"]
[If clean: omit this section]

✅ Workspace clean
```

## Execution Steps

1. Run: `python3 N5/scripts/conversation_end_quick.py --convo-id <id> --json`
2. Parse the JSON output
3. Read conversation to understand actual content
4. Write enhanced summary (2-3 sentences, specific to THIS conversation)
5. Check git status: `git -C /home/workspace status --porcelain | wc -l`
6. Format final output

## Quality Checklist

- [ ] Summary is specific to this conversation (not generic)
- [ ] Title follows format: `Mon DD | 🔣 Brief Description`
- [ ] Files listed match actual workspace contents
- [ ] Git status checked and reported if changes exist
- [ ] Total LLM tokens used < 500 (cost target: <$0.05)

