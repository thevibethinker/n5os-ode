---
description: 'Command: tally-create'
tags: []
---
# tally-create

**Category:** tally  
**Workflow:** automation  
**Script:** `/home/workspace/N5/scripts/tally_manager.py`

---

## Description

Create a new Tally survey programmatically from specifications.

---

## Usage

### Command Line
```bash
python3 /home/workspace/N5/scripts/tally_manager.py create \
  --title "Survey Title" \
  --description "Optional description" \
  [--draft] \
  [--quick] \
  [--workspace WORKSPACE_ID]
```

### In Conversation

Just describe the survey you want naturally:

> "Create a customer feedback form with name, email, rating 1-5, and comments"

> "Create a workshop registration form"

---

## Parameters

**Required:**
- `--title` - Form title

**Optional:**
- `--description` - Form description/subtitle
- `--draft` - Create as draft (default: published)
- `--quick` - Add default contact fields (Name, Email, Comments)
- `--workspace` - Workspace ID to assign form to

---

## Output

Returns:
- Form ID
- Form name
- Status (DRAFT/PUBLISHED)
- Public URL (https://tally.so/r/FORM_ID)
- Edit URL (https://tally.so/forms/FORM_ID/edit)

---

## Examples

### Basic Form
```bash
python3 /home/workspace/N5/scripts/tally_manager.py create \
  --title "Contact Us"
```

### Quick Contact Form
```bash
python3 /home/workspace/N5/scripts/tally_manager.py create \
  --title "Get In Touch" \
  --description "We'd love to hear from you" \
  --quick
```

### Draft Form
```bash
python3 /home/workspace/N5/scripts/tally_manager.py create \
  --title "Survey Draft" \
  --draft
```

---

## Notes

- FREE plan: Unlimited forms and submissions
- Forms default to PUBLISHED (live immediately)
- Use `--draft` to review in UI before publishing
- All forms editable in Tally UI after creation
- API creates functional structure; polish design in UI if needed

---

## Related Commands

- `tally-list` - List all forms
- `tally-get` - Get form details
- `tally-submissions` - View responses

---

**Added:** 2025-10-26
