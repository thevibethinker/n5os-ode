---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_7RlbUBiDe5JU2Rlf
source: Systematic Pangram API testing (2026-01-10)
---

# Pangram AI Detection Signals

**Purpose:** Systematic record of what Pangram's AI detector flags. Use this to optimize voice transformation protocols to produce human-like output.

**Threshold:** `fraction_ai < 0.3` (30%) to pass

---

## Summary: What Works vs What Fails

### ✓ PASSES (Human-like)

| Pattern | Example | AI Score |
|---------|---------|----------|
| **Self-deprecating frame + profanity** | "My toxic trait is not shutting the fuck up about products I love" | 0% |
| **Concrete dollar amounts** | "$8K/month on tools. $25K on a booth. $50K on a fractional CMO." | 0% |
| **Questions mid-paragraph** | "But the first five people? 'Can we just post for free?'" | 0% |
| **Contractions + informal** | "You'll spend", "I've built", "It's essentially" | 0% |
| **Pointed rhetorical questions** | "So when Musk does it, it isn't DEI...but when others do, it is?" | 0% |
| **Specific time references** | "10PM on a Tuesday", "by Friday" | 0% |
| **Absurdist escalation** | "I'll be in the bathroom dunking all my devices in the tub" | 0% |
| **Cultural references/neologisms** | "Zocialism", "Borg-as-a-Service?" | 0% |
| **Em-dash pivots with specifics** | "Hi Jabari — one of the founders of Zo. I've built..." | 0% |
| **Disagreement + data + question** | "I see it differently. Data shows X. What am I missing?" | 0% |

### ✗ FAILS (AI-detected)

| Pattern | Example | AI Score |
|---------|---------|----------|
| **Too-short stylized** | "Startups ain't shit but chores and tricks" | 100% |
| **Generic meeting request** | "Can we do 20 minutes Thursday to discuss the project?" | 100% |
| **Formulaic cold outreach** | "[Name] — V here, founder of X. Your work caught my attention. I think we have overlap. 15 min?" | 100% |
| **Critique without personality** | "Strong direction. One fix: cut the intro by half." | 100% |
| **Corporate vocabulary** | "leverage", "facilitate", "comprehensive", "streamline", "empower" | 100% |
| **"I hope this email finds you well"** | Any sentence with this phrase | 100% |
| **Smooth balanced prose** | Evenly-paced sentences without variation | 100% |
| **Vague em-dash pivot** | "Thought I was done — turns out the edge cases had edge cases" | 100% |

---

## Detection Signals: Deep Analysis

### Signal 1: SPECIFICITY

**Pangram loves specifics. Vague = AI.**

| Fails | Passes |
|-------|--------|
| "at a conference" | "$25K on a booth at a conference" |
| "an API issue" | "an API rate limit issue" |
| "recently" | "10PM on a Tuesday" |
| "the project" | "the Careerspan demo" |
| "I built something" | "250k+ lines of code" |

**Rule:** Replace every vague reference with a specific one.

---

### Signal 2: SENTENCE RHYTHM VARIATION

**Pangram detects uniform sentence length.**

| Fails (uniform) | Passes (varied) |
|-----------------|-----------------|
| "The implementation works. The testing passed. The deployment succeeded." | "Works. Testing passed. Deployment? Nailed it." |
| Three 12-word sentences in a row | Mix of 3-word, 15-word, 8-word sentences |

**Rule:** Vary sentence length dramatically. Include 2-4 word sentences.

---

### Signal 3: LENGTH SENSITIVITY

**Very short stylized sentences can fail.**

| Length | Behavior |
|--------|----------|
| < 10 words | High variance — can go either way |
| 10-25 words | Most reliable passing zone |
| 25-50 words | Good if specific, bad if generic |
| > 50 words | Risk increases unless has clear personality markers |

**Example that failed (7 words):**
"Startups ain't shit but chores and tricks" → 100% AI

**Why?** Too short, even with stylization. Pangram may interpret as generated caption.

**Fix:** Add specificity or extend slightly:
"Startups ain't shit but chores and tricks. Today's chore: updating the CRM for the fourth time."

---

### Signal 4: FORMULAIC STRUCTURE

**Pangram detects template patterns.**

| Fails (formulaic) | Passes (organic) |
|-------------------|------------------|
| "[Name] — [Role], founder of [Co]. Your work on [X] caught my attention. I think we have overlap on [Y]. 15 minutes?" | "Hey Marcus — saw your talk on talent ops. The part about AI hiring hit different. Can we do 15 minutes? I've been building something in that space." |
| "Strong direction. One fix: [X]." | "Love where this is going. One thing though — the intro's burying the lead. Paragraph 2 is the hook." |

