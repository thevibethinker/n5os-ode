# Meeting Prep Digest Redesign — Action Plan

**Date:** 2025-10-14 07:23 ET  
**Status:** Planning Phase  
**Previous attempt:** Lost due to container crash

---

## Situation Assessment

### What Exists Now
- **Current script:** `file 'N5/scripts/meeting_prep_digest.py'` (24K, working)
- **Backup:** `meeting_prep_digest.py.backup-vos` (28K)
- **Output:** Daily digests in `N5/digests/`
- **Problem:** Output is mechanical, uninspiring, full of HTML garbage

### What Was Lost
During container crash, I created 3 new files that didn't persist:
- `meeting_prep_digest_v2.py` 
- `n5_linkedin_intel.py`
- `n5_possibility_engine.py`

---

## Your Requirements (From This Session)

1. **Make it energizing** — "feel energized about taking on those meetings"
2. **Show possibilities** — "what possibilities" in each meeting
3. **Fresh intel** — LinkedIn posts (last 3), profile updates
4. **Relationship context** — LinkedIn messages, meaningful history
5. **Auto-enrich profiles** — Update stakeholder profiles with new data
6. **Preserve unread status** — If LinkedIn message was unread, keep it unread

---

## Critical Questions Before Proceeding

I need clarity on these before building:

### 1. LinkedIn Access
- **You mentioned:** "I logged into LinkedIn in your Zo browser"
- **Confirm:** Can I use `view_webpage` tool to access LinkedIn when you're logged in?
- **Test needed:** Should I test fetching one LinkedIn profile first before full build?

### 2. Scope & Phasing
Which approach do you prefer?

**Option A: Full rebuild (3-4 hours)**
- All 3 modules (LinkedIn intel, possibility engine, main digest)
- Complete format transformation
- LinkedIn scraping integration
- Auto-profile enrichment
- Ready for production

**Option B: Phased approach (1 hour Phase 1)**
- Phase 1: Fix format only (no LinkedIn yet)
  - Remove HTML garbage
  - Better structure
  - Possibility-focused language
  - Use existing data sources
- Phase 2: Add LinkedIn intelligence later
- Faster validation, lower risk

**Option C: Manual demonstration first (30 min)**
- I manually create ONE perfect digest for today
- You review and provide feedback
- Then I automate based on approved template
- Ensures we're aligned before coding

### 3. Testing Strategy
- Test on tomorrow's meetings first?
- Or regenerate today's digest for comparison?
- Want dry-run output before committing?

### 4. Profile Enrichment Rules
When LinkedIn reveals new info:
- Auto-update profiles immediately? Or flag for review?
- What sections to add? (Recent posts, current focus, engagement patterns)
- Preserve existing data or append only?

### 5. Fallback Behavior
If LinkedIn scraping fails:
- Generate digest without it?
- Send alert?
- Use cached data from previous runs?

---

## Proposed Build Sequence (If Approved)

### Stage 1: Foundation (30 min)
1. Create LinkedIn scraping helper using `view_webpage`
2. Test on one real profile (e.g., Michael Maher)
3. Verify data extraction works
4. Show you the results

### Stage 2: Format Engine (45 min)
1. Create possibility engine module
2. Build new digest formatter
3. Test output format without LinkedIn data
4. Show you comparison: old vs new

### Stage 3: Integration (45 min)
1. Combine LinkedIn + formatter
2. Add profile auto-enrichment
3. Full end-to-end test
4. Dry-run for tomorrow's meetings

### Stage 4: Deployment (15 min)
1. Update scheduled task
2. Create rollback plan
3. Monitor first run

**Total time: ~2.5 hours**

---

## Risk Mitigation

**P5 (Anti-Overwrite):** 
- Backup existing script before touching it
- Create V2 as separate file initially
- Test thoroughly before replacing

**P7 (Dry-Run):**
- All testing in dry-run mode first
- Verify output before saving
- No profile changes until approved

**P11 (Failure Modes):**
- Graceful fallback if LinkedIn unavailable
- Cache LinkedIn data for resilience
- Alert if data quality drops

---

## What I Need From You

**Before I proceed, please clarify:**

1. **LinkedIn access confirmation** — Can I use `view_webpage` for LinkedIn with your auth?

2. **Approach preference** — A (full), B (phased), or C (demo first)?

3. **Timeline urgency** — Need this for tomorrow morning? Or can iterate?

4. **Risk tolerance** — Replace existing script quickly or parallel testing first?

5. **Must-haves vs nice-to-haves** — Which features are critical?

---

## Success Criteria

How will we know this succeeded?

- [ ] You actually want to read the digest
- [ ] You learn something new about stakeholders
- [ ] Format is scannable in < 2 minutes
- [ ] Strategic moves are actionable
- [ ] Profiles get richer over time
- [ ] No regression in reliability

---

**Next step:** Await your answers to the 5 questions above, then execute approved plan.

---

2025-10-14 07:23:47 ET
