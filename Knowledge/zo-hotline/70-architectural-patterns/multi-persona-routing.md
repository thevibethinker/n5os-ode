---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# Multi-Persona Routing Pattern

## What It Is

- Zo automatically switches between specialized personas based on task type
- Each persona has domain expertise and behavioral rules
- Creates consistent, context-appropriate responses

## When to Use

- Different types of requests need different AI behavior
- You want expert-level responses in multiple domains
- Tasks require specialized knowledge or tone
- Consistency matters across similar request types

## Minimal Build Recipe

- Create personas: `create_persona("Expert Name", "Specialized prompt")`
- Add routing rules to determine when each triggers
- Use `set_active_persona()` based on request classification
- Document handoff protocols between personas
- Test routing logic with sample requests

## Example Prompts

- "Set up technical writer persona for documentation, strategist for planning"
- "Create teacher persona for explanations, analyst for data requests"

## Common Failure Modes

- Personas overlap too much, causing confusion
- Routing rules too complex or contradictory
- No clear handoff when task changes mid-conversation