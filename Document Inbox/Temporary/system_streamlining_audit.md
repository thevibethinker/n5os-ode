# N5 System Streamlining Audit

**Date:** 2025-10-27 22:15 ET  
**Priority:** HIGH - System integrity issue

---

## Critical Finding: commands.jsonl Corruption

### Current State
- **Current:** 140 entries, 138 are null (98.6% corruption)
- **Backup (Oct 24):** 129 entries, 128 valid commands (99.2% healthy)
- **Loss:** ~128 command registrations

### How It Happened
Based on archive evidence, there WAS a Commands/ → Recipes/ migration on Oct 27.  
The migration likely:
1. Moved user-facing workflows from Commands/ → Recipes/  
2. Accidentally corrupted commands.jsonl (internal system registry)
3. Left 121 command files in N5/commands/ orphaned

### Impact
- Standing rule "check commands.jsonl before operations" is broken
- Command discovery broken (`search-commands` won't work)
- Docgen broken (can't generate docs from corrupt registry)
- 121 commands in N5/commands/ have no trigger registration

---

## Architecture Issues Discovered

### 1. Three-Layer Command Confusion

**Current Reality:**
```
Layer 1: Recipes/            (13 files) - User workflows (slash commands)
Layer 2: N5/commands/        (121 files) - Command docs
Layer 3: N5/config/commands.jsonl (corrupted) - Command registry
```

**Problem:** Unclear relationship between layers. Are they:
- Option A: Independent systems? (Recipes = new, commands = old)
- Option B: Complementary? (Recipes = UX, commands = system ops)
- Option C: Migrating? (Commands → Recipes incomplete)

### 2. Bootstrap Duplicates

```
/Documents/Deliverables/N5_Bootstrap_v1.0.0/
/N5/exports/N5_Bootstrap_v1.0.0/
```

Both contain full N5 system snapshots. Unclear which is canonical.

### 3. Commands/ Directory Orphans

121 command .md files in N5/commands/ with:
- ❌ No triggers registered in commands.jsonl
- ❌ No corresponding recipes
- ❓ Unclear if they're active, deprecated, or documentation

---

## Streamlining Plan

### Phase 1: Restore commands.jsonl (IMMEDIATE)
```bash
# Backup current corrupt version
cp N5/config/commands.jsonl N5/config/commands.jsonl.corrupt-2025-10-27

# Restore from Oct 24 backup
cp N5/config/commands.jsonl.backup-2025-10-24 N5/config/commands.jsonl

# Verify
cat N5/config/commands.jsonl | jq -r 'select(.command != null) | .command' | wc -l
# Expect: 128
```

### Phase 2: Clarify Architecture

**Decision needed:** What is the relationship between:
1. **Recipes/** - User-facing workflows (slash invocation)
2. **N5/commands/** - Command documentation
3. **commands.jsonl** - Command registry

**Proposed Architecture:**
```
Recipes/                     - User workflows (/, natural language)
  ↓ references
N5/prefs/operations/         - SSOT workflow docs
  ↓ implemented by
N5/scripts/                  - Implementation
  ↓ registered in
N5/config/commands.jsonl     - System command registry (automation, scheduled tasks)
```

**N5/commands/** - Either:
- Option A: Auto-generated docs from commands.jsonl (docgen)
- Option B: Deprecated, migrate to Recipes/
- Option C: Keep for system-internal commands only

### Phase 3: Bootstrap Cleanup

**Decision:**
- Keep: `N5/exports/N5_Bootstrap_v1.0.0/` (if this is the canonical export)
- Archive: `Documents/Deliverables/N5_Bootstrap_v1.0.0/` → Tar + delete
- OR vice versa

### Phase 4: Commands/ Directory Strategy

**Options:**

**A. Migrate to Recipes (full transition)**
- Move useful commands from N5/commands/ → Recipes/
- Update to recipe format (YAML frontmatter)
- Delete N5/commands/
- Deprecate commands.jsonl

**B. Keep Separate (complementary systems)**
- Recipes/ = User workflows
- commands.jsonl = System automation only
- Generate N5/commands/ docs from commands.jsonl (docgen)
- Clear documentation of distinction

**C. Hybrid**
- Recipes/ = All user-visible commands
- commands.jsonl = Background/scheduled automation only
- N5/commands/ = Auto-generated docs (read-only)

---

## Questions for V

### Critical (Must answer before proceeding)

1. **commands.jsonl recovery:** Restore from Oct 24 backup? (128 commands)

2. **Architecture vision:** What should the relationship be between:
   - Recipes/ (13 files)
   - N5/commands/ (121 files)  
   - commands.jsonl (registry)

3. **Commands/ directory fate:** 
   - Migrate to Recipes?
   - Keep separate?
   - Generate from commands.jsonl?

### Important

4. **Bootstrap duplicates:** Which is canonical?
   - `/N5/exports/N5_Bootstrap_v1.0.0/`
   - `/Documents/Deliverables/N5_Bootstrap_v1.0.0/`

5. **Migration completion:** The Oct 27 Commands → Recipes migration - was that:
   - Incomplete (finish it)?
   - Wrong direction (revert it)?
   - Partial by design (some stay, some move)?

---

## Immediate Actions (Pending Approval)

### 1. Restore commands.jsonl ✅ SAFE
- Restores 128 command registrations
- No data loss (corrupt version backed up)
- Fixes command discovery immediately

### 2. Load planning prompt
- This is system architecture work
- Need design philosophy loaded

### 3. Create decision document
- Document current state
- Propose architecture options
- Get explicit decisions before major changes

---

## Risk Assessment

**Current Risk:** HIGH
- Command system partially broken
- Standing rules failing (check commands.jsonl)
- Unclear system boundaries

**Recovery Risk:** LOW
- Have good backup (Oct 24)
- Can restore without data loss
- Changes are reversible

---

## Next Steps

1. **V decides:** Restore commands.jsonl from backup?
2. **V decides:** Architecture vision (see options above)
3. **Execute:** Based on decisions, systematic cleanup
4. **Document:** Update N5.md with final architecture
5. **Test:** Verify command invocation works end-to-end

