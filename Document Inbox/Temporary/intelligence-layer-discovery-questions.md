# Intelligence Layer - Discovery Questions for V

**Date:** 2025-10-12  
**Purpose:** Design comprehensive intelligence layer for N5 OS  
**Context:** Unifying weekly summary, daily prep, stakeholder tagging, meeting transcripts, Howie integration

---

## 🏗️ ARCHITECTURAL FOUNDATIONS (Critical - Answer First)

### 1. Single Source of Truth & Data Flow

**Question:** When you meet someone new (e.g., Sarah Chen from Acme Ventures), what should be the PRIMARY record of this contact?

**Options:**
- **A)** Stakeholder profile at `N5/records/stakeholder_profiles/sarah-chen.md`
- **B)** Meeting record at `N5/records/meetings/2025-10-14_sarah-chen-acme/stakeholder_profile.md`
- **C)** Intelligence layer cache at `N5/intelligence/contacts/sarah-chen.json`
- **D)** Multiple sources with sync/merge logic

**Follow-up:** How should data flow between:
- Meeting transcripts → Stakeholder profiles?
- Weekly summary discoveries → Stakeholder profiles?
- Email analysis → Stakeholder profiles?
- Howie calendar tags → Stakeholder profiles?

**Why it matters:** This determines the entire data architecture. We need ONE authoritative place or a clear sync strategy.

---

### 2. Contact Identity & Deduplication

**Scenario:** Sarah Chen has:
- Personal email: sarah.chen.personal@gmail.com
- Work email: sarah@acmeventures.com  
- LinkedIn: linkedin.com/in/sarahchen
- Phone: +1-555-0123

**Questions:**
1. Do you want ONE unified contact record or separate records per context?
2. How should we handle identity resolution?
   - Manual review when duplicates suspected?
   - Auto-merge based on name similarity?
   - Keep separate until you explicitly merge?
3. What's the unique identifier?
   - Primary email?
   - System-generated ID?
   - LinkedIn URL?

**Why it matters:** Affects database design, merge logic, and data integrity.

---

### 3. Historical Data Retention

**Question:** How much history do you want to keep?

**For each contact:**
- Email history: Last 30 days? 90 days? All time?
- Meeting history: Last 5 meetings? All meetings?
- Relationship state changes: Full history or current only?
- Tag changes: Track who added tags when? Or just current tags?

**Storage considerations:**
- Full email bodies or just metadata (subject, date, snippet)?
- Full meeting transcripts or just summaries?
- Enrichment data (LinkedIn, web research) - cache how long?

**Why it matters:** Affects storage size, query performance, and privacy/security.

---

### 4. Data Ownership & Privacy

**Question:** What level of data sensitivity do you have?

**Considerations:**
1. Should we cache email content from Gmail, or only metadata?
2. Should we store full LinkedIn profiles, or just extracted fields?
3. Should meeting transcripts be linked or embedded in profiles?
4. Any contacts that should NOT be in the intelligence layer?
   - Internal Careerspan employees?
   - Personal contacts?
   - Sensitive relationships?

**Why it matters:** Compliance, security, and system design.

---

## 💼 WORKFLOW & USE CASES (High Priority)

### 5. Primary Daily Workflows

**Question:** Walk me through your ideal daily/weekly workflow with this intelligence layer.

**Specific scenarios:**

**Scenario A: Morning of a meeting with Sarah (new contact)**
- What do you want to see?
- When do you want to see it? (email digest? on-demand query? Howie integration?)
- How much detail? (quick summary vs. full dossier)

**Scenario B: Weekly planning on Sunday evening**
- What do you need to prepare for the week?
- What decisions do you need to make? (who to follow up with, who to deprioritize, etc.)
- How much time do you want to spend reviewing?

**Scenario C: Mid-week relationship triage**
- How do you track "who haven't I heard from in a while"?
- Who should you proactively reach out to?
- How do you identify "hot" vs "cold" relationships?

**Scenario D: Ad-hoc lookup**
- When do you need to quickly look up a contact?
- What's the query interface? (ask Zo? search command? web dashboard?)

**Why it matters:** Drives UI/UX design and automation priorities.

---

### 6. Decision Points & Automation Boundaries

**Question:** Where do you want automation vs. manual control?

**Auto vs. Manual:**

| Action | Auto | Manual | Approval-Required |
|--------|------|--------|-------------------|
| Discover new contact from email | ? | ? | ? |
| Suggest tags for contact | ? | ? | ? |
| Apply verified tags to profile | ? | ? | ? |
| Trigger deep research on investor | ? | ? | ? |
| Update relationship status (warm→cold) | ? | ? | ? |
| Add contact to must-contact list | ? | ? | ? |
| Send follow-up reminders | ? | ? | ? |
| Sync tags to Howie calendar | ? | ? | ? |

