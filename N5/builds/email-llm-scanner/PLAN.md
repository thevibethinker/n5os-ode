---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_plan
status: draft
---

# Plan: LLM-Powered Email Deal Scanner

**Objective:** Replace regex/exact-match email scanning with semantic LLM analysis that finds deal signals even when names, emails, or companies aren't exact matches.

**Trigger:** Email backfill agent failed to find obvious deal signals (e.g., emails with Vir) because it relied on Python scripts generating exact Gmail queries rather than LLM-powered semantic analysis.

**Key Design Principle:** The LLM is the brain, not the script. Scripts handle mechanics (fetching, batching, storage). The LLM handles semantics (understanding, matching, extraction).

---

## Open Questions

- [x] Should we pull ALL emails or filter first? → Hybrid: broad pull with smart filters (exclude newsletters, notifications)
- [x] How do we handle contacts with no email address in DB? → Search by name + company, update DB with discovered emails
- [ ] What's the batch size limit before LLM context becomes unwieldy? → Test with 20-50 emails per batch
- [ ] Should backfill be incremental or one-shot? → Incremental (agent runs 2x, 30 days each)

---

## Core Framework Design

### The Problem with Current Approach

```
Current (Broken):
┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ Python script│────▶│ Exact Gmail │────▶│ Regex match  │
│ generates    │     │ queries     │     │ (misses most)│
│ queries      │     │ "Vir" = 0   │     └──────────────┘
└──────────────┘     └─────────────┘
```

**Failures:**
1. Contact "Vir" has no email in DB → can't search `from:vir@instalily.ai`
2. Exact name match `"Vir"` returns noise (unrelated emails mentioning "virtual")
3. No semantic understanding → can't recognize "hey V, Vir here" as Vir Bhatt
4. Script advances backfill even when nothing meaningful was found

### The Fixed Approach

```
Fixed (LLM-Powered):
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Broad Gmail  │────▶│ Pre-filter  │────▶│ LLM Semantic │────▶│ Route via    │
│ pull (recent │     │ (exclude    │     │ Analysis     │     │ DealSignal-  │
│ 30-60 days)  │     │ newsletters)│     │ per email    │     │ Router       │
└──────────────┘     └─────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │ Enrichment:  │
                                         │ Update contact│
                                         │ emails in DB │
                                         └──────────────┘
```

---

## LLM Analysis Framework

### Phase 1: Email Retrieval (Mechanical)

**Gmail Query Strategy:**
Instead of N specific queries, use 2-3 broad queries:

```
# Query 1: All non-promotional emails in date range
-category:promotions -category:social -category:updates after:YYYY/MM/DD before:YYYY/MM/DD

# Query 2: Specific deal-related terms (catch explicit mentions)
(deal OR partnership OR acquire OR acquisition OR meeting) after:YYYY/MM/DD
```

**Pre-filter rules (Python):**
- Exclude domains: `linkedin.com`, `notify.`, `noreply@`, `no-reply@`
- Exclude subjects: "Your weekly digest", "Unsubscribe", "Reset password"
- Keep max 100 emails per 30-day window

### Phase 2: LLM Semantic Analysis (The Brain)

**For EACH email, the LLM answers:**

```markdown
## Email Analysis Prompt

You are analyzing an email for deal intelligence for V's CRM.

### Email:
From: {sender}
Subject: {subject}
Date: {date}
Snippet: {snippet}

### Known Contacts & Deals:
{deal_contacts_summary}

### Questions to answer:

1. **Person Match**: Does this email involve any known contact?
   - Check: sender name, sender email, mentions in snippet
   - Consider: first names, nicknames, company associations
   - Output: matched_contact_id or null

2. **Deal Match**: Does this relate to any tracked deal?
   - Check: company mentions, deal context
   - Output: matched_deal_id or null

3. **Email Discovery**: If we matched a contact, extract their email address for DB enrichment
   - Output: discovered_email or null

4. **Signal Strength**: Is this deal-relevant?
   - "none" = promotional, automated, irrelevant
   - "weak" = tangentially related (newsletter mentioning company)
   - "medium" = person communication, not deal-specific
   - "strong" = explicit deal discussion, meeting, next steps
   - Output: signal_strength

5. **Intelligence Extract** (if signal >= medium):
   - stage_signal: none | positive | negative | stage_change
   - key_facts: [list of notable information]
   - next_action: implied or explicit
   - Output: intel_json or null

Return JSON:
{
  "matched_contact_id": "...",
  "matched_deal_id": "...",
  "discovered_email": "...",
  "signal_strength": "...",
  "intel": {...} or null,
  "skip_reason": "..." (if signal_strength = none)
}
```

### Phase 3: Routing & Storage (Mechanical)

For each email with signal_strength >= medium:
1. If `discovered_email` → Update contact record in deals.db
2. If `matched_deal_id` → Route through DealSignalRouter
3. Log to `processed_emails` table with extraction summary

---

## Checklist

