---
description: Generate B46 Knowledge Transfer block for learning and knowledge sharing
tags: [meeting-intelligence, block-generation, b46, knowledge-transfer, learning]
tool: true
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_kjU4NIoVthBGRdTk
---

# Generate B46: Knowledge Transfer

Document knowledge sharing, learning moments, and institutional knowledge from internal meetings.

## Purpose

Internal meetings are rich sources of institutional knowledge - lessons learned, expertise shared, context transferred. This block captures these knowledge elements for organizational learning.

## Input Format

Meeting transcript containing knowledge sharing moments, lessons learned, expertise transfer, or contextual insights.

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
# B46: Knowledge Transfer

## Key Knowledge Shared

### {Topic/Domain}
- **Knowledge**: What was shared
- **Source**: Who shared it (if relevant)
- **Context**: Why this knowledge matters
- **Applications**: How team can use this knowledge

## Lessons Learned

### {Lesson Category}
- **Lesson**: What we learned
- **Source**: What experience taught us this
- **Implication**: How this changes our approach
- **Documentation Need**: Should this be written down somewhere?

## Expertise Transfer

### {Subject Matter}
- **Expert**: Who has deep knowledge
- **Knowledge Gap**: What others need to learn
- **Transfer Method**: How knowledge will be shared
- **Timeline**: When this transfer should happen

## Institutional Knowledge

### {Process/System/Relationship}
- **Context**: Background information shared
- **Key Details**: Important specifics to remember
- **Stakeholders**: Who else should know this
- **Documentation Status**: Is this captured anywhere?

## Learning Opportunities Identified

### {Skill/Knowledge Area}
- **Gap Identified**: What we need to learn
- **Priority**: [High|Medium|Low]
- **Learning Method**: [Training|Mentoring|Documentation|Experience]
- **Owner**: Who will drive this learning
- **Timeline**: When we need this knowledge

## Knowledge Preservation

- **Critical Knowledge at Risk**: Knowledge that exists with only one person
- **Documentation Priorities**: What knowledge should be written down
- **Knowledge Sharing Sessions**: Future sessions needed
```

**Generate the B46 block now using the transcript provided.**