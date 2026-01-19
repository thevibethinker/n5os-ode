---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_oaJd6YmS7ETcg4UZ
worker_id: W6_validation
status: pending
dependencies: [W1_placeholders, W2_init_build_script, W3_context_files, W4_prompts_fix, W5_docs_and_links]
---
# Worker Assignment: W6_validation

**Project:** n5os-ode-release-fix  
**Component:** final_validation  
**Orchestrator:** con_oaJd6YmS7ETcg4UZ  
**Estimated time:** 30 minutes

**DEPENDENCIES:** ALL other workers must complete first (W1-W5)

---

## Objective

Run the complete verification checklist, fix any remaining issues, validate all prompts, and create final git commits.

---

## Context

This is the final validation worker. All previous workers have made changes. This worker validates everything works together, catches any gaps, and commits all changes with proper git messages.

**Working directory:** `/home/workspace/N5/export/n5os-ode/`

---

## Tasks

### Task 1: Run Full Verification Checklist

Execute each verification command from PLAN.md:

```bash
cd /home/workspace/N5/export/n5os-ode

# 1. No placeholder URLs
echo "=== Check 1: Placeholders ==="
rg "PROJECT_REPO" . && echo "❌ FAIL: Placeholders remain" || echo "✅ PASS: No placeholders"

# 2. All Python files compile
echo "=== Check 2: Python Compile ==="
python3 -m py_compile N5/scripts/*.py && echo "✅ PASS: All scripts compile" || echo "❌ FAIL: Compilation errors"

# 3. Context loading works
echo "=== Check 3: Context Loading ==="
python3 N5/scripts/n5_load_context.py build && echo "✅ PASS: Context loads" || echo "❌ FAIL: Context load error"

# 4. Init build works
echo "=== Check 4: Init Build ==="
python3 N5/scripts/init_build.py verify-test --title "Verification Test"
if [ -d "N5/builds/verify-test" ]; then
    echo "✅ PASS: Build init works"
    rm -rf N5/builds/verify-test
else
    echo "❌ FAIL: Build init failed"
fi

# 5. LICENSE exists
echo "=== Check 5: LICENSE ==="
test -f LICENSE && echo "✅ PASS: LICENSE exists" || echo "❌ FAIL: No LICENSE"

# 6. Safety script works
echo "=== Check 6: Safety Script ==="
python3 N5/scripts/n5_safety.py audit && echo "✅ PASS: Safety audit works" || echo "❌ FAIL: Safety script error"
```

Document results. If any check fails, investigate and fix before proceeding.

### Task 2: Validate Block Prompts

Check all prompts in `Prompts/Blocks/`:

```bash
cd /home/workspace/N5/export/n5os-ode

echo "=== Validating Block Prompts ==="
for f in Prompts/Blocks/*.prompt.md; do
    echo "Checking: $f"
    # Check YAML frontmatter is valid
    python3 -c "import yaml; yaml.safe_load(open('$f').read().split('---')[1])" 2>/dev/null || echo "  ⚠️ YAML issue in $f"
    # Check for references to non-existent scripts
    grep -E "scripts/.*\.py" "$f" | grep -v "N5/scripts" && echo "  ⚠️ Relative path in $f"
done
echo "Block prompts checked"
```

Fix any issues found.

### Task 3: Validate Reflection Prompts

Check all prompts in `Prompts/reflections/`:

```bash
cd /home/workspace/N5/export/n5os-ode

echo "=== Validating Reflection Prompts ==="
for f in Prompts/reflections/*.prompt.md; do
    echo "Checking: $f"
    python3 -c "import yaml; yaml.safe_load(open('$f').read().split('---')[1])" 2>/dev/null || echo "  ⚠️ YAML issue in $f"
    grep -E "scripts/.*\.py" "$f" | grep -v "N5/scripts" && echo "  ⚠️ Relative path in $f"
done
echo "Reflection prompts checked"
```

Fix any issues found.

### Task 4: Check for Remaining Issues

