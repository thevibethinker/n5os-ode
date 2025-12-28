---
created: 2025-11-28
last_edited: 2025-11-28
version: 1
---
# Worker 2: Target Knowledge Architecture & Migration Rules

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W2-TARGET-ARCH  
**Estimated Time:** 60–90 minutes  
**Dependencies:**
- Worker 1 complete (`PHASE1_current_state_map.md` present and validated)

---

## Mission
Design the **target knowledge architecture** for V's workspace with `Personal/Knowledge/` as the single source of truth (SSOT) for human-facing knowledge, and define clear **migration rules** from the current state.

---

## Context
Phase 1 established that:
- `Knowledge/` is now a hollow shell: N5 still treats it as SSOT, but the real canon lives under `Personal/Knowledge/Legacy_Inbox/**` and related subtrees.
- `Personal/Meetings/` correctly acts as SSOT for meeting intelligence but doubles as a live pipeline workspace.
- CRM, market intelligence, and architectural principles are split between legacy `Knowledge/` paths and richer, DB-backed structures in `Personal/Knowledge/Legacy_Inbox/` and N5.

V wants:
- All knowledge canon to live under `Personal/Knowledge/` going forward.
- N5 to remain front-stage, but as a **system lens** on top of that canon rather than a competing SSOT.

---

## Deliverables

Create **one markdown document**:

- `Records/Personal/knowledge-system/PHASE2_target_architecture.md`

This doc must include:

1. **Target Folder Topology**  
   - A tree-level view of the desired structure, including at least:
     - `Personal/Knowledge/Canon/`
     - `Personal/Knowledge/Frameworks/`
     - `Personal/Knowledge/ContentLibrary/`
     - `Personal/Knowledge/CRM/` (if separate) and/or how `Legacy_Inbox/crm/` gets normalized
     - `Personal/Knowledge/MarketIntelligence/` (or chosen naming) replacing legacy `Knowledge/market_intelligence/`
     - `Personal/Knowledge/Architecture/` or similar for principles/specs
     - `Personal/Knowledge/Archive/` (for long-term cold storage)
     - How `Legacy_Inbox/` is to be treated (archived vs. reorganized)
     - Relationship to `Personal/Meetings/` and `Records/`

2. **Role Definitions & SSOT Declarations**  
   - For each major area, define:
     - **Role** (what lives here)
     - **SSOT status** (Yes/No, and for what domain)
     - **Examples** of expected content.
   - Explicitly declare:
     - SSOT for knowledge canon
     - SSOT for CRM
     - SSOT for meeting intelligence
     - SSOT for system specs/architecture docs

3. **N5 Integration & Surfaces**  
   - Describe how N5 should interact with the new layout:
     - Where N5 **reads** canonical knowledge
     - Where N5 **writes** digests, logs, and DBs
     - How N5 knowledge digests (`N5/knowledge/digests/*.md`) relate to `Personal/Knowledge/`
   - Clarify which directories are **system-only** vs. **user-facing knowledge**.

4. **Migration Rules (Semantic, Not Mechanical)**  
   - For each major legacy area (as described in Phase 1), specify **rules** like:
     - "All `Personal/Knowledge/Legacy_Inbox/stable/company/*.md` → `Personal/Knowledge/Canon/Company/`"
     - "`Personal/Knowledge/Legacy_Inbox/crm/` becomes `Personal/Knowledge/CRM/` with a single SSOT DB + profiles."
     - "`Knowledge/crm/individuals/` is either merged or deprecated (state clearly)."
   - These are **conceptual rules**; Worker 3 will design the actual stepwise migration.

5. **Meeting & Records Interfaces**  
   - Define how and when meeting intelligence (from `Personal/Meetings/`) should be promoted into `Personal/Knowledge/` (e.g., recurring insights, stakeholder patterns, GTM lessons).
   - Clarify the role of `Records/` vs. `Personal/Knowledge/` (history/logs vs. curated knowledge).

6. **Open Questions / Design Decisions**  
   - List any unresolved questions or forks in the road (e.g., naming conventions, how aggressive to be with deprecating `Knowledge/`), with recommended options.

---

## Requirements

- **Design-only:** Do **not** move, rename, or delete any files. This worker produces a design document only.
- **Grounded in Phase 1:** All proposals must acknowledge the current-state realities documented in `PHASE1_current_state_map.md`.
- **Opinionated but reversible:** Provide clear recommendations, but in a way that can be implemented stepwise and rolled back if needed.
- **N5 front-stage:** Make N5's role explicit as a system lens, not a competing SSOT.

---

## Implementation Guide

Suggested steps:

1. **Re-read Phase 1 map**
   - Extract the key existing clusters: canon, semi_stable, CRM, GTM, architectural principles, meetings, digests.

2. **Propose the target `Personal/Knowledge/` layout**
   - Start from how V naturally thinks: canon, frameworks, CRM, GTM, systems/architecture, wisdom.
   - Layer in ContentLibrary as a service-oriented subtree.

3. **Align N5 surfaces with this layout**
   - Decide what becomes system-only (e.g., N5/knowledge, N5/logs/**, DBs) vs. what should be consumable knowledge.

4. **Write migration rules**
   - For each major legacy path, specify its destination (or deprecation) in the new layout.

5. **Clarify meeting + records interactions**
   - When does a meeting insight “graduate” into the knowledge base?
   - How do Records/ artifacts get promoted or linked?

---

## Testing

- Verify file exists:
  - `ls -lh Records/Personal/knowledge-system/PHASE2_target_architecture.md`
- Sanity check contents:
  - Sections for: Target Folder Topology, Role Definitions, N5 Integration, Migration Rules, Meeting/Records interfaces, Open Questions.
  - Uses concrete example paths and is consistent with Phase 1 map.

---

## Report Back

When this worker is complete, report to the orchestrator with:

1. Confirmation that `PHASE2_target_architecture.md` exists and is populated.
2. A 3–5 sentence summary of the **target architecture**.
3. Any key tradeoffs or open questions that should be resolved before implementation (Phase 3).

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-28  

