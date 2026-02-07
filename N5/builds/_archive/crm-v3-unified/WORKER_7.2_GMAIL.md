---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
worker_id: 7.2
parent: WORKER_7_INTEGRATION
---

# Worker 7.2: Gmail Integration Implementation

## Mission
Replace stub Gmail thread analysis with real `use_app_gmail` tool calls.

## Context
- Gmail connected: V has 2 accounts (attawar.v@gmail.com, vrijen@mycareerspan.com)
- Tool available: `use_app_gmail`
- Current enrichment worker has stub: file 'N5/scripts/crm_enrichment_worker.py' (lines 126-149)

## Inputs
1. `use_app_gmail` tool documentation from `list_app_tools`
2. file 'N5/scripts/crm_enrichment_worker.py' - Current enrichment worker with stub
3. Connected Gmail accounts

## Task Breakdown

### Step 1: Review Gmail Tool API
Call `list_app_gmail_tools` to understand:
- What search/query methods exist?
- How to search for threads with specific email?
- What response format to expect?

### Step 2: Design Gmail Analysis Approach
**Deterministic:** Search Gmail for threads
**Semantic:** Analyze thread content for relationship context

Approach:
1. Use `use_app_gmail` with `gmail-search-email-messages` tool
2. Query: threads with profile email address
3. Extract: subject, date, snippet
4. Analyze: communication patterns, tone, frequency

### Step 3: Create Gmail Helper
Create helper function (or prompt) that:
- Takes email address as input
- Calls `use_app_gmail` to search
- Returns formatted intelligence block

### Step 4: Integrate into Enrichment Worker
Update file 'N5/scripts/crm_enrichment_worker.py':
- Remove stub (lines 126-149)
- Call Gmail helper
- Format response into intelligence block
- Handle no-results gracefully

### Step 5: Test with Real Profile
Run enrichment on profile with known Gmail history:
- Verify real threads appear
- Check intelligence quality
- Validate error handling

## Outputs
1. **Modified file:** `N5/scripts/crm_enrichment_worker.py` (with real Gmail calls)
2. **Helper/Prompt:** Gmail analysis function
3. **Test results:** Enriched profile with real Gmail intelligence

## Constraints
- **Use tools, not scripts:** Prefer `use_app_gmail` tool over writing custom Gmail API code
- **Semantic analysis:** LLM should analyze thread content, not regex
- **Privacy:** Be mindful of email content in logs
- **Rate limits:** Handle Gmail API rate limits

## Success Criteria
- [ ] Gmail tool tested and working
- [ ] Stub code removed from enrichment worker
- [ ] Real Gmail search performed
- [ ] Thread analysis produces useful intelligence
- [ ] Error handling for no-results case
- [ ] Test profile enriched with real Gmail data

## Dependencies
- Gmail connection ✅
- `use_app_gmail` tool ✅
- Worker 7.1 complete ⏳

## Estimated Time
30 minutes

## Handoff
When complete, hand to **WORKER_7.3_LINKEDIN** for LinkedIn integration.

