# START HERE - Phase 1 Execution on Demonstrator

**Account**: vademonstrator.zo.computer  
**Date**: 2025-10-28  
**Status**: Ready to Execute

---

## ⚠️ CRITICAL SETUP - Read First

### You ARE on Demonstrator

You're reading this ON **vademonstrator.zo.computer**. This is correct. You will BUILD Phase 1 here, not transfer to another account.

### Knowledge Base Files (MANDATORY)

**Included in transfer**:
- `planning_prompt.md` - Design philosophy (MANDATORY for system work)
- `architectural_principles.md` - P0-P22 principles (MANDATORY reference)

**Action**: Place these in `/home/workspace/Knowledge/architectural/` before starting:

```bash
mkdir -p /home/workspace/Knowledge/architectural
cp planning_prompt.md /home/workspace/Knowledge/architectural/
cp architectural_principles.md /home/workspace/Knowledge/architectural/
```

### Phase 0 Verification

**Before starting Phase 1, verify**:
1. Git repo exists at `/home/workspace/.git`
2. N5 directory structure present (`/home/workspace/N5/`)
3. Phase 0 files exist (rules.md, templates/, etc.)

**If Phase 0 incomplete**: STOP and notify V

**If Phase 0 complete**: Install pytest and verify:
```bash
pip install pytest
cd /home/workspace
pytest N5/tests/ -v
```

Expected: 34 tests passing (Phase 0 baseline)

### Environment Setup

```bash
# Install dependencies
pip install pytest

# Verify git status
cd /home/workspace
git status
git log --oneline -5

# Clean up duplicate files if present
find . -name "*\(1\)*" -type f
```

---

## Instructions for Demonstrator AI

You are beginning **Phase 1 (Core Infrastructure)** of N5 OS Core. This is a continuation from Phase 0, which is already complete and live on GitHub.

### Pre-Flight Checklist

Before starting, verify:

```bash
# 1. Confirm you're on Demonstrator account
echo "Account: vademonstrator.zo.computer"

# 2. Verify Phase 0 is complete
cd /home/workspace
git status
git log --oneline | head -5

# 3. Check current version
git describe --tags || echo "No tags yet"

# 4. Verify test suite passes
python3 -m pytest N5/tests/ -v

# 5. Confirm clean working state
git diff --stat
```

**Expected**:

- Git repo exists and is clean
- On main branch
- Phase 0 tests passing (34/34)
- Ready to begin Phase 1

---

## What to Do Next

### Step 1: Load Essential Files

Load these in order:

1. **Planning Prompt** (MANDATORY for system work):

   ```markdown
   Load file 'Knowledge/architectural/planning_prompt.md'
   ```

2. **Orchestrator Brief** (Primary instructions):

   ```markdown
   Load file 'PHASE1_ORCHESTRATOR_BRIEF.md'
   ```

3. **Detailed Plan** (Full specifications):

   ```markdown
   Load file 'PHASE1_DETAILED_PLAN.md'
   ```

### Step 2: Copy File Guard System

```bash
# Copy file protection system from transfer package
cp n5_protect.py /home/workspace/N5/scripts/
chmod +x /home/workspace/N5/scripts/n5_protect.py

# Copy documentation
cp N5-File-Protection-System.md /home/workspace/Documents/
```

### Step 3: Initialize Session

```bash
# Create Phase 1 branch
cd /home/workspace
git checkout -b phase1-core-infrastructure

# Initialize session state for this conversation
python3 /home/workspace/N5/scripts/session_state_manager.py init \
  --convo-id <your_conversation_id> \
  --type build \
  --load-system
```

### Step 4: Begin Phase 1.1

Read the orchestrator brief and detailed plan, then start with **Phase 1.1: Session State Manager**.

Follow the **Think → Plan → Execute** framework:

- 70% of time: THINK + PLAN
- 10% of time: EXECUTE (coding)
- 20% of time: REVIEW (testing)

---

## Build Order (STRICT SEQUENCE)

Must be built in this exact order due to dependencies:

1. **Phase 1.1**: Session State Manager (2h)

   - Others depend on this
   - Build first, test thoroughly

2. **Phase 1.2**: System Bulletins (1h)

   - Independent, can build after 1.1

3. **Phase 1.3**: Conversation Registry (1.5h)

   - Session State Manager integrates this

4. **Phase 1.4**: Safety System (2h)

   - Includes file guard (n5_protect.py)
   - Validates all other components

---

## Checkpoint System

After completing each sub-component (1.1, 1.2, 1.3, 1.4), report back:

```markdown
## Phase 1.X Complete

**Component**: [name]
**Time**: [actual] vs [estimate]
**Tests**: [X/Y passing]
**Coverage**: [%]
**Issues**: [any problems or learnings]
**Next**: [next component or integration testing]
```

Wait for approval before proceeding to next component.

---

## Success Criteria

Phase 1 is complete when:

- ✅ All 4 components built and working
- ✅ 35+ tests passing (target)
- ✅ Integration tests pass
- ✅ Fresh thread test passes
- ✅ Documentation complete
- ✅ Git tagged: `v0.2-phase1`
- ✅ Pushed to GitHub
- ✅ Learnings documented

---

## Key Principles

From planning prompt and architectural principles:

- **Think → Plan → Execute** (70-20-10)
- **Simple Over Easy** (SQLite &gt; Postgres, JSONL &gt; DB for logs)
- **Flow Over Pools** (bulletins = append-only)
- **Code Is Free, Thinking Is Expensive** (spend time planning)
- **P7**: Dry-run everything before execution
- **P15**: Complete before claiming
- **P19**: Error handling mandatory
- **P22**: Python for everything (LLM corpus advantage)

---

## Files in This Package

- **START_HERE.md** (this file) - Instructions
- **PHASE1_ORCHESTRATOR_BRIEF.md** - Primary brief (read this)
- **PHASE1_DETAILED_PLAN.md** - Full specs
- **TRANSFER_README.md** - Transfer context
- **n5_protect.py** - File guard system (copy to N5/scripts/)
- **N5-File-Protection-System.md** - File guard docs (copy to Documents/)

---

## Estimated Timeline

| Phase | Duration | Cumulative |
| --- | --- | --- |
| 1.1 Session State | 2h | 2h |
| 1.2 Bulletins | 1h | 3h |
| 1.3 Registry | 1.5h | 4.5h |
| 1.4 Safety | 2h | 6.5h |
| Integration Testing | 1h | 7.5h |
| Documentation | 1h | 8.5h |
| GitHub Release | 0.5h | 9h |
| Buffer | 1-2h | 10-11h |

**Total**: 10-11 hours

---

## Need Help?

If stuck:

1. Stop and step back
2. Review planning prompt principles
3. Check architectural principles
4. Ask clarifying questions
5. Document assumptions (P21)

---

## When Complete

1. Tag release: `git tag -a v0.2-phase1 -m "Phase 1: Core Infrastructure"`
2. Push to GitHub: `git push origin phase1-core-infrastructure --tags`
3. Create PR and merge to main
4. Document learnings for Main account
5. Report completion with summary

---

**Ready to begin?**

Load the orchestrator brief and start with Phase 1.1!

---

*Prepared: 2025-10-28 02:19 ET*  
*From: Main (va.zo.computer)*  
*For: Demonstrator (vademonstrator.zo.computer)*