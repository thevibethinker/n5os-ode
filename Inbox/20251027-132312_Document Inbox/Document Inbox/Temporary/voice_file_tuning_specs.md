# Voice File Tuning Specifications

**Date:** 2025-10-12 18:22:00 ET  
**Purpose:** Exact changes to make to voice/style files based on Hamoon email analysis  
**Target:** Implement 10-15% compression improvement

---

## File 1: `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md`

### CHANGES TO MAKE:

#### 1. Update Compression Target

**Current:**
```markdown
## Core Principle: Professional, Structured, Concise

**Target Compression: Moderate (20-30% reduction from baseline)**
- Baseline (uncompressed): ~650 words
- Target output: 400-550 words
```

**Change To:**
```markdown
## Core Principle: Professional, Structured, Concise

**Target Compression: Moderate-Aggressive (30-35% reduction from baseline)**
- Baseline (uncompressed): ~650 words
- Target output: 420-480 words (narrowed from 400-550)
- Rationale: Assume 10-15% additional tightening of V's natural style
```

---

#### 2. Update Section Word Counts

**Current:**
```markdown
## Target Word Counts by Section

- Opening paragraph: 40-60 words
- Use case description: 100-120 words each
- Integration options: 60-80 words
- Next steps: 60-80 words
- Closing: 20-30 words
```

**Change To:**
```markdown
## Target Word Counts by Section

- Opening paragraph: 40-50 words (tightened from 40-60)
- Use case description: 85-100 words each (tightened from 100-120)
- Integration options: 45-55 words (tightened from 60-80)
- Next steps: 50-60 words (tightened from 60-80)
- Closing: 12-18 words (tightened from 20-30)

**Total target: 420-480 words**
```

---

#### 3. Add Compression Techniques Section

**Add After "What to KEEP":**
```markdown
## Compression Techniques (Apply in Order)

### Level 1: Remove Filler (Baseline)
- Hedge phrases: "essentially", "basically", "in order to", "quite"
- Intensifiers: "really", "very", "absolutely", "genuinely"
- Redundant qualifiers: "direct", "actual", "specific"

### Level 2: Tighten Structure (10% additional)
- Articles where meaning is clear: "A 5-8 minute flow" → "5-8 minute flow"
- Possessives where implied: "FutureFit's platform" → "FutureFit"
- Context phrases: "As you described", "For my part" (only when non-essential)
- Wordy transitions: "which is why I'm grateful" → "grateful"

### Level 3: Consolidate Content (15% additional)
- Convert bullets to arrow flows for technical processes
- Combine related bullets: merge where logical
- Remove implied details: "basic candidate data" → "candidate data"
- Shorten headers: "Integration Options" → "Integration"
```

---

#### 4. Update "What to CUT" Section

**Current:**
```markdown
## What to CUT

- Hedge phrases: "essentially", "basically", "in order to"
- Redundant explanations
- Obvious statements
- Filler words: "would then", "directly", "actual"
```

**Change To:**
```markdown
## What to CUT

### Always Remove:
- Hedge phrases: "essentially", "basically", "in order to", "quite"
- Intensifiers: "really", "very", "absolutely" (keep "genuinely" sparingly)
- Filler words: "would then", "directly", "actual", "specific"
- Obvious statements and redundant explanations

### Remove When Implied:
- Articles: "A" or "The" before technical terms
- Possessives: "'s platform", "'s infrastructure"
- Qualifiers: "basic", "simple", "existing"
- Context phrases: "As you mentioned", "For my part"
- List descriptors: "(from one of your org partners)"

### Tighten Phrases:
- "what they're looking for" → "what they need" or "needs"
- "feel worth exploring" → "resonate"
- "I'm grateful for the chance to" → "grateful to"
- "Looking forward to hearing your take" → "Looking forward to your thoughts"
- "If it makes sense" → "If this resonates" or "If this feels right"
```

---

#### 5. Add Use Case Structure Guidelines

