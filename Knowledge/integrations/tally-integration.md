# Tally Integration - System Knowledge

**Type:** Integration Knowledge (SSOT)  
**Created:** 2025-10-26  
**Status:** Active  
**Location:** Knowledge/integrations/

---

## Purpose

Canonical reference for Tally.so survey platform integration within N5 OS.

---

## Overview

Tally.so is a FREE survey platform integrated into N5, enabling programmatic survey creation and management through conversation.

**Key Capability:** Describe survey in natural language → deployed automatically

---

## System Components

### 1. Core Script
**Location:** `file 'N5/scripts/tally_manager.py'`  
**Purpose:** Python API client and CLI tool  
**Capabilities:**
- Create forms from structured data
- List all forms
- Get form details
- Retrieve submissions
- Delete forms
- User account info

### 2. Configuration
**API Key:** `N5/config/tally_api_key.env` (git-ignored, secured)  
**Base URL:** https://api.tally.so  
**Rate Limit:** 100 requests/minute

### 3. Commands
**Registered in:** `file 'N5/config/commands.jsonl'`

Commands:
- `tally-list` - List all forms
- `tally-create` - Create new form
- `tally-get` - Get form details  
- `tally-submissions` - Retrieve responses
- `tally-user` - Account information

### 4. Recipe
**Location:** `file 'Recipes/Create Tally Survey.md'`  
**Invocation:** Type `/Create Tally Survey` in chat

### 5. Data Storage
**Location:** `Records/Surveys/`  
**Structure:**
- `incoming/` - Survey specifications
- `drafts/` - Unpublished survey metadata
- `published/` - Active survey metadata
- `responses/` - Downloaded response data
- `exports/` - Analysis and reports

---

## Account Details

**Name:** Vrijen Attawar  
**Email:** vrijen@mycareerspan.com  
**Plan:** FREE (unlimited forms & submissions)  
**Organization:** nrKXB2  
**Timezone:** America/New_York

**Existing Surveys:**
1. Future of Careertech Cartel Interest Form (`wdeWZD`) - 8 submissions
2. NYC Builder Outing (`3x8yoy`) - 14 submissions

---

## FREE Plan Capabilities

### ✅ Unlimited
- Forms
- Submissions per form
- Questions per form
- API access
- Advanced features
- Integrations

### ⚠️ Limitations
- Tally branding on forms (Pro: $29/mo removes)
- Analytics: 7-day window (Pro: unlimited)
- No team workspaces (Business plan)

### Features Included
All advanced features FREE:
- Conditional logic
- Multi-page forms
- File uploads
- Electronic signatures
- Payment collection
- Webhooks
- Email notifications
- Custom domains
- Password protection
- Embed anywhere

---

## Supported Field Types

**Text Inputs:**
- Single-line text
- Email (validated)
- Number
- Phone
- URL
- Date/Time
- Multi-line textarea

**Selection:**
- Multiple choice (radio)
- Checkboxes
- Dropdown
- Multi-select
- Rating stars
- Linear scale
- Ranking

**Advanced:**
- File upload
- Signature
- Matrix questions
- Hidden fields
- Calculations
- Payment integration

---

## Usage Patterns

### Pattern 1: Natural Language (Primary)
```
User: "Create customer feedback with name, email, rating 1-5, comments"
Zo: [Parses requirements → Generates API payload → Creates form]
    Returns: Form ID, URLs, metadata
```

### Pattern 2: Slash Command
```
User: Types "/" in chat
      Selects "Create Tally Survey"
Zo: Guides through requirements
```

### Pattern 3: Direct CLI
```bash
python3 N5/scripts/tally_manager.py create \
  --title "Survey Title" \
  --quick
```

---

## Data Flow

```
1. Requirements → Records/Surveys/incoming/
2. API Creation → Form ID, URLs
3. Metadata → Records/Surveys/drafts/ OR published/
4. Collect Responses → Tally servers
5. Download → Records/Surveys/responses/
6. Analyze → Records/Surveys/exports/
7. Insights → Knowledge/ (promotion)
```

---

## Integration Points

