---
date: "2025-10-12T00:00:00Z"
version: 2.0
category: design
priority: high
---
# Design Principles

These principles guide system architecture and information design.

## 8) Minimal Context, Maximal Clarity

**Purpose:** Efficient token usage, focused execution

**Rules:**
- Keep prompts self-contained; avoid excessive file loading.
- Summon only what is needed to execute with precision.
- Load files selectively based on task requirements.

**When to apply:**
- Designing workflows
- Creating commands
- Structuring documentation
- Building automation

**Implementation:**
- Modular file structure
- Context-aware loading
- Progressive detail (index → module → detail)

---

## 20) Modular Design for Context Efficiency

**Purpose:** Enable selective loading and efficient operation

**Rules:**
- Break large monolithic outputs into focused, selectively-loadable modules.
- Align structure with actual usage patterns (when would someone need this?).
- Enable progressive loading: load minimal context first, then load detail as needed.
- Each module should serve a specific purpose and be independently useful.

**When to apply:**
- Large documents (>500 lines)
- Multi-purpose systems
- Reference documentation
- Configuration files

**Rationale:** Large context windows are expensive; selective loading is efficient.

**Example from thread export modular refactoring (2025-10-12):**
- Monolithic thread export → 6 files aligned with 5-phase framework
- Each file independently useful
- Load only what's needed for specific tasks

**Anti-patterns:**
- One massive file that must be loaded entirely
- Arbitrary splits (by size rather than purpose)
- Circular dependencies between modules
- Modules that can't stand alone

---

## 3) Voice Integration Policy (Tiered + Tags)

**Purpose:** Apply appropriate voice level by content type

**Rules:**
- Voice is applied by tier:
  - Primary (Semantic Chunks): `<voice_level>none</voice_level>`
  - Primary (Resonant Details): `<voice_level>light</voice_level>`
  - Secondary (Action Items): `<voice_level>none</voice_level>`
  - Secondary (Outstanding Questions): `<voice_level>light</voice_level>`
  - Tertiary (Insights): `<voice_level>none</voice_level>`
  - Tertiary (Sentiment): `<voice_level>none</voice_level>`
  - Quaternary (Outputs/Copyable Blocks): `<voice_level>full</voice_level>`

**Rationale:** Extraction stays neutral; copyable blocks adopt V's voice.

**When to apply:**
- Meeting ingestion
- Content generation
- Email drafting
- Document creation

---

## 4) Ontology-Weighted Analysis

**Purpose:** Prioritize extraction based on intellectual priorities

**Rules:**
- Use the Intellectual Priorities Ontology (P1–P19) to weight extraction.
- Emphasize P1–P7; de-emphasize P15–P19 unless explicitly requested.

**When to apply:**
- Meeting processing
- Content analysis
- Information extraction
- Knowledge ingestion

**Reference:** See `file 'Knowledge/ontology/intellectual_priorities.md'` for full ontology