**Add New Section:**
```markdown
## Use Case Structure: Optimal Compression

### Standard Structure (90-100 words per use case):

**What it is:** [1 sentence, <20 words]
- Remove: articles ("A"), qualifiers ("sophisticated")
- Example: "5-8 minute conversational AI embedded in FutureFit that helps users articulate career story, values, and strengths."

**How it works:** [Bullets or arrow flow]
- Use bullets if 3+ distinct steps: maintain scannability
- Use arrow flow if linear process: saves words
- Remove: implied details ("basic", "structured", "our")
- Example bullets:
  - "FutureFit passes candidate data via API"
  - "User engages with conversational interface (iframe or widget)"
  - "We return 100+ data points (biographical, soft skills, values)"
  
**Why this matters:** [2-3 short sentences or bullets]
- Start with strong verb: "Bridges", "Solves", "Differentiates"
- Remove: "for [RecipientCompany]" header (implied)
- Remove: hedges like "can help" → state directly
- Example: "Bridges basic profiling to actionable insights for your 200K users without building in-house."

**Production-ready:** [List, <15 words]
- Remove: "What's" header
- Remove: descriptors like "structure", "system"
- Example: "Conversational engine, data extraction, API handoff (tested with one partner)"

**Requires work:** [1 sentence, <12 words]
- Remove: "What" header
- Remove: implied context ("on our side", "end-to-end")
- Example: "White-label UI (~2-3 weeks)"
```

---

## File 2: `N5/prefs/communication/voice.md`

### CHANGES TO MAKE:

#### 1. Update Lexicon - Add to "Avoid" List

**Current "Avoid" Section:**
```markdown
### Avoid
- Generic verbs: get, make, take, go, have, do
- Buzzwords: synergy, leverage, circle back, touch base
- Vague: soon, shortly, quickly
```

**Add To "Avoid" Section:**
```markdown
### Avoid
- Generic verbs: get, make, take, go, have, do
- Buzzwords: synergy, leverage, circle back, touch base
- Vague: soon, shortly, quickly

**Additional Patterns to Avoid:**
- "go after [problem]" → use "tackle [problem]" or "work on [problem]"
- "makes sense" → use "resonates" or "feels right"
- "grab a time" (in formal contexts) → use "book a time" or "find a slot"
- "no worries" (in formal contexts) → remove or use "no problem"
- "for my part" → remove when non-essential
```

---

#### 2. Add Compression Preference

**Add New Section After "Tone Weights":**
```markdown
## Compression Preference

**Target:** Assume 10-15% additional tightening of natural speaking style

**Principle:** V speaks conversationally in meetings but prefers written communication to be tighter. Remove:
- Spoken fillers that don't add meaning
- Intensifiers (really, very, absolutely) unless essential for emphasis
- Context reminders that are implied ("As you mentioned", "For my part")
- Redundant qualifiers (basic, simple, actual, direct)

**Balance:** Maintain warmth and personality while removing unnecessary words. Should still sound like V, just more concise.
```

---

#### 3. Update Opening/Closing Patterns

**Current:**
```markdown
## Greetings & Sign-offs by Relationship Depth

Depth 0-1 (Stranger/New Contact):
- Greeting: "Hi {{name}},"
- Closing: "Best regards," "Thank you,"

Depth 2-3 (Warm Contact/Partner):
- Greeting: "Hey {{name}},"
- Closing: "Best," "Thanks," "Warmly,"

Depth 4 (Inner Circle):
- Greeting: "Hey {{name}}—"
- Closing: "Cheers," "Talk soon,"
```

**Add Compression Variants:**
```markdown
## Greetings & Sign-offs by Relationship Depth

Depth 0-1 (Stranger/New Contact):
- Greeting: "Hi {{name}},"
- Closing: "Best regards," "Thank you," "Looking forward to your thoughts,"

Depth 2-3 (Warm Contact/Partner):
- Greeting: "Hey {{name}},"
- Closing: "Best," "Thanks," "Let me know what you think,"

Depth 4 (Inner Circle):
- Greeting: "Hey {{name}}—"
- Closing: "Cheers," "Talk soon,"

**Compression Variants (for all depths):**
- Avoid: "Looking forward to hearing your take" (wordy)
- Prefer: "Looking forward to your thoughts" (concise)
- Avoid: "I'd genuinely value any feedback" (wordy)
- Prefer: "I'd value feedback" (concise)
```

