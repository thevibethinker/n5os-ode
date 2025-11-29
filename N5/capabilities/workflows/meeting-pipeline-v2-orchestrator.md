---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Meeting Pipeline v2 Orchestrator

```yaml
capability_id: meeting-pipeline-v2-orchestrator
name: "Meeting Pipeline v2 Orchestrator"
category: orchestrator
status: active
confidence: medium
last_verified: 2025-11-29
tags:
  - meetings
  - pipeline
  - automation
  - mg-series
entry_points:
  - type: script
    id: "N5/orchestration/meeting-pipeline-v2-BUILD/BUILD_PLAN_FINAL.md"
  - type: prompt
    id: "Prompts/Meeting Manifest Generation.prompt.md"
  - type: prompt
    id: "Prompts/Meeting Intelligence Generator.prompt.md"
  - type: prompt
    id: "Prompts/Meeting State Transition.prompt.md"
  - type: prompt
    id: "Prompts/Meeting Archive.prompt.md"
  - type: prompt
    id: "Prompts/Warm Intro Generator.prompt.md"
  - type: prompt
    id: "Prompts/Follow-Up Email Generator.prompt.md"
  - type: agent
    id: "⇱ 🧠 Meeting Manifest Generation Process [MG-1️⃣]"
  - type: agent
    id: "⇱ 🧠 Meeting Block Generation Process [MG-2️⃣]"
  - type: agent
    id: "⇱ 🧠 Meeting Blurbs Generation Process [MG-3️⃣]"
  - type: agent
    id: "⇱ 🧠 Warm Intro Setup [MG-4️⃣]"
  - type: agent
    id: "⇱ 🧠 Follow-Up Email Generation v2 [MG-5️⃣]"
  - type: agent
    id: "🧠 [M] -> [P] Transition [MG-6️⃣]"
  - type: agent
    id: "⇱ 🧠 Meeting Archive Automation [MG-7️⃣]"
owner: "V"
```

## What This Does

End-to-end orchestrator for the **Meeting Pipeline v2** system. Coordinates a family of MG-stage workflows (MG-1 → MG-7) and scheduled tasks that transform raw meeting artifacts into processed intelligence, follow-ups, intros, blurbs, and archived records under `Personal/Meetings/`.

## How to Use It

- Use `file 'N5/capabilities/internal/meeting-pipeline-v2.md'` for the underlying data model and lifecycle; use **this** capability when reasoning about **automation and orchestration**.
- To review architecture and build plan, open `file 'N5/orchestration/meeting-pipeline-v2-BUILD/BUILD_PLAN_FINAL.md'`.
- Control MG-series agents via the **Agents UI** or `list_scheduled_tasks`:
  - MG-1 – Manifest generation for raw `[Inbox]` meetings.
  - MG-2 – Intelligence block generation (`B01`+ core blocks).
  - MG-3 – Blurb generation for meetings needing public blurbs.
  - MG-4 – Warm intro detection + setup.
  - MG-5 – Follow-up email generation v2.
  - MG-6 – `[M] → [P]` state transition checks.
  - MG-7 – Archive automation for processed meetings.
- Run prompts interactively (e.g. `@Meeting Manifest Generation`, `@Meeting Intelligence Generator`) for manual control or debugging.

## Associated Files & Assets

- `file 'N5/capabilities/internal/meeting-pipeline-v2.md'` – internal system definition
- `file 'N5/orchestration/meeting-pipeline-v2-BUILD/BUILD_PLAN_FINAL.md'` – final architecture + worker plan
- `file 'Prompts/Meeting Manifest Generation.prompt.md'` – MG-1 manifest generator
- `file 'Prompts/Meeting Intelligence Generator.prompt.md'` – MG-2 intelligence blocks
- `file 'Prompts/Meeting State Transition.prompt.md'` – MG-6 `[M] → [P]` transition
- `file 'Prompts/Meeting Archive.prompt.md'` – MG-7 archive
- `file 'Prompts/Follow-Up Email Generator.prompt.md'` – MG-5 follow-up emails
- `file 'Prompts/Warm Intro Generator.prompt.md'` – MG-4 warm intros
- `file 'Prompts/meeting-block-generator.prompt.md'` and `file 'Prompts/meeting-block-selector.prompt.md'` – block-level helpers
- `file 'N5/scripts/meeting_pipeline/health_scanner.py'` – monitored by `🔧 Daily Meeting System Health` agent

## Workflow

At a high level, the orchestrator manages a staged pipeline:

```mermaid
flowchart TD
  A[Raw meetings in Personal/Meetings/Inbox] --> B[MG-1 Manifest Generation]
  B --> C[MG-2 Intelligence Blocks]
  C --> D[MG-3 Blurbs Generation]
  C --> E[MG-4 Warm Intro Setup]
  C --> F[MG-5 Follow-Up Email Generation]
  C --> G[MG-6 [M] -> [P] Transition Checks]
  G --> H[MG-7 Archive Automation]
  H --> I[Personal/Meetings/Archive/{YYYY}-Q{Q}]
```

**Core flow:**
- MG-1: Detect new meeting folders, generate `manifest.json` and basic structure.
- MG-2: Generate intelligence blocks (`B01`+ others) and log to `PROCESSING_LOG.jsonl`.
- MG-3: Generate external blurbs when requested.
- MG-4: Detect intro signals and prepare warm intro drafts.
- MG-5: Generate follow-up email drafts using voice system + content library.
- MG-6: Ensure all required blocks/artifacts exist before moving from `[M]` to `[P]`.
- MG-7: Move completed meetings into the canonical archive tree.

## Notes / Gotchas

- Many stages are driven by **scheduled tasks**; disabling one MG agent can stall downstream stages.
- Meeting pipeline SSOT is `Personal/Meetings/` – never write meeting files elsewhere.
- MG-2 and MG-5 are **content-heavy** and should use higher-capability models as configured in their scheduled tasks.
- Always check `Personal/Meetings/PROCESSING_LOG.jsonl` and manifests for debugging before changing pipeline behavior.

