---
title: Position Seed Interview
description: |
  Structured interview to extract V's cornerstone positions. 
  Seeds the position tracking system with known, high-confidence beliefs
  before automated extraction begins.
tags:
  - positions
  - worldview
  - setup
tool: true
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
provenance: con_UZUPaOsIaw4Xb9hD
---

# Position Seed Interview

## Purpose

Extract 5-10 cornerstone positions from V to seed the position tracking system. These become anchor points that:
- Validate the schema before automation
- Provide comparison anchors for extraction quality
- Prevent cold-start problem

## Interview Protocol

For each cornerstone position, capture:

1. **Claim** — The position stated crisply (1-2 sentences max)
2. **Confidence** — 0.0-1.0 scale (cornerstone = 0.85+)
3. **Topic** — Hierarchical category (e.g., `careerspan/recruiting/future`)
4. **Key sources** — Where this belief crystallized (meetings, experiences, readings)
5. **Defense count** — How many times have you defended this publicly?

## Suggested Domains

Pull from these areas to ensure coverage:

- **Careerspan** — Recruiting, product, GTM, market position
- **AI** — Agents, automation, future-of-work, LLM strategy
- **Founder** — Strategy, operations, personal growth
- **Worldview** — Career philosophy, society, technology trends

## Output

For each position, create a markdown file at:
`Knowledge/positions/<topic>/<position-slug>.md`

With frontmatter following the position schema from the build plan.

## Interview Questions

1. "What's a belief about [domain] you'd defend publicly and have defended before?"
2. "When did this belief crystallize? What was the moment?"
3. "How confident are you? 0-100%"
4. "What would change your mind?"
5. "Is there tension with any other position you hold?"

## Quality Bar

- Each position must be **specific** enough to be falsifiable
- Each position must be **V's own** (speaker: V, v_stance: endorsed)
- Confidence must be 0.85+ for cornerstone status
- At least 2 domains represented

---

## Execution

Run this interview conversationally. Don't force all 10 positions at once — 5 high-quality cornerstones are better than 10 weak ones.

