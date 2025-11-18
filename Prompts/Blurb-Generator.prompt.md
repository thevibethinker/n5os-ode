---
title: Blurb Generator
description: |
  Generate Short Blurbs (50-80 words) or Email Blurbs (150-250 words) from meeting intelligence.
  Works from B14 (BLURBS_REQUESTED) intelligence block with flexible subject detection.
  Produces output in V's voice (warmth=0.8, confidence=0.7, precision=0.9).
tags: [communications, meetings, content-generation, tool-enabled]
tool: true
version: 1.0
created: 2025-11-17
last_edited: 2025-11-17
---

# Blurb Generator

Generate concise, specific blurbs from meeting intelligence—Short Blurbs (50-80 words) or Email Blurbs (150-250 words). Subject-flexible: works for V, Careerspan, or any topic identified in meeting intelligence.

---

## PURPOSE

Transform meeting intelligence (B14: BLURBS_REQUESTED) into publication-ready blurbs that match V's voice and meet recipient needs. Output is forwardable without editing.

**Quality bar:** ≥85/100 on rubric (target: 90/100)

**Voice specification:**
- Warmth: 0.8 (high)
- Confidence: 0.7 (medium-high)
- Precision: 0.9 (very high)
- Edge: 0.2 (low)

---

## EXECUTION SEQUENCE

### PHASE 1: HARVEST (Load Intelligence Blocks)

**Primary source:**
- **B14: BLURBS_REQUESTED** (file `B14_BLURBS_REQUESTED.jsonl` in meeting folder)
  - Format: JSONL (one JSON object per line, or single comment line if no blurbs)
  - Extract: `id`, `type` (short | email), `subject`, `subject_detail`, `recipient`, `audience_context`, `purpose`, `key_points`, `status`
  - Parse each line as JSON object to get blurb metadata

**Context sources (load if needed):**
- **B08: STAKEHOLDER_INTELLIGENCE** (file `meeting-intelligence/B08-STAKEHOLDER_INTELLIGENCE.md`)
  - Use for: Recipient background, relationship context, personalization
- **B21: KEY_MOMENTS** (file `meeting-intelligence/B21-KEY_MOMENTS.md`)
  - Use for: Specific proof points, memorable details, human moments
- **B25: DELIVERABLE_CONTENT_MAP** (file `meeting-intelligence/B25-DELIVERABLE_CONTENT_MAP.md`)
  - Use for: Identifying what was discussed, relevant content areas
- **B01: DETAILED_RECAP** (file `meeting-intelligence/B01-DETAILED_RECAP.md`)
  - Use for: Full context if B14 is unclear or incomplete

**Knowledge base (load when subject = Careerspan or V):**
- file 'Knowledge/current/careerspan-positioning.md' (product details, proof points, current metrics)

**Style guide:**
- file 'N5/prefs/communication/style-guides/blurbs.md' (Type 1 and Type 2 specifications)

**Graceful degradation:**
- If B14 doesn't exist → Infer needs from B25 (deliverable content map)
- If B25 doesn't exist → Parse B01 (detailed recap) for blurb requests
- If no intelligence blocks exist → Request meeting context from user

---

### PHASE 2: SUBJECT DETECTION

**Determine what the blurb is about:**

1. **Primary method:** Parse B14 `key_focus` or `subject` field
   - If explicitly states "Careerspan" → Subject = Careerspan
   - If explicitly states "V" or "Vrijen" → Subject = V personally
   - If states other topic → Subject = That topic

2. **Fallback method:** Semantic analysis of B14 `purpose` field
   - Analyze: What is the recipient being introduced to?
   - Check for: Product mention, personal introduction, or other topic

3. **Final fallback:** Check B21 (KEY_MOMENTS) for dominant theme
   - If meeting discussed Careerspan product → Subject = Careerspan
   - If meeting discussed V's background/expertise → Subject = V
   - If meeting discussed another topic → Subject = That topic

