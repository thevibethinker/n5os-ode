# Howie ↔ Zo Harmonization Plan — REVISED

**Date:** 2025-10-11  
**Version:** 2.0 (Incorporating V's feedback)  
**Status:** Ready for implementation

---

## REVISION NOTES

### Key Changes Based on Feedback

1. ✅ **Complete tag mapping** — All V-OS tags now mapped (not just subset)
2. ✅ **Asterisk placement** — Must go at END of tags section to activate
3. ✅ **Binary priority system** — Critical vs non-critical (simpler)
4. ✅ **Howie can populate calendar descriptions** — Auto-translation confirmed
5. ✅ **Creative synergy use cases** — Expanded beyond basic scheduling

---

## COMPLETE V-OS TAG MAPPING

### Tag Categories (from images)

```
{TWIN}  [!!] [D5] [D5+] [D10]
{CATG}  [LD-INV] [LD-HIR] [LD-COM] [LD-NET] [LD-GEN]
{POST}  [OFF] [AWA]
{FLUP}  [F-X] [FL-X] [FM-X]
{CORD}  [LOG] [ILS]
{WKND}  [WEX] [WEP]
{MISC}  [A-X] [TERM]
{GPT}   [GPT-I] [GPT-E] [GPT-F]
```

**Activation:** Asterisk `*` goes at END of tag block, e.g., `[D5+] [LD-NET] [OFF] *`

---

## COMPLETE TAG MAPPING: Howie → N5

| Category | Howie Tag | N5 Tag | Meaning | Notes |
|----------|-----------|--------|---------|-------|
| **TWIN (Timing)** | | | | |
| | `!!` | `#priority:critical` | Override constraints, next 2 business days | Ultra-urgent |
| | `[D5]` | `#schedule:within_5d` | Schedule within 5 business days | Short-term |
| | `[D5+]` | `#schedule:5d_plus` | Schedule 5+ business days out | Mid-term |
| | `[D10]` | `#schedule:10d_plus` | Schedule 10+ business days out | Long-term |
| **CATG (Category/Lead Type)** | | | | |
| | `[LD-INV]` | `#stakeholder:investor` `#type:discovery` | Investor meeting | Add type on first meeting |
| | `[LD-HIR]` | `#stakeholder:job_seeker` `#type:discovery` | Hiring/recruiting | Candidate meetings |
| | `[LD-COM]` | `#stakeholder:community` `#type:partnership` | Community partnerships | Align with Logan |
| | `[LD-NET]` | `#stakeholder:partner` `#type:discovery` | Networking/business development | Could be new `#stakeholder:network` |
| | `[LD-GEN]` | `#stakeholder:prospect` | General lead | Catch-all for new contacts |
| **POST (Meeting Status)** | | | | |
| | `[OFF]` | `#status:postponed` | Meeting postponed/off calendar | Remove from digest |
| | `[AWA]` | `#status:awaiting` | Awaiting response/confirmation | Tentative, may change |
| **FLUP (Follow-up Rules)** | | | | |
| | `[F-X]` | `#followup:external_X` | After X days, Howie sends reminder | External follow-up |
| | `[FL-X]` | `#followup:logan_X` | After X days, private to Logan | Internal coordination |
| | `[FM-X]` | `#followup:vrijen_X` | After X days, remind V only | Personal reminder |
| **CORD (Coordination)** | | | | |
| | `[LOG]` | `#align:logan` | Align with Logan's schedule | Internal coordination |
| | `[ILS]` | `#align:ilse` | Align with Ilse's schedule | Internal coordination |
| **WKND (Weekend Availability)** | | | | |
| | `[WEX]` | `#availability:weekend_ok` | Allow weekend slots before 5 PM | Extended availability |
| | `[WEP]` | `#availability:weekend_preferred` | Prefer weekend scheduling | Weekend priority |
| **MISC (Miscellaneous)** | | | | |
| | `[A-0]` | `#accommodation:minimal` | Only on our terms | Strong position |
| | `[A-1]` | `#accommodation:baseline` | Standard accommodation | Default |
| | `[A-2]` | `#accommodation:full` | Fully accommodating | Flexible position |
| | `[TERM]` | `#status:inactive` | Howie involvement terminated | Exclude from processing |
| **GPT (Priority/Preference)** | | | | |
| | `[GPT-I]` | `#priority:internal` | Prioritize internal stakeholders | Careerspan team first |
| | `[GPT-E]` | `#priority:external` | Prioritize external stakeholders | Guest convenience |
| | `[GPT-F]` | `#priority:founders` | Prioritize founders' preferences | Logan + V first |

---

## SIMPLIFIED PRIORITY SYSTEM (Binary)

**Per V's feedback: Critical vs Non-Critical**

### Priority Mapping

| Context | Howie Input | N5 Tag | Behavior |
|---------|-------------|--------|----------|
| Ultra-urgent | `!!` | `#priority:critical` | Do not reschedule, protect time |
| Investor (default) | `[LD-INV]` | `#priority:critical` | High-value, protect time |
| High accommodation | `[A-2]` | `#priority:non-critical` | Can reschedule if needed |
| Flexible | From context | `#priority:non-critical` | Normal priority |

**Simplified logic:**
- `#priority:critical` → "⚠️ Protect this time block"
- `#priority:non-critical` → No special warning

---

## CALENDAR DESCRIPTION AUTO-POPULATION

### Howie's Role: Tag Translation

When Howie schedules a meeting, populate calendar description with:

```markdown
#stakeholder:[type] #type:[type] #priority:[critical|non-critical]
[Additional relevant tags from: #schedule, #align, #accommodation, #availability]

Purpose: [Brief description from email context]

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

[Conferencing details]
[Rescheduling links]
```

### Example Translation

**Email tags:** `[D5+] [LD-NET] [OFF] *`

**Calendar description:**
```markdown
#stakeholder:partner #type:discovery #priority:non-critical #schedule:5d_plus #status:postponed

Purpose: Explore partnership opportunities with [Organization]

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

Google Meet: [link]
Reschedule: [link]
```

---

## N5 TAG SYSTEM UPDATES

### New Tags to Add

**Stakeholder types (add 2):**
- `prospect` — General leads (from `[LD-GEN]`)
- `network` — Optional alternative to `partner` for pure networking

**Status tags (new category):**
- `#status:postponed` — From `[OFF]`
- `#status:awaiting` — From `[AWA]`
- `#status:inactive` — From `[TERM]`

**Schedule tags (new category):**
- `#schedule:within_5d` — From `[D5]`
- `#schedule:5d_plus` — From `[D5+]`
- `#schedule:10d_plus` — From `[D10]`

**Coordination tags (new category):**
- `#align:logan` — From `[LOG]`
- `#align:ilse` — From `[ILS]`
- `#align:founders` — From `[GPT-F]`

**Accommodation tags (new category):**
- `#accommodation:minimal` — From `[A-0]`
- `#accommodation:baseline` — From `[A-1]`
- `#accommodation:full` — From `[A-2]`

**Availability tags (new category):**
- `#availability:weekend_ok` — From `[WEX]`
- `#availability:weekend_preferred` — From `[WEP]`

**Follow-up tags (new category):**
- `#followup:external_X` — From `[F-X]`
- `#followup:logan_X` — From `[FL-X]`
- `#followup:vrijen_X` — From `[FM-X]`

**Priority tags (new category, separate from old priority):**
- `#priority:internal` — From `[GPT-I]`
- `#priority:external` — From `[GPT-E]`
- `#priority:founders` — From `[GPT-F]`

### Revised Priority System

**Main priority (binary):**
- `#priority:critical` — Do not reschedule
- (No tag) — Non-critical, default

**Secondary priority (stakeholder preference):**
- `#priority:internal` — Favor internal schedules
- `#priority:external` — Favor external schedules
- `#priority:founders` — Favor founders' schedules

---

## SPECIAL EVENT HANDLING

### Events to Exclude from Digest

N5's `filter_external_meetings()` should skip:

1. **Deep Work blocks** — Title contains `[DW]`
2. **Meeting Buffers** — Title contains "Meeting Buffer"
3. **Follow-up slots** — Title contains "Follow-up" (unless action items added)
4. **Travel buffers** — Auto-generated buffer events
5. **Postponed meetings** — Has `#status:postponed` tag
6. **Inactive threads** — Has `#status:inactive` tag

### Events to Flag in Digest

1. **Awaiting confirmation** — Has `#status:awaiting` → Add note "⏳ Awaiting confirmation"
2. **Weekend meetings** — Has `#availability:weekend_*` → Add note "📅 Weekend meeting"
3. **High accommodation** — Has `#accommodation:full` → Emphasize understanding their needs in BLUF

---

## CREATIVE SYNERGY USE CASES

### 1. **Meeting Intelligence Feedback Loop**

**How it works:**
- After meeting, Zo generates insights (key topics, follow-up needs, relationship strength)
- Zo emails Howie with context: "Meeting with [Person] went well, priority relationship, prefer Tuesday/Thursday for future"
- Howie stores this as preference override for future scheduling with that contact

**Use case:** Optimize scheduling patterns based on actual meeting outcomes

---

### 2. **Automated Pre-Meeting Brief Delivery**

**How it works:**
- Howie schedules meeting for next Tuesday 2 PM
- Howie triggers Zo: "Generate brief for [Meeting] by Monday 5 PM"
- Zo generates research, BLUF, prep actions
- Howie emails brief to V at optimal time (Monday evening or Tuesday morning)

**Use case:** Never walk into a meeting unprepared, automatically

---

### 3. **Relationship Warming Engine**

**How it works:**
- Zo tracks last contact date for each stakeholder (from calendar + email)
- When stakeholder hasn't been contacted in X days, Zo notifies Howie
- Howie sends "checking in" email from V: "Hi [Name], been a while since we connected. Would love to catch up on [topic]. Are you free for a 30-min call?"

**Use case:** Maintain relationships proactively without manual tracking

---

### 4. **Context-Aware Scheduling Triage**

**How it works:**
- Person emails requesting meeting
- Howie CC's Zo: "Do we have context on [Person]?"
- Zo searches email history, calendar history, knowledge base
- Zo replies to Howie: "Yes, last met 3 months ago re: [topic], investor intro, recommend [LD-INV] [A-1]"
- Howie uses this to determine tags and scheduling approach

**Use case:** Smart scheduling decisions based on relationship history

---

### 5. **Post-Meeting Action Automation**

**How it works:**
- Meeting ends
- Howie auto-schedules 10-min "Follow-up" slot next day (per LD-* rules)
- Zo generates action items from meeting (if V provides notes or uses voice memo)
- Zo pre-populates follow-up slot description with action items
- Howie sends summary email to meeting participants with action items

**Use case:** Complete meeting lifecycle automation

---

### 6. **Conflict Intelligence Resolution**

**How it works:**
- Howie receives scheduling request that conflicts with existing meeting
- Howie queries Zo: "Can we move [Existing Meeting]? Priority comparison?"
- Zo checks tags: Existing = `#priority:critical`, New = `#priority:non-critical`
- Zo replies: "Keep existing, offer alternative slots for new"
- Howie proposes alternatives to new request

**Use case:** Smart conflict resolution without bothering V

---

### 7. **Attendee Research Pipeline**

**How it works:**
- Howie schedules new meeting with external person
- Howie triggers Zo: "New meeting scheduled with [Person] for [Date], research needed"
- Zo immediately starts research (LinkedIn, company info, past interactions)
- Zo saves research to knowledge base
- Research is ready when digest is generated

**Use case:** Proactive research, not last-minute scrambling

---

### 8. **Email Triage & Forwarding Protocol**

**How it works:**
- Howie handles scheduling emails in thread
- If email contains substantive content (not just scheduling):
  - Articles, attachments, long context → Howie forwards to Zo with tag `[FWD-Z]*`
  - Zo processes: extracts key info, saves to knowledge base, drafts response if needed
- Howie focuses on scheduling, Zo handles content

**Use case:** Division of labor between AIs, Howie = logistics, Zo = substance

---

### 9. **Recurring Outreach Automation**

**V's use case: Monthly doctor prescription emails**

**Enhanced with Zo:**
- Howie sends recurring email every month
- Zo pre-populates email with updated info (current medications, recent changes)
- Howie sends email with Zo's content
- Doctor replies → Howie forwards to Zo → Zo updates health records

**Other applications:**
- Monthly investor updates (Zo generates metrics, Howie distributes)
- Quarterly partnership check-ins (Zo drafts context, Howie schedules + sends)
- Weekly team summaries (Zo compiles, Howie distributes)

---

### 10. **Public-Facing AI Operation**

**V's vision: Howie as public face**

**How it works:**
- External contacts interact primarily with Howie (via email)
- Howie: Polite, professional, handles logistics
- Zo: Behind-the-scenes intelligence, research, strategy
- V: Reviews and approves at key decision points

**Benefits:**
- Consistent external communication style (Howie's persona)
- Deep intelligence without exposing complexity (Zo in background)
- V freed from scheduling minutiae but maintains control

**Example flow:**
1. External contact emails → Howie responds
2. Howie schedules meeting → Adds N5 tags to calendar
3. Zo generates prep brief → Howie delivers to V
4. Meeting happens → V provides quick notes
5. Zo generates follow-up → Howie sends to external contact
6. Zo tracks relationship → Suggests next touchpoint to Howie

---

### 11. **Stakeholder Database Sync**

**How it works:**
- Zo maintains stakeholder profiles in N5 knowledge base
- Each profile includes:
  - Relationship type (investor, partner, customer, etc.)
  - Preferred meeting times/days
  - Communication style preferences
  - Key topics of interest
  - Last interaction date
- Howie references this database when scheduling
- After each meeting, Zo updates profile with new insights
- Howie's scheduling gets smarter over time

**Use case:** Self-improving scheduling based on accumulated knowledge

---

### 12. **Team Coordination Amplifier**

**How it works:**
- Meeting tagged with `[LOG]` (align with Logan)
- Howie checks Logan's calendar for availability
- Zo checks what Logan is working on (from internal docs, stand-ups)
- Zo generates coordination agenda: "Topics to sync with Logan: [X], [Y], [Z]"
- Agenda is added to meeting prep brief
- Post-meeting, Zo updates Logan with relevant action items

**Use case:** Seamless internal coordination without manual alignment

---

### 13. **Travel Intelligence Integration**

**How it works:**
- Flight/train scheduled → Howie adds travel event with 2-hour buffers
- Zo detects travel event in digest generation
- Zo generates travel checklist:
  - Meetings before/after travel (prepare handoffs)
  - Documents needed for trip
  - Contacts in destination city
  - Meetings to schedule while there
- Howie offers to schedule meetings in destination city
- Zo tracks travel patterns, suggests recurring trips to streamline

**Use case:** Travel becomes opportunity for strategic meetings, not just logistics

---

### 14. **Accommodation-Based Research Depth**

**How it works:**
- Meeting tagged `[A-2]` (full accommodation)
- Zo increases research depth: more detailed background, their priorities, pain points
- BLUF emphasizes: "Understand their needs and constraints"
- Prep actions: "Prepare 3+ options showing flexibility"

- Meeting tagged `[A-0]` (our terms only)
- Zo focuses research on: validating fit, establishing value prop
- BLUF emphasizes: "Establish clear value and requirements"
- Prep actions: "Prepare 1-2 clear options, non-negotiables"

**Use case:** Research and prep tailored to negotiating posture

---

### 15. **Follow-up Tag Automation**

**How it works:**
- Meeting has `[F-5]` tag (external follow-up in 5 days)
- Howie tracks: no response after 5 days
- Howie sends reminder: "Hi [Name], following up on our conversation..."
- Zo provides context for reminder: "Mention [specific topic] from meeting"
- If still no response after second reminder, Zo flags to V: "Consider alternative approach?"

**Use case:** Automated persistence without being annoying

---

### 16. **Weekend Meeting Optimization**

**How it works:**
- Meeting tagged `[WEP]` (weekend preferred) + `#stakeholder:investor`
- Zo recognizes: weekend meeting = high priority contact accommodating them
- BLUF includes: "Weekend meeting signals strong interest/urgency from their side"
- Prep actions: "Prepare for potentially longer/more strategic conversation"
- Post-meeting: Zo suggests immediate follow-up given high engagement

**Use case:** Extract maximum value from non-standard meeting times

---

### 17. **Email Thread Context Preservation**

**How it works:**
- Howie manages scheduling in long email thread (multiple people)
- Thread contains substantive discussion beyond scheduling
- Howie forwards entire thread to Zo with summary: "Meeting scheduled, context preserved"
- Zo extracts key points from thread, adds to meeting prep brief under "Thread Context"
- V walks into meeting with full email discussion context, not just calendar event

**Use case:** Don't lose context in email → meeting transition

---

### 18. **Dynamic Meeting Duration Adjustment**

**How it works:**
- First meeting with `[LD-INV]` → Howie schedules 45 min (discussion)
- Zo's research reveals: early-stage VC, exploratory phase
- Zo suggests to Howie: "Consider 30 min (chat) instead, this is likely quick screen"
- Howie adjusts
- After meeting, V notes: "This is serious, follow-up needed"
- Next meeting with same VC → Howie schedules 60 min (detailed discussion)

**Use case:** Meeting duration adapts to relationship stage

---

### 19. **Cross-Meeting Pattern Recognition**

**How it works:**
- Zo tracks all meetings with `#stakeholder:investor` tag
- Recognizes pattern: investor meetings scheduled Tuesday/Thursday have 80% conversion to follow-up
- Zo notifies Howie: "Recommend Tuesday/Thursday for investor meetings"
- Howie updates default behavior for `[LD-INV]` tags
- System learns V's optimal patterns without explicit rules

**Use case:** Self-optimizing scheduling based on outcomes

---

### 20. **Prep Brief Progressive Enhancement**

**How it works:**
- Meeting scheduled 10+ days out (`[D10]`)
- Zo generates basic brief immediately (bio, company, past interactions)
- 5 days before: Zo updates with recent news, company updates
- 2 days before: Zo adds specific talking points based on V's current priorities
- Morning of: Zo adds last-minute context (overnight news, emails)
- Brief evolves from generic → highly specific as meeting approaches

**Use case:** Early awareness + just-in-time detail

---

## IMPLEMENTATION PRIORITY

### Phase 1: Core Harmonization (Week 1)
1. ✅ Complete tag mapping documented
2. 🔧 Update N5 code with new tag categories
3. 🔧 Create Howie calendar description template
4. 🔧 Test Howie → N5 tag translation
5. 🔧 Update documentation

### Phase 2: Basic Integration (Week 2)
6. 📧 Set up Howie → Zo email forwarding for `[FWD-Z]*` tag
7. 📧 Set up Zo → Howie email communication (va@zo.computer → howie@howie.ai)
8. 🔧 Implement special event filtering ([DW], Meeting Buffer, etc.)
9. 🧪 Test end-to-end workflow with real scheduling scenario

### Phase 3: Advanced Synergies (Weeks 3-4)
10. 🤖 **Use Case #7:** Attendee research pipeline (auto-trigger on new meetings)
11. 🤖 **Use Case #2:** Pre-meeting brief delivery (Howie triggers Zo)
12. 🤖 **Use Case #8:** Email triage & forwarding protocol
13. 🤖 **Use Case #5:** Post-meeting action automation

### Phase 4: Intelligence Features (Month 2+)
14. 🤖 **Use Case #11:** Stakeholder database sync
15. 🤖 **Use Case #4:** Context-aware scheduling triage
16. 🤖 **Use Case #1:** Meeting intelligence feedback loop
17. 🤖 **Use Case #3:** Relationship warming engine

---

## COORDINATION PROTOCOL

### When Zo Can Contact Howie

**Proactive (Zo initiates):**
- Relationship warming suggestions ("Haven't contacted [Person] in 60 days")
- Calendar conflict warnings ("Two high-priority meetings scheduled same time")
- Meeting prep complete notifications ("Brief ready for [Meeting]")
- Follow-up recommendations ("Suggest follow-up with [Person] re: [Topic]")

**Reactive (Zo responds):**
- Howie requests context on person/company
- Howie requests priority comparison for conflicts
- Howie forwards substantive email content

### When Howie Can Contact Zo

**Proactive (Howie initiates):**
- New meeting scheduled (trigger research)
- Meeting rescheduled (update brief if needed)
- Scheduling email contains substantive content (forward for processing)
- No response after follow-up threshold (flag for V's attention)

**Reactive (Howie responds):**
- Zo requests Howie schedule something
- Zo provides context for scheduling decision

### Communication Format

**Subject line format:**
```
[ZO→HOWIE] <Action>: <Brief Description>
[HOWIE→ZO] <Action>: <Brief Description>
```

**Actions:**
- `[REQUEST]` — Asking for something
- `[NOTIFY]` — FYI, no action needed
- `[CONTEXT]` — Providing background info
- `[TRIGGER]` — Initiating automated workflow

**Example:**
```
Subject: [HOWIE→ZO] [TRIGGER] New Meeting: John Smith x Vrijen - 10/18 2pm
Body:
Meeting scheduled with John Smith (john@example.com)
Date: Thursday, October 18, 2025, 2:00 PM ET
Duration: 45 minutes
Tags: [LD-INV]* 
Please generate research brief by 10/17 5pm.
```

---

## QUESTIONS FOR V

1. **Howie configuration:** Do you need specific template/instructions for Howie to populate N5 tags in calendar descriptions, or can Howie infer from this document?

2. **Email forwarding trigger:** Should Howie auto-forward all scheduled meetings to Zo, or only when specific tag used (e.g., `[FWD-Z]`)?

3. **Priority ranking:** For `[GPT-*]` tags, should these override other priority signals, or just inform scheduling preferences?

4. **Stakeholder database:** Should Zo maintain formal stakeholder profiles in N5, or keep this informal/memory-based for now?

5. **Communication frequency:** How often should Zo → Howie relationship warming suggestions happen? Weekly digest? As-needed?

6. **Research timing:** When should Zo trigger research: immediately upon meeting scheduled, or X days before meeting?

---

## SUCCESS METRICS

**Short-term (Month 1):**
- ✅ 100% of Howie-scheduled meetings have N5 tags in calendar descriptions
- ✅ Zo meeting prep digests include all Howie tag context
- ✅ Zero manual tag translation needed

**Mid-term (Month 3):**
- 📊 80% of meeting briefs generated automatically before meeting
- 📊 50% reduction in "unprepared for meeting" situations
- 📊 100% of high-priority relationships contacted within target window

**Long-term (Month 6+):**
- 📊 Howie + Zo handle 90% of scheduling → prep → follow-up cycle automatically
- 📊 V's time spent on scheduling/prep reduced by 75%
- 📊 Relationship intelligence database covers 100% of active stakeholders

---

## SUMMARY

**Tag mapping:** Complete (all 26 V-OS tags mapped to N5 equivalents)  
**Priority system:** Simplified to binary (critical vs non-critical)  
**Translation:** Howie auto-populates calendar descriptions with N5 tags  
**Synergies:** 20 creative use cases identified, prioritized for implementation  
**Protocol:** Clear communication standards for Zo ↔ Howie coordination  

**Next step:** Implement Phase 1 (core harmonization) and test with real scheduling scenario.
