---
description: Weekend cognitive conciliatory - resurface and process week's strategic
  thinking
tags:
- strategic
- review
- weekly
- reflection
tool: true
---
# `weekly-strategic-review`

**Version**: 1.0.0  
**Summary**: Weekend cognitive conciliatory - resurface and process week's strategic thinking

**Schedule**: Every Saturday 12:00 PM ET (proactive notification)

---

## Purpose

The Weekly Strategic Review is your **cognitive conciliatory** - a structured time to:

1. **Resurface topics** from the week's strategic partner sessions
2. **Reconcile contradictions** that emerged during the week
3. **Identify critical decisions** that need resolution
4. **Synthesize patterns** across multiple sessions
5. **Process unresolved tensions** with more time and space
6. **Update topics-to-revisit** based on progress

**This is NOT:**
- A task completion checklist
- A productivity review
- Passive reporting

**This IS:**
- Deep cognitive processing
- Strategic pattern recognition
- Contradiction reconciliation
- Decision-making facilitation
- Proactive cognitive engagement

---

## How It Works

### Proactive Notification (Saturday 12:00 PM ET)

You'll receive:

```
📬 Weekly Strategic Review Ready

This week you had [N] strategic partner sessions:
- [Topic 1] (unresolved tension)
- [Topic 2] (emerging contradiction)
- [Topic 3] (critical decision needed)
- [Topic 4] (pattern noticed)

[N] contradictions detected that need reconciliation:
1. [Contradiction 1]
2. [Contradiction 2]

[N] critical decisions flagged:
1. [Decision 1]
2. [Decision 2]

Ready when you are: weekly-strategic-review
```

**You engage when ready** - notification is non-intrusive, review is optional.

---

## Usage

### Basic: Run Review

```bash
weekly-strategic-review
```

Starts the weekend strategic review process.

### Advanced: Review Specific Week

```bash
weekly-strategic-review --week 2025-10-07
```

Review a specific week's sessions (defaults to current week).

### Advanced: Focus on Contradictions Only

```bash
weekly-strategic-review --contradictions-only
```

Fast-track to contradiction reconciliation.

---

## Review Process

### Phase 1: Week Summary (5 min)

**What happened:**
- [N] strategic partner sessions
- [N] decision memos generated
- [N] insights surfaced
- [N] action items created
- [N] topics added to revisit list

**Session topics:**
- Pricing strategy (2 sessions)
- Partnership evaluation (1 session)
- Product roadmap (1 session)

### Phase 2: Topics to Revisit (10-15 min)

**From topics-to-revisit.jsonl:**

```
High Priority (3 items):
1. TalentOS partnership terms
   - Reason: Exclusivity blind spot, decision deadline approaching
   - Original session: 2025-10-09-session-1
   - Status: Open

2. Pricing strategy validation
   - Reason: TAM assumption unvalidated
   - Original session: 2025-10-08-session-2
   - Status: Open

3. Enterprise vs. B2C strategic focus
   - Reason: Recurring contradiction across sessions
   - Original session: Multiple
   - Status: Open

Medium Priority (2 items):
[...]
```

**For each topic:**
- Review original context
- Assess current state
- Facilitate deeper processing
- Determine if resolved or still open
- Update status

### Phase 3: Contradiction Reconciliation (15-20 min)

**Detected contradictions:**

#### Contradiction 1: Enterprise Ambition vs. SMB Product Reality
**Sessions:** 2025-10-09-session-1, 2025-10-08-session-2

**The Tension:**
- Strategy says: "Pursue enterprise partnerships for scale"
- Product reality: "Built for SMB, 3+ months to enterprise-ready"
- Resource constraint: "4-person team already stretched"

**Processing:**
- What's driving enterprise ambition? (revenue pressure, validation seeking, FOMO)
- What's the true cost of enterprise pivot? (dev time, focus loss, team burnout)
- Is there a middle path? (pilot programs, white-label first, etc.)
- What would resolution look like? (clear strategic choice, resource allocation)