---

#### 4. Add CTA Patterns

**Add New Section:**
```markdown
## CTA Compression Patterns

### Standard CTA Structure
- 2-3 options maximum (not 4+)
- Combine related actions when possible
- Remove implied context

### Compression Examples:

**Wordy:**
> If one or both of these feel worth exploring:
> 1. I can send over a 1-page technical spec + mockup for the embedded experience

**Concise:**
> If one or both resonate:
> 1. I can send a 1-page spec + mockup

**Changes:**
- "feel worth exploring" → "resonate"
- Remove: "over" after "send"
- Remove: "technical" (implied by "spec")
- Remove: "for the embedded experience" (context clear)

---

**Wordy:**
> We could grab a time for a 30-min call to walk through a live demo

**Concise:**
> [Book a time] for a 30-min demo

**Changes:**
- "grab a time" → "Book a time" (more professional)
- Remove: "for a 30-min call to walk through a live"
- Keep: Inline link for smooth UX
```

---

## File 3: `N5/commands/follow-up-email-generator.md`

### CHANGES TO MAKE:

#### 1. Update Step 3 (Dial Inference) - Warmth Scoring

**Find Step 3:**
```markdown
### Step 3: Enhanced Dial Inference (Warmth/Familiarity)

Calculate warmthScore (0-10) from conversation signals:
- Personal anecdotes: +2
- Humor instances: +1.5 each (max +3)
- Compliments: +1 each (max +2)
- Shared values discussion: +1.5
- Emotional openness: +1
- **First meeting: cap warmthScore at 6.0**
```

**Change To:**
```markdown
### Step 3: Enhanced Dial Inference (Warmth/Familiarity)

Calculate warmthScore (0-10) from conversation signals:
- Personal anecdotes: +2
- Humor instances: +1.5 each (max +3)
- Compliments: +1 each (max +2)
- Shared values discussion: +2 (increased from +1.5)
- Emotional openness: +1
- **First meeting: cap warmthScore at 6.5** (increased from 6.0)
  - Rationale: Strong shared values + humor in first meeting signals higher warmth appropriateness

**Warmth Override Logic:**
If first meeting AND (shared values present OR 2+ humor instances):
- Allow warmth up to 6.5 (instead of 6.0)
- This reflects authentic connection despite new relationship
```

---

#### 2. Update Step 6B (Compression Pass)

**Find Step 6B:**
```markdown
### Step 6B: Compression Pass (MODERATE)

**Target: 20-30% reduction from baseline**

Apply compression rules from EMAIL_GENERATOR_STYLE_CONSTRAINTS.md:
- Remove hedge phrases
- Remove redundant explanations
- Keep section headers and bullet structure
- Maintain formal tone
```

**Change To:**
```markdown
### Step 6B: Compression Pass (MODERATE-AGGRESSIVE)

**Target: 30-35% reduction from baseline (10-15% tighter than V's natural style)**

Apply compression rules from EMAIL_GENERATOR_STYLE_CONSTRAINTS.md in 3 levels:

**Level 1 (Baseline - 20% reduction):**
- Remove hedge phrases and intensifiers
- Remove redundant explanations
- Remove filler words

**Level 2 (10% additional - total 30% reduction):**
- Remove articles where meaning is clear
- Remove possessives where implied
- Tighten wordy phrases to concise equivalents
- Fix lexicon (go after → tackle, makes sense → resonates)

**Level 3 (15% additional - total 35% reduction):**
- Convert bullets to arrow flows for linear processes
- Combine related bullets
- Remove implied details
- Shorten section headers

**Always Maintain:**
- Section headers for structure
- Professional tone
- Scannability (don't over-compress)
- Key technical details and numbers

**Default: Apply Level 2 (30% reduction)** unless specified otherwise
```

