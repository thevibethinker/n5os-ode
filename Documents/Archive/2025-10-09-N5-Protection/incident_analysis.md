# N5.md Overwrite Incident Analysis
**Date:** 2025-10-09 04:49 UTC  
**Incident:** N5.md file overwritten to empty (0 bytes)  
**Status:** Recovered from git history

---

## Timeline of Events

### Current Incident (2025-10-09)
- **04:49 UTC**: N5.md modified to 0 bytes
- **04:50 UTC**: File recovered from git commit `1526653`
- **No git commits between**: File was overwritten without being committed first
- **Active conversation**: `con_ph7SqJYqSJWlwoGb` (empty workspace, no artifacts)
- **Recovery conversation**: `con_rftEK15ZZ8An0qMc` (current)

### Previous Incident (2025-09-20)
- **04:37 UTC**: N5.md overwritten to empty during timeline system creation
- **04:37 UTC**: Recovered from git history
- **04:39 UTC**: Created `file_protector.py` in response
- **04:41 UTC**: Implemented "Smart File Protection System"

---

## Root Cause Analysis

### What We Know

1. **File was not committed before overwrite**
   - Git shows no intermediate commits
   - File went directly from 71 lines to 0 bytes
   - Suggests a direct write operation, not a git operation

2. **Protection systems exist but are not enforced**
   - `N5/scripts/file_protector.py` exists with hard protection for N5.md
   - `N5/prefs/system/file-protection.md` clearly classifies N5.md as HARD PROTECTION
   - `N5/prefs/prefs.md` lists N5.md under "Manual-Edit Only"
   - **BUT**: These are documentation/scripts, not active guardrails

3. **Pattern: Second occurrence in ~3 weeks**
   - September 20: Overwrite during timeline system work
   - October 9: Overwrite during unknown operation
   - Both times file was emptied completely
   - Both times recovered from git

### What We Don't Know

1. **Exact triggering action**
   - No conversation artifacts in `con_ph7SqJYqSJWlwoGb`
   - No git log of the overwrite action
   - Unclear what user request or AI action triggered it

2. **Why protection didn't activate**
   - `file_protector.py` is not called automatically
   - No hooks in place to intercept file writes
   - AI tool calls don't route through protection layer

---

## The Core Problem: Documentation ≠ Enforcement

### Current State

**We have:**
- ✅ Clear classification (HARD PROTECTION)
- ✅ Protection policy documented
- ✅ Python script that can validate operations
- ✅ Git governance guidelines

**We DON'T have:**
- ❌ Automatic enforcement before file writes
- ❌ Hooks that intercept dangerous operations
- ❌ AI awareness of protection at tool-call time
- ❌ Pre-flight checks before `create_or_rewrite_file`

### The Gap

The protection system is **prescriptive** (tells AI what to do) but not **preventive** (stops AI from doing wrong thing).

When an AI:
1. Calls `create_or_rewrite_file` on N5.md
2. The tool executes immediately
3. No validation happens
4. File is overwritten
5. Protection doc is ignored

---

## Why This Keeps Happening

### Hypothesis 1: Context Loading Issues
- AIs may not load or prioritize the prefs.md protection rules
- File protection policy buried in long preference file
- Not prominent enough in system prompt

### Hypothesis 2: Tool-Level Gap
- `create_or_rewrite_file` tool has no protection built in
- AI must manually choose to respect protection
- Under time pressure or confusion, AI may skip checks

### Hypothesis 3: Refactoring Side Effect
- Recent refactor (Oct 8) moved preferences to modular structure
- May have broken assumptions about where rules live
- Protection scripts reference old paths (though they seem updated)

### Hypothesis 4: Emergency Overrides
- In recovery or fix situations, AI may bypass normal checks
- "Just fix it quickly" mentality overrides careful validation

---

## Solutions: Multi-Layer Defense

### Layer 1: AI Context & Prompting (Quick Fix)

**Add to user rules at TOP:**
```markdown
CRITICAL FILE PROTECTION:
Before ANY file write operation on these paths, you MUST:
1. Read the file first to verify current content
2. If file has content (>0 bytes), STOP and ask for explicit permission
3. Show user what will be lost
4. Require user to type "APPROVED" before proceeding

PROTECTED FILES:
- Documents/N5.md (system entry point)
- N5/prefs/prefs.md (system preferences)
- N5/config/commands.jsonl (command registry)

NEVER use create_or_rewrite_file on these without explicit approval.
```

**Pros:** Immediate, no code changes needed  
**Cons:** Still relies on AI compliance, can be overlooked

