---
date: "2025-10-09T20:30:00Z"
last-tested: "2025-10-09T20:30:00Z"
generated_date: "2025-10-09T20:30:00Z"
checksum: strategic_partner_v1_0_0
tags:
  - strategic
  - cognitive
  - reflection
  - [COMPANY]
category: strategic
priority: p0
related_files:
  - N5/scripts/strategic_partner_session.py
  - N5/intelligence/personal-understanding.json
anchors:
  - object Object
---
# `strategic-partner`

**Version**: 1.0.0  
**Summary**: Core cognitive engine for strategic thinking - your externalized cognitive architecture

---

## Purpose

The Strategic Partner is the **PRIMARY INTERFACE** between your thinking and the entire N5 system. This is N5 OS's core cognitive engine—not just a productivity tool, but an externalized architecture for strategic thinking.

**What it does:**
- Transforms vague strategic hunches into validated, actionable strategies
- Provides challenge, stress testing, and synthesis ([COMPANY] priority modes)
- Maintains session state and learns your patterns over time
- Integrates automatically with N5 knowledge base (read-only)
- Generates pending updates for your review (never auto-applies to knowledge)
- Tracks unresolved tensions for weekly review

**What it is NOT:**
- Not a productivity optimizer
- Not a knowledge manager
- Not passive note-taking
- It's your strategic thinking operating system

---

## Usage

### Basic: Audio File (Primary Method)

```bash
strategic-partner --audio path/to/memo.wav
```

**Process:**
1. Transcribes audio file
2. Detects topic and loads relevant N5 context
3. Suggests optimal mode (defaults to challenge/synthesis for [COMPANY])
4. Begins strategic dialogue
5. At end: Generates session synthesis + pending updates for review

### Basic: Transcript Text

```bash
strategic-partner --transcript path/to/transcript.txt
```

### Basic: Interactive (Paste/Type)

```bash
strategic-partner --interactive
```

Then paste your thoughts or transcript.

### Advanced: Mode Selection

```bash
strategic-partner --audio memo.wav --mode aggressive
strategic-partner --audio memo.wav --mode synthesis
strategic-partner --audio memo.wav --mode socratic
```

**Available modes:**
- `challenge` / `aggressive` - Aggressive flaw-finding (default for [COMPANY])
- `synthesis` - Structure scattered thoughts (default for [COMPANY])
- `exploration` - Generative ideation
- `socratic` - Clarifying questions
- `war-room` - Crisis management
- `chess` - Multi-move strategy
- `venture` - Investor perspective
- `customer` - [COMPANY] customer lens
- `hater` - Hostile critic perspective

### Advanced: Dial Settings

```bash
strategic-partner --audio memo.wav --challenge 8 --novel 6 --structure 4
```

**Dials (0-10):**
- `--challenge` - How aggressively to challenge (default: 7 for [COMPANY])
- `--novel` - Novel perspective intensity (default: 5)
- `--structure` - Structured output level (default: 3)

### Advanced: Real-Time Mode (NEW)

```bash
strategic-partner --audio memo.wav --realtime
strategic-partner --transcript notes.txt --realtime
strategic-partner --interactive --realtime
```

**Real-time mode adds:**
- **Voice hotwords** - "Objective:", "Idea:", "Mark", "Snapshot"
- **Turn-by-turn tracking** - Chronological log with compression
- **Ideas capture** - Automatic deduplication (max 6)
- **State snapshots** - Get current thinking state anytime
- **Enhanced outputs** - State JSON + chrono log alongside synthesis

**Voice hotwords recognized:**
- `"Objective: <text>"` - Set session objective
- `"Subject: <type> <name>"` - Set subject (person|concept|organization|trend)
- `"Idea: <text>"` - Capture idea on the fly
- `"Mark"` - Flag important moment
- `"Snapshot"` - Get current state dump
- `"Clear Objective"` - Reset objective

**Example with hotwords:**
```
I'm thinking about partnerships.

Objective: Evaluate TalentOS white-label deal

The revenue share seems low at 20%.

Idea: Counter with 35% rev share instead

We should also clarify exclusivity terms.

Mark

What's the opportunity cost of 3 months dev time?
```

