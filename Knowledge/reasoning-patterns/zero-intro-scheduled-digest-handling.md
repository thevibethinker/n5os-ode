---
created: 2025-12-06
last_edited: 2025-12-06
version: 1.0
---

# Pattern: Zero-Intro Scheduled Digest Handling

## Context

Scheduled task scans a set of meetings for warm intro opportunities using semantic signals stored in dedicated blocks (e.g., `B07_WARM_INTRO_BIDIRECTIONAL.md`). In some runs, **no eligible signals exist** (blocks missing or absent), but the task should still complete cleanly and produce a useful digest.

## When to Use

- Scheduled digest run over a corpus (meetings, contacts, tasks) where:
  - Inputs are structurally present (folders, manifests), but
  - The specific signal block for this workflow (e.g., B07 warm-intro) is missing or unpopulated.
- You must **avoid placeholder/stub outputs** but still want observability and a clear success/failure signal.

## Steps

1. **Scan Canonical Scope**
   - Enumerate all eligible items in the canonical location (e.g., `[M]` meeting folders in `Personal/Meetings/Inbox` within the last 30 days).
   - Count unique items (e.g., unique `[M]` folder names) for the "meetings scanned" metric.

2. **Check for Signal Blocks**
   - Search within scope for the expected signal block (e.g., `B07_WARM_INTRO_BIDIRECTIONAL.md`).
   - If **zero** such blocks exist in the time window, short-circuit semantic detection: record that the warm-intro pipeline is not yet activated.

3. **Skip Generation, Not the Digest**
   - Do **not** generate any INTRO files or modify manifests, because there are no real opportunities.
   - Still create the digest markdown file for the day, with:
     - `Meetings scanned`
     - `Intro signals detected = 0`
     - `Email pairs generated = 0`
     - Clear statement that no signal blocks were present.

4. **Surface Configuration State**
   - In the digest notes, document configuration status:
     - Whether the generator prompt file exists.
     - That no B07 blocks were found (and therefore semantic detection did not run).
   - This turns a "no-op" run into a **useful health check** for the pipeline.

5. **Avoid Unnecessary Manifest Writes**
   - When zero signals are detected, **do not** update per-meeting manifests with `warm_intros_generated` unless there's a defined schema for the "none detected" state.
   - This keeps manifests from being polluted with ambiguous or ad-hoc fields.

## Outcomes

- The scheduled task completes successfully even when there are zero intro opportunities.
- The digest provides transparent observability (what was scanned, what was missing).
- No placeholder email drafts or misleading manifest entries are created.
- Future runs can immediately show the transition from "no B07 blocks" to "intro signals present" without confusion.

