---
description: 'Command: tally-list'
tags: []
tool: true
---
# tally-list

**Category:** tally  
**Workflow:** automation  
**Script:** `/home/workspace/N5/scripts/tally_manager.py`

---

## Description

List all Tally forms with metadata including submissions count, status, and URLs.

---

## Usage

### Command Line
```bash
python3 /home/workspace/N5/scripts/tally_manager.py list
```

### In Conversation

> "Show me my Tally forms"

> "List all my surveys"

---

## Output

For each form:
- Status icon (✅ published, 📝 draft)
- Form name
- Form ID
- Status
- Number of submissions
- Creation date
- Public URL

---

## Example Output

```
📋 Found 2 form(s):

✅ Future of Careertech Cartel Interest Form
   ID: wdeWZD
   Status: PUBLISHED
   Submissions: 8
   Created: 2025-07-24T06:51:43.000Z
   URL: https://tally.so/r/wdeWZD

✅ NYC Builder Outing
   ID: 3x8yoy
   Status: PUBLISHED
   Submissions: 14
   Created: 2025-07-17T15:43:09.000Z
   URL: https://tally.so/r/3x8yoy
```

---

## Related Commands

- `tally-create` - Create new form
- `tally-get` - Get detailed form info
- `tally-submissions` - View responses

---

**Added:** 2025-10-26
