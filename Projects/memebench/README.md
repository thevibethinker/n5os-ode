---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
provenance: con_jfdmQM1xwEi3Gcta
---

# MemeBench

**An AI benchmark for cultural zeitgeist fluency.**

## What This Tests

MemeBench evaluates AI models' ability to interpret meme culture—not just image recognition, but understanding:

- **Layered irony** — Multiple levels of sincerity/irony
- **Cultural references** — The source material being riffed on
- **Temporal context** — When the meme emerged and why it mattered then
- **Sociological subtext** — Class dynamics, generational attitudes, political sentiment encoded in the meme
- **Format literacy** — Why *this* format for *this* message

Traditional benchmarks test factual recall or reasoning. MemeBench tests something different: **does the AI actually get the joke?**

## Why It Matters

Memes are compressed sociological information. They encode:
- Class dynamics ("Old Money vs New Money" memes)
- Generational trauma (Millennial nihilism memes)
- Political sentiment (protest imagery remixes)
- Absurdist philosophy (deep-fried irony-poisoned content)
- Collective in-group knowledge (format recognition)

An AI that "gets" memes demonstrates deep cultural pattern recognition—a proxy for sociological intelligence that no current benchmark measures.

## Categories

MemeBench tests 6 categories of meme comprehension:

| # | Category | Tests |
|---|----------|-------|
| 1 | **Absurdist Meta-Irony** | Layers of irony, post-ironic content, deliberate meaninglessness |
| 2 | **Corporate Cringe** | Recognition of inauthenticity, "fellow kids" dynamics |
| 3 | **Generational Trauma** | Millennial/Gen-Z nihilism, economic anxiety, collective coping |
| 4 | **Political Subtext** | Coded political messaging, dog whistles, ideological formatting |
| 5 | **Internet Archaeology** | Historical meme literacy, format evolution, cultural references |
| 6 | **Format Literacy** | Understanding why specific formats carry specific meanings |

See `categories/` for detailed definitions.

## Scoring

Each response is scored on 5 dimensions (1-5 scale):

1. **Cultural Reference Recognition** — Identifies the source material
2. **Irony Detection** — Recognizes sincerity vs irony layers
3. **Temporal Context** — Understands historical placement
4. **Sociological Subtext** — Gets the underlying social commentary
5. **Format Appropriateness** — Understands format choice

Total score: 5-25 per question.

See `scoring/rubric.yaml` for detailed rubric.

## Status

🚧 **Framework only** — Categories and scoring defined. No evaluation data yet.

## Structure

```
memebench/
├── README.md           # This file
├── categories/         # Category definitions
├── scoring/            # Scoring rubric
├── data/               # Evaluation questions (TBD)
└── src/                # Evaluation harness (scaffold)
```

## Author

Vrijen Attawar | Pilot project for benchmark construction learning

