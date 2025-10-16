---
date: "2025-10-16T00:00:00Z"
version: 2.1
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
