# N5 Intelligence Layer - Discovery Questions

**Date:** 2025-10-12  
**Purpose:** Deep dive into requirements for comprehensive relationship intelligence system  
**Context:** Integrating weekly summary, stakeholder auto-tagging, meeting prep, and enrichment

---

## Question Categories

1. Current State & Pain Points
2. Priority Use Cases & Workflows
3. Data Sources & Scope
4. Review & Interaction Patterns
5. Integration Touchpoints
6. Trust, Automation & Human-in-Loop
7. Success Criteria & Metrics
8. Evolution & Maintenance
9. Technical Constraints & Preferences

---

## 1. Current State & Pain Points

### Your Current Workflow

**Q1.1:** Walk me through how you currently prepare for an upcoming meeting with an external stakeholder (e.g., investor, partner).

**Q1.2:** When you get back from a meeting, what do you do to capture context and maintain the relationship?

**Q1.3:** How do you currently track which relationships need attention? (e.g., "I haven't talked to Alex in a while")

**Q1.4:** Where do you currently store stakeholder information? (e.g., mental notes, calendar, CRM, docs, profiles)

**Q1.5:** How do you decide whether someone is worth investing time in vs. deprioritizing?

### What's Broken or Missing

**Q1.6:** What relationship management tasks take the most time today?

**Q1.7:** What information do you wish you had at your fingertips during meetings?

**Q1.8:** Have you ever been caught off-guard in a meeting because you forgot context or didn't see an important signal?

**Q1.9:** What relationships have gone cold that you wish you had maintained better?

**Q1.10:** What manual work are you doing repeatedly that should be automated?

---

## 2. Priority Use Cases & Workflows

### Core Scenarios (Rank these 1-5, where 1 = most critical)

**UC1:** **Pre-meeting prep** - Getting context before a scheduled meeting
- _Your ranking:_ ___
- _What makes good prep?_ ___

**UC2:** **Weekly relationship review** - Strategic view of who needs attention
- _Your ranking:_ ___
- _Ideal timing?_ (e.g., Sunday evening, Monday morning)

**UC3:** **Post-meeting follow-up** - Capturing context and tracking commitments
- _Your ranking:_ ___
- _Current pain points?_ ___

**UC4:** **Opportunity identification** - Spotting high-value connections or partnerships
- _Your ranking:_ ___
- _What signals matter?_ ___

**UC5:** **Relationship health monitoring** - Preventing relationships from going cold
- _Your ranking:_ ___
- _What's "at risk"?_ ___

### Additional Scenarios

**Q2.6:** What other scenarios am I missing?

**Q2.7:** Are there seasonal patterns? (e.g., fundraising season, conference prep, quarterly check-ins)

**Q2.8:** How do your needs differ for investors vs. partners vs. advisors vs. community?

---

## 3. Data Sources & Scope

### What Should Feed the Intelligence Layer?

**Q3.1:** Should the system analyze ALL external contacts or only specific types?
- [ ] All external (anyone not @mycareerspan/@theapply)
- [ ] Only meeting participants
- [ ] Only high-priority (investors, partners, advisors)
- [ ] Custom list (must-contact + discovered)

**Q3.2:** For email analysis, how far back should we look?
- Recent activity only (30 days)?
- Medium history (90 days)?
- Full context (1 year+)?
- Different windows for different stakeholder types?

**Q3.3:** Should we track internal stakeholders (Logan, Ilse, team)?
- If yes, what intelligence matters? (e.g., coordination patterns, workload)

