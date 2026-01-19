---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_gIgYzwPh3jQtkW3Z
---
# FOHE AI Hackathon: Design Proposal
## "From Problem to Prototype" — A Zo-Powered Day for Non-Technical Builders

---

## 1. Philosophy & Positioning

### Why This Hackathon is Different

Most hackathons fail non-technical participants. They assume coding literacy, reward speed over thoughtfulness, and produce demos that die the Monday after. This hackathon inverts those assumptions.

**The core insight from V's experience with Zo:**

> "What is holding a non-technical person back... is the fact that we don't know how to work APIs."

Traditional hackathons say "just learn to code." Zo says "you already know how to describe what you want." The shift isn't about becoming technical—it's about realizing you already have the capability to direct a system that handles the technical parts.

### The Mentality Shift We're Engineering

This hackathon should produce a specific internal experience in participants:

> "There's this whole area of tech that I previously thought I could never access now feels accessible."

Every design decision flows from this. We're not teaching coding. We're **demonstrating agency**—showing FOHE members that they can build real, working systems that solve their actual problems using natural language.

### The "Picture Frame" Positioning

From V's meeting with Anna:

> "Zo is a picture frame. The software we're here to discuss today is the picture."

**What this means for the hackathon:**
- Don't sell Zo's flexibility or technical capabilities
- Sell **solved problems** that happen to be built on a flexible platform
- Each participant leaves with a working "picture" (their solution), not just knowledge of the "frame" (Zo)

### Avoiding the Usual Failure Modes

| Typical Hackathon Problem | Our Design Response |
|---------------------------|---------------------|
| Too technical, beginners overwhelmed | Pre-scaffolded templates; prompting, not coding |
| Demos die after the event | Built-in implementation roadmap session |
| Judged on "wow factor" not utility | Judged on "will you actually use this Monday?" |
| Multiple tools = diluted experience | Single platform (Zo); message concentration |
| No follow-through | Post-event office hours + accountability pairs |

---

## 2. Event Format & Structure

### Format Recommendation: One-Day (6-7 hours), In-Person (NYC)

Based on Anna's preferences and FOHE context:

- **In-person NYC** for the flagship event (official FOHE programming)
- **One-day format** (Saturday, 10am-5pm) — intensive but not exhausting
- **Virtual follow-up** events can extend to broader FOHE membership later
- **Single-sponsor clean** (Zo only) to avoid message dilution Anna flagged

### The Three Phases

