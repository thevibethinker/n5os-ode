# Stakeholder System — Implementation Plan
**Date:** 2025-10-12  
**Status:** 🚀 READY TO EXECUTE  
**Context:** Resuming from thread export after system build completion

---

## 🎯 Mission: Production Deployment

Transform the tested stakeholder system into a live, automated workflow that enhances your meeting prep and captures relationship intelligence progressively.

---

## 📊 Current State

### ✅ What's Built & Tested
- **Core Infrastructure:** Profile manager, safe updater, auto-creation scripts
- **3 Test Profiles:** Michael Maher, Fei Ma, Elaine Pak (all verified)
- **Safeguards Validated:** Backups, conflict detection, append-only updates
- **APIs Connected:** Gmail ✅ | Google Calendar ✅

### 📋 Existing Profiles Ready for Oct 14 Meetings
1. **Michael Maher** (mmm429@cornell.edu) - Cornell MBA, LD-COM, 3:00 PM Oct 14
2. **Elaine Pak** (epak171@gmail.com) - Cornell alum, RAG interest, 3:30 PM Oct 14
3. **Fei Ma** (fei@withnira.com) - Nira CEO, co-selling partner, 4:00 PM Oct 14

### 🆕 New Stakeholders Detected (Need Profiles)
1. **Kat de Haen** (kat@thefourtheffect.com) - Oct 15, 11:00 AM
2. **Jake/Ray/Shivani @ FOHE** (fohe.org) - Oct 15, 12:00 PM, partnership kickoff
3. **Hei-Yue Pang @ YUU** (hpang@yearupunited.org) - Oct 16, 2:00 PM, partnership

---

## 🗓️ Implementation Timeline

### **Phase 1: Profile Creation (Today - Oct 12)**
**Goal:** Create profiles for new stakeholders before their meetings

#### Task 1.1: Kat de Haen Profile
- **Meeting:** Oct 15, 11:00 AM (30 min)
- **Email:** kat@thefourtheffect.com
- **Actions:**
  - [ ] Search Gmail for full email history
  - [ ] Analyze relationship context with LLM
  - [ ] Infer organization, role, lead type
  - [ ] Generate profile with initial interaction summary
  - [ ] Add to index

#### Task 1.2: FOHE Team Profiles
- **Meeting:** Oct 15, 12:00 PM (partnership kickoff)
- **Contacts:** jake@fohe.org, ray@fohe.org, shivani@fohe.org
- **Context:** "Pilot kickoff alignment; roles; timeline; logistics"
- **Actions:**
  - [ ] Search Gmail for FOHE correspondence
  - [ ] Create organization profile (FOHE as entity)
  - [ ] Create individual profiles for Jake, Ray, Shivani
  - [ ] Tag as LD-COM (partnership)
  - [ ] Link profiles together (same org)

#### Task 1.3: YUU Partnership Profile
- **Meeting:** Oct 16, 2:00 PM
- **Contact:** Hei-Yue Pang (hpang@yearupunited.org)
- **Event:** "CareerSpan <> YUU"
- **Actions:**
  - [ ] Search Gmail for Year Up United correspondence
  - [ ] Create profile for Hei-Yue
  - [ ] Infer role and partnership context
  - [ ] Tag as LD-COM

---

### **Phase 2: Meeting Prep Enhancement (Oct 13-14)**
**Goal:** Generate rich, profile-powered meeting prep for Oct 14 meetings

#### Task 2.1: Enhanced Meeting Prep Script
- **Input:** Calendar events + Stakeholder profiles
- **Output:** Contextual prep digest (not cold start)
- **Implementation:**
  ```python
  # N5/scripts/enhanced_meeting_prep.py
  
  1. Load calendar events for next 24-48 hours
  2. For each external meeting:
     - Load stakeholder profile(s) from index
     - Fetch recent emails (last 30-90 days only)
     - Generate prep:
       * Profile context (how we met, objectives)
       * Recent activity summary
       * Suggested talking points
       * Open loops to address
  3. Generate daily digest markdown
  4. Save to N5/digests/meeting-prep-YYYY-MM-DD.md
  ```

#### Task 2.2: Test with Oct 14 Meetings
- **Test Cases:**
  - Michael Maher (has profile)
  - Elaine Pak (has profile)
  - Fei Ma (has profile)
