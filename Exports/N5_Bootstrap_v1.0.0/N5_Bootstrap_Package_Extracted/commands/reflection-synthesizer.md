---
date: "2025-10-09T21:00:00Z"
last-tested: "2025-10-09T21:00:00Z"
generated_date: "2025-10-09T21:00:00Z"
checksum: reflection_synthesizer_v1_0_0
tags:
  - strategic
  - synthesis
  - reflection
  - [COMPANY]
category: strategic
priority: p1
related_files:
  - N5/scripts/reflection_synthesizer.py
  - N5/commands/strategic-partner.md
anchors: [object Object]
---
# `reflection-synthesizer`

**Version**: 1.0.0  
**Summary**: Transform strategic sessions and transcripts into structured outputs

---

## Purpose

The Reflection Synthesizer converts strategic partner sessions, transcripts, or raw thinking into four structured output formats:

1. **Decision Memo** - Structured markdown document with context, analysis, insights, recommendation, and actions
2. **Key Insights** - 5-7 strategic insights with confidence levels and implications
3. **Action Items** - 3-6 prioritized next actions with owners, deadlines, and rationale
4. **Executive Blurb** - 1-paragraph summary for quick executive consumption

**Integrates with Strategic Partner sessions** or can be used standalone.

---

## Usage

### Basic: From Strategic Partner Session

```bash
reflection-synthesizer --session-id 2025-10-09-session-1
```

Synthesizes an existing strategic partner session into structured outputs.

### Basic: From File

```bash
reflection-synthesizer --session-file path/to/transcript.txt
```

Synthesizes any transcript or notes file.

### Basic: Interactive

```bash
reflection-synthesizer --interactive
```

Paste content directly (Ctrl+D when done).

---

## Output Formats

### 1. Decision Memo (Markdown)

**Location:** `N5/sessions/strategic-partner/syntheses/[ID]-decision-memo.md`

**Structure:**
```markdown
# Decision Memo: [Topic]

## Executive Summary
[One paragraph blurb]

## Strategic Context
- Current state
- Challenge addressed
- Key constraints

## Key Insights
1. [Insight with confidence + implication]
2. [Insight with confidence + implication]
...

## Analysis
- Assumptions challenged
- Blind spots identified
- Contradictions detected
- Risk assessment

## Recommendation
- Primary recommendation
- Rationale
- Alternative considered

## Next Actions
1. [Action] (Priority: HIGH)
   - Why: [rationale]
   - By When: [specific date]
   - Owner: [who]
...

## Unresolved Questions
[Questions for weekly review]

## Appendix
[Session metadata, quality metrics, context loaded]
```

### 2. Key Insights (JSON)

**Location:** `N5/sessions/strategic-partner/syntheses/[ID]-insights.json`

**Format:**
```json
[
  {
    "insight": "Current pricing assumes TAM of $10B (unvalidated)",
    "confidence": "high",
    "strategic_implication": "Revenue projections may be overstated by 2-3x",
    "related_hypothesis": "gtm_hypotheses.md#pricing-strategy"
  },
  ...
]
```

**Target:** 5-7 insights per session

### 3. Action Items (JSON)

**Location:** `N5/sessions/strategic-partner/syntheses/[ID]-actions.json`

**Format:**
```json
[
  {
    "action": "Run willingness-to-pay survey with 50 current customers",
    "why": "Validate pricing assumptions before 30% increase",
    "by_when": "2025-10-20",
    "owner": "V",
    "priority": "high",
    "dependencies": ["Customer list segmentation"]
  },
  ...
]
```

**Target:** 3-6 actions per session

### 4. Executive Blurb (Markdown)

**Location:** `N5/sessions/strategic-partner/syntheses/[ID]-blurb.md`

**Format:**
```markdown
# Executive Summary

[COMPANY] evaluated a white-label partnership with TalentOS (500K users, 
$50K + 20% rev share). Core tension: enterprise opportunity vs. B2C focus. 
Key insight: 20% rev share is below market (30-40% standard), exclusivity 
terms undefined, and 3-month dev time creates significant opportunity cost. 
Recommendation: Counter with 35% rev share, non-exclusive terms, and 
validation pilot before full integration. Next action: Schedule negotiation 
call by 2025-10-15.
```

**Format:** Context → Challenge → Key Insight → Recommendation (one paragraph)