**For "Approval-Required" items:**
- How should approval work? (email digest? in-app notification? SMS?)
- How long do you have to respond before auto-timeout?

**Why it matters:** Determines how much human-in-the-loop vs. full automation.

---

### 7. Notification & Delivery Preferences

**Question:** How do you want to receive intelligence updates?

**Options:**
- **Email digest** (daily? weekly? per-event?)
- **SMS notifications** (high-priority only? all updates?)
- **In-app/workspace notifications** (check when convenient?)
- **On-demand queries** (ask Zo when needed?)
- **Calendar integration** (meeting prep in event description?)

**Specific examples:**
- New contact discovered: Email? SMS? Silent?
- Relationship going cold: Email reminder? SMS? Silent?
- Investor meeting tomorrow: Email prep? SMS reminder? Howie integration?
- Weekly relationship review: Email digest? In-app only?

**Why it matters:** Determines delivery infrastructure and scheduled task design.

---

## 🔍 INTELLIGENCE QUALITY & ENRICHMENT (Medium Priority)

### 8. Enrichment Triggers & Depth

**Question:** When should we enrich a contact, and how deep?

**Enrichment levels:**
- **Level 0:** Email only (name, company from signature)
- **Level 1:** + Domain analysis (company website, industry guess)
- **Level 2:** + LinkedIn profile (role, experience, connections)
- **Level 3:** + Web search (company background, news, funding)
- **Level 4:** + Deep research (full dossier, strategic fit analysis)

**Trigger rules:**
1. **New contact discovered from email:**
   - Auto-enrich to what level?
   - Only if meeting scheduled?
   - Only if external domain?

2. **Existing contact with upcoming meeting:**
   - Re-enrich (data may be stale)?
   - Only enrich if >30 days old?
   - Skip if recently enriched?

3. **High-priority contact (investor, partner):**
   - Always Level 4 (deep research)?
   - Manual trigger only?
   - Auto-trigger but require review?

**Cost/performance trade-offs:**
- LinkedIn lookups: ~5-10 seconds each (rate-limited)
- Web search: ~2-3 seconds each
- Deep research: ~30-60 seconds each (LLM-intensive)

**Why it matters:** API costs, performance, and data freshness.

---

### 9. Relationship Status Tracking

**Question:** How should we track relationship momentum?

**Relationship states (from your taxonomy):**
- `#relationship:new` → `#relationship:warm` → `#relationship:active`
- `#relationship:cold` → `#relationship:dormant`

**Auto-detection rules:**

| State | Definition | Auto-detect? |
|-------|------------|--------------|
| `new` | First interaction | Yes (first meeting/email) |
| `warm` | Active conversation, not yet established | ? |
| `active` | Regular engagement (2+ interactions/month) | ? |
| `cold` | No contact in 30-60 days | ? |
| `dormant` | No contact in 60+ days | ? |

**For auto-state transitions:**
- Should we notify you? ("Jake went cold - no contact in 45 days")
- Should we suggest actions? ("Re-engage with warm intro?")
- Should we auto-add to must-contact list?

**Manual overrides:**
- Can you manually set state? (e.g., "Keep as active even though dormant")
- Can you block auto-transitions? (e.g., "Don't mark as cold, just on pause")

**Why it matters:** Determines relationship health tracking and proactive outreach.

---

### 10. Tag Confidence & Review Process

**Question:** How much do you trust AI tag suggestions?

**Confidence thresholds:**
- **>90% confidence:** Auto-apply? Or still review?
- **70-90% confidence:** Suggest with "likely correct" flag?
- **<70% confidence:** Suggest with "needs review" flag?

**Bulk review workflow:**
- Would you prefer to review 10 contacts at once (weekly batch)?
- Or review contact-by-contact as discovered?
- Or trust high-confidence auto-tagging with audit log?

**Feedback loop:**
- If you correct a tag, should system learn? (e.g., "Always trust LinkedIn job title for stakeholder type")
- Track accuracy over time and adjust thresholds?

**Why it matters:** User trust, time efficiency, and system learning.

---

## 🔗 SYSTEM INTEGRATION (Medium Priority)

### 11. Weekly Summary Integration Strategy

**Question:** How should weekly summary and intelligence layer work together?

**Option A: Weekly summary reads from intelligence layer**
- Intelligence layer is updated continuously
- Weekly summary just queries and formats it
- Pro: No duplicate enrichment
- Con: Weekly summary becomes a "view" not a "generator"