**Q3.4:** What about passive contacts? (people you met once but haven't followed up)
- Track them?
- Surface them periodically?
- Let them fade unless they reach out?

### Enrichment Data Priorities

**Q3.5:** For each data source, rate importance (Critical / Nice-to-have / Skip):
- LinkedIn profiles: ___
- Company research (funding, size, industry): ___
- Deep due diligence (for investors): ___
- News mentions (person or company): ___
- Social media activity (Twitter/X): ___
- Mutual connections (via LinkedIn): ___
- Company website content: ___

**Q3.6:** For new contacts, should enrichment be:
- Automatic and immediate (as soon as discovered)?
- Queued for weekly batch processing?
- On-demand only (when you request it)?
- Tiered by stakeholder type (investors = auto, others = batch)?

---

## 4. Review & Interaction Patterns

### How You Want to Consume Intelligence

**Q4.1:** For weekly relationship digest, what's your ideal review flow?
- Quick scan (5-10 min) → flag interesting items → deeper dive later?
- Full review session (30+ min) with decisions?
- Incremental (review throughout the week)?

**Q4.2:** How do you prefer to receive intelligence?
- [ ] Email digest (like weekly summary)
- [ ] In-app notification
- [ ] SMS alert for critical items
- [ ] Just-in-time (before meetings, via daily prep)
- [ ] Combination (specify): ___

**Q4.3:** For tag suggestions, how do you want to review them?
- Bulk approve/reject in weekly digest?
- Individual review per contact?
- Auto-apply high confidence (>90%), review medium (60-90%), skip low (<60%)?
- Different thresholds for different tag categories?

**Q4.4:** When you review a stakeholder profile, what information do you look at?
- Recent activity only?
- Full history?
- Just highlights and action items?

### Feedback and Corrections

**Q4.5:** If the system gets something wrong (wrong tag, missed signal, incorrect inference), how should you correct it?
- Edit the profile directly?
- Reply to digest with corrections?
- Flag and system learns?
- Manual override in config?

**Q4.6:** Should the system explain its reasoning?
- Always show confidence scores and reasoning?
- Only for uncertain suggestions?
- Hide mechanics, just show results?

---

## 5. Integration Touchpoints

### Connecting to Existing Systems

**Q5.1:** For daily meeting prep, should it pull from the intelligence layer?
- Real-time query for each meeting?
- Pre-populated from weekly sync?
- Hybrid (weekly cache + real-time updates)?

**Q5.2:** Should the weekly summary and stakeholder tagging be:
- Two separate digests (relationship intelligence + calendar)? 
- One unified digest?
- Modular (relationship section within weekly summary)?

**Q5.3:** For Howie integration, what queries should Howie be able to make?
- "Who is this person and why are they important?"
- "What's our relationship history?"
- "What tags should I use for this meeting?"
- "Any prep materials or context I should know?"
- Other: ___

**Q5.4:** Should meeting transcripts automatically update stakeholder profiles?
- Yes, always (extract relationship context from transcripts)
- Only for first meetings (to create initial profile)
- Manual trigger only
- Depends on stakeholder type

**Q5.5:** Should the intelligence layer connect to your must-contact list?
- Auto-add discovered high-value contacts to must-contact?
- Highlight must-contact people in digests?
- Track progress on must-contact outreach?
- Alert if must-contact going cold?

---

## 6. Trust, Automation & Human-in-Loop

### Where You Need Control

**Q6.1:** What decisions should NEVER be automated?
- Sending external emails?
- Applying certain tags (e.g., priority:critical)?
- Adding someone to must-contact list?
- Initiating deep research?
- Updating stakeholder profiles?

**Q6.2:** What's safe to auto-apply (no review needed)?
- High-confidence tags (>95%)?
- Domain-based classifications (e.g., .edu = academic)?
- Email activity tracking (volume, recency)?
- Relationship state updates (e.g., cold → warm if new emails)?

**Q6.3:** For enrichment data, how much do you trust automated research?
- Trust LinkedIn data as ground truth?
- Verify web research before using?
- Require manual review for deep research?
- Different trust levels for different sources?

**Q6.4:** Should the system surface uncertainty?
- "75% confident this person is an investor - please verify"
- Hide uncertainty, only show high-confidence?
- Show all signals and let you judge?

### Privacy and Sensitivity

**Q6.5:** Any types of contacts that should be excluded from automated processing?
- Personal friends/family?
- Sensitive conversations (legal, HR)?
- Competitors?

**Q6.6:** Should all enrichment data be logged and auditable?
- Full provenance (where each fact came from)?
- Simplified (just final results)?
- Privacy-focused (minimal logging)?

---

## 7. Success Criteria & Metrics

### How We'll Know It's Working

**Q7.1:** What would make this intelligence layer indispensable to you?

**Q7.2:** If we nail this, what changes for you?
- Time saved per week: ___
- Better meeting outcomes (how measured?): ___
- Stronger relationships (how measured?): ___
- Fewer dropped balls (examples): ___

**Q7.3:** What metrics matter to you?
- Time to prepare for a meeting (target: <5 min?)
- Relationship coverage (% of contacts with verified tags)
- Catch rate (% of at-risk relationships saved)
- Discovery rate (new valuable contacts identified)
- Other: ___

**Q7.4:** How will you judge digest quality?
- Accuracy of tag suggestions?
- Relevance of surfaced information?
- Actionability (clear next steps)?
- Surprises (insights you wouldn't have had)?
- Time to review (shorter = better)?

---

## 8. Evolution & Maintenance

### System Adaptation

**Q8.1:** Should the system learn from your feedback?
- Adjust confidence thresholds based on approval rates?
- Learn which signals you care about?
- Adapt tag suggestions to your corrections?

**Q8.2:** How often should enrichment data be refreshed?
- Weekly (for active contacts)?
- Monthly?
- On-demand only?
- Before scheduled meetings?

**Q8.3:** For relationship state tracking, what triggers updates?
- New email → update last_contact date
- Meeting scheduled → update relationship state
- Long silence (30+ days) → flag as at-risk
- Pattern changes → surface anomalies

**Q8.4:** Should the system archive old/dormant contacts?
- Move to archive after X months inactive?
- Periodic "are these still relevant?" reviews?
- Keep forever (storage is cheap)?

### Maintenance Burden

**Q8.5:** How much ongoing maintenance are you willing to do?
- Weekly digest review: acceptable
- Monthly profile audits: too much?
- Quarterly taxonomy updates: okay?
- Continuous feedback: fine?

**Q8.6:** Should the system surface its own health metrics?
- "Tag accuracy has dropped to 70% - review needed"
- "30 contacts haven't been enriched - run batch?"
- "Cache is stale for 10 high-priority contacts"

---

## 9. Technical Constraints & Preferences

### System Design Preferences

**Q9.1:** Storage format for intelligence layer:
- JSON files (human-readable, git-friendly)?
- JSONL (append-only log style)?
- SQLite database (queryable)?
- Combination (JSONL for logs, JSON for state)?

**Q9.2:** Where should the intelligence layer live?
- `N5/intelligence/` (proposed)?
- `N5/records/intelligence/`?
- Top-level `Intelligence/`?
- Distributed (with each record type)?

**Q9.3:** Should there be a query API/interface?
- Python module with query functions?
- CLI tool (`n5 intelligence query "sarah@acmeventures.com"`)?
- Direct file access (for simplicity)?
- All of the above?

**Q9.4:** For caching, what TTL (time to live) makes sense?
- Participant context: 7 days? 30 days?
- LinkedIn data: 90 days? Never expire?
- Web research: 30 days? 60 days?
- Email activity: Real-time? Daily sync?

### API Rate Limits & Costs

**Q9.5:** Are there hard limits I should be aware of?
- Gmail API quota (currently unlimited for your use?)
- LinkedIn scraping rate (suggest 12/hour to be safe?)
- Web search costs (how much spending is okay?)
- Deep research LLM costs (acceptable for investors only? all?)

**Q9.6:** Should the system batch operations to minimize API calls?
- Group LinkedIn lookups (12/hour max)?
- Weekly batch for non-urgent enrichment?
- Smart caching to avoid redundant lookups?

---

## 10. Specific Design Decisions

### Schema and Structure

**Q10.1:** For participant cache, what fields are essential?
```json
{
  "email": "required",
  "name": "required",
  "company": "optional?",
  "title": "optional?",
  "stakeholder_type": "required?",
  "tags": "required?",
  "last_contact_date": "required?",
  "email_volume_30d": "nice-to-have?",
  "linkedin_url": "optional?",
  "profile_path": "optional?",
  // What else?
}
```

**Q10.2:** Should relationships be tracked as:
- Point-in-time snapshots (state at each check)?
- Event log (every email, meeting, state change)?
- Aggregated metrics (total emails, meeting count)?
- All of the above?

**Q10.3:** For tag suggestions, should we track:
- Suggestion history (what was suggested, what you chose)?
- Rejection reasons (why you rejected a tag)?
- Confidence calibration (actual accuracy vs. predicted)?

### Intelligence Layer Modules

**Q10.4:** Should these be separate scripts or one unified system?
- Separate: `discover_contacts.py`, `enrich_contact.py`, `track_relationships.py`, etc.
- Unified: `intelligence_manager.py` with submodules
- Hybrid: Core manager + pluggable modules

**Q10.5:** Should the intelligence layer have a "brain" that orchestrates everything?
- Central orchestrator that coordinates all intelligence operations?
- Distributed (each system writes to intelligence layer independently)?
- Event-driven (intelligence layer reacts to triggers)?

---

## 11. The Big Picture

### Your Vision

**Q11.1:** In 6 months, what does the intelligence layer enable you to do that you can't do now?

**Q11.2:** What's the "killer feature" - the one thing that would make this indispensable?

**Q11.3:** How does this fit into your broader vision for N5OS?
- Relationship intelligence is the foundation for ___?
- This unlocks future capabilities like ___?
- Eventually, this should enable ___?

**Q11.4:** Should this system be:
- V-specific (optimized for your workflow)?
- Generalizable (could work for Logan, Ilse, future team)?
- Exportable (could be a Careerspan product feature)?

**Q11.5:** What systems should this intelligence layer eventually power?
- Meeting prep (already identified)
- Stakeholder tagging (already identified)
- Weekly summaries (already identified)
- Fundraising pipeline?
- Partnership development?
- Network effect amplification?
- Customer relationship management?
- Other: ___

---

## Summary of Decisions Needed

Based on your answers, we'll define:

1. **Core architecture** - Storage, modules, APIs
2. **Data model** - Schemas, relationships, caching strategy  
3. **Enrichment pipeline** - What data, when, how much
4. **Review workflows** - How you interact with intelligence
5. **Automation boundaries** - What's auto vs. manual
6. **Integration patterns** - How systems connect
7. **Success metrics** - How we measure value
8. **Evolution plan** - How system learns and adapts

---

## Next Steps

1. **V answers discovery questions** (prioritize the ones that resonate most)
2. **Zo synthesizes requirements** into technical specification
3. **V reviews spec** and approves/adjusts
4. **Zo builds Phase 1** (foundation + quick wins)
5. **V tests and provides feedback**
6. **Iterate and expand**

---

## Your Turn

Which questions should we start with? I can:

**Option A:** You answer all of them comprehensively (might take 30-60 min)  
**Option B:** We do rapid-fire on highest-priority questions first  
**Option C:** I propose a strawman design and you react/correct  
**Option D:** We workshop specific thorny design decisions interactively

What's your preference?
