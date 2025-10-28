# N5 Intelligence Layer - Architecture v1.0

**Date:** 2025-10-12  
**Status:** Design specification based on V's requirements  
**Purpose:** Comprehensive relationship intelligence system

---

## Executive Summary

**Mission:** Never let a deal slip through the cracks.

**Core capabilities:**
1. **Relationship health monitoring** - Auto-detect slipping opportunities
2. **Auto-drafted holding emails** - "It's been a week, I'll get back to you this week"
3. **Sunday evening strategic planning** - Weekly relationship review (10 min)
4. **Daily morning tactical prep** - Meeting intelligence (10 min)
5. **Post-meeting ingestion** - Verbal vomit → structured intelligence

---

## V's Requirements (Direct from Discovery)

### Use Case Priority
1. **Post-meeting follow-up** - Capture context, track commitments
2. **Weekly relationship review** - Who needs attention, who's slipping
3. **Relationship health monitoring** - Flag opportunities going cold
4. **Pre-meeting prep** - Context for upcoming meetings
5. **Opportunity identification** - Surface high-value connections

### Pain Points
- Follow-up emails burn time
- Forgetting active dialogues → deals slip through fingers

### Must-Have Features
- **Surface ongoing deals/interactions** - Nothing slips
- **Auto-draft holding emails** - "Been a week, will get back this week"
- **Binary priority tagging** - Critical vs non-critical
- **Sunday evening digest** - Strategic planning for week (10 min)
- **Daily morning digest** - Tactical meeting prep (10 min, lightweight)
- **Two separate digests** - Calendar vs stakeholder intelligence

### Current Workflow
**Pre-meeting prep:**
- LinkedIn profile
- Crunchbase
- Quick news search
- Check mutuals against intelligence list

**Post-meeting:**
- Networking ingestion (verbal vomit)
- System extracts and organizes

### Enrichment Priority
1. **LinkedIn** (critical) - First step
2. **Deep research** (critical for investors) - Before first meeting
3. **Company research** (critical) - Funding, alignment with Careerspan
4. **News mentions** (nice to have)

### Automation
- **Tag confidence:** 90% threshold for auto-apply
- **Tag confirmation:** Must be confirmed (no silent application)
- **Everything else:** Can be automated
- **Boundaries:** Figure out iteratively

### Data & Privacy
- **Historical data:** Keep everything, timestamp properly, prune as needed
- **Sensitivity:** Nothing too sensitive now, V will flag if needed
- **Contact deduplication:** Primary email as key, auxiliary emails section

### Notifications
- **SMS:** Emergency/blocking issues only
- **In-app:** Everything else
- **Zo discretion:** Always ping if critical blocker

---

## Architectural Decision: Primary Contact Record

### Recommendation: Hybrid Architecture

**Single source of truth:** `N5/intelligence/contacts/{email_hash}.json`

**Why:**
1. **Centralized:** All systems read/write from same place
2. **Fast queries:** Can build indexes for lookups
3. **Git-friendly:** JSON format, human-readable
4. **Deduplication-ready:** One file per unique contact
5. **Cross-system sync:** Meeting transcripts, emails, calendar all update same record

**Supporting records:**
- Meeting transcripts at `N5/records/meetings/{meeting_id}/` (links to intelligence layer)
- Stakeholder profiles are generated views (derived from intelligence layer)
- Weekly/daily digests are views (query intelligence layer)

**Data flow:**
```
Gmail API → Intelligence Layer
Calendar API → Intelligence Layer
Meeting Transcripts → Intelligence Layer
Post-meeting ingestion → Intelligence Layer

Intelligence Layer → Weekly digest
Intelligence Layer → Daily digest
Intelligence Layer → Stakeholder profiles
Intelligence Layer → Howie context API
```

**Benefits:**
- Single update propagates everywhere
- No sync conflicts
- No duplicate enrichment
- Consistent state across all systems

---

## Contact Record Schema

