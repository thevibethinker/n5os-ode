# Email Factual Corrections Review
**Date:** 2025-10-27  
**Report Generated:** 2025-10-27 08:07:40 ET

## Summary

| Metric | Count |
|--------|-------|
| Emails Reviewed | 0 |
| Corrections Found | 0 |
| Auto-Apply Ready | 0 |
| Requires Manual Review | 0 |
| Critical Issues | 0 |

## Status

**Current State:** No emails marked 'sent' in N5/registry/email_registry.jsonl for past 24 hours.

### Email Registry Status
- **Registry File:** N5/registry/email_registry.jsonl
- **Status:** Empty (0 entries)
- **Generated Emails File:** N5/registry/generated_emails.jsonl (1 entry, status: 'generated', not sent)

### Sent Emails from Past 24 Hours
**Total Found:** 0

No emails with 'sent' status found in the registry for the past 24 hours.

## Corrections by Category

| Category | Count | Auto-Apply | Requires Review |
|----------|-------|-----------|-----------------|
| Stakeholder | 0 | 0 | 0 |
| Business Terms | 0 | 0 | 0 |
| Content Library | 0 | 0 | 0 |
| Links | 0 | 0 | 0 |
| Tone | 0 | 0 | 0 |
| **TOTAL** | **0** | **0** | **0** |

## Priority Items Flagged

No corrections requiring manual review at this time.

## System Configuration Notes

### Email Corrections System Setup
The email corrections extraction system (N5/scripts/email_corrections.py) is configured and ready to process:

1. **Relationship Depth:** Detects changes indicating closer/distant relationships
2. **Business Terms:** Identifies pricing model, product terminology changes
3. **Links:** Tracks link additions/removals in communications
4. **Content Library:** Detects deprecated/updated snippets
5. **Tone:** Measures sentence length and formality adjustments

### System Operation

**Extraction Flow:**
```
1. Email Registry Check → Identify emails marked 'sent'
2. Extract Draft vs Sent → Run email_corrections.py extract
3. Classify Corrections → Categorize by type
4. Flag Priority Items → Identify critical business changes
5. Generate Summary → Compile into report
```

### Next Steps

To populate this report with actual corrections:

1. **Generate/Send Emails:** Use the email generation system to create and send stakeholder emails
2. **Update Registry:** Mark emails as 'sent' in N5/registry/email_registry.jsonl with timestamp
3. **Run Extraction:** Execute for each sent email:
   ```bash
   python3 N5/scripts/email_corrections.py extract \
     --draft <path> --sent <path> \
     --meeting-id <id> --stakeholder <name> \
     --output <corrections.json>
   ```
4. **Review Corrections:** Manual review of all non-auto-apply corrections

### Data Files Referenced

- **Email Registry:** N5/registry/email_registry.jsonl
- **Generated Emails:** N5/registry/generated_emails.jsonl
- **Extraction Script:** N5/scripts/email_corrections.py
- **Content Library:** N5/prefs/communication/content-library.json

---

**Report Location:** N5/logs/corrections_review_2025-10-27.md  
**Generated At:** 2025-10-27 08:07:40 ET
