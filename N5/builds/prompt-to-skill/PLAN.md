---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_plquQK5mpVEUO74p
---

# Build Plan: Prompt-to-Skill Conversion System

## Open Questions

1. ~~Should we create a `prompt-to-skill` skill that automates future conversions?~~ **YES** - V confirmed systematic/repeatable process
2. ~~Full migration vs wrapper?~~ **FULL MIGRATION** - V confirmed
3. ~~What to do with missing scripts?~~ **BUILD THEM** - V confirmed
4. ~~What to do with original prompt?~~ **EXPUNGE** - V confirmed

## Objective

Create a systematic, repeatable process for converting high-eligibility prompts to Agent Skills format, then apply it to `Close Conversation.prompt.md` as the first case.

**Two deliverables:**
1. `Skills/prompt-to-skill/` — The conversion process itself (reusable)
2. `Skills/conversation-close/` — First application (the converted skill)

---

## Checklist

### Stream 1: Foundation (Parallel)
- [ ] D1.1: Create `prompt-to-skill` skill structure and conversion process doc
- [ ] D1.2: Create `conversation-close` skill structure (scaffold only)
- [ ] D1.3: Build missing scripts (`update_build.py`, `build_worker_complete.py`)

### Stream 2: Migration (Sequential after Stream 1)
- [ ] D2.1: Migrate conversation-close scripts to skill
- [ ] D2.2: Migrate references/assets to skill
- [ ] D2.3: Write SKILL.md with full instructions
- [ ] D2.4: Integration test + expunge original prompt

---

## Architecture Decision: Skill Structure

### Alternative A: Thin Wrapper (REJECTED)
Keep scripts in `N5/scripts/`, skill just references them.
- ❌ Not portable
- ❌ Doesn't reduce N5/scripts sprawl
- ❌ Violates "skills are self-contained" principle

### Alternative B: Full Migration (SELECTED)
Move all close-related scripts into skill, with CLI entry point.
- ✅ Self-contained, portable
- ✅ Clear ownership
- ✅ Matches Agent Skills spec intent
- ⚠️ More work upfront

### Alternative C: Hybrid (CONSIDERED)
Move unique scripts, symlink shared utilities.
- ❌ Complexity without clear benefit
- ❌ Symlinks break portability

**Decision:** Alternative B — Full Migration

---

## Phase 1: Foundation

### D1.1: prompt-to-skill Skill

**Scope:**
- `Skills/prompt-to-skill/SKILL.md` — Conversion process documentation
- `Skills/prompt-to-skill/scripts/assess.py` — Score a prompt for skill eligibility
- `Skills/prompt-to-skill/scripts/scaffold.py` — Generate skill folder structure
- `Skills/prompt-to-skill/assets/skill-template/` — Template SKILL.md

**Files Created:**
```
Skills/prompt-to-skill/
├── SKILL.md
├── scripts/
│   ├── assess.py
│   └── scaffold.py
└── assets/
    └── skill-template/
        └── SKILL.md.template
```

**Success Criteria:**
- `python3 Skills/prompt-to-skill/scripts/assess.py "Prompts/X.prompt.md"` returns eligibility score
- `python3 Skills/prompt-to-skill/scripts/scaffold.py conversation-close` creates folder structure

---

### D1.2: conversation-close Scaffold

**Scope:**
- Create empty skill structure
- No content yet (populated in Stream 2)

**Files Created:**
```
Skills/conversation-close/
├── SKILL.md (stub)
├── scripts/
├── references/
└── assets/
```

---

### D1.3: Missing Scripts

**Scope:**
- `N5/scripts/update_build.py` — Build state management (referenced by Close Conversation)
- `N5/scripts/build_worker_complete.py` — Worker completion notification

These are referenced by the prompt but don't exist. Build them.

**Note:** These stay in N5/scripts because they're build-system utilities, not close-specific.

**Files Created:**
- `/home/workspace/N5/scripts/update_build.py`
- `/home/workspace/N5/scripts/build_worker_complete.py`

**Success Criteria:**
- `python3 N5/scripts/update_build.py status <slug>` works
- `python3 N5/scripts/build_worker_complete.py --help` works

