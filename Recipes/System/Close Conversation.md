---
description: |
  Formal conversation end-step - resolve all conversation effects.
  Reviews files, proposes organization, executes cleanup, generates AAR, archives build tracker.
tags:
  - session
  - cleanup
  - organization
  - aar
  - conversation
---
# Close Conversation

Runs the formal **conversation-end workflow** - like Magic: The Gathering's end step, where all conversation effects are resolved.

## What This Does

**6-Phase Workflow:**

1. **Phase -1:** Lesson Extraction - Captures reusable patterns
2. **Phase 0:** AAR Generation - Creates after-action report with thread export
3. **Phase 0.5:** Artifact Symlinking - Links deliverables to AAR folder
4. **Phase 1-2:** File Organization - Reviews and moves conversation files
5. **Phase 2.5:** Placeholder Detection - Enforces P16 (Accuracy) & P21 (Document Assumptions)
6. **Phase 3:** Personal Intelligence Update - Updates your behavioral patterns
7. **Phase 3.5:** Build Tracker Archival - Archives completed tasks from BUILD_MAP
8. **Phase 4:** Git Status Check - Prompts to commit uncommitted changes
9. **Phase 4.5:** System Timeline Check - Auto-detects timeline-worthy changes
10. **Phase 5:** Thread Title Generation - Creates descriptive thread title
11. **Phase 6:** Archive & Cleanup - Cleans workspace, archives if significant

## When to Use

**Invoke when:**
- Wrapping up a conversation
- Marking work as complete
- Want formal AAR and cleanup
- Ready to archive conversation artifacts

**Commands:**
- `/close-conversation`
- "End conversation"
- "Wrap up"
- "conversation-end"

## What You Get

✅ Complete AAR with thread export  
✅ Files organized to permanent locations  
✅ Build tracker tasks archived  
✅ Git changes committed (if confirmed)  
✅ System timeline updated  
✅ Thread title generated  
✅ Clean workspace ready for next conversation

## Full Documentation

`file N5/prefs/operations/conversation-end.md`

---

**Related:**
- `recipe 'Meetings/Export Thread.md'` - AAR only (Phase 0 standalone)
- `recipe 'Meetings/Analyze Meeting.md'` - Meeting-specific processing