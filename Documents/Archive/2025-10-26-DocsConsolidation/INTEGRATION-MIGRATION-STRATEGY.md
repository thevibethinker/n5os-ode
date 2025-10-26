# Stakeholder Tagging System — Integration & Migration Strategy

**Date:** 2025-10-12  
**Version:** 1.0  
**Status:** Strategy Approved

---

## V's Decisions (System Integration)

### 1. Historical Profile Migration ✅
**Strategy:** Lazy migration — tag only when contacts become active again

**Implementation:**
- Do NOT retroactively tag all old profiles now
- When contact re-engages (email, meeting, mention), tag at that time
- Old profiles remain as-is until interaction

**Location of old profiles:**
- `Knowledge/crm/profiles/*.md` (6 profiles) — Old format, no tags
- `N5/records/meetings/2025-08-*` (4-5 profiles) — Older format with blocks but no tags

**Migration trigger:** Contact becomes active (email received, meeting scheduled, V mentions them)

---

### 2. Scanner Schedule ✅
**Two-tier schedule:**

**Tier 1: Sunday Extended Review (Weekly)**
- **Time:** Sundays 6:00 PM ET
- **Scope:** Full week ahead (next 7 days)
- **Purpose:** Strategic stakeholder review, tag verification, week planning
- **Enrichment:** Full enrichment for all new/updated contacts
- **Output:** Comprehensive weekly review digest
- **Notification:** SMS + scheduled task output

**Tier 2: Daily Brief (Weekdays)**
- **Time:** 8:00 AM ET (Monday-Friday)
- **Scope:** Today only
- **Purpose:** Daily meeting prep, immediate focus
- **Enrichment:** Use existing tags, no new enrichment
- **Output:** Brief daily digest (existing meeting prep format)
- **Notification:** SMS text "Your daily digest is ready"

---

### 3. Meeting Monitor Integration ✅
**Strategy:** Integrate stakeholder tagging with existing meeting monitor

**Architecture:**
```
Meeting Monitor (Daily 8am)
    ↓
Scans Google Calendar for V-OS tagged meetings
    ↓
Checks if stakeholder profile exists
    ├─ Exists → Load tags, use in digest
    └─ New → Run email scanner, enrich if high-priority, create profile
    ↓
Generate daily meeting prep digest (8am)
    ↓
SMS notification
```

**Integration points:**
1. **Meeting monitor calls stakeholder tagging** when new external meeting detected
2. **Stakeholder profiles feed context** to meeting prep digest
3. **Tags determine enrichment** (critical priority → auto-enrich)
4. **Unified output** (daily digest includes stakeholder intelligence)

---

### 4. CRM Strategy ✅
**Primary:** Markdown-based stakeholder profiles (canonical source of truth)  
**Secondary:** SQLite `crm.db` (query interface, defer for now)

**Current focus:**
- Stakeholder profiles in `N5/records/meetings/{folder}/stakeholder_profile.md`
- Tags embedded in markdown
- Query via grep/filesystem (simple, works)

**Future (deferred):**
- Sync tags to `Knowledge/crm/crm.db` for advanced queries
- Build query API for Howie integration
- Structured search by tags, priority, context

**Decision:** Focus on markdown CRM, database sync later (Phase 4)

---

### 5. Auto-Enrichment Rules ✅
**Binary priority system:**
- `#priority:critical` → Auto-enrich (web + LinkedIn + deep research)
- `#priority:non-critical` → Basic enrichment only (domain analysis)

**Enrichment triggers (critical priority auto-assigned to):**
- `#stakeholder:investor` → Always critical → Auto-enrich
- `#stakeholder:advisor` → Always critical → Auto-enrich
- `#stakeholder:customer` → Always critical → Auto-enrich
- `#stakeholder:partner:*` → Manual priority → Enrich if V sets critical
- All others → Non-critical → Basic enrichment only

**V's rule:** "Literally the moment I give someone a critical priority, then you have to enrich them"

**Implementation:**
- Check priority tag
- If critical → Run full enrichment (web + LinkedIn + due diligence)
- If non-critical → Basic only (domain analysis, no LinkedIn/web search)

