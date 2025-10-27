# Root Clearinghouse Quick Start

**Goal:** Automated root cleanup with AI-powered file routing

---

## 5-Minute Setup

### 1. Test the System (Dry Run)

```bash
# See what would be moved from root
python3 N5/scripts/root_cleanup.py --dry-run

# See how files would be analyzed
python3 N5/scripts/inbox_analyzer.py --dry-run

# See what review would be generated
python3 N5/scripts/inbox_review_generator.py --dry-run
```

### 2. Run Your First Cleanup

```bash
# Move root items to Inbox (for real)
python3 N5/scripts/root_cleanup.py
```

**What happened:**
- Unprotected items moved to `Inbox/` with timestamps
- All moves logged to `N5/logs/.cleanup_log.jsonl`
- Root now contains only protected directories

### 3. Process the Inbox

```bash
# Analyze files
python3 N5/scripts/inbox_analyzer.py

# Route high-confidence files (≥85%)
python3 N5/scripts/inbox_router.py

# Generate review document
python3 N5/scripts/inbox_review_generator.py
```

### 4. Review & Decide

Open `Inbox/REVIEW.md` and:
- Check auto-routed files (already moved)
- Review suggested routings (60-84% confidence)
- Classify manual items (<60% confidence)
- Move files as needed

---

## Daily Workflow (Automated)

**11pm ET:** Root cleanup runs automatically
- Moves new root items to Inbox/
- You wake up to clean workspace root

## Weekly Workflow (5-10 min)

**Sunday 8pm ET:** Inbox processing runs automatically
- Analyzes all Inbox files
- Routes high-confidence items
- Generates REVIEW.md

**Monday morning:** You review REVIEW.md
- Handle suggested routings (middle confidence)
- Classify manual items (low confidence)
- Everything else already done!

---

## Key Files

**Config:**
- `N5/config/root_cleanup_config.json` - What to move
- `N5/config/routing_config.json` - Where to route

**Logs:**
- `N5/logs/.cleanup_log.jsonl` - All root moves
- `N5/logs/.inbox_analysis.jsonl` - All analyses

**Review:**
- `Inbox/REVIEW.md` - Human review document (auto-generated)

**Docs:**
- `Inbox/POLICY.md` - Full Inbox policy
- `Documents/System/Root-Clearinghouse-System.md` - Complete system docs

---

## Commands

```bash
# Manual cleanup (anytime)
python3 N5/scripts/root_cleanup.py

# Full inbox processing
python3 N5/scripts/inbox_analyzer.py
python3 N5/scripts/inbox_router.py
python3 N5/scripts/inbox_review_generator.py

# Just regenerate review
python3 N5/scripts/inbox_review_generator.py
```

---

## Confidence Levels Explained

**≥85% (Auto-route):**
- System is very confident
- Moves automatically
- Listed in REVIEW.md for transparency

**60-84% (Suggest):**
- System has good guess but not certain
- Flagged in REVIEW.md for your review
- You decide: accept or correct

**<60% (Manual):**
- System can't confidently classify
- Needs your judgment
- You review content and decide

---

## Adjusting Thresholds

Edit `N5/config/routing_config.json`:

```json
"confidence_thresholds": {
  "auto_route": 0.85,  // Lower if too conservative (0.80)
  "suggest": 0.60,      // Raise if too many suggestions (0.70)
  "manual_only": 0.0
}
```

**Too conservative?** (Everything stuck in Inbox)
- Lower `auto_route` to 0.80

**Too aggressive?** (Wrong auto-routing)
- Raise `auto_route` to 0.90

**Start with 0.85** and adjust based on accuracy.

---

## What Gets Moved?

**Protected directories** (NEVER moved):
- Knowledge/, Lists/, Records/
- N5/, Documents/
- Careerspan/, Personal/
- Articles/, Images/
- projects/, Recipes/
- Inbox/, .git

**Everything else** moves to Inbox with timestamp:
- Files in root
- Folders in root
- Downloads, screenshots, etc.

---

## Need Help?

**System not working?**
1. Check `N5/logs/*.jsonl` for errors
2. Run scripts with `--dry-run` to test
3. Review `Documents/System/Root-Clearinghouse-System.md`

**Files going to wrong places?**
1. Review `N5/logs/.inbox_analysis.jsonl`
2. Check `reasoning` field for AI logic
3. Adjust thresholds or update destinations

**Inbox growing too fast?**
1. Check TTL warnings in `REVIEW.md`
2. Lower auto-route threshold
3. Add explicit routing rules

---

## Next Steps

1. ✅ Test with dry-run
2. ✅ Run first cleanup
3. ✅ Process Inbox files
4. ✅ Review REVIEW.md
5. ⏭️ Create scheduled tasks (daily + weekly)
6. ⏭️ Monitor for first week
7. ⏭️ Adjust thresholds based on accuracy

---

**Quick reference:** `file 'Inbox/POLICY.md'`  
**Full docs:** `file 'Documents/System/Root-Clearinghouse-System.md'`

**Created:** 2025-10-27  
**Status:** Ready to use
