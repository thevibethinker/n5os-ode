---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 7: Architecture & Frameworks Migration Scripts (Phases 4–5 Implementation)

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W7-ARCH-FRAMEWORKS-MIGRATION  
**Estimated Time:** 60–120 minutes  
**Dependencies:**
- Workers 4–6 complete.
- `PHASE2_target_architecture.md` (v1.1) and `PHASE3_migration_plan.md` (v1.1) reviewed.

---

## Mission
Implement migration scripts to consolidate Architecture docs under `Personal/Knowledge/Architecture/**` and conceptual frameworks/patterns/hypotheses under `Personal/Knowledge/Frameworks/**`, including compatibility stubs for `Knowledge/reasoning-patterns/`.

---

## Context

Legacy architecture and frameworks are scattered across:
- `Personal/Knowledge/Legacy_Inbox/systems/**`.
- `Personal/Knowledge/Legacy_Inbox/infrastructure/**`.
- `Personal/Knowledge/Specs/**`.
- `Inbox/20251028-132904_n5os-core/Knowledge/architectural/**`.
- `Personal/Knowledge/Legacy_Inbox/{patterns,hypotheses,reasoning-patterns}/**`.
- `Knowledge/reasoning-patterns/**`.

Phase 2/3 design centralizes:
- Architecture specs + principles → `Personal/Knowledge/Architecture/**`.
- Patterns + hypotheses + reasoning patterns → `Personal/Knowledge/Frameworks/**`.

---

## Dependencies

- Path config: `personal_knowledge.architecture` and `personal_knowledge.frameworks` can be inferred from `knowledge_paths.yaml` (or extended if needed).
- Preflight skeleton (Worker 4) has created target subdirs.

---

## Deliverables

1. Architecture migration script, e.g. `N5/scripts/knowledge_migrate_architecture.py`.
2. Frameworks migration script, e.g. `N5/scripts/knowledge_migrate_frameworks.py`.
3. Consolidated directories:
   - `Personal/Knowledge/Architecture/{principles,ingestion_standards,planning_prompts,case_studies,specs}/` populated from legacy sources.
   - `Personal/Knowledge/Frameworks/{Strategic,Operational,Patterns,Hypotheses}/` populated from legacy sources.
4. Compatibility stubs for `Knowledge/reasoning-patterns/**`.
5. Migration reports summarizing moved files and any items requiring manual review.

---

## Requirements

- **Language:** Python 3.12.
- **Non-destructive in initial runs:** Prefer copy-then-verify before deleting originals.
- **Classification:** Use simple heuristics and/or minimal LLM assistance (if permitted) to classify specs vs beliefs, patterns vs hypotheses.
- **.n5protected-aware:** Respect `.n5protected` markers.

---

## Implementation Guide

1. **Architecture Migration**

- Sources:
  - `Personal/Knowledge/Legacy_Inbox/systems/**` → `Architecture/specs/systems/`.
  - `Personal/Knowledge/Legacy_Inbox/infrastructure/**` → `Architecture/specs/infrastructure/`.
  - `Personal/Knowledge/Specs/*.md` → Architecture or Wisdom depending on content.
  - `Inbox/20251028-132904_n5os-core/Knowledge/architectural/**` → Architecture (live) + Archive (historical copy).

- Classification hint:
  - If document is about "how system works" or "how to change system" → Architecture/specs.
  - If document is more like belief/philosophy (without implementation details) → Wisdom.

2. **Frameworks Migration**

- Sources:
  - `Personal/Knowledge/Legacy_Inbox/patterns/*.md`.
  - `Personal/Knowledge/Legacy_Inbox/hypotheses/*.md`.
  - `Personal/Knowledge/Legacy_Inbox/reasoning-patterns/*.md`.
  - `Knowledge/reasoning-patterns/*.md`.

- Mapping:
  - Patterns → `Frameworks/Patterns/`.
  - Hypotheses → `Frameworks/Hypotheses/`.
  - More general frameworks → `Frameworks/Strategic/` or `Frameworks/Operational/`.

3. **Reasoning Patterns Stubs**

- After moving canonical copies under Frameworks, convert `Knowledge/reasoning-patterns/*.md` to stubs:

```markdown
---
role: compatibility_stub
canonical_path: Personal/Knowledge/Frameworks/Patterns/<filename>.md
---

This reasoning pattern now lives at `Personal/Knowledge/Frameworks/Patterns/<filename>.md`.
```

4. **Metadata Normalization (Optional)**

- For each framework/hypothesis file, ensure basic frontmatter exists for future use (`grade`, `domain`, `stability`, etc.), but keep changes minimal in this worker.

---

## Testing

1. Dry-run both scripts and inspect planned moves.
2. Execute migrations, then:
   - Verify Architecture and Frameworks trees are populated as expected.
   - Confirm no remaining live content in `Legacy_Inbox/patterns`, `hypotheses`, `reasoning-patterns` beyond archival leftovers.
   - Confirm `Knowledge/reasoning-patterns/` contains only stubs.

---

## Report Back

When complete, report with:

1. Paths to both migration scripts.
2. Counts of files moved into Architecture and Frameworks.
3. Any ambiguous files flagged for manual classification.

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-29  