---

## Integration Architecture (Final)

### Daily Flow (Weekdays 8am)

```
1. Meeting Monitor Wakes Up (8:00 AM ET)
    ↓
2. Scan Google Calendar (today's meetings with V-OS tags)
    ↓
3. For each external meeting:
    ├─ Check if stakeholder profile exists
    │   ├─ Exists → Load tags, skip enrichment
    │   └─ New → Discover contact via email scanner
    │             ↓
    │         Check priority (auto-assigned by stakeholder type)
    │             ├─ Critical → Full enrichment (web + LinkedIn + research)
    │             └─ Non-critical → Basic enrichment (domain only)
    │             ↓
    │         Create stakeholder profile with tags
    │             ↓
    │         Add to CRM staging
    ↓
4. Generate Daily Meeting Prep Digest
    ├─ Use stakeholder tags for context
    ├─ Include enrichment highlights (if critical)
    └─ Format as existing BLUF digest
    ↓
5. Save to N5/digests/daily-meeting-prep-{date}.md
    ↓
6. SMS Notification: "Your daily digest is ready"
```

---

### Weekly Flow (Sundays 6pm)

```
1. Weekly Stakeholder Review Triggers (6:00 PM ET)
    ↓
2. Email Scanner Scans Gmail (past 7 days)
    ├─ Find meeting-related emails
    ├─ Extract external participants
    └─ Filter: new contacts only (not already profiled)
    ↓
3. For each new contact:
    ├─ Basic enrichment (domain analysis)
    ├─ Infer stakeholder type
    ├─ Check priority (auto-assigned)
    │   ├─ Critical → Full enrichment (web + LinkedIn + research)
    │   └─ Non-critical → Basic only
    ↓
4. Pattern Analyzer Suggests Tags
    ├─ Analyze email patterns (frequency, tone, keywords)
    ├─ Use enrichment data (LinkedIn, web search)
    ├─ Generate tag suggestions with confidence scores
    └─ Include reasoning and Careerspan relevance
    ↓
5. Generate Weekly Review Digest
    ├─ Compile new contacts (with enrichment)
    ├─ Compile updated contacts (tag changes)
    ├─ Format with confidence scores, reasoning
    └─ Include strategic insights (partnerships, competitive intel)
    ↓
6. Save to N5/digests/weekly-stakeholder-review-{date}.md
    ↓
7. Deliver via Scheduled Task Output
    ↓
8. SMS Notification: "Weekly stakeholder review ready"
    ↓
9. V Reviews & Approves Tags (within 3 days)
    ↓
10. Apply Verified Tags to Profiles
     ↓
11. Update CRM markdown (profiles updated)
```

---

## Migration Strategy (Lazy)

### Trigger: Contact Becomes Active

**Active = any of:**
- Email received from contact
- Meeting scheduled with contact
- V mentions contact in conversation
- Contact referenced in meeting notes

**When triggered:**
1. Check if profile has tags
   - Has tags → Skip
   - No tags → Run pattern analyzer + enrichment
2. Generate tag suggestions
3. Add to next weekly review (Sunday digest)
4. V approves tags
5. Tags applied to profile

**Implementation:**
- Meeting monitor checks for tags when processing meetings
- If no tags found → Flag for weekly review
- Email scanner marks "needs tagging" when discovering old contacts
- Weekly review includes "updated contacts" section (old contacts reactivated)

### Example: Fei Ma Profile

**Current state:** `Knowledge/crm/profiles/fei-ma-nira.md` (old format, no tags)

**If Fei emails V tomorrow:**
1. Email scanner detects Fei in Gmail thread
2. Checks: Does Fei have profile? → Yes (`Knowledge/crm/profiles/fei-ma-nira.md`)
3. Checks: Does profile have tags? → No
4. Marks: "Fei Ma — needs tagging (reactivated contact)"
5. Sunday review: Includes Fei with suggested tags based on old profile + new email context
6. V reviews: Approves tags
7. Profile updated: Tags added to existing `fei-ma-nira.md`

