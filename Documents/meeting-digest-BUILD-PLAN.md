# Meeting Digest Redesign — Build Plan (APPROVED)

**Date:** 2025-10-14 07:27 ET  
**Timeline:** 3-4 hours to complete  
**Deadline:** Must work for tomorrow 6:30 AM run  
**Status:** EXECUTING

---

## Confirmed Requirements

### Must-Have Features (Tier 1)
1. ✅ Remove HTML garbage from output
2. ✅ Scannable structure (not wall of text)
3. ✅ **"What's possible"** = Ways Careerspan can contribute to their/org goals (requires research)
4. ✅ Strategic moves for each meeting
5. ✅ LinkedIn recent posts (last 3)
6. ✅ **Both** email AND LinkedIn DM context
7. ✅ Auto-profile enrichment (critical)

### Key Clarification
**"What's possible"** means:
- Research person's goals (profile, LinkedIn, posts)
- Research org's goals (company info, news)
- Map how Careerspan capabilities serve those goals
- Present as contribution opportunities

---

## Build Sequence

### Phase 1: LinkedIn Intelligence Module (60 min)
**File:** `N5/scripts/n5_linkedin_intel.py`

**Functions to build:**
- `get_recent_posts(profile_url)` → List[Dict] with post content, date, themes
- `get_linkedin_messages(person_name)` → List[Dict] with message context
- `get_profile_summary(profile_url)` → Dict with current role, headline, about
- `detect_person_goals(profile, posts)` → List[str] of inferred goals
- `enrich_stakeholder_profile(email, linkedin_data)` → Updates CRM profile

**Method:** Use Zo authenticated browser via view_webpage tool  
**Cache:** 24-hour cache to avoid rate limits  
**Safety:** Preserve unread status on DMs

### Phase 2: Possibility Engine (60 min)
**File:** `N5/scripts/n5_possibility_engine.py`

**Functions to build:**
- `research_org_goals(company_name)` → List[str] of org objectives
- `map_careerspan_contributions(person_goals, org_goals)` → List[str] opportunities
- `infer_meeting_purpose(calendar_desc, email_context, dm_context)` → str
- `suggest_strategic_moves(stakeholder_type, relationship_status)` → List[str]
- `synthesize_fresh_intel(posts, messages)` → str summary of new info

**Intelligence sources:**
- Stakeholder profile (CRM)
- LinkedIn posts + DMs
- Email thread analysis
- Company research (web search if needed)

### Phase 3: Main Digest Script (90 min)
**File:** `N5/scripts/meeting_prep_digest_v2.py`

**Architecture:**
```python
class MeetingPrepDigestV2:
    def __init__(self):
        self.linkedin_intel = LinkedInIntel()
        self.possibility_engine = PossibilityEngine()
        self.view_webpage = view_webpage  # Tool injection
    
    def generate_digest(date, enrich_profiles=True):
        meetings = fetch_calendar_events(date)  # Existing
        briefs = []
        
        for meeting in meetings:
            brief = self.create_meeting_brief(meeting, enrich_profiles)
            briefs.append(brief)
        
        return self.format_digest(briefs, date)
    
    def create_meeting_brief(meeting, enrich_profiles):
        # 1. Get stakeholder profile
        # 2. Fetch LinkedIn intel (posts + DMs)
        # 3. Research person/org goals
        # 4. Map Careerspan contributions
        # 5. Generate strategic moves
        # 6. Enrich profile if enabled
        return brief_dict
    
    def format_digest(briefs, date):
        # Clean, scannable format
        # Remove HTML garbage
        # Highlight what's possible
        return markdown_string
```

**Output format:**
```markdown
# Your Meetings — Monday, Oct 14

**3 conversations · 2 new opportunities · 1 follow-up needed**

---

## 3:00 PM — Michael Maher (Cornell MBA)

### 🎯 What Careerspan Can Offer
- [Specific contribution based on their goals]
- [Specific contribution based on org goals]
- [Specific contribution based on recent activity]

### 💡 Fresh Intel
- LinkedIn: [Recent post theme + date]
- Recent DM: [Last exchange context]
- Email: [Last conversation topic]

### 🎬 Strategic Moves
1. [Specific action based on context]
2. [Specific action based on relationship]
3. [Specific action based on opportunity]

### 📋 Quick Context
- **Last spoke:** Oct 8 about partnership terms
- **Status:** Active partner, exploring expansion
- **Priority:** High (strategic partnership)

---
```

### Phase 4: Integration & Testing (30 min)
1. Import existing helpers from `meeting_prep_digest.py`
2. Add tool injection for `view_webpage` access
3. Create test harness
4. Dry-run on tomorrow's meetings
5. Verify profile enrichment works

### Phase 5: Safety & Deployment (15 min)
1. Create backup of existing script
2. Test dry-run mode (P7)
3. Verify no data loss (P5)
4. Document assumptions (P21)
5. Deploy for 6:30 AM run

---

## Technical Decisions

### LinkedIn Access
- **Method:** view_webpage tool with user's authenticated session
- **Parsing:** BeautifulSoup for HTML extraction
- **Rate limiting:** 24-hour cache + respectful delays
- **DM preservation:** Note unread status, don't mark as read

### Profile Enrichment
- **Trigger:** Every digest run (if enrich_profiles=True)
- **Method:** Append new sections to existing profiles
- **Safety:** Never overwrite existing data (P5)
- **Format:** Markdown sections with timestamps

### Error Handling (P19)
- Graceful fallback if LinkedIn fails
- Log errors but don't block digest
- Show "Data unavailable" vs empty
- Continue with partial data

### Context Management (P0, P8)
- Rule-of-Two: Max 2 profiles loaded at once
- Minimal context: Only load what's needed per meeting
- Clean up after each brief generation

---

## Success Criteria

- [ ] Tomorrow's digest feels energizing (not mechanical)
- [ ] "What's possible" shows real Careerspan contributions
- [ ] Fresh intel reveals something new about each person
- [ ] Strategic moves are specific and actionable
- [ ] Profiles auto-enrich with new data
- [ ] Generated by 6:30 AM without errors
- [ ] Takes < 5 minutes to read and prep from

---

## Risk Mitigation

**Risk:** LinkedIn scraping fails  
**Mitigation:** Graceful fallback to existing data + email only

**Risk:** Tool injection doesn't work in scheduled task  
**Mitigation:** Test in scheduled task context first

**Risk:** Takes too long, misses 6:30 AM deadline  
**Mitigation:** Add timeout + partial generation

**Risk:** Profile enrichment corrupts existing data  
**Mitigation:** Backup profiles before first run (P5)

---

## Build Log

**07:27 ET** — Build plan approved, starting Phase 1  
**07:30 ET** — [Phase 1 status]  
**08:30 ET** — [Phase 2 status]  
**10:00 ET** — [Phase 3 status]  
**10:30 ET** — [Phase 4 status]  
**10:45 ET** — [Phase 5 complete]

---

## Next Action

**IMMEDIATE:** Start Phase 1 - Build LinkedIn Intelligence Module

**Command:**
```bash
cd /home/workspace/N5/scripts
# Create n5_linkedin_intel.py
```

---

2025-10-14 07:27:48 ET
