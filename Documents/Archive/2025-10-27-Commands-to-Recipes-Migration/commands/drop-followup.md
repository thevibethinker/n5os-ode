# drop-followup

**Category:** Communication  
**Version:** 1.0.0  
**Created:** 2025-10-13

---

## Purpose

Mark a follow-up email as declined to stop receiving reminders in the unsent-followups-digest.

---

## Usage

```bash
# Drop a follow-up
python3 /home/workspace/N5/scripts/n5_drop_followup.py "Stakeholder Name"

# Drop with reason
python3 /home/workspace/N5/scripts/n5_drop_followup.py "Stakeholder Name" --reason "Already followed up via text"

# Undo (restore follow-up)
python3 /home/workspace/N5/scripts/n5_drop_followup.py "Stakeholder Name" --undo
```

---

## How It Works

1. **Finds meeting** by stakeholder name (fuzzy match)
2. **Updates metadata** with `followup_status: declined`
3. **Records reason** (optional) in `followup_declined_reason`
4. **Timestamps** the action in `followup_declined_at`
5. **Excludes** from future digests

---

## Examples

```bash
# Drop follow-up for Hamoon
drop-followup "Hamoon Ekhtiari"

# Drop with reason
drop-followup "Hamoon" --reason "decided not to pursue partnership"

# Restore follow-up
drop-followup "Hamoon" --undo
```

---

## Fuzzy Matching

- Matches partial names: `"Hamoon"` finds `"Hamoon Ekhtiari"`
- Case-insensitive
- Only searches meetings with:
  - External classification
  - Generated follow-up emails
  - Valid stakeholder_primary field

---

## Metadata Updates

### On Drop
```json
{
  "followup_status": "declined",
  "followup_declined_at": "2025-10-13T19:30:00-04:00",
  "followup_declined_reason": "Already followed up via text"
}
```

### On Undo
```json
{
  "followup_status": "pending",
  "followup_status_updated_at": "2025-10-13T19:35:00-04:00",
  "followup_declined_reason": null
}
```

---

## Error Handling

- **No match found:** Error if no meeting matches stakeholder name
- **Multiple matches:** Lists all matches and prompts for more specific name
- **Metadata missing:** Error if `_metadata.json` not found

---

## Related Commands

- `unsent-followups-digest` — View all unsent follow-ups
- `follow-up-email-generator` — Generate new follow-up emails

---

**Status:** Active  
**Maintainer:** N5 System
