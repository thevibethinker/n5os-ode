---
created: 2026-01-11
last_edited: 2026-01-11
version: 0.1
provenance: con_wkgwgDeEtgUjiPYf
type: voice_library
status: canonical
scope: writing
source_policy: transcripts_minimum
---
# Voice Primitives (Canonical)

This is the canonical, **broad** repository of reusable “V-voice primitives” (phrases, pivots, analogy frames, metaphor families, comparison moves, disclaimers, etc.) that should be used by Vibe Writer to make outputs sound like *your writing*.

**Important:** This repository is *curated*. Automation can propose candidates, but promotion into this file (or into `Knowledge/voice-library/primitives/`) requires human approval.

## Design intent

- **Goal:** increase “sounds like V (in writing)” while avoiding repetitive catchphrase spam.
- **Non-goal:** “beat detectors” as the primary objective. We use detectors (Pangram) as a post-check, not the steering wheel.

## Capture signals (high priority)

If a transcript contains any of the following *explicit capture signals*, treat nearby language as a high-priority candidate:

- **"I’m stealing that"** → the metaphor/analogy/example immediately before/after is likely worth retaining.
- **"That’s a great way to put it" / "That lands"** → check the phrasing that triggered it.

(We’ll refine this list once we’ve seen what patterns show up in your calls.)

## How primitives are stored

We support two canonical storage shapes:

1) **Atomic primitives (preferred at scale):**
   - One primitive per markdown file in `Knowledge/voice-library/primitives/`
   - This file (`voice-primitives.md`) stays as an index + a small set of highest-value primitives

2) **Index-only canonical (acceptable early):**
   - Keep everything directly in this file

We are starting with **(1)** as the long-term target, but keeping this file usable even before seeding.

## Primitive schema (what every primitive needs)

Each primitive should include:

- **Primitive ID:** stable slug (e.g., `vp-000123_talent-as-optionality-frame`)
- **Type:** phrase | pivot | analogy | metaphor | comparison | disclaimer | framing_move
- **Exact text:** the exact wording you used (or the minimal editable unit)
- **Function:** what it accomplishes (e.g., “forces trade-off clarity”, “de-escalates moralizing”, “compresses a thesis”)
- **When to use:** conditions/triggers
- **When NOT to use:** anti-patterns / failure modes
- **Tags:** domain tags (career coaching, hiring, incentives, ethics, etc.)
- **Source:** transcript pointer(s) (meeting path + speaker + approximate timestamp if available)

## Retrieval contract (for Vibe Writer)

When Vibe Writer is generating a draft, it should retrieve a *small*, relevant set:

- Default: **5–15 primitives** for a 1,000–2,500 word piece
- Throttle: **≤1 signature phrase per 300–500 words** unless explicitly requested
- Diversity: prefer primitives not used recently (once we have history)

## Promotion workflow (Model B)

- Automation extracts candidates from transcripts → writes a review batch to `N5/review/voice/`
- Human approves/rejects/promotes
- Approved items get written to:
  - `Knowledge/voice-library/primitives/` (atomic)
  - and optionally summarized/linked here

## Status

Shell created; seeding intentionally deferred.

