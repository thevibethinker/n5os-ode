# Weekly Summary System - Quick Reference

**Status:** ✅ PRODUCTION (Deployed 2025-10-12)  
**Schedule:** Every Sunday at 8:00 PM ET  
**First Run:** Today (2025-10-12 at 8pm)

---

## What It Does

Generates a comprehensive weekly digest every Sunday evening covering:

1. **📅 Calendar Overview** - External meetings for the upcoming week (Mon-Sun)
   - Filtered to external events only
   - Includes N5OS tags, participants, times
   - Grouped by day

2. **📧 Email Activity** - Last 30 days of email history with meeting participants
   - High-activity contacts ranked by volume
   - Key email threads surfaced
   - Topics and recency tracked

3. **📊 Week Ahead Insights** - Strategic preparation
   - Tag breakdown (LD-COM, LD-NET, etc.)
   - Busiest day identification
   - Notable patterns and themes
   - Preparation recommendations

---

## Quick Access

### Files

**Latest digest:**
```
N5/digests/weekly-summary-2025-10-14.md
```

**All digests:**
```
N5/digests/weekly-summary-*.md
```

**Generation history:**
```
N5/records/weekly_summaries/.state.json
```

**Logs:**
```
N5/logs/weekly_summary.log
```

**Scripts:**
```
N5/scripts/weekly_summary_integration.py (primary)
N5/scripts/email_analyzer.py (helper)
```

### Scheduled Task

**Task ID:** `f2ee8467-4adc-46e9-823e-92aea0e3b278`  
**View/Edit:** https://va.zo.computer/schedule  
**RRULE:** `FREQ=WEEKLY;BYDAY=SU;BYHOUR=20;BYMINUTE=0`

---

## Monitoring

### After Each Run, Check:

1. ✅ **Email inbox** - Did I receive the digest?
2. ✅ **Digest file** - Is it saved at `N5/digests/weekly-summary-{date}.md`?
3. ✅ **State file** - Does it show successful run?
4. ✅ **Logs** - Any errors in `N5/logs/weekly_summary.log`?
5. ✅ **Content quality** - Does the digest look good?

### Success Indicators

- ✅ Email arrives within 2 minutes of 8pm
- ✅ Digest file created with today's date
- ✅ State file updated with new entry
- ✅ No ERROR lines in logs
- ✅ Calendar events are external-only
- ✅ Email activity is relevant
- ✅ Insights are actionable

---

## Common Tasks

### View Last Generation

```bash
cat N5/digests/weekly-summary-$(ls -t N5/digests/weekly-summary-*.md | head -1 | grep -oP '\d{4}-\d{2}-\d{2}').md
```

### Check State

```bash
cat N5/records/weekly_summaries/.state.json | jq '.generation_history[-1]'
```

### View Recent Logs

```bash
tail -50 N5/logs/weekly_summary.log
```

### Manual Trigger (In Zo)

```python
from N5.scripts.weekly_summary_integration import run_weekly_summary

result = run_weekly_summary(
    calendar_tool=use_app_google_calendar,
    gmail_tool=use_app_gmail,
    week_start_date='2025-10-21',  # Monday of target week
    lookback_days=30,
    send_email=True
)
```

---

## Troubleshooting

### Email Not Received

1. Check logs: `tail -100 N5/logs/weekly_summary.log`
2. Check digest file exists: `ls -la N5/digests/weekly-summary-*.md`
3. Check state file: `cat N5/records/weekly_summaries/.state.json`
4. Check scheduled task ran: View https://va.zo.computer/schedule

### Poor Content Quality

1. **Missing events?** - Check external filter logic in script
2. **Wrong participants?** - Verify domain exclusion list
3. **No email activity?** - Check Gmail query and lookback window
4. **Missing tags?** - Verify events have bracketed text in descriptions

### API Failures

1. Check Gmail/Calendar connections in Zo settings
2. Verify API quotas not exceeded
3. Check specific error in logs
4. Try manual run to isolate issue

---

## Configuration

### Change Schedule

1. Go to: https://va.zo.computer/schedule
2. Edit task: `f2ee8467-4adc-46e9-823e-92aea0e3b278`
3. Modify RRULE (e.g., `BYHOUR=19` for 7pm instead of 8pm)

### Adjust Email Lookback

Edit `N5/scripts/weekly_summary_integration.py`:
```python
lookback_days=30  # Change to desired days
```

### Modify External Domains

Edit `N5/scripts/weekly_summary_integration.py`:
```python
INTERNAL_DOMAINS = ['@mycareerspan.com', '@theapply.ai']  # Add/remove domains
```

### Change Digest Location

Edit `N5/scripts/weekly_summary_integration.py`:
```python
DIGESTS_DIR = ROOT / "digests"  # Change to desired path
```

---

## Integration Points

### Google Calendar API

**Tool:** `use_app_google_calendar`  
**Method:** `google_calendar-list-events`  
**Params:** `calendarId`, `timeMin`, `timeMax`, `singleEvents`, `maxResults`

### Gmail API

**Tool:** `use_app_gmail`  
**Method:** `gmail-find-email`  
**Params:** `q`, `maxResults`, `withTextPayload`

### Email Delivery

**Tool:** `send_email_to_user`  
**Params:** `subject`, `markdown_body`

---

## Key Metrics

**Typical Performance:**
- Total time: ~14 seconds
- Calendar API: ~2s (50-100 events)
- Gmail API: ~2s per contact (5-20 contacts)
- Processing: ~2s

**Typical Output:**
- External events: 10-20 per week
- Unique participants: 15-25
- High-activity contacts: 3-8
- Digest length: 200-300 lines

---

## Related Systems

**Daily Meeting Prep:** `file 'N5/digests/daily-meeting-prep-*.md'`
- Scheduled: Daily at 10am ET
- Scope: Today's meetings only
- Includes: Same-day email prep

**Stakeholder Profiles:** `file 'N5/records/stakeholder_profiles/'`
- Manual maintenance
- Detailed relationship tracking
- Future: Auto-update from weekly summaries

**Meeting Transcripts:** `file 'Knowledge/meetings/'`
- Processed from Google Drive
- 10-minute scan interval
- Source for relationship context

---

## Version Info

**Version:** 1.0  
**Last Updated:** 2025-10-12  
**Primary Script:** `weekly_summary_integration.py`  
**Architecture:** Zo-orchestrated (not subprocess-based)  
**Dependencies:** Google Calendar API, Gmail API, Python 3.12

---

## Support

**Documentation:**
- Full deployment log: `file 'N5/logs/DEPLOYMENT-weekly-summary-system-2025-10-12.md'`
- Test results: `file 'N5/logs/threads/con_RC9h1hAcnQcIu9bn-weekly-summary-api-test-production-validation/TESTING_COMPLETE.md'`
- Logical review: `file '/home/.z/workspaces/con_RPvZdUW7dufhEhLe/deployment_review.md'`

**For Issues:**
1. Check logs first: `N5/logs/weekly_summary.log`
2. Review state file: `N5/records/weekly_summaries/.state.json`
3. Consult deployment docs above
4. Ask Zo for help with specific error messages

---

**Quick Status Check:**

```bash
# Is it running?
cat N5/records/weekly_summaries/.state.json | jq -r '.last_generated'

# When is next run?
# Check: https://va.zo.computer/schedule

# Last 5 errors?
grep ERROR N5/logs/weekly_summary.log | tail -5
```

---

*For detailed information, see full deployment documentation*
