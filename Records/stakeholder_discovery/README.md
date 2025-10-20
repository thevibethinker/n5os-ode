Records/stakeholder_discovery — discovery records storage

Format: one JSON file per discovered stakeholder or per source message.

Example file name: 2025-10-16T173951_message-<message-id>.json

Example content:
```
{
  "discovered_at": "2025-10-16T17:39:51-04:00",
  "source": "email_scanner",
  "source_message_id": "<gmail message ID>",
  "source_subject": "Email subject line",
  "stakeholder": {
    "name": "Full Name",
    "email": "email@domain.com",
    "organization": "Company Name",
    "title": "Job Title",
    "context": "Meeting purpose and relationship",
    "is_decision_maker": true
  }
}
```

This directory was created by the scheduled task run on 2025-10-16T17:39:51 ET.