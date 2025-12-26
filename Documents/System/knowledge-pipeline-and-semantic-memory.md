---
created: 2025-12-16
last_edited: 2025-12-16
version: 1.0
provenance: con_XKiLRFt7ycFixjsH
---

# Knowledge Pipeline + Semantic Memory (N5 OS)

## Purpose
This document is the canonical, human-readable explanation of how your information system works end-to-end:

- how raw inputs become structured knowledge
- how knowledge is distilled into durable insights
- how durable insights become **Positions** (high-signal “wisdom primitives”)
- how everything becomes retrievable through **semantic memory** (`brain.db`)

## The Big Picture (Flow)

![N5 Knowledge Pipeline](../Images/n5_knowledge_pipeline_infographic_text.png)

### TL;DR
1. **Content Library** = capture + organize raw material (the “field notes”).
2. **Distillation** = extract multiple “atoms” (claims, heuristics, patterns) and synthesize.
3. **Positions** = promote a small subset into stable, reusable stances.
4. **Brain (`brain.db`)** = one semantic substrate underneath everything (search by meaning).

---

## Stage 1 — Content Library (Capture)

### What goes in
Examples:
- meeting transcripts + summaries
- articles / URLs
- notes, drafts, snippets
- system docs (guides, principles, specs)

### What comes out
A **stored record** you can later search, re-use, and distill.

### Key property
The Content Library is intentionally high-volume. It’s allowed to be messy.

---

## Stage 2 — Distillation (Make meaning)

Distillation is the conscious process of turning a single source into **multiple reusable “atoms.”**

### The unit of output: an Atom
An atom is one of:
- **Claim** (testable statement)
- **Heuristic** (rule of thumb)
- **Mechanism** (why/how something works)
- **Framework** (structured model)
- **Question** (important uncertainty)

A single document can yield 0–N atoms.

### The standard distillation loop
1. **Extract atoms** (split)
2. **Validate** (what evidence supports it? what would falsify it?)
3. **Name** it (a compact label that’s greppable)
4. **Store** it back into your knowledge system

### Promotion gate: “Is this durable?”
Most atoms stay as general knowledge. Some become stable enough to promote.

---

## Stage 3 — Positions (Wisdom primitives)

A **Position** is your highest-signal unit of belief/stance.

### When something becomes a Position
A good candidate Position is:
- durable across contexts/time
- action-guiding (changes decisions)
- specific enough to be falsifiable
- grounded in evidence or repeated experience

### Where Positions live
- **Registry / metadata:** `N5/data/positions.db`
- **Semantic memory (embeddings):** `N5/cognition/brain.db` (tagged as `positions`)

This split matters:
- `positions.db` is the authoritative table of “what positions exist.”
- `brain.db` is the recall substrate (“find by meaning”).

---

## Stage 4 — Semantic Memory (brain.db)

### What semantic memory is
A unified “meaning index” across:
- system docs
- content library items
- meeting intelligence
- positions

So you can ask questions like:
- “What is the knowledge pipeline?”
- “What do I believe about hiring funnels?”

…and get back:
- raw sources (context)
- distilled atoms (insights)
- positions (high-signal stance)

### What we fixed/standardized in this thread
- Search results now include line metadata (`start_line`, `end_line`, and `lines=[start,end]`) so downstream renderers like `n5_load_context.py` don’t crash.
- Positions now embed into `brain.db` as the canonical embedding store.

---

## Indexing (Is documentation indexed?)

### Yes — documentation is indexed
We verified the brain currently contains:
- `Documents/System/**` resources: **134**
- `Personal/Knowledge/Architecture/**` resources: **19**

### Canonical “put it where it will be indexed” rule
If you want a document to be reliably retrievable via semantic memory, store it in one of these canonical homes:

- `Documents/System/**` (system/product documentation)
- `Personal/Knowledge/Architecture/**` (architecture/principles/standards)
- `Knowledge/content-library/**` (legacy content library; still indexed)

---

## References (Existing canon)
- Conversation-end operational standard: `N5/prefs/operations/conversation-end.md`
- Knowledge path conventions: `N5/prefs/paths/knowledge_paths.yaml`
- Ingestion standards (explicitly references brain.db): `Personal/Knowledge/Architecture/ingestion_standards/INGESTION_STANDARDS.md`


