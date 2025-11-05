---
tool: true
description: Generate B03 intelligence block
tags:
  - meeting
  - intelligence
  - b03
---

# B03 - STAKEHOLDER_PROFILES Generation Prompt

You are generating a STAKEHOLDER_PROFILES intelligence block from a meeting transcript.

## Input
- Meeting transcript with timestamps
- Attendee list
- Meeting metadata

## Output Structure

Create one profile per external stakeholder (not internal team members). Each profile uses this format:

---

### [Stakeholder Name]

**Role/Title**: [Their current position]  
**Company/Organization**: [Where they work]  
**Relationship to Careerspan**: [How they connect to us]

**Background Summary** (2-3 sentences):
[Their professional background, experience, expertise areas based on what emerged in conversation]

**Communication Style**:
[How they communicate - direct/diplomatic, technical/business-focused, formal/casual, question style, decision-making approach]

**Interests & Motivations**:
- [Key area of interest #1 with evidence]
- [Key area of interest #2 with evidence]
- [What drives them professionally]

**Pain Points Mentioned**:
- [Challenge #1 they're facing]
- [Challenge #2 they're facing]

**Potential Value Exchange**:
- What we can offer them: [Specific help, connections, knowledge]
- What they can offer us: [Expertise, connections, opportunities]

**Follow-Up Notes**:
[Specific considerations for future interactions - topics to avoid, topics of high interest, optimal communication frequency/channel]

---

## Extraction Rules

### Include:
- Professional background revealed during conversation
- Communication patterns and style observations
- Explicit and implicit interests/motivations
- Problems or challenges they mentioned
- Their network, expertise, or resources
- Personality indicators (risk-averse vs entrepreneurial, data-driven vs intuitive, etc.)

### Exclude:
- Speculation without evidence
- Detailed company information (that belongs in B31)
- Commitments/action items (that's B02)

## Quality Standards

✅ **DO:**
- Ground observations in specific transcript moments
- Identify communication style from HOW they engaged
- Note what energized them vs what they rushed through
- Identify mutual value exchange opportunities
- Capture personality and working style indicators

❌ **DON'T:**
- Create generic profiles that could apply to anyone
- Miss implicit signals about interests/motivations
- Ignore communication style indicators
- Forget to note follow-up considerations

## Edge Cases

**Multiple stakeholders**: Create separate ## sections for each

**Limited background information**: Note "Limited background discussed - primary focus was [X]"

**Internal-only meeting**: DO NOT generate this block. Use B40 instead.

**Group dynamics**: If multiple stakeholders with different roles, note relationship dynamics between them
