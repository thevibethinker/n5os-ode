# Meeting Processing System - Quick Reference

## ✅ Status: ACTIVE

**Runs**: Every 30 minutes  
**Checks**: Google Drive Fireflies/Transcripts  
**Model**: Claude Sonnet 4  
**Mode**: FULL (20+ blocks)  
**Schedule**: https://va.zo.computer/schedule

---

## What Gets Generated

### Every Meeting Gets (7 core):
1. action-items.md
2. decisions.md
3. key-insights.md
4. stakeholder-profile.md
5. follow-up-email.md
6. REVIEW_FIRST.md
7. transcript.txt

### Plus Conditional (9 intelligence):
8. warm-intros.md
9. risks.md
10. opportunities.md
11. user-research.md
12. competitive-intel.md
13. career-insights.md
14. deal-intelligence.md
15. investor-thesis.md
16. partnership-scope.md

### Plus Deliverables (3):
17. blurb
18. one-pager
19. proposal/pricing

### Plus Metadata (1):
20. _metadata.json

**Total: 15-20+ blocks per meeting**

---

## Quick Commands

```bash
# View processing log
cat N5/logs/meeting-processing/processed_transcripts.jsonl | jq .

# Count processed meetings
wc -l N5/logs/meeting-processing/processed_transcripts.jsonl

# Find duplicates
grep 'duplicate_skipped' N5/logs/meeting-processing/processed_transcripts.jsonl

# List recent meetings
ls -lt Careerspan/Meetings/ | head -5

# Verify system
/home/workspace/N5/scripts/verify_meeting_system.sh

# Test duplicate detector
python3 N5/scripts/meeting_duplicate_detector.py "filename.docx"
```

---

## Manual Trigger

Don't want to wait? Just say:
```
Process new meeting transcripts now
```

---

## File Locations

| Item | Path |
|------|------|
| Processing Log | `N5/logs/meeting-processing/processed_transcripts.jsonl` |
| Staging Area | `Documents/Meetings/_staging/` |
| Output Folders | `Careerspan/Meetings/` |
| Duplicate Detector | `N5/scripts/meeting_duplicate_detector.py` |
| System Verifier | `N5/scripts/verify_meeting_system.sh` |

---

## Documentation

📘 `COMPLETE_BLOCK_LIST.md` - All 20+ blocks explained  
📘 `FINAL_SYSTEM_COMPLETE.md` - Full system summary  
📘 `AUTOMATED_MEETING_SYSTEM_COMPLETE.md` - Technical details  
📘 `N5/commands/meeting-auto-process.md` - Command docs

---

## What Was Fixed

### Before:
❌ Only 7 blocks documented

### Now:
✅ 20+ blocks generated  
✅ Duplicate detection  
✅ N5 integration  
✅ All deliverables included

---

## Need Help?

- **View schedule**: https://va.zo.computer/schedule
- **Check docs**: See list above
- **Run verification**: `/home/workspace/N5/scripts/verify_meeting_system.sh`
- **Ask me**: "How many meetings have been processed?" or "Show me the processing log"
