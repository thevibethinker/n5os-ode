---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# Worker 2: Gmail Integration

**Orchestrator:** con_rMaSw6rzVNkWvsQ4
**Mission:** Replace Gmail enrichment stubs with real `use_app_gmail` tool calls
**Status:** READY TO EXECUTE

## Context

**What Exists:**
- ✅ Gmail connected (attawar.v@gmail.com, vrijen@mycareerspan.com)
- ✅ `use_app_gmail` tool available
- ✅ `gmail-find-email` for thread searching
- ✅ `gmail-list-thread-messages` for content extraction

**What's Needed:**
- ❌ Stub code in `crm_enrichment_worker.py` lines 126-133
- ❌ No real Gmail thread analysis
- ❌ Profiles showing "⚠️ STUB DATA" for Gmail

**Current Stub Code:**
```python
gmail_note = f"""**Gmail Thread Analysis:**

Recent threads with {email}:
- Thread 1: "Project Discussion" (2025-11-15)
- Thread 2: "Introduction Request" (2025-11-10)

⚠️ STUB DATA - use_app_gmail tool not yet integrated
"""
```

## Mission

Build real Gmail enrichment that:
1. Uses `use_app_gmail` to search for threads with contact
2. Analyzes thread content with LLM (via prompt)
3. Synthesizes relationship intelligence
4. Returns formatted markdown for YAML appending

## Deliverables

### 1. Create `/home/workspace/N5/workflows/gmail_thread_analyzer.prompt.md`

**Purpose:** LLM prompt to analyze Gmail threads and extract relationship intelligence

**Frontmatter:**
```yaml
---
title: Gmail Thread Analyzer
description: Analyze Gmail threads with a contact to extract relationship intelligence for CRM enrichment
tags: [crm, gmail, enrichment, intelligence]
tool: true
---
```

**Prompt Content:**
```markdown
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

\`\`\`markdown
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
\`\`\`

## Quality Standards

- Be specific (quote subject lines, dates)
- Don't hallucinate - only report what's in threads
- If no threads found, say so clearly
- Focus on CRM-relevant intelligence (not personal details)
```

### 2. Create `/home/workspace/N5/scripts/enrichment/gmail_enricher.py`

**Function signature:**
```python
async def enrich_via_gmail(email: str, name: Optional[str] = None) -> dict:
    """
    Enrich profile using Gmail thread analysis.
    
    Returns:
        {
            "success": bool,
            "threads_found": int,
            "markdown": str,  # Formatted intelligence block
            "error": str or None
        }
    """
```

**Implementation approach:**
```python
# 1. Search Gmail for threads with this email
# Use: use_app_gmail tool with gmail-find-email
# Query: "from:{email} OR to:{email}"

# 2. Extract thread content
# Use: gmail-list-thread-messages for each thread

# 3. Invoke LLM prompt for analysis
# Load: N5/workflows/gmail_thread_analyzer.prompt.md
# Pass: contact_email, contact_name, threads_json

# 4. Return formatted markdown
```

**Error Handling:**
- No threads found → Return "No Gmail history found"
- Gmail API error → Return error message
- Too many threads (>20) → Sample recent 20

### 3. Update `/home/workspace/N5/scripts/crm_enrichment_worker.py`

**Replace lines 126-133:**
```python
# 2. Gmail enrichment (REAL)
from N5.scripts.enrichment.gmail_enricher import enrich_via_gmail

gmail_result = await enrich_via_gmail(email, profile_name)
if gmail_result['success'] and gmail_result['threads_found'] > 0:
    intelligence_parts.append(gmail_result['markdown'])
elif gmail_result['threads_found'] == 0:
    intelligence_parts.append(f"""**Gmail Thread Intelligence:**
No Gmail history found with {email}.
""")
else:
    intelligence_parts.append(f"""**Gmail Thread Intelligence:**
Error retrieving Gmail data: {gmail_result['error']}
""")
```

### 4. Test on Known Contacts

**Test Subjects:**
```python
test_contacts = [
    ("konrad@aviato.co", "Konrad Kucharski"),  # Recent demo meeting
    ("austin@aviato.co", "Austin"),            # Recent demo meeting  
    ("attawar.v@gmail.com", "V Attawar"),      # Self (edge case)
]
```

**Test command:**
```bash
cd /home/workspace
python3 -c "
import asyncio
from N5.scripts.enrichment.gmail_enricher import enrich_via_gmail

async def test():
    result = await enrich_via_gmail('konrad@aviato.co', 'Konrad')
    print(f'Threads: {result[\"threads_found\"]}')
    print(result['markdown'])

asyncio.run(test())
"
```

## Implementation Strategy

**Tool-First (P25):**
- Gmail search → `use_app_gmail` tool
- Thread analysis → LLM prompt (not script logic)
- Synthesis → Semantic understanding

**Division of Labor:**
- Script = Mechanics (API calls, data fetching)
- LLM = Semantics (thread analysis, intelligence extraction)

**Key Decision:**
Should enricher invoke the prompt directly or return raw threads for worker to process?

**Recommendation:** Enricher should invoke prompt internally
- Keeps enrichment logic encapsulated
- Worker just calls `enrich_via_gmail()` and gets markdown back
- Cleaner separation of concerns

## Validation Criteria

**Before handoff to Worker 4:**
- [ ] `gmail_thread_analyzer.prompt.md` created
- [ ] `gmail_enricher.py` created and working
- [ ] `crm_enrichment_worker.py` updated
- [ ] Tested on 3 known contacts
- [ ] Handles "no threads found" gracefully
- [ ] Handles Gmail API errors
- [ ] LLM synthesis produces quality intelligence
- [ ] No stub data in outputs

**Quality Check:**
Read the generated intelligence blocks - do they:
- Contain real subject lines/dates?
- Accurately reflect relationship context?
- Provide CRM-relevant insights?
- Avoid hallucination?

## Key Resources

**Tools:**
- `use_app_gmail` - Gmail integration
- `gmail-find-email` - Search threads
- `gmail-list-thread-messages` - Extract content

**Files:**
- `file 'N5/scripts/crm_enrichment_worker.py'` - Stub location
- V's Gmail accounts: attawar.v@gmail.com, vrijen@mycareerspan.com

**Prompt Design:**
- Review existing prompts in `N5/workflows/` for format patterns
- Use tool: true in frontmatter
- Design for reusability

## Handoff to Worker 4

**Success Message:**
```
✅ Worker 2 Complete: Gmail Integration

Deliverables:
- gmail_thread_analyzer.prompt.md (enrichment prompt)
- gmail_enricher.py (X lines)
- crm_enrichment_worker.py updated
- Tested on 3 contacts

Results:
- konrad@aviato.co: X threads found, intelligence extracted
- austin@aviato.co: X threads found, intelligence extracted
- attawar.v@gmail.com: [edge case result]

Ready for Worker 4 to execute enrichment queue with real Gmail analysis.
```

---

**Load this file in a new conversation to execute Worker 2.**

**Start Command:**
```
I am Worker 2 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/orchestration/crm-v3-enrichment/WORKER_2_GMAIL.md'

Replace Gmail stub with real tool integration using use_app_gmail and LLM prompts for thread analysis.
```

