---
description: Generate B40 Internal Decisions block for internal meeting transcripts
tags: [meeting-intelligence, block-generation, b40, internal-decisions]
tool: true
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_kjU4NIoVthBGRdTk
---

# Generate B40: Internal Decisions

Extract and document strategic decisions made during internal meetings.

## Purpose

Internal meetings often contain critical decision points that shape company direction. This block captures explicit decisions, their rationale, and implementation context.

## Input Format

Meeting transcript with internal team participants. Expected content includes strategic discussions, option evaluations, and explicit decision-making moments.

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
# B40: Internal Decisions

## Strategic Decisions

### Decision: {Decision Title}
- **Context**: What prompted this decision
- **Options Considered**: [Option A, Option B, Option C]
- **Decision Made**: Final choice with brief rationale
- **Decision Maker**: Who made the final call
- **Implementation**: Next steps or implications

### Decision: {Another Decision}
[... same structure ...]

## Deferred Decisions

### {Decision Title}
- **Reason for Deferral**: Why postponed
- **Required Information**: What's needed before deciding
- **Timeline**: When decision will be revisited

## Decision Dependencies

- {Decision A} → requires → {Decision B}
- {Decision C} → blocks → {Decision D}
```

**Generate the B40 block now using the transcript provided.**