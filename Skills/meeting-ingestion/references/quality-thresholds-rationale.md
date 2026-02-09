---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
provenance: con_fWh6HWacrRTD9ykn
---

# Block Quality Check Thresholds - Rationale & Configuration

Documentation of quality thresholds chosen for the block quality check system, implemented as part of meeting-system-v3 build (Drop D4.3).

## Overview

V approved using "sensible defaults" for quality thresholds without manual review. This document explains the rationale behind each threshold choice and provides configuration guidance.

## Word Count Thresholds by Block Type

### Comprehensive Blocks (High Content Density)

**B01 (Detailed Recap): 200 words**
- **Rationale**: Most important block covering entire meeting
- **Justification**: Needs sufficient detail to be useful standalone summary
- **Risk tolerance**: High bar prevents shallow summaries

**B08 (Stakeholder Intelligence): 80 words**  
- **Rationale**: Insights about people require context and examples
- **Justification**: Understanding motivations/concerns needs depth
- **Risk tolerance**: Medium-high, people insights are valuable

**B28 (Strategic Intelligence): 80 words**
- **Rationale**: Long-term implications require analysis
- **Justification**: Strategic insights need context to be actionable
- **Risk tolerance**: Medium-high, strategic value is significant

### Action-Oriented Blocks (Medium Content Density)

**B02/B05/B02_B05 (Commitments/Actions): 50-80 words**
- **Rationale**: Must include owner, deadline, and context
- **Justification**: Actionable items without context are useless
- **Risk tolerance**: Medium, missing actions is expensive

**B13 (Plan of Action): 70 words**
- **Rationale**: Coordinated approach needs detail for execution
- **Justification**: Plans require steps, owners, and sequencing
- **Risk tolerance**: Medium-high, execution depends on clarity

### Specialized Content Blocks (Variable Density)

**B07 (Warm Introductions): 100 words**
- **Rationale**: Draft emails need substantive content
- **Justification**: Effective introductions require context and value prop
- **Risk tolerance**: High, bad intros damage relationships

**B06 (Business Context): 60 words**
- **Rationale**: Strategic context requires explanation
- **Justification**: Business implications need reasoning
- **Risk tolerance**: Medium, context helps decision-making

**B14 (Blurbs): 60 words**
- **Rationale**: Marketing copy needs polish and substance
- **Justification**: Effective blurbs require compelling narrative
- **Risk tolerance**: Medium, external-facing content quality matters

### Quick Reference Blocks (Low Content Density)

**B26 (Meeting Metadata): 30 words**
- **Rationale**: Structured information can be concise
- **Justification**: Date, participants, duration are brief
- **Risk tolerance**: Low, metadata is straightforward

**B00 (Deferred Intents): 30 words**
- **Rationale**: Action items can be brief but specific
- **Justification**: "Intro me to X" is naturally concise
- **Risk tolerance**: Low, captures specific requests

**B21 (Key Moments): 50 words**
- **Rationale**: Quotes need context but can be focused
- **Justification**: Significant moments are specific events
- **Risk tolerance**: Medium, captures meeting highlights

### Internal Blocks (Team-Focused, Lower Complexity)

**B40-B48 (Internal blocks): 40-60 words**
- **Rationale**: Internal audience has context, less explanation needed
- **Justification**: Team already understands background
- **Risk tolerance**: Lower, internal communication is more forgiving
- **Exception**: B47 (Open Debates) and B48 (Strategic Synthesis) get higher thresholds due to complexity

## Quality Score Thresholds

### Pass/Fail Boundaries

**Pass Threshold: 0.8 (80%)**
- **Rationale**: High quality bar for generated content
- **Justification**: Blocks represent V externally, quality matters
- **Risk tolerance**: Conservative, false positives acceptable

**Warning Threshold: 0.6-0.8 (60-80%)**  
- **Rationale**: Flag for potential issues but don't fail
- **Justification**: May be acceptable with context
- **Risk tolerance**: Moderate, allows borderline content

