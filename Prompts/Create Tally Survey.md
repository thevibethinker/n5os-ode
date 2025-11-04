---
description: |
tool: true
  Create a Tally.so survey programmatically from natural language description.
  Supports all field types available on FREE plan (unlimited forms & submissions).
tags:
  - tally
  - surveys
  - forms
  - automation
---
# Create Tally Survey

## What This Does

Translates your survey requirements into Tally API calls and creates a functional form immediately.

## Usage

Simply describe the survey you want:

**Examples:**

> "Create a workshop registration form with attendee name, email, company, and dietary preferences"

> "Create a customer feedback survey with rating 1-5, comments, and would-recommend yes/no"

> "Create a simple contact form"

## Field Types Available

**Text Inputs:**
- Text (single line)
- Email
- Number  
- Phone number
- URL
- Date/Time
- Textarea (multi-line)

**Selection:**
- Multiple choice
- Checkboxes
- Dropdown
- Multi-select
- Rating
- Linear scale

**Advanced:**
- File upload
- Signature
- Matrix questions
- Ranking
- Hidden fields
- Calculations

## Output

You'll receive:
- ✅ Form ID
- ✅ Public survey URL
- ✅ Edit URL (to customize in Tally UI)
- ✅ Form status

## What Happens

1. **Parse your description** → Extract fields, types, requirements
2. **Generate API payload** → Create proper Tally block structure
3. **Create form via API** → POST to Tally API
4. **Return URLs** → Form is live and ready to use

## Free Plan Benefits

- Unlimited forms
- Unlimited submissions
- All field types
- Webhooks
- Integrations
- No time limits

Only limitation: Tally branding on forms (removable with Pro plan)

## Notes

- Forms created as PUBLISHED by default (immediately live)
- Add `--draft` flag to create as draft first
- You can refine design/styling in Tally UI after creation
- API key stored securely in N5 config

## Related

- View all forms: "Show me my Tally forms"
- Get submissions: "Get submissions from form [ID]"  
- User info: "What's my Tally account status?"

---

**Script:** `file 'N5/scripts/tally_manager.py'`  
**Docs:** `file 'Documents/tally-survey-system-guide.md'`