```json
{
  "id": "uuid-v4",
  "identity": {
    "primary_email": "sarah@acmeventures.com",
    "auxiliary_emails": ["sarah.chen@gmail.com"],
    "name": {
      "full": "Sarah Chen",
      "first": "Sarah",
      "last": "Chen",
      "confidence": 0.95
    },
    "phone": "+1-555-0123",
    "linkedin_url": "https://linkedin.com/in/sarahchen",
    "crunchbase_url": "https://crunchbase.com/person/sarah-chen"
  },
  
  "tags": {
    "verified": {
      "#stakeholder:investor": {
        "added_at": "2025-10-12T14:00:00Z",
        "added_by": "auto",
        "confidence": 0.95
      },
      "#priority:critical": {
        "added_at": "2025-10-12T14:00:00Z",
        "added_by": "auto_inheritance",
        "confidence": 1.0
      }
    },
    "suggested": {
      "#context:venture_capital": {
        "suggested_at": "2025-10-12T14:00:00Z",
        "confidence": 0.88,
        "reasoning": "LinkedIn shows Partner at VC firm"
      }
    }
  },
  
  "company": {
    "name": "Acme Ventures",
    "domain": "acmeventures.com",
    "role": "Partner",
    "industry": "venture_capital",
    "last_updated": "2025-10-12T14:00:00Z"
  },
  
  "relationship": {
    "status": "active",  // new, warm, active, cold, dormant
    "priority": "critical",  // critical, non-critical (binary per V's request)
    "first_contact": "2025-10-08T00:00:00Z",
    "last_contact": "2025-10-11T18:30:00Z",
    "last_email_from_v": "2025-10-11T18:30:00Z",
    "last_email_from_them": "2025-10-11T12:00:00Z",
    "last_meeting": "2025-10-14T14:00:00Z",
    "days_since_contact": 1,
    "email_frequency_30d": 5,
    "momentum": "heating_up",  // heating_up, stable, cooling_down, cold
    "health_status": "healthy",  // healthy, at_risk, slipping, lost
    "needs_followup": true,
    "followup_reason": "Been 7 days since their last email",
    "followup_urgency": "medium"
  },
  
  "enrichment": {
    "linkedin": {
      "fetched_at": "2025-10-12T14:00:00Z",
      "profile_url": "https://linkedin.com/in/sarahchen",
      "current_role": "Partner",
      "current_company": "Acme Ventures",
      "experience": [
        {
          "title": "Partner",
          "company": "Acme Ventures",
          "duration": "2020-Present"
        }
      ],
      "education": [
        {
          "school": "Stanford GSB",
          "degree": "MBA"
        }
      ],
      "connections": 500,
      "mutual_connections": ["John Doe", "Jane Smith"]
    },
    "crunchbase": {
      "fetched_at": "2025-10-12T14:00:00Z",
      "firm_aum": "$500M",
      "fund_info": "Fund III - $200M (2024)",
      "investment_thesis": "Early-stage B2B SaaS, 50% future-of-work/HR tech",
      "portfolio_companies": 25,
      "notable_investments": ["CompanyA", "CompanyB"]
    },
    "deep_research": {
      "fetched_at": "2025-10-12T14:00:00Z",
      "strategic_fit_score": 4,  // 1-5 scale
      "careerspan_alignment": "Strong thesis match, active in HR tech",
      "recent_activity": "Led $5M seed in competing HR tech (June 2024)",
      "timing": "Excellent - Fund III 40% deployed, actively investing",
      "risks": ["Portfolio includes competitor"],
      "opportunities": ["Thesis alignment", "3 portfolio companies in HR tech"],
      "summary_path": "N5/records/research/sarah-chen-acme-ventures.md"
    },
    "news": {
      "fetched_at": "2025-10-12T14:00:00Z",
      "recent_mentions": [
        {
          "title": "Acme Ventures announces Fund III",
          "url": "https://...",
          "date": "2024-06-01",
          "summary": "..."
        }
      ]
    },
    "last_enriched": "2025-10-12T14:00:00Z",
    "enrichment_level": "deep"  // basic, standard, deep
  },
  
  "email_history": {
    "total_threads": 3,
    "total_emails": 5,
    "last_30_days": 5,
    "topics": ["fundraising", "deck review", "scheduling"],
    "threads": [
      {
        "subject": "Re: Careerspan Series A Discussion",
        "last_date": "2025-10-11T12:00:00Z",
        "email_count": 3,
        "awaiting_response_from": "v",
        "days_waiting": 1,
        "snippet": "Thanks for the deck, couple questions..."
      }
    ]
  },
  
  "meetings": [
    {
      "date": "2025-10-14T14:00:00Z",
      "calendar_event_id": "event_123",
      "meeting_type": "discovery",
      "transcript_path": "N5/records/meetings/2025-10-14_sarah-chen-acme/",
      "smart_blocks_extracted": true,
      "commitments_tracked": [
        {
          "who": "v",
          "what": "Send updated deck with unit economics",
          "due": "2025-10-18",
          "status": "pending"
        }
      ]
    }
  ],
  
  "deals": [
    {
      "id": "deal_001",
      "name": "Acme Ventures - Series A Discussion",
      "stage": "initial_conversation",  // initial_conversation, active_dialogue, awaiting_response, stalled, closed_won, closed_lost
      "health": "healthy",  // healthy, at_risk, slipping
      "last_activity": "2025-10-11T12:00:00Z",
      "next_action": "V to send updated deck",
      "next_action_due": "2025-10-18",
      "days_since_activity": 1,
      "momentum": "positive"
    }
  ],
  
  "auto_drafted_emails": {
    "holding_email_needed": true,
    "last_suggested": "2025-10-12T14:00:00Z",
    "draft": {
      "subject": "Re: Careerspan Series A Discussion",
      "body": "Hi Sarah,\n\nIt's been a week since we last connected. I wanted to let you know I'm working on the updated deck with unit economics and will get it to you by end of this week.\n\nThanks for your patience!\n\nVrijen",
      "confidence": 0.85,
      "trigger_reason": "7 days since their last email, V hasn't responded"
    }
  },
  
  "metadata": {
    "created_at": "2025-10-08T00:00:00Z",
    "updated_at": "2025-10-12T14:00:00Z",
    "last_reviewed_by_v": "2025-10-12T14:00:00Z",
    "data_sources": ["gmail", "calendar", "linkedin", "crunchbase", "deep_research"],
    "review_status": "reviewed",  // pending, reviewed, archived
    "is_active": true,
    "notes": "Promising investor, strong Careerspan fit"
  }
}
```