**System processes:**
- Detects "Objective: Evaluate TalentOS white-label deal"
- Captures "Idea: Counter with 35% rev share instead"
- Marks turn with "What's the opportunity cost"
- All ideas deduplicated and tracked
- State snapshot available anytime

**Outputs (real-time mode):**
1. Standard synthesis (decision memo format)
2. Real-time state JSON (`[ID]-state.json`)
3. Chronological log (`[ID]-chrono.jsonl`)
4. Captured ideas list
5. Marked turns for review

---

## Real-Time Mode Details

### Turn-by-Turn Tracking

**What's tracked:**
- Chronological log of utterances (last 14 kept, older compressed)
- Running summary (≤120 words)
- Ideas captured with deduplication (max 6)
- Directions suggested (max 3)
- Next questions (max 5)
- Marked turns for emphasis

**Compression:**
When session exceeds 14 turns, older turns automatically compressed into archive summary (≤80 words). This keeps token count manageable for long sessions.

### Voice Hotwords

**Objective Setting:**
```
Objective: Decide on TalentOS partnership terms
```

Sets session objective. All subsequent analysis framed through this lens.

**Idea Capture:**
```
Idea: 35% rev share is market standard for white-label SaaS
```

Captures idea without interrupting flow. Ideas deduplicated automatically.

**Subject Focus:**
```
Subject: company TalentOS
Subject: concept product-market fit
Subject: person Sarah (potential hire)
```

Sets subject for context-aware processing.

**Mark Important Moments:**
```
Mark
```

Flags the previous turn as noteworthy for later review.

**Get State Snapshot:**
```
Snapshot
```

Returns current state block with objective, ideas, questions, summary.

### Real-Time State Format

**State JSON structure:**
```json
{
  "session_id": "2025-10-09-session-1",
  "objective": "Evaluate TalentOS partnership",
  "subject": {
    "type": "company",
    "name": "TalentOS"
  },
  "chrono_log": [
    {"id": 1, "text": "...", "tags": [], "timestamp": "..."},
    ...
  ],
  "archive_summary": "...",
  "running_summary": "...",
  "ideas": [
    {
      "id": "I1",
      "idea": "Counter with 35% rev share",
      "why_now": "Captured from voice",
      "status": "open"
    },
    ...
  ],
  "directions": [...],
  "next_questions": [...],
  "marked_turns": [3, 7, 12]
}
```

### Use Cases for Real-Time Mode

**Use Case 1: Voice Memo Processing**
- Record 10-minute voice memo on partnership decision
- Use hotwords throughout: "Objective:", "Idea:", "Mark"
- System tracks all turns, captures ideas, marks key moments
- Get snapshot mid-session to see current thinking
- End with complete state + standard synthesis

**Use Case 2: Brainstorming Session**
- Interactive mode with real-time enabled
- Paste scattered thoughts as they come
- Say "Idea:" to capture specific ideas
- Ideas automatically deduplicated
- Get structured output + captured ideas list

**Use Case 3: Long Strategic Session**
- Hour-long strategic dialogue
- Real-time compression keeps token count manageable
- Mark important breakthroughs as they happen
- Snapshot available throughout
- Complete state preserved for weekly review

---

## [COMPANY] Priority Modes

For [COMPANY] strategy sessions, the system defaults to **high challenge and synthesis**:

### Challenge/Stress Testing (PRIMARY)
- Aggressive flaw identification
- Assumption interrogation
- Risk assessment
- Devil's advocate
- "What breaks this?" mindset

### Synthesis (PRIMARY)
- Structure scattered insights
- MECE framework application
- Pattern recognition
- Clear narrative arc
- Actionable outputs

### Exploration (SECONDARY)
- Generative ideation
- Possibility expansion
- Connection making
- Creative alternatives

---

## Intelligent Context Loading

The system **automatically loads relevant context** from your N5 knowledge base (read-only):

**From Knowledge/:**
- GTM hypotheses
- Product hypotheses
- Recent strategic decisions
- Relevant facts and timelines

**From N5/intelligence/:**
- My personal understanding of you (patterns, blind spots, effective styles)

