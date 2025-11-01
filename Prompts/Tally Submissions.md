---
description: 'Command: tally-submissions'
tags: []
---
# tally-submissions

**Category:** tally  
**Workflow:** automation  
**Script:** `/home/workspace/N5/scripts/tally_manager.py`

---

## Description

List form submissions with filtering and pagination options.

---

## Usage

### Command Line
```bash
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id FORM_ID \
  [--page N] \
  [--filter all|completed|partial] \
  [--verbose]
```

### In Conversation

> "Show me submissions from form wdeWZD"

> "Get responses from my NYC Builder Outing form"

---

## Parameters

**Required:**
- `--form-id` - Tally form ID

**Optional:**
- `--page` - Page number (default: 1, 50 per page)
- `--filter` - Filter type: all, completed, partial (default: all)
- `--verbose` or `-v` - Show response details

---

## Output

For each submission:
- Completion status icon (✅ complete, ⏳ partial)
- Submission ID
- Submission timestamp
- Respondent ID
- Response data (if --verbose)

---

## Examples

### List All Submissions
```bash
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id wdeWZD
```

### Show Response Details
```bash
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id wdeWZD \
  --verbose
```

### Filter Completed Only
```bash
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id wdeWZD \
  --filter completed
```

### Pagination
```bash
python3 /home/workspace/N5/scripts/tally_manager.py submissions \
  --form-id wdeWZD \
  --page 2
```

---

## Notes

- FREE plan: Unlimited access to all submissions
- 50 submissions per page
- Use `--verbose` to see actual response data
- Rate limit: 100 requests/minute

---

## Related Commands

- `tally-list` - List all forms
- `tally-get` - Get form details
- `tally-create` - Create new form

---

**Added:** 2025-10-26
