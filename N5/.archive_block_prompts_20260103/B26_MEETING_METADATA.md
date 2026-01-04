---
created: 2025-11-15
last_edited: 2025-11-15
version: 1
block_code: B26
block_name: MEETING_METADATA
category: core
---
# B26: Meeting Metadata Summary

## Objective

Extract and structure essential meeting metadata in a consistent, machine-readable format for indexing, search, and cross-referencing.

## Output Format

Structured metadata fields in markdown with YAML-like formatting for easy parsing.

## Output Structure

```yaml
date: YYYY-MM-DD
time: HH:MM (ET/PT/etc with timezone)
duration: "X minutes/hours"
participants:
  - Full Name (Role/Company if relevant)
  - Full Name
type: [one-on-one | team sync | client call | investor pitch | technical deep-dive | strategy session | etc]
title: "Descriptive Meeting Title"
topics:
  - topic1
  - topic2
  - topic3
gdrive_id: "Google Drive file ID" # From meeting_pipeline.db
gcal_event_id: "Google Calendar event ID or null" # Fetched via script
series: "Series name if part of recurring series, else null"
related_meetings:
  - meeting_id or folder reference if mentioned
```

## Special Fields

**gdrive_id:** Pull from meeting_pipeline.db (already tracked during ingestion)

**gcal_event_id:** Fetch via script that:
1. Searches Google Calendar for events matching date/time range
2. Matches participant emails
3. Returns event ID if confident match found
4. Returns null if no calendar event exists

**Note:** Script requirement: `N5/scripts/fetch_gcal_event_id.py`

**Note:** Calendar event ID lookup requires querying Google Calendar API based on meeting date/time and participants. Some meetings (ad-hoc, transcript-only) may not have associated calendar events.

## Quality Criteria

**Good B26 includes:**
- Complete participant list with correct spellings
- Accurate meeting type classification
- Meaningful title that captures meeting purpose
- Key topics as searchable tags
- Context about meeting series/relationship

**Avoid:**
- Generic titles ("Meeting with X")
- Incomplete participant lists
- Incorrect date/time information
- Missing critical metadata fields

## Instructions

Extract the following metadata:

1. **Date & Time** - When meeting occurred
2. **Duration** - How long (if determinable)
3. **Participants** - Full list with roles when known
4. **Meeting Type** - Category/classification
5. **Title** - Descriptive, specific title
6. **Topic Tags** - 3-7 key themes/topics
7. **Series Info** - If part of recurring series
8. **Related Meetings** - References to past/future meetings mentioned

## Edge Cases

**If participant names unclear:**
- Use best available information
- Mark uncertain names with [?]

**If meeting type ambiguous:**
- Choose most specific applicable category
- Use "General Discussion" as fallback

**If no clear title emerges:**
- Construct from: "[Primary Topic] Discussion with [Key Participant]"

## Example Output

```markdown
## B26_MEETING_METADATA

**Date:** November 15, 2025  
**Time:** 2:00 PM EST  
**Duration:** 47 minutes  

### Participants
- Vrijen Attawar (Careerspan, Founder)
- Rory Brown (Strategic Advisor)
- Nicole Holubar (Emory University, Career Services)

### Meeting Classification
**Type:** Partnership Strategy Discussion  
**Category:** Business Development  
**Stage:** Pre-Contract Negotiation  

### Title
Emory-Careerspan Partnership: Hiring-Based Monetization Model

### Topic Tags
- `partnership-strategy`
- `pricing-model`
- `higher-education`
- `career-services`
- `revenue-sharing`
- `implementation-planning`

### Series Information
**Series:** Emory Partnership Development  
**Frequency:** Ad-hoc  
**Previous Meetings:** 
- 2025-10-28: Initial exploratory conversation
- 2025-11-01: Technical capabilities review

**Next Steps:** Board presentation scheduled for Nov 22

### Context Notes
- This is the third meeting in ongoing partnership discussions
- Nicole preparing proposal for Emory leadership
- Timeline: Aiming for Spring 2026 pilot launch
- Key decision point: Pricing structure approval needed
```

## Validation

Before finalizing, check:
- [ ] All participants listed with correct names
- [ ] Date/time accurate
- [ ] Meeting type appropriately specific
- [ ] Title is descriptive and searchable
- [ ] 3-7 meaningful topic tags included
- [ ] Series context captured if applicable
- [ ] Related meetings referenced when mentioned

## Quality Checklist

Before finalizing, check:
- [ ] GDrive ID included if meeting source is Drive
- [ ] Calendar event ID populated if meeting was scheduled (use lookup tool)
- [ ] Calendar ID explicitly set to null if no calendar event exists
- [ ] All participant names spell correctly



