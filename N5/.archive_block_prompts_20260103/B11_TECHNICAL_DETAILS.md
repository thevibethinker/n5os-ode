---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
block_code: B11
block_name: TECHNICAL_DETAILS
category: contextual
---

# B11: Technical Architecture & Implementation

## Objective

Capture technical architecture discussions, implementation details, technology decisions, and engineering considerations.

## What to Capture

**Architecture Decisions:**
- System design choices
- Technology stack decisions
- Integration approaches
- Data flow and structure

**Implementation Details:**
- How something will be built
- Technical approach
- Code/infrastructure considerations
- Development methodology

**Technical Constraints:**
- Performance requirements
- Scalability needs
- Security considerations
- Compatibility requirements

**Technologies Discussed:**
- Languages and frameworks
- Platforms and services
- Tools and libraries
- Infrastructure components

**Technical Trade-offs:**
- Why one approach over another
- Pros and cons discussed
- Performance vs simplicity
- Cost vs capability

**Integration Points:**
- APIs and connections
- Data exchange formats
- Authentication/authorization
- External dependencies

## Output Format

### Architecture Overview
[High-level description of system design or technical approach]

### Key Technical Decisions

**Decision: [Name]**
- **Chosen Approach:** [What was decided]
- **Rationale:** [Why this choice]
- **Alternatives Considered:** [What else was discussed]
- **Trade-offs:** [Pros and cons]

### Technology Stack
- **[Component Type]:** [Technology chosen]
  - Purpose: [What it does]
  - Justification: [Why selected]

### Implementation Approach
[How this will be built, step by step technical plan]

### Technical Constraints
- [Constraint 1]: [Description and impact]
- [Constraint 2]: [Description and impact]

### Integration Details
- **[System/Service]:** [How it connects]
  - Protocol: [REST, GraphQL, etc.]
  - Auth: [Authentication method]
  - Data Format: [JSON, XML, etc.]

### Open Technical Questions
- [Question 1]
- [Question 2]

## Generation Guidelines

1. Listen for technical language:
   - Architecture/design discussions
   - "We'll use..."
   - "The system will..."
   - Performance/scale considerations
   - Technology comparisons

2. Capture decisions and rationale:
   - Not just WHAT but WHY
   - Document alternatives considered
   - Note trade-offs

3. Be specific:
   - Name technologies explicitly
   - Include version numbers if mentioned
   - Document protocols and formats

4. Include context:
   - Why this technical approach
   - How it fits business needs
   - What constraints drive decisions

5. Note open items:
   - Technical questions to resolve
   - Research needed
   - Proof-of-concept requirements

## When to Generate

Generate B11 when meeting includes:
- Architecture or design discussions
- Technology selection decisions
- Implementation planning
- Technical trade-off discussions
- Engineering approach debates
- Integration planning

Skip for non-technical business meetings.

## Quality Checklist

Before finalizing, check:
- [ ] Architecture decisions documented
- [ ] Technology choices with rationale
- [ ] Implementation approach clear
- [ ] Technical constraints noted
- [ ] Integration points specified
- [ ] Trade-offs explained
- [ ] Sufficient detail for engineers to reference
- [ ] Open questions captured