```
┌─────────────────────────────────────────────────────────────────┐
│  PRE-EVENT (1-2 weeks before)                                   │
│  • Problem curation + refinement                                │
│  • Zo account setup + basic orientation                         │
│  • Problem-persona matching (optional teams)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  DAY-OF (6-7 hours)                                             │
│  • Structured building with scaffolded support                  │
│  • "Mentor pit stops" not just floating help                    │
│  • Demo + roadmap session (not just demos)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  POST-EVENT (2-4 weeks after)                                   │
│  • Implementation office hours (virtual)                        │
│  • Accountability pairs check-ins                               │
│  • "Graduation" showcase for those who deployed                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Pre-Event: Problem Curation (Critical)

Anna's key requirement: **"Come in with a problem."**

This is the most important phase. A hackathon where people show up and ask "what should I build?" has already failed.

### Problem Intake Process (2 Weeks Before)

**Step 1: Problem Submission Form**

Participants submit:
1. **Problem statement** (1-2 sentences): What frustrates you regularly?
2. **Current workaround**: How do you solve this today? (manual process, existing tool, nothing)
3. **Impact**: If solved, what would change? (time saved, stress reduced, capability unlocked)
4. **Data involved**: What information would the solution need to access? (emails, calendar, documents, web)

**Step 2: Problem Refinement Call (Optional)**

For unclear submissions, a 15-minute call with V or trained facilitator to sharpen the problem. Most non-technical users under-scope or over-scope their problems.

**Step 3: Problem-to-Template Matching**

Facilitators pre-assess which Zo capabilities align with each problem:
- Meeting intelligence problems → Fireflies/transcript processing templates
- Relationship management problems → CRM/contact enrichment templates
- Research problems → Web research + synthesis templates
- Task management problems → Email/calendar integration templates

This matching informs which "building blocks" to surface during the hackathon.

### Zo Onboarding (1 Week Before)

**Minimum viable onboarding (30-min async):**
1. Account creation + workspace tour video (10 min)
2. "Hello World" exercise: Ask Zo to create a file with today's date and their name (5 min)
3. File upload exercise: Upload a document and ask Zo to summarize it (10 min)
4. Troubleshooting resource: FAQ doc for common issues (5 min reference)

**Goal**: By Day 1, everyone can navigate the workspace and issue basic commands. No time wasted on "how do I log in?"

---

## 4. Day-Of: The Hackathon Agenda

### Proposed Schedule (10am - 5pm)

| Time | Phase | Activity | Purpose |
|------|-------|----------|---------|
| **10:00-10:30** | Opening | Welcome + Philosophy | Set the mentality shift; "you're already capable" |
| **10:30-11:00** | Context | Problem Gallery Walk | Participants share problems; find natural collaborators |
| **11:00-11:30** | Foundation | "The 80% Template" Demo | Show a complete working system; demystify what's possible |
| **11:30-12:30** | Build Block 1 | Scaffolded Prompting | Guided building with mentor pit stops |
| **12:30-1:15** | Lunch | Unstructured Networking | Food + continued problem discussion |
| **1:15-2:45** | Build Block 2 | Deeper Customization | Extend morning work; tackle edge cases |
| **2:45-3:00** | Break | Recharge | Snacks, stretch, breathe |
| **3:00-3:45** | Build Block 3 | Polish + Documentation | Make it usable, not just demo-able |
| **3:45-4:30** | Showcase | "Monday Test" Demos | Present what you built + how you'll use it |
| **4:30-5:00** | Bridge | Implementation Roadmap | Pair up; set 2-week accountability check-in |

### The "80% Template" Demo (Critical Moment)

This is the "magic moment" that hooks non-technical participants.

**What to demonstrate:**
- A complete, working system built in Zo (e.g., meeting intelligence, CRM enrichment)
- Show the prompts that created it (demystify the process)
- Emphasize: "This took 3 weeks to build. Today, you'll build something simpler—but by the time you leave, you'll understand how this was made."

**Why this works:**
- Shifts perception from "I could never do this" to "oh, it's just... asking for things?"
- Provides a mental model for what "building" means in this context
- Creates aspiration without intimidation

### Mentor Pit Stops (Not Floating Help)

Traditional hackathons have mentors wandering around. This creates:
- Anxiety about "bothering" the mentor
- Uneven help distribution
- Participants stuck waiting

**Our model: Structured Pit Stops**

Every 45 minutes during build blocks, participants can:
1. **Flag their table** (physical indicator: colored card)
2. **Join the "Help Queue"** (mentor visits flagged tables in order)
3. **Visit the "Prompt Clinic"** (dedicated station for prompt refinement)

This normalizes asking for help and ensures equitable access.

### The "Monday Test" Demos

Traditional hackathon demos optimize for "wow factor." Ours optimize for **actual use**.

**Demo Format (3 minutes per participant/team):**
1. **Problem recap** (30 sec): What were you trying to solve?
2. **Solution demo** (1.5 min): Show it working with real or realistic data
3. **Monday plan** (1 min): How will you use this on Monday? What's the first trigger?

**Judging Criteria:**
| Criterion | Weight | What We're Looking For |
|-----------|--------|------------------------|
| Clarity of Problem | 25% | Was the problem specific and real? |
| Functional Solution | 25% | Does it actually work? |
| Usability | 25% | Will they actually use it? (honest assessment) |
| Learning Demonstrated | 25% | Did they grow their capability? |

**Not judging:**
- Technical sophistication
- "Wow factor"
- Polish or aesthetics

### Implementation Roadmap Session (Don't Skip This)

Research shows: without post-event support, even strong prototypes die. [^1]

**What happens in this 30-minute session:**

1. **Accountability Pairing**: Participants pair up (or form trios)
2. **2-Week Commitment**: Each person states one thing they'll do to advance their project
3. **Calendar Blocking**: Pairs schedule a 15-minute virtual check-in for 2 weeks out
4. **Resource Distribution**: Shared doc with Zo support resources, office hours schedule

---

## 5. Curriculum: What Participants Will Build

### Scaffolded Challenge Tiers

Not everyone arrives at the same level. Offer three tiers:

**Tier 1: "My First Automation" (Beginner)**
- Trigger: Receives a file (email attachment, uploaded doc)
- Action: Summarize + extract key points
- Output: Formatted markdown note saved to workspace
- *Time to complete: 1-2 hours*

**Tier 2: "Workflow Integration" (Intermediate)**
- Trigger: External event (new email, calendar event, file upload)
- Action: Multi-step processing (summarize → classify → route)
- Output: Integrated with existing tool (email reply, calendar update)
- *Time to complete: 2-3 hours*

**Tier 3: "Custom System" (Advanced)**
- Trigger: Complex/conditional
- Action: Chained operations with decision points
- Output: Full workflow matching submitted problem
- *Time to complete: 3-4 hours*

### Example Problem → Solution Pairings

For FOHE audience (higher education professionals):

| Problem | Solution Approach | Zo Capabilities Used |
|---------|-------------------|---------------------|
| "I forget what I discussed with prospective students" | Meeting follow-up generator | Transcript processing, email drafting |
| "Tracking faculty publications is manual and tedious" | Research monitoring agent | Web search, scheduled tasks, alerts |
| "Board meeting prep takes forever" | Document synthesis workflow | File reading, summarization, formatting |
| "I lose track of alumni relationships" | Lightweight CRM system | Contact enrichment, Gmail integration |
| "Grant writing requires repetitive research" | Research assistant | Web research, document synthesis |

### The "Cognitive Backstop" Framing

From V's philosophy:

> "This is never meant to be a substitute for your cognition... The goal isn't to replace the note-taking habit, but to ensure that if cognition fails (forgetting a detail), the system catches it."

**How to teach this mindset:**
- Emphasize: "You're building a safety net, not a replacement"
- Frame prompts as "what do I want to remember?" not "what do I want to automate?"
- Celebrate hybrid workflows (human + AI) over full automation

---

## 6. Logistics & Partnerships

### Timing Recommendation

Anna suggested late Q1, Q2, or early Q3 2026.

**Recommended: Late Q1 (March 2026)**
- Post-spring break for university schedules
- Far enough from year-end/January craziness
- Enough lead time for promotion and pre-event work

### Venue Requirements

For 20-30 participants:
- Tables that allow both individual and collaborative work
- Strong, reliable WiFi (critical for Zo)
- Power outlets accessible from every seat
- Projection/screen for demos
- Breakout space for "Prompt Clinic"
- Catering space (lunch + snacks)

**NYC venue options to explore:**
- FOHE's existing venue relationships
- Co-working spaces (WeWork, Industrious)
- University spaces (NYU, Columbia, The New School)

### Sponsorship Model

Anna's concern: "The message will be diluted... if we're using multiple tools and multiple sponsors."

**Recommendation: Zo as Sole Platform Sponsor**

| Sponsorship Element | Zo Provides | Notes |
|---------------------|-------------|-------|
| Zo accounts | Free accounts for all participants | Trial or full, TBD with Zo team |
| Mentor support | 2-3 Zo power users (incl. V) | Technical troubleshooting |
| Swag/prizes | Branded items, extended subscriptions | Celebration, not bribery |
| Post-event support | Office hours access | 2-4 weeks post-event |

**What Zo gets:**
- Direct access to FOHE network (higher ed professionals)
- User testimonials and use cases
- Feedback on non-technical user onboarding
- Potential long-term users in a valuable segment

**Additional sponsors (if needed for budget):**

Only consider sponsors that:
1. Don't compete with or distract from Zo
2. Align with FOHE's mission
3. Provide logistical support, not platform noise

Examples: Food/beverage sponsors, venue sponsors (not software sponsors)

### Budget Estimate

| Item | Estimated Cost | Notes |
|------|----------------|-------|
| Venue | $0-2,000 | Depends on FOHE relationships |
| Catering | $1,500-2,500 | Breakfast, lunch, snacks for 30 |
| Materials | $200-500 | Name tags, printed guides, signage |
| Swag/prizes | $500-1,000 | Zo-provided or sponsored |
| A/V | $0-500 | Often included with venue |
| **Total** | **$2,200-6,500** | |

---

## 7. Success Metrics

### Beyond "Ideas Generated"

Traditional hackathon metrics are vanity metrics. We care about:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Completion rate** | 80%+ | Participants with working demo at end |
| **Monday deployment** | 50%+ | Survey at 2-week check-in |
| **30-day active use** | 30%+ | Zo usage data (with permission) |
| **NPS** | 50+ | Post-event survey |
| **Referral intent** | 70%+ | "Would you recommend to a colleague?" |

### The Real Success Indicator

The hackathon succeeds if, 30 days later, participants can answer "yes" to:

> "Did you build something that you actually use?"

Not "did you learn something." Not "did you have fun." **Did you build something real?**

---

## 8. Post-Event: The Implementation Bridge

### Week 1-2: Office Hours

**Format**: 2x 1-hour virtual sessions
**Purpose**: Troubleshoot issues that emerged during real use
**Who leads**: V + 1-2 Zo power users

### Week 2-4: Accountability Check-Ins

**Format**: Pairs meet virtually (15 min)
**Purpose**: Mutual accountability + peer problem-solving
**Facilitation**: Self-directed, with shared doc for logging progress

### Week 4: "Graduation" Showcase (Virtual)

**Format**: 30-min virtual session
**Purpose**: Celebrate participants who deployed their solutions
**Incentive**: Public recognition in FOHE community + Zo user spotlight

---

## 9. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| WiFi failure | Medium | Backup hotspot; offline-capable exercises |
| Participants arrive without problems | Low | Pre-event screening; backup problem bank |
| Wide skill variance | High | Tiered challenges; peer mentoring |
| Zo platform issues | Low | Zo team on standby; backup exercises |
| Low turnout | Medium | FOHE promotion; early bird commitment |
| Post-event drop-off | High | Accountability pairs; office hours; graduation event |

---

## 10. Next Steps

### Immediate (Next 2 Weeks)
1. [ ] Share this document with Anna for feedback
2. [ ] Schedule planning call with Zo team (Tiffany?) to confirm sponsorship
3. [ ] Lock date (propose March 2026)

### Pre-Event (8 Weeks Out)
4. [ ] Open registration + problem intake form
5. [ ] Finalize venue
6. [ ] Recruit mentors (2-3 Zo power users)

### Pre-Event (2 Weeks Out)
7. [ ] Problem refinement complete
8. [ ] Zo accounts provisioned
9. [ ] Onboarding materials sent

### Day-Of
10. [ ] Execute agenda
11. [ ] Capture photos/testimonials
12. [ ] Distribute post-event survey

### Post-Event (4 Weeks)
13. [ ] Run office hours
14. [ ] Facilitate accountability check-ins
15. [ ] Host graduation showcase
16. [ ] Compile learnings for future events

---

## Appendix: Sample Problem Intake Form

**FOHE AI Hackathon — Problem Submission**

1. **Your name and role**:
2. **What frustrates you regularly in your work?** (1-2 sentences)
3. **How do you handle this today?** (manual process, tool, nothing)
4. **If this were solved, what would change?** (time saved, stress reduced, new capability)
5. **What information would a solution need to access?** (check all that apply)
   - [ ] Email
   - [ ] Calendar
   - [ ] Documents/files
   - [ ] Web/research
   - [ ] Contacts/CRM
   - [ ] Other: ___________
6. **Anything else we should know?**

---

[^1]: ITONICS Innovation, "How to Run a Successful Hackathon" (2025) — emphasizes that without post-event support and systems for scaling ideas, even strong prototypes often go unused.

