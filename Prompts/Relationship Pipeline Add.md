---
description: 'Command: relationship-pipeline-add'
tool: true
tags:
- networking
- relationships
- introductions
- people
---
# Add to Relationship Pipeline

Track people you want to develop relationships with or get introduced to in the future.

## Quick Add

```bash
python3 /home/workspace/N5/scripts/n5_lists_add.py relationship-pipeline \
  "Person Name - Title/Company" \
  --body "## Overview
**Name:** Full Name
**Current Role:** Title, Company
**Location:** City, State/Country
**LinkedIn:** URL
**X/Twitter:** Handle (if relevant)

## Company
- Brief company description
- Why they're notable

## Background
- Key career highlights
- Relevant experience

## Why Connect
- Why you want to connect
- Potential synergies
- Mutual interests

## Notes
- Any additional context" \
  --tags "tag1" "tag2" "tag3"
```

## Essential Fields to Capture

**Basic Info:**
- Full name
- Current title & company
- Location
- LinkedIn URL
- Other social handles (Twitter/X, etc.)

**Company Context:**
- Company founded/joined date
- Company mission/focus
- Team size
- Funding info (if relevant)
- Notable details

**Professional Background:**
- Current role & responsibilities
- Previous notable positions
- Career trajectory
- Key skills/expertise

**Education:**
- Degrees & institutions
- Relevant certifications
- Notable programs

**Achievements:**
- Awards & recognition
- Major accomplishments
- Published work
- Speaking engagements

**Why Connect:**
- Specific reasons for wanting connection
- Potential synergies with your work
- Shared interests/networks
- Introduction paths

**Tags to Use:**
- Industry/sector (e.g., "climate-tech", "edtech", "fintech")
- Role type (e.g., "founder", "investor", "executive")
- Location (e.g., "san-francisco", "new-york", "remote")
- Characteristics (e.g., "community-builder", "technical", "sales")
- Status markers (e.g., "forbes-30-under-30", "yc-alumni")

## View the List

```bash
cat /home/workspace/N5/lists/relationship-pipeline.md
```

## Search for People

```bash
# By tag
grep -A 20 "climate-tech" /home/workspace/N5/lists/relationship-pipeline.md

# By location
grep -A 20 "san-francisco" /home/workspace/N5/lists/relationship-pipeline.md

# By company
grep -A 20 "Company:" /home/workspace/N5/lists/relationship-pipeline.md
```

## Update Status

When you've connected with someone or no longer need to track them:

```bash
# Mark as done (connected)
# Or delete the entry if no longer relevant
```

## Tips

1. **Be specific about why** - Always include clear reasons for wanting to connect
2. **Track introduction paths** - Note mutual connections or warm intro opportunities
3. **Update regularly** - Add notes as you learn more about them
4. **Tag strategically** - Use tags that make searching easy
5. **Include context** - Why now? What's the trigger for wanting to connect?
6. **Note timing** - If there's a specific event or milestone to wait for