- **Validation:**
  - [ ] Profile context loaded correctly
  - [ ] Recent emails included (not full history)
  - [ ] Talking points are specific to relationship
  - [ ] No "first meeting" language

---

### **Phase 3: Post-Meeting Auto-Update (Oct 14+)**
**Goal:** Automatically update profiles after meeting transcripts processed

#### Task 3.1: Transcript Ingestion Hook
- **Trigger:** Meeting transcript saved to N5/records/meetings/
- **Actions:**
  1. Detect external attendees from transcript metadata
  2. For each external attendee:
     - Find profile in index (by email)
     - Generate summary from transcript (LLM)
     - Extract key points, outcomes, action items
     - Call `update_profile_from_transcript()` (already built ✅)
     - Backup created automatically
     - Index updated with last_interaction date

#### Task 3.2: Integration Points
- **Option A:** Manual trigger (you run script after transcript ready)
- **Option B:** Automated watch (inotify on meetings directory)
- **Recommendation:** Start with Option A, upgrade to B after validation

---

### **Phase 4: Weekly Auto-Discovery (Oct 20+)**
**Goal:** Scan calendar weekly for new external stakeholders

#### Task 4.1: Weekly Calendar Scan
- **Schedule:** Sunday 6:00 PM ET
- **Process:**
  1. Fetch next 2 weeks of calendar events
  2. Identify external attendees (not @mycareerspan.com/@theapply.ai)
  3. Check if profile exists in index
  4. If not exists:
     - Search Gmail for email history
     - LLM analysis for organization/role/lead type
     - Generate profile
     - Add to pending review list
  5. Generate digest: "New stakeholders detected this week"
  6. Send to you for confirmation

#### Task 4.2: Scheduled Task Setup
```bash
# Use Zo's scheduled task feature
RRULE: "FREQ=WEEKLY;BYDAY=SU;BYHOUR=18;BYMINUTE=0"
Instruction: "Scan calendar for new external stakeholders and create profiles"
```

---

### **Phase 5: Monitoring & Refinement (Oct 14-20)**
**Goal:** Monitor first week of production use and refine

#### Metrics to Track
- **Profile Creation:**
  - New profiles created: Target 5-10 in week 1
  - Auto-detection accuracy: Target >80%
  - Manual correction rate: Track edits needed
  
- **Meeting Prep Quality:**
  - Profiles used in prep: Track which meetings benefit
  - Context accuracy: Your feedback on prep quality
  - Time saved: Estimate vs. manual prep

- **Post-Meeting Updates:**
  - Transcripts processed: Track success rate
  - Update conflicts: Should be zero (safeguards)
  - Backup health: Validate backups exist

#### Refinement Areas
- [ ] LLM prompts for analysis (tune based on accuracy)
- [ ] Lead type inference rules (adjust confidence thresholds)
- [ ] Meeting prep format (adjust based on your feedback)
- [ ] Tag taxonomy (add/refine as patterns emerge)

---

## 🔧 Technical Implementation

### Scripts to Write

#### 1. `N5/scripts/create_stakeholder_from_email.py`
```python
"""
Create stakeholder profile from email address.
- Search Gmail for full history
- LLM analysis for context
- Generate profile
- Add to index
"""
```

#### 2. `N5/scripts/enhanced_meeting_prep.py`
```python
"""
Generate meeting prep using stakeholder profiles.
- Load profiles for external attendees
- Fetch recent emails only
- Generate contextual prep
- Save to digests/
"""
```

#### 3. `N5/scripts/auto_update_from_transcript.py`
```python
"""
Update stakeholder profiles after meeting transcripts.
- Parse transcript for attendees
- Generate summary
- Update profiles safely
- Track in audit log
"""
```

#### 4. `N5/scripts/weekly_stakeholder_scan.py`
```python
"""
Weekly scan for new external stakeholders.
- Fetch calendar events (next 2 weeks)
- Detect new external contacts
- Create profiles for review
- Generate digest
"""
```

### API Integration Code