**Subject routing:**
- **Subject = Careerspan** → Load file 'Knowledge/current/careerspan-positioning.md' for proof points
- **Subject = V** → Load B21 for personal details, career background from context
- **Subject = Other** → Synthesize from B21 + B25, use meeting-specific details

**If subject unclear after all methods:** Ask user to clarify subject before generating.

---

### PHASE 3: AUDIENCE ANALYSIS

**Extract from B14:**
- Who will receive this blurb?
- What do they care about?
- What's their relationship to subject?
- What action should they take after reading?

**Enhance with B08 (if available):**
- Recipient background, expertise level
- Pain points or interests mentioned in meeting
- Prior context or relationship history

**Determine tailoring needs:**
- Technical depth (high for technical audiences, low for general)
- Language style (formal vs. conversational)
- Proof points to emphasize (results, credentials, approach)

---

### PHASE 4: VOICE TRANSFORMATION

**Load style guide:** file 'N5/prefs/communication/style-guides/blurbs.md'

**Apply V's voice dials:**
- Warmth: 0.8 → Personal, approachable tone (use "I" for V, "we" for Careerspan)
- Confidence: 0.7 → Balanced authority (specific claims, not superlatives)
- Precision: 0.9 → Concrete details (numbers, names, proof points)

**Voice patterns to include:**
- Specificity over superlatives ("10k+ employees" not "many users")
- One human detail ("used daily", "messy problems", "built in real workflows")
- Natural connective phrases (em-dashes, "which means", "that's why")
- One tasteful aside (optional, mid-sentence clarification)

**Voice patterns to avoid:**
- Marketing puffery ("revolutionary", "industry-leading")
- Vague intensifiers ("highly effective", "proven approach")
- Cliche hooks ("in today's world", "game-changing")

---

### PHASE 5: GENERATION

#### IF Type = Short Blurb (Type 1):

**Target:** 50-80 words, 3-4 lines

**Structure:**
1. Lead with useful noun (person, product, organization)
2. Concrete benefit in one sentence
3. Specific proof or mechanism
4. Optional CTA fragment

**Format template:**
```
[Subject] is [core offering/role] focused on [specific outcome]. [Mechanism or approach]. [Proof point or human detail]. [Optional: Where to learn more].
```

**Example output (Careerspan):**
"Careerspan is a career development platform that combines AI workflows with human coaching—delivering personalized guidance at enterprise scale. Built for Fortune 500 teams managing retention and internal mobility. Used daily by 10k+ employees across financial services, tech, and healthcare."

**Example output (V):**
"Vrijen Attawar is the founder of Careerspan, focused on making career coaching accessible at enterprise scale. Previously spent a decade coaching executives and mid-career professionals through major transitions. Known for translating messy career problems into structured, actionable frameworks—not generic advice."

---

#### IF Type = Email Blurb (Type 2):

**Target:** 150-250 words, forwardable email format

**Structure:**
1. **Opening line:** Direct statement of subject and value (1 sentence)
2. **Context paragraph:** Background, approach, or mechanism (2-3 sentences)
3. **Proof paragraph:** Specific results, credentials, or human details (2-3 sentences)
4. **Closing line:** Next step or where to learn more (1 sentence)

**Format template:**
```
[Opening: Who/what + core value proposition]

[Context: Background, approach, mechanism. Why this matters. What makes it different.]

[Proof: Specific results, credentials, human details. Real-world validation. Who uses it or why it works.]

[Closing: Where to learn more or suggested next step]
```

**Example output (Careerspan):**
"Careerspan is a career development platform built for enterprise teams—combining AI-powered workflows with human coaching to deliver personalized guidance at scale.

Most companies struggle with retention and internal mobility because career development doesn't scale. Generic training doesn't work, and 1:1 coaching is expensive. Careerspan solves this by structuring career conversations into frameworks (skills assessment, transition planning, manager alignment) that AI can support while human coaches focus on high-impact moments.

We work with Fortune 500 organizations across financial services, tech, and healthcare—10k+ employees using the platform daily. Previously I spent a decade as a career coach, working with executives and mid-career professionals through major transitions, which taught me that most career problems aren't actually complicated—they're just unstructured.