---

## Phase 2: Migration

### D2.1: Migrate Scripts

**Scope:**
Move these from `N5/scripts/` to `Skills/conversation-close/scripts/`:
- `conversation_end_router.py`
- `conversation_end_quick.py`
- `conversation_end_standard.py`
- `conversation_end_full.py`
- `conversation_pii_audit.py`

Create new unified CLI:
- `close.py` — Main entry point (`python3 Skills/conversation-close/scripts/close.py --help`)

**Files Moved:**
- `N5/scripts/conversation_end_*.py` → `Skills/conversation-close/scripts/`
- `N5/scripts/conversation_pii_audit.py` → `Skills/conversation-close/scripts/`

**Files Created:**
- `Skills/conversation-close/scripts/close.py` (new CLI wrapper)

---

### D2.2: Migrate References/Assets

**Scope:**
Copy (not move, these may be used elsewhere) to skill:
- `N5/prefs/operations/conversation-end-v5.md` → `references/`
- `N5/config/emoji-legend.json` → `assets/`
- `N5/config/commit_targets.json` → `assets/`
- Templates → `assets/templates/`

**Files Created:**
```
Skills/conversation-close/
├── references/
│   └── conversation-end-v5.md
└── assets/
    ├── emoji-legend.json
    ├── commit_targets.json
    └── templates/
        ├── tier1-output.md
        └── tier3-aar.md
```

---

### D2.3: Write SKILL.md

**Scope:**
Full skill documentation with:
- Frontmatter (name, description)
- Quick start
- Two modes (Worker Close, Full Close)
- CLI reference
- Integration with Pulse/builds

**Source:** Derive from `Close Conversation.prompt.md` content

---

### D2.4: Integration Test + Expunge

**Scope:**
1. Run skill on a test conversation
2. Verify all modes work
3. Archive original prompt to `Prompts/Archive/`
4. Update any references to point to skill

**Success Criteria:**
- `python3 Skills/conversation-close/scripts/close.py --convo-id con_test --dry-run` works
- Original prompt archived
- No broken references

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Moving scripts out of N5/scripts | Medium | Git history preserves; can move back |
| Deleting original prompt | Low | Archive first, don't delete |
| Breaking existing scheduled tasks | High | Grep for references before expunge |

---

## MECE Validation

| Item | Owner | Exclusions |
|------|-------|------------|
| prompt-to-skill SKILL.md | D1.1 | — |
| assess.py, scaffold.py | D1.1 | — |
| conversation-close scaffold | D1.2 | Content (D2.*) |
| update_build.py | D1.3 | — |
| build_worker_complete.py | D1.3 | — |
| Script migration | D2.1 | References (D2.2) |
| Reference/asset migration | D2.2 | Scripts (D2.1) |
| SKILL.md content | D2.3 | — |
| Testing + expunge | D2.4 | — |

No overlaps. No gaps. ✓

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scheduled tasks reference old prompt | Medium | High | Grep before expunge, update refs |
| Scripts have hidden dependencies | Low | Medium | Test each script in isolation |
| Import paths break after move | Medium | Medium | Update imports, add __init__.py |

---

## Success Criteria

1. **prompt-to-skill skill works:** Can assess any prompt and scaffold a skill
2. **conversation-close skill works:** All three tiers execute correctly
3. **Worker close works:** Pulse drops can close via skill
4. **Original expunged:** Prompt archived, no dangling references
5. **Process documented:** Future conversions can follow same pattern

---

## Estimated Effort

| Drop | Complexity | Est. Time |
|------|------------|-----------|
| D1.1 | Medium | 15 min |
| D1.2 | Low | 5 min |
| D1.3 | Medium | 20 min |
| D2.1 | Medium | 15 min |
| D2.2 | Low | 10 min |
| D2.3 | Medium | 15 min |
| D2.4 | Low | 10 min |

**Total:** ~90 min of Zo execution time

---

## Execution Mode

**Recommended:** Pulse with auto-spawn
- Stream 1: D1.1, D1.2, D1.3 in parallel
- Stream 2: D2.1 → D2.2 → D2.3 → D2.4 sequential (dependencies)
