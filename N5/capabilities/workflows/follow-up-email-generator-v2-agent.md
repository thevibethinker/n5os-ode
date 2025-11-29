---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
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

## How to Use It

- Interactively: run `@Follow-Up Email Generator` on a specific meeting to generate or revise a draft.
- As automation: the scheduled task `⇱ 🧠 Follow-Up Email Generation v2 [MG-5️⃣]` scans `[M]` meetings for pending follow-ups and runs the prompt in batch mode.
- Use `file 'N5/scripts/content_library_db.py'` to query and maintain the content library backing essential links.

## Associated Files & Assets

- `file 'Prompts/Follow-Up Email Generator.prompt.md'` – full execution sequence, rubric, and examples
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
  D --> E[Compose subject + structured body]
  E --> F[Score against quality rubric (≥90/100 target)]
  F --> G[Save FOLLOW_UP_EMAIL.md in meeting folder]
```

## Notes / Gotchas

- This capability must run under a **writer-quality persona** for best voice fidelity.
- Links should **never** be hard-coded; always pull from `content_library.db` or flag missing entries for follow-up.
- Quality bar is intentionally high; if drafts routinely score <90, revisit style guide and prompt configuration.

