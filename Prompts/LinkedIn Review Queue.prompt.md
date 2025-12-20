---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
title: LinkedIn Review Queue
description: Review LinkedIn contacts and decide which to add to CRM
tags: [linkedin, crm, review, kondo]
tool: true
---

# LinkedIn Review Queue

Review LinkedIn contacts from Kondo and decide which ones should get CRM profiles (with Aviato enrichment).

## Usage

When invoked, this prompt will:
1. Show the pending review queue grouped by engagement level
2. Allow you to approve/reject contacts
3. Approved contacts can then be enriched with Aviato data

## Commands

```bash
# Show pending reviews
python3 N5/scripts/linkedin_review_queue.py pending

# Generate digest
python3 N5/scripts/linkedin_review_queue.py digest

# Approve a contact
python3 N5/scripts/linkedin_review_queue.py approve "David Speigel"

# Reject a contact  
python3 N5/scripts/linkedin_review_queue.py reject "Random Recruiter"

# Ignore (hide from queue)
python3 N5/scripts/linkedin_review_queue.py ignore "LinkedIn Team"
```

## Instructions for Zo

When V asks to review the LinkedIn queue:

1. Run `python3 N5/scripts/linkedin_review_queue.py scan` first to catch any new contacts
2. Run `python3 N5/scripts/linkedin_review_queue.py digest` to generate the review
3. Present the digest to V, grouped by engagement level
4. Wait for V's decisions (approve/reject/ignore)
5. Execute the appropriate commands
6. For approved contacts, offer to run Aviato enrichment and create CRM profiles

