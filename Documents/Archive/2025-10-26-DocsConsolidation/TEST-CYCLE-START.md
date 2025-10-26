# Test Cycle - Quick Start

**Status:** Ready to test  
**Thread Export:** `file 'N5/logs/threads/con_hCMhknce0sdNGU4S/THREAD-EXPORT-PRIORITY-4-BUILD.md'`

---

## For Next Thread: Start Here

### Command to Begin Test

```
Run a test cycle of the meeting monitor system. 

Context: Phase 2B Priority 4 is complete. All infrastructure 
deployed and ready. Need to validate end-to-end before creating 
scheduled task.

Reference full context at: 
file 'N5/logs/threads/con_hCMhknce0sdNGU4S/THREAD-EXPORT-PRIORITY-4-BUILD.md'

Test objectives:
1. Verify Google Calendar API access
2. Verify Gmail API access  
3. Test meeting detection (V-OS tag filtering)
4. Validate state tracking
5. Check logging
6. Confirm error handling

Run one cycle and report results.
```

---

## What Zo Should Do

1. Load thread export for context
2. Import run_meeting_monitor module
3. Call run_single_cycle_with_zo_tools()
4. Use Google Calendar and Gmail API tools
5. Set lookahead_days=7
6. Execute cycle
7. Report results with:
   - Events checked
   - Events with V-OS tags found
   - Profiles created
   - Any errors
   - Log file location
   - State file status

---

## Expected Outcomes

### Likely: No V-OS Tags Yet
- System runs successfully
- Finds 0 events with V-OS tags
- Logs "0 new events processed"
- Updates state file
- **This is success!**

### Possible: V-OS Tags Present
- System runs successfully
- Finds N events with V-OS tags
- Creates N profiles
- Generates digest sections
- **Full validation!**

### If Errors:
- Review error message
- Check API access
- Verify configuration
- Debug and re-run

---

## Files to Check After Test

1. **Log file:** `file 'N5/logs/meeting_monitor.log'`
2. **State file:** `file 'N5/records/meetings/.processed.json'`
3. **Profiles:** `N5/records/meetings/` (if any created)
4. **Health check:** Run `python3 N5/scripts/monitor_health.py`

---

## Next Steps After Test

### If Test Passes ✅
→ Create Zo scheduled task  
→ Wait for first scheduled cycle  
→ Begin 24-hour monitoring

### If Test Fails ⚠️
→ Debug the issue  
→ Fix and re-test  
→ Repeat until passing

---

## Quick Reference

**System Status:** 100% complete (4/4 priorities)  
**Test Status:** Not yet run  
**Deployment:** Successful  
**Blockers:** None

**Ready to test!** 🚀

---

## Lessons Learned (Applied to This Test)

### From Recent System Development

**Lesson 1: Test with production configuration**
- Meeting digest had accuracy issues because testing used Claude, production used gpt-5-mini
- **Applied here:** Test cycle uses actual Zo tools and real Google APIs
- **Validation:** No mock data, no simulation - real end-to-end test

**Lesson 2: Complete before claiming complete**
- Thread export refactoring had 59% section coverage but was marked "complete"
- **Applied here:** Test cycle explicitly validates ALL 6 objectives before declaring success
- **Validation:** Checklist must be 6/6 before moving to scheduled task creation

**Lesson 3: Make assumptions explicit**
- Meeting digest made unfounded inferences that "looked sophisticated"
- **Applied here:** Document expected outcomes (likely: 0 tags, possible: N tags, errors: debug)
- **Validation:** Test report states facts, not assumptions

**Lesson 4: Error handling is not optional**
- Original designs often omit error paths
- **Applied here:** Explicit "If Errors" section with recovery steps
- **Validation:** Logging captures failures for post-mortem

**Lesson 5: State verification matters**
- Systems that write state should verify writes succeeded
- **Applied here:** "Files to Check After Test" section with explicit paths
- **Validation:** Confirm log file, state file, and profiles exist/updated

### From Architectural Principles

**Principle 7: Idempotence and Dry-Run by Default**
- Support dry-run mode for any workflow that writes files
- **Applied:** Test cycle IS the dry-run before scheduled automation
- **Why it matters:** Catches issues before they become recurring problems

**Principle 11: Failure Modes and Recovery**
- On any exception, write incident note and stop before destructive actions
- **Applied:** Clear error handling section, logging required, debug before retry
- **Why it matters:** Failed test doesn't break system or lose data

**Principle 8: Minimal Context, Maximal Clarity**
- Keep prompts self-contained; load only what's needed
- **Applied:** Command provides reference to full context but doesn't require loading all files
- **Why it matters:** Test can run in fresh thread with minimal setup

