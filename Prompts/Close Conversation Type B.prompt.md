---
created: 2025-12-07
last_edited: 2025-12-11
version: 1.1
title: Close Conversation Type B
description: |
  Extracts position candidates from a conversation, checks for overlaps with existing positions,
  and either extends existing positions or creates new ones. Outputs a summary showing changes
  and artifacts referenced. Use for conversations that developed or refined worldview positions.
tags:
  - conversation-end
  - positions
  - knowledge-synthesis
tool: true
---

# Close Conversation Type B

## Purpose

Extract **positions** (compound insights representing worldview claims) from the current conversation and integrate them into the positions database. This is for conversations where V developed, refined, or articulated a belief/stance on a topic.

## When to Use

- Conversation involved deep thinking about a topic
- V articulated a position or belief
- New evidence or reasoning was presented for an existing position
- A strategic or philosophical insight emerged

## Workflow

### Step 1: Audit Current State

First, check current positions and any incomplete entries:

```bash
python3 /home/workspace/N5/scripts/positions.py list
python3 /home/workspace/N5/scripts/positions.py audit
```

### Step 2: Catalog Evidence From This Conversation

**CRITICAL: Identify evidence FIRST, before creating positions.**

Scan the conversation and catalog:
- **URLs cited or referenced**
- **Files created or referenced** 
- **Content Library items used**
- **Meetings discussed**
- **Conversations that informed this thinking**

Document each piece of evidence with the appropriate type prefix:

| Evidence Type | Format | Example |
|---------------|--------|---------|
| Content Library item | `content_library:<id>` | `content_library:hiring-signal-collapse-worldview` |
| Meeting | `meeting:<folder-name>` | `meeting:2025-10-10_hamoon-ekhtiari-futurefit` |
| URL | `url:<full-url>` | `url:https://example.com/article` |
| File | `file:<path>` | `file:Documents/Strategy/analysis.md` |
| Conversation | `conversation:<convo-id>` | `conversation:con_abc123` |
| Article | `article:<title-or-id>` | `article:why-ai-changes-hiring` |

### Step 3: Identify Position Candidates

Review the conversation and identify any position candidates—compound insights that represent a worldview claim. Look for:

- **Assertions with reasoning**: "X is true because Y and Z"
- **Strategic beliefs**: "The way to win is by doing X"
- **Market observations**: "This industry is changing because..."
- **Philosophical stances**: "I believe that..."

For each candidate, articulate:
- **Domain**: What area does this belong to? (hiring-market, ai-capabilities, career-development, productivity, etc.)
- **Title**: Short name for the position (kebab-case-friendly)
- **Insight**: The compound insight as a clear statement (2-4 sentences)
- **Components**: Sub-claims that make up this insight
- **Evidence**: Which items from Step 2 support this position?

### Step 4: Check for Overlaps

For each candidate insight, check if it overlaps with existing positions:

```bash
python3 /home/workspace/N5/scripts/positions.py check-overlap "YOUR_INSIGHT_TEXT" --threshold 0.4
```

**Interpretation:**
- **≥0.60**: Strong overlap → EXTEND existing position
- **0.50-0.59**: Moderate overlap → review carefully, could go either way
- **<0.50**: Low overlap → CREATE new position

### Step 5: Execute Updates

**To CREATE a new position (include evidence!):**

```bash
python3 /home/workspace/N5/scripts/positions.py add \
  --domain "domain-name" \
  --title "Position Title" \
  --insight "The compound insight text..." \
  --component "First sub-claim" \
  --component "Second sub-claim" \
  --evidence "content_library:item-id" \
  --evidence "meeting:folder-name" \
  --evidence "url:https://example.com" \
  --stability emerging \
  --confidence 3 \
  --source-conversation "con_CURRENT_CONVO_ID"
```

**To EXTEND an existing position:**

```bash
python3 /home/workspace/N5/scripts/positions.py extend <position-id> \
  --add-component "New sub-claim or nuance from this conversation" \
  --add-evidence "meeting:folder-name" \
  --source-conversation "con_CURRENT_CONVO_ID"
```

**Stability levels:** `emerging` (new), `stable` (well-supported), `canonical` (foundational)
**Confidence:** 1-5 scale (1=hypothesis, 5=certain)

### Step 6: Add Connections (REQUIRED)

After creating or extending positions, check for connections:

```bash
python3 /home/workspace/N5/scripts/positions.py suggest-connections <position-id>
```

For each suggested connection, add it:

```bash
python3 /home/workspace/N5/scripts/positions.py extend <position-id> \
  --add-connection "other-position-id:relationship"
```

**Relationship types:**
- `supports` — This position provides evidence for the other
- `extends` — This position builds on/elaborates the other
- `contradicts` — This position conflicts with the other
- `prerequisite` — The other position must be true for this one to hold
- `implies` — If this position is true, the other follows
- `related` — General thematic connection

### Step 7: Final Audit

Verify no positions are left incomplete:

```bash
python3 /home/workspace/N5/scripts/positions.py audit
```

If issues remain, fix them before completing.

### Step 8: Generate Summary

Output using this template:

---

## Type B Conversation End Summary

### Conversation: con_XXX

### Positions Updated

| Action | ID | Title | Similarity |
|--------|-----|-------|------------|
| CREATED | new-position-id | New Position Title | N/A |
| EXTENDED | existing-id | Existing Title | 0.XX |

### New Position Details
- **position-id**: Brief description of the position and why it was created

### Extensions Made
- **position-id**: What was added (component, evidence, connection)

### Connections Added
- `position-a` → `position-b` (relationship)

### Evidence Cataloged
- [content_library] hiring-signal-collapse-worldview
- [meeting] 2025-10-10_hamoon-ekhtiari-futurefit
- [conversation] con_abc123

### Final Audit Status
✅ All positions complete OR ⚠️ Issues remaining: [list]

---

## Important Notes

1. **Evidence is mandatory**: Never create a position without at least one evidence pointer. The conversation itself (`conversation:con_XXX`) always counts as evidence.

2. **Connections matter**: After creating a position, always run `suggest-connections` and add at least one connection if suggestions exist.

3. **Quality over quantity**: One well-articulated position is better than three vague ones.

4. **Use existing positions**: Extending is often better than creating. The positions database should grow slowly.

5. **Track sources**: Always use `--source-conversation` so we can trace back.

## Quick Reference

```bash
# List positions
python3 /home/workspace/N5/scripts/positions.py list

# Audit for incomplete positions
python3 /home/workspace/N5/scripts/positions.py audit

# Check overlap before creating
python3 /home/workspace/N5/scripts/positions.py check-overlap "insight text" --threshold 0.4

# Suggest connections
python3 /home/workspace/N5/scripts/positions.py suggest-connections <id>

# Get full details of a position
python3 /home/workspace/N5/scripts/positions.py get <id>

# Search semantically
python3 /home/workspace/N5/scripts/positions.py search "query" --threshold 0.4
```


