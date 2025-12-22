---
created: 2025-12-11
last_edited: 2025-12-11
version: 2
---
# Ingestion Standards

Defines how content enters, flows through, and elevates across N5's knowledge systems—operationalizing DIKW at personal scale.

---

## 1. Foundational Principles

### 1.1 DIKW as a Looped System

DIKW (Data → Information → Knowledge → Wisdom) is a **loop**, not a one-way ladder:

- Transitions are mediated by **context** (semantic understanding) and **human judgment**
- Reversible: knowledge can be downgraded, wisdom can be revised
- Wisdom is **ultra-lossy**: a compressed, operational form of many roots, *not* a substitute for those roots

**The key insight:** AI makes DIKW operational by enabling the *transformation pipeline*, not just automating tasks.

### 1.2 Context + Grade Architecture

| Dimension | What It Is | What It Determines |
|-----------|------------|-------------------|
| **Context** | Semantic understanding — what this means, why it matters, where it should go | Routing decisions |
| **Grade** | DIKW tier — position in the transformation pipeline | Elevation tracking |

**Context without Grade** = smart organization with no destination  
**Grade without Context** = tiers without a mechanism to move between them  
**Context + Grade** = an operational DIKW pipeline

### 1.3 AI as Exoskeleton

- AI **amplifies** V's cognition, judgment, and style—it does not replace or override them
- RAG/semantic search **shrinks the search surface**—it is never the decider
- Human-in-the-loop for: creation/elevation of Wisdom, modification of core principles, architectural changes

---

## 2. The DIKW Implementation

| DIKW Tier | N5 Implementation | What Lives Here | Storage |
|-----------|------------------|-----------------|---------|
| **Data** | Raw Inputs | Meeting transcripts, emails, voice notes, articles — anything unprocessed | `Inbox/`, conversation workspaces |
| **Information** | Content Library | Organized, referenceable blocks — links, snippets, structured articles | `content-library-v3.db` + `ContentLibrary/content/` |
| **Knowledge** | Intelligence + Stances | Synthesized patterns, validated insights, normative beliefs | `Personal/Knowledge/Intelligence/`, `Personal/Knowledge/Stances/` |
| **Wisdom** | Sacred Texts | Core principles (P00–P37), mental models, decision frameworks | `Personal/Knowledge/Canon/`, `Personal/Knowledge/Wisdom/` |

### 2.1 Two Kinds of Content Value

When evaluating chunks for ingestion:

**Informational Value:**
- Novelty / non-redundancy — adds ideas not already covered
- Clarity / precision — says something crisp that anchors reasoning
- Generativity — produces useful downstream questions or patterns
- Centrality — core to V's worldview vs. peripheral detail

**Characteristic Value:**
- Stylistic density — distinct patterns worth preserving
- Signature voice — recognizably "V-ish" or desired external style
- Transferability — patterns reusable without copying verbatim

---

## 3. The Four Destinations

### 3.1 Brain (Cognition Layer)

**Purpose:** Semantic recall for natural language queries ("how does V prefer X", "what's our approach to Y")

**Storage:** `N5/cognition/brain.db` (SQLite + embeddings)

**INCLUDE:**
- `Personal/Knowledge/**/*.md` — All elevated knowledge
- `N5/prefs/**/*.md` — Operational preferences and protocols
- `Knowledge/stable/**/*.md` — Canonical stable references
- `Knowledge/reasoning-patterns/**/*.md` — Extracted reasoning approaches

**EXCLUDE:**
- Meeting transcripts (too noisy)
- `Inbox/` content (transient)
- `**/Archive/**` content (stale)
- Auto-generated logs
- Files with `brain: false` in frontmatter

**Role:** RAG substrate that *shrinks search surface*. Never the decider of truth.

### 3.2 Content Library v3

**Purpose:** Structured access to operational handles and reference content (Information tier)

**Storage:** `Personal/Knowledge/ContentLibrary/content-library-v3.db`

**INCLUDE:**
- **Links** — Calendly, product URLs, trial codes, operational handles
- **Snippets** — Bios, boilerplate, templates
- **Articles** — Long-form reference content (full text in `ContentLibrary/content/`)
- **Frameworks** — Mental models, methodologies
- **Media** — Videos, podcasts, decks (references)

**NOT for Content Library:**
- CRM data (separate system)
- Meeting records (separate system)
- Operational preferences (prefs → Brain)
- Stances/beliefs (Knowledge tier, not Information)

### 3.3 Knowledge Layer (Stances + Intelligence)

**Purpose:** The normative layer between Information and Wisdom — synthesized patterns, validated beliefs

**Storage:** 
- `Personal/Knowledge/Intelligence/` — Synthesized aggregators
- `Personal/Knowledge/Stances/` — Structured belief objects (future)

**What goes here:**
- Go-to-market intelligence
- Competitive synthesis
- Validated positions with evidence roots
- Insights V actively leverages

**Key property:** Every knowledge object should have **roots** — explicit references to underlying evidence in Content Library, meetings, or conversations.

### 3.4 Wisdom Layer (Canon + Sacred Texts)

**Purpose:** Core principles, mental models, decision frameworks — the "second soul"

**Storage:**
- `Personal/Knowledge/Canon/` — VibeThinker posts, foundational beliefs
- `Personal/Knowledge/Wisdom/` — Systems, principles, worldviews

**Elevation criteria:**
- Has survived multiple challenges
- Guides actual decisions repeatedly
- Worth preserving even if all supporting material were lost

