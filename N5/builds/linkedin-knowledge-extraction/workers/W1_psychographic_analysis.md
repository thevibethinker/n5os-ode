---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zTfB7kehxEEHmaoC
---

# WORKER ASSIGNMENT: W1 — Psychographic Analysis

**Blocked by:** W0 (needs `posts.jsonl`, `articles.jsonl`, `comments.jsonl`)
**Objective:** Analyze V's LinkedIn corpus to produce a structured psychographic profile at the synthesis level.

## Context from Parent

V wants to understand: "Who am I as a person? What do I write about? What animates me, pisses me off, excites me, upsets me?"

This is semantic-level analysis. Do NOT extract direct quotes for linguistic/voice purposes (voice library handles that). Stay at the synthesis level.

## Input Files

From W0's conversation workspace (paths will be in W0's completion message):
- `posts.jsonl` — 130 posts
- `articles.jsonl` — 3 long-form articles
- `comments.jsonl` — 689 comments (reveals what V *reacts to*)

## Analysis Dimensions

### 1. Topical Domains
Cluster content into domains. Expected domains (but discover what's actually there):
- Career coaching / job search
- Hiring market critique
- AI/automation in hiring
- Entrepreneurship / Careerspan
- Personal philosophy
- Industry commentary

**Output:** Domain frequency distribution + representative themes per domain

### 2. Emotional Valence Map
Classify content by emotional driver:
| Valence | Indicators |
|---------|------------|
| Anger/Frustration | Critique, calling out, "broken," "absurd" |
| Advocacy | "Should," "must," prescriptive language |
| Excitement | Announcements, possibilities, optimism |
| Reflection | Personal stories, lessons learned |
| Teaching | Explanatory, instructional |

**Output:** Distribution + what triggers each emotional state

### 3. Recurring Targets
Who/what does V direct energy toward?
- Positive targets (champions, allies, causes)
- Negative targets (villains, broken systems, bad actors)

### 4. Self-Positioning Patterns
How does V position himself?
- Expert vs. fellow traveler
- Insider vs. outsider
- Critic vs. builder
- Solo voice vs. community voice

### 5. Temporal Evolution (if detectable)
Has V's focus or tone shifted over the 5-year posting history (2020-2025)?

## Output Artifact

Create a file called `psychographic_portrait.md` in your conversation workspace:

```markdown
---
created: 2026-01-12
subject: Vrijen Attawar
source: LinkedIn corpus (130 posts, 3 articles, 689 comments)
analysis_type: psychographic
provenance: [your_conversation_id]
---

# Psychographic Portrait: Vrijen Attawar

## Executive Summary
[2-3 paragraph synthesis of who V is based on this corpus]

## Topical Domains
[Domain breakdown with percentages and themes]

## Emotional Drivers
### What Animates V
[...]
### What Frustrates V
[...]
### What Excites V
[...]

## Worldview Positioning
[How V sees himself in relation to his industry/audience]

## Recurring Targets
### Champions (Positive)
[...]
### Critiques (Negative)
[...]

## Evolution Over Time
[Any detectable shifts 2020→2025]

## Synthesis
[Final integration — the coherent picture]
```

## Success Criteria

1. Portrait covers all 5 analysis dimensions
2. Claims are grounded in corpus patterns (not speculation)
3. Stays at synthesis level (no direct quote extraction)
4. File created in conversation workspace

## On Completion

1. Print path to `psychographic_portrait.md`
2. Print a 3-sentence summary of findings
3. Update STATUS.md: mark W1 as ✅ Complete

