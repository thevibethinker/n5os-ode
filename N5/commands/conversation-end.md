---
date: '2025-10-08T22:41:14Z'
last-tested: '2025-10-08T22:41:14Z'
generated_date: '2025-10-08T22:41:14Z'
checksum: conversation_end_v1_0_0
tags: ['conversation', 'workflow']
category: productivity
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/conversation-end.md
---
# `conversation-end`

**Version**: 1.0.0  
**Summary**: Formal conversation end-step - review temp files, propose organization, execute cleanup

---

## Purpose

The **conversation end-step** is a formal phase (like Magic: The Gathering's end step) where all conversation effects are resolved:
- Review files created in conversation workspace
- Propose permanent locations based on file type and context
- Execute batch file moves with user confirmation
- Cleanup conversation workspace
- Log conversation artifacts
- Archive conversation if requested

This is NOT just the conversation ending naturally - it's an **intentional command** that triggers the resolution phase.

---

## When to Use

**Explicit triggers**:
- User says: "End conversation", "Close thread", "Wrap up", "conversation-end"
- User exports conversation (export includes end-step)
- User marks conversation as "closed"

**Implicit triggers** (with confirmation):
- Conversation inactive for 24+ hours
- User starts new conversation on unrelated topic
- System detects natural conversation completion

---

## End-Step Workflow

### Phase 1: Inventory
```bash
# List all files created during conversation
find /home/.z/workspaces/con_[ID]/ -type f -newer [CONVERSATION_START]

# Categorize by type and directory
- scripts/
- data/
- images/
- documents/
- exports/
- temp/
```

### Phase 2: Classification
For each file, determine:
- **File type**: Extension, content analysis
- **Purpose**: What was it created for? (from conversation context)
- **Value**: Permanent vs temporary
- **Destination**: Where should it live permanently?

Classification matrix:
| Pattern | Type | Destination | Action |
|---------|------|-------------|--------|
| *.png, *.jpg | Generated image | Images/ | Move with date prefix |
| *.png (temp_*, chart_*) | Temp visualization | - | Delete |
| *meeting*.md, *transcript*.md | Meeting record | Records/Company/meetings/ | Move with date |
| *analysis*.md, *report*.md | Analysis/report | Documents/ | Move with date |
| *.py (user-requested) | Permanent script | Code/ | Move |
| *.py (temporary) | Temp automation | - | Delete |
| *.csv, *.json (export) | Data export | Exports/ | Move |
| *.csv, *.json (intermediate) | Processing temp | - | Delete |
| *article*.md, saved_page.md | Saved article | Articles/ | Move |
| *.md (draft) | Temporary note | - | Delete or ask |

### Phase 3: Propose Moves
```markdown
## Conversation End-Step: File Resolution

### Files Created: [N] total

#### Images ([X] files)
✓ concept_design.png → Images/concept_design_20251008.png
✓ wireframe.png → Images/wireframe_20251008.png
✗ temp_chart.png → DELETE (temporary visualization)

#### Documents ([Y] files)
✓ meeting_notes.md → Records/Company/meetings/2025-10-08-board-meeting.md
✓ analysis_report.md → Documents/Market_Analysis_20251008.md
? draft_ideas.md → AMBIGUOUS - Keep or delete?

#### Scripts ([Z] files)
✗ data_processor.py → DELETE (one-time script)

### Summary
- Move: [N] files
- Delete: [M] files
- Ambiguous: [K] files (require decision)

**Proceed with moves? (Y/n)**
If ambiguous files exist, resolve those first.
```

### Phase 4: Execute
```bash
# Move permanent files
for file in permanent_files:
    mv [conversation_workspace]/[file] [destination]
    echo "Moved [file] → [destination]" >> N5/runtime/file_moves.log

# Delete temporary files
for file in temp_files:
    rm [conversation_workspace]/[file]
    echo "Deleted [file] (temporary)" >> N5/runtime/file_moves.log

# Log conversation artifacts
echo "Conversation [ID] closed: [N] files moved, [M] deleted" >> N5/runtime/conversations.log
```

### Phase 5: Archive (Optional)
```bash
# If user requested conversation export/archive
conversation_summary.md → Documents/Conversations/2025-10-08-[topic].md
conversation_metadata.json → N5/runtime/conversations/con_[ID].json

# Include:
- Conversation topic/summary
- Files created and their destinations
- Key decisions made
- Commands executed
- Duration, message count
```

### Phase 6: Cleanup
```bash
# Remove conversation workspace
rm -rf /home/.z/workspaces/con_[ID]/

# Verify cleanup
test -d /home/.z/workspaces/con_[ID]/ || echo "✓ Workspace cleaned"
```

---

## Examples

### Example 1: Research Session
```
User: "conversation-end"

Zo: "## Conversation End-Step

I created 8 files during this research session:

Images (5):
✓ product_concept_1.png → Images/product_concept_1_20251008.png
✓ product_concept_2.png → Images/product_concept_2_20251008.png
✓ wireframe.png → Images/wireframe_draft_20251008.png
✗ temp_comparison.png → DELETE
✗ quick_viz.png → DELETE

Documents (3):
✓ competitor_analysis.md → Articles/competitor_analysis_20251008.md
✓ research_summary.md → Documents/Product_Research_Summary_20251008.md
✗ rough_notes.md → DELETE

Total: 5 files moving to permanent locations, 3 deleting.

Proceed? (Y/n)"

User: "Y"

Zo: "✓ Moved 5 files to permanent locations
✓ Deleted 3 temporary files
✓ Conversation workspace cleaned
✓ Logged to N5/runtime/file_moves.log

Conversation closed. See you next time!"
```

### Example 2: Meeting Processing
```
User: "End thread and archive"

Zo: "## Conversation End-Step + Archive

Files created:

Documents (3):
✓ board_meeting_transcript.md → Records/Company/meetings/2025-10-08-board-meeting-transcript.md
✓ board_meeting_summary.md → Meetings/2025-10-08-Board-Meeting-Summary.md
✗ processing_notes.md → DELETE

Note: Action items already written to Lists/must-contact.jsonl

Archive:
✓ Conversation summary → Documents/Conversations/2025-10-08-Board-Meeting-Processing.md

Total: 2 files moved, 1 deleted, 1 archived.

Proceed? (Y/n)"
```

---

## Integration

### Conversation Export
When user exports conversation, automatically trigger conversation-end:
1. Export conversation to file
2. Trigger conversation-end workflow
3. Include file moves in export summary
4. Package conversation archive

### Natural Language Triggers
- "end conversation"
- "close thread"
- "wrap up"
- "we're done here"
- "conversation-end"
- "export and close"

### System Integration
- Incantum Engine recognizes end-step triggers
- Commands continue working normally during conversation
- End-step is separate from command execution

---

## Related Commands

- `review-workspace` - Preview files before end-step
- `organize-files` - Manual file organization mid-conversation
- `cleanup-temp` - Clean old conversation workspaces (maintenance)

---

## Notes

- This is a **formal phase**, not automatic cleanup
- User must trigger it explicitly (or confirm implicit trigger)
- Safe default: Files stay in conversation workspace if end-step not executed
- Conversation workspace retained for 7 days if end-step not completed
- Can be executed mid-conversation if needed (then continue)

---

*The conversation end-step: where all effects are resolved and the board state is cleaned.*
