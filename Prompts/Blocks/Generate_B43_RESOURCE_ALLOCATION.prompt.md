---
description: Generate B43 Resource Allocation block for resource planning and capacity discussions
tags: [meeting-intelligence, block-generation, b43, resource-allocation, capacity]
tool: true
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_kjU4NIoVthBGRdTk
---

# Generate B43: Resource Allocation

Document resource allocation decisions, capacity planning, and workload distribution from internal meetings.

## Purpose

Internal meetings often involve discussions about how to allocate limited resources - time, budget, people. This block captures these resource planning elements.

## Input Format

Meeting transcript containing discussions about resource constraints, capacity planning, budget allocation, or workload distribution.

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
# B43: Resource Allocation

## Capacity Planning

### Team Capacity Assessment
- **Available Hours**: {Total team capacity}
- **Committed Work**: {Currently allocated hours/percentage}
- **Available Capacity**: {Remaining capacity}
- **Capacity Constraints**: Key bottlenecks or limitations

## Resource Allocation Decisions

### {Project/Initiative}
- **Resources Allocated**: {People, time, budget}
- **Priority Level**: [P0|P1|P2|P3]
- **Resource Owner**: Who manages these resources
- **Duration**: Expected resource commitment timeline
- **Trade-offs**: What we're not doing to prioritize this

## Budget Allocation

### {Budget Category}
- **Allocated Amount**: ${Amount} or {Percentage}
- **Purpose**: What this funds
- **Owner**: Who manages this budget
- **Review Timeline**: When to reassess allocation

## Workload Distribution

### Current Sprint/Period
- **{Team Member}**: {Workload percentage} - Focus: {Primary projects}
- **{Team Member}**: {Workload percentage} - Focus: {Primary projects}

## Resource Constraints

- **Bottlenecks**: What's limiting our capacity
- **Missing Resources**: What we need but don't have
- **Potential Solutions**: How we might address constraints
```

**Generate the B43 block now using the transcript provided.**