---

## System Architecture

### Core Modules

**1. Contact Manager** (`N5/scripts/intelligence/contact_manager.py`)
- CRUD operations on contact records
- Deduplication logic
- Identity resolution
- Contact merging

**2. Relationship Monitor** (`N5/scripts/intelligence/relationship_monitor.py`)
- Track relationship health
- Detect slipping opportunities
- Flag at-risk deals
- Auto-draft holding emails
- Momentum analysis

**3. Enrichment Engine** (`N5/scripts/intelligence/enrichment_engine.py`)
- LinkedIn scraping
- Crunchbase lookup
- Deep research orchestration
- News monitoring
- Caching and TTL management

**4. Email Analyzer** (`N5/scripts/intelligence/email_analyzer.py`)
- Gmail API integration
- Extract email threads
- Topic classification
- Response tracking (who's waiting for whom)
- Frequency analysis

**5. Meeting Intelligence** (`N5/scripts/intelligence/meeting_intelligence.py`)
- Pre-meeting prep generation
- Post-meeting ingestion
- Commitment extraction
- Follow-up tracking

**6. Digest Generator** (`N5/scripts/intelligence/digest_generator.py`)
- Sunday strategic digest
- Daily tactical digest
- Template rendering
- Action item prioritization

**7. Tag Manager** (`N5/scripts/intelligence/tag_manager.py`)
- Tag suggestion engine
- Confidence scoring
- Auto-inheritance rules
- Hashtag ↔ bracket translation
- Tag verification workflow

**8. Deal Tracker** (`N5/scripts/intelligence/deal_tracker.py`)
- Track ongoing deals/opportunities
- Stage management
- Health monitoring
- Next action tracking

---

## File Structure

```
N5/
├── intelligence/
│   ├── contacts/                    # Primary contact records
│   │   ├── {email_hash}.json       # One file per contact
│   │   └── index.json               # Fast lookup index
│   ├── cache/                       # Enrichment cache
│   │   ├── linkedin/
│   │   ├── crunchbase/
│   │   └── news/
│   ├── relationships/               # Relationship tracking logs
│   │   └── relationship_log.jsonl  # Time-series data
│   ├── deals/                       # Deal tracking
│   │   └── deals.jsonl             # Active deals log
│   └── auto_drafts/                # Auto-drafted emails
│       └── pending_drafts.json
│
├── digests/
│   ├── weekly-relationship-review-{date}.md
│   ├── daily-meeting-prep-{date}.md
│   └── weekly-summary-{date}.md  # Existing calendar digest
│
├── scripts/
│   └── intelligence/
│       ├── contact_manager.py
│       ├── relationship_monitor.py
│       ├── enrichment_engine.py
│       ├── email_analyzer.py
│       ├── meeting_intelligence.py
│       ├── digest_generator.py
│       ├── tag_manager.py
│       ├── deal_tracker.py
│       └── post_meeting_ingestion.py  # New: verbal vomit processor
│
├── config/
│   ├── enrichment_settings.json
│   ├── relationship_thresholds.json  # When to flag as at-risk, etc.
│   └── auto_draft_templates.json     # Email templates
│
└── records/
    ├── meetings/                     # Existing structure
    └── research/                     # Deep research dossiers
```

---

## Data Flow Architecture

### Discovery Flow
```
Gmail API + Calendar API
    ↓
Email Analyzer discovers new contact
    ↓
Contact Manager creates record in intelligence/contacts/
    ↓
Enrichment Engine: LinkedIn → Crunchbase → (if investor) Deep Research
    ↓
Tag Manager suggests tags (90% confidence → auto-apply, else suggest)
    ↓
Relationship Monitor initializes tracking
    ↓
Contact appears in next Sunday digest for V's review
```

### Ongoing Monitoring Flow
```
Relationship Monitor (runs daily)
    ↓
Check all active contacts for:
- Days since last contact > threshold
- Awaiting response from V > 7 days
- Email frequency declining
    ↓
If slipping detected:
- Flag in relationship status
- Auto-draft holding email
- Add to "Needs Action" in Sunday digest
```

### Pre-Meeting Flow
```
Daily Digest Generator (runs 10am daily)
    ↓
Query intelligence/contacts/ for today's meetings
    ↓
For each meeting:
- Pull LinkedIn profile
- Pull Crunchbase data
- Check mutual connections
- Show email history
- List commitments from last meeting
- Show deal status
    ↓
Generate 10-min tactical digest
    ↓
Email to V
```

### Post-Meeting Flow
```
V does verbal vomit (via existing networking ingestion)
    ↓
Post-Meeting Ingestion script
    ↓
Extract:
- Smart blocks (action items, insights, hypotheses)
- Commitments (who owes what by when)
- Relationship state updates
- Deal stage updates
- Tag updates
    ↓
Update intelligence/contacts/{contact}.json
    ↓
Update deal status
    ↓
Schedule follow-up reminders
```

### Sunday Digest Flow
```
Digest Generator (Sunday 6pm ET)
    ↓
Query intelligence layer for:
1. Contacts needing action (slipping, awaiting response)
2. New contacts discovered this week
3. Deals with status changes
4. Upcoming meetings needing prep
5. Relationship momentum changes
    ↓
Generate markdown digest:
- Priority 1: Slipping opportunities (needs action NOW)
- Priority 2: Active deals (keep momentum)
- Priority 3: New contacts (review & verify tags)
- Priority 4: Week ahead preview
    ↓
Target: 10 minutes to review
    ↓
Email + SMS notification
```

---

## Key Features

### 1. Relationship Health Monitoring

**Health statuses:**
- **Healthy:** Regular contact, active dialogue
- **At risk:** Slowing frequency, approaching threshold
- **Slipping:** Past threshold, needs action
- **Lost:** No contact in 60+ days

**Thresholds (configurable):**
- Investor: 7 days → at risk, 14 days → slipping
- Partner: 14 days → at risk, 30 days → slipping  
- Advisor: 21 days → at risk, 45 days → slipping
- Community: 30 days → at risk, 60 days → slipping

**Triggers:**
- Days since last contact
- Days since V's last response
- Email frequency declining
- Deal stage stalled

---

### 2. Auto-Drafted Holding Emails

**Triggers:**
- Contact waiting for V's response > 7 days
- Active deal with no activity > 14 days
- Commitment deadline approaching (2 days out)

**Templates:**
```markdown
**Type: Acknowledgment (they're waiting for you)**

Hi {first_name},

It's been {days} since we last connected. I wanted to let you know I'm working on {what_you_owe} and will get it to you by {new_deadline}.

Thanks for your patience!

Vrijen

---

**Type: Check-in (deal going cold)**

Hi {first_name},

Wanted to check in on {deal_name}. It's been {days} since we last connected. 

Are you still interested in exploring this? Happy to schedule a quick call if helpful.

Vrijen

---

**Type: Commitment reminder (to self)**

⚠️ REMINDER: You committed to {action} for {contact_name} by {deadline} ({days_until} days).

Status: {current_status}

[Draft follow-up if overdue]
```

**Workflow:**
1. System detects trigger
2. Generates draft email
3. Saves to `intelligence/auto_drafts/pending_drafts.json`
4. Appears in Sunday digest as "Suggested Follow-ups"
5. V reviews, edits, and sends (or dismisses)

---

### 3. Deal Tracking

**Deal stages:**
- `initial_conversation` → First contact, exploratory
- `active_dialogue` → Back-and-forth, building relationship
- `awaiting_response` → Ball in someone's court
- `stalled` → No movement, at risk
- `closed_won` → Success!
- `closed_lost` → Not moving forward

**Deal health:**
- **Healthy:** Regular activity, clear next steps
- **At risk:** Activity slowing, unclear next steps
- **Slipping:** Stalled, needs intervention

**Tracking:**
- Last activity date
- Next action (who owes what)
- Days since activity
- Momentum (positive, neutral, negative)

---

### 4. Sunday Strategic Digest

**Format:**

```markdown
# Weekly Relationship Review — Oct 13-19, 2025

**Generated:** 2025-10-12 18:00 ET  
**Review time:** ~10 minutes  
**Action items:** 3 critical, 5 normal

---

## 🚨 CRITICAL: Needs Action Now

### 1. Sarah Chen (Acme Ventures) — Investor
**Status:** 🔴 SLIPPING  
**Issue:** Awaiting your response for 10 days  
**Last contact:** Oct 2 (their email: "Thanks for deck, couple questions...")  
**Deal:** Series A Discussion — Stage: Active dialogue  
**Next action:** Send updated deck with unit economics

**Auto-drafted holding email:**
> Hi Sarah,
>
> It's been 10 days since we last connected. I wanted to let you know I'm working on the updated deck with unit economics and will get it to you by end of this week.
>
> Thanks for your patience!

[Send] [Edit] [Dismiss] [Snooze 3 days]

---

### 2. Jake Thompson (FOHE) — Partner
**Status:** 🟡 AT RISK  
**Issue:** No contact in 18 days, deal momentum stalling  
**Last contact:** Sep 24 (meeting about Careerspan integration)  
**Deal:** FOHE Partnership — Stage: Awaiting response  
**Next action:** Follow up on integration timeline

**Suggested action:** Send check-in email

---

## 📊 Active Deals (Keep Momentum)

### 3. Fei (Nira) — Partner
**Status:** 🟢 HEALTHY  
**Momentum:** 📈 Heating up (10 emails this week, up from 3 last week)  
**Deal:** Nira Partnership — Stage: Active dialogue  
**Last contact:** Yesterday (discussing integration specs)  
**Next action:** V to review integration proposal by Oct 15

---

## 🆕 New Contacts This Week

### 4. Michael Rodriguez (Cornell Foundation)
**Discovered:** Oct 10 (email introduction from Michael Maher)  
**Suggested tags:**
- ✅ `#stakeholder:community` (95% confidence)
- ✅ `#priority:non-critical` (auto-apply)
- ⚠️ `#context:nonprofit` (85% confidence - **needs review**)

**LinkedIn:** [Profile](https://linkedin.com/in/michaelrodriguez)  
**Current role:** Director of Alumni Relations, Cornell Johnson Foundation  
**Enrichment:** Standard level (LinkedIn + web search)

**Action:** Review and verify tags → [Approve All] [Edit] [Skip]

---

## 📅 Week Ahead Preview

**Monday (3 meetings):**
- 3:00 PM - Michael Maher (Cornell) — [View prep](...)
- 4:00 PM - Elaine P (Exec coach) — [View prep](...)
- 6:00 PM - Immigrant Happy Hour (Community) — [View prep](...)

**Wednesday (2 meetings):**
- 2:00 PM - Sarah Chen (Acme Ventures) — **PREP NEEDED** (investor meeting)
- 5:00 PM - Alex Caveny (Advisor) — Regular coaching session

**Prep status:**
- ✅ 4 meetings fully prepped
- ⚠️ 1 meeting needs enrichment (Sarah Chen - run deep research?)

---

## 📈 Relationship Trends

**Heating up:**
- Fei (Nira): 10 emails this week (up from 3)
- Elaine P: Meeting scheduled + 8 emails

**Cooling down:**
- Jake (FOHE): No emails in 2+ weeks (was 5/week in Sept)

**Stable:**
- Alex Caveny: Regular 2x/month cadence maintained
- Michael Maher: Consistent monthly engagement

---

## 🎯 Action Summary

**Must do this week:**
1. ✅ Send deck to Sarah Chen (Acme) — **DUE: Oct 15**
2. ✅ Check in with Jake (FOHE) — **DUE: Oct 13**
3. ⚠️ Review Fei's integration proposal — **DUE: Oct 15**

**Can defer:**
- Review new contact tags (4 contacts)
- Schedule follow-up with community contacts

---

**Time estimate:** 8-12 minutes to review + take action

[Mark all reviewed] [Export to tasks] [Snooze until Monday]
```

---

### 5. Daily Tactical Digest

**Format:**

```markdown
# Daily Meeting Prep — Monday, Oct 14, 2025

**Generated:** 2025-10-14 06:00 ET  
**Review time:** ~5 minutes  
**Meetings today:** 3

---

## 3:00 PM - Michael Maher (Cornell Johnson)

**Context:** MBA Career Advisor, Cornell Johnson School  
**LinkedIn:** [Profile](https://linkedin.com/in/michaelmaher)  
**Tags:** `#stakeholder:community` `#relationship:warm` `#priority:non-critical`

**Last meeting:** Sep 15, 2025  
**Key insight:** Suggested alumni intro to 3 Cornell founders  
**Commitment from last time:** V to send use case examples (✅ SENT Sep 20)

**Recent emails (30 days):** 7  
**Last email:** Oct 2 - "Careerspan evaluation for Cornell alumni network"  
**Topics:** Alumni intros, Careerspan evaluation, Cornell partnership

**Deal status:** Cornell Partnership - Initial conversation stage  
**Momentum:** Stable

**Prep notes:**
- Follow up on alumni intro status
- Discuss Cornell partnership potential
- Ask about evaluation timeline

**Mutual connections:** 2 (Sarah Lee, John Kim)

---

## 4:00 PM - Elaine P (Executive Coach)

... [Similar format]

---

## 6:00 PM - Immigrant Happy Hour (Community Event)

... [Similar format]

---

**Total prep time:** 5-7 minutes
```

---

## MVP Implementation Plan

### Phase 1: Foundation (Week 1)
**Goal:** Core intelligence layer + relationship monitoring

**Deliverables:**
1. Contact Manager - CRUD operations, deduplication
2. Email Analyzer - Gmail integration, thread extraction
3. Relationship Monitor - Health tracking, slipping detection
4. Basic enrichment - LinkedIn + domain analysis
5. Contact record schema implementation
6. File structure setup

**Test with:** 10-20 existing contacts, validate accuracy

---

### Phase 2: Digests (Week 2)
**Goal:** Sunday strategic + daily tactical digests

**Deliverables:**
1. Digest Generator - Template rendering
2. Sunday digest - Slipping contacts, active deals, new contacts
3. Daily digest - Meeting prep with enrichment
4. Scheduled tasks (Sunday 6pm, Daily 6am)
5. Email delivery integration

**Test with:** First real digest for V's review

---

### Phase 3: Auto-Drafts + Deals (Week 2-3)
**Goal:** Never let deals slip

**Deliverables:**
1. Deal Tracker - Stage management, health monitoring
2. Auto-drafted holding emails - Templates, triggers
3. Post-meeting ingestion - Verbal vomit → structured data
4. Commitment tracking - Extract from meetings, set reminders
5. Sunday digest integration - Show suggested follow-ups

**Test with:** Real deals, validate draft quality

---

### Phase 4: Deep Enrichment (Week 3)
**Goal:** Rich intelligence for investor meetings

**Deliverables:**
1. Enrichment Engine - LinkedIn, Crunchbase, Deep Research
2. Deep research integration - Auto-trigger for investors
3. Careerspan alignment assessment - Strategic fit scoring
4. Mutual connection analysis
5. Enrichment caching (TTL management)

**Test with:** Upcoming investor meetings

---

### Phase 5: Tag Management (Week 3-4)
**Goal:** Auto-tagging with 90% confidence

**Deliverables:**
1. Tag Manager - Suggestion engine, confidence scoring
2. Auto-inheritance rules
3. Tag verification workflow
4. Hashtag ↔ bracket translation (for Howie)
5. Tag history tracking

**Test with:** New contacts, validate accuracy against V's feedback

---

### Phase 6: Integration & Polish (Week 4)
**Goal:** Connect all systems

**Deliverables:**
1. Weekly summary integration - Link to intelligence layer
2. Daily prep integration - Shared participant cache
3. Meeting transcript integration - Auto-update profiles
4. Howie context API (basic) - Query interface
5. System health monitoring
6. Documentation

**Test with:** Full end-to-end workflow

---

## Success Criteria

**Quantitative:**
- 0 deals slip through cracks (down from current ~30% slip rate?)
- 10-minute Sunday digest review time (target met)
- 5-minute daily digest review time (target met)
- 90%+ tag accuracy for high-confidence suggestions
- <24hr response time on slipping opportunities

**Qualitative:**
- V feels "in control" of relationships
- Never caught off-guard in meetings
- Proactive follow-ups (not reactive)
- Clear visibility into deal pipeline
- Reduced mental load on relationship management

**V's quote:** "I feel like the system is watching my back."

---

## Open Questions for V

### Question 1: Contact Record Location
**Recommendation:** `N5/intelligence/contacts/{email_hash}.json`

**Pros:**
- Centralized, single source of truth
- Fast lookups
- Git-friendly
- Easy to query

**Cons:**
- Different from current meeting-based structure

**Alternative:** Keep meeting-based stakeholder profiles, sync bidirectionally

**Your preference?**

---

### Question 2: Email Response Tracking
Should we track "ball in whose court"?
- Track who sent last email (V or them)
- Track if they're waiting for V
- Track if V is waiting for them
- Flag if V needs to respond

**Is this useful?**

---

### Question 3: Deal Definition
What counts as a "deal" to track?
- Only fundraising conversations?
- Partnerships too?
- Advisory relationships?
- Community collaborations?

**Or should we track all "opportunities" regardless of type?**

---

### Question 4: Auto-Draft Sensitivity
For auto-drafted holding emails:
- Should we draft for ALL slipping contacts?
- Only for critical priority?
- Only for deals (not general relationships)?
- Different cadence for different stakeholder types?

**Where's the line?**

---

### Question 5: Post-Meeting Ingestion Integration
You mentioned "existing networking ingestion function."

**Questions:**
- Where is this currently? (script, command, workflow?)
- How does it work? (voice notes? text input? structured prompts?)
- What does it output? (text? structured data? meeting notes?)
- Should I integrate with it or build new?

**Can you point me to the existing implementation?**

---

## Next Steps

**Immediate (Today):**
1. ✅ V reviews this architecture
2. ⏳ V answers open questions
3. ⏳ V confirms MVP priorities

**This Week:**
1. Build Phase 1 (foundation)
2. Test with 10-20 real contacts
3. Show V first prototype

**Next Week:**
1. Build Phase 2 (digests)
2. Generate first real Sunday digest
3. Iterate based on V's feedback

**Week 3:**
1. Build Phase 3 (auto-drafts + deals)
2. Full end-to-end testing
3. Production deployment

---

**Ready to build when you confirm!** 🚀
