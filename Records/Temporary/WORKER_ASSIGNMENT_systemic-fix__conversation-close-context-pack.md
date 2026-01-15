---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_qnXavDoXyEDzP7ED
---

# WORKER ASSIGNMENT: Systemic fix — Close Conversation should produce “Context Pack” for philosophy/worldview threads

## Objective
Design a systemic improvement to the Close Conversation workflow so that **philosophy/worldview-advancing conversations** reliably produce a *high-fidelity semantic context pack* suitable for:
- spawning article-writing workers
- semantic memory / positions capture
- future retrieval

This fix should prevent the failure mode: “Tier 2 close runs, but no deep semantic artifact exists for later writing.”

## Ground rules
- Scripts handle mechanics (scans, file lists, routing decisions).
- LLM writes semantics (packs, summaries, decisions, rationales).
- Must respect the N5 doctrine in `file 'Prompts/Close Conversation.prompt.md'`.
- Prefer minimal changes, additive where possible.

## Tasks
1) **Inspect current Close Conversation prompt + scripts**
   - `file 'Prompts/Close Conversation.prompt.md'`
   - Identify which tiers generate which artifacts.
   - Identify the exact gap that caused the Vibe Thinking thread to miss a detailed pack.

2) **Propose a new artifact type: Context Pack**
   - A markdown doc with YAML frontmatter
   - Sections (minimum viable):
     - Executive summary
     - Narrative retelling (high fidelity)
     - Canonical definitions / primitives
     - Key insights + rationale
     - Decisions made
     - Open questions
     - Reusable prompts/contracts
     - Candidate “positions” phrased as beliefs/doctrines
     - Artifact index (files created/updated)

3) **Define routing logic for when to generate Context Packs**
   - Option A: always for Tier 2+
   - Option B: only when conversation appears “worldview/philosophy” (detect via SESSION_STATE focus tags or heuristics)
   - Recommend default + tradeoffs (cost/benefit)

4) **Implementation plan (minimal viable)**
   - Where does the pack live? (recommend canonical location)
   - How is it named?
   - What script should create the “context bundle” for the LLM to read?
   - Where should the Librarian be invoked, and with what inputs?

5) **Deliver concrete patch plan**
   - Exact files to edit
   - Outline of changes in each
   - If adding a new script, specify what it outputs/consumes

## Output format
Return:
1) A 1–2 page design memo
2) A step-by-step implementation plan
3) A “definition of done” checklist

## Reference conversation artifact
- `file 'Records/Temporary/con_qnXavDoXyEDzP7ED__vibe-thinking_context-pack.md'` (this is the kind of artifact the system should produce automatically)

