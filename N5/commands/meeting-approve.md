# `meeting-approve`

Approve meeting outputs and trigger downstream actions (e.g., send follow-up emails, update CRM).

## Usage

```bash
N5: meeting-approve <meeting_folder>
```

## Parameters

- `meeting_folder`: The name of the meeting directory in `Careerspan/Meetings/`.

## Description

This command is a placeholder for the meeting approval workflow. It reviews all generated intelligence blocks (15-20+ files including core blocks, intelligence blocks in INTELLIGENCE/, and deliverables in DELIVERABLES/) and allows you to approve them for downstream actions like:

- Sending follow-up emails
- Updating CRM with stakeholder information
- Scheduling follow-up meetings
- Publishing deliverables (blurbs, one-pagers, proposals)

The approval process validates that all critical blocks have been generated and reviews quality before triggering automated actions.
