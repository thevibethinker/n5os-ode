---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_TBnwuolXxSkp5t1D
type: style_guide
status: active
---

# Novelty Injection Prompts

Part of Voice Library V2 (Phase 4: Chaos Factor).

These prompt templates break predictable AI patterns and inject distinctiveness into generated content. Use when content feels "correct but boring" or Pangram scores are too high.

---

## When to Use Novelty Injection

| Trigger | Action |
|---------|--------|
| Pangram AI score > 0.6 | Apply 1-2 strategies below |
| Content feels generic/safe | Use Socratic Iteration or Inversion |
| Topic is saturated (many write about it) | Use Constraint Prompting or Forced Primitive |
| Explicit request ("make this spicier") | Use Multi-Angle Generation |
| Opening paragraph is weak | Use Multi-Angle on first paragraph only |

---

## Strategy 1: Forced Primitive Injection

**Purpose:** Guarantee usage of distinctive V-phrases/metaphors.

**Template:**
```
You MUST incorporate this [primitive_type] somewhere in the piece: "[primitive]"

Integrate it naturally — don't force it if it truly doesn't fit, but try hard to find 
a place where it resonates. The primitive should feel like it belongs, not like it 
was inserted.
```

**Example:**
```
You MUST incorporate this metaphor somewhere in the piece: "gardening position in 
the midwest and an investment banking internship in New York City"

Use it to illustrate contrast, optionality, or the breadth of career paths.
```

**Retrieval:**
```bash
python3 N5/scripts/retrieve_primitives.py --min-distinctiveness 0.8 --count 3 --json
```

---

## Strategy 2: Constraint Prompting

**Purpose:** Force creative thinking by limiting available metaphor domains.

**Templates:**

**Domain Lock:**
```
Explain [concept] using only metaphors from [domain].

Domains to try:
- cooking/kitchen (recipes, ingredients, heat, timing)
- gardening (seeds, seasons, pruning, harvest)
- construction (foundations, scaffolding, blueprints)
- sports (training, competition, teamwork, coaching)
- music (rhythm, harmony, improvisation, composition)
- navigation (maps, compass, waypoints, course correction)
```

**Word Budget:**
```
Rewrite this paragraph in exactly [N] words. Not approximately — exactly [N].
This constraint forces you to choose every word deliberately.
```

**Forbidden Words:**
```
Rewrite this without using any of these words: [list common/overused terms]

Forbidden for career content: passionate, excited, leverage, synergy, innovative
Forbidden for AI content: revolutionary, game-changing, cutting-edge, disrupt
```

---

## Strategy 3: Multi-Angle Generation

**Purpose:** Generate variety, then select best framing.

**Template:**
```
Generate 3 distinct versions of [this section/opening/paragraph]:

Version A: Lead with the counterintuitive insight
Version B: Lead with a specific story or example  
Version C: Lead with the stakes (what's at risk if reader ignores this)

Keep each version to [N] sentences. I'll pick the strongest opening.
```

**For headlines/hooks:**
```
Generate 5 different hooks for this piece:

1. Question that challenges assumption
2. Surprising statistic or fact
3. Contrarian statement
4. Specific story in 1 sentence
5. "What if" scenario

No generic hooks. Each must make a reader stop scrolling.
```

---

## Strategy 4: Socratic Iteration

**Purpose:** Push past the obvious first draft through directed critique.

**Templates:**

**Generic Detection:**
```
This draft feels safe. Identify the 2 most generic sentences and rewrite them 
with more specific, surprising language. What would make a reader screenshot this?
```

**Scroll-Stop Test:**
```
Rewrite paragraph [N] with a more surprising angle. 

Ask yourself: Would this make someone stop scrolling on LinkedIn? If not, 
it's not sharp enough. Find the unexpected take.
```

**"So What" Pressure:**
```
For each claim in this draft, answer "so what?" 

If the answer isn't compelling, either cut the claim or sharpen it until 
the "so what" is obvious and impactful.
```

---

## Strategy 5: Inversion Prompt

**Purpose:** Surface contrarian angles and strengthen arguments by addressing opposition.

**Templates:**

**Contrarian Take:**
```
Write the contrarian take on this topic. What would someone who disagrees say, 
and why might they be partially right?

Then: Does this contrarian view reveal a nuance we should incorporate into 
the main piece?
```

**Steel Man Opposition:**
```
What's the strongest argument against [position in draft]? 

Write 2-3 sentences presenting that argument charitably. Then decide: 
should we address this directly, or does it reveal a flaw in our thinking?
```

**Flip the Frame:**
```
This piece argues [X]. Write a version that argues the opposite.

Not to publish — but to find the weak points in our original argument and 
the strongest version of the counter-position.
```

---

## Strategy 6: Primitive Cascade

**Purpose:** Layer multiple primitives for compound distinctiveness.

**Template:**
```
Incorporate ALL of these primitives into the piece (naturally distributed):

1. [signature_phrase]: "[text]"
2. [metaphor]: "[text]"  
3. [conceptual_frame]: "[text]"

Don't cluster them — spread across the piece. Each should feel like it 
belongs in its location.
```

**Retrieval for cascade:**
```bash
# Get one of each type for maximum variety
python3 N5/scripts/retrieve_primitives.py --type signature_phrase --count 1 --json
python3 N5/scripts/retrieve_primitives.py --type metaphor --count 1 --json
python3 N5/scripts/retrieve_primitives.py --type conceptual_frame --count 1 --json
```

---

## Combining Strategies

**Light touch (Pangram 0.5-0.6):**
- Apply Strategy 1 (single forced primitive) OR Strategy 4 (Socratic on 1-2 paragraphs)

**Medium intervention (Pangram 0.6-0.7):**
- Apply Strategy 1 + Strategy 4
- OR Strategy 3 (multi-angle) on opening + Strategy 2 (constraint) on body

**Heavy intervention (Pangram > 0.7):**
- Start over with Strategy 5 (inversion) to find fresh angle
- Then apply Strategy 6 (primitive cascade)
- Final pass with Strategy 4 (Socratic on weakest sections)

---

## Anti-Patterns (Don't Do This)

| Anti-Pattern | Why It Fails |
|--------------|--------------|
| Inject 5+ primitives in short piece | Feels forced, damages flow |
| Use same primitive twice | Repetitive, loses impact |
| Force metaphor that doesn't fit topic | Reader notices the stretch |
| Apply all strategies at once | Overcorrection, loses coherence |
| Skip Pangram re-check after injection | Don't know if intervention worked |

---

## Quick Reference

```
# Check if novelty injection needed
python3 N5/scripts/voice_postcheck.py --text "..." --threshold 0.5

# Get high-distinctiveness primitives for injection
python3 N5/scripts/retrieve_primitives.py --min-distinctiveness 0.8 --count 3

# After injection, re-check
python3 N5/scripts/voice_postcheck.py --text "..." --threshold 0.5
```

---

## Related Files

- **Retrieval:** `N5/scripts/retrieve_primitives.py`
- **Post-check:** `N5/scripts/voice_postcheck.py`
- **System spec:** `N5/prefs/communication/voice-primitives-system.md`
- **Vibe Writer:** `Prompts/Generate With Voice.prompt.md`

