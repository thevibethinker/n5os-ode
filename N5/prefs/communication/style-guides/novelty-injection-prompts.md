---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_TBnwuolXxSkp5t1D
type: prompt_templates
status: active
---

# Novelty Injection Prompts

**Purpose:** Break out of AI-generic patterns when content feels "correct but boring." These prompt templates inject creative constraints that force distinctive, V-like output.

**Part of:** Voice Library V2 (Phase 4)

---

## When to Use

| Trigger | Action |
|---------|--------|
| Pangram score > 0.5 after first pass | Apply Strategy 1 or 2 |
| Content feels "correct but boring" | Apply Strategy 3 or 4 |
| Topic is saturated (many people writing about it) | Apply Strategy 5 |
| Explicitly requested ("make this spicier") | User's choice |
| Draft lacks distinctive V-isms | Apply Strategy 1 with high-distinctiveness primitives |

---

## Strategy 1: Forced Primitive Injection

**Use when:** Draft lacks V's linguistic fingerprint. Pangram score too high.

**How it works:** Retrieve high-distinctiveness primitives (≥0.8) and force their inclusion.

### Templates

```
You MUST incorporate this exact phrase somewhere in the piece: "[PRIMITIVE]"

Find a natural place for it—don't force it awkwardly. The phrase should feel 
like it belongs, not like it was stapled on.
```

```
Rewrite this paragraph incorporating at least ONE of these V-isms:
- "[PRIMITIVE_1]"
- "[PRIMITIVE_2]"
- "[PRIMITIVE_3]"

Choose the one that fits most naturally. If none fit, explain why.
```

```
This draft is missing V's voice. Inject this conceptual frame: "[FRAME]"

The frame should shape how you present the main argument, not just appear 
as a throwaway line.
```

### Retrieval Command
```bash
python3 N5/scripts/retrieve_primitives.py --min-distinctiveness 0.8 --count 5 --json
```

---

## Strategy 2: Constraint Prompting

**Use when:** Default framing is generic. Need fresh angles.

**How it works:** Force explanation through an unexpected domain's lens.

### Templates

```
Explain [CONCEPT] using ONLY metaphors from [DOMAIN].

Domains to try:
- Cooking/kitchen operations
- Construction/architecture  
- Gardening/cultivation
- Sports/competition
- Music/performance
- Navigation/exploration
```

```
Describe this without using any of these words: [BANNED_WORDS]

Common banned lists:
- Business jargon: leverage, synergy, optimize, scalable, robust
- AI-speak: delve, tapestry, embark, landscape, realm
- Filler: very, really, actually, basically, essentially
```

```
Write this as if explaining to [AUDIENCE]:
- A skeptical CFO who hates buzzwords
- A 10-year-old who asks "but why?" repeatedly
- Someone who's been burned by this exact promise before
- A founder who's heard 50 pitches today
```

### Domain Mapping (V's natural domains)
| Topic | Natural V-domain |
|-------|------------------|
| Hiring/recruiting | Agriculture, filtering, sorting |
| Career decisions | Portfolio theory, optionality |
| Incentive design | Game theory, mechanism design |
| Leadership | Coaching, gardening |
| Tech products | Infrastructure, plumbing |

---

## Strategy 3: Multi-Angle Generation

**Use when:** Not sure which framing works best. Want options.

**How it works:** Generate multiple versions with different approaches, then select.

### Templates

```
Generate 3 versions of this [SECTION]:

Version A: Lead with the contrarian take
Version B: Lead with a concrete story/example  
Version C: Lead with a provocative question

Keep each to ~[WORD_COUNT] words. I'll pick the best.
```

```
Write 3 different opening hooks for this piece:

1. Start with a surprising statistic or fact
2. Start with a "most people think X, but actually Y" inversion
3. Start with a vivid, specific scenario

Each hook should be 2-3 sentences max.
```

```
Give me 3 framings for the core argument:

1. The "it's not about X, it's about Y" reframe
2. The "everyone's solving the wrong problem" frame
3. The "here's what changed that makes this matter now" frame

One paragraph each. Be specific to [TOPIC].
```

