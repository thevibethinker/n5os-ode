---
created: 2025-11-18
last_edited: 2025-11-18
version: 1
worker_id: 7.3
parent: WORKER_7_INTEGRATION
---
# Worker 7.3: LinkedIn Integration (Limited Scope)

## Mission
Implement basic LinkedIn enrichment OR document technical limitation with clear next steps.

## Context
- No LinkedIn API access currently
- Web scraping is technically possible but rate-limited
- LinkedIn has strict ToS around scraping
- Goal: Production-ready system (stub with good documentation is acceptable)

## Decision Tree

### Option A: Implement Basic Scraping
**If:** Time permits and scraping is feasible
**Then:** Build rate-limited scraper with proper error handling

### Option B: Document Limitation
**If:** Scraping too complex or violates ToS
**Then:** Keep stub but add clear documentation on how to enable

## Task Breakdown (Option A: Scraping)

### Step 1: Research Approach
Use `web_research` to find:
- Is there a semi-official LinkedIn scraping tool?
- What are the rate limits?
- What's the ToS stance?

### Step 2: Test Scraping
Build minimal Python script that:
- Takes LinkedIn profile URL
- Extracts: name, title, company, location
- Uses proper User-Agent
- Respects rate limits

### Step 3: Integrate
Add to enrichment worker with:
- Rate limiting (max 5 requests/hour)
- Error handling for blocked requests
- Fallback to stub if scraping fails

## Task Breakdown (Option B: Documentation)

### Step 1: Document Current State
Create clear documentation in enrichment worker:
```python
# LinkedIn enrichment NOT YET IMPLEMENTED
# Reason: Requires authenticated scraping or API access
# To enable:
#   1. Get LinkedIn API credentials OR
#   2. Implement rate-limited scraping (see LINKEDIN_INTEGRATION.md)
#   3. Replace this stub with real implementation
```

### Step 2: Create Integration Plan
Write file 'N5/docs/LINKEDIN_INTEGRATION.md' with:
- Technical requirements
- API options
- Scraping approach
- Estimated implementation time

### Step 3: Update Enrichment Worker
Keep stub but:
- Add clear "NOT IMPLEMENTED" marker
- Link to integration plan
- Ensure system works without LinkedIn

## Outputs

### Option A:
1. **Scraper:** Basic LinkedIn profile scraper
2. **Integration:** Real LinkedIn data in enrichment
3. **Rate limiting:** Proper throttling

### Option B:
1. **Documentation:** file 'N5/docs/LINKEDIN_INTEGRATION.md'
2. **Clear stubs:** Well-documented limitation
3. **Integration path:** Clear next steps

## Constraints
- **15 minute time box:** Don't over-invest if complex
- **Production ready:** Stub with docs is acceptable
- **Legal:** Must respect LinkedIn ToS
- **Pragmatic:** Working system > perfect system

## Success Criteria

**Option A:**
- [ ] Scraper working for public profiles
- [ ] Rate limiting implemented
- [ ] Integrated into enrichment worker

**Option B:**
- [ ] Limitation clearly documented
- [ ] Integration plan created
- [ ] Stub updated with clear markers
- [ ] System works without LinkedIn

## Dependencies
- Web research capability ✅
- Python for scraping (if Option A) ✅
- Worker 7.1, 7.2 complete ⏳

## Estimated Time
15 minutes (time-boxed)

## Recommendation
**Choose Option B** - Document limitation, move forward with Aviato + Gmail as production data sources. LinkedIn can be Phase 2.

## Handoff
When complete, hand to **WORKER_7.4_EXECUTION** to run enrichment queue.

