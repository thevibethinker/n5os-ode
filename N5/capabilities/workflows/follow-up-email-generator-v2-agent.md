---
created: 2025-11-29
last_edited: 2025-11-30
version: 1.1
---

# Follow-Up Email Generator v2 [MG-5]

```yaml
capability_id: follow-up-email-generator-v2-agent
name: "Follow-Up Email Generator v2 [MG-5]"
category: agent
status: active
confidence: medium
last_verified: 2025-11-29
tags:
  - meetings
  - email
  - communications
  - followup
entry_points:
  - type: prompt
    id: "Prompts/Follow-Up Email Generator.prompt.md"
  - type: agent
    id: "⇱ 🧠 Follow-Up Email Generation v2 [MG-5️⃣]"
  - type: script
    id: "N5/scripts/content_library_db.py"
owner: "V"
```

## What This Does

Generates high-quality, voice-true follow-up email drafts from meeting intelligence for meetings in the MG series. Uses intelligence blocks (commitments, deliverables, key moments, metadata) plus the **Content Library** to insert canonical links, then scores each draft against a rubric before saving it into the meeting folder.

Each draft:
- Writes about promised assets (slides, articles, 1-pagers, etc.) as if they are **included in the current email** (attachments or links), rather than defaulting to "I'll send this over later" language.
- Includes an internal **Promised Deliverables Checklist (for V before sending)** at the end of `FOLLOW_UP_EMAIL.md` that enumerates every promised item and whether it is already in the content library or is a candidate to add.

## How to Use It

- Interactively: run `@Follow-Up Email Generator` on a specific meeting to generate or revise a draft.
- As automation: the scheduled task `⇱ 🧠 Follow-Up Email Generation v2 [MG-5️⃣]` scans `[M]` meetings for pending follow-ups and runs the prompt in batch mode.
- Use `file 'N5/scripts/content_library_db.py'` to query and maintain the content library backing essential links.

## Associated Files & Assets

- `file 'Prompts/Follow-Up Email Generator.prompt.md'` – full execution sequence, rubric, examples, and checklist behavior
- `file 'N5/data/content_library.db'` – content library database
- `file 'N5/scripts/content_library_db.py'` – CLI helper for link lookup
- `file 'N5/prefs/communication/voice-system-prompt.md'` – voice transformation system
- `file 'N5/prefs/communication/style-guides/follow-up-email-style-guide.md'` – style guide
- `file 'N5/prefs/communication/email.md'` – email preferences

## Workflow

```mermaid
flowchart TD
  A[Meetings with MG intelligence blocks] --> B[Harvest commitments & deliverables]
  B --> C[Query content_library.db for essential links]
  C --> D[Apply voice transformation + style guides]
  D --> E[Compose subject + structured body (assume promised assets are included in this email)]
  E --> F[Score against quality rubric (≥90/100 target)]
  F --> G[Save FOLLOW_UP_EMAIL.md in meeting folder with Promised Deliverables Checklist for V]
```

## Notes / Gotchas

- This capability must run under a **writer-quality persona** for best voice fidelity.
- Links should **never** be hard-coded; always pull from `content_library.db` or flag missing entries for follow-up.
- The **Promised Deliverables Checklist** is internal-only and must list every promised asset with a note about content-library status (existing vs candidate).
- Quality bar is intentionally high; if drafts routinely score <90, revisit style guide and prompt configuration.


