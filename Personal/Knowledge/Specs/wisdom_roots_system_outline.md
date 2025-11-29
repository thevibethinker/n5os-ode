---
created: 2025-11-23
last_edited: 2025-11-23
version: 1
---
# Wisdom Roots & Exoskeleton System – Outline

## Purpose

Define the conceptual and architectural blueprint for a system where:
- AI acts as an **exoskeleton**, not a robot.
- Personal knowledge behaves like a **water system** (healthy flows) rather than static reservoirs.
- Canonical beliefs and principles (**Wisdom**) are backed by explicit, inspectable **roots** in underlying material.
- Retrieval / similarity (RAG-like substrate) reduces search surface area without ever becoming the **decider** of truth.

This document is the launch pad for building the actual implementation.

---

## 1. Core Concepts

### 1.1 AI as Exoskeleton
- AI amplifies V's cognition, judgment, and style; it does **not** replace or override them.
- The more custom-fit and integrated the system, the safer and more powerful it becomes.
- Goal: one coherent "armor set" (Zo + N5OS + Sacred Texts + content library), not mismatched tools.

### 1.2 Water-System PKM (Flows, Not Pools)
- System should behave like healthy water infrastructure:
  - Data is **captured**, **routed**, **transformed**, and **checked**.
  - Stagnant pools (dead notes, forgotten documents) are anti-goals.
- "Healthy flow" means:
  - Every bit of data is ingested through a known process.
  - It has plausible destinations (content library, working sets, tasks, etc.).
  - It is periodically re-examined or challenged.

### 1.3 DIKW as a **Looped System**
- We use DIKW (Data → Information → Knowledge → Wisdom) only as a **loop**, never as a one-way ladder.
- Transitions are:
  - Mediated by **context** and **human judgment**.
  - Reversible: knowledge can be downgraded, wisdom can be revised.
- Wisdom is **ultra-lossy**: a compressed, operational form of many roots, *not* a substitute for those roots.

### 1.4 Two Kinds of Content

#### Informational Content
- What the text **says about the world**.
- Facts, claims, arguments, implications, principles.
- Example: "N5OS treats organization as a side-effect of good flows, not a separate task."

#### Characteristic Content
- What the text **is as a stylistic object**.
- Dense clusters of "form observations": rhythm, metaphors, sentence shapes, transitions, voice.
- Example: a particularly V-flavored turn of phrase describing a familiar idea.
- Can be harvested from V, or from external authors, when the goal is to imbue the system with certain stylistic DNA.

### 1.5 Content Library
- The place where rich chunks of external and internal material live **before** being elevated to knowledge or wisdom.
- Stores:
  - Informationally valuable chunks (novel, precise, generative ideas).
  - Characteristically valuable chunks (high-density stylistic patterns worth imitating or referencing).
- Think of it as the "soil" from which knowledge and wisdom objects grow.

### 1.6 Wisdom + Digital Roots
- A **Wisdom object** is:
  - A highly compressed, operational statement (principle, pattern, doctrine).
  - Intended to guide decisions and behavior quickly.
- Every Wisdom object must have **digital roots**:
  - Explicit references to underlying material (notes, sources, conversations, books, etc.).
  - Roots are append-only and never destroyed, even if the Wisdom object is revised or deleted.
- This preserves:
  - Auditability ("Why do we believe this?").
  - The ability to reconstruct or update Wisdom in light of new evidence.

---

## 2. Rubric – Evaluating Chunks

Goal: evaluate text in **chunks** (paragraphs/sections/pages) on both informational and characteristic axes.

### 2.1 Informational Value
- **Novelty / Non-Redundancy**
  - Does this chunk add ideas or distinctions not already well-covered elsewhere?
- **Clarity / Precision**
  - Does it say something crisp that could anchor future reasoning?
- **Generativity**
  - Does this chunk produce useful downstream questions, patterns, or design moves?
- **Centrality**
  - Is it about the core of V's worldview / system, or a peripheral detail?

### 2.2 Characteristic Value
- **Stylistic Density**
  - How many distinct stylistic observations can be extracted? (metaphor types, sentence patterns, transitions, etc.)
- **Signature Voice**
  - Is this recognizably "V-ish" (or a desired external style) in a way worth preserving?
- **Transferability**
  - Can the style patterns in this chunk be reused in other contexts without copying the content verbatim?

### 2.3 Practical Use
- For now, rubric can be **soft** (qualitative notes, not rigid scores):
  - Example labels: `high-info/high-char`, `high-info/low-char`, `low-info/high-char`, `reference-only`.
- Over time, can evolve toward simple numeric scales (0–3 per axis) to guide automation.

---

## 3. RAG as Substrate (Not Decider)

### 3.1 Role of RAG
- We use embeddings + similarity search to:
  - **Shrink the search surface area** when evaluating new or revised material.
  - Answer: "Where do we already say something like this?" and "What roots fed into this Wisdom object?".
- RAG answers:
  - "What might be the same / nearby?"
