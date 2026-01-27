---
description: Generate B41 Team Coordination block for internal team alignment discussions
tags: [meeting-intelligence, block-generation, b41, team-coordination, alignment]
tool: true
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_kjU4NIoVthBGRdTk
---

# Generate B41: Team Coordination

Document team alignment, role clarifications, and coordination agreements from internal meetings.

## Purpose

Internal meetings often involve team coordination - clarifying roles, aligning on priorities, coordinating cross-functional work. This block captures these coordination elements.

## Input Format

Meeting transcript with internal team members discussing roles, responsibilities, timelines, and coordination needs.

## Output Format

**REQUIRED YAML FRONTMATTER:**
```yaml
---
created: {YYYY-MM-DD}
last_edited: {YYYY-MM-DD}
version: 1.0
provenance: {agent_id or conversation_id}
---
```

**REQUIRED STRUCTURE:**

```markdown
# B41: Team Coordination

## Role Clarifications

### {Project/Initiative Name}
- **Owner**: Primary owner identified
- **Contributors**: Supporting team members and their roles
- **Dependencies**: What this person/team needs from others
- **Deliverables**: Expected outputs and timelines

## Priority Alignment

### Team Priorities This Week/Sprint
1. **{Priority 1}** - Owner: {Name} - Due: {Date}
2. **{Priority 2}** - Owner: {Name} - Due: {Date}
3. **{Priority 3}** - Owner: {Name} - Due: {Date}

## Communication Agreements

- **Meeting Cadence**: {Frequency and format}
- **Check-in Process**: How team stays aligned
- **Escalation Path**: When and how to raise blockers

## Cross-functional Coordination

### {Initiative/Project}
- **Teams Involved**: {List teams/individuals}
- **Handoff Points**: When work passes between teams
- **Success Metrics**: How teams measure joint success
```

**Generate the B41 block now using the transcript provided.**