### Phase 1: Update email_deal_scanner.py
- ☐ Replace `get_search_queries()` with broad Gmail pull function
- ☐ Add pre-filter logic to exclude noise
- ☐ Add function to format deal/contact context for LLM
- ☐ Test: Verify broad pull returns 50-100 emails for 30-day window

### Phase 2: Add LLM analysis prompt
- ☐ Add `EMAIL_ANALYSIS_PROMPT` to deal_llm_prompts.py
- ☐ Add `analyze_email_batch()` function that calls LLM
- ☐ Handle LLM response parsing with fallback
- ☐ Test: Run on 5 sample emails, verify matching works

### Phase 3: Integration & enrichment
- ☐ Add `update_contact_email()` function for discovered emails
- ☐ Wire analysis results into DealSignalRouter
- ☐ Update backfill agent instruction to use new flow
- ☐ Test: Full backfill run finds Vir emails correctly

---

## Phase 1: Update email_deal_scanner.py

### Affected Files
- `N5/scripts/email_deal_scanner.py` - UPDATE - Replace query generation with broad pull + pre-filter

### Changes

**1.1 Add broad Gmail query function:**

Replace `get_search_queries()` logic. Instead of generating N specific queries, generate 1-2 broad queries:

```python
def get_broad_email_queries(days: int, offset: int = 0) -> List[str]:
    """Generate broad Gmail queries for semantic analysis."""
    end_date = datetime.now() - timedelta(days=offset)
    start_date = end_date - timedelta(days=days)
    
    date_filter = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"
    
    return [
        f"-category:promotions -category:social -category:updates {date_filter}",
    ]
```

**1.2 Add pre-filter function:**

```python
EXCLUDE_DOMAINS = [
    'linkedin.com', 'facebookmail.com', 'notify.', 'noreply@', 
    'no-reply@', 'mailer-daemon', 'postmaster@'
]

EXCLUDE_SUBJECT_PATTERNS = [
    r'weekly digest', r'unsubscribe', r'reset password', 
    r'verify your email', r'your .* receipt'
]

def should_analyze_email(email: dict) -> bool:
    """Pre-filter to exclude obvious noise."""
    sender = email.get('from', '').lower()
    subject = email.get('subject', '').lower()
    
    for domain in EXCLUDE_DOMAINS:
        if domain in sender:
            return False
    
    for pattern in EXCLUDE_SUBJECT_PATTERNS:
        if re.search(pattern, subject, re.IGNORECASE):
            return False
    
    return True
```

**1.3 Add context builder for LLM:**

```python
def build_llm_context() -> str:
    """Build deal/contact context string for LLM prompt."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get contacts
    c.execute("""
        SELECT id, full_name, email, company, pipeline 
        FROM deal_contacts 
        WHERE full_name IS NOT NULL
        LIMIT 50
    """)
    contacts = [dict(r) for r in c.fetchall()]
    
    # Get deals
    c.execute("""
        SELECT id, company, primary_contact, pipeline, stage 
        FROM deals 
        WHERE company IS NOT NULL
        LIMIT 30
    """)
    deals = [dict(r) for r in c.fetchall()]
    
    context = "## Known Contacts:\n"
    for c in contacts:
        email_str = f" <{c['email']}>" if c.get('email') else ""
        company_str = f" ({c['company']})" if c.get('company') else ""
        context += f"- {c['full_name']}{email_str}{company_str} [id: {c['id']}]\n"
    
    context += "\n## Active Deals:\n"
    for d in deals:
        context += f"- {d['company']} ({d['pipeline']}/{d['stage']}) [id: {d['id']}]\n"
    
    return context
```

### Unit Tests
- Run `get_broad_email_queries(30, 0)` → Should return 1 query string
- Run `should_analyze_email({'from': 'no-reply@linkedin.com'})` → Should return False
- Run `should_analyze_email({'from': 'vir@instalily.ai'})` → Should return True

---

## Phase 2: Add LLM Analysis Prompt

### Affected Files
- `N5/scripts/deal_llm_prompts.py` - UPDATE - Add EMAIL_ANALYSIS_PROMPT
- `N5/scripts/email_deal_scanner.py` - UPDATE - Add analyze function

### Changes

**2.1 Add prompt to deal_llm_prompts.py:**

```python
EMAIL_ANALYSIS_PROMPT = """You are analyzing an email for deal intelligence.

## Email:
From: {sender}
Subject: {subject}  
Date: {date}
Body Preview: {snippet}

## Known Contacts & Deals:
{context}

## Analysis Task:

1. **Person Match**: Does this email involve any known contact?
   - Check sender name, email, and body for mentions
   - Consider first names, nicknames, company associations
   - Example: "vir@instalily.ai" matches contact "Vir" even if email not in DB

2. **Deal Match**: Does this relate to any tracked deal?
   - Check for company mentions, deal context

3. **Email Discovery**: If matched a contact, what's their email address?
   - Extract from the "From" field

4. **Signal Strength**:
   - "none" = promotional, automated, irrelevant
   - "weak" = tangentially related  
   - "medium" = person communication, not deal-specific
   - "strong" = explicit deal discussion, meeting setup, next steps

5. **Intelligence** (if signal >= medium):
   - What stage signal does this indicate?
   - What are the key facts?
   - What's the implied next action?

Return ONLY valid JSON:
{{
  "matched_contact_id": "contact-id or null",
  "matched_deal_id": "deal-id or null", 
  "discovered_email": "email@domain.com or null",
  "signal_strength": "none|weak|medium|strong",
  "intel": {{
    "stage_signal": "none|positive|negative|stage_change",
    "key_facts": ["fact1", "fact2"],
    "next_action": "action or null"
  }} or null,
  "skip_reason": "why skipped, if signal_strength=none"
}}"""
```