---

## Integration with Strategic Partner

The Reflection Synthesizer is **automatically called** at the end of Strategic Partner sessions to generate structured outputs.

**Manual override:**
```bash
strategic-partner --audio memo.wav --skip-synthesis
```

Skip synthesis if you want just the dialogue without structured outputs.

**Standalone synthesis:**
```bash
# After a strategic partner session
reflection-synthesizer --session-id 2025-10-09-session-1
```

Generate synthesis after the fact, or re-synthesize with different parameters.

---

## Context Loading

Synthesizer automatically loads relevant context from N5 knowledge base (read-only):

**From Knowledge/:**
- GTM hypotheses
- Product hypotheses
- Recent strategic decisions
- Relevant facts

**Used for:**
- Relating insights to existing hypotheses
- Identifying contradictions with existing strategy
- Proposing knowledge updates (staged for review)

**Read-only:** No automatic updates to knowledge base.

---

## Pending Updates

Each synthesis generates **staged knowledge updates** based on insights:

**Location:** `N5/sessions/strategic-partner/pending-updates/[ID].json`

**Format:**
```json
{
  "synthesis_id": "2025-10-09-synthesis-1400",
  "timestamp": "2025-10-09T14:00:00Z",
  "source": "reflection-synthesizer",
  "updates": [
    {
      "type": "hypothesis_update",
      "target": "gtm_hypotheses.md#pricing-strategy",
      "proposed_change": "confidence_adjustment",
      "reason": "Pricing assumptions validated through TalentOS analysis",
      "requires_approval": true
    }
  ],
  "status": "pending_review",
  "auto_apply": false
}
```

**CRITICAL:** All updates require human review via `review-pending-updates` command.

---

## Use Cases

### Use Case 1: After Strategic Partner Session

**Workflow:**
```bash
# 1. Strategic dialogue
strategic-partner --audio pricing_strategy.wav

# 2. Synthesis happens automatically
# Outputs generated in N5/sessions/strategic-partner/syntheses/

# 3. Review outputs
cat N5/sessions/strategic-partner/syntheses/2025-10-09-synthesis-1400-decision-memo.md

# 4. Review pending updates
review-pending-updates
```

### Use Case 2: Standalone Transcript Processing

**Workflow:**
```bash
# You have meeting notes or voice memo transcript
reflection-synthesizer --session-file meeting_notes.txt

# Outputs:
# - Decision memo
# - Key insights
# - Action items  
# - Executive blurb
```

### Use Case 3: Re-synthesis

**Workflow:**
```bash
# You want different synthesis of existing session
reflection-synthesizer --session-id 2025-10-09-session-1

# Generates new synthesis with fresh perspective
```

---

## Quality Standards

### Decision Memo
- **Length:** 2-4 pages (structured)
- **Tone:** Executive-ready, crisp, actionable
- **Structure:** MECE framework applied
- **Voice:** Follows voice.md (warm but direct)

### Key Insights
- **Count:** 5-7 per session (target)
- **Confidence:** Explicit confidence levels (low/medium/high)
- **Implications:** Strategic implications stated clearly
- **Linkage:** Related to existing hypotheses when relevant

### Action Items
- **Count:** 3-6 per session (target)
- **Specificity:** What, Why, By When, Owner (all explicit)
- **Priority:** Clear prioritization (high/medium/low)
- **Dependencies:** Identified when present

### Executive Blurb
- **Length:** 1 paragraph (100-150 words)
- **Format:** Context → Challenge → Insight → Recommendation
- **Audience:** Executive level (CEO, board, investors)
- **Actionability:** Clear decision implications

---

## Examples

### Example: TalentOS Partnership Decision

**Input:** Strategic partner session transcript (TalentOS white-label opportunity)

**Outputs:**

**Decision Memo:** (excerpt)
```markdown
# Decision Memo: TalentOS Partnership Evaluation

## Executive Summary
[COMPANY] evaluated a white-label partnership with TalentOS... 
[full blurb]

## Key Insights
1. **20% rev share below market standard** (Confidence: high)
   Implication: $200K-300K annual revenue left on table vs. 35% market rate

2. **Exclusivity terms undefined** (Confidence: high)
   Implication: Could block future enterprise partnerships worth $1M+ annually

3. **3-month dev time = $150K opportunity cost** (Confidence: medium)
   Implication: Delays B2C roadmap, impacts Q1 2026 revenue targets
...

## Recommendation
**Counter-offer:** 35% rev share, non-exclusive, 2-week validation pilot

## Next Actions
1. **Schedule negotiation call with TalentOS** (Priority: HIGH)
   - Why: Need to counter-offer before 2-week deadline expires
   - By When: 2025-10-15
   - Owner: V
```