**Facilitation:**
- Apply CHESS_GRANDMASTER style (multi-move thinking)
- Stress test both paths
- Surface hidden assumptions
- Generate decision framework

**Output:**
- Contradiction synthesis document
- Decision framework
- Recommended resolution
- Next actions

#### Contradiction 2: Speed-to-Market vs. Quality-First Messaging
**Sessions:** 2025-10-07-session-3

[Similar structure...]

### Phase 4: Critical Decisions (10-15 min)

**Flagged decisions:**

1. **TalentOS Partnership: Counter-offer decision**
   - Deadline: 2025-10-15 (6 days)
   - Stakes: $200K-500K annual revenue potential
   - Status: Pending negotiation call
   - Decision needed: Go/no-go on counter-offer

   **Decision Support:**
   - Review decision memo from 2025-10-09-session-1
   - Update with any new information
   - Stress test counter-offer terms
   - Generate negotiation talking points
   - Set commitment date

2. **Pricing Strategy: 30% increase timing**
   - Deadline: Q1 2026 planning cycle (6 weeks)
   - Stakes: $300K annual revenue impact
   - Status: Validation experiments not started
   - Decision needed: Proceed, delay, or modify

   [Similar structure...]

### Phase 5: Pattern Synthesis (10 min)

**Patterns noticed across week:**

- **Recurring Theme:** Resource constraints limiting strategic options
  - Appeared in: 3 of 4 sessions
  - Implication: Hiring might be the real strategic priority
  - Question: Should we prioritize team expansion over feature expansion?

- **Strategic Evolution:** Shift from B2C purity to enterprise pragmatism
  - Week 1: "We need to own customer relationship"
  - Week 2: "Maybe white-label isn't so bad"
  - Implication: Strategy evolving, need to formalize new position

- **Decision-Making Pattern:** Analysis paralysis on major decisions
  - TalentOS: 2 weeks, still no counter-offer sent
  - Pricing: 6 weeks discussing, no validation started
  - Implication: Need forcing functions or decision deadlines

**Processing:**
- Are these patterns productive or problematic?
- What's driving them?
- What would shift them?
- Update personal intelligence layer with observations

### Phase 6: Week Ahead Planning (5 min)

**Strategic priorities for next week:**

Based on contradictions, decisions, and patterns:

1. **Priority 1:** TalentOS counter-offer decision (deadline-driven)
2. **Priority 2:** Start pricing validation experiments
3. **Priority 3:** Enterprise vs. SMB strategy resolution
4. **Priority 4:** [Etc.]

**Strategic partner sessions planned:**
- Monday: TalentOS negotiation prep
- Wednesday: Pricing validation design
- Friday: Enterprise strategy clarification

---

## Output Artifacts

### 1. Weekly Review Synthesis
**Location:** `N5/sessions/strategic-partner/weekly-reviews/YYYY-WW-review.md`

Contains:
- Week summary
- Topics processed (with resolution status)
- Contradictions reconciled
- Decisions made
- Patterns synthesized
- Week ahead priorities

### 2. Contradiction Resolution Documents
**Location:** `N5/sessions/strategic-partner/weekly-reviews/YYYY-WW-contradiction-N.md`

For each major contradiction:
- Full context
- Tension analysis
- Decision framework
- Recommended resolution
- Action items

### 3. Updated Topics-to-Revisit
**Location:** `N5/sessions/strategic-partner/topics-to-revisit.jsonl`

Updated with:
- Resolved items (status changed to "closed")
- Updated priorities
- New unresolved items from review
- Next review dates

### 4. Personal Intelligence Deep Update
**Automatic:** My weekly deep intelligence update runs during review

I analyze:
- Patterns across week's sessions
- Style effectiveness
- Breakthrough triggers
- Blind spots recurring
- Most honest assessment refinement

---

## Safety & Control

### Knowledge Write Protection 🔒
- No automatic updates to knowledge base
- Decisions and resolutions staged for approval
- Human-in-the-loop required