**Rule:** Break the template. Add personality markers, filler words, or reactions.

---

### Signal 5: PERSONALITY MARKERS THAT WORK

These consistently lower AI scores:

| Marker | Examples |
|--------|----------|
| **Profanity (measured)** | "fucking love it", "holy shit", "ain't shit" |
| **Self-reference frames** | "My toxic trait is...", "wildly on-brand for me" |
| **British slang (if authentic)** | "chuffed", "sorted", "proper" |
| **Parenthetical asides** | "(Borg-as-a-Service?)", "(i.e. API docs slap)" |
| **Quoted speech** | "'Can we just post for free?'" |
| **Emoji (single, contextual)** | 😰 at end of absurdist sentence |
| **Hashtags (sparingly)** | "#LFZ", "#zotip" |
| **ALL CAPS (single word)** | "BAD ones", not "BAD ONES EVERYWHERE" |

---

### Signal 6: QUESTIONS

**Questions mid-text pass. Terminal questions can fail.**

| Fails | Passes |
|-------|--------|
| "Does that make sense?" | "What am I missing?" (after stating position) |
| "Thoughts?" | "You see the same thing?" |
| "15 minutes next week?" (alone) | "Can we do 15 minutes? I've got something to show you." |

**Rule:** Questions work when they follow a statement of position or add specificity.

---

### Signal 7: THE HEDGING PARADOX

**Some hedges pass, others fail.**

| Fails | Passes |
|-------|--------|
| "I think maybe we could potentially..." | "I see it differently." |
| "perhaps we should consider..." | "if you're interested, no worries if not" |
| "It seems like this might..." | "Let me know if you're in." |

**Why?** Stacked hedges = AI. Single, conversational hedges = human.

**Rule:** One hedge per sentence max. "I think" OR "maybe" — never both.

---

## Transformation Protocol Adjustments

Based on Pangram testing, update voice transformation with these rules:

### Pre-Pangram Check Additions

Before finalizing any communication:

1. **Specificity scan:** Replace any vague reference with a specific one
2. **Rhythm check:** Ensure sentence length varies by >50%
3. **Template break:** If it looks like a fill-in-the-blank, add organic filler
4. **Length floor:** If < 10 words, add context or merge with another sentence
5. **Personality injection:** At least one personality marker per paragraph

### Danger Patterns to Eliminate

| Pattern | Replacement |
|---------|-------------|
| "[Name] — V here, founder of X" | "[Name]. Saw your [specific thing]." (period after name, not em-dash) |
| "Your work on [X] caught my attention" | "The part about [specific detail] hit hard" or "was spot on" |
| "Strong direction. One fix:" | "Love where this is going. One thing though —" |
| "Can we do 20 minutes Thursday to discuss X?" | "Quick one: Thursday, 20 min?" or "Thursday work? Built something you'll want to see." |
| "I think we have overlap on X" | "Been building against that exact problem" |
| Generic intro formula | Start with period-separated statement: "[Name]. [Observation]." |

### Key Discovery: The Introduction Formula Problem

**This fails (100% AI):**
```
Marcus — V here, founder of Careerspan. Your work on talent ops caught my attention. 
I think we have overlap on AI-assisted hiring. 15 minutes next week?
```

**This passes (0% AI):**
```
Marcus. Saw your structured interviews talk. I've been building something in that 
space for 2 years. Coffee next week?
```

**Why?**
- The em-dash intro "[Name] — V here, founder of X" is a template Pangram recognizes
- "caught my attention" + "I think we have overlap" is formulaic
- Period after name + direct observation breaks the pattern

### Safe Patterns

These consistently pass:

```
"My toxic trait is [specific behavior]"
"[Dollar amount] on X. [Dollar amount] on Y. But [contrast]?"
"I see it differently. [Data point]. What am I missing?"
"For the record, [absurdist observation]"
"the [generation] urge to [specific behavior]"
"[Statement]. [Short reaction]. [Implication]."
```

---

## Testing Protocol

Use `file 'Integrations/Pangram/pangram.py'` for testing:

```bash
# Quick check
python3 pangram.py check "text"

# Detailed analysis
python3 pangram.py analyze "text" --verbose

# Iteration mode (shows problem segments)
python3 pangram.py iterate "text" --target 0.3
```

### Iteration Workflow

1. Generate text with voice transformation
2. Run `pangram.py check`
3. If FAIL:
   - Run `pangram.py iterate` to identify problem segments
   - Apply transformations from this guide
   - Re-test