Run a final sweep for common problems:

```bash
cd /home/workspace/N5/export/n5os-ode

echo "=== Final Sweep ==="

# Check for TODO/FIXME markers
echo "TODOs/FIXMEs:"
rg -i "TODO|FIXME" --type md --type py || echo "None found"

# Check for placeholder markers
echo "Placeholder patterns:"
rg "XXX|PLACEHOLDER|\[TBD\]|\[TODO\]" --type md --type py || echo "None found"

# Check for broken file references in prompts
echo "Broken file refs:"
rg "file\s*'" Prompts/*.prompt.md | head -20

# Verify all created directories exist
echo "Directory check:"
test -d N5/prefs/operations && echo "✅ N5/prefs/operations"
test -d N5/prefs/communication && echo "✅ N5/prefs/communication"
test -d N5/docs && echo "✅ N5/docs"
test -d N5/schemas && echo "✅ N5/schemas"
test -d Knowledge/architectural && echo "✅ Knowledge/architectural"
```

### Task 5: Create Git Commits

Stage and commit all changes with appropriate messages:

```bash
cd /home/workspace/N5/export/n5os-ode

# Check git status first
git status

# Commit 1: Placeholder fixes
git add N5/scripts/n5_load_context.py N5/scripts/content_ingest.py N5/scripts/debug_logger.py N5/scripts/journal.py N5/scripts/n5_protect.py N5/scripts/session_state_manager.py
git commit -m "fix: replace PROJECT_REPO placeholders with actual repo URL"

# Commit 2: Init build script
git add N5/scripts/init_build.py
git commit -m "feat: add init_build.py script for build capability workflow"

# Commit 3: Context files
git add N5/prefs/operations/ N5/prefs/communication/ N5/scripts/n5_safety.py N5/schemas/index.schema.json Knowledge/architectural/principles.md Lists/POLICY.md
git commit -m "feat: add missing context files referenced in manifest"

# Commit 4: Prompt fixes
git add Prompts/Close\ Conversation.prompt.md Prompts/Journal.prompt.md Prompts/Build\ Capability.prompt.md
git commit -m "fix: simplify Close Conversation prompt and correct script paths"

# Commit 5: Documentation
git add LICENSE N5/docs/ N5/README.md N5/prefs/prefs.md docs/DEPENDENCIES.md
git commit -m "docs: add LICENSE, ARCHITECTURE, CONTRIBUTING and fix broken links"

# Final status
git log --oneline -5
```

Note: If some files weren't changed by other workers, adjust the commit groupings accordingly. The goal is logical commits, not necessarily the exact groupings above.

---

## Verification Summary Template

After completing all tasks, provide this summary:

```
## N5OS-Ode Release Fix - Validation Summary

### Verification Results
| Check | Status |
|-------|--------|
| No placeholders | ✅/❌ |
| Python compiles | ✅/❌ |
| Context loading | ✅/❌ |
| Init build | ✅/❌ |
| LICENSE exists | ✅/❌ |
| Safety script | ✅/❌ |

### Prompt Validation
- Block prompts: X/Y valid
- Reflection prompts: X/Y valid
- Other prompts: X/Y valid

### Issues Fixed
- [List any issues discovered and fixed]

### Commits Created
1. fix: replace PROJECT_REPO placeholders
2. feat: add init_build.py
3. feat: add missing context files
4. fix: prompt path corrections
5. docs: LICENSE and documentation

### Ready for Push
- [ ] All checks pass
- [ ] All commits clean
- [ ] Ready for `git push origin main`
```

---

## Handoff

When complete:
1. Provide the full Validation Summary
2. Note any issues that couldn't be resolved
3. Confirm ready for git push (or note blockers)
4. This completes the n5os-ode-release-fix project

---

## Files Modified

This worker validates but doesn't create new files (unless fixing issues).

May need to fix:
- Any remaining broken references in prompts
- Any scripts that don't compile
- Any missing files discovered during validation