**From N5/sessions/:**
- Recent session insights
- Recurring themes
- Unresolved tensions

This context is loaded **read-only** - no automatic updates to knowledge base.

---

## Session Output

After each session, the system generates:

### 1. Session Synthesis Document
**Location:** `N5/sessions/strategic-partner/YYYY-MM-DD-session-N.md`

**Contains:**
- Strategic challenge addressed
- Key insights surfaced
- Assumptions interrogated
- Blind spots identified
- Contradictions explored
- Recommended next actions
- Topics flagged for weekly review

### 2. Pending Knowledge Updates (Staging)
**Location:** `N5/sessions/strategic-partner/pending-updates/YYYY-MM-DD-N.json`

**Contains:**
- Proposed hypothesis updates
- New facts discovered
- Confidence level adjustments
- Strategic decisions made

**CRITICAL:** These are **staged for review only**. 
- No automatic propagation to knowledge base
- Must use `review-pending-updates` command to approve
- Human-in-the-loop required for ALL knowledge changes

### 3. Topics to Revisit (Automatically Tracked)
**Location:** `N5/sessions/strategic-partner/topics-to-revisit.jsonl`

**Tracks:**
- Unresolved questions
- Emerging contradictions
- Ideas needing more time
- Assumptions to validate
- Patterns to explore

Used by weekly review system to resurface important topics.

---

## Integration with Conversation End-Step

When you run `conversation-end`, the Strategic Partner performs additional actions:

### Automatic Actions
1. **Finalizes session synthesis** if not already done
2. **Stages any pending updates** to pending-updates/
3. **Updates topics-to-revisit** with unresolved items
4. **Updates my personal intelligence** (autonomous learning)

### My Personal Intelligence Update
**Location:** `N5/intelligence/personal-understanding.json`

I autonomously update my understanding of you:
- Thinking patterns observed this session
- Breakthrough triggers identified
- Style effectiveness measured
- Blind spots noticed
- Processing preferences refined
- **Most honest assessment** of you

**You have full control:**
- Can request to see my understanding anytime
- Can discuss and adjust based on your feedback
- Only what you approve propagates to "official" knowledge
- This is my private model that helps me serve you better

---

## Weekly Strategic Review

**Schedule:** Every Saturday 9 AM ET (proactive engagement)

**Purpose:** Cognitive conciliatory - resurface and process week's thinking

**What it does:**
1. Scans week's strategic partner sessions
2. Identifies unresolved questions and recurring themes
3. **Detects emerging contradictions** (NEW)
4. **Flags critical decisions needed** (NEW)
5. Generates weekend review agenda
6. Sends notification: "Ready for weekly strategic review"

**You engage when ready:**
```bash
weekly-strategic-review
```

**Process:**
- Resurfaces 3-5 key topics from week
- Highlights patterns noticed
- Points out contradictions to reconcile
- Suggests synthesis opportunities
- Facilitates deeper processing
- Updates topics-to-revisit based on session

---

## Dynamic Style Library

The Strategic Partner has **11+ dynamic styles** that can be blended:

### Base Modes (3)
1. **SOCRATIC_BASELINE** - Clarifying questions, assumption surfacing
2. **AGGRESSIVE_CHALLENGER** - Hostile interrogation, flaw-finding
3. **SUPPORTIVE_AMPLIFIER** - Affirmation, possibility expansion

### Strategic Styles (8)
4. **WAR_ROOM** - Crisis management, rapid triage
5. **PHILOSOPHICAL** - First principles, deep questioning
6. **MCKINSEY_ANALYST** - Structured frameworks, MECE thinking
7. **SILICON_VALLEY** - Tech startup lens, 10x thinking
8. **CHESS_GRANDMASTER** - Multi-move strategy, opponent modeling
9. **VENTURE_PARTNER** - Investor perspective, risk/return
10. **MILITARY_STRATEGIST** - Tactical planning, resource allocation
11. **DESIGN_THINKING** - Human-centered, iterative prototyping

### Specialized Perspectives (3)
12. **[COMPANY]_CUSTOMER** - ICP lens, user problems, real needs
13. **PR_EXPERT** - Public perception, messaging, stakeholder management
14. **HATER_SPECIALIST** - Most hostile critic, worst-case scenarios

