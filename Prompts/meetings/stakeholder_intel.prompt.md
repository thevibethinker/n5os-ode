---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
title: Stakeholder Intelligence Viewer
description: |
  Run the consolidated stakeholder intelligence view for a person or meeting.
  Uses the canonical script N5/scripts/stakeholder_intel.py to join CRM, Kondo/LinkedIn,
  and Aviato enrichment for one person (--person-id) or all people linked to a meeting (--meeting-id).
  This prompt is read-only: it never modifies CRM or meeting files.
tags:
  - stakeholders
  - meetings
  - intelligence
  - crm
  - linkedin
  - aviato
tool: true
---

# Usage

1. **By person**
   - Provide a CRM person slug, e.g. `lauren-salitan`.
   - I will run:
     - `python3 N5/scripts/stakeholder_intel.py --person-id <slug>`
   - I will paste the resulting report into the conversation.

2. **By meeting**
   - Provide a meeting ID (as stored in `**Meeting IDs:**` metadata in the CRM individual files),
     or paste the CRM line that contains it.
   - I will run:
     - `python3 N5/scripts/stakeholder_intel.py --meeting-id <meeting_id>`
   - I will paste the consolidated intel for all stakeholders linked to that meeting.

# Assistant behavior

- Always prefer calling `python3 N5/scripts/stakeholder_intel.py` over re-deriving stakeholder intel manually.
- Never modify CRM files or Kondo/LinkedIn/Aviato data from this prompt; this is **view-only**.
- When invoked from the context of a specific meeting, first ask for either:
  - the meeting ID, or
  - the relevant CRM slug(s),
  then run the script accordingly.
- If no CRM matches are found for a meeting ID, report that explicitly rather than guessing.

