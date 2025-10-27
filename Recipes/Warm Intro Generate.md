---
description: 'Command: warm-intro-generate'
tags: []
---
# warm-intro-generate

Generate warm introductions (blurbs or full emails) using the B07 bi-directional block as the SSOT. Supports double opt-in by generating a first opt-in request email and the connecting email after approval.

## Usage

```bash
N5: warm-intro-generate <meeting_folder> \
  [--format blurb|email] \
  [--intro-number N] \
  [--only-opt-in] \
  [--only-connecting] \
  [--auto-crm] \
  [--dry-run]
```

- `meeting_folder`: Path to the meeting directory (e.g., `N5/records/meetings/2025-10-20_external-bennett-lee`)
- `--format`: `blurb` (default) or `email`
- `--intro-number`: Generate a specific intro only (1-indexed across section)
- `--only-opt-in`: Only generate opt-in request emails (for double opt-in intros)
- `--only-connecting`: Only generate connecting intros (for after opt-in approval)
- `--auto-crm`: Auto-create CRM profiles for people not in database
- `--dry-run`: Preview outputs without writing files

## Outputs

Files are written to: `DELIVERABLES/intros/`

**Naming:**
- Direct intro: `01_logan-curry_to_bennett-lee_blurb.txt` or `_email.txt`
- Double opt-in: `_opt_in_request_email.txt` and `_connecting_blurb.txt`/`_connecting_email.txt`
- Inbound intros: `01_bennett-lee_to_vrijen's-network_*.txt`
- Manifest: `intros_manifest.md`

**Side Effects:**
- If `--auto-crm` flag is used, creates minimal CRM profiles in `Knowledge/crm/individuals/` for people not in database
- Automatically updates `B25_DELIVERABLE_CONTENT_MAP.md` if present

## Double Opt-In Workflow

For intros marked as "Tentative" or containing keywords ("needs to speak", "gauge interest", "confirm"):
1. **Opt-in request** email sent to person being introduced (asks permission)
2. **Connecting intro** generated for after approval

Use `--only-opt-in` to regenerate just opt-in requests.
Use `--only-connecting` to regenerate just connecting intros.

## Examples

```bash
# Generate all intros in blurb format
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee

# Generate emails and auto-create CRM profiles
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee --format email --auto-crm

# Regenerate only opt-in requests
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee --only-opt-in --format email

# Generate specific intro
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee --intro-number 2 --format email

# Preview without writing
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee --dry-run
```

## Notes

- Pulls resonant details from B01/B08/B21 when present
- Uses CRM if profiles exist; otherwise continues and can auto-create with `--auto-crm`
- Subject lines are LLM-generated; bodies follow V's voice calibration
- Blurb format is default (body text only, ready to copy-paste)
- Email format includes subject line + addressed body