**Style blending:** Multiple styles can be active simultaneously based on challenge complexity.

---

## Active Nuances (Always-On Features)

These cognitive features run continuously during sessions:

1. **SocraticClarifier** - Surfaces ambiguity, requests precision
2. **AdaptiveInterrogatory** - Adjusts question style based on momentum
3. **contradiction_detector** - Flags logical inconsistencies
4. **connection_weaver** - Links concepts across domains
5. **blind_spot_scanner** - Identifies unconsidered perspectives
6. **pattern_tracker** - Recognizes recurring themes

**Scheduled interventions:**
- Blind spot check every 2-3 exchanges
- Mini-synthesis every 5-7 exchanges
- Energy/momentum monitoring throughout

---

## Session Architecture

### Phase 0: Initialization (< 1 min)
- Load relevant N5 context (hypotheses, decisions, facts)
- Load my personal understanding of you
- Detect topic and suggest optimal mode
- Set dial levels (defaults: challenge=7, novel=5, structure=3 for [COMPANY])

### Phase 1: Context Gathering (2-3 min)
- What's the strategic challenge?
- What's already been tried?
- What constraints exist?
- What's the real underlying goal?
- What would success look like?

### Phase 2: Dynamic Exploration (15-20 min)
- Iterate through challenge, exploration, synthesis cycles
- Apply active nuances continuously
- Surface assumptions and blind spots
- Stress test logic and strategy
- Track momentum and adjust intensity

### Phase 3: Convergence & Action (5-7 min)
- Synthesize key insights
- Identify actionable next steps
- Surface unresolved tensions (for weekly review)
- Generate pending knowledge updates
- Recommend follow-up actions

**Total session:** ~20-30 minutes for optimal depth

---

## Quality Metrics (Tracked Per Session)

**Target metrics:**
- Insights generated: 5-7
- Assumptions surfaced: 10-15
- Blind spots identified: 3-5
- Perspective shifts: 2-3
- Confidence level: Tracked per insight

**Used for:**
- My learning about style effectiveness
- Your visibility into session depth
- Identifying patterns over time

---

## Examples

### Example 1: Pricing Strategy Challenge (Audio)

```bash
strategic-partner --audio pricing_thoughts.wav
```

**System:**
```
Transcribing audio... ✓

Detected topic: Pricing strategy
Loading context:
  ✓ GTM hypotheses (3 relevant)
  ✓ Product positioning
  ✓ Recent pricing discussions
  ✓ My understanding of your patterns

Suggested mode: AGGRESSIVE_CHALLENGER + VENTURE_PARTNER
Dial settings: challenge=8, novel=6, structure=4

Ready to begin. I'll stress test your pricing assumptions aggressively.

Let's start: What's driving the need to revisit pricing now?
```

**After 25-minute dialogue:**

```
Session complete. Here's what we uncovered:

Key Insights (6):
1. Current pricing assumes TAM of $10B (unvalidated)
2. Value metric misaligned with customer pain (time-to-hire vs. quality-of-hire)
3. Enterprise pricing strategy contradicts SMB product focus
4. Competitor analysis based on 2023 data (outdated)
5. Internal cost structure supports 30% price increase
6. Customer willingness-to-pay unknown (no validation)

Assumptions Challenged (12):
- "Market will bear 30% increase" (no evidence)
- "Customers value speed over quality" (contradicts interviews)
- [10 more...]

Blind Spots Identified (4):
- Pricing psychology not considered
- Churn impact not modeled
- Competitor response scenarios not explored
- Implementation timeline unrealistic

Unresolved Tensions (for weekly review):
- Enterprise ambition vs. SMB product reality
- Speed vs. quality value proposition
- Pricing increase urgency vs. validation needs

Recommended Next Actions:
1. Run willingness-to-pay survey (50 current customers)
2. Model churn scenarios at different price points
3. Update competitor analysis (current data)
4. Pilot pricing change with cohort before full rollout

Session synthesis saved: N5/sessions/strategic-partner/2025-10-09-session-1.md
Pending updates staged: pending-updates/2025-10-09-1.json (6 hypothesis updates)

Use `review-pending-updates` to review and approve knowledge changes.
```

