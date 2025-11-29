---
title: CRM Gmail Enrichment
description: Enrich CRM profile using Gmail thread analysis - extracts relationship intelligence from email history
tags: [crm, gmail, enrichment, intelligence]
tool: true
---

# CRM Gmail Enrichment

Analyze Gmail threads with a contact to extract relationship intelligence for CRM profile enrichment.

## Input

You will receive a contact email address as the first argument after the prompt mention.

Example usage:
```
@crm-gmail-enrichment bogomil@sequoiacap.com
```

## Task

1. **Search Gmail** for threads with this contact:
   - Use `use_app_gmail` with tool `gmail-find-email`
   - Query: `from:{email} OR to:{email}`
   - Max results: 20

2. **Extract Thread Content**:
   - For each unique thread ID found (max 20)
   - Use `use_app_gmail` with tool `gmail-list-thread-messages`
   - Collect thread metadata and messages

3. **Analyze Relationship Intelligence**:
   Extract the following from thread content:
   - **Communication Pattern**: Total threads, date range, last exchange, frequency
   - **Relationship Context**: What is the nature of the relationship? What do they discuss?
   - **Recent Topics**: Key themes from thread subjects and content
   - **Notable Mentions**: Introductions, projects, mutual connections, opportunities
   - **Follow-up Items**: Open loops or action items

4. **Format Output**:
   Return ONLY the markdown intelligence block in this exact format:

```markdown
**Gmail Thread Intelligence:**

**Communication Pattern:**
- Total threads: {count}
- Date range: {first_date} to {last_date}
- Last exchange: {most_recent_date}
- Frequency: [weekly/monthly/occasional/single]

**Relationship Context:**
{2-3 sentence summary of relationship and discussion topics}

**Recent Topics:**
- {Topic from thread subject/content}
- {Topic from thread subject/content}
- {Topic from thread subject/content}

**Notable Mentions:**
- {Significant items: intros, projects, shared connections}

**Follow-up Items:**
- {Open loops or action items if any}
```

## Quality Standards

- Be **specific**: Quote actual subject lines and dates from threads
- Be **honest**: Don't hallucinate - only report what's in the actual threads
- Be **concise**: Focus on CRM-relevant intelligence
- Be **protective**: Don't expose personal/private details irrelevant to professional relationships

## Edge Cases

**No threads found:**
```markdown
**Gmail Thread Intelligence:**

No Gmail history found with {email}.
```

**Gmail API error:**
```markdown
**Gmail Thread Intelligence:**

Error retrieving Gmail data: {error_message}
```

**Rate limited:**
```markdown
**Gmail Thread Intelligence:**

Gmail API rate limit exceeded. Enrichment will be retried automatically.
```

## Example Output

```markdown
**Gmail Thread Intelligence:**

**Communication Pattern:**
- Total threads: 4
- Date range: 2025-10-15 to 2025-11-12
- Last exchange: 2025-11-12
- Frequency: occasional

**Relationship Context:**
Bogomil reached out initially to explore partnership opportunities between Sequoia and Careerspan. The conversation has been professional and exploratory, focused on understanding product-market fit and potential investment interest.

**Recent Topics:**
- Partnership exploration / potential investment
- Product demo scheduling  
- Market positioning for AI career tools

**Notable Mentions:**
- Mentioned introduction to Sarah Chen at Sequoia Capital
- Discussed upcoming demo scheduled for next week
- Expressed interest in GTM strategy for enterprise

**Follow-up Items:**
- Demo scheduled for 2025-11-20
- Follow up with deck sent on 2025-11-10
```

## Execution

Execute this enrichment now for the provided contact email.