**2.2 Add analysis function to email_deal_scanner.py:**

The actual LLM call happens agentic-ally (Zo calls the LLM). The script just formats the prompt:

```python
def format_email_for_analysis(email: dict, context: str) -> str:
    """Format email + context into analysis prompt."""
    from deal_llm_prompts import EMAIL_ANALYSIS_PROMPT
    
    return EMAIL_ANALYSIS_PROMPT.format(
        sender=email.get('from', 'Unknown'),
        subject=email.get('subject', 'No subject'),
        date=email.get('date', 'Unknown'),
        snippet=email.get('snippet', ''),
        context=context
    )
```

### Unit Tests
- Format a sample email → Prompt should be valid, include context
- Parse sample LLM response → Should extract all fields

---

## Phase 3: Integration & Enrichment

### Affected Files
- `N5/scripts/email_deal_scanner.py` - UPDATE - Add email enrichment
- Agent instruction - UPDATE - New execution flow

### Changes

**3.1 Add contact email enrichment:**

```python
def update_contact_email(contact_id: str, email: str, dry_run: bool = False) -> bool:
    """Update a contact's email if currently empty."""
    if dry_run:
        print(f"[DRY RUN] Would update {contact_id} with email: {email}")
        return True
        
    conn = get_db_connection()
    c = conn.cursor()
    
    # Only update if email is currently empty
    c.execute("""
        UPDATE deal_contacts 
        SET email = ?, updated_at = ?
        WHERE id = ? AND (email IS NULL OR email = '')
    """, (email, _now_iso(), contact_id))
    
    conn.commit()
    return c.rowcount > 0
```

**3.2 Updated agent execution flow:**

```markdown
## New Agent Instruction Flow

1. Get broad emails:
   - Call Gmail with: `-category:promotions -category:social after:YYYY/MM/DD`
   - Limit to 100 emails

2. Pre-filter (Python):
   - Exclude automated/noise emails
   - Result: ~50-80 relevant emails

3. Build context once:
   - Get all contacts + deals from DB
   - Format into context string

4. For each email (LLM analysis):
   - Format email + context into prompt
   - LLM returns: match info, signal strength, intel
   - If discovered_email → update contact DB
   - If signal >= medium → route through DealSignalRouter

5. Summarize:
   - Emails analyzed: X
   - Signals found: Y
   - Contacts enriched: Z
```

### Unit Tests
- Full flow on 10 emails → Should find matches, enrich contacts
- Verify Vir's email gets discovered and stored

---

## Success Criteria

1. Running backfill finds emails from Vir (vir@instalily.ai) and matches to contact
2. Contact "Vir" in DB gets email field populated automatically
3. Deal signals are extracted semantically, not by exact regex
4. No more "0 emails found" for contacts who definitely emailed

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM costs for analyzing many emails | Pre-filter aggressively; batch analysis |
| False positive matches | Require signal_strength >= medium before acting |
| Context too long for LLM | Limit to 50 contacts, 30 deals |
| Backfill takes too long | Keep 30-day windows, 2 runs max |

---

## Alternatives Considered

### Alternative A: Enhanced regex matching
- More fuzzy matching in Python (Levenshtein distance, etc.)
- **Rejected**: Still can't handle "Vir Bhatt" → "vir@instalily.ai" without semantic understanding

### Alternative B: Embedding-based search
- Embed all contacts, embed email content, vector similarity
- **Rejected**: Overkill for this use case; LLM semantic analysis is simpler and sufficient

### Alternative C: Pre-index all Gmail
- Sync entire mailbox to local DB, then query locally
- **Rejected**: Privacy concerns, storage overhead, sync complexity

**Selected Approach**: Hybrid (broad Gmail pull + LLM semantic analysis) is simplest and directly addresses the failure mode.

---

## Level Upper Review

Not yet invoked. Will invoke before finalizing if V approves direction.

## Worker Briefs

| Wave | Worker | Title | Brief File | Status |
|------|--------|-------|------------|--------|
| 1 | W1.1 | Broad Query + Pre-filter | `workers/W1.1-broad-query-prefilter.md` | pending |
| 1 | W1.2 | LLM Analysis Prompt | `workers/W1.2-llm-prompt.md` | pending |
| 2 | W2.1 | Integration & Agent Flow | `workers/W2.1-integration.md` | pending |

**Wave 1** (parallel): W1.1 and W1.2 can run simultaneously — they touch different files.
**Wave 2** (sequential): W2.1 depends on both W1.1 and W1.2 completing first.
