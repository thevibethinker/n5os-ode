# Tally Survey Creation System - Usage Guide

**Created:** 2025-10-26  
**System:** N5 / Zo Conversation  
**Plan:** Tally FREE (unlimited forms & submissions)

---

## Overview

You can now create and manage Tally surveys programmatically through conversation or command-line.

**Capabilities:**
- ✅ Create surveys from natural language descriptions
- ✅ List all existing forms  
- ✅ View form submissions
- ✅ Get form details
- ✅ All operations within FREE plan limits

---

## Quick Start

### In Conversation

Just describe what you need:

> "Create a feedback survey with name, email, rating 1-5, and comments"

> "Show me all my Tally forms"

> "Get submissions from my NYC Builder Outing form"

### Command Line

```bash
# List forms
python3 /home/workspace/N5/scripts/tally_manager.py list

# Create quick contact form
python3 /home/workspace/N5/scripts/tally_manager.py create \
  --title "Contact Form" \
  --description "Get in touch" \
  --quick

# Get form submissions
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id wdeWZD

# View user info
python3 /home/workspace/N5/scripts/tally_manager.py user
```

---

## Conversation Examples

### Create a Survey

**You:** "Create a workshop registration form with:
- Attendee name (required)
- Email (required)
- Company name
- Dietary preferences (multiple choice: None, Vegetarian, Vegan, Gluten-free)
- Special requests (optional textarea)"

**Zo:** [Creates form via API and provides URL]

### List Forms

**You:** "Show me all my Tally forms"

**Zo:** [Lists forms with IDs, status, submission counts, URLs]

### Get Submissions

**You:** "Get the submissions from form wdeWZD"

**Zo:** [Retrieves and displays submission data]

---

## Command Reference

### `tally_manager.py list`
List all your forms with metadata

**Output:**
- Form name
- Form ID
- Status (PUBLISHED/DRAFT)
- Number of submissions
- Public URL
- Creation date

### `tally_manager.py create`
Create a new form

**Required:**
- `--title "Form Title"` - Main form title

**Optional:**
- `--description "Description text"` - Form description
- `--draft` - Create as draft (default: published)
- `--quick` - Add default fields (Name, Email, Comments)
- `--workspace ID` - Assign to specific workspace

**Example:**
```bash
python3 /home/workspace/N5/scripts/tally_manager.py create \
  --title "Customer Feedback" \
  --description "We value your input" \
  --quick
```

### `tally_manager.py get`
Get detailed form information

**Required:**
- `--form-id FORM_ID` - The form's ID

**Optional:**
- `--json` - Output full JSON response

**Example:**
```bash
python3 /home/workspace/N5/scripts/tally_manager.py get \
  --form-id me1Lyq \
  --json
```

### `tally_manager.py submissions`
List form submissions

**Required:**
- `--form-id FORM_ID` - The form's ID

**Optional:**
- `--page N` - Page number (default: 1)
- `--filter TYPE` - Filter: all, completed, partial (default: all)
- `--verbose` or `-v` - Show response details

**Example:**
```bash
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id wdeWZD \
  --verbose
```

### `tally_manager.py user`
Get your Tally account information

---

## Available Field Types

When describing surveys, you can request:

**Text Inputs:**
- Text (single line)
- Email (with validation)
- Number
- Phone number
- URL
- Date
- Time
- Textarea (multi-line)

**Selection:**
- Multiple choice (radio buttons)
- Checkboxes
- Dropdown
- Multi-select
- Rating (stars/emoji)
- Linear scale (1-5, 1-10, etc.)
- Ranking

**Advanced:**
- File upload
- Signature
- Payment fields
- Matrix questions
- Hidden fields
- Calculations

---

## FREE Plan Limits

**What's Unlimited:**
- ✅ Forms
- ✅ Submissions/responses
- ✅ Questions per form
- ✅ Most advanced features
- ✅ API access
- ✅ Webhooks