---

#### 3. Update Step 7 (Subject Line)

**Find Step 7:**
```markdown
### Step 7: Generate Subject Line

Format: "Follow-Up Email – {{FirstName}} x Careerspan [keyword1 • keyword2]"

Rules:
- Extract 2-3 keywords from CTAs or main topics
- Use bullet separator (•) between keywords
- Keep under 90 characters
```

**Add Compression Variant:**
```markdown
### Step 7: Generate Subject Line

**Standard Format:**
"Follow-Up Email – {{FirstName}} x Careerspan [keyword1 • keyword2]"

**Compressed Format (if warmth ≥ 6.0):**
"{{FirstName}} x Careerspan – [keyword1 • keyword2]"

Rules:
- Extract 2-3 keywords from CTAs or main topics
- Use bullet separator (•) between keywords
- Keep under 90 characters
- Remove "Follow-Up Email" for warmer relationships (more casual)
```

---

## Implementation Checklist

### Phase 1: Update Style Files (15 minutes)

- [ ] Update `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md`:
  - [ ] Change compression target: 20-30% → 30-35%
  - [ ] Narrow word count: 400-550 → 420-480
  - [ ] Update section targets (see above)
  - [ ] Add compression techniques section
  - [ ] Update "What to CUT" section
  - [ ] Add use case structure guidelines

### Phase 2: Update Voice File (10 minutes)

- [ ] Update `N5/prefs/communication/voice.md`:
  - [ ] Add to "Avoid" lexicon (go after, makes sense, grab a time, no worries)
  - [ ] Add compression preference section
  - [ ] Add compression variants for opening/closing
  - [ ] Add CTA compression patterns

### Phase 3: Update Command Logic (15 minutes)

- [ ] Update `N5/commands/follow-up-email-generator.md`:
  - [ ] Adjust warmth scoring (shared values: +1.5 → +2.0)
  - [ ] Adjust first-meeting cap (6.0 → 6.5)
  - [ ] Add warmth override logic
  - [ ] Update compression pass to Level 2 default
  - [ ] Add compressed subject line variant

### Phase 4: Test (30 minutes)

- [ ] Regenerate Hamoon email with new settings
- [ ] Compare to Version B (10% tighter sample)
- [ ] Verify word count: 420-480 words
- [ ] Verify section targets met
- [ ] Check lexicon adherence
- [ ] Review tone/warmth appropriateness

### Phase 5: Validate (1-2 days)

- [ ] Generate 3-5 test emails with different contexts
- [ ] Review with internal team
- [ ] Gather stakeholder feedback
- [ ] Document improvements
- [ ] Iterate if needed

---

## Expected Outcomes

### Quantitative Improvements:
- **Word count:** 485 → 435 words (-50 words, -10%)
- **Use case length:** 115 → 95 words (-20 words, -17%)
- **Opening length:** 58 → 49 words (-9 words, -16%)
- **CTA length:** 72 → 58 words (-14 words, -19%)

### Qualitative Improvements:
- ✅ More concise without losing professionalism
- ✅ Better lexicon consistency (tackle vs. go after)
- ✅ Tighter CTAs (resonate vs. feel worth exploring)
- ✅ More accurate warmth calibration
- ✅ Maintained scannability and structure

### Success Metrics:
- Response rate (baseline vs. improved)
- Time to response (faster suggests higher engagement)
- Meeting booking rate (for CTAs with Calendly links)
- Stakeholder feedback ("This sounds like me but tighter")

---

## Maintenance

### After Initial Tuning:

**Weekly:**
- Review 2-3 generated emails
- Check for lexicon drift
- Verify compression targets met

**Monthly:**
- Analyze response rates
- Gather stakeholder feedback
- Update voice files based on learnings
- Document patterns in successful emails

**Quarterly:**
- Full system review
- Update targets if needed
- Expand lexicon based on patterns
- Refine dial calibration algorithm

---

*Generated: 2025-10-12 18:22:00 ET*