**Option B: Weekly summary writes to intelligence layer**
- Weekly summary discovers contacts and enriches them
- Writes back to intelligence layer for others to use
- Pro: Weekly summary drives discovery
- Con: Duplicate logic with stakeholder tagging

**Option C: Hybrid**
- Intelligence layer handles discovery and enrichment
- Weekly summary is one of many consumers
- Both read and write to shared cache
- Pro: True shared intelligence
- Con: More complex coordination

**Which model fits your mental model best?**

**Why it matters:** Determines architectural relationships between systems.

---

### 12. Daily Prep vs. Weekly Summary

**Question:** How should daily prep and weekly summary divide responsibilities?

**Current state:**
- **Daily prep:** Today's meetings, tactical
- **Weekly summary:** Next week's meetings, strategic

**With intelligence layer:**
- Should daily prep just be a "filtered view" of weekly summary?
- Or should daily prep add additional enrichment (same-day email activity)?
- Should they share the same participant cache?

**Specific question:**
- If weekly summary enriches Sarah Chen on Sunday, should daily prep on Tuesday re-enrich or reuse data?
- If daily prep finds new info on Tuesday, should it update weekly summary state?

**Why it matters:** Avoid redundancy, ensure consistency.

---

### 13. Meeting Transcript Processing Integration

**Question:** How should meeting transcripts feed the intelligence layer?

**Current state:**
- Meeting transcripts processed to `N5/records/meetings/{meeting_id}/`
- Stakeholder profiles sometimes created
- Smart blocks extracted (action items, insights, hypotheses)

**With intelligence layer:**
- Should transcript processing auto-update stakeholder profiles?
- Should it update relationship status? (new → warm → active)
- Should it extract and apply tags automatically?
- Should it update email history context?

**Specific example:**
- After meeting with Sarah Chen, transcript shows:
  - Discussed Series A fundraising (add `#context:fundraising`?)
  - Next steps: V to send deck by Friday (add `#followup:vrijen_5`?)
  - Relationship seems promising (update `#relationship:warm`?)

**Auto-apply or suggest for review?**

**Why it matters:** Closes the loop from meeting → intelligence → next meeting.

---

### 14. Howie Integration Depth

**Question:** What should Howie be able to query from the intelligence layer?

**Potential queries:**
- "Give me context on Sarah Chen for tomorrow's meeting"
- "Show me all investors I've met in the last 6 months"
- "Who should I follow up with this week?"
- "Recommend V-OS tags for this new contact"

**Data access:**
- Read-only (Howie queries, N5 is source of truth)?
- Read-write (Howie can update tags/notes)?
- Bidirectional sync (tags applied in Howie sync back to N5)?

**Authentication:**
- Should Howie have an API key?
- Or should queries be proxied through Zo (you ask Zo, Zo queries intelligence layer)?

**Why it matters:** Security, data flow, and integration complexity.

---

## 📊 DATA STRUCTURE & SCHEMA (Lower Priority - Technical)

### 15. Contact Record Schema

**Question:** What fields should a contact record have?

**Proposed schema (feedback welcome):**
```json
{
  "id": "uuid",
  "primary_email": "sarah@acmeventures.com",
  "alternate_emails": ["sarah.chen@gmail.com"],
  "name": {
    "full": "Sarah Chen",
    "first": "Sarah",
    "last": "Chen"
  },
  "company": {
    "name": "Acme Ventures",
    "domain": "acmeventures.com",
    "role": "Partner"
  },
  "tags": {
    "verified": ["#stakeholder:investor", "#priority:critical"],
    "suggested": ["#context:venture_capital"],
    "auto_applied": ["#relationship:new"]
  },
  "enrichment": {
    "linkedin_url": "...",
    "last_enriched": "2025-10-12T14:00:00Z",
    "enrichment_level": 3,
    "data": { /* cached enrichment data */ }
  },
  "relationship": {
    "status": "new",
    "first_contact": "2025-10-08",
    "last_contact": "2025-10-11",
    "contact_frequency": "3 emails in last 7 days",
    "momentum": "heating_up"
  },
  "meetings": [
    {
      "date": "2025-10-14",
      "transcript_path": "N5/records/meetings/...",
      "type": "discovery"
    }
  ],
  "email_history": {
    "total_emails": 5,
    "last_30_days": 5,
    "topics": ["fundraising", "deck review", "scheduling"],
    "threads": [ /* email thread summaries */ ]
  },
  "metadata": {
    "created_at": "2025-10-08",
    "updated_at": "2025-10-12",
    "data_sources": ["gmail", "calendar", "linkedin"],
    "review_status": "pending"
  }
}
```

