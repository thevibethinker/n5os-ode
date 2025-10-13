---
date: "2025-10-12T00:00:00Z"
version: 2.0
category: design
priority: high
---
# Design Principles

These principles guide system architecture and information design.

## 8) Minimal Context, Maximal Clarity

**Purpose:** Efficiency in token usage and cognitive load

**Rules:**
- Keep prompts self-contained; avoid excessive file loading.
- Summon only what is needed to execute with precision (Rule-of-Two enforced).
- Load modules selectively based on task needs.

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


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Split 400-line monolithic architectural principles document into 5 focused modules: core.md (principles 0,2), safety.md (5,7,11,19), quality.md (1,15,16,18,21), design.md (3,4,8,20), operations.md (6,9,10,12,13,14,17). Created lightweight index for navigation.
- Context: Monolithic principles document was loaded entirely every time, wasting tokens and context window. Different tasks need different subsets of principles. User wanted Rule-of-Two compliance with selective loading.
- Resolution: Achieved ~70% context reduction for typical operations. Can now load index + 1-2 relevant modules instead of entire document. Follows Principle 20 (Modular Design) and Principle 8 (Minimal Context).


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Split 400-line monolithic architectural principles document into 5 focused modules: core.md (principles 0,2), safety.md (5,7,11,19), quality.md (1,15,16,18,21), design.md (3,4,8,20), operations.md (6,9,10,12,13,14,17). Created lightweight index for navigation.
- Context: Monolithic principles document was loaded entirely every time, wasting tokens and context window. Different tasks need different subsets of principles. User wanted Rule-of-Two compliance with selective loading.
- Resolution: Achieved ~70% context reduction for typical operations. Can now load index + 1-2 relevant modules instead of entire document. Follows Principle 20 (Modular Design) and Principle 8 (Minimal Context).


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Split large monolithic configuration/principle documents into focused modules that can be loaded selectively based on task needs, reducing token usage and improving context efficiency.
- Context: Architectural principles document was 400+ lines and loaded entirely every time, wasting tokens. Needed selective loading based on actual task requirements.
- Resolution: Split into 5 focused modules (core, safety, quality, design, operations). Can now load index + 1-2 modules instead of entire document. Reduced context by ~70% for typical operations.


**Example from lesson extraction (2025-10-12):**
- Thread: con_JB5UD88QWtAkoaXF
- Issue: Split large monolithic configuration/principle documents into focused modules that can be loaded selectively based on task needs, reducing token usage and improving context efficiency.
- Context: Architectural principles document was 400+ lines and loaded entirely every time, wasting tokens. Needed selective loading based on actual task requirements.
- Resolution: Split into 5 focused modules (core, safety, quality, design, operations). Can now load index + 1-2 modules instead of entire document. Reduced context by ~70% for typical operations.

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