---

## Meeting Monitor Integration

### Current: Meeting Monitor (Phase 2B Priority 4)
**Script:** `N5/scripts/run_meeting_monitor.py`

**Flow:**
1. Scan Google Calendar for V-OS tagged meetings
2. Analyze Gmail threads for meeting participants
3. Create stakeholder profiles (basic format)
4. Generate meeting prep digest

### New: Integrated with Stakeholder Tagging

**Enhanced flow:**
1. Scan Google Calendar for V-OS tagged meetings
2. **NEW:** Check if stakeholder profile exists with tags
   - Exists with tags → Use tags in digest
   - Exists without tags → Add to weekly review for tagging
   - Doesn't exist → Email scanner discovers contact
3. **NEW:** Auto-enrich if critical priority
4. Create/update stakeholder profile **with tags**
5. Generate meeting prep digest **with stakeholder intelligence**

**Code changes needed:**
- `run_meeting_monitor.py`: Add stakeholder tag check
- `stakeholder_profile_manager.py`: Add tag inference call
- `meeting_prep_digest.py`: Use tags for context section

---

## CRM Sync Strategy (Deferred)

### Phase 1-3: Markdown CRM Only
**Source of truth:** Stakeholder profiles (`N5/records/meetings/{folder}/stakeholder_profile.md`)

**Query method:** Filesystem + grep
- Search by tag: `grep "#stakeholder:investor" N5/records/meetings/*/stakeholder_profile.md`
- Search by name: `grep "Sarah Chen" N5/records/meetings/*/stakeholder_profile.md`
- Simple, fast enough for <100 profiles

**No database sync yet**

---

### Phase 4: Database Sync (Later)
**When needed:** >100 profiles, complex queries, Howie integration API

**Sync strategy:**
- Read all stakeholder profiles
- Parse tags from markdown
- Insert/update records in `Knowledge/crm/crm.db`
- Keep profiles as canonical, database as cache

**Not urgent:** Current scale (<10 profiles) doesn't justify database overhead

---

## Enrichment Automation (Binary)

### Rule: Priority Determines Enrichment

**Critical priority (`#priority:critical`):**
- ✅ Run full enrichment: Web search + LinkedIn + deep research (if investor)
- ✅ Sources: Gmail + web + LinkedIn + due diligence dossier
- ✅ Time investment: 2-5 minutes per contact
- ✅ Auto-assigned to: Investors, advisors, customers

**Non-critical priority (`#priority:non-critical`):**
- ✅ Run basic enrichment only: Domain analysis
- ✅ Sources: Gmail metadata only
- ✅ Time investment: <5 seconds per contact
- ✅ Auto-assigned to: Job seekers, community, prospects, vendors

**V can override:**
- If V manually sets `#priority:critical` on any contact → Auto-enrich
- Example: V says "Weston is actually really important" → Change to critical → Enrichment triggers

---

## Implementation Checklist

### Phase 1B: Pattern Analyzer (This Week)
- [ ] Build pattern analyzer script
- [ ] Validate against 6 existing profiles
- [ ] Achieve >80% accuracy on tag suggestions
- [ ] Integrate with enrichment (critical = full, non-critical = basic)

### Phase 1C: Meeting Monitor Integration (This Week)
- [ ] Modify `run_meeting_monitor.py` to check for stakeholder tags
- [ ] Add tag-based enrichment trigger (critical → enrich)
- [ ] Update digest to use stakeholder intelligence
- [ ] Test with upcoming meetings

### Phase 2A: Daily Digest (This Week)
- [ ] Schedule daily task (weekdays 8am ET)
- [ ] Brief format for today's meetings only
- [ ] SMS notification integration
- [ ] Test Monday morning

### Phase 2B: Weekly Review (Next Week)
- [ ] Build weekly review generator
- [ ] Compile new/updated contacts (past 7 days)
- [ ] Format with tag suggestions + enrichment
- [ ] Schedule Sunday 6pm ET
- [ ] SMS notification integration

