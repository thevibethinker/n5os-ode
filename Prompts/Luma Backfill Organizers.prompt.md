---
title: Luma Backfill Organizers
description: Manually backfill organizer tally from Past events (requires user interaction)
tags: [luma, backfill, organizers]
tool: true
---

# Luma Organizer Backfill (Manual)

Since Luma's Past events tab requires JavaScript interaction, this prompt guides manual backfill.

<system>
## Current Status
```bash
cat /home/workspace/N5/data/luma_organizer_tally.json
```

## Manual Backfill Process

### Option A: User Provides Screenshot
1. Ask user to:
   - Go to https://lu.ma/home in Zo's Browser
   - Click the "Past" tab
   - Take a screenshot or share the page

2. Parse the organizer names from past events
3. Update the tally file

### Option B: Incremental Build
The tally will grow automatically as:
- New events are scraped and attended
- `luma_feedback_check.py` runs after events pass
- User confirms attendance

### Update Tally Command
```python
import json
tally_path = "/home/workspace/N5/data/luma_organizer_tally.json"
with open(tally_path) as f:
    tally = json.load(f)

# Add/increment organizer
organizer = "New Organizer Name"
tally[organizer] = tally.get(organizer, 0) + 1

with open(tally_path, 'w') as f:
    json.dump(tally, f, indent=2)
```

## Why This Matters
- Organizers with higher tally scores get +0.5 points per attended event
- Priority organizers (manually set) get +5.0 bonus
- This builds trust over time
</system>