**Key Insights JSON:**
```json
[
  {
    "insight": "20% rev share is 15-20 points below market standard for white-label SaaS partnerships",
    "confidence": "high",
    "strategic_implication": "Leaves $200K-300K annual revenue on table",
    "related_hypothesis": "gtm_hypotheses.md#partnership-strategy"
  },
  {
    "insight": "Exclusivity terms not discussed - critical blind spot",
    "confidence": "high",
    "strategic_implication": "Could block $1M+ future enterprise opportunities",
    "related_hypothesis": null
  }
]
```

**Executive Blurb:**
```
[COMPANY] evaluated a white-label partnership with TalentOS (500K users, 
$50K + 20% rev share). Core tension: enterprise opportunity vs. B2C strategic 
focus. Key insight: 20% rev share is 15-20 points below market (30-40% 
standard), exclusivity terms are undefined (critical blind spot), and 3-month 
dev time creates $150K opportunity cost against B2C roadmap. Recommendation: 
Counter with 35% rev share, explicit non-exclusive terms, and 2-week validation 
pilot before full integration. Next action: Schedule negotiation call by 
2025-10-15 to present counter-offer before deadline.
```

---

## Integration Points

### With Strategic Partner
- Called automatically at Phase 3 (Convergence)
- Generates all 4 output formats
- Feeds insights into personal intelligence layer

### With Knowledge Base
- Reads GTM/product hypotheses (read-only)
- Generates pending updates based on insights
- Links insights to existing hypotheses

### With Weekly Review
- Decision memos accumulated for weekend review
- Unresolved questions feed topics-to-revisit
- Action items tracked for completion

---

## Safety Features

### Knowledge Write Protection 🔒
- Zero automatic updates to knowledge base
- All updates staged in pending-updates/
- Requires `review-pending-updates` to approve
- Human-in-the-loop for ALL changes

### Quality Assurance
- Confidence levels explicit on insights
- Strategic implications required
- Pending updates have clear rationale
- All dates specific (never "ASAP" or "soon")

---

## Technical Details

**Processing:**
- Input: Session transcript or strategic partner session
- Analysis: Pattern recognition, assumption extraction, blind spot identification
- Synthesis: MECE frameworks, structured thinking, voice.md compliance
- Output: 4 formats (memo, insights, actions, blurb)

**Context Integration:**
- Automatic keyword matching to hypotheses
- Recent decisions (last 30 days)
- Relevant facts from knowledge base
- All read-only during synthesis

**File Structure:**
```
N5/sessions/strategic-partner/syntheses/
├── [ID]-decision-memo.md
├── [ID]-insights.json
├── [ID]-actions.json
└── [ID]-blurb.md

N5/sessions/strategic-partner/pending-updates/
└── [ID].json
```

---

## Voice Compliance

Follows `N5/prefs/communication/voice.md` v3.0:
- Warm but direct (calibrated balance)
- Uses specific dates, never "ASAP" or "soon"
- Authentic voice, not corporate
- Crisp language, no jargon unless necessary
- Executive-ready quality

---

## Related Commands

- `strategic-partner` - Core cognitive engine (calls synthesizer automatically)
- `review-pending-updates` - Approve staged knowledge updates
- `weekly-strategic-review` - Reviews accumulated decision memos

---

## Notes

The Reflection Synthesizer is **Phase 2** of the Strategic Partner implementation. It transforms the dialogue outputs from Phase 1 into structured, actionable formats.

**Key principle:** Synthesis is not just summarization. It's:
- Pattern recognition across dialogue
- Assumption extraction and validation
- Blind spot identification and documentation
- Strategic implication analysis
- Actionable recommendation generation

The synthesizer applies structured thinking frameworks (MECE, etc.) to ensure outputs are comprehensive, non-overlapping, and actionable.

---

*The Reflection Synthesizer: Where strategic dialogue becomes structured action.*
