# Testing Checklist - Meeting System Migration

**Date:** 2025-11-16 09:39 ET  
**Next Test Window:** Wait for next scheduled run (top of hour)

---

## What to Test

### ✅ Test 1: Finalize Task Adds to Database
**When:** Next time "Finalize Meeting Intelligence and Relocation" runs (hourly)

**Expected Behavior:**
1. Task finds a `_[P]` folder in Inbox
2. Validates all blocks complete
3. **Runs add_to_database.py script**
4. Moves folder to `Personal/Meetings/{meeting_id}/`
5. Database now contains entry with `status='complete'`

**How to Verify:**
```bash
sqlite3 /home/workspace/N5/data/meeting_pipeline.db \
  "SELECT meeting_id, status, completed_at FROM meetings ORDER BY completed_at DESC LIMIT 5;"
```

Should see newly finalized meeting with today's timestamp.

### ✅ Test 2: No Duplicates Created
**When:** Firefly webhook receives a meeting that already exists

**Expected Behavior:**
- Webhook creates transcript in Inbox
- Manifest generation runs
- System checks if folder already exists in `Personal/Meetings/`
- If exists: Skips or logs warning

**How to Verify:**
- Monitor `/home/workspace/N5/logs/fireflies_webhook.log`
- Check Inbox for duplicate `_[M]` folders

### ✅ Test 3: Complete Workflow
**Trigger:** When Firefly sends a new meeting

**Expected Flow:**
1. Transcript lands in `Inbox/{raw_meeting}/`
2. "Generate manifest" creates `Inbox/{meeting}_[M]/manifest.json`
3. "Generate blocks" creates intelligence files, marks `_[P]`
4. "Finalize" **adds to database** and moves to `Personal/Meetings/{meeting}/`

**How to Verify:**
```bash
# Check database entry exists
sqlite3 /home/workspace/N5/data/meeting_pipeline.db \
  "SELECT * FROM meetings WHERE meeting_id = '{new_meeting_id}';"

# Check folder moved
ls -la /home/workspace/Personal/Meetings/{new_meeting_id}/
```

---

## Manual Test (Optional)

Test the database script directly:

```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/add_to_database.py \
  "TEST_MEETING_$(date +%s)" \
  --transcript "/tmp/test.md" \
  --type "EXTERNAL" \
  --status "complete" \
  --notes "Manual test"

# Verify
sqlite3 /home/workspace/N5/data/meeting_pipeline.db \
  "SELECT * FROM meetings WHERE meeting_id LIKE 'TEST_MEETING_%';"

# Cleanup
sqlite3 /home/workspace/N5/data/meeting_pipeline.db \
  "DELETE FROM meetings WHERE meeting_id LIKE 'TEST_MEETING_%';"
```

---

## Success Criteria

- ✅ New meetings get added to database automatically
- ✅ Database shows `status='complete'` after finalization
- ✅ No duplicate [M] folders in Inbox for already-processed meetings
- ✅ No JSONL registry references in logs

---

**Ready to test!**

