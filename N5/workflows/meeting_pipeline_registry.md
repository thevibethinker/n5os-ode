---
created: 2025-11-22
last_edited: 2025-11-22
version: 1.0
---

# Meeting Pipeline Registry (MG-1 → MG-7)

Single source of truth for the meeting-processing system.

All paths are relative to the workspace root (`/home/workspace`). `status: canonical` means "this is the current, supported implementation". Anything listed under **Legacy / superseded** should be treated as historical.

## Stage Overview

| Stage | Purpose                               | Canonical Prompt(s)                                        | Legacy / Superseded                              | Notes |
|-------|----------------------------------------|-------------------------------------------------------------|--------------------------------------------------|-------|
| MG-1  | Raw meeting → `[M]` + manifest        | `Prompts/Meeting Manifest Generation.prompt.md`            | `Prompts/meeting-block-selector.prompt.md`       | Creates `manifest.json`, renames folder to `_[M]`. |
| MG-2  | Intelligence blocks (B01–B26)         | `Prompts/Meeting Intelligence Generator.prompt.md`         | `Prompts/meeting-block-generator.prompt.md`      | Generates B01/B03/B05/B06/B07/B14/B21/B25/B26; logs to `Personal/Meetings/PROCESSING_LOG.jsonl`. |
| MG-3  | Blurbs from intelligence              | `Prompts/Blurb-Generator.prompt.md`                        | —                                                | Uses B-blocks (esp. B14/B21/B25) to generate blurbs/short summaries. |
| MG-4  | Warm intro emails                     | `Prompts/Warm Intro Generator.prompt.md`, `Prompts/warm-intro-generator.prompt.md` | older warm-intro variants (if any)               | Scanner + writer pair; generates connector-addressed warm intros. |
| MG-5  | Follow-up emails                      | `Prompts/Follow-Up Email Generator.prompt.md`              | any older follow-up email prompts (if present)   | Uses commitments + key moments to draft follow-up email(s). |
| MG-6  | `[M]` → `[P]` state transition        | `Prompts/Meeting State Transition.prompt.md`               | transition logic embedded in older block prompts | Checks manifest + artifacts, then renames folder to `_[P]`. |
| MG-7  | Archive `[P]` → Archive/YYYY-QX       | `Prompts/Meeting Archive.prompt.md`                        | ad-hoc archive/cleanup scripts                   | Moves processed meetings from Inbox to `Personal/Meetings/Archive/{YYYY}-Q{Q}/`. |

## Logging Conventions

- **Canonical pipeline log:** `Personal/Meetings/PROCESSING_LOG.jsonl` (JSONL, one object per line).
  - MG-2 **must** append entries with at least: `timestamp`, `stage: "MG-2"`, `meeting_id`, `status`, `blocks_generated`, `source`.
  - Other stages may also log here using their own `stage` values (e.g., `MG-1`, `MG-3`, `MG-6`, `MG-7`).
- `meeting-intelligence.log` is **retired** and must not be recreated.

## Workflow Location Principle (Work-in-Progress)

- **Prompts** (reusable behaviors, tools, and building blocks) live under `Prompts/` as `.prompt.md` files.
- **Workflows** (end-to-end orchestrations like the MG-1→MG-7 chain) are documented and tracked under `N5/workflows/`.
  - Each major workflow (like the meeting pipeline) should eventually have:
    - A registry/overview file (like this one).
    - A clearly defined set of canonical prompts and any legacy/superseded ones.
- Some meeting-related prompts currently live in other locations (e.g., under `N5/workflows/` itself). These will be gradually normalized back into `Prompts/` as part of future cleanup, using this registry as the authoritative map.


