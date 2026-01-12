---
created: 2026-01-11
last_edited: 2026-01-11
version: 0.1
provenance: con_wkgwgDeEtgUjiPYf
type: system_spec
status: draft
---
# Voice Primitives System (Spec)

## Purpose

Provide Vibe Writer with a curated, expandable repository of reusable voice primitives sourced primarily from transcripts, optimized for **V’s writing voice**.

## Canonical locations

- Canonical library (human-facing):
  - `Knowledge/voice-library/voice-primitives.md`
  - `Knowledge/voice-library/primitives/`

- Candidate review batches (HITL):
  - `N5/review/voice/`

## Source policy

- Minimum: meeting transcripts (`transcript.md` / transcript JSONL)
- Optional: other meeting blocks (when they add useful context)

## Integration points

- Vibe Writer generation:
  - retrieve 5–15 relevant primitives
  - enforce throttle + diversity

- Pangram gate:
  - run as post-check
  - rewrite targeted windows, not entire drafts

## Status

Phase 1 shell created. Extraction + seeding deferred.

