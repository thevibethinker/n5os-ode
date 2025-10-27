# Tally Integration Preferences

**Module:** integration/tally  
**Purpose:** Tally.so survey platform integration preferences

---

## When to Use

Use Tally integration when:
- Creating surveys or forms
- Collecting structured feedback
- Event registration
- Lead collection
- Customer research
- Product feedback
- Satisfaction tracking

---

## Invocation

### Natural Language (Primary)
User describes survey requirements in conversation:
```
"Create a feedback survey with name, email, rating, and comments"
```

### Slash Command
User types `/` and selects "Create Tally Survey"

### Direct Command
Explicit command invocation:
```
"Use tally-create to make a new survey"
```

---

## Data Storage

Follow Records layer pattern:

**Specifications** → `Records/Surveys/incoming/`  
**Drafts** → `Records/Surveys/drafts/`  
**Published** → `Records/Surveys/published/`  
**Responses** → `Records/Surveys/responses/{form-id}/`  
**Analysis** → `Records/Surveys/exports/`

**Tracking** → `Lists/surveys.jsonl`  
**Knowledge** → `Knowledge/integrations/tally-integration.md` (SSOT)

---

## Processing Workflow

1. **Capture Requirements** → Save spec to incoming/
2. **Create Survey** → Via API, get form ID and URLs
3. **Save Metadata** → Draft or published JSON
4. **Track** → Add to Lists/surveys.jsonl
5. **Monitor** → Check submissions periodically
6. **Download** → Responses to responses/{form-id}/
7. **Analyze** → Generate reports in exports/
8. **Promote** → Valuable insights to Knowledge/

---

## Field Type Selection

**For text:** Use INPUT_TEXT (short) or TEXTAREA (long)  
**For email:** Use INPUT_EMAIL (validated)  
**For numbers:** Use INPUT_NUMBER or LINEAR_SCALE (ratings)  
**For selection:** Use MULTIPLE_CHOICE (single) or checkboxes (multi)  
**For dates:** Use INPUT_DATE  
**For files:** Use FILE_UPLOAD  
**For ratings:** Use LINEAR_SCALE or RATING

---

## Best Practices

### Survey Design
- Keep surveys short (<10 questions optimal)
- Use required fields sparingly
- Provide clear labels and placeholders
- Group related questions
- Use conditional logic for complex flows

### Data Management
- Download responses weekly minimum
- Keep metadata files updated
- Track in Lists/surveys.jsonl
- Archive closed surveys after 90 days

### Security
- Never commit API key
- Don't commit response data with PII
- Export files may contain sensitive data (review before sharing)

---

## Plan Limitations

**FREE Plan (Current):**
- ✅ Unlimited forms and submissions
- ✅ All advanced features
- ✅ Full API access
- ⚠️ Tally branding on forms
- ⚠️ 7-day analytics window

**Rate Limits:**
- 100 requests/minute via API
- Use webhooks to avoid polling

---

## Error Handling

**API Failures:**
- Retry with exponential backoff
- Log errors for review
- Fallback to UI creation if needed

**Rate Limits:**
- Implement request throttling
- Use webhook push instead of polling
- Queue batch operations

**Data Loss Prevention:**
- Save metadata immediately after creation
- Track in Lists/surveys.jsonl
- Backup response data locally

---

## Maintenance

**Weekly:**
- Check submission counts
- Update Lists/surveys.jsonl

**Monthly:**
- Download response data
- Generate analysis reports

**Quarterly:**
- Archive closed surveys
- Review API key validity
- Clean up old response data

---

## Integration Points

**With Lists:**
- Track surveys in `Lists/surveys.jsonl`
- Link follow-ups to form IDs

**With Knowledge:**
- Promote insights to `Knowledge/customer/`
- Document patterns in `Knowledge/insights/`

**With CRM (Future):**
- Cross-reference submissions with contacts
- Auto-create CRM records from responses

---

## Command Reference

- `tally-list` - List all forms
- `tally-create` - Create new survey
- `tally-get` - Get form details
- `tally-submissions` - Download responses
- `tally-user` - Account information

**Recipe:** `/Create Tally Survey`

---

## See Also

- `file 'Knowledge/integrations/tally-integration.md'` - System SSOT
- `file 'Records/Surveys/README.md'` - Data storage structure
- `file 'Documents/tally-system-overview.md'` - Quick reference
- `file 'N5/schemas/tally.survey.schema.json'` - Metadata schema

---

**Status:** Active  
**Created:** 2025-10-26  
**Last Updated:** 2025-10-26