### Phase 3: Tag Application (Next Week)
- [ ] Build feedback parser (approve, edit, skip)
- [ ] Apply verified tags to profiles
- [ ] Mark as reviewed with timestamp

### Phase 4: Deferred
- [ ] CRM database sync (when >100 profiles)
- [ ] Howie integration API
- [ ] Advanced query interface

---

## File Organization Strategy

### Current: Two Profile Locations
1. **NEW format:** `N5/records/meetings/{date}_{name}-{org}/stakeholder_profile.md` (with tags)
2. **OLD format:** `Knowledge/crm/profiles/{name}.md` (no tags)

### Strategy: Gradual Consolidation

**Rule:** New profiles use NEW format (in meetings folder)

**OLD profiles:**
- Leave as-is until contact reactivates
- When reactivated: Add tags section to existing file
- Don't move/rename (preserve history)
- Use filesystem location as-is

**Result:** Mixed formats okay (both work, both searchable)

**Future:** Eventually all active contacts will have tags (through natural reactivation)

---

## Integration Points Map

### Stakeholder Tagging → Meeting Monitor
**Direction:** Stakeholder profiles feed context to meeting prep

**Data flow:**
- Meeting monitor reads stakeholder profile
- Extracts tags (priority, stakeholder type, relationship, context)
- Uses in digest: "Meeting with Sarah Chen (Investor, Critical priority, New relationship)"

**File:** `meeting_prep_digest.py` reads tags from stakeholder profiles

---

### Email Scanner → Stakeholder Tagging
**Direction:** Email scanner discovers contacts, triggers tagging

**Data flow:**
- Email scanner finds external participants
- Creates staged contact (basic enrichment)
- Pattern analyzer suggests tags
- Weekly review presents to V
- V approves → Tags applied to profile

**File:** `scan_meeting_emails.py` → `pattern_analyzer.py` → `weekly_review_generator.py`

---

### Stakeholder Tagging → Daily Digest
**Direction:** Tags determine meeting context and priority

**Data flow:**
- Daily digest checks meeting participants
- Loads stakeholder profiles for each
- Displays tags in context section
- Critical priority → Highlight in digest

**File:** Daily digest script (8am weekdays) reads from stakeholder profiles

---

### Weekly Review → Tag Application
**Direction:** V's feedback updates profiles

**Data flow:**
- V reviews weekly digest
- Provides approval/edits (via response)
- Feedback parser extracts decisions
- Tags applied to profiles automatically
- Profiles marked as "reviewed" with timestamp

**File:** `apply_verified_tags.py` (to be built, Phase 3)

---

## Scheduling Strategy

### Daily (Weekdays 8:00 AM ET)
**Task:** Meeting prep digest (brief, today only)  
**RRULE:** `FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8;BYMINUTE=0`  
**Notification:** SMS text "Your daily digest is ready"

**Instruction:**
```
Generate daily meeting prep digest for today's meetings. 
Use existing meeting prep format with BLUF structure.
Include stakeholder intelligence from tags where available.
Send SMS notification when complete.
```

---

### Weekly (Sundays 6:00 PM ET)
**Task:** Stakeholder review + weekly planning  
**RRULE:** `FREQ=WEEKLY;BYDAY=SU;BYHOUR=18;BYMINUTE=0`  
**Notification:** SMS text "Weekly stakeholder review ready"

**Instruction:**
```
Generate weekly stakeholder review digest.
Scan Gmail for past 7 days, discover new external contacts.
Run full enrichment on critical priority contacts.
Suggest tags with confidence scores and reasoning.
Compile week-ahead strategic view (meetings, follow-ups, priorities).
Send SMS notification when complete.
```

---

## Priority Binary System (Critical vs. Non-Critical)

### Critical Priority (Auto-Enrich)
**Auto-assigned to:**
- `#stakeholder:investor` (always)
- `#stakeholder:advisor` (always)
- `#stakeholder:customer` (always)

**Manual assignment:**
- V says "This partner is critical" → Tag updated → Enrichment triggers