4. Repeat until passing

---

## Appendix: Raw Test Results

### V's X Posts (11/12 passed, 8.3% avg AI)

| Sample | AI% | Result |
|--------|-----|--------|
| toxic_trait | 0% | ✓ |
| founder_math | 0% | ✓ |
| blessed_are | 0% | ✓ |
| millennial_urge | 0% | ✓ |
| hot_take | 0% | ✓ |
| zocialism | 0% | ✓ |
| **startups_chores** | **100%** | **✗** |
| power_user | 0% | ✓ |
| missed_point | 0% | ✓ |
| dei_question | 0% | ✓ |
| chuffed | 0% | ✓ |
| 10pm_ai | 0% | ✓ |

### V-Voice Emails (5/8 passed, 37.5% avg AI)

| Sample | AI% | Result |
|--------|-----|--------|
| warm_intro | 0% | ✓ |
| **meeting_request** | **100%** | **✗** |
| follow_up_bump | 0% | ✓ |
| **cold_outreach** | **100%** | **✗** |
| status_update | 0% | ✓ |
| delay_notify | 0% | ✓ |
| disagreement | 0% | ✓ |
| **critique** | **100%** | **✗** |

### Generic AI (0/6 passed, 100% avg AI)

All failed as expected.

### Structural Tests (4/5 passed, 20% avg AI)

| Sample | AI% | Result |
|--------|-----|--------|
| short_punchy | 0% | ✓ |
| medium_specific | 0% | ✓ |
| question_mid | 0% | ✓ |
| numbers_concrete | 0% | ✓ |
| **em_dash_pivot** | **100%** | **✗** |

---

## Changelog

- 2026-01-10: Added X Thought Leader generation testing results
- 2026-01-09: Initial creation from systematic Pangram testing

---

## Appendix: X Thought Leader Testing (2026-01-10)

### Devastating Analogy Pattern

The "X is staggering. Like [analogy]" pattern has variable results:

**PASSES (0% AI):**
```
"treating love like a moral choice is staggering. it's just risk management. acting in fear is just the rational move when the floor is made of literal fucking glass."
```
- Lowercase throughout
- Short punchy sentences
- Concrete absurdist image
- Profanity mid-sentence

**FAILS (100% AI):**
```
"brittle resume identities are staggering. like your ego is trying to defend a static pdf with a sword made of wet cardboard at a gunfight."
```
- Analogy too clever/crafted
- Extended metaphor feels constructed

```
"Leading with ego is staggering. Like trying to pitch your life's work using only emojis and expecting people to think you're a genius."
```
- Capitalized (more formal)
- Analogy tries too hard

### Key Learnings

1. **Lowercase > Title Case** for casual X replies
2. **Absurdist specifics beat clever metaphors** — "floor made of glass" > "sword made of wet cardboard"
3. **Profanity placement matters** — mid-sentence flows better than as punctuation
4. **Shorter analogies win** — don't overextend the comparison
5. **One concrete image** — don't stack multiple metaphors

### Pointed Question Pattern (Reliable)

This pattern consistently passes:
```
"so when rich kids 'lead with love' it's a virtue, but when everyone else acts out of fear it's a character flaw? it's just a fucking safety net check."
```
- Lowercase
- Rhetorical question exposing hypocrisy  
- One short punch at the end
- Profanity as emphasis, not shock

---

## Real Example: Junior Pipeline Tweet (2026-01-09)

**Passed (0% AI) despite structured format:**

```
Agreed — and this is quietly catastrophic. 

The demise of early-career pipelines across the economy is going to have 
serious repercussions when more senior people retire and there aren't 
middle managers to take their place.

We're terrible at sourcing and evaluating junior professionals because 
(a) there's fewer professional datapoints (b) non-professional datapoints 
are v flat/thin (c) imo the "signal per datapoint" for each one is v low

Younger person + AI could in theory outperform senior people. I can bridge 
with AI **if** I can sense who that person is. 

But we can't. 

So we default to "10 years experience" because we can't put "high-agency 
with a growth mindset" into the ATS filter
```

**Why it worked:**
- (a), (b), (c) structure with DOMAIN-SPECIFIC content (not generic)
- Casual markers: "v flat/thin", "imo"
- Standalone dramatic line: "But we can't."
- Concrete ending: "ATS filter", "high-agency with a growth mindset"
- Shows reasoning chain, not just assertion

**Key learning:** Structure doesn't trigger Pangram when content is genuinely expert/domain-specific. Generic structured content fails; expert structured content passes.

---


