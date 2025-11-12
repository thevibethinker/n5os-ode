---
tool: true
description: Generate B01 intelligence block
tags:
  - meeting
  - intelligence
  - b01
---

# B01 - DETAILED_RECAP Generation Prompt

You are generating a DETAILED_RECAP intelligence block from a meeting transcript.

## Input
- Meeting transcript with timestamps
- Attendee list
- Meeting metadata (date, type, participants)

## Output Structure

### 1. KEY DECISIONS & AGREEMENTS (3-5 items)

For each major decision or agreement:

**WHAT:** [Clear statement of what was decided/agreed]

**WHY IT MATTERS:** [2 sentences explaining strategic significance, implications, or impact]

Focus on:
- Explicit agreements or commitments
- Strategic direction changes
- Resource allocation decisions
- Go/no-go decisions
- Timeline agreements

### 2. STRATEGIC CONTEXT

Synthesize the conversation's strategic implications across:

**Positioning:**
- How this conversation positions Careerspan vs competitors
- Value propositions that resonated
- Differentiation moments
- Credibility signals

**Pain Points Identified:**
- Specific problems the stakeholder/organization faces
- Urgency indicators
- Cost of status quo
- Failed solutions they've tried

**Competitive Landscape:**
- Competitors mentioned (direct or indirect)
- Comparative discussions
- Market gaps identified
- Incumbent weaknesses revealed

**Underlying Motivations:**
- What's really driving this conversation (beyond surface topics)
- Career/business pressures influencing decisions
- Personal vs organizational priorities
- Hidden agendas or constraints

### 3. CRITICAL NEXT ACTION

Structure as a single high-priority action:

**Owner:** [Specific person name]  
**Deliverable:** [Concrete output or action]  
**Timeline:** [Specific date or relative timeframe from transcript]  
**Purpose:** [Why this matters strategically - connects back to key decisions or pain points]

## Quality Standards

✅ **DO:**
- Extract strategic insights, not just surface facts
- Every decision includes WHY IT MATTERS
- Strategic Context is interpretive analysis, not summary
- Use direct quotes when they reveal motivation or pain
- Balance breadth (covering main topics) with depth (strategic interpretation)
- Target ~600 words total

❌ **DON'T:**
- Write generic meeting notes without strategic interpretation
- List what was discussed without explaining implications
- Skip the "why it matters" context
- Create vague next actions without clear ownership/timeline
- Miss competitive/positioning intelligence opportunities
- Exceed 800 words or go below 400 words

## Example Quality Indicators

**HIGH QUALITY:**
- Reader understands not just WHAT happened but WHY it matters for Careerspan
- Strategic Context reveals competitive advantages or market insights
- Next Action is concrete enough to execute immediately
- Decisions connect to underlying stakeholder motivations

**LOW QUALITY:**
- Reads like chronological notes: "First they discussed X, then Y..."
- Missing strategic interpretation
- Vague next actions: "Follow up next week"
- No connection to competitive landscape or positioning
- Generic insights that don't reveal stakeholder-specific context

## Edge Cases

**If no clear decisions:** Focus on emerging strategic themes, key questions raised, or areas requiring further exploration. Strategic Context becomes primary value.

**If highly tactical meeting:** Still extract strategic implications even from tactical discussions - what do these tactical choices reveal about priorities, constraints, or direction?

**If multiple stakeholders:** Distinguish whose perspective drives which insights. Track alignment/misalignment.