- RAG does **not** answer:
  - "Are these actually equivalent?"
  - "Which one is true?"
  - "What should remain canon?"

### 3.2 Core Workflows Using RAG

1. **Ingestion Coverage Check**
   - For each new chunk V is ingesting:
     - Embed chunk.
     - Query vector store.
     - Show nearest neighbors + short summaries.
   - Purpose: help V see **what is genuinely new** vs already present.

2. **Wisdom Roots Discovery**
   - Given a Wisdom object:
     - Pull the explicit roots.
     - Use RAG to find additional, related chunks that might deserve to be added as roots.
   - Purpose: enrich and document the grounding of each principle.

3. **Drift / Pollution Detection (Candidate Stage)**
   - When a knowledge/wisdom statement is modified:
     - Compare old vs new versions.
     - Use RAG over roots + nearby content to flag potential inconsistencies.
   - Purpose: raise *candidates* for human review, not auto-rewrite.

---

## 4. Human-in-the-Loop Design

### 4.1 Where Humans Must Decide

- **Creation / Elevation of Wisdom**
  - Only V decides when something becomes a Wisdom object.
  - RAG can suggest roots and siblings; V chooses.

- **Modification of Wisdom**
  - Any significant change to a Wisdom object:
    - Prompts a review of its roots.
    - May trigger a small W-check (sanity pass) using the RAG substrate.

- **Architectural Principle Changes**
  - Changes to core principles (e.g., Zero-Touch, exoskeleton metaphor, DIKW loop) are always human-approved events.

### 4.2 Where AI/Agents Can Run Autonomously

- **Chunking & Embedding**
  - Breaking documents into chunks and embedding them.

- **Similarity Queries & Summaries**
  - "Where is this idea already discussed?"
  - "Show me the top 5 closest chunks and how they differ."

- **Maintenance Scans**
  - Periodic checks for:
    - Highly similar chunks with divergent claims.
    - Orphaned roots (roots not referenced by any Wisdom).

---

## 5. Digital Roots & History

### 5.1 Roots Model
- Each Wisdom object keeps a structured list of **roots**, e.g.:
  - `source_type` (article, note, conversation, book, external quote)
  - `source_path_or_ref` (file path, URL, citation key)
  - `chunk_id` or `location` (paragraph index, anchor ID)
  - `notes` (why this root matters)

### 5.2 Append-Only History
- Roots are never destroyed, only **appended**:
  - Wisdom deletion or demotion keeps its roots as historical record.
  - This allows:
    - Reconstruction of why a belief existed.
    - Post-mortems when ideas are retired.

### 5.3 Self-Healing
- When drift or contradictions are detected:
  - System can:
    - Surface the conflicting statements.
    - Aggregate the relevant roots.
    - Ask V to decide: revise, split concepts, or demote to lower level.

---

## 6. Build Backlog (High-Level)

This is **not** the full implementation plan—just the major components we know we need.

1. **Data Model Sketch**
   - Objects: `Chunk`, `ContentItem`, `Wisdom`, `Root`.
   - Minimal fields for each, including IDs and metadata.

2. **Chunking & Embedding Subsystem**
   - Consistent chunking over:
     - Sacred Texts.
     - Core philosophy docs.
     - VibeThinker posts (and future content).
   - Vector index (SQLite+FAISS or similar) with metadata.

3. **Ingestion Workflow**
   - Given a new source (article, book section, post, meeting):
     - Chunk → embed → store.
     - Run coverage check ("what do we already have?").
     - Let V tag chunks with informational/characteristic labels when warranted.

4. **Wisdom Object Store**
   - Simple, structured representation of Wisdom objects (likely YAML/SQLite).
   - Each with:
     - Text of the principle.
     - Status (draft/active/deprecated).
     - Roots list.

5. **Roots Management Tools**
   - Commands / scripts / prompts to:
     - Add/edit roots.
     - View all roots for a Wisdom object.
     - Run RAG-based enrichment of roots.

6. **Maintenance & Drift Detection**
   - Periodic jobs to:
     - Flag near-duplicate or conflicting chunks.
     - Find orphaned roots.
     - Suggest W-checks when high-impact Wisdom objects shift.

7. **Interfaces & Workflows**
   - Concrete flows for V, e.g.:
     - "Ingest this book section and show me what’s actually new."
     - "Given this candidate principle, show me related chunks and propose a draft roots list."
     - "Audit this Wisdom object for consistency with its roots."

---

## 7. Scope for Phase 1 Build (Suggested)

When starting a new build thread, Phase 1 can be:

1. Limit the universe to:
   - Core productivity philosophy docs.
   - The three published VibeThinker posts.
2. Implement:
   - Chunking + embedding + vector index for this small universe.
   - A single workflow: **"Do we already have this?"** given a new paragraph.
3. Represent:
   - A handful of Wisdom objects + explicit roots, using the data model.
4. Test:
   - That the exoskeleton role of RAG feels right in practice (narrowing, surfacing, not deciding).

This outline is the starting point and should be refined/extended in the new build conversation.