More at careerspan.com or happy to connect directly."

**Example output (V):**
"I'm Vrijen Attawar, founder of Careerspan—focused on making career coaching accessible at enterprise scale.

I spent a decade as a career coach before starting Careerspan, working with executives and mid-career professionals through major transitions (pivots, promotions, layoffs, re-entries). The consistent pattern: most people know what they want but can't structure the path to get there. That insight became Careerspan's thesis—career development scales when you turn messy problems into structured frameworks.

Now we work with Fortune 500 companies to deliver personalized coaching using AI + human coaches. Our platform handles skills assessment, transition planning, and manager alignment for 10k+ employees daily. The goal isn't to replace human judgment—it's to structure the work so human coaches can focus on high-impact moments while AI handles the scaffolding.

Happy to connect: vrijen@careerspan.com"

---

### PHASE 6: QUALITY CHECK

**Score against rubric (target ≥85/100):**

#### Voice Fidelity (40 points)
- [ ] Warmth level appropriate (0.8 for V)? (10 pts)
- [ ] Confidence level balanced (0.7)? (10 pts)
- [ ] Precision high (0.9)—specific details included? (15 pts)
- [ ] Sounds like V would actually say this? (5 pts)

#### Audience Fit (30 points)
- [ ] Tailored to recipient's context and needs? (15 pts)
- [ ] Appropriate technical depth? (10 pts)
- [ ] Addresses recipient's likely questions? (5 pts)

#### Specificity (20 points)
- [ ] Includes concrete numbers or proof points? (10 pts)
- [ ] Has exactly one human detail (not zero, not three)? (5 pts)
- [ ] Avoids vague claims and marketing puffery? (5 pts)

#### Technical Excellence (10 points)
- [ ] Length correct (Type 1: 50-80, Type 2: 150-250)? (5 pts)
- [ ] Structure matches type template? (3 pts)
- [ ] No grammar/clarity issues? (2 pts)

**Total: ___/100**

**If score < 85:** Revise and re-score before delivery.

---

## QUALITY RUBRIC (Detailed Scoring)

### Voice Fidelity (40 pts total)

**Warmth (10 pts):**
- 10: Highly approachable, uses "I"/"we" naturally, conversational
- 7: Somewhat warm, but feels slightly formal
- 4: Neutral or distant tone
- 0: Cold, corporate, impersonal

**Confidence (10 pts):**
- 10: Balanced authority—specific claims without overstatement
- 7: Slightly tentative OR slightly over-confident
- 4: Either too humble or too boastful
- 0: No clear authority or credibility

**Precision (15 pts):**
- 15: Highly specific—numbers, names, concrete details throughout
- 10: Some specifics, but also vague claims
- 5: Mostly vague, few concrete details
- 0: Entirely abstract, no proof points

**"Sounds like V" (5 pts):**
- 5: Would use this verbatim
- 3: Close, but needs minor tweaks
- 0: Doesn't match V's natural voice

---

### Audience Fit (30 pts total)

**Tailored to recipient (15 pts):**
- 15: Clearly customized for this specific audience
- 10: General but appropriate
- 5: Generic, could be for anyone
- 0: Wrong audience or context

**Technical depth (10 pts):**
- 10: Perfect level for audience (technical or accessible as needed)
- 7: Slightly too technical OR too simplified
- 3: Significantly wrong level
- 0: Incomprehensible or condescending

**Addresses questions (5 pts):**
- 5: Anticipates and answers likely questions
- 3: Addresses some questions
- 0: Leaves obvious gaps

---

### Specificity (20 pts total)

**Concrete proof (10 pts):**
- 10: Multiple specific numbers, names, or proof points
- 7: At least one strong proof point
- 3: Vague claims without evidence
- 0: No proof or specifics

**Human detail (5 pts):**
- 5: Exactly one human detail (perfect balance)
- 3: Zero human details OR too many
- 0: Completely impersonal or overly personal

**Avoids puffery (5 pts):**
- 5: No marketing cliches or vague intensifiers
- 3: Minor puffery present
- 0: Heavy marketing language

