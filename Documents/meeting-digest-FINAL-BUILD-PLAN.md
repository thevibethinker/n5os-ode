# Meeting Digest Redesign — Final Build Plan

**Date:** 2025-10-14 07:28 ET  
**Deadline:** Tomorrow 6:30 AM ET  
**Approved scope:** Full implementation

---

## Critical Clarification: "What's Possible"

**NOT:** Generic opportunities ("pipeline to Cornell MBAs")  
**YES:** How Careerspan can help THEM achieve THEIR goals

**Approach:**
1. Research their goals (from LinkedIn posts, profile, emails, CRM)
2. Map Careerspan's capabilities to those specific goals
3. Present as value proposition: "Here's how we can help them"

**Example transformation:**

❌ **Generic:** "Partnership opportunity with Cornell career services"

✅ **Careerspan-focused:** 
> **How Careerspan Can Help Michael:**
> - His goal: Transform career services for MBA students (per Oct 12 post)
> - Our value: Proven track record with FOHE placement system
> - The play: Offer to pilot Careerspan's MBA-to-tech transition framework at Cornell

---

## Final Feature Set (Approved)

### Core Format (45 min)
- [x] Remove HTML garbage from email subjects
- [x] Scannable structure with clear hierarchy
- [x] Clean timestamp formatting

### Intelligence Layer (3 hours)
- [x] **Research their goals** (LinkedIn posts, profile, CRM, emails)
- [x] **Map Careerspan value** to their specific goals
- [x] **Strategic moves** — concrete talking points
- [x] **LinkedIn recent posts** (last 3) with themes
- [x] **LinkedIn DM context** (preserve unread status)
- [x] **Email thread highlights** (smart summaries, not subjects)
- [x] **Last spoke context** from CRM profiles

### Profile Enrichment (30 min)
- [x] Auto-update profiles with LinkedIn data
- [x] Auto-update with email insights
- [x] Append, never overwrite
- [x] Log all changes

**Total estimated time:** 5-6 hours

---

## Build Sequence

### Phase 1: Core Utilities (30 min)
**Files:**
- `n5_text_cleaner.py` — Remove HTML, clean formatting
- `n5_email_summarizer.py` — Smart email thread analysis

**Tests:**
- HTML garbage → clean text
- Email threads → key points extracted

---

### Phase 2: Intelligence Modules (2.5 hours)

**File:** `n5_linkedin_intel.py`
- Fetch recent posts via `view_webpage` (authenticated)
- Extract themes/topics from posts
- Fetch DM context (preserve unread)
- Parse profile summary
- 24-hour cache layer

**File:** `n5_careerspan_value_mapper.py`
- Research stakeholder goals from all sources
- Map to Careerspan capabilities
- Generate specific value propositions
- Suggest concrete plays

**Tests:**
- LinkedIn scraping works with auth
- Goal extraction accurate
- Value mapping makes sense
- DM unread status preserved

---

### Phase 3: Profile Enrichment Engine (30 min)

**File:** `n5_profile_enricher.py`
- Read existing profile
- Append new LinkedIn section
- Append new email insights
- Update last_interaction metadata
- Log changes

**Safety (P5):**
- Never overwrite existing data
- Always append with timestamps
- Backup before write
- Verify writes

---

### Phase 4: Main Digest Generator (1.5 hours)

**File:** `meeting_prep_digest_v2.py`
- Import all modules
- Fetch calendar via existing helpers
- For each meeting:
  - Research stakeholder goals
  - Map Careerspan value
  - Fetch LinkedIn intel
  - Summarize email context
  - Generate strategic moves
  - Enrich profile
- Format output in energizing structure
- Save to N5/digests/

**Format:**
```markdown
# Your Meetings — [Date]

## [Time] — [Name] ([Role/Org])

### 🎯 How Careerspan Can Help
- **Their goal:** [Specific goal from research]
- **Our value:** [Careerspan capability that maps]
- **The play:** [Concrete action/offer]

### 💡 Fresh Intel
**LinkedIn (last 3 posts):**
- [Post summary with theme]

**Recent DMs:**
- [Key context if exists]

**Email highlights:**
- [Smart summary]

### 📋 Quick Context
- **Last spoke:** [Date + topic]
- **Status:** [Relationship status]
- **Strategic moves:**
  1. [Specific talking point]
  2. [Specific question to ask]
```

---

### Phase 5: Testing & Deployment (30 min)

**Test with dry-run:**
```bash
cd /home/workspace/N5/scripts
python3 meeting_prep_digest_v2.py --date 2025-10-15 --dry-run
```

**Verify:**
- [ ] LinkedIn data fetched correctly
- [ ] Goals accurately identified
- [ ] Careerspan value propositions make sense
- [ ] Email summaries are meaningful
- [ ] DMs show up if they exist
- [ ] Profiles enriched correctly
- [ ] Format is scannable

**Deploy:**
1. Update scheduled task command
2. Test manual run for tomorrow
3. Verify 6:30 AM trigger set correctly

---

## Risk Mitigation

**P5 (Anti-Overwrite):**
- Backup current script before replacing
- Profile enrichment appends only
- Git commit before deploy

**P7 (Dry-Run):**
- Test with --dry-run first
- Show you output before deploying
- Verify no data corruption

**P11 (Failure Modes):**
- Graceful fallback if LinkedIn fails
- Graceful fallback if no profile exists
- Never break calendar/email fetching
- Log all errors

**P15 (Complete Before Claiming):**
- Full test on real meetings
- Your approval before deploying
- Verify scheduled task trigger

---

## Careerspan Capabilities Reference

**For value mapping, I'll need to know:**

What can Careerspan do for different stakeholder types?

**For example:**
- **Career services:** Placement tracking, alumni engagement, employer partnerships?
- **MBA students:** Job search, tech transitions, skill development?
- **Employers:** Talent pipeline, diversity hiring, retention?
- **Investors:** Growth metrics, market validation, traction?
- **Partners:** Co-marketing, integration, referrals?

**Question:** Should I load this from somewhere in Knowledge/, or do you want to brief me now?

---

## Timeline

**Start:** Now (07:30 ET)  
**Phase 1-3 complete:** 10:30 ET  
**Phase 4 complete:** 12:00 ET  
**Phase 5 complete:** 12:30 ET  
**Your review:** 12:30-13:00 ET  
**Deploy:** 13:00 ET  
**First run:** Tomorrow 06:30 ET

**Slack:** 2-3 hours for unknowns

---

## Next Steps

1. **I need:** Careerspan capabilities reference (see question above)
2. **Then:** Start building Phase 1
3. **Check-in:** Show you Phase 1-2 output for feedback (~2 hours)
4. **Final:** Complete build and test with dry-run

**Ready to start?**

---

2025-10-14 07:28:52 ET