**Questions:**
1. Is this too much detail or not enough?
2. What fields are missing?
3. What fields are unnecessary?
4. Should we embed data or reference it?

**Why it matters:** This is the foundation of everything.

---

### 16. Storage Format & Performance

**Question:** How should we store the intelligence layer data?

**Options:**
- **A) JSON files** (one per contact): Easy to read/edit, good for git, slower queries
- **B) JSONL database** (append-only log): Good for history, harder to query
- **C) SQLite database**: Fast queries, harder to inspect manually
- **D) Hybrid**: SQLite for queries, JSON exports for git/backup

**Query patterns you'll need:**
- "Show me all investors with meetings this week"
- "Show me all contacts with no activity in 60 days"
- "Show me all partners in HR tech space"
- "Show me relationship momentum trends over time"

**Which storage format best supports your needs?**

**Why it matters:** Performance, maintainability, and git-friendliness.

---

### 17. Version Control & Audit Trail

**Question:** Do you want to track changes to contact data over time?

**Examples:**
- Tag changes: Who added `#priority:high` and when?
- Relationship transitions: When did Sarah go from `new` → `warm`?
- Enrichment updates: What changed in her LinkedIn profile since last check?
- Manual edits: Did you override an auto-suggestion?

**Audit trail depth:**
- **Minimal:** Just current state + last_updated timestamp
- **Standard:** Track changes with date + reason (auto vs. manual)
- **Full:** Complete history with diffs

**Why it matters:** Debugging, accountability, and learning from patterns.

---

## 🎯 PRIORITIES & SEQUENCING (Critical - Answer Last)

### 18. MVP Definition

**Question:** What's the MINIMUM system that would be valuable to you?

**Must-haves:**
- Contact discovery from emails/meetings?
- Basic enrichment (LinkedIn + web search)?
- Tag suggestions?
- Weekly review digest?
- Integration with one system (weekly summary? daily prep? stakeholder tagging?)

**Can wait:**
- Deep research integration?
- Trend analysis?
- Howie API?
- Full audit trail?
- Advanced queries?

**Why it matters:** Determines what to build first vs. what to defer.

---

### 19. Success Criteria

**Question:** How will you know this intelligence layer is working well?

**Measurable outcomes:**
- Time savings: "Weekly prep takes 10 min instead of 30 min"?
- Relationship quality: "Never miss a follow-up" or "All active contacts engaged monthly"?
- Meeting outcomes: "Better prepared for 90% of meetings"?
- Business results: "Close more partnerships" or "Raise from right investors"?

**What would make you say "this is a game-changer"?**

**Why it matters:** Defines success and guides priorities.

---

### 20. Implementation Pace

**Question:** How fast do you want to move on this?

**Options:**
- **Sprint mode:** Build MVP in 1-2 weeks, iterate based on real usage
- **Careful mode:** Design thoroughly, build in 3-4 weeks with full features
- **Hybrid:** Build foundation this week, add features incrementally over month

**Your availability:**
- How much time can you spend testing/reviewing/providing feedback?
- Daily check-ins or weekly reviews?
- Prefer working prototypes fast or polished features slower?

**Why it matters:** Determines development approach and milestone planning.

---

## 📋 SUMMARY OF QUESTION CATEGORIES

**Critical (Answer First):**
1. Single source of truth & data flow
2. Contact identity & deduplication
3. Historical data retention
4. Data ownership & privacy

**High Priority:**
5. Primary daily workflows
6. Decision points & automation boundaries
7. Notification & delivery preferences

**Medium Priority:**
8. Enrichment triggers & depth
9. Relationship status tracking
10. Tag confidence & review process
11. Weekly summary integration strategy
12. Daily prep vs. weekly summary
13. Meeting transcript processing integration
14. Howie integration depth

**Lower Priority (Can Answer Later):**
15. Contact record schema
16. Storage format & performance
17. Version control & audit trail

**Strategic:**
18. MVP definition
19. Success criteria
20. Implementation pace

---

## 🎤 Your Turn, V

**Please answer in any order, but prioritize:**
1. **Questions 1-4** (architectural foundations)
2. **Questions 5-7** (workflows)
3. **Questions 18-20** (MVP and priorities)

**Format suggestions:**
- Answer inline in this doc
- Record voice notes and I'll transcribe
- Schedule a working session to discuss
- Answer async over multiple messages

**I'll design the complete system architecture based on your answers.**

Ready when you are!
