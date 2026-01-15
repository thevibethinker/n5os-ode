---
created: 2026-01-14
last_edited: 2026-01-14
version: 1
provenance: Vibe Researcher (d0f04503-3ab4-447f-ba24-e02611993d90)
status: Draft / Discovery
---
# N5 OS Kernel: Export Candidates

This document tracks the capabilities, infrastructure, and Quality of Life (QoL) improvements identified for export to create a "Vanilla+" N5 distribution.

## 1. Core "OS" Infrastructure (The Scaffolding)
*The invisible layer that makes Zo smarter and safer.*

- [ ] **Session State Manager** (`N5/scripts/session_state_manager.py`)
    - *Why:* This is the brain. It allows the AI to maintain context across long threads, track artifacts, and "remember" the state of work. Without this, Zo is amnesiac.
- [ ] **N5 Safety Protocols** (`N5/scripts/n5_protect.py`, `N5/lists/detection_rules.md`)
    - *Why:* Prevents accidental deletion of critical infrastructure. Essential for a builder who is experimenting.
- [ ] **Debug Logger** (`N5/scripts/debug_logger.py`)
    - *Why:* Enforces the "scientific method" for error fixing. Prevents circular error loops.
- [ ] **Context Loading System** (`N5/scripts/n5_load_context.py`)
    - *Why:* Allows the user to switch modes (Builder vs. Writer vs. Strategist) and load specific rules/files automatically.

## 2. The Meeting Intelligence Engine (The Killer App)
*The system that turns raw audio into structured knowledge.*

- [ ] **Standardize Meeting Folder** (Script/Prompt)
    - *Why:* Enforces a clean filesystem hierarchy (`YYYY-MM-DD_Topic`).
- [ ] **The "B-Block" Generators** (Prompts `B01` through `B35`)
    - *Why:* This is the atomic unit of N5 intelligence. Breaking transcripts into Decisions (B03), Risks (B11), and Insights (B31) is vastly superior to generic summaries.
    - *Selection:* We should export the core set (B01-Recap, B02-Commitments, B03-Decisions) and the "Intel" set (B31-Stakeholder, B35-Linguistics).
- [ ] **Meeting Manifest System** (State tracking `[M]` -> `[P]` -> `[C]`)
    - *Why:* Allows tracking which meetings have been processed vs. pending.

## 3. The Reflection & Knowledge System
*Tools for thinking and synthesis.*

- [ ] **Reflection Workflow** (Morning Pages, Weekly Review prompts)
    - *Why:* High-leverage use of AI for personal clarity.
- [ ] **The "R-Block" System** (R01-Personal, R02-Learning, R06-Synthesis)
    - *Why:* Structuring thoughts allows them to be queried later.
- [ ] **Knowledge Graph Scaffolding**
    - *Why:* The folder structure for `Knowledge/` (Entities, Concepts, Library) is a massive QoL improvement over a flat list.

## 4. Developer/Builder Quality of Life
*Tools that make building on Zo easier.*

- [ ] **Prompt Engineering Standards** (`N5/prefs/workflows/researcher_workflow.md` etc.)
    - *Why:* The Persona definitions and routing contracts.
- [ ] **"Build Capability" Workflow**
    - *Why:* The Architect -> Builder pattern. It creates a plan before writing code.

## 5. User Experience / Interface
- [ ] **The "Command" System Pattern**
    - *Why:* Teaching the user they can just type `@Command` instead of writing a long prompt.
- [ ] **Visual/Markdown Styling**
    - *Why:* The consistent use of headers, YAML frontmatter, and citations.

## 6. Exclusions (To Discuss)
- [ ] **Proprietary Data:** Careerspan JD Logic, specific CRM databases (`people.db`), private keys.
- [ ] **Heavy External Dependencies:** Scripts that require complex local setups (like `gfetch` or specific API keys she might not have yet).


---

## DEEP AUDIT FINDINGS (Append-Only)

### 7. PII/Personal Data Scan Results
*Locations that contain personal information and MUST be scrubbed:*

- [ ] **Email addresses found in scripts:**
    - `N5/scripts/akiflow_bridge.py` — hardcoded Aki email
    - `N5/scripts/gmail_scan_sent.py` — hardcoded `attawar.v@gmail.com`
    - `N5/scripts/crm_query.py` — example email `vrijen@mycareerspan.com`
    - `N5/scripts/meeting_attendee_check.py` — checks `@mycareerspan.com` domain
    - Multiple scripts have `va@zo.computer` reference
- [ ] **Personal context files:**
    - `Personal/Health/synthesis/Vrijen-Bio-Context.md` — personal health data
    - `Knowledge/content-library/personal/psychographic-portrait-linkedin-*.md` — V's authentic voice
    - `Knowledge/stable/careerspan-timeline.md` — company-specific
