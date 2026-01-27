---
description: Generate B42 Internal Actions block for internal-only action items and tasks
tags: [meeting-intelligence, block-generation, b42, internal-actions, tasks]
tool: true
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_kjU4NIoVthBGRdTk
---

# Generate B42: Internal Actions

Extract and structure internal action items that don't require external coordination.

## Purpose

Separate internal actions (team processes, internal systems, documentation) from external commitments. These are tasks the team controls completely without external dependencies.

## Input Format

Meeting transcript with internal discussions containing task assignments, process improvements, and internal work items.

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
# B42: Internal Actions

## Process Actions

### {Action Item}
- **Owner**: {Name}
- **Category**: [Documentation|Systems|Process|Tooling]
- **Timeline**: {Expected completion}
- **Dependencies**: Internal blockers or requirements
- **Success Criteria**: How we'll know it's done

## System/Tool Updates

### {System/Tool Name}
- **Action**: What needs to be done
- **Owner**: {Name}
- **Impact**: Who benefits and how
- **Timeline**: {Expected completion}

## Documentation Tasks

### {Documentation Item}
- **Type**: [Playbook|Process Doc|Knowledge Base|README]
- **Owner**: {Name}
- **Audience**: Who will use this
- **Timeline**: {Expected completion}

## Recurring Tasks

### {Recurring Action}
- **Frequency**: {How often}
- **Owner**: {Name}
- **Process**: Brief description of what's involved
- **Review Date**: When to evaluate if still needed
```

**Generate the B42 block now using the transcript provided.**