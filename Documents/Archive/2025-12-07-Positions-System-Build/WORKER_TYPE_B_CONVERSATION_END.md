---
created: 2025-12-06
last_edited: 2025-12-07
version: 2.0
worker_id: type-b-conversation-end
depends_on: positions-core (COMPLETE ✅)
---

# Worker: Type B Conversation End

## Context

**Positions system is BUILT and VERIFIED.** Location: `/home/workspace/N5/scripts/positions.py`

Database: `/home/workspace/N5/data/positions.db`  
Current positions: 2 (hiring-signal-collapse, selfknowledge-deficit)

## Objective

Create a **minimal** Type B conversation-end that:
1. Extracts position candidates from a conversation
2. Checks for overlaps with existing positions
3. Either extends existing or creates new
4. Outputs a summary showing changes + artifacts used

## Verified API

The positions.py CLI is confirmed working:

```bash
# List all positions
python3 /home/workspace/N5/scripts/positions.py list

# Get specific position
python3 /home/workspace/N5/scripts/positions.py get <id>

# Semantic search
python3 /home/workspace/N5/scripts/positions.py search "query text" --threshold 0.5

# Check overlap before adding
python3 /home/workspace/N5/scripts/positions.py check-overlap "insight text" --threshold 0.5

# Add new position
python3 /home/workspace/N5/scripts/positions.py add \
  --domain "domain-name" \
  --title "Position Title" \
  --insight "The compound insight text..." \
  --stability emerging \
  --confidence 3 \
  --source-conversation "con_XXX"

# Extend existing position
python3 /home/workspace/N5/scripts/positions.py extend <id> \
  --add-component "New sub-claim" \
  --add-evidence "content-library:item-id" \
  --add-connection "other-position-id:supports" \
  --source-conversation "con_XXX"
```

## Implementation Options

### Option A: Prompt-Based (Recommended for v0)

Create `Prompts/Close Conversation Type B.prompt.md` that:
1. LLM reads conversation context
2. LLM identifies position candidates
3. LLM runs `check-overlap` for each
4. LLM decides: extend vs. create new
5. LLM executes appropriate commands
6. LLM generates summary output

**Pros:** Flexible, LLM handles nuance, easy to iterate  
**Cons:** Depends on LLM judgment quality

### Option B: Script-Based

Create `N5/scripts/conversation_end_type_b.py` that:
1. Takes conversation ID as input
2. Programmatically extracts insights (harder without LLM)
3. Runs overlap checks
4. Makes decisions based on similarity scores
5. Generates structured output

**Pros:** Deterministic, testable  
**Cons:** Hard to extract insights programmatically without LLM

### Recommendation

**Option A (Prompt-Based)** for v0. The insight extraction step fundamentally requires LLM judgment—identifying "what did V conclude here?" is not a pattern-matching task.

## Deliverables

1. **`Prompts/Close Conversation Type B.prompt.md`**
   - Frontmatter with tool: true
   - Clear instructions for the extraction → overlap-check → write workflow
   - Output template showing positions added/extended + artifacts used

2. **Test run** on this conversation (con_0CASX5AGlViD01uu)

## Output Template

When Type B completes, output should look like:

```markdown
## Type B Conversation End Summary

### Conversation: con_XXX

### Positions Updated

| Action | ID | Title | Similarity |
|--------|-----|-------|------------|
| CREATED | new-position-id | New Position Title | N/A |
| EXTENDED | existing-id | Existing Title | 0.72 |

### New Position Details
- **new-position-id**: [Brief description of what was added]

### Extensions Made
- **existing-id**: Added component "X", linked evidence "Y"

### Artifacts Referenced in Conversation
- `file 'path/to/file.md'` - [how it was used]
- `https://example.com` - [how it was used]

### Knowledge Units Used
- Content Library: item-id-1, item-id-2
- Meetings: meeting-folder-name
- [Other references]
```

## Constraints

- **Minimal scope**: Just calls existing positions.py functionality
- **No new tables**: Knowledge units are summarized in output, not stored
- **Threshold**: Use 0.5-0.6 for overlap detection (verified as effective)
- **Manual trigger**: This is NOT automatic—user invokes it explicitly

## Success Criteria

- [x] Prompt file created and callable
- [x] Can extract at least 1 position from a test conversation
- [x] Correctly identifies overlap when it exists
- [x] Correctly creates new when no overlap
- [x] Output follows template format
- [x] Artifacts/knowledge units listed in summary

## Completion Signal

When done, report: "Worker type-b-conversation-end complete. Type B ready for use."

---

*Open this file in a new conversation to begin work.*