---

## Strategy 4: Socratic Iteration

**Use when:** Draft exists but feels flat. Need to push deeper.

**How it works:** Challenge the draft with pointed questions that force improvement.

### Templates

```
This draft is correct but boring. Answer these questions, then rewrite:

1. What would make a reader stop scrolling?
2. What's the most surprising implication you haven't stated?
3. Where are you hedging when you should be asserting?
4. What's the one sentence that captures the whole point?

Now rewrite paragraph [N] with more edge.
```

```
Play devil's advocate on this draft:

1. What's the strongest objection someone could raise?
2. Where does the logic have gaps?
3. What are you assuming that might not be true?

Address the strongest objection directly in the piece.
```

```
This reads like AI wrote it. Specifically:

- Where is it too balanced/hedged?
- Where does it use generic examples instead of specific ones?
- Where does it tell instead of show?

Fix those specific problems.
```

---

## Strategy 5: Inversion Prompt

**Use when:** Topic is saturated. Need to stand out from the crowd.

**How it works:** Write the opposite take first, then find the real insight.

### Templates

```
Write the contrarian take on [TOPIC]:

What would someone who disagrees say? Why might they be right?

Don't strawman—give the strongest version of the opposing view.
Then: what's the synthesis that's smarter than both positions?
```

```
Everyone says [COMMON WISDOM]. 

Write a piece arguing the opposite. Not to be edgy—because you 
actually believe there's truth in the inversion.

What evidence supports the contrarian view?
```

```
What's the thing everyone in [FIELD] knows but doesn't say publicly?

Write about that. Be specific. Name names if appropriate (or describe 
the pattern without names if not).
```

```
Invert the framing:

Original: "[STANDARD_FRAMING]"
Inverted: "[OPPOSITE_FRAMING]"

Now write from the inverted frame. The inversion should reveal something 
the original framing obscured.
```

---

## Combination Patterns

### Pattern A: Pangram Rescue
When Pangram score > 0.5:
1. Retrieve 3 high-distinctiveness primitives (Strategy 1)
2. Identify the paragraph with highest AI probability
3. Force primitive injection into that paragraph
4. Re-check with Pangram
5. Max 2 iterations

### Pattern B: Boring-to-Bold
When draft feels flat:
1. Run Socratic Iteration (Strategy 4) to identify weak spots
2. Apply Constraint Prompting (Strategy 2) to one section
3. Generate 3 alternative hooks (Strategy 3)
4. Select best combination

### Pattern C: Saturated Topic
When topic is crowded:
1. Write Inversion take first (Strategy 5)
2. Identify the genuine insight from the inversion
3. Reframe main piece around that insight
4. Inject 1-2 primitives that reinforce the fresh angle

---

## Integration with Voice Library

These prompts work best when combined with voice primitive retrieval:

```bash
# Get primitives relevant to topic
python3 N5/scripts/retrieve_primitives.py --topic "[TOPIC]" --count 5

# Get high-distinctiveness for injection
python3 N5/scripts/retrieve_primitives.py --min-distinctiveness 0.8 --random --count 3

# Get domain-specific primitives
python3 N5/scripts/retrieve_primitives.py --domains career,hiring --count 5
```

---

## Anti-Patterns (Don't Do This)

| Anti-Pattern | Why It Fails |
|--------------|--------------|
| Forcing ALL retrieved primitives | Feels like a word salad |
| Using novelty injection on every piece | Exhausting; loses impact |
| Contrarian for contrarian's sake | Comes off as try-hard |
| Banning too many words | Creates awkward circumlocutions |
| Multi-angle on tight deadlines | Time sink; just pick one and ship |

---

## Related Files

- **Retrieval:** `N5/scripts/retrieve_primitives.py`
- **Post-check:** `N5/scripts/voice_postcheck.py`
- **Voice System:** `N5/prefs/communication/voice-primitives-system.md`
- **Vibe Writer:** `Prompts/Generate With Voice.prompt.md`