#### Gmail Search (Full History)
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def search_gmail_history(email, max_results=100):
    """
    Search Gmail for all messages with stakeholder email.
    No 3-message limit - pagination available.
    """
    service = build('gmail', 'v1', credentials=creds)
    
    query = f"from:{email} OR to:{email}"
    results = []
    
    # Paginate through all results
    page_token = None
    while True:
        response = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results,
            pageToken=page_token
        ).execute()
        
        messages = response.get('messages', [])
        results.extend(messages)
        
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    return results
```

#### Calendar External Detection
```python
def detect_external_attendees(event):
    """
    Identify external stakeholders from calendar event.
    Exclude internal team domains.
    """
    internal_domains = ['mycareerspan.com', 'theapply.ai']
    external = []
    
    for attendee in event.get('attendees', []):
        email = attendee['email']
        domain = email.split('@')[-1]
        
        if domain not in internal_domains:
            external.append({
                'email': email,
                'name': attendee.get('displayName', ''),
                'response': attendee.get('responseStatus')
            })
    
    return external
```

---

## 🚦 Execution Order

### Today (Oct 12) - Evening
1. ✅ Review this implementation plan
2. **Create new stakeholder profiles:**
   - Kat de Haen (Oct 15 meeting)
   - FOHE team (Oct 15 meeting)
   - YUU contact (Oct 16 meeting)
3. **Write profile creation script** (`create_stakeholder_from_email.py`)
4. **Test profile creation** with Kat de Haen

### Tomorrow (Oct 13) - Morning
1. **Write enhanced meeting prep script** (`enhanced_meeting_prep.py`)
2. **Generate Oct 14 meeting prep** using profiles
3. **Compare with previous prep** (validate improvement)
4. **Send prep digest** to you for review

### Oct 14 (Monday) - After Meetings
1. **Process meeting transcripts** (when available)
2. **Test auto-update workflow** with one profile
3. **Validate safeguards** (backups, no overwrites)
4. **Review updated profiles** for accuracy

### Oct 15-20 (Rest of Week)
1. **Monitor daily prep generation**
2. **Track new profiles created**
3. **Collect feedback** on prep quality
4. **Refine LLM prompts** based on results
5. **Document learnings** for next iteration

---

## ✅ Success Criteria

### Week 1 (Oct 14-20)
- [ ] 5-10 new profiles created from real meetings
- [ ] Daily meeting prep generated with profile context
- [ ] 3+ transcripts processed with auto-updates
- [ ] Zero profile corruption (safeguards working)
- [ ] Measurable time savings on meeting prep

### Week 4 (Nov 11)
- [ ] 20-30 profiles with rich interaction histories
- [ ] Tag accuracy >80% (minimal corrections needed)
- [ ] Meeting prep quality rated "excellent" by you
- [ ] Post-meeting updates 100% automated
- [ ] Weekly scan catching all new stakeholders

### Month 3 (Jan 2026)
- [ ] 50+ profiles = strategic intelligence asset
- [ ] Relationship patterns identified (dormant, active, etc.)
- [ ] Network insights emerging (warm intro paths)
- [ ] Integration with Howie (context API)
- [ ] System running fully automated

---

## 🎯 Key Questions for You

Before I start executing, please confirm:

1. **Profile Creation Approach:**
   - Should I create profiles for Kat, FOHE, and YUU tonight?
   - Or wait until you review this plan first?

2. **Meeting Prep Timing:**
   - When do you want Oct 14 prep? Tonight or tomorrow morning?
   - Preferred delivery: Email, N5 digest file, or both?

3. **Automation Preferences:**
   - Post-meeting updates: Manual trigger or auto-detect?
   - Weekly scan: Auto-create profiles or send for review first?

4. **Lead Type for New Stakeholders:**
   - Kat de Haen: LD-NET (general networking) or LD-COM (potential partner)?
   - FOHE team: LD-COM confirmed (partnership kickoff)?
   - YUU contact: LD-COM confirmed (partnership discussion)?

---

## 📁 Files to Create

1. **N5/scripts/create_stakeholder_from_email.py** - New profile creation
2. **N5/scripts/enhanced_meeting_prep.py** - Profile-powered prep
3. **N5/scripts/auto_update_from_transcript.py** - Post-meeting updates
4. **N5/scripts/weekly_stakeholder_scan.py** - Auto-discovery
5. **N5/digests/meeting-prep-2025-10-14.md** - Oct 14 prep (with profiles)

---

## 🔄 Next Action

**Awaiting your confirmation on the 4 questions above, then I'll begin:**

1. Creating new stakeholder profiles (Kat, FOHE, YUU)
2. Writing the enhanced meeting prep script
3. Generating Oct 14 meeting prep digest

**Ready to execute when you give the green light!** 🚀
