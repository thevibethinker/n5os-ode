---
title: Close Conversation
description: Smart close — auto-detects context (thread/drop/build) and runs appropriate close workflow
created: 2025-10-15
last_edited: 2026-02-16
version: 7.3
provenance: con_iWYnvvOstEK9TrTG
---
# Close Conversation

Auto-detect context and close this conversation appropriately.

## Instructions

1. **Get the current conversation ID** from context (it's in the system prompt under `<conversation_workspace>`)

2. **Check for Conversational Cache:**
   ```bash
   ls /home/.z/workspaces/<CONVO_ID>/CONVERSATIONAL_CACHE.md 2>/dev/null
   ```
   If this file exists, read it and note any unchecked items (`- [ ]`) for the final output reminder.

3. **Run the router** to detect context and execute the correct close:
   ```bash
   python3 Skills/thread-close/scripts/router.py --convo-id <CONVO_ID>
   ```

4. **The router will:**
   - Check SESSION_STATE.md for context signals
   - Route to `thread-close`, `drop-close`, or `build-close` automatically
   - Output JSON context for you to analyze

5. **After the script runs, you MUST:**

   ### For Thread Close (most common):
   
   a. **Generate title** following the 3-slot emoji system:
      ```
      MMM DD | {state} {type} {content} [parent_context] Semantic Title
      ```
      
      - **Slot 1 (State):** ✅ complete | ⏸️ paused | 🚧 in_progress | ❌ failed | ‼️ critical
      - **Slot 2 (Type):** 📌 normal | 🐙 orchestrator | 👷🏽‍♂️ worker | 🔗 linked
      - **Slot 3 (Content):** 🏗️ build | 🔎 research | 🛠️ repair | 🕸️ site | ✍️ content | 📝 planning | etc.
      
      See `file 'Skills/thread-close/SKILL.md'` for full emoji reference.
   
   b. **Resolve parent context** for [brackets]:
      - If `build_slug` exists → Get build title from `N5/builds/<slug>/meta.json`
      - If `orchestrator_id` or `parent_convo_id` exists → Look up that conversation's title
      - If this IS an orchestrator → No brackets
      - If standalone → No brackets
      
      Use: `python3 -c "from N5.lib.close import guards; print(guards.detect_orchestrator_context('<CONVO_ID>'))"` to check
   
   c. **Summarize** decisions and write outputs based on tier
   
   d. **Call the write function** with your generated title and summary

   e. **Echo the title in chat response (required):**
      - Include an explicit line exactly once:
        `Close Title: <full title>`
      - Do not rely on JSON viewers for title visibility.
      - This is required even when files are written successfully.

   ### For Drop Close:
   - Confirm deposit was written to `N5/builds/<slug>/deposits/`
   - Note any concerns in the deposit

   ### For Build Close:
   - Synthesize across all deposits
   - Write BUILD_AAR.md

6. **Enforce Close Contract Gate (required before claiming complete):**

   a. Create checklist JSON at:
   ```bash
   /home/.z/workspaces/<CONVO_ID>/CLOSE_CHECKLIST.json
   ```
   with these required boolean fields:
   - `title_generated`
   - `artifacts_itemized`
   - `build_folder_closed`
   - `close_artifact_written`

   b. Run:
   ```bash
   python3 N5/scripts/close_contract_check.py --checklist /home/.z/workspaces/<CONVO_ID>/CLOSE_CHECKLIST.json
   ```

   c. If this check fails, do not mark the close as complete.

7. **Surface Conversational Cache (if exists):**
   
   If CONVERSATIONAL_CACHE.md was found in step 2 with unchecked items:
   
   a. **Display reminder block:**
      ```
      📋 **Conversational Cache Reminder**
      
      The following items were held during this conversation:
      - <item 1>
      - <item 2>
      ...
      ```
   
   b. **For each item, assess actionability:**
      - Is this something Zo can act on? (schedule, draft, file, research, etc.)
      - If YES, mark with ⚡ and propose a 3-bullet action plan
      - If NO, just list it as a reminder for V
   
   c. **Format actionable items:**
      ```
      ⚡ **Actionable: <item summary>**
      Proposed plan:
      1. <first action>
      2. <second action>  
      3. <third action>
      
      Reply "go" to execute, or "skip" to dismiss.
      ```

## Incantation

You can also invoke this verbally:
- `n5:close` — Run this prompt
- `n5:close --tier 3` — Force Tier 3 close
- `n5:close --dry-run` — Preview only

## Context Detection

| SESSION_STATE has... | Routes to | Output |
|---------------------|-----------|--------|
| `drop_id` | drop-close | Deposit JSON |
| `build_slug` (no drop) | build-close | BUILD_AAR.md |
| Neither | thread-close | CLOSE_OUTPUT.json, maybe AAR |

### Thread Close Artifacts (expected)

- `CLOSE_OUTPUT.json` (machine-readable, includes `title`)
- `CLOSE_TITLE.txt` (single-line human-readable title)
- `CLOSE_OUTPUT.md` (human-readable close summary with title + summary)

## Title Generation Checklist

Before writing the title, verify:

- [ ] Date is today's date (MMM DD format)
- [ ] State emoji reflects actual completion status
- [ ] Type emoji is correct (normal/orchestrator/worker/linked)
- [ ] Content emoji matches primary work type
- [ ] Parent context in [brackets] if this thread has a parent
- [ ] Semantic title is 2-6 words describing the work

## Related Skills

- `file 'Skills/thread-close/SKILL.md'` — Full thread close docs (READ THIS for emoji reference)
- `file 'Skills/drop-close/SKILL.md'` — Pulse worker close docs  
- `file 'Skills/build-close/SKILL.md'` — Build synthesis docs
- `file 'N5/config/emoji-legend.json'` — Canonical emoji definitions
