---
created: 2025-11-11
last_edited: 2025-11-11
version: 1.0
---

# Telemetry Analysis Framework

**Purpose:** Systematic analysis of test results to validate SESSION_STATE system and guide final refinements.

## Analysis Protocol

### Step 1: Aggregate Results

```python
# Collect from V's report:
total_tests = 5
passed_tests = X  # Count of conversations with 100% checks passed
overall_success_rate = (passed_tests / total_tests) * 100

# By conversation type:
build_success = [pass/fail]
research_success = [pass/fail]
discussion_success = [pass/fail]
planning_success = [pass/fail]
edge_success = [pass/fail]
```

### Step 2: Identify Failure Patterns

**If failures occur, categorize by:**

| Failure Type | Diagnostic | Root Cause | Fix |
|--------------|------------|------------|-----|
| **workspace_not_exists** | Workspace dir missing | Rule didn't trigger initialization | Add pre-check or scheduled agent |
| **state_file_missing** | No SESSION_STATE.md | Script didn't run or failed | Check script execution path |
| **wrong_classification** | Type != expected | Auto-classification logic weak | Improve keyword matching |
| **db_not_synced** | DB record missing/wrong | Sync failed or didn't trigger | Check auto-sync integration |
| **missing_sections** | Template incomplete | Template generation issue | Fix template in script |

### Step 3: Calculate Confidence Metrics

```
Reliability Score = (passed_tests / total_tests) * 100
  - Target: ≥80% (4/5 pass)
  - Acceptable: ≥60% (3/5 pass)  
  - Unacceptable: <60% (needs redesign)

Classification Accuracy = correct_types / total_tests * 100
  - Target: ≥80%
  - Note: Edge case (Test 5) allowed to be ambiguous

DB Sync Rate = conversations_in_db / total_tests * 100
  - Target: 100%
  - Indicates: Auto-sync reliability
```

### Step 4: Decision Matrix

| Success Rate | Classification | DB Sync | Decision |
|--------------|----------------|---------|----------|
| ≥80% | ≥80% | 100% | ✅ **SHIP IT** - System validated |
| ≥80% | <80% | 100% | ⚠️ **REFINEMENT NEEDED** - Fix classification |
| ≥80% | ≥80% | <100% | ⚠️ **REFINEMENT NEEDED** - Fix DB sync |
| 60-79% | Any | Any | 🔧 **ITERATION REQUIRED** - Address failures |
| <60% | Any | Any | 🚫 **REDESIGN** - Fundamental issue |

### Step 5: Extract Insights

**Questions to answer:**

1. **Was SESSION_STATE missing?**
   - If yes → Rule didn't trigger (LLM attention issue)
   - Solution: Strengthen P0 marker or add scheduled agent

2. **Was classification wrong?**
   - If yes → Which types confused?
   - Solution: Add more keywords or use different classification approach

3. **Was DB sync incomplete?**
   - If yes → Silent failure or integration bug?
   - Solution: Add logging, strengthen error handling

4. **Were templates incomplete?**
   - If yes → Script template generation issue
   - Solution: Fix template in session_state_manager.py

5. **Did edge case (Test 5) work?**
   - Ambiguous prompt should still initialize (any type is OK)
   - If failed to init → Critical rule firing issue

### Step 6: Generate Action Plan

**Based on results, create prioritized fixes:**

```markdown
## Post-Test Action Plan

### Critical (Must Fix Before Ship):
- [ ] [Issue 1 from failures]
- [ ] [Issue 2 from failures]

### Important (Fix This Week):
- [ ] [Issue 3 from warnings]
- [ ] [Issue 4 from patterns]

### Nice-to-Have (Future):
- [ ] [Enhancement 1]
- [ ] [Enhancement 2]

### Validated (No Action):
- [x] [What worked well]
- [x] [What worked well]
```

## Telemetry Queries to Run

After V reports results, run these to gather additional context:

```bash
# Check all test conversations in DB
sqlite3 /home/workspace/N5/data/conversations.db \
  "SELECT id, type, status, created_at FROM conversations 
   WHERE id LIKE 'con_%' 
   ORDER BY created_at DESC LIMIT 10;"

# Check for failed syncs (STATE exists but DB doesn't)
python3 /home/workspace/N5/scripts/conversation_sync.py audit

# Review telemetry files
ls -lh /home/workspace/N5/tests/telemetry/

# Aggregate telemetry stats
python3 /home/workspace/N5/scripts/analyze_telemetry.py
```

## Success Declaration Criteria

**To declare system "production-ready":**

✅ **Reliability:** ≥80% of fresh conversations initialize correctly  
✅ **Classification:** ≥80% accuracy in type detection  
✅ **DB Sync:** 100% of initialized conversations sync to DB  
✅ **No Critical Bugs:** Zero show-stopper errors  
✅ **Documentation:** Complete usage guide  
✅ **Tests:** 100% test coverage maintained  

**If all criteria met → SHIP IT**
**If any criteria failed → ITERATE → RE-TEST**

## Expected Timeline

- **Test execution:** 30-60 minutes (5 conversations)
- **Results reporting:** 5 minutes
- **Analysis + action plan:** 30 minutes  
- **Fixes (if needed):** 1-3 hours
- **Re-test (if needed):** 30 minutes

**Total:** 2-6 hours to full validation

