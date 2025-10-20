---
date: "2025-10-16T00:00:00Z"
version: 2.1
category: design
priority: high
---
# Design Principles

These principles guide system architecture and information design.

## 1) Human-Readable First

**Purpose:** Humans review and edit; machines consume

**Rules:**
- Generate outputs readable and editable by humans first.
- JSON formats are derived from human text, never vice versa.
- Markdown is preferred for all documentation.

**When to apply:**
- Documentation
- Reports  
- Data exports
- System design

**Anti-patterns:**
- Generating machine formats first, then reverse-engineering human docs
- Binary or encoded formats without human-readable source
- Documentation as afterthought rather than primary artifact

**Lessons Learned:**

**Noun-First Title Structure for UI Constraints (2025-10-16):**
- **Context:** Thread titles displayed in dropdown UI with limited width
- **Problem:** Verb-first titles ("Building X", "Creating Y") look identical in narrow dropdown
- **Solution:** Noun-first structure makes subjects immediately scannable ("API Design", "Database Schema")
- **Examples:**
  - ❌ "Building the conversational API system" → "Building..."
  - ✅ "Conversational API Design and Implementation" → "Conversational..."
- **Key insight:** UI constraints ARE architectural design considerations, not just stylistic preferences
- **Application:** Any naming system where truncation is expected (file names, dropdown menus, tabs, logs with width limits)
- **Pattern:** [Primary Noun/Subject] + [Context/Action] structure

---

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

**Lessons Learned:**

**Case Study: Architectural Principles Modularization (Oct 2025-10-12)**
- **Problem:** 400-line monolithic architectural principles document loaded entirely every time, wasting tokens and context window
- **Solution:** Split into 5 focused modules based on usage patterns:
  - `core.md` (P0, P2) - foundational rules
  - `safety.md` (P5, P7, P11, P19) - file operations, automation
  - `quality.md` (P1, P15, P16, P18, P21) - accuracy, completeness
  - `design.md` (P3, P4, P8, P20, P22) - architecture, information design
  - `operations.md` (P6, P9, P10, P12, P13, P14, P17) - workflows, deployments
- **Index file:** Lightweight navigation + loading guidance
- **Results:** 
  - ~70% context reduction for typical operations
  - Can load index + 1-2 relevant modules instead of entire document
  - Follows Rule-of-Two: max 2 config files for most tasks
- **Key insight:** Module boundaries should match actual usage patterns (when would someone need this?), not arbitrary size limits

---

## 22) Language Selection for Purpose

**Purpose:** Choose the right language for the task's constraints

**Decision Tree:**
```
Task involves:
├─ 80%+ calling Unix tools → Shell
├─ API-heavy + first-class SDK? → Node.js/TypeScript  
├─ Performance-critical daemon? → Go (validate need first)
├─ Complex logic/data processing → Python
├─ Prototyping/vibe-coding → Python (LLM corpus advantage)
└─ When in doubt → Python
```

**Key Trade-offs:**

| Language | Best For | Avoid For | Notes |
|----------|----------|-----------|-------|
| **Shell** | Gluing Unix tools, simple pipelines | Complex logic, error handling | Fast to write, already installed |
| **Python** | General default, data processing | High-performance daemons | Best LLM support, memory-intensive |
| **Node.js** | Web APIs (Gmail, OpenAI, Stripe) | Unix tool orchestration | First-class async, native JSON |
| **Go** | Performance-critical, concurrent | Rapid prototyping | High performance, worse ergonomics |

**Database Selection:**
- **SQLite:** Single-user, local-first, portable (N5 default) → File at `/path/to/data.db`
- **PostgreSQL:** Multi-user, network access (rarely needed in N5)

**SDK Consideration:** If a task heavily uses APIs (OpenAI, Gmail, Stripe), check which language has the best official SDK. First-class SDKs = less code, better error handling, automatic retries.

**Vibe-Coding Factor:** Python has the largest LLM training corpus → better autocomplete, fewer hallucinations. Matters for rapid prototyping and learning.

**When to apply:**
- Choosing language for new scripts
- Refactoring existing implementations
- Evaluating performance vs development speed

**Anti-patterns:**
- Python for simple glue code (use shell)
- Shell for complex logic (use Python)
- Go for everything (premature optimization)
- Ignoring SDK quality when building API-heavy tools

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