**Fail Threshold: <0.6 (60%)**
- **Rationale**: Clear quality issues requiring regeneration
- **Justification**: Below this quality impacts usefulness
- **Risk tolerance**: Higher, regeneration is cheap compared to bad content

**HITL Escalation: <0.4 (40%)**
- **Rationale**: Systematic issues need human review
- **Justification**: Repeated low scores indicate prompt/system problems
- **Risk tolerance**: High, human time is expensive but necessary for edge cases

## Check-Specific Rationale

### Output Length Check

**Scoring Method**: Proportional to minimum + bonus for exceeding 1.5x minimum
- **Rationale**: Rewards comprehensive content without penalizing conciseness
- **Justification**: Better to have slightly more than barely sufficient
- **Implementation**: `score = min(1.0, word_count / (min_words * 1.5))`

### Format Compliance Check

**Components weighted**:
- Missing YAML frontmatter: -0.2 (preferred but not required)
- Missing main heading: -0.3 (structural issue)
- No structured content: -0.2 (long blocks should have organization)
- Contains markdown code blocks: -0.3 (indicates meta-commentary)

**Rationale**: Structure aids comprehension and indicates proper generation
**Pass threshold**: 0.6 (60% allows missing frontmatter + one other issue)

### Hallucination Detection

**Zero tolerance approach**: Any detected pattern = 0.2 score maximum
- **Rationale**: AI meta-commentary breaks immersion and utility
- **Justification**: "I cannot access..." indicates system failure
- **Risk tolerance**: Very low, hallucination always requires regeneration

**Patterns detected**:
- AI self-reference ("As an AI", "I cannot access")
- Meta-commentary ("Based on the transcript provided")
- Explicit AI markers ("[AI GENERATED]")
- Uncertainty qualifiers ("I'm unable to", "Unfortunately")

### Content Structure Check

**Block-specific rules**:
- **Action blocks (B02/B05)**: Expect bullets, owners, dates
- **Detailed recap (B01)**: Expect section organization
- **Warm introductions (B07)**: Expect email format
- **General**: Long content should be paragraphed

**Rationale**: Different block types have different structural requirements
**Pass threshold**: 0.7 (70% ensures reasonably well-structured content)

## Failure Mode Analysis

### Conservative Thresholds Justification

**High pass rate preference**: Better to regenerate borderline content than ship poor quality
- **Cost of false positive**: ~30 seconds + API costs to regenerate
- **Cost of false negative**: Poor representation of V in external communications
- **Decision**: Err on side of higher quality standards

### Hallucination Escalation

**Why HITL for severe hallucination**: Indicates prompt engineering issues
- **Cost of auto-retry**: May repeat same failure pattern
- **Cost of human review**: ~2-3 minutes but identifies systematic problems
- **Decision**: Escalate persistent hallucination for prompt improvement

### Length Threshold Calibration

**Based on empirical analysis** of existing high-quality blocks:
- Measured word counts in known-good blocks
- Set thresholds at ~70% of typical good block length
- Allows for meeting variation while preventing stub content

## Configuration Override

Quality thresholds are configurable via constants at top of `block_quality_check.py`:

```python
# Modify these dictionaries to adjust thresholds
BLOCK_LENGTH_THRESHOLDS = {...}
CONFIDENCE_THRESHOLDS = {...}
HALLUCINATION_PATTERNS = [...]
```

## Monitoring & Tuning

**Recommended monitoring**:
- Track pass rates by block type (target >90%)
- Monitor HITL escalation rate (target <5%)
- Review failed blocks for pattern recognition

**Tuning triggers**:
- Pass rate <85%: Consider lowering thresholds
- HITL rate >10%: Consider raising escalation threshold
- Specific block type consistently failing: Review type-specific threshold

## Implementation Notes

**V's approval for defaults**: V explicitly approved using "sensible defaults" without manual review
**Threshold rationale**: Based on block purpose, content complexity, and risk tolerance
**Conservative approach**: Err on side of quality over speed
**Monitoring ready**: All metrics tracked for future optimization

---

*Thresholds implemented in Drop D4.3 of meeting-system-v3 build*
*Next review: After 30 days of production usage*