---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_zOEUyAwnj6feZ9hH
status: canonical
---

# Socratic Articulation Protocol

## Purpose

Bypass AI detection by inverting the content creation workflow: **extract V's spoken articulation first**, then arrange (not compose) using voice library patterns. The AI acts as interviewer → arranger, never as composer.

## Core Principle

**"V would text this to a friend"** — the succinctness test.

If the output is longer or more formal than what V would naturally text, it needs tightening.

## The Detection Problem

Pangram and similar detectors identify AI-generated text through:
- Token distribution patterns (AI outputs are statistically "smooth")
- Structural regularity (consistent paragraph length, parallel constructions)
- Compositional signatures (how ideas are assembled, not just word choice)

**Solution:** If raw material is human-spoken and arrangement follows human-written patterns, the token distribution inherits from human sources.

## Architecture

```
V speaks (raw articulation)
        ↓
[Socratic Extraction] ← Content-type spec defines questions
        ↓
Raw material: V's phrases, examples, key lines
        ↓
[Synthesis] ← Voice library + tightening factor
        ↓
Output: V's words, V's style, human signal
```

## Source Material Locations

| Source | Location | Size |
|--------|----------|------|
| LinkedIn corpus | `file 'N5/builds/voice-library-v2/linkedin_corpus.jsonl'` | 385 posts |
| LinkedIn (content library) | `file 'Knowledge/content-library/social-posts/linkedin/'` | ~20 posts |
| Articles (Canon) | `file 'Personal/Knowledge/Canon/VibeThinker/'` | 8+ pieces |
| Articles (Canon) | `file 'Personal/Knowledge/Canon/Vrijen/'` | Essays |
| Voice primitives | `file 'Knowledge/voice-library/voice-primitives.md'` | Shell |

## Unit Size: Paragraph-Level Chunks

**Problem:** Sentence-level primitives lose characteristic patterns. A single sentence is linguistically meaningless for voice—it's the *flow across sentences* that carries the human signal.

**Solution:** Extract and store paragraph-level chunks (3-5 sentences) that preserve:
- Rhythm and cadence across sentences
- Transition patterns
- Characteristic development of ideas
- Human token distribution

## Content Type Taxonomy (V's Actual Patterns)

### 1. Philosophical / System Thinking
- **Pattern**: Opens with a high-level observation or a specific failure in a complex system (ATS, resume tailoring). Moves to a "why" explanation involving incentives or architecture.
- **Move**: The "Turning the Prism" move - taking a familiar object (the resume) and looking at it as a "broken proxy."
- **Exemplar**: "Now let me be blunt: resumes are fundamentally terrible. They're one-dimensional representations of complex, nuanced careers. In an ideal world, they would be as extinct as dial-up internet."

### 2. Contrarian Take / Myth Busting
- **Pattern**: Directly attacks a common behavior or piece of advice. Often uses "Real Talk" or "Warning" tags.
- **Move**: The "Rational Actor" move - explaining why people do the "wrong" thing because of flawed incentives.
- **Exemplar**: "The old guard optimized for efficiency and employers. This crew optimizes for self-advocacy and humanity. The collaboration wasn't performative—it was founders genuinely wanting each other to succeed."

### 3. Tactical Career Advice (Pragmatic)
- **Pattern**: Specific, actionable steps with a narrative wrapper. Often starts with a story of a mistake or a success.
- **Move**: The "Insider Correction" - "I used to think X, but after doing Y, I realize Z."
- **Exemplar**: "What most people don't realize: recruiters spent 5 seconds on your resume *to decide* whether they're going to spend an additional 30 seconds on your resume."

### 4. Product Advocacy (Narrative-Led)
- **Pattern**: Weaving product capability into a personal story of struggle or a client's win. Avoids "feature lists."
- **Move**: The "Stack Displacement" - mentioning how a new tool "Thanos-snapped" old ones out of existence.
- **Exemplar**: "Y'all Thanos-snapped ChatGPT, Claude, and Notion (and a few other minor ones) out of my stack. Imagine a product so good, using it saves you $100 a month off rip."

