---
title: Gmail Thread Analyzer
description: Analyze Gmail threads with a contact to extract relationship intelligence for CRM enrichment
tags: [crm, gmail, enrichment, intelligence]
tool: true
---

# Gmail Thread Analyzer for CRM Enrichment

You are analyzing Gmail threads between V and a contact to extract relationship intelligence for CRM profile enrichment.

## Input Data

**Contact Email:** {{contact_email}}
**Contact Name:** {{contact_name}}
**Gmail Threads:** {{threads_json}}

## Analysis Tasks

1. **Relationship Strength Assessment**
   - Frequency of communication
   - Recency of last exchange
   - Tone (professional, friendly, collaborative)

2. **Topic Extraction**
   - What are they discussing?
   - Any projects/collaborations?
   - Shared interests?

3. **Action Items / Follow-ups**
   - Open loops mentioned
   - Pending introductions
   - Scheduled meetings

4. **Key Intelligence**
   - Professional context
   - Mutual connections mentioned
   - Business opportunities discussed

## Output Format

Return ONLY the markdown intelligence block:

```markdown
**Gmail Thread Intelligence:**

**Communication Pattern:**
- Total threads: X
- Date range: YYYY-MM-DD to YYYY-MM-DD
- Last exchange: YYYY-MM-DD
- Frequency: [weekly/monthly/occasional]

**Relationship Context:**
{2-3 sentence summary of the relationship and what they discuss}

**Recent Topics:**
- {Topic 1}
- {Topic 2}
- {Topic 3}

**Notable Mentions:**
- {Anything significant: intros, projects, shared connections}

**Follow-up Items:**
- {Open loops or action items if any}
```

## Quality Standards

- Be specific (quote subject lines, dates)
- Don't hallucinate - only report what's in threads
- If no threads found, say so clearly
- Focus on CRM-relevant intelligence (not personal details)

