# Howie ↔ Zo Implementation Plan — FINAL

**Date:** 2025-10-11  
**Version:** 3.0 (Based on V's feedback)  
**Status:** Ready to execute

---

## KEY DECISIONS FROM V

### 1. Tag System: Use V-OS Tags Everywhere ✅
- **Decision:** N5 adopts Howie's V-OS tag format (not translation layer)
- **Rationale:** Reduces cognitive load, single system to remember
- **Change:** N5 calendar tags switch from `#stakeholder:*` format to `[LD-*]` format

### 2. Communication Protocol ✅
- **Howie → Zo:** One-directional for now, auto-forward ALL scheduled meetings
- **Zo → Howie:** Not yet enabled (future phase)
- **Tag-based forwarding:** Use `[FWD-Z]*` for explicit email content forwarding (not just meetings)

### 3. Research Timing ✅
- **Immediate trigger:** When Howie schedules meeting, Zo starts research immediately
- **Check existing records first:** Don't duplicate research for known contacts
- **Progressive enhancement:** Basic brief immediately, enhanced closer to meeting

### 4. Priority System ✅
- **Binary:** Critical vs Non-critical
- **Mapping:** `!!` and `[LD-INV]` = critical, everything else = non-critical

---

## IMPLEMENTATION PHASES

### Phase 1: Core N5 Updates (This Week)
**Duration:** 2-3 hours  
**Goal:** N5 understands V-OS tags and can process Howie-scheduled meetings

#### 1.1 Update N5 Tag Extraction (30 min)
- [ ] Update `meeting_prep_digest.py` tag extraction to recognize V-OS format
- [ ] Add new tag categories: status, schedule, coordination, accommodation, availability, follow-up
- [ ] Update constants with all V-OS tag types

#### 1.2 Update Priority System (15 min)
- [ ] Simplify to binary: `critical` vs `non-critical`
- [ ] Map `!!` and `[LD-INV]` to critical
- [ ] Update prep action logic

#### 1.3 Update BLUF Generation (30 min)
- [ ] Use `[LD-*]` tags for stakeholder-specific BLUFs
- [ ] Add accommodation level context (`[A-2]` = understand their needs)
- [ ] Add weekend meeting flags

#### 1.4 Special Event Filtering (20 min)
- [ ] Skip `[DW]` blocks (deep work)
- [ ] Skip "Meeting Buffer" events
- [ ] Skip `[OFF]` (postponed) events
- [ ] Skip `[TERM]` (inactive) events

#### 1.5 Testing (30 min)
- [ ] Test with mock calendar events using V-OS tags
- [ ] Verify tag extraction works
- [ ] Verify BLUF generation adapts to tags
- [ ] Dry-run full digest

**Deliverable:** N5 can read and process V-OS tags in calendar descriptions

---

### Phase 2: Howie Integration Setup (Next Week)
**Duration:** 1-2 hours  
**Goal:** Howie can populate N5-readable tags, notify Zo of new meetings

#### 2.1 Howie Calendar Description Template (15 min)
Create instructions for Howie to populate calendar descriptions:

```
When scheduling a meeting, populate the Google Calendar event description with:

[Active V-OS tags from email thread]

Purpose: [Brief description from email context]

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

[Conferencing details]
[Rescheduling links]
```

**Example:**
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline and requirements

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.
```

#### 2.2 Howie → Zo Auto-Forward (30 min)
- [ ] Set up Howie to auto-forward ALL scheduled meeting confirmations to va@zo.computer
- [ ] Email format: `[HOWIE→ZO] [NOTIFY] Meeting Scheduled: [Person] x Vrijen - [Date/Time]`
- [ ] Include: Person name, email, date/time, V-OS tags, any context from thread

#### 2.3 Tag-Based Content Forwarding (15 min)
- [ ] Set up Howie to forward emails tagged `[FWD-Z]*` to va@zo.computer
- [ ] Use for substantive email content (not just scheduling logistics)
- [ ] Email format: `[HOWIE→ZO] [CONTEXT] Email Content: [Subject]`

#### 2.4 Zo Email Processing (30 min)
- [ ] Set up filter/rule to recognize `[HOWIE→ZO]` emails
- [ ] Auto-process meeting notifications:
  - Extract person name, email, date/time
  - Trigger immediate research if new contact
  - Update stakeholder database if existing contact
- [ ] Auto-process content forwards:
  - Save to appropriate knowledge location
  - Extract key points
  - Link to relevant stakeholders/meetings

**Deliverable:** Howie → Zo communication pipeline active and processing

---

### Phase 3: Immediate Research Pipeline (Week 3)
**Duration:** 2-3 hours  
**Goal:** Zo automatically researches new contacts when meetings scheduled

#### 3.1 Research Trigger System (1 hour)
- [ ] When `[HOWIE→ZO]` meeting notification received:
  1. Check if person exists in stakeholder database
  2. If new: Trigger full research (LinkedIn, company, past emails)
  3. If existing: Update last interaction date, pull existing brief
  4. Save research to knowledge base with timestamp

#### 3.2 Existing Records Check (30 min)
- [ ] Search patterns:
  - Email address (exact match)
  - Name variations (John Smith = Jonathan Smith)
  - Company domain patterns
- [ ] If found: Pull existing profile, check recency
- [ ] If >30 days old: Refresh research (recent news, company updates)

#### 3.3 Progressive Brief Enhancement (1 hour)
- [ ] Immediate (when scheduled):
  - Basic bio, company, past interactions
  - Save as draft brief
- [ ] T-5 days:
  - Add recent company news
  - Add specific talking points based on V's current priorities
- [ ] T-2 days:
  - Finalize BLUF based on latest context
  - Add prep actions
- [ ] Morning-of:
  - Last-minute updates (overnight news, new emails)
  - Final brief ready

**Deliverable:** Zero manual research required, briefs auto-generated and auto-enhanced

---

### Phase 4: Stakeholder Database (Week 4)
**Duration:** 3-4 hours  
**Goal:** Maintain CRM-like profiles for all contacts, inform Howie's scheduling

#### 4.1 Stakeholder Profile Schema (1 hour)
Create standardized profile structure:

```yaml
name: John Smith
email: john@example.com
company: Example Corp
role: VP Engineering
stakeholder_type: [LD-NET]  # From first meeting tag
first_contact: 2025-10-11
last_contact: 2025-10-11
interaction_count: 1
preferred_days: [Tuesday, Thursday]  # Learned from patterns
preferred_time: afternoon  # Learned from patterns
key_topics: [hiring, technical recruiting]
relationship_strength: warm  # cold/warm/hot
notes: "Met at conference, interested in Careerspan for his team"
meetings:
  - date: 2025-10-11
    tags: [LD-NET] [D5] *
    outcome: positive
    follow_up_needed: yes
```

#### 4.2 Profile Auto-Creation (1 hour)
- [ ] When new meeting scheduled → Create profile automatically
- [ ] Populate from:
  - Email signature (name, title, company)
  - LinkedIn research (role, background)
  - Initial email thread context
- [ ] Save to `/home/workspace/Knowledge/stakeholders/[company]/[name].md`

#### 4.3 Profile Auto-Update (1 hour)
- [ ] After each meeting → Update profile:
  - Increment interaction count
  - Update last_contact date
  - Add meeting notes (if V provides)
  - Adjust relationship_strength based on outcomes
- [ ] Pattern learning:
  - Track which days/times meetings happened
  - Identify preferred scheduling patterns
  - Save for future reference

#### 4.4 Howie Access (Future)
When ready for bi-directional communication:
- [ ] Howie can query: "What do we know about John Smith?"
- [ ] Zo responds with profile summary
- [ ] Howie uses this to personalize scheduling responses
- [ ] Example: "I see you last connected with Vrijen 3 months ago about hiring. Looking forward to your follow-up!"

**Deliverable:** Self-building stakeholder database that learns over time

---

### Phase 5: Relationship Warming Engine (Month 2)
**Duration:** 2-3 hours  
**Goal:** Proactive relationship maintenance, prevent contacts from going cold

#### 5.1 Contact Tracking (1 hour)
- [ ] Track last contact date for each stakeholder
- [ ] Define warming thresholds by stakeholder type:
  - Investors: 30 days
  - Active customers: 21 days
  - Partners: 45 days
  - Community: 60 days
  - Prospects: 90 days

#### 5.2 Warming Suggestions (1 hour)
- [ ] Weekly digest to V:
  - "Contacts needing touch-base:"
  - List names, last contact date, suggested approach
  - Draft check-in messages for each
- [ ] Example:
  ```
  John Smith (Example Corp) - Last contact: 45 days ago
  Suggested: "Hi John, been a while since we discussed hiring. 
  How's the team building going? Would love to catch up."
  ```

#### 5.3 Howie Integration (1 hour)
- [ ] When V approves warming outreach:
  - Forward to Howie with instructions
  - Howie sends check-in email
  - If response, Howie offers to schedule catch-up
  - If no response, Howie follows up after X days (per `[F-X]` rules)

**Deliverable:** No relationship goes cold unintentionally

---

## IMMEDIATE PRIORITY: Phase 1 (This Session)

Let's execute Phase 1 now:

### Files to Update

1. **`N5/scripts/meeting_prep_digest.py`**
   - Lines 31-48: Update tag constants to V-OS format
   - Lines 75-103: Update tag extraction regex
   - Lines 254-275: Update BLUF generation
   - Lines 329-344: Update prep actions
   - Add special event filtering

2. **`N5/docs/calendar-tagging-system-COMPLETE.md`**
   - Update all examples to use V-OS tags
   - Update taxonomy section
   - Add Howie integration notes

3. **`N5/docs/calendar-tagging-system.md`**
   - Update user guide with V-OS tags
   - Add Howie coordination section

4. **`N5/commands/meeting-prep-digest.md`**
   - Update tag reference table
   - Add Howie integration instructions

---

## TESTING CHECKLIST

### Phase 1 Testing
- [ ] Create mock calendar event with `[LD-INV] *` tag
- [ ] Run `meeting_prep_digest.py --dry-run`
- [ ] Verify tag extraction works
- [ ] Verify BLUF says "investor meeting"
- [ ] Verify prep actions include "Protect this time block"

### Phase 2 Testing
- [ ] Have Howie schedule test meeting
- [ ] Verify calendar description has V-OS tags
- [ ] Verify Zo receives notification email
- [ ] Verify Zo processes notification correctly

### Phase 3 Testing
- [ ] New contact meeting scheduled
- [ ] Verify Zo auto-starts research
- [ ] Verify brief generated before meeting
- [ ] Verify brief enhances over time

---

## SUCCESS METRICS

**Phase 1 (Week 1):**
- ✅ 100% of V-OS tags recognized by N5
- ✅ Meeting prep digests use V-OS tag context

**Phase 2 (Week 2):**
- ✅ 100% of Howie-scheduled meetings notify Zo
- ✅ Calendar descriptions populated with V-OS tags

**Phase 3 (Week 3):**
- ✅ 100% of new contacts auto-researched
- ✅ Zero meetings without prep brief

**Phase 4 (Week 4):**
- ✅ Stakeholder database has 100% coverage
- ✅ Profiles auto-update after meetings

**Phase 5 (Month 2):**
- ✅ Zero high-priority contacts go >threshold without touchpoint
- ✅ Warming outreach coordinated between Zo and Howie

---

## QUESTIONS RESOLVED

1. ✅ **Tag system:** Use V-OS tags everywhere (no translation)
2. ✅ **Auto-forward:** Yes, all scheduled meetings
3. ✅ **Research timing:** Immediate + progressive enhancement
4. ✅ **Priority:** Binary (critical vs non-critical)

---

## READY TO PROCEED?

**Next action:** Execute Phase 1 (core N5 updates)

Shall I proceed with updating the meeting_prep_digest.py script with V-OS tag support?
