---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_uvKzM58e214FKyUj (W2.1)
---

# Email Backfill Agent — LLM-Powered Deal Intelligence

**Purpose:** Scan historical emails using semantic analysis to find deal signals and enrich contact data.

## STEP 1: Check if backfill complete
```bash
python3 /home/workspace/N5/scripts/email_deal_scanner.py backfill --check --json
```
If status is "complete", skip to STEP 10 (self-destruct).

## STEP 2: Get current backfill window
From the backfill state, get `current_offset` and `window_size` (default 30 days).

## STEP 3: Execute broad Gmail queries
```bash
python3 /home/workspace/N5/scripts/email_deal_scanner.py --days 30 --offset <current_offset> --json
```
Get the broad query from `get_broad_email_queries(30, current_offset)`.

## STEP 4: Fetch emails via Gmail API
```python
use_app_gmail(
    tool_name="gmail-find-email",
    configured_props={"q": "<broad_query>", "maxResults": 100}
)
```

## STEP 5: Pre-filter emails
For each email, call `should_analyze_email()` logic:
- Skip if sender matches EXCLUDE_SENDER_PATTERNS (linkedin, noreply, notifications, etc.)
- Skip if subject matches EXCLUDE_SUBJECT_PATTERNS (digest, unsubscribe, receipt, etc.)
- Track: `emails_fetched`, `emails_skipped`, `emails_to_analyze`

## STEP 6: Build context once
```python
context = build_llm_context()  # 50 contacts + 30 deals
```
Save this context for all email analyses.

## STEP 7: Analyze each email (YOU are the LLM)
For each email that passed pre-filter:

**You (Zo) analyze the email semantically using the EMAIL_ANALYSIS_PROMPT logic:**

Given the email (from, subject, date, snippet) and the context (contacts/deals list):
1. **Person Match**: Does sender match a known contact? Check names, emails, companies.
2. **Deal Match**: Does this relate to a tracked deal?
3. **Email Discovery**: If matched a contact without email, extract their email.
4. **Signal Strength**: none/weak/medium/strong
5. **Intel** (if medium/strong): stage_signal, key_facts, next_action

For each analysis result:
- If `discovered_email` + `matched_contact_id` → Call `update_contact_email()`
- If signal >= medium + `matched_deal_id` → Route through `DealSignalRouter`

Track: `emails_analyzed`, `signals_found`, `contacts_enriched`

## STEP 8: Advance backfill
```bash
python3 /home/workspace/N5/scripts/email_deal_scanner.py backfill --advance \
    --emails-processed <emails_analyzed> --signals-found <signals_found>
```

## STEP 9: Send progress SMS
- If backfill complete: "🎉 Email backfill complete! X days scanned. Emails: Y, Signals: Z, Contacts enriched: W"
- If in progress: "📧 Backfill: X% complete. Analyzed: Y emails, Found: Z signals, Enriched: W contacts. Next run: tomorrow 2 AM"

## STEP 10: Self-destruct if complete
If backfill status shows "complete":
```python
delete_agent(agent_id="<THIS_AGENT_ID>")
```

## Key Files
- Script: `/home/workspace/N5/scripts/email_deal_scanner.py`
- Prompts: `/home/workspace/N5/scripts/deal_llm_prompts.py`
- State: `/home/workspace/N5/data/backfill_state.json`
- Target: 60 days (2 runs × 30-day windows)

## Key Functions (in email_deal_scanner.py)
- `get_broad_email_queries(days, offset)` — Returns query excluding promo/social/updates
- `should_analyze_email(email)` — Pre-filter returning (should_analyze, skip_reason)
- `build_llm_context()` — Gets 50 contacts + 30 deals for matching
- `update_contact_email(contact_id, email)` — Enriches contact if email missing
- `process_email_with_llm_analysis(email, analysis)` — Routes signals, marks processed

## Analysis Response Format
When analyzing each email, structure your analysis as:
```json
{
  "matched_contact_id": "contact-id or null",
  "matched_deal_id": "deal-id or null",
  "discovered_email": "email@domain.com or null",
  "signal_strength": "none|weak|medium|strong",
  "intel": {
    "stage_signal": "none|positive|negative|stage_change",
    "inferred_stage": "stage name or null",
    "key_facts": ["fact 1", "fact 2"],
    "next_action": "what V should do next",
    "sentiment": "positive|neutral|negative"
  },
  "match_reasoning": "how you matched (for debugging)"
}
```