**Principle 12: Testing in Fresh Threads**
- Run workflows in new thread to guarantee clean context
- **Applied:** This test cycle document IS the fresh thread starting point
- **Why it matters:** Validates system works without hidden dependencies

---

## Architectural Principles Compliance Checklist

**Before running test:**
- [ ] Load only required files (Rule-of-Two: architectural principles + this test doc)
- [ ] Verify Google Calendar and Gmail API tools available
- [ ] Confirm log directory exists: `N5/logs/`
- [ ] Confirm state directory exists: `N5/records/meetings/`

**During test:**
- [ ] System logs all operations (Principle 11: incident logging)
- [ ] System handles errors gracefully (Principle 11: failure modes)
- [ ] State writes are atomic (Principle 5: anti-overwrite)
- [ ] Test is idempotent - can re-run safely (Principle 7)

**After test:**
- [ ] Human-readable output generated first (Principle 1)
- [ ] State file updated (SSOT for processed events)
- [ ] Logs captured for review
- [ ] No files overwritten without versioning (Principle 5)

---

## Test Success Criteria (Explicit)

### Minimum Requirements (Must Pass)
1. ✅ Google Calendar API accessible
2. ✅ Gmail API accessible  
3. ✅ Script executes without crashes
4. ✅ Log file created with timestamp
5. ✅ State file updated
6. ✅ Results reported with facts (not assumptions)

### Full Validation (Ideal)
7. ✅ V-OS tags detected correctly (if present)
8. ✅ Profiles generated (if tags found)
9. ✅ Digest sections created (if applicable)
10. ✅ Error handling tested (if errors occur)

**Pass threshold:** 6/6 minimum requirements  
**Gold standard:** All applicable criteria pass

---

## What NOT To Do (Anti-Patterns)

❌ **Don't assume success** - Check files, verify state, read logs  
❌ **Don't skip error paths** - If test errors, that's valuable information  
❌ **Don't over-infer** - Report what happened, not what you think it means  
❌ **Don't rush to scheduled task** - Test must pass first  
❌ **Don't ignore warnings** - Log warnings are pre-cursors to failures

---

## Debugging Guide (If Test Fails)

### API Access Issues
**Symptom:** "Unable to access Google Calendar API"  
**Check:**
```bash
# Verify app tools available
list_app_tools('google_calendar')
list_app_tools('gmail')
```
**Fix:** Ensure apps connected in Zo settings

### Import Errors
**Symptom:** "Cannot import run_meeting_monitor"  
**Check:**
```bash
python3 -c "from N5.scripts.run_meeting_monitor import run_single_cycle_with_zo_tools"
```
**Fix:** Check Python path, verify file exists

### State File Issues
**Symptom:** "Unable to write state file"  
**Check:**
```bash
ls -la N5/records/meetings/
cat N5/records/meetings/.processed.json
```
**Fix:** Verify directory exists and is writable

### Logging Issues
**Symptom:** "No log file created"  
**Check:**
```bash
ls -la N5/logs/meeting_monitor.log
tail -20 N5/logs/meeting_monitor.log
```
**Fix:** Verify log directory exists

---

## Post-Test Validation Script

```bash
#!/bin/bash
# Run this after test to verify system state

echo "=== Meeting Monitor Test Validation ==="
echo ""

echo "1. Checking log file..."
if [ -f "N5/logs/meeting_monitor.log" ]; then
    echo "   ✓ Log file exists"
    echo "   Last 5 lines:"
    tail -5 N5/logs/meeting_monitor.log | sed 's/^/     /'
else
    echo "   ✗ Log file missing"
fi
echo ""

echo "2. Checking state file..."
if [ -f "N5/records/meetings/.processed.json" ]; then
    echo "   ✓ State file exists"
    echo "   Contents:"
    cat N5/records/meetings/.processed.json | sed 's/^/     /'
else
    echo "   ✗ State file missing"
fi
echo ""

echo "3. Checking for profiles..."
PROFILE_COUNT=$(find N5/records/meetings -name "*.md" -type f | wc -l)
echo "   Found $PROFILE_COUNT profile(s)"
if [ $PROFILE_COUNT -gt 0 ]; then
    echo "   Profiles:"
    find N5/records/meetings -name "*.md" -type f | sed 's/^/     /'
fi
echo ""

echo "4. Health check..."
if [ -f "N5/scripts/monitor_health.py" ]; then
    python3 N5/scripts/monitor_health.py
else
    echo "   ⚠ Health check script not found"
fi

echo ""
echo "=== Validation Complete ==="
```

**Save as:** `N5/scripts/validate_test.sh`  
**Run after test:** `bash N5/scripts/validate_test.sh`
