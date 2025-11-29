---
created: 2025-11-29
last_edited: 2025-11-29
version: 1
---
# Worker 3: Migration Plan & Guardrails

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W3-MIGRATION-PLAN  
**Estimated Time:** 60–90 minutes  
**Dependencies:**
- Worker 1 complete (`PHASE1_current_state_map.md` present and validated)
- Worker 2 complete (`PHASE2_target_architecture.md` present and validated)

---

## Mission
Translate the Phase 2 target architecture into a **concrete, stepwise migration plan** and **safety guardrails**. This worker designs *how* to implement the realignment (scripts, sequences, checks) but does **not** actually move, rename, or delete files.

---

## Context (from Phase 2 summary)

- `Personal/Knowledge/` is the **SSOT for human-facing knowledge**, with subtrees for Canon, Frameworks, ContentLibrary, CRM, MarketIntelligence, Architecture, Wisdom, Logs, Archive, and a time-bounded Legacy_Inbox.
- `Personal/Meetings/` is the **SSOT for meeting intelligence**, while `Records/` is explicitly for historical/audit trails and design docs.
- CRM and GTM are to be normalized under `Personal/Knowledge/CRM/` and `Personal/Knowledge/MarketIntelligence/` with markdown as the human layer and DBs as implementation detail.
- N5 acts as a **system lens**: reading from `Personal/Knowledge/**` and `Personal/Meetings/**`, writing digests/logs/DBs into N5 and system areas, and only promoting curated insights into the knowledge SSOT.
- `Knowledge/` is downgraded to a thin **compatibility shell** (no SSOT domains) with a README pointing to `Personal/Knowledge/` and a temporary mirror for high‑risk automations.

---

## Deliverables

Create **one markdown document**:

- `Records/Personal/knowledge-system/PHASE3_migration_plan.md`

It must include:

1. **Migration Phases & Order of Operations**  
   - Break the migration into discrete phases (e.g., "CRM realignment", "GTM/MarketIntelligence", "Architecture & Principles", "Canon & Archive", "Compatibility shell cleanup").
   - For each phase, specify:
     - Pre-conditions (what must already be true)
     - Actions (at the level of "move this subtree there", "update these configs", not literal shell commands)
     - Post-conditions and validation checks.

2. **Path-Level Migration Rules (Concrete)**  
   - For each major legacy area identified in Phase 1, write explicit rules like:
     - `Personal/Knowledge/Legacy_Inbox/stable/company/*` → `Personal/Knowledge/Canon/Company/`
     - `Personal/Knowledge/Legacy_Inbox/crm/**` → `Personal/Knowledge/CRM/**`
     - `Personal/Knowledge/Legacy_Inbox/market_intelligence/**` → `Personal/Knowledge/MarketIntelligence/**`
     - Decide fate of `Knowledge/crm/individuals/**` (merge vs. deprecate) and `Knowledge/reasoning-patterns/**`.
   - Include handling for: hypotheses, patterns, personal-brand/social-content, stakeholder_research, systems specs, intelligence pipelines, and any other key clusters from Phase 1.

3. **Safety & Guardrails**  
   - Define how to use `.n5protected` and other mechanisms to prevent destructive mistakes during migration.
   - Specify when to:
     - Take Git snapshots
     - Run N5 maintenance/audit scripts (e.g., daily_guardian, monthly_audit) as validation
     - Perform dry-run previews for bulk moves (>5 files) before actual changes.
   - Identify any high-risk areas (e.g., DBs, `Personal/Meetings/`, N5 internals) where only minimal or no structural change should occur.

4. **Automation Refactor Plan**  
   - List which scripts, prompts, and scheduled tasks must be updated to use the new `Personal/Knowledge/**` and `Personal/Meetings/**` paths.
   - For each major family (CRM, GTM, architecture loading, document/media curation, conversation-end workflows), specify:
     - Old assumptions (e.g., `Knowledge/` as SSOT)
     - New path conventions
     - Suggested refactor approach (e.g., centralizing path constants in one config file).

5. **Compatibility Shell Strategy for `Knowledge/`**  
   - Define what, if anything, should remain in `Knowledge/` during a compatibility window.
   - Specify criteria and a timeline for when it is safe to:
     - Stop mirroring anything into `Knowledge/`
     - Update N5 prefs/docs to no longer treat `Knowledge/` as special
     - Potentially retire or repurpose `Knowledge/`.

6. **Testing & Verification Plan**  
   - Describe how to validate that the migration succeeded, including:
     - Directory sanity checks (e.g., "no live canon remains in Legacy_Inbox except Archive")
     - Running key N5 scripts in check/dry-run mode
     - Spot-checking CRM, GTM, and architecture loads under the new layout.

---

## Requirements

- **Design-only:** Do **not** perform any file operations. All moves/renames/deletes should be described as plans, not executed.
- **Aligned with Phase 2:** All migration rules must be consistent with the target architecture in `PHASE2_target_architecture.md`.
- **Safety-first:** Every phase must include explicit guardrails and validation.
- **Actionable:** The plan should be concrete enough that a Builder persona (or future worker) can implement it stepwise.

---

## Implementation Guide

Suggested steps:

1. Re-read `PHASE1_current_state_map.md` and `PHASE2_target_architecture.md` to extract all major legacy → target mappings.
2. Group migrations into logical phases that minimize blast radius and keep the system usable between steps.
3. For each legacy cluster (CRM, GTM, architecture, canon, patterns, social content, etc.), define precise path mappings.
4. Layer on safety: `.n5protected`, Git checkpoints, dry-runs, and maintenance/audit checks.
5. Map automation families to new paths, ensuring no orphaned references to `Knowledge/` remain.
6. Design the compatibility window for `Knowledge/` and conditions for its eventual retirement.

---

## Testing

- Verify file exists:
  - `ls -lh Records/Personal/knowledge-system/PHASE3_migration_plan.md`
- Sanity check contents:
  - Clear sections for: Phases & Order, Path-Level Rules, Safety/Guardrails, Automation Refactor Plan, Compatibility Shell Strategy, Testing & Verification.
  - Uses concrete paths and is coherent with Phases 1 and 2.

---

## Report Back

When this worker is complete, report to the orchestrator with:

1. Confirmation that `PHASE3_migration_plan.md` exists and is populated.
2. A short summary of the migration phases and safety strategy.
3. Any constraints or implementation questions that should be resolved before actual moves.

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-29  