### With N5 Lists
Track active surveys in `Lists/surveys.jsonl`:
```json
{
  "form_id": "wdeWZD",
  "title": "Careertech Interest",
  "status": "active",
  "purpose": "collect_leads",
  "created": "2025-07-24",
  "last_checked": "2025-10-26"
}
```

### With Knowledge
Promote insights to:
- `Knowledge/customer/` - Customer intelligence
- `Knowledge/insights/` - Survey-derived insights
- `Knowledge/trends/` - Patterns over time

### With Webhooks (Future)
Real-time submission notifications:
1. Configure webhook in Tally
2. Point to N5 endpoint
3. Auto-process submissions
4. Update CRM/Knowledge

---

## API Reference

**Base URL:** `https://api.tally.so`  
**Authentication:** Bearer token in Authorization header  
**Documentation:** https://developers.tally.so

**Key Endpoints:**
- `GET /forms` - List forms
- `POST /forms` - Create form
- `GET /forms/{id}` - Get form details
- `PATCH /forms/{id}` - Update form
- `DELETE /forms/{id}` - Delete form
- `GET /forms/{id}/submissions` - Get responses
- `GET /users/me` - Account info

---

## Security

- ✅ API key stored in `N5/config/tally_api_key.env`
- ✅ File git-ignored (verified in `.gitignore`)
- ✅ No hardcoded credentials
- ✅ Key tied to user account (inherits permissions)
- ⚠️ Response data may contain PII (keep in Records/, don't commit)

---

## Troubleshooting

### API Key Issues
```bash
# Test API key
python3 N5/scripts/tally_manager.py user

# Expected: Account info
# Error: "Unauthorized" → Key invalid/expired
```

### Rate Limits
- Limit: 100 requests/minute
- Solution: Use webhooks instead of polling
- Tracking: Script logs rate limit errors

### Form Creation Failures
Common issues:
1. Invalid block structure → Check FormBuilder methods
2. Missing required fields → Verify payload
3. Workspace permissions → Check account access

---

## Documentation Map

**Primary Guides:**
- `file 'Documents/tally-system-overview.md'` - Quick reference
- `file 'Documents/tally-survey-system-guide.md'` - Usage guide
- `file 'Documents/tally-api-integration-guide.md'` - API technical reference

**Knowledge:**
- `file 'Knowledge/integrations/tally-integration.md'` - This file (SSOT)
- `file 'Knowledge/tally-free-plan-capabilities.md'` - Plan features

**Data:**
- `file 'Records/Surveys/README.md'` - Data storage structure

**Commands:**
- `file 'N5/commands/tally-create.md'`
- `file 'N5/commands/tally-list.md'`
- `file 'N5/commands/tally-submissions.md'`

**Recipe:**
- `file 'Recipes/Create Tally Survey.md'`

---

## Future Enhancements

**Planned:**
1. Webhook integration for real-time processing
2. Automated response analysis
3. Survey template library
4. Batch operations (create multiple forms)
5. Integration with CRM (`crm-find` cross-reference)
6. Submission export automation
7. Trend analysis over time

**Possible:**
- A/B testing framework
- Response quality scoring
- Auto-follow-ups based on responses
- Integration with email digest
- Survey effectiveness metrics

---

## Maintenance

**Regular Tasks:**
- Check submission counts (weekly)
- Download responses (monthly)
- Archive old surveys (quarterly)
- Review API key validity (quarterly)

**Monitoring:**
- Active forms count
- Response rate trends
- API usage vs. rate limits

---

## Version History

**v1.0 - 2025-10-26**
- Initial integration
- Full CRUD operations
- 5 registered commands
- Recipe created
- Documentation complete

---

## Related Systems

- **CRM:** Survey responses can feed into CRM records
- **Email Digest:** Survey metrics in daily/weekly digests
- **Lists:** Track survey lifecycle in Lists/surveys.jsonl
- **Knowledge:** Promote insights to Knowledge/customer/

---

**Status:** ✅ Fully Operational  
**Maintainer:** N5 OS  
**Last Verified:** 2025-10-26  
**Next Review:** 2025-11-26