### Proactive Engagement Boundaries ⚠️
- Weekly only (not daily intrusions)
- Weekend timing (Saturday noon - when you have space)
- Always optional (notification, not forced)
- You control when to engage

### Personal Intelligence Update 🧠
- I run weekly deep update during review
- Autonomous analysis of week's patterns
- You can request to see my observations
- You control what propagates to official knowledge

---

## Integration Points

### With Strategic Partner
- Reviews all sessions from the week
- Synthesizes across multiple dialogues
- Identifies patterns in your thinking

### With Reflection Synthesizer
- Reviews accumulated decision memos
- Synthesizes insights across memos
- Tracks action item completion

### With Topics-to-Revisit
- Primary input source
- Updates status during review
- Closes resolved items
- Adds new items

### With Personal Intelligence
- Triggers weekly deep update
- Cross-session pattern analysis
- Style effectiveness learning
- Honest assessment refinement

---

## Scheduled Task

**Schedule:** Every Saturday at 12:00 PM ET

**Task:**
```bash
# Automated notification
weekly-strategic-review --notify

# When you engage
weekly-strategic-review
```

**Can be rescheduled:**
```bash
# Change to different time
update-scheduled-task weekly-strategic-review --time "14:00"

# Change to different day
update-scheduled-task weekly-strategic-review --day "Sunday"
```

---

## Examples

### Example: October Week 2 Review

**Notification received:**
```
📬 Weekly Strategic Review Ready

This week you had 4 strategic partner sessions covering:
- TalentOS partnership evaluation (unresolved)
- Pricing strategy analysis (critical decision needed)
- Product roadmap prioritization (emerging contradiction)
- Fundraising timeline (pattern noticed)

3 contradictions detected:
1. Enterprise ambition vs. SMB product focus
2. Speed-to-market vs. quality-first messaging
3. Investor timeline vs. product readiness

2 critical decisions flagged:
1. TalentOS counter-offer (deadline: Oct 15)
2. Pricing 30% increase timing (Q1 planning)

Ready when you are: weekly-strategic-review
```

**You run review:**
```bash
weekly-strategic-review
```

**Review session (45-60 min):**
- Process 5 high-priority topics
- Reconcile enterprise vs. SMB contradiction → Decision framework generated
- Make TalentOS counter-offer decision → Negotiation talking points ready
- Identify resource constraint pattern → Hiring priority surfaced
- Plan week ahead with 3 strategic priorities

**Outputs:**
- Weekly review synthesis (3 pages)
- 3 contradiction resolution documents
- 2 decision frameworks
- Updated topics-to-revisit (7 items closed, 4 still open)
- My weekly deep intelligence update (autonomous)

---

## Quality Standards

### Review Depth
- **Not superficial:** Deep processing, not checkbox review
- **Pattern recognition:** Cross-session synthesis
- **Decision facilitation:** Generate frameworks, not just lists
- **Contradiction reconciliation:** Genuine resolution attempts

### Time Investment
- **Target:** 45-60 minutes per week
- **Flexible:** Can be split across weekend
- **Optional:** Skip weeks when not needed
- **Valuable:** Should feel like strategic clarity, not burden

### Voice & Tone
- **Reflective:** Thoughtful, not rushed
- **Challenging:** Still applies strategic partner principles
- **Supportive:** Weekend space, not pressure
- **Honest:** Surface uncomfortable truths

---

## Notes

The Weekly Strategic Review is **Phase 3** of the Strategic Partner system. It closes the loop on:
- Strategic thinking (Phase 1: Strategic Partner)
- Structured outputs (Phase 2: Reflection Synthesizer)
- **Long-term processing (Phase 3: Weekly Review)**

**Key principle:** Not all strategic thinking resolves in a single session. Some contradictions need time, some patterns need multiple data points, some decisions need space to breathe.

The weekly review provides that space - a structured time to revisit, reflect, reconcile, and resolve.

---

*The Weekly Strategic Review: Where strategic sessions become strategic clarity.*