- [ ] **Name references in prefs:**
    - `N5/prefs/block_type_registry.json` — mentions "Vrijen" in B07, B14 definitions
    - Persona routing contract has V-specific mappings

### 8. The Persona System (HIGH VALUE — Export Candidate)
*This is the "brain" of the system.*

- [ ] **Core Personas to Export:**
    - Operator (navigation, routing, state)
    - Builder (implementation)
    - Researcher (external info synthesis)
    - Writer (polished communication)
    - Strategist (decision frameworks)
    - Teacher (explanations)
    - Debugger (QA, verification)
    - Level Upper (meta-reasoning)
    - Librarian (organization, state sync)
- [ ] **Routing Contract:** `N5/prefs/system/persona_routing_contract.md`
    - *Action:* Strip V-specific persona IDs, make generic
- [ ] **NOT TO EXPORT:**
    - Nutritionist, Trainer (personal/health domain)
    - Careerspan-specific personas

### 9. The Rules System (HIGH VALUE — Export as Template)
*User Rules in Zo settings — export as starter templates.*

- [ ] **Universal Rules (Export):**
    - Session State initialization rule
    - Debug logging discipline rule
    - File protection rule (`.n5protected`)
    - Progress reporting rule (P15)
    - YAML frontmatter rule
- [ ] **Personal Rules (DO NOT Export):**
    - Bio-log check-in rule
    - Careerspan name spelling rule
    - V-OS Tags rule (V's personal workflow)
    - Health context loading rule

### 10. The Block System (THE KILLER APP)
*The atomic units of meeting intelligence.*

- [ ] **Essential Blocks to Export (B-series):**
    - B01: Detailed Recap
    - B02: Commitments
    - B03: Decisions Made
    - B04: Open Questions
    - B05: Action Items
    - B06: Business Context
    - B11: Risks & Flags
    - B15: Energy & Sentiment
    - B21: Key Moments
    - B23: Context & Continuity
- [ ] **Advanced Blocks (Optional Export):**
    - B07: Warm Introductions (needs CRM)
    - B08: Stakeholder Intel (needs CRM)
    - B14: Blurbs Requested (needs voice system)
    - B31: Stakeholder Research
    - B35: Linguistic Primitives
- [ ] **Reflection Blocks (R-series):**
    - R01: Personal Insight
    - R02: Learning Note
    - R03: Strategic Thought
    - R06: Synthesis

### 11. The Context Loading System
*Makes Zo context-aware.*

- [ ] **Files to Export:**
    - `N5/prefs/context_manifest.yaml` (stripped of personal paths)
    - `N5/scripts/n5_load_context.py` (genericized)
- [ ] **Context Categories to Keep:**
    - `build` — coding, implementation
    - `strategy` — planning, decisions
    - `system` — lists, operations
    - `safety` — destructive ops
    - `writer` — content creation
    - `research` — deep analysis
    - `general` — fallback
- [ ] **Context Categories to REMOVE:**
    - `health` — personal health stack

### 12. The Reflection/Journal System
*High-value QoL for personal development.*

- [ ] **Prompts to Export:**
    - `Prompts/reflections/morning-pages.prompt.md`
    - `Prompts/reflections/evening-reflection.prompt.md`
    - `Prompts/reflections/weekly-review.prompt.md`
    - `Prompts/reflections/gratitude.prompt.md`
- [ ] **Script to Export:**
    - `N5/scripts/journal.py` (check for PII)
- [ ] **To OMIT:**
    - `temptation-check-in.prompt.md` (too personal)

### 13. Folder Structure (THE SCAFFOLD)
*The organization itself is valuable.*

```
N5/
├── config/           # System configs (sanitized)
├── prefs/            # Preferences hub
│   ├── communication/  # Voice & style
│   ├── operations/     # Workflow protocols
│   ├── principles/     # P-series principles
│   └── system/         # Core system rules
├── scripts/          # Utility scripts (sanitized)
├── templates/        # Build/block templates
└── workflows/        # Reusable workflows

Prompts/
├── Blocks/           # B-series generators
│   └── Reflection/   # R-series generators
└── reflections/      # Journal prompts

Knowledge/
├── architectural/    # System design docs
├── reasoning-patterns/  # Reusable thinking
└── (user populates)  

Lists/                # SSOT list system
Documents/            # User documents
Personal/             # Private area
```

### 14. Safety & Protection (NON-NEGOTIABLE)
*Guardrails that prevent disasters.*

- [ ] **Scripts:**
    - `N5/scripts/n5_protect.py` — directory protection
    - `N5/scripts/n5_safety.py` — safety checks
- [ ] **Rules:**
    - `.n5protected` marker file system
    - Blast radius analysis
    - Dry-run enforcement

### 15. Voice & Communication (ADVANCED)
*V's voice transformation system — genericize for export.*

- [ ] **Files to Review:**
    - `N5/prefs/communication/voice-transformation-system.md`
    - `N5/prefs/communication/patterns/`
    - `N5/prefs/communication/style-guides/`
- [ ] **Action:** Strip V-specific examples, keep the framework

---

## EXPORT STRATEGY PROPOSAL

### Tier 1: The Kernel (Essential)
1. Session State Manager (prompt-based version)
2. Persona System + Routing Contract (genericized)
3. File Protection System
4. Core Block Generators (B01-B06, B11)
5. Folder Structure Template
6. Core User Rules Template

### Tier 2: Quality of Life
1. Journal/Reflection System
2. Context Loading (genericized manifest)
3. Debug Logging Discipline
4. R-series Reflection Blocks

### Tier 3: Advanced
1. Voice Transformation Framework (anonymized)
2. Advanced Blocks (B07, B08, B14, B31, B35)
3. Build Planning Protocol (Architect pattern)

---

## PII SCRUBBING CHECKLIST

- [ ] Replace all `attawar.v@gmail.com` → `user@example.com`
- [ ] Replace all `vrijen@mycareerspan.com` → `user@company.com`
- [ ] Replace all `va@zo.computer` → `handle@zo.computer`
- [ ] Replace all `@mycareerspan.com` domain checks → `@company.com`
- [ ] Remove `Vrijen`, `Attawar`, `V` name references
- [ ] Remove all Careerspan references
- [ ] Remove health context files entirely
- [ ] Remove psychographic portrait files
- [ ] Genericize persona IDs or make them placeholder
- [ ] Remove Aki/Akiflow specific integrations
- [ ] Remove phone numbers from any configs


---

## V'S CONFIRMATIONS (2026-01-14)

### Confirmed for Export ✓
- [x] Session State Manager
- [x] Safety Protocols (n5_protect)
- [x] Debug Logger
- [x] Context Loading System
- [x] Reflection Workflow (Morning Pages, Weekly Review)
- [x] R-Block System (R01-R06)
- [x] Knowledge Graph Scaffolding
- [x] Prompt Engineering Standards (Personas)
- [x] Build Capability / Architect Pattern
- [x] Build Orchestration System
- [x] **Content Library System** (added)
- [x] **Semantic Memory** (brain.db + n5_memory_client.py)

### Semantic Memory Export Notes
V's semantic memory setup uses:
- `N5/cognition/n5_memory_client.py` — The client library
- `N5/cognition/brain.db` — SQLite database for chunks
- `N5/cognition/brain.hnsw` — HNSW index for fast similarity
- Provider: OpenAI `text-embedding-3-large` (requires OPENAI_API_KEY)
- Dependencies: `openai`, `hnswlib`, `rank_bm25`, `sentence_transformers` (optional)

**For friend's setup:**
1. Install deps: `pip install openai hnswlib rank_bm25`
2. Set `OPENAI_API_KEY` in environment
3. Initialize empty brain.db with schema
4. Run indexer on her content

### Deferred / Not Exporting
- [ ] Incantum command system (Zo has native @ commands now)
- [ ] Health context (personal)
- [ ] Careerspan-specific workflows
- [ ] Nutritionist/Trainer personas

---

## CONTENT LIBRARY SYSTEM (Addition)

*High-value knowledge capture system.*

### Files to Export:
- [ ] `N5/scripts/content_ingest.py` — Ingests articles/content
- [ ] `Knowledge/content-library/` folder structure template
- [ ] `N5/prefs/ingestion/` — Ingestion protocols

### Folder Structure:
```
Knowledge/
└── content-library/
    ├── articles/       # Saved articles
    ├── frameworks/     # Mental models
    ├── playbooks/      # How-to guides
    ├── references/     # Reference material
    └── personal/       # Personal context (PII - exclude)
```

### Key Feature:
- Auto-ingest from `save_webpage` tool
- YAML frontmatter with source, tags, created date
- Indexed into semantic memory for retrieval

---

## PARALLEL WORKSTREAM: PII Tracking

Spawned Worker 001 to enhance `.n5protected` with PII tracking.
See: `/home/.z/workspaces/con_GVEpFCdNSkLXYuwW/workers/worker_001_pii_tracking.md`

Goal: Add `contains_pii: true` flag to protection markers so export scripts automatically exclude sensitive files.