**What's Limited:**
- ⚠️ Form analytics (last 7 days only)
- ⚠️ Tally branding on forms
- ⚠️ No team workspaces
- ⚠️ 100 API requests per minute

**Fair Use Policy:**
Essentially: don't abuse the system, don't spam, don't resell. Normal usage is completely fine.

---

## Typical Workflows

### Workflow 1: Event Registration
1. **Describe form** → "Create event registration with name, email, ticket type"
2. **Zo creates** → Returns form URL
3. **Share URL** → Distribute to attendees
4. **View submissions** → "Show me registrations for form [ID]"
5. **Export if needed** → Can integrate with Google Sheets, Notion, etc.

### Workflow 2: Customer Feedback
1. **Quick create** → "Create feedback form with quick defaults"
2. **Customize in UI** → Open edit URL to add branding
3. **Embed on site** → Get embed code from Tally
4. **Monitor** → Check submissions periodically

### Workflow 3: Survey Campaign
1. **Batch create** → Create multiple survey variants
2. **A/B test** → Different versions for different audiences
3. **Aggregate data** → Pull all submissions via API
4. **Analyze** → Process in spreadsheet or Python

---

## Files & Configuration

**API Key:** `/home/workspace/N5/config/tally_api_key.env`
- Contains your Tally API key
- DO NOT commit to git
- Already configured

**Script:** `/home/workspace/N5/scripts/tally_manager.py`
- Main CLI tool
- Can be called directly or through Zo

**Documentation:**
- `file 'Documents/tally-api-integration-guide.md'` - Complete API reference
- `file 'Knowledge/tally-free-plan-capabilities.md'` - Plan limits and features

---

## Troubleshooting

### "Unauthorized" Error
- API key may be invalid or expired
- Check `file 'N5/config/tally_api_key.env'`
- Regenerate key at https://tally.so/settings/api-keys

### "Rate Limited" (429)
- Hit 100 requests/minute limit
- Wait 60 seconds
- Consider using webhooks instead of polling

### Form Creation Failed
- Check field types are valid
- Ensure required parameters present
- Review error message for specifics

### Can't See Form
- Check if created as DRAFT
- May need to publish via UI or recreate without `--draft` flag

---

## Next Steps

### Recommended Enhancements

1. **Webhook Integration**
   - Set up webhook endpoint to receive submissions in real-time
   - Avoid polling API repeatedly

2. **Template Library**
   - Create reusable form templates
   - Store as JSON configurations

3. **Submission Processing**
   - Automated email responses
   - Integration with Notion/Airtable
   - Data analysis workflows

4. **Custom Form Builder**
   - More sophisticated programmatic creation
   - Form generation from spreadsheets
   - Bulk form operations

---

## Support

**Tally Resources:**
- Documentation: https://developers.tally.so
- Help Center: https://tally.so/help
- Support: https://tally.so/support

**Your Forms:**
- Dashboard: https://tally.so/forms
- API Keys: https://tally.so/settings/api-keys

**N5 Documentation:**
- `file 'Documents/tally-api-integration-guide.md'`
- `file 'Knowledge/tally-free-plan-capabilities.md'`

---

## Example: Creating Custom Survey

```bash
# 1. Create base form
python3 /home/workspace/N5/scripts/tally_manager.py create \
  --title "Product Feedback Survey" \
  --description "Help us improve our product"

# 2. Get form ID from output
# Example output: ID: abc123

# 3. Open in browser to customize
# https://tally.so/forms/abc123/edit

# 4. Add your specific fields in UI
# (or extend script for more field types)

# 5. Publish and share
# Public URL: https://tally.so/r/abc123

# 6. Monitor submissions
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id abc123 \
  --verbose
```

---

**System Status:** ✅ Fully operational  
**Test Form Created:** `me1Lyq` (Draft)  
**Existing Forms:** 2 (Future of Careertech Cartel, NYC Builder Outing)

*2025-10-26 20:22 ET*