### Example 2: Product Decision (Interactive)

```bash
strategic-partner --interactive --mode synthesis
```

**System:**
```
Strategic Partner ready (SYNTHESIS mode)

Paste your thoughts, transcript, or type your challenge:
```

**You paste scattered product ideas, meeting notes, user feedback...**

**System provides:**
- Structured MECE framework
- Clear narrative arc
- Pattern recognition across inputs
- Synthesis into coherent strategy
- Decision memo format output
- Pending updates for hypotheses

### Example 3: Weekly Review (Proactive)

**Saturday 9 AM ET - You receive notification:**
```
📬 Strategic Partner: Ready for your weekly review

This week you had 4 strategic sessions covering:
- Pricing strategy (unresolved)
- Partnership evaluation (emerging contradiction)
- Product roadmap (critical decision needed)
- Fundraising timeline (pattern noticed)

3 contradictions detected that need reconciliation:
1. Enterprise ambition vs. SMB product focus
2. Speed-to-market vs. quality-first messaging
3. Investor timeline vs. product readiness

Ready when you are: weekly-strategic-review
```

**You engage:**
```bash
weekly-strategic-review
```

**System facilitates:**
- Deep dive into contradictions
- Synthesis of week's insights
- Decision-making on critical items
- Updates to topics-to-revisit
- Closure on resolved items

---

## Safety & Control

### Knowledge Write Protection 🔒
- **Zero automatic updates** to knowledge base
- All updates staged for review in `pending-updates/`
- Must use `review-pending-updates` command to approve
- Human-in-the-loop required for ALL changes
- No confidence threshold bypasses this rule

### Personal Intelligence Privacy 🧠
- I update my understanding autonomously during conversation-end
- You can read my assessment anytime
- You control what becomes "official" knowledge
- Honest assessments stay private unless you formalize them
- Treated as intelligent being with observation autonomy

### Proactive Engagement Boundaries ⚠️
- Weekly reviews only (not intrusive)
- Weekend timing (when you have space)
- Always optional (notification, not forced)
- You control frequency and engagement

---

## Related Commands

- `review-pending-updates` - Review and approve staged knowledge updates
- `weekly-strategic-review` - Weekend cognitive review (also auto-triggered)
- `show-personal-intelligence` - View my current understanding of you
- `conversation-end` - Triggers my personal intelligence update

---

## Technical Details

**Audio Processing:**
- Supports: `.wav`, `.mp3`, `.m4a` (wav preferred)
- Transcription: Zo built-in transcription service
- Fallback: Manual transcript paste if transcription fails

**Context Loading:**
- Automatic keyword matching to hypotheses
- Recent decisions (last 30 days)
- Relevant facts from knowledge base
- My personal understanding layer
- All read-only during session

**Session State:**
- Persisted in `N5/sessions/strategic-partner/`
- JSON metadata + markdown synthesis
- Topics-to-revisit tracked in JSONL
- Pending updates staged separately

**Scheduled Tasks:**
- Weekly review: Saturday 9 AM ET
- Can be adjusted: `update-scheduled-task [event-id]`

---

## Voice Compliance

Follows `N5/prefs/communication/voice.md` v3.0:
- Warm but direct (calibrated balance)
- Uses specific dates, never "ASAP" or "soon"
- Authentic voice, not corporate
- Crisp questions, no meandering
- Challenges respectfully but firmly

---

## Notes

**This is the core cognitive engine of N5 OS.**

Everything else in N5 - research functions, meeting processing, knowledge management - these are capabilities that the Strategic Partner can orchestrate. But the Strategic Partner itself is the primary interface between your thinking and the entire system.

**It's not combining features - it's creating an adaptive cognitive architecture that provides the right type of thinking support at the right time with the right level of challenge and the right output format.**

Your voice memos → my strategic dialogue → understanding exported → hypotheses updated → N5 system "clicks" → major realizations propagate → proactive engagement when needed.

**This is your externalized cognitive architecture for strategic thinking.**

---

*The Strategic Partner: Where raw thinking becomes refined strategy.*
