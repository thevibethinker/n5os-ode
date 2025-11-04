# B06 - PILOT_INTELLIGENCE Generation Prompt

You are generating a PILOT_INTELLIGENCE intelligence block for pilot/POC discussions.

## Core Principle

Capture everything needed to design, launch, and evaluate a pilot or proof-of-concept with this stakeholder.

## Output Structure

### Pilot Scope
**What they want to test**: [Specific use case/problem]  
**Success criteria**: [How they'll measure if pilot worked]  
**Timeline**: [Duration mentioned or implied]  
**Scale**: [Number of users, scope of test]

### Technical Requirements
- [Requirement 1]
- [Requirement 2]
- [Integration needs]

### Stakeholders & Decision Process
**Champion**: [Primary advocate]  
**Decision-maker**: [Final approval authority]  
**Users**: [Who will actually use it]  
**IT/Security**: [Gatekeeper considerations]

### Risk Factors
- [Potential blocker 1]
- [Potential blocker 2]
- [Concerns expressed]

### Next Steps to Launch
1. [First action]
2. [Second action]
3. [Third action]

## Extraction Rules

Include:
- Explicit pilot/POC mentions
- Implied testing interest ("We'd need to see if...")
- Success metrics discussed
- Technical constraints mentioned
- Political dynamics (who needs to approve?)

## Quality Standards

✅ DO: Extract decision criteria, timeline expectations, scope constraints, risk concerns  
❌ DON'T: Assume pilot interest without clear signals, miss political/approval dynamics

## Edge Cases

**No pilot discussed**: Output: "No pilot or POC discussion in this meeting."  
**Implied interest without structure**: Note: "POTENTIAL - Monitor for future pilot signals: [context]"
