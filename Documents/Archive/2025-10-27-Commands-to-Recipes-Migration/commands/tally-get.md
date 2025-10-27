# tally-get

**Category:** tally  
**Workflow:** automation  
**Script:** `/home/workspace/N5/scripts/tally_manager.py`

---

## Description

Get detailed information about a specific Tally form including structure, settings, and blocks.

---

## Usage

```bash
python3 /home/workspace/N5/scripts/tally_manager.py get --form-id FORM_ID
```

**Required:**
- `--form-id` - The 6-character Tally form ID

---

## Output

Returns complete form details:
- Form ID and title
- Status (DRAFT/PUBLISHED/CLOSED)
- Workspace and organization
- Creation and modification timestamps
- Number of submissions
- All form blocks (questions, text, etc.)
- Form settings and configuration
- Public URL
- Edit URL

---

## Example

```bash
# Get details for specific form
python3 /home/workspace/N5/scripts/tally_manager.py get \
  --form-id wdeWZD
```

**Output:**
```
Form: Future of Careertech Cartel Interest Form
ID: wdeWZD
Status: PUBLISHED
Submissions: 8
Created: 2025-07-24T06:51:43.000Z
URL: https://tally.so/r/wdeWZD

[Detailed JSON structure follows]
```

---

## Use Cases

- Verify form exists
- Check form structure before updates
- Debug form configuration
- Export form definition
- Audit form settings

---

## Notes

- Returns full API response as JSON
- Useful for programmatic form inspection
- Can pipe output to jq for filtering
- Does not include submission data (use tally-submissions)

---

## Related Commands

- `tally-list` - List all forms
- `tally-create` - Create new form
- `tally-submissions` - View responses

---

**Added:** 2025-10-26