### Layer 2: Pre-Flight Validation Command (Medium Fix)

**Create N5 command: `validate-file-write`**

Usage: Before writing protected files, AI must call this command
```bash
python3 /home/workspace/N5/scripts/file_protector.py /path/to/file write
```

Modify AI instructions to require this before writes.

**Pros:** Structured validation, reusable, logged  
**Cons:** Still requires AI to remember to call it

### Layer 3: Git Pre-Commit Hook (Strong Fix)

**Install git pre-commit hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

PROTECTED_FILES=(
  "Documents/N5.md"
  "N5/prefs/prefs.md"
  "N5/config/commands.jsonl"
)

for file in "${PROTECTED_FILES[@]}"; do
  if git diff --cached --name-only | grep -q "^$file$"; then
    # File is being committed, check if it's empty or size decreased significantly
    if [ ! -s "$file" ]; then
      echo "ERROR: Protected file $file is empty!"
      exit 1
    fi
  fi
done
```

**Pros:** Catches empty files before git commit  
**Cons:** Only works if AI commits (many don't immediately)

### Layer 4: File System Watcher (Strongest Fix)

**Background daemon monitoring protected files:**
- Watches for changes to protected files
- Backs up automatically on any modification
- Alerts on suspicious changes (e.g., >90% size reduction)
- Can restore automatically

**Pros:** True enforcement, automatic, catches all writes  
**Cons:** Requires running service, more complex

### Layer 5: Backup Before Write (Pragmatic Fix)

**Modify file protection workflow:**

Before AI writes to protected file:
1. Create timestamped backup: `N5.md.backup.YYYYMMDD-HHMMSS`
2. Then proceed with write
3. Verify write succeeded
4. Keep last 5 backups, rotate older ones

**Pros:** Simple, always have recovery point  
**Cons:** Doesn't prevent bad write, just makes recovery easier

---

## Recommended Action Plan

### Immediate (Today)
1. ✅ Add prominent protection warning to user rules (top of list)
2. ✅ Update N5 timeline with this incident
3. ✅ Document this analysis for future reference

### Short-term (This Week)
4. Create backup-on-write wrapper for protected files
5. Test file_protector.py integration into workflow
6. Add git pre-commit hook for empty file detection

### Medium-term (Next 2 Weeks)
7. Create `validate-file-write` command in N5
8. Update AI training/context to use validation command
9. Add automated backup rotation system

### Long-term (Future Enhancement)
10. Implement file system watcher daemon
11. Add protection level indicators to file browser UI
12. Create "protection override log" for auditing bypasses

---

## Detection & Prevention Checklist

**Before writing to any file, AI should:**
- [ ] Check if file is in HARD_PROTECTION list
- [ ] Read current content if exists
- [ ] Verify file size > 0 if exists
- [ ] Show user preview of what will be replaced
- [ ] Get explicit "APPROVED" confirmation for protected files
- [ ] Create timestamped backup before write
- [ ] Verify write succeeded after operation
- [ ] Log operation to appropriate audit trail

**For N5.md specifically:**
- [ ] This is the system entry point - treat as critical
- [ ] 71 lines of curated content
- [ ] Has been overwritten twice in 3 weeks
- [ ] Requires highest protection level
- [ ] Consider making read-only at filesystem level

---

## Lessons Learned

1. **Documentation alone doesn't protect files**
   - Need active enforcement mechanisms
   - Policy without enforcement is just guidance

2. **AI tools need guardrails**
   - File write tools should have protection built-in
   - Can't rely on AI to always check documentation

3. **Git is excellent backup but reactive**
   - Prevents permanent loss
   - Doesn't prevent initial overwrite

4. **Refactors are high-risk periods**
   - More AI activity = more opportunities for errors
   - Need extra vigilance during system changes

5. **Multiple defense layers needed**
   - Any single layer can fail
   - Combine prompting + validation + hooks + backups

---

## Next Steps

1. User decides which protection layers to implement
2. Priority should be balancing safety vs workflow friction
3. Consider starting with Layers 1, 2, and 5 (prompting, validation command, backups)
4. Monitor for 2 weeks, then add Layer 3 (git hooks) if still having issues
5. Layer 4 (file watcher) only if problem persists

---

## Related Files

- `file 'N5/prefs/system/file-protection.md'` - Protection policy
- `file 'N5/scripts/file_protector.py'` - Protection validation script
- `file 'N5/timeline/system-timeline.jsonl'` - System incident log
- `file 'Documents/N5.md'` - The protected file in question