### 5. Community / Connection
- **Pattern**: High-signal shout-outs that highlight technical or creative depth in others.
- **Move**: The "Top 1%" move - praising a specific cross-domain reference (e.g., "Ted Chiang and Ronald Dahl in the same paragraph").
- **Exemplar**: "Oh hey look it's two of my favorite people in tech making all the sense in the world."

### 6. General Observation / Reflection
- **Pattern**: Short, punchy reflections on the speed of change or human behavior.
- **Move**: The "Wild Yo" - expressing amazement at the pace of technological shift.
- **Exemplar**: "Software transmissions went from CDs to digital downloads to linked text files just in our lifetime. Shit is wild yo."

## Socratic Extraction Protocol

### Phase 1: Orientation (30 seconds)
- Confirm content type
- Confirm target medium (LinkedIn, blog, X thread)
- Confirm length target

### Phase 2: Core Extraction (2-5 minutes)

**Universal questions:**
- "What's the one thing you want people to remember?"
- "Give me an example from your work that proves this."
- "How would you explain this at a dinner party?"

**Type-specific questions:**

#### For Contrarian Take:
- "What's the conventional wisdom you're pushing against?"
- "What have you seen that made you realize this?"
- "What's the strongest counterargument?"

#### For Founder Observation:
- "Where did you first notice this pattern?"
- "Give me specific numbers or behaviors."
- "Why do founders keep doing this?"

#### For Career Tech Insight:
- "What's the problem in one sentence?"
- "Why do current tools miss this?"
- "What would solving this actually look like?"

#### For Vulnerable Moment:
- "What's the specific moment?"
- "What did it feel like at the time?"
- "What do you do differently now?"

#### For Thought Leadership:
- "What's your thesis in one sentence?"
- "What's the strongest evidence you have?"
- "Where are you uncertain?"

### Phase 3: Line Hunting
- "Say that again—I want to capture that exact phrase."
- "That's good. Can you make it punchier?"
- "What's the one-liner version?"

## Synthesis Protocol

### Inputs:
1. **Spoken raw material** — V's phrases from extraction
2. **Voice library** — Paragraph-level chunks with characteristic patterns
3. **Content-type spec** — Structure and tone for target medium
4. **Tightening factor** — Bias toward brevity

### Process:
1. **Arrange** V's spoken phrases into target structure
2. **Bridge** using voice library patterns (paragraph-level, not sentence-level)
3. **Tighten** — apply succinctness test ("Would V text this?")
4. **Verify** — read aloud, check for AI-smooth passages

### Constraints:
- **No invention** — only arrange what V said or wrote
- **Preserve exact phrases** — V's words are the signal
- **Paragraph chunks** — never decompose to sentence level
- **Tighten, don't expand** — brevity is the bias

### Quality Gate:
- [ ] Every key phrase came from V (spoken or voice library)
- [ ] No AI-composed transitions (use V's existing transition patterns)
- [ ] Passes "Would V text this?" succinctness test
- [ ] Paragraph rhythm feels irregular (not AI-smooth)

## Testing Protocol

After synthesis:
1. Run through Pangram (`python3 /home/workspace/Integrations/Pangram/pangram.py analyze "..."`)
2. Target: <50% AI detection (ideal: <30%)
3. If fails: identify AI-smooth passages, replace with V's raw phrases
4. Iterate until passes

## Next Steps

1. [ ] Analyze LinkedIn corpus to refine content type taxonomy
2. [ ] Extract paragraph-level chunks for voice library
3. [ ] Test protocol on Talent-Optionality article
4. [ ] Refine based on Pangram results

---

## Version History

- 1.0 (2026-01-12): Initial protocol based on Pangram research and V's workflow proposal