**Key property:** Every Wisdom object must have **digital roots** — append-only references to underlying material that can never be destroyed.

---

## 4. Ingestion Workflows

### 4.1 External Content (Article/Link)

```
Source URL
    │
    ├─[Always]─► Content Library ingest (metadata + type)
    │
    ├─[If valuable]─► Full text to ContentLibrary/content/<slug>.md
    │
    └─[If high-value]─► Brain reindex picks it up
```

**Evaluation questions:**
- Does this add novel ideas not already covered? (Informational value)
- Is the style worth preserving? (Characteristic value)
- Is it reference material I'll need to find again? (Content Library)
- Does it challenge or support existing beliefs? (Knowledge layer candidate)

### 4.2 Knowledge Elevation (Info → Knowledge → Wisdom)

```
Raw information (meeting, research, article)
    │
    ▼
[Context extraction] — What is this, really?
    │
    ▼
[Grade assessment] — Which DIKW tier?
    │
    ├─[Information]─► Content Library block
    │
    ├─[Knowledge]─► Personal/Knowledge/Intelligence/ or Stances/
    │                (with evidence roots linked)
    │
    └─[Wisdom candidate]─► Propose for Sacred Texts
                          (human approval required)
```

**Transition triggers:**
- **Data → Information:** Structured, organized, referenceable
- **Information → Knowledge:** Synthesized, validated, connected to other beliefs
- **Knowledge → Wisdom:** Compressed, operational, has survived challenges

### 4.3 Conversation-End Knowledge Distribution

For conversations primarily about *understanding*, *worldview*, *strategic thinking*:

1. **Extract stance-worthy claims** — thesis + sub-claims
2. **Route to appropriate tier:**
   - Full document → Content Library (Information)
   - Structured stance → Stances layer (Knowledge)
   - Principle-worthy → Candidate for Sacred Texts (Wisdom)
3. **Link & integrate** — connect to related beliefs, add evidence pointers
4. **Update roots** — conversation becomes a root for the stance (append-only)

### 4.4 CRM/People Knowledge

```
Meeting or interaction
    │
    ▼
Meeting Intelligence extracts person context
    │
    ▼
Updates: Knowledge/crm/individuals/<name>.md
    │
    ▼
Brain reindex includes CRM files
```

---

## 5. Frontmatter Standards

### Required (all knowledge files):

```yaml
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: X.Y
---
```

### Optional (for DIKW tracking):

```yaml
grade: data|information|knowledge|wisdom
domain: [career, product, systems, personal]
stability: durable|provisional|experimental
form: article|snippet|stance|principle|spec
brain: false  # Exclude from Brain indexing
source: <url>  # Original source if external
topics: [AI, career]  # Content Library alignment
```

### For Wisdom objects:

```yaml
roots:
  - type: content_library
    id: <item-id>
  - type: meeting
    path: <meeting-path>
  - type: conversation
    id: <conversation-id>
supersedes:
  - id: <old-belief-id>
    note: "Why this evolved"
```

---

## 6. Brain Indexing Configuration

**Directories to index (priority order):**

```bash
python3 N5/scripts/memory_indexer.py \
  /home/workspace/Personal/Knowledge \
  /home/workspace/N5/prefs \
  /home/workspace/Knowledge/stable \
  /home/workspace/Knowledge/reasoning-patterns
```

**Exclusion patterns:**
- `**/Archive/**`
- `**/Inbox/**`
- `**/_quarantine/**`
- `**/node_modules/**`
- `**/*.transcript.md`
- Files with `brain: false` frontmatter

**Recommended schedule:** Nightly reindex via scheduled task

---

## 7. Decision Tree: Where Does This Go?

```
Is it raw, unprocessed input?
    YES → Data tier (Inbox, stays in conversation workspace)
    NO  ↓

Is it a URL, snippet, or operational handle?
    YES → Content Library (Information tier)
    NO  ↓

Is it organized reference material worth finding again?
    YES → Content Library + ContentLibrary/content/ → Brain indexes it
    NO  ↓

Is it a synthesized belief/position with evidence?
    YES → Knowledge tier (Intelligence/ or Stances/)
    NO  ↓

Is it a core principle that guides decisions?
    YES → Wisdom tier (Canon/ or Wisdom/) — human approval required
    NO  ↓

Is it operational preferences for Zo?
    YES → N5/prefs/ → Brain indexes it
    NO  ↓

Probably transient — leave in workspace, don't persist
```

---

## 8. Human-in-the-Loop Boundaries

### AI Can Run Autonomously:
- Chunking & embedding
- Similarity queries & coverage checks ("Where is this already discussed?")
- Suggesting routes based on Context
- Maintenance scans (duplicates, orphaned roots, drift detection)
- Data → Information transitions

### Human Must Decide:
- Creation/elevation to Wisdom tier
- Modification of existing Wisdom objects
- Architectural principle changes
- What to include in Sacred Texts
- Stance validation and confidence levels

---

## 9. Compatibility & Migration Notes

- `Knowledge/` (root) is a **compatibility shell** — new content goes to `Personal/Knowledge/`
- `Knowledge/architectural/ingestion_standards.md` points here
- Legacy content in `Knowledge/crm/`, `Knowledge/stable/` remains indexed until migrated
- Content Library v2 items should be migrated to v3 schema

---

*Ingestion Standards v2.0 — Operationalizing DIKW at Personal Scale — 2025-12-11*