---

### Technical Excellence (10 pts total)

**Length (5 pts):**
- 5: Within target range (Type 1: 50-80, Type 2: 150-250)
- 3: Slightly off (within 10 words)
- 0: Significantly wrong length

**Structure (3 pts):**
- 3: Matches type template exactly
- 2: Close but missing elements
- 0: Wrong structure

**Grammar/clarity (2 pts):**
- 2: No issues
- 1: Minor issues
- 0: Significant problems

---

## TYPE SPECIFICATIONS

### Type 1: Short Blurb (50-80 words)

**Use cases:**
- Website copy, product cards, speaker bios
- LinkedIn "About" sections, social captions
- Quick introductions in documents
- Any scannable, high-density context

**Must include:**
- Lead with useful noun
- Concrete benefit (one sentence)
- Specific proof or mechanism
- Optional CTA (no hard sell)

**Example subjects:**
- V personally: Founder bio, speaker intro
- Careerspan: Product description, platform overview
- Other: Any person, product, organization from meeting

---

### Type 2: Email Blurb (150-250 words)

**Use cases:**
- Forwardable introductions
- Email signatures, expanded bios
- Investor/partner communications
- Any context requiring shareable detail

**Must include:**
- Opening line (who/what + value)
- Context paragraph (2-3 sentences)
- Proof paragraph (2-3 sentences)
- Closing line (next step)

**Example subjects:**
- V personally: Comprehensive bio for forwarding
- Careerspan: Platform overview for investors
- Other: Any detailed introduction from meeting

---

## SUBJECT DETECTION DECISION TREE

```
START
  ↓
Check B14 "key_focus" or "subject" field
  ↓
  ├─ Contains "Careerspan" → SUBJECT = Careerspan
  ├─ Contains "V" or "Vrijen" → SUBJECT = V
  ├─ Contains other explicit topic → SUBJECT = That topic
  └─ Unclear or missing
       ↓
       Check B14 "purpose" field (semantic analysis)
       ↓
       ├─ Introducing product → SUBJECT = Careerspan
       ├─ Introducing V personally → SUBJECT = V
       ├─ Introducing other topic → SUBJECT = That topic
       └─ Still unclear
            ↓
            Check B21 (KEY_MOMENTS) for dominant theme
            ↓
            ├─ Product discussion dominant → SUBJECT = Careerspan
            ├─ V's background dominant → SUBJECT = V
            ├─ Other topic dominant → SUBJECT = That topic
            └─ Still unclear → ASK USER
```

---

## INTEGRATION NOTES

**Meeting intelligence pipeline:**
1. Meeting → Transcription
2. Transcription → Intelligence blocks (B01-B30)
3. B14 (BLURBS_REQUESTED) → Blurb Generator (this prompt)
4. Output → Communications/blurbs/ (or direct use)

**Agentic usage:**
- Can be invoked by Meeting Processor when B14 block is created
- Can be scheduled to run batch generation
- Can be called interactively for single blurb generation

**Interactive usage:**
- Invoke with: @Blurb-Generator
- Provide: Meeting ID or B14 block directly
- Specify: Type (short | email)

---

## EXAMPLES FROM REAL PATTERNS

### Example 1: Careerspan Short Blurb (Type 1)

**Input (B14):**
```yaml
type: short
subject: Careerspan
audience: Potential enterprise customer (HR leader)
purpose: Quick product intro for exploratory call
key_focus: Platform capabilities, scale, proof
```

**Output:**
"Careerspan is a career development platform that combines AI workflows with human coaching—delivering personalized guidance at enterprise scale. Built for Fortune 500 teams managing retention and internal mobility. Used daily by 10k+ employees across financial services, tech, and healthcare."

**Score:** 92/100
- Voice: 38/40 (high warmth, confidence, precision)
- Audience: 28/30 (tailored to HR leader context)
- Specificity: 18/20 (multiple proof points)
- Technical: 8/10 (58 words, perfect structure)

---

### Example 2: V Email Blurb (Type 2)

