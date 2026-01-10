---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_ctpO4tmxumzIn8RP
tool: true
description: "View your intellectual landscape - what ideas are rising, stabilizing, evolving, or decaying"
tags: [resonance, ideas, patterns, self-reflection, cognitive-mirror]
rotation_eligible: true
rotation_category: self-reflection
rotation_frequency: weekly
---
# Resonance Report

Generate a report of V's intellectual landscape based on the Context Graph.

## What This Shows

1. **Resonance Hierarchy** — Your ideas classified by how often they appear:
   - L0 Cornerstones (10+ meetings): Foundational beliefs
   - L1 Active Theses (4-9 meetings): Ideas you're developing
   - L2 Recurring Tools (2-3 meetings): Frameworks you reach for
   - L3 Sparks (1 meeting): Novel ideas worth watching

2. **Movement** — Ideas that have shifted levels recently

3. **Evolution Events** — Where ideas have been expanded, refined, challenged, or abandoned

4. **Decay Watch** — Ideas you haven't mentioned in 30+ days

## Execution

```bash
# Generate fresh resonance index
python3 /home/workspace/N5/scripts/resonance/pattern_surfacer.py generate

# View the report
python3 /home/workspace/N5/scripts/resonance/pattern_surfacer.py report

# Check evolution events
python3 /home/workspace/N5/scripts/resonance/evolution_tracker.py report

# Check a specific idea
python3 /home/workspace/N5/scripts/resonance/evolution_tracker.py check --idea "<idea-slug>"
```

## Output Format

Present findings conversationally:

### Your Intellectual Landscape (as of {date})

**Active Theses** (what you're developing):
- {idea}: {context}

**Rising Ideas** (Sparks → Recurring):
- {idea}: appeared in {n} recent meetings

**Under Challenge**:
- {idea}: challenged by {person} on {date}

**Decaying** (30+ days silent):
- {idea}: last mentioned {date}

## When to Run

- After a week of heavy meetings
- When feeling intellectually scattered
- Before strategic planning sessions
- When you want to see "what's sticking"

