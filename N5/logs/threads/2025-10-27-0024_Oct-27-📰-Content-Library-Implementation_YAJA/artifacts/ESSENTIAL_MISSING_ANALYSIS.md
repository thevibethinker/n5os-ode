# Essential Components Missing from Core

**Analysis Date**: 2025-10-27  
**Current Core**: 32 commands, 23 scripts

---

## 1. ✅ MUST ADD: spawn-worker capability

**Why Essential:**
- Enables parallel work execution
- Core to N5's multi-threaded workflow model
- Users will want to delegate tasks to parallel conversations

**What to add:**
- `spawn-worker.md` command (needs creation)
- `spawn_worker.py` script (exists)
- Documentation on worker pattern

**Use case**: "Research X while I work on Y" → spawn worker conversation

---

## 2. 🤔 CONSIDER: Backup/Restore

**Why Potentially Essential:**
- Users will modify their N5 installation
- Need safety net before experiments
- Git helps but not enough for data (Lists, Knowledge)

**What would be needed:**
- `backup-n5.md` command
- `restore-n5.md` command  
- Simple tar.gz + manifest approach
- Store in `~/.n5_backups/`

**Decision**: ???

---

## 3. 🤔 CONSIDER: Config Validator

**Why Potentially Essential:**
- Users will edit prefs, commands.jsonl, schemas
- Invalid JSON breaks system
- Helpful to validate before committing

**What would be needed:**
- `validate-config.md` command
- `n5_config_validator.py` script
- Checks: JSON syntax, schema compliance, references

**Decision**: ???

---

## 4. 🤔 CONSIDER: Dependency Checker

**Why Potentially Essential:**
- Commands reference scripts
- Scripts import modules
- Users need to know what's missing

**What would be needed:**
- `check-deps.md` command
- `n5_dependency_check.py` script
- Validates: Python imports, script references, file paths

**Decision**: ???

---

## 5. ❌ NOT CORE: Orchestrator Builder

**Why NOT Essential:**
- Advanced use case
- Requires understanding of N5 internals
- Can be expansion pack

**Decision**: Confirmed exclusion per V

---

## 6. 🤔 CONSIDER: Update Checker

**Why Potentially Essential:**
- Users need to know when core has updates
- Simple version check against GitHub
- Optional but helpful

**What would be needed:**
- `check-updates.md` command
- `n5_update_checker.py` script
- Compares local vs remote version

**Decision**: ???

---

## 7. ❌ NOT NEEDED: Everything Else

**Definitely NOT core:**
- Meeting workflows → Expansion
- Social media → Expansion
- Job scraping → Expansion
- CRM → Expansion
- Reflections → Expansion
- All V-specific business logic → Private

---

## Recommendation Priority

**Must Have (P0):**
1. spawn-worker capability ← V explicitly requested

**Nice to Have (P1):**
2. Config validator (prevents broken systems)
3. Dependency checker (helps troubleshooting)

**Optional (P2):**
4. Backup/restore
5. Update checker

**Question for V:** Which of P1/P2 should go into core vs. future expansion?

---

**Status**: Analysis complete, awaiting decision  
**Next**: Add spawn-worker + any others V approves
