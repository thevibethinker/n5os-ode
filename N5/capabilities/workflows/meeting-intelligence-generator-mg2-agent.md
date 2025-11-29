---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Meeting Intelligence Generator [MG-2]

```yaml
capability_id: meeting-intelligence-generator-mg2-agent
name: "Meeting Intelligence Generator [MG-2]"
category: agent
status: active
confidence: medium
last_verified: 2025-11-29
tags:
  - meetings
  - intelligence
  - blocks
  - automation
entry_points:
  - type: prompt
    id: "Prompts/Meeting Intelligence Generator.prompt.md"
  - type: agent
    id: "⇱ 🧠 Meeting Block Generation Process [MG-2️⃣]"
owner: "V"
```

## What This Does

Generates **core intelligence blocks** (B01, B03, B05, B06, B07, B14, B21, B25, B26) for meetings in `[M]` state that have transcripts but are missing detailed analysis. Updates each meeting's `manifest.json` and logs progress to `Personal/Meetings/PROCESSING_LOG.jsonl` as part of the Meeting Pipeline v2 MG series.

## How to Use It

- Interactively: run `@Meeting Intelligence Generator` in a build or operations conversation to process selected meetings.
- As automation: manage the `⇱ 🧠 Meeting Block Generation Process [MG-2️⃣]` scheduled task via Agents; it periodically scans `[M]` meetings and applies this prompt.
- Use this capability when you need to reason about **where intelligence blocks come from**, how they are named, and how they are logged.

## Associated Files & Assets

- `file 'Prompts/Meeting Intelligence Generator.prompt.md'` – canonical behavior spec for MG-2
- `file 'Personal/Meetings/PROCESSING_LOG.jsonl'` – canonical MG log
- `file 'N5/capabilities/workflows/meeting-pipeline-v2-orchestrator.md'` – parent orchestrator capability
- `file 'N5/capabilities/internal/meeting-pipeline-v2.md'` – internal system description

## Workflow

```mermaid
flowchart TD
  A[Meetings in [M] with transcript.jsonl] --> B[Scan for missing B01_DETAILED_RECAP]
  B --> C[Generate B01,B03,B05,B06,B07,B14,B21,B25,B26]
  C --> D[Update manifest.json block flags]
  D --> E[Append MG-2 entry to PROCESSING_LOG.jsonl]
  E --> F[Meeting ready for downstream MG stages]
```

## Notes / Gotchas

- Filenames must match the uppercase canon exactly (e.g. `B01_DETAILED_RECAP.md`).
- When re-running MG-2 on a meeting, only log blocks that are actually created or updated.
- MG-2 assumes meeting SSOT under `Personal/Meetings/`; do not point it at other directories.

