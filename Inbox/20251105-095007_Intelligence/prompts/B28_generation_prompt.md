---
tool: true
description: Generate B28 strategic intelligence metadata - decision architecture, power dynamics, and strategic insights
tags:
  - meeting
  - intelligence
  - strategic
  - metadata
  - b28
---

# B28 - STRATEGIC_INTELLIGENCE_METADATA Generation Prompt

You are generating a STRATEGIC_INTELLIGENCE_METADATA block. This is the **STRATEGIC COMPANION** to B26 (system operations metadata).

## Core Principle

Extract strategic signal for decision-making, power dynamics analysis, and insight synthesis. This block enables **strategic intelligence** not operational automation.

## Output Structure

### Meeting Classification

**Meeting Type**: [Type from taxonomy below]
**Strategic Context**: [1-2 sentences: Why this meeting matters strategically]
**Decision Stage**: [Information Gathering / Option Generation / Decision Making / Execution Planning / Post-Mortem]

### Stakeholder Intelligence

**Primary Stakeholders**:
- **[Name]** ([Organization if known])
  - **Role/Title**: [Their position]
  - **Power/Influence**: [High/Medium/Low] - [Why]
  - **Decision Authority**: [What they can decide]
  - **Key Motivations**: [What drives their decisions]
  - **Internal/External**: [Classification]

**Existing CRM Record**: [YES with link / NO - needs creation / UNCERTAIN]

### Strategic Insights

**Key Insights** (3-5 maximum):
1. **[Insight Theme]**
   - **Signal**: [What was said/observed]
   - **Implication**: [What this means strategically]
   - **Confidence**: [High/Medium/Low]

**Decision Architecture**:
- **Decision at stake**: [What decision is being made or influenced]
- **Decision criteria**: [What factors matter most]
- **Our positioning**: [How we're positioned relative to criteria]
- **Risks/Blockers**: [What could prevent desired outcome]

**Power Dynamics**:
- **Who has leverage**: [Analysis of relative power]
- **Dependencies**: [What each party needs from the other]
- **Negotiation position**: [Strong/Balanced/Weak] - [Why]

### Value Exchange

**What They Offered**:
- [Specific value, connections, information, resources]

**What We Offered**:
- [Specific value, connections, information, resources]

**Exchange Balance**: [Balanced / We gave more / They gave more] - [Reasoning]

### Strategic Follow-Through

**Critical Next Steps** (3 maximum):
1. **[Action]** - [Why critical] - [Timeframe] - [Owner]

**Success Metrics**:
- [How we'll know if this meeting led to desired outcome]

**Follow-Up Intelligence Needed**:
- [What information gaps must be filled]

## Meeting Type Taxonomy

### External Meetings
- **Sales/Prospect**: Active opportunity, moving toward close
- **Partnership Development**: Potential collaboration, value co-creation
- **Fundraising**: Investor conversations, pitch refinement
- **Strategic Advisory**: Getting guidance from experienced operators
- **Warm Introduction**: Bi-directional value matching, network expansion
- **Customer Intelligence**: Understanding user needs, product direction
- **Market Intelligence**: Industry trends, competitive landscape
- **Recruiting/Talent**: Evaluating candidates, selling opportunity

### Internal Meetings
- **Strategic Planning**: Direction-setting, big decisions
- **Technical Deep Dive**: Architecture, implementation decisions
- **Team Coordination**: Execution alignment, blocker removal
- **Retrospective/Learning**: What worked, what didn't, why
- **Product Strategy**: Roadmap, prioritization, user needs

## Quality Criteria

### REQUIRED for HIGH-QUALITY output:
- **Specificity**: No generic insights. Quote specific moments.
- **Actionability**: Each insight connects to decision or action.
- **Quantification**: Where possible, add numbers (timeline, probability, scale).
- **Confidence levels**: State uncertainty explicitly.
- **Strategic relevance**: Focus on what matters for decisions, not trivia.

### Common FAILURES to avoid:
- ❌ Generic insights: "Good chemistry" → ✅ "Responded enthusiastically to AI-first positioning, asked 3 follow-up questions"
- ❌ Missing implications: "They mentioned timeline" → ✅ "They mentioned Q1 timeline, which conflicts with our Q2 product launch"
- ❌ No decision context: "Discussed pricing" → ✅ "Pricing sensitivity emerged - $10K is ceiling, our $15K proposal needs discount justification"
- ❌ Vague stakeholders: "Met with team" → ✅ "Sarah (CTO, budget authority) and Mike (Director, user champion, no budget authority)"

## Generation Instructions

1. **Read transcript carefully** for strategic signal
2. **Extract decision-relevant information** - what matters for choices
3. **Map power dynamics** - who can make what happen
4. **Quantify where possible** - timelines, budgets, probabilities
5. **State confidence explicitly** - distinguish fact from inference
6. **Connect to action** - each insight should inform a decision

## Validation Checklist

Before finalizing, verify:
- [ ] Meeting type accurately classified
- [ ] All stakeholders identified with roles/authority
- [ ] CRM status checked (existing record or not)
- [ ] Insights are specific with quotes/examples
- [ ] Decision architecture mapped explicitly
- [ ] Value exchange assessed (balanced or not)
- [ ] Critical next steps identified with owners
- [ ] Confidence levels stated where uncertain

---

**Output Format**: Use exactly the structure above. Be concise but substantive. Every section must have content - if truly not applicable, state "N/A - [reason]" rather than omitting.
