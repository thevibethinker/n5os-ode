---
description: Generate B45 Team Dynamics block for interpersonal and cultural observations
tags: [meeting-intelligence, block-generation, b45, team-dynamics, culture]
tool: true
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_kjU4NIoVthBGRdTk
---

# Generate B45: Team Dynamics

Document team dynamics, communication patterns, and cultural signals from internal meetings.

## Purpose

Internal meetings reveal important team dynamics - communication styles, conflict patterns, collaboration quality, and team health signals. This block captures these interpersonal observations.

## Input Format

Meeting transcript with internal team interactions showing communication patterns, collaborative moments, tension points, or team culture signals.

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
# B45: Team Dynamics

## Communication Patterns

### Positive Dynamics Observed
- **Collaborative Moments**: When team worked well together
- **Open Communication**: Examples of transparent dialogue
- **Mutual Support**: Team members helping each other
- **Constructive Feedback**: Healthy challenge/feedback exchanges

### Areas for Attention
- **Communication Gaps**: Misunderstandings or unclear exchanges
- **Participation Imbalances**: Who spoke more/less than usual
- **Tension Points**: Moments of disagreement or friction
- **Unresolved Issues**: Topics that need follow-up

## Team Energy & Engagement

### Energy Level
- **Overall Tone**: [Energized|Focused|Stressed|Tired|Mixed]
- **Engagement Indicators**: Who was most/least engaged
- **Momentum Signals**: Areas where team feels excited vs. stuck

## Cultural Signals

### Team Values in Action
- **Decision Making**: How team approaches choices
- **Problem Solving**: Team's collaborative approach
- **Conflict Resolution**: How disagreements are handled
- **Innovation**: Openness to new ideas and approaches

## Relationship Dynamics

### Working Relationships
- **Strong Partnerships**: Effective collaborations observed
- **Communication Styles**: Different approaches and how they mesh
- **Leadership Moments**: Natural leadership behaviors

## Team Development Opportunities

- **Skill Gaps**: Areas where team could grow
- **Process Improvements**: Better ways to work together
- **Communication Enhancements**: How to improve dialogue
```

**Generate the B45 block now using the transcript provided.**