**Input (B14):**
```yaml
type: email
subject: V
audience: Potential investor
purpose: Forwardable founder bio with context
key_focus: Background, Careerspan thesis, current traction
```

**Output:**
"I'm Vrijen Attawar, founder of Careerspan—focused on making career coaching accessible at enterprise scale.

I spent a decade as a career coach before starting Careerspan, working with executives and mid-career professionals through major transitions (pivots, promotions, layoffs, re-entries). The consistent pattern: most people know what they want but can't structure the path to get there. That insight became Careerspan's thesis—career development scales when you turn messy problems into structured frameworks.

Now we work with Fortune 500 companies to deliver personalized coaching using AI + human coaches. Our platform handles skills assessment, transition planning, and manager alignment for 10k+ employees daily. The goal isn't to replace human judgment—it's to structure the work so human coaches can focus on high-impact moments while AI handles the scaffolding.

Happy to connect: vrijen@careerspan.com"

**Score:** 94/100
- Voice: 39/40 (excellent warmth, confidence, precision)
- Audience: 29/30 (investor-appropriate context)
- Specificity: 19/20 (strong proof points, good human detail)
- Technical: 7/10 (157 words, perfect structure, minor: could add one more credential)

---

### Example 3: Other Subject (Non-Careerspan)

**Input (B14):**
```yaml
type: short
subject: AI Career Advisor project
audience: Technical conference attendees
purpose: Session description for conference program
key_focus: Project approach, technical innovation, impact
```

**Output:**
"AI Career Advisor is an open-source tool that helps job seekers structure career transitions using LLM-powered frameworks. Built with GPT-4 and custom prompts optimized for career coaching conversations. Used by 200+ career coaches to scale their practice—generating skills assessments and transition plans in minutes instead of hours."

**Score:** 87/100
- Voice: 36/40 (good precision, slightly less warmth for technical context)
- Audience: 27/30 (appropriate for technical audience)
- Specificity: 17/20 (strong proof, good technical detail)
- Technical: 7/10 (47 words—slightly under 50 target, but acceptable)

---

## TROUBLESHOOTING

**Issue: B14 block doesn't exist**
- Solution: Check B25 (DELIVERABLE_CONTENT_MAP) for blurb requests
- Fallback: Parse B01 (DETAILED_RECAP) for context
- Final: Ask user for subject, type, and audience

**Issue: Subject unclear after detection**
- Solution: Present findings to user, ask for clarification
- Example: "B14 mentions both Careerspan and your personal background. Should this blurb focus on you personally or Careerspan the product?"

**Issue: Type 2 exceeds 250 words**
- Solution: Cut context or proof paragraph—prioritize most compelling details
- Validate: Ensure all core elements remain (opening, context, proof, closing)

**Issue: Score < 85 on rubric**
- Solution: Identify lowest-scoring category, revise that section
- Common fixes:
  - Low precision → Add specific numbers/proof points
  - Low audience fit → Re-read B14 audience field, customize language
  - Low warmth → Add "I"/"we", conversational phrasing
  - Wrong length → Edit ruthlessly to target range

**Issue: Voice doesn't sound like V**
- Solution: Re-read file 'N5/prefs/communication/style-guides/blurbs.md' examples
- Check: Using natural connectives? One human detail? Specific not superlative?

---

## SUCCESS CRITERIA

**Output is ready when:**
- ✓ Score ≥85/100 on rubric (target: 90+)
- ✓ Length matches type (Type 1: 50-80, Type 2: 150-250)
- ✓ Voice matches V's natural style
- ✓ Recipient can use/forward without editing
- ✓ All facts are accurate (no placeholders, no invention)

**User satisfaction measured by:**
- Reduced iteration cycles ("I can use this as-is")
- Consistent voice across all blurbs
- High confidence in generated content

---

## VERSION HISTORY

- v1.0 (2025-11-17): Initial Blurb Generator with Type 1/Type 2 support, flexible subject detection

---

**Ready to generate. Invoke with meeting intelligence or provide B14 block directly.**