**Enrichment:**
- ✅ Web search (company + person background)
- ✅ LinkedIn profile (authenticated access)
- ✅ Deep research dossier (for investors)
- ✅ Strategic fit scoring
- ✅ Careerspan relevance assessment

**Time:** 2-5 minutes per contact

---

### Non-Critical Priority (Basic Only)
**Auto-assigned to:**
- `#stakeholder:job_seeker`
- `#stakeholder:community`
- `#stakeholder:prospect`
- `#stakeholder:vendor`
- `#stakeholder:networking_contact`
- `#stakeholder:partner:*` (unless V overrides)

**Enrichment:**
- ✅ Domain analysis (VC firm detection, company inference)
- ❌ No web search
- ❌ No LinkedIn
- ❌ No deep research

**Time:** <5 seconds per contact

---

## Migration Timeline

### This Week: Integration
- **Monday-Tuesday:** Build pattern analyzer, integrate with meeting monitor
- **Wednesday:** Test daily digest (8am) with existing profiles
- **Thursday-Friday:** Refine and validate

### Next Week: Automation
- **Sunday (Oct 20):** First automated weekly review (6pm)
- **Monday (Oct 21):** First automated daily digest (8am)
- **Week of Oct 21:** Monitor, refine, optimize

### Ongoing: Lazy Migration
- When old contacts reactivate → Add tags
- Natural migration over time (no forced migration)
- Eventually all active contacts will have tags

---

## File Structure (Final)

```
N5/
├── config/
│   ├── tag_mapping.json ✅ (hashtag ↔ bracket)
│   ├── tag_taxonomy.json ✅ (full catalog)
│   ├── stakeholder_rules.json ✅ (business rules)
│   └── enrichment_settings.json ✅ (enrichment config)
├── scripts/
│   ├── scan_meeting_emails.py ✅ (email scanner)
│   ├── enrich_stakeholder_contact.py ✅ (enrichment module)
│   ├── pattern_analyzer.py ⏳ (NEXT — tag inference)
│   ├── weekly_review_generator.py ⏳ (NEXT — digest builder)
│   ├── apply_verified_tags.py ⏳ (tag application)
│   └── run_meeting_monitor.py ✅ (existing, needs integration)
├── records/
│   ├── meetings/
│   │   └── {date}_{name}-{org}/
│   │       └── stakeholder_profile.md (with tags)
│   └── crm/
│       └── staging/ (discovered contacts, pending review)
├── stakeholders/ (OLD format, migrate when active)
│   └── {name}.md (no tags, update when reactivated)
└── docs/
    ├── TAG-TAXONOMY-MASTER.md ✅ (single source of truth)
    ├── INTEGRATION-MIGRATION-STRATEGY.md ✅ (this doc)
    └── PHASE-1A-COMPLETE.md ✅ (status)
```

---

## Success Criteria

### Integration Success
- ✅ Meeting monitor uses stakeholder tags in digest
- ✅ Daily digest (8am) includes stakeholder intelligence
- ✅ Weekly review (6pm Sunday) discovers new contacts
- ✅ Tags applied automatically after V's approval

### Migration Success
- ✅ Old profiles remain usable (no data loss)
- ✅ New tags added when contacts reactivate
- ✅ No forced migration (lazy, on-demand)
- ✅ All active contacts eventually tagged

### Enrichment Success
- ✅ Critical priority → Full enrichment (100%)
- ✅ Non-critical → Basic only (100%)
- ✅ Enrichment time: <5 min per critical contact
- ✅ LinkedIn access rate: >70% for critical contacts

---

## Next Steps (In Order)

1. ✅ **V approves strategy** (this document)
2. ⏳ **Build pattern analyzer** (Phase 1B)
3. ⏳ **Integrate with meeting monitor** (Phase 1C)
4. ⏳ **Test daily digest** (Wednesday 8am)
5. ⏳ **Build weekly review generator** (Phase 2)
6. ⏳ **Schedule tasks** (daily 8am, weekly Sunday 6pm)
7. ⏳ **First automated cycle** (next week)

---

**Status:** Integration and migration strategy complete, ready to build pattern analyzer
