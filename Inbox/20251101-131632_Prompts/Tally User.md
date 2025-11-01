---
description: "Command: tally-user"
tags:
tool: true
---
# tally-user

**Category:** tally  
**Workflow:** automation  
**Script:** `/home/workspace/N5/scripts/tally_manager.py`

---

## Description

Get Tally account information including plan details, organization, and user settings.

---

## Usage

```bash
python3 /home/workspace/N5/scripts/tally_manager.py user
```

No arguments required.

---

## Output

Returns account details:
- Name and email
- User ID
- Organization ID
- Subscription plan (FREE/PRO/BUSINESS)
- Timezone
- Account creation date
- Authentication methods
- Organization ownership status

---

## Example

```bash
python3 /home/workspace/N5/scripts/tally_manager.py user
```

**Output:**
```
👤 Vrijen Attawar (vrijen@mycareerspan.com)
   Plan: FREE
   Organization: nrKXB2
   Timezone: America/New_York
```

---

## Use Cases

- Verify API key is working
- Check current plan and limits
- Confirm account details
- Debug authentication issues
- Document account configuration

---

## Notes

- Quick health check for API connection
- Shows which plan features are available
- Useful for troubleshooting access issues
- No rate limit concerns (single call)

---

## Related Commands

- `tally-list` - List forms on account
- `tally-create` - Create new form
- All tally commands use same account

---

**Added:** 2025-10-26
