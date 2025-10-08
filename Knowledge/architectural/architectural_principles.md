---
date: "2025-09-21T00:00:00Z"
last-tested: "2025-09-21T00:00:00Z"
generated_date: "2025-09-21T00:00:00Z"
version: 1
category: core
priority: high
related_files: "['N5/knowledge/ingestion_standards.md']"
---
# N5 Architectural Principles

These principles are sourced on every run. They define how Zo should process information, what to load into context, and how to prevent data loss and drift.

## 0) LLM Sourcing Directive (Rule-of-Two)
- Always load at most two preference/config files in context:
  1. `file 'N5/knowledge/ingestion_standards.md'`
  2. `file 'N5/knowledge/architectural_principles.md'`
- Do not load additional prefs/voice files. If a third is needed, stop and ask.
- Order of precedence for conflicts: Architectural Principles > Ingestion Standards > ephemeral instructions.

## 1) Human-Readable First
- Generate human-readable outputs before any machine format.
- JSON skeletons are derived from the human text, not vice versa.

## 2) Single Source of Truth (SSOT)
- Each fact lives in exactly one reservoir file, linked everywhere else.
- Prefer updating the canonical location over duplicating content.

## 3) Voice Integration Policy (Tiered + Tags)
- Voice is applied by tier:
  - Primary (Semantic Chunks): `<voice_level>none</voice_level>`
  - Primary (Resonant Details): `<voice_level>light</voice_level>`
  - Secondary (Action Items): `<voice_level>none</voice_level>`
  - Secondary (Outstanding Questions): `<voice_level>light</voice_level>`
  - Tertiary (Insights): `<voice_level>none</voice_level>`
  - Tertiary (Sentiment): `<voice_level>none</voice_level>`
  - Quaternary (Outputs/Copyable Blocks): `<voice_level>full</voice_level>`
- Rationale: Extraction stays neutral; copyable blocks adopt V’s voice.

## 4) Ontology-Weighted Analysis
- Use the Intellectual Priorities Ontology (P1–P19) to weight extraction.
- Emphasize P1–P7; de-emphasize P15–P19 unless explicitly requested.

## 5) Safety, Determinism, and Anti-Overwrite
- Never overwrite protected files without explicit confirmation.
- If a filename conflict exists, auto-version: `_v2`, `_v3`, … and log.
- Keep a rolling backup and write an audit line per operation.

## 6) Mirror Sync Hygiene
- If a file suddenly appears empty or truncated, suspect mirror sync.
- Action: halt writes, snapshot directory, compare against last known checksums, then proceed.

## 7) Idempotence and Dry-Run by Default
- Support `dry-run` mode for any workflow that writes files or schedules events.
- Re-running the same instruction should produce identical end-state unless inputs changed.

## 8) Minimal Context, Maximal Clarity
- Keep prompts self-contained; avoid excessive file loading.
- Summon only what is needed to execute with precision (Rule-of-Two enforced).

## 9) Copyable Blocks Philosophy
- Provide crisp, ready-to-paste blocks for follow-ups and questions.
- Avoid boilerplate; surface the crux and let V add connective tissue.

## 10) Calendar & Time Semantics
- When creating follow-ups, propose calendar entries with clear descriptions like: “Processed via N5 Ingestion – [Component]”.
- Respect the user’s timezone; never auto-schedule without confirmation.

## 11) Failure Modes and Recovery
- If transcript quality is low or uncertainty >25%, pause for better input.
- On any exception, write a minimal incident note to logs and stop before destructive actions.

## 12) Testing in Fresh Threads
- To validate changes, run workflows in a new thread to guarantee only declared files are in context.

## 13) Naming and Placement
- Meetings go under `/home/workspace/Meetings/` using `{type}_{date}_{topic}.md`.
- Ask for location if ambiguous; never create new roots without consent.

## 14) Change Tracking
- Append a concise change log in standards files.
- Example: `2025-09-21 — Added Rule-of-Two, tiered voice policy, anti-overwrite.`

---

## Execution Checklist (Per Run)
- [ ] Load Rule-of-Two files (this file + ingestion standards).
- [ ] Apply tiered voice tags per component.
- [ ] Weight extraction via ontology (P1–P7 prioritized).
- [ ] Generate human-readable first; derive JSON after.
- [ ] Use anti-overwrite and logging; dry-run until approved.
- [ ] Offer calendar adds for action items; do not auto-send.
- [ ] Store outputs in correct folders with naming convention.