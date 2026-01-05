---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.1
provenance: con_zGQhfwqIoAIKek4Q
---

# Reflection Block Registry v2

**System:** Reflection Engine v2
**Namespace:** R-Series (R00-R09+)
**Location:** `Prompts/Blocks/Reflection/`

## Block Definitions

| Block | Name | Domain | What It Captures |
|-------|------|--------|------------------|
| R00 | Emergent | Extensibility | Content that doesn't fit existing blocks — generates provisional framework |
| R01 | Personal Insight | Self | Emotional, growth, self-awareness |
| R02 | Learning Note | Knowledge | Insights from reading, conversations, research |
| R03 | Strategic Thought | Direction | Vision, positioning, long-term thinking (Careerspan) |
| R04 | Market Signal | Competition | Competitive intel, market trends, opportunities |
| R05 | Product Idea | Building | Features, roadmap, user insights (Careerspan product) |
| R06 | Synthesis | Meta | Cross-reflection patterns, emergent insights |
| R07 | Prediction | Future | Trends, forecasts, what's coming (external/macro) |
| R08 | Venture Idea | Ventures | Startup ideas outside Careerspan |
| R09 | Content Idea | Expression | Blog posts, social content, thought leadership |

## Block Categories

### Careerspan-Centric
- R03 (Strategic) — Company direction
- R04 (Market) — Competitive landscape
- R05 (Product) — What to build

### Personal/Internal
- R01 (Personal) — Self-awareness, growth
- R02 (Learning) — Knowledge capture

### External/Macro
- R07 (Prediction) — Trends and forecasts
- R08 (Venture) — Non-Careerspan ideas

### Expression
- R09 (Content) — Things to write/say publicly

### Meta
- R00 (Emergent) — Extensibility mechanism
- R06 (Synthesis) — Cross-block patterns

## Block Selection Logic

The orchestrator (`@Process Reflection`) determines which blocks apply based on content analysis.

**Core (always attempt):** R01, R02, R03
**Domain-specific (if content warrants):** R04, R05, R07, R08, R09
**Meta (special cases):** R06 (cross-domain synthesis), R00 (novel content)

## Extensibility

When reflection content doesn't fit R01-R09:
1. Generate R00 with a provisional framework
2. Flag for V's review
3. If pattern recurs, consider promoting to formal R-block (R10, R11, etc.)

## Output Location

Processed reflections are stored in: `Personal/Reflections/YYYY/MM/`

Filename format: `YYYY-MM-DD_<slug>.md`

