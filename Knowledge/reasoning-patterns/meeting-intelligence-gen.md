---
created: 2025-12-22
last_edited: 2025-12-22
version: 1.0
provenance: con_ODoRhKt2V9wAWZRS
---

# Meeting Intelligence Generation Pattern

## Context
When processing raw meeting transcripts into structured intelligence blocks (MG-2), accuracy and semantic depth are critical to downstream workflows (like follow-up generation and CRM enrichment).

## Pattern: The "Iron Triangle" Synthesis
Instead of merely summarizing text, this pattern synthesizes the meeting through three distinct lenses:
1. **Mechanical (What):** Extracting explicit decisions, dates, and owners (B03 Decisions, B05 Action Items).
2. **Semantic (Why):** Identifying underlying motivations, business models, and strategic fit (B06 Business Context, B21 Key Moments).
3. **Emotional (How):** Capturing tone, subtext, and rapport quality (B07 Tone & Context).

## Execution Strategy
1. **Transcript Saturation:** Read the full transcript twice—once for facts, once for vibe.
2. **Block Inter-dependency:** Ensure B05 (Action Items) maps directly to B14 (Blurbs Requested) and B25 (Deliverables).
3. **Frontmatter Integrity:** Always include provenance and versioning to maintain the system's "Chain of Custody."
4. **Manifest State Update:** Transition the folder state programmatically only after all blocks are validated.

## Rationale
This ensures that the meeting intelligence is not just a record, but a high-fidelity data asset that V can use for automated follow-ups and relationship compounding.

