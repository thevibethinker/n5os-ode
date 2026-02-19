---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: con_o9nkV9huRbIpeEGn
build_type: upgrade
---

# N5OS Ode v2 Upgrade — Build Plan

**Objective:** Bring the n5os-ode repo up to par with the current live N5 system, generalized for external Zo users setting up for the first time.

**Branch:** `feature/ode-v2-upgrade` on `vrijenattawar/n5os-ode`
**Repo location:** `/tmp/n5os-ode` (cloned, branch created)

---

## Scope Summary

| Dimension | Repo v1 | Target v2 | Delta |
|-----------|---------|-----------|-------|
| Personas | 6 | 9 (+Architect, Teacher, Librarian) | +3 new personas |
| Rules | 6 | ~13 (generalized set) | +7 new rules |
| Scripts | 24 (11 unreferenced) | 14 referenced + validate_repo + journal | Prune 8 meeting/content scripts, add agent_conflict_gate |
| Principles | P1-P36 (18 files) | P0.1-P37 (37 files) | +19 principle files |
| Skills | 2 (meeting-ingestion, pulse) | 6 (+close family, systematic-debugging, frontend-design) | +4 skills |
| Context manifest | V-specific paths | Generalized paths | Full rewrite |
| Routing contract | Implicit | Explicit (persona_routing_contract.md) | New file |
| Workflows | 4 files | 4+ files (add architect, teacher, librarian) | +3 workflow files |
| Docs | 22 files | Update all to reflect v2 | Updates |

---

## Drops

### Drop 1: Personas (D1)
**Type:** Content generation + generalization
**Output:** 9 generalized persona definitions in BOOTLOADER.prompt.md + updated docs/PERSONAS.md

Work:
- Generalize Operator persona (remove V-specific refs, keep routing table with placeholder IDs)
- Generalize Builder, Researcher, Writer, Strategist, Debugger (update to v3.1 quality level)
- Create generalized Architect persona (from live v3.1, remove V-specific refs)
- Create generalized Teacher persona (from live v1.0, remove Careerspan-specific examples)
- Create generalized Librarian persona (from routing contract definition)
- Update routing table in Operator to include all 9 personas
- Update docs/PERSONAS.md with all 9 personas

### Drop 2: Rules (D2)
**Type:** Content generation + generalization
**Output:** ~13 generalized rules in BOOTLOADER.prompt.md + updated docs/RULES.md

Rules to ship:
1. Session state init (simplified — no action tagger)
2. Context loading at conversation start
3. YAML frontmatter on markdown
4. Progress reporting (P15)
5. File protection (destructive ops)
6. Debug escalation (3 failures → step back)
7. Clarifying questions (always)
8. Persona routing (always — the master routing rule)
9. Session state updates (every 3-5 exchanges)
10. New directory caution (check before creating)
11. Agent conflict gate (before creating scheduled agents)
12. Pulse orchestration (when running builds)
13. Honest reporting (scripts=mechanics, AI=semantics)

### Drop 3: Principles (D3)
**Type:** File updates + additions
**Output:** Complete principles set in N5/prefs/principles/

Work:
- Add all missing principle YAML files (P0.1, P3, P4, P6, P9, P10, P12, P14, P22, P24-P31, P33-P35, P37)
- Generalize any V-specific content in principles
- Update principles_index.yaml to reflect full set
- Add P35-P39 building fundamentals as Knowledge/architectural/building_fundamentals.md
- Update docs/PRINCIPLES.md

### Drop 4: Scripts + Infrastructure (D4)
**Type:** Code update + generalization
**Output:** Updated N5/scripts/ with 14-16 referenced scripts

Work:
- Generalize all 14 referenced scripts (remove V-specific paths/refs, fix PROJECT_REPO placeholders)
- Add agent_conflict_gate.py (generalized from live)
- Keep journal.py and validate_repo.py (useful utilities)
- Remove 8 unreferenced scripts (meeting_*, content_*, positions.py)
- Update context_manifest.yaml (generalize all paths)
- Add/update persona_routing_contract.md (generalized)
- Add workflow files for Architect, Teacher, Librarian
- Update N5/cognition/ files if needed

### Drop 5: Skills (D5)
**Type:** File copy + generalization
**Output:** 6 skills in Skills/

Work:
- Keep meeting-ingestion and pulse (update if needed)
- Add close/ (universal router)
- Add thread-close/ (conversation close)
- Add drop-close/ (Pulse worker close)
- Add build-close/ (build synthesis)
- Add systematic-debugging/ (imported skill)
- Add frontend-design/ (imported skill, Anthropic version)
- Generalize any V-specific paths in skill scripts

### Drop 6: BOOTLOADER + Docs + Polish (D6)
**Type:** Content rewrite
**Output:** Updated BOOTLOADER.prompt.md, PERSONALIZE.prompt.md, README.md, all docs/

Work:
- Rewrite BOOTLOADER to install 9 personas + 13 rules
- Update PERSONALIZE.prompt.md for expanded persona set
- Update README.md with v2 features
- Update all docs/ files to reflect v2 architecture
- Update install.sh for new skills
- Update CHANGELOG.md
- Clean up Prompts/ (fix broken refs, remove dead Block prompts if V-specific)
- Final validation pass

---

## Success Criteria

- [ ] Fresh Zo user can run BOOTLOADER without errors
- [ ] All 9 personas created with correct routing
- [ ] All 13 rules installed
- [ ] `n5_load_context.py` works for all context groups
- [ ] All scripts compile without errors
- [ ] No broken file references in any prompt or doc
- [ ] No V-specific content leaks (Careerspan, personal paths, etc.)
- [ ] All 6 skills functional
- [ ] install.sh works cleanly

---

## Commit Strategy

One commit per Drop, squash-friendly:
1. `feat(personas): add Architect, Teacher, Librarian — 9 persona system`
2. `feat(rules): expand to 13 generalized rules`
3. `feat(principles): complete P0.1-P37 principle set`
4. `feat(scripts): generalize + add agent_conflict_gate, prune unreferenced`
5. `feat(skills): add close family, systematic-debugging, frontend-design`
6. `feat(bootloader): v2 rewrite with 9 personas, 13 rules, expanded docs`
