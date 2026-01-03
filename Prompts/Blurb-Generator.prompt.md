---
title: Blurb Generator
description: |
  Generate Short Blurbs (50-80 words) or Email Blurbs (150-250 words) from meeting intelligence.
  Works from B14 (BLURBS_REQUESTED) intelligence block with flexible subject detection.
  Produces output in V's voice with selective generation gate and forwardable email wrapper.
tags: [communications, meetings, content-generation, tool-enabled, semantic-memory]
tool: true
version: 2.1
created: 2025-11-17
last_edited: 2026-01-03
mg_stage: MG-3
status: canonical
---

# Blurb Generator v2.1

Generate concise, specific blurbs from meeting intelligence—Short Blurbs (50-80 words) or Email Blurbs (150-250 words). Subject-flexible: works for V, Careerspan, or any topic identified in meeting intelligence.

**v2.1 Key Changes:**
- ⭐ PHASE 1.1: Anti-hallucination gate (CRITICAL - prevents fabricated claims)
- ⭐ PHASE 0: Selectivity gate (generate only when truly needed)
- ⭐ PHASE 1.5: Semantic memory enrichment
- ⭐ PHASE 5: Always generates forwardable email wrapper
- ⭐ Updated voice: More direct, stronger pressure, clearer CTAs

---

## PURPOSE

Transform meeting intelligence into publication-ready blurbs that match V's voice and meet recipient needs. Output includes both raw blurb AND forwardable email wrapper.

**Quality bar:** ≥85/100 on rubric (target: 90/100)

**Voice specification:**
- Warmth: 0.7 (medium-high) – approachable but professional
- Confidence: 0.8 (high) – assertive, clear authority
- Precision: 0.9 (very high) – specific details, concrete claims
- Directness: 0.8 (high) – get to the point, no hedging
- Pressure: 0.6 (medium-high) – clear CTAs, gentle urgency, socially acceptable push

---

## EXECUTION SEQUENCE

### PHASE 0: SELECTIVITY GATE ⭐ NEW in v2.0

**Purpose:** Only generate blurbs when truly needed. Avoid wasting tokens on meetings that don't require introductory content.

**Decision Tree:**
```
START
  ↓
Is this an INTERNAL-ONLY meeting?
  ├─ YES → SKIP (no blurb needed)
  └─ NO → Continue
       ↓
Does B14 (BLURBS_REQUESTED) exist with explicit requests?
  ├─ YES → PROCEED (explicit request)
  └─ NO → Continue
       ↓
Does B02 (COMMITMENTS) contain intro promises?
  (Look for: "introduce", "connect", "put you in touch", "share info")
  ├─ YES → PROCEED (implicit need)
  └─ NO → Continue
       ↓
Does B25 (DELIVERABLES) mention sharing blurb/bio/description?
  ├─ YES → PROCEED (implicit need)
  └─ NO → Continue
       ↓
Is stakeholder type FOUNDER, INVESTOR, or CUSTOMER?
  ├─ YES → PROCEED (high-value relationship)
  └─ NO → SKIP (networking/community rarely needs blurb)
```

**Skip notification:**
When skipping, log: `"Blurb generation skipped: [reason]"` in meeting manifest.

**Override:**
User can force generation by passing `force=true` or explicitly requesting.

---

### PHASE 1: HARVEST (Load Full Meeting Context) ⭐ ENHANCED in v2.0

**Purpose:** Load ALL relevant intelligence blocks for rich context, not just B14.

**REQUIRED blocks (must load):**
- **B01: DETAILED_RECAP** – Full meeting narrative, strategic context
- **B21: KEY_MOMENTS** – Memorable quotes, resonant details, human moments
- **B08: STAKEHOLDER_INTELLIGENCE** – Recipient profile, relationship context

**PRIMARY source:**
- **B14: BLURBS_REQUESTED** (file `B14_BLURBS_REQUESTED.jsonl` in meeting folder)
  - Format: JSONL (one JSON object per line, or single comment line if no blurbs)
  - Extract: `id`, `type` (short | email), `subject`, `subject_detail`, `recipient`, `audience_context`, `purpose`, `key_points`, `status`
  - Parse each line as JSON object to get blurb metadata

**SUPPORTING blocks (load for context):**
- **B02: COMMITMENTS** – Promises made, intro commitments
- **B25: DELIVERABLE_CONTENT_MAP** – What was promised, relevant content areas
- **B26: METADATA** – Meeting type, stakeholder classification

**Knowledge base (load when subject = Careerspan or V):**
- file 'Knowledge/current/careerspan-positioning.md' (product details, proof points, current metrics)
- **⚠️ CRITICAL:** This file is REQUIRED for Careerspan blurbs. See PHASE 1.1.

**Style guide:**
- file 'N5/prefs/communication/style-guides/blurbs.md' (Type 1 and Type 2 specifications)

**Graceful degradation:**
- If B14 doesn't exist → Infer needs from B02 + B25 (commitments + deliverables)
- If B01/B21 limited → Use B26 metadata + transcript summary
- If no intelligence blocks exist → Request meeting context from user
- **If positioning file missing/incomplete → See PHASE 1.1 (do NOT invent facts)**

**Build Meeting Context Map:**
```json
{
  "recipient": {
    "name": "[from B08 or B14]",
    "company": "[from B08]",
    "role": "[from B08]",
    "relationship_depth": "[from B08 CRM section]"
  },
  "meeting_highlights": {
    "key_quotes": ["[from B21]"],
    "resonant_moments": ["[from B21]"],
    "human_details": ["[from B01/B21]"]
  },
  "strategic_context": {
    "why_meeting_happened": "[from B01]",
    "outcomes": ["[from B01]"],
    "next_steps": ["[from B02]"]
  },
  "blurb_request": {
    "type": "[short | email]",
    "subject": "[Careerspan | V | Other]",
    "purpose": "[from B14]",
    "audience": "[from B14]"
  }
}
```

---

### PHASE 1.1: ANTI-HALLUCINATION GATE ⭐ NEW in v2.1

**Purpose:** Prevent fabrication of unverified claims. This is CRITICAL for maintaining trust.

**⚠️ FUNDAMENTAL RULE: NEVER INVENT FACTS**

```
ALLOWED sources for claims:
├── Knowledge/current/careerspan-positioning.md (REQUIRED for Careerspan blurbs)
├── Meeting transcript (verbatim quotes, discussed topics)
├── Intelligence blocks (B01, B21, B08, etc.)
└── CRM profile (verified relationship context)

FORBIDDEN:
├── Inventing metrics (user counts, revenue, percentages)
├── Fabricating customer names or industries
├── Making up timelines ("18+ months to build")
├── Creating proof points not in positioning file
└── Assuming facts not explicitly stated
```

**Positioning File Check:**

```
IF subject = Careerspan:
  ↓
  Load file 'Knowledge/current/careerspan-positioning.md'
  ↓
  Is file present AND populated (not just template)?
    ├─ YES → Extract verified claims, proceed to PHASE 1.5
    └─ NO → HALT and output:
            "⚠️ POSITIONING FILE MISSING OR INCOMPLETE
             Cannot generate Careerspan blurb without verified facts.
             Please populate: Knowledge/current/careerspan-positioning.md

             Proceeding with PLACEHOLDER MODE (all claims marked for verification)"
```

**PLACEHOLDER MODE (when positioning file incomplete):**

If positioning file is missing or has `[FILL IN]` placeholders:
1. Generate blurb structure using meeting context ONLY
2. Mark ALL unverified claims with `[VERIFY: claim]`
3. Use qualitative language instead of specific metrics
4. Add verification checklist to output

**Claim Classification:**

| Claim Type | Source Required | If Missing |
|------------|-----------------|------------|
| User/customer metrics | Positioning file | Use `[VERIFY: X users]` or omit |
| Industry/segment claims | Positioning file | Use "enterprise teams" (generic) |
| Timeline claims | Positioning file OR transcript | Use `[VERIFY: timeline]` or omit |
| Methodology description | Transcript OR positioning | OK if discussed in meeting |
| Competitive claims | Positioning file | Omit entirely |
| Contact info/links | Positioning file | Use `[VERIFY: URL]` |

**Anti-Hallucination Checklist (include in output):**

```markdown
## Fact Verification Status
| Claim | Source | Status |
|-------|--------|--------|
| [claim 1] | [positioning/transcript/etc] | ✓ Verified |
| [claim 2] | [source] | ⚠️ NEEDS VERIFICATION |
```

---

### PHASE 1.5: SEMANTIC MEMORY ENRICHMENT ⭐ NEW in v2.0

**Purpose:** Pull relevant context from past meetings, CRM profiles, and similar blurbs before generating.

**Memory Client:**
```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()
```

**Query Patterns:**

**1. Similar Past Blurbs (Style Reference):**
```python
similar_blurbs = client.search(
    query=f"blurb {subject} {recipient_type}",
    metadata_filters={"path": ("contains", "BLURB")},
    limit=3
)
```
- Past blurbs for same subject as style exemplars
- Match recipient type (founder, investor, customer)

**2. Recipient Relationship Context:**
```python
crm_context = client.search_profile(
    profile="crm",
    query=f"{recipient_name} {recipient_company}",
    limit=3
)
```
- Prior interactions, relationship depth
- Use to calibrate formality and pressure

**3. V's Positioning on Blurb Topic:**
```python
positions = client.search_profile(
    profile="positions",
    query=f"{blurb_subject} {key_topics}",
    limit=3
)
```
- Relevant strategic positions
- Use for Careerspan blurbs to ensure consistent messaging

**Build Semantic Context Map:**
```json
{
  "style_exemplars": [
    {"content": "[past blurb content]", "score": 92}
  ],
  "recipient_history": {
    "prior_meetings": 2,
    "last_interaction": "2025-11-10",
    "relationship_depth": "warm"
  },
  "positioning": [
    {"topic": "enterprise coaching", "key_message": "AI + human hybrid"}
  ]
}
```

**Usage in Generation:**
- Reference style exemplars for consistent voice
- Use relationship depth to calibrate pressure dial
- Incorporate positioning for subject consistency

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

### PHASE 4: VOICE TRANSFORMATION ⭐ ENHANCED in v2.0

**Load style guide:** file 'N5/prefs/communication/style-guides/blurbs.md'

**Apply V's voice dials (updated for directness + pressure):**
- **Warmth: 0.7** → Professional but approachable (use "I" for V, "we" for Careerspan)
- **Confidence: 0.8** → Assertive authority (specific claims, clear expertise)
- **Precision: 0.9** → Concrete details (numbers, names, proof points)
- **Directness: 0.8** → Get to the point, no hedging, clear value statement upfront
- **Pressure: 0.6** → Clear CTAs, gentle urgency, make the ask explicit

**Directness Calibration (NEW):**
| Context | Directness | Pressure | CTA Style |
|---------|------------|----------|-----------|
| Cold intro | 0.7 | 0.5 | "Would love to connect" |
| Warm intro | 0.8 | 0.6 | "Let's find 15 minutes" |
| Investor | 0.8 | 0.7 | "Happy to share more—what's your calendar like?" |
| Customer | 0.8 | 0.6 | "Would love to show you—can we schedule?" |
| Partnership | 0.9 | 0.7 | "I think there's real synergy here. Let's talk." |

**Voice patterns to include:**
- **Lead with value** – State benefit in first sentence, not background
- **Specificity over superlatives** – "10k+ employees" not "many users"
- **One human detail** – "used daily", "messy problems", "built in real workflows"
- **Clear CTA** – End with specific ask, not vague "let me know"
- **Natural connectives** – em-dashes, "which means", "that's why"
- **Confidence markers** – "I've found", "We've proven", "The data shows"

**Voice patterns to avoid:**
- ❌ Hedging language ("I think maybe", "if you're interested")
- ❌ Marketing puffery ("revolutionary", "industry-leading")
- ❌ Vague CTAs ("let me know", "reach out if interested")
- ❌ Over-qualification ("I don't want to take too much time")
- ❌ Cliche hooks ("in today's world", "game-changing")

**Pressure Techniques (Socially Acceptable):**
- Imply scarcity: "We're selective about partnerships"
- Create urgency: "Timing works well because..."
- Make ask specific: "Can we do 20 minutes next Tuesday?"
- Offer value exchange: "I'd love to share [X]—in exchange, I'd value your perspective on [Y]"
- Reference momentum: "Given our conversation, I'd suggest we..."

---

### PHASE 5: GENERATION ⭐ ENHANCED in v2.0

**CRITICAL:** Always generate BOTH raw blurb AND forwardable email wrapper.

---

#### PART A: Raw Blurb Generation

##### IF Type = Short Blurb (Type 1):

**Target:** 50-80 words, 3-4 lines

**Structure:**
1. Lead with value statement (what's in it for recipient)
2. Concrete benefit in one sentence
3. Specific proof or mechanism
4. Clear CTA fragment (not optional)

**Format template:**
```
[Subject] [value/benefit statement]. [Mechanism or approach]. [Proof point or human detail]. [Direct CTA: where to learn more or what to do next].
```

**Example output (Careerspan) – MORE DIRECT:**
"Careerspan delivers personalized career coaching at enterprise scale—combining AI workflows with human coaches. Built for Fortune 500 teams managing retention and internal mobility. 10k+ employees use it daily across financial services, tech, and healthcare. See it in action: careerspan.com/demo"

**Example output (V) – MORE DIRECT:**
"I'm Vrijen Attawar—I've spent a decade helping executives and mid-career professionals navigate major transitions. Now I run Careerspan, which brings that coaching to enterprise scale through AI + human hybrid. Known for turning messy career problems into actionable frameworks. Let's connect: vrijen@careerspan.com"

---

##### IF Type = Email Blurb (Type 2):

**Target:** 150-250 words, forwardable email format

**Structure:**
1. **Opening line:** Direct value statement (what you can do for them) – 1 sentence
2. **Context paragraph:** How it works, why it matters – 2-3 sentences
3. **Proof paragraph:** Specific results, credentials, human details – 2-3 sentences
4. **Closing line:** Clear, specific CTA – 1 sentence

**Format template:**
```
[Opening: Value proposition—what's in it for the recipient]

[Context: How it works. Why this approach. What makes it different.]

[Proof: Specific results, credentials, human details. Who uses it. Real-world validation.]

[Closing: Specific CTA—not "let me know" but "here's what to do next"]
```

**Example output (Careerspan) – MORE DIRECT + PRESSURE:**
"Careerspan helps enterprise teams solve their biggest career development challenge: making coaching scalable without losing quality.

We combine AI-powered workflows with human coaches—AI handles assessments, planning frameworks, and manager alignment, while humans focus on high-impact moments. The result: personalized guidance at scale, not generic training that gets ignored.

Fortune 500 organizations across financial services, tech, and healthcare use us—10k+ employees on the platform daily. I spent a decade as a career coach before building this, which taught me that most career problems aren't complicated—they're just unstructured. Careerspan fixes that.

Best way to see it: careerspan.com/demo or grab 20 minutes with me—vrijen@careerspan.com"

**Example output (V) – MORE DIRECT + PRESSURE:**
"I'm Vrijen Attawar, founder of Careerspan. I help companies make career coaching accessible at enterprise scale.

Before Careerspan, I spent a decade coaching executives and mid-career professionals through major transitions—pivots, promotions, layoffs, re-entries. The pattern was consistent: people know what they want but can't structure the path. That insight became Careerspan's thesis—career development scales when you turn messy problems into structured frameworks.

Now we work with Fortune 500 companies, using AI + human coaches to handle skills assessment, transition planning, and manager alignment for 10k+ employees daily. The goal: structure the work so human coaches focus on high-impact moments while AI handles scaffolding.

Let's find 20 minutes—I'd love to show you how this could work for your team. vrijen@careerspan.com"

---

#### PART B: Forwardable Email Wrapper ⭐ ENHANCED in v2.1

**Purpose:** Generate a TWO-LAYER email structure for warm introductions:
1. **Layer 1:** Cover note TO the introducer (the mutual acquaintance)
2. **Layer 2:** Forwardable content that the introducer can pass along to the end recipient

**Key insight:** The introducer (e.g., Victor) will forward Layer 2 to their contact. Layer 1 is just for the introducer; Layer 2 is what gets forwarded.

---

**STRUCTURE:**

**Layer 1: Cover Note to Introducer**
- Written TO the mutual acquaintance (the person V met with)
- Provides context for why V is sending this
- Asks them to forward Layer 2
- References the meeting conversation

**Layer 2: Forwardable Intro (designed to be forwarded)**
- Written as if V is introducing themselves to the END recipient
- Self-contained (makes sense without Layer 1)
- Includes context the introducer mentioned (so end recipient knows why they're receiving it)
- Has clear CTA for the end recipient

---

**Format template:**
```markdown
---
## Layer 1: Cover Note to Introducer

**To:** [Introducer name] (the person V met with)
**Subject:** Quick intro for [end recipient / their team] — ready to forward

---

Hi [Introducer],

[Reference the conversation where intro was discussed]

Below is something you can forward to [end recipient / team]. I've written it so it provides all the context they need — just forward as-is or add your own note on top.

[Optional: any specific ask or context for the introducer]

Thanks for making the connection!

Best,
V

---

## Layer 2: Forwardable Intro (copy/paste or forward below this line)

**Suggested subject:** Intro – [Subject] | [Value Prop]

---

Hi [End Recipient or "there"],

[Introducer name] mentioned you're [context from meeting — what the end recipient is working on/evaluating].

[Embedded blurb — the Type 1 or Type 2 blurb from Part A]

[Specific CTA for end recipient — schedule call, reply with availability, etc.]

Best,
V

[Contact info]

---
```

---

**Example (Victor intro to portfolio company):**

```markdown
---
## Layer 1: Cover Note to Introducer

**To:** Victor Hu
**Subject:** Quick intro for your portfolio company — ready to forward

---

Hi Victor,

Following up on our conversation about your portfolio company evaluating AI coaching solutions.

Below is something you can forward to the team there. I've written it so it provides all the context they need around the "build vs. partner" question — just forward as-is or add your own note.

Let me know if you'd like me to adjust anything before you send it along.

Thanks for making the connection!

Best,
V

---

## Layer 2: Forwardable Intro (copy/paste or forward below this line)

**Suggested subject:** Intro – Careerspan | AI Career Coaching Partnership

---

Hi,

Victor mentioned you're evaluating AI coaching solutions and weighing whether to build or partner. I run Careerspan — we've been solving exactly this problem.

[Embedded blurb from Part A]

I'd love to show you how this could work for your team. Can we find 30 minutes?

Best,
V

vrijen@mycareerspan.com | calendly.com/v-at-careerspan/30min

---
```

---

**Old pattern (DEPRECATED — for direct sends only):**

The previous single-layer pattern is still valid when V is emailing the end recipient DIRECTLY (not through an introducer):

```markdown
## Direct Email (No Introducer)

**Subject:** Intro – [Subject] | [Value Prop]

---

Hi [Recipient],

[Context for why V is reaching out]

[Embedded blurb]

[CTA]

Best,
V
```

Use the TWO-LAYER pattern when there's a mutual acquaintance facilitating the intro.
Use the DIRECT pattern when V is cold-emailing or following up directly.

---

**Example (direct send — no introducer):**

```markdown
---
## Direct Email

**Subject:** Intro – Careerspan | Enterprise Career Development at Scale

---

Hi Sarah,

Great talking about your retention challenges yesterday—especially the coaching bottleneck you mentioned. Here's what I told you I'd send:

Careerspan helps enterprise teams solve their biggest career development challenge: making coaching scalable without losing quality.

We combine AI-powered workflows with human coaches—AI handles assessments, planning frameworks, and manager alignment, while humans focus on high-impact moments. The result: personalized guidance at scale, not generic training that gets ignored.

Fortune 500 organizations across financial services, tech, and healthcare use us—10k+ employees on the platform daily. I spent a decade as a career coach before building this, which taught me that most career problems aren't complicated—they're just unstructured. Careerspan fixes that.

Best way to see it: careerspan.com/demo or grab 20 minutes with me.

Can we do Thursday afternoon? Let me know what works.

Best,
V

---
```

**Personalized Opener Sources:**
- **B21 (Key Moments):** Reference specific quote or resonant moment
- **B01 (Detailed Recap):** Reference strategic context or outcome discussed
- **B08 (Stakeholder Intel):** Reference their challenge or interest
- **B02 (Commitments):** Reference what was promised ("Here's what I told you I'd send")

**CTA Calibration:**
| Relationship | CTA Style |
|--------------|-----------|
| Cold intro | "Would love to connect—here's my calendar: [link]" |
| Warm intro | "Can we do [specific day]? Let me know what works." |
| Investor | "Happy to dive deeper—what's your calendar like this week?" |
| Customer | "Want to show you a demo—can we grab 30 minutes?" |
| Partnership | "I think there's real alignment here. Let's talk [specific day]." |

---

### PHASE 6: QUALITY CHECK ⭐ UPDATED in v2.0

**Score against rubric (target ≥85/100):**

#### Voice Fidelity (30 points)
- [ ] 8pts: Directness appropriate (0.8)—leads with value, no hedging
- [ ] 8pts: Pressure level right (0.6)—clear CTA, not vague "let me know"
- [ ] 8pts: Confidence present (0.8)—assertive claims, clear authority
- [ ] 6pts: Sounds like V would actually say this?

#### Meeting Context Integration (20 points) ⭐ NEW
- [ ] 8pts: Uses specific details from B01/B21 (not generic)
- [ ] 6pts: Reflects stakeholder relationship from B08
- [ ] 6pts: References commitments from B02 (if applicable)

#### Audience Fit (20 points)
- [ ] 10pts: Tailored to recipient's context and needs
- [ ] 6pts: Appropriate technical depth
- [ ] 4pts: Addresses recipient's likely questions

#### Specificity (15 points)
- [ ] 6pts: Includes concrete numbers or proof points
- [ ] 5pts: Has 1-2 human details (not zero, not more)
- [ ] 4pts: Avoids vague claims and marketing puffery

#### Email Wrapper Quality (15 points) ⭐ NEW
- [ ] 6pts: Personalized opener references specific meeting moment
- [ ] 5pts: CTA is specific and actionable (not generic)
- [ ] 4pts: Subject line follows format: `Intro – [Subject] | [Value]`

**Total: ___/100**

**Score Interpretation:**
- 90-100: Send-ready, authentic V voice, clear pressure
- 85-89: Good but needs polish (revise CTA or opener)
- 80-84: Acceptable but missing context or pressure
- <80: Regenerate with more meeting context

**If score < 85:** Revise and re-score before delivery.

---

## QUALITY RUBRIC (Detailed Scoring) ⭐ UPDATED in v2.0

### Voice Fidelity (30 pts total)

**Directness (8 pts):**
- 8: Leads with value, no hedging, gets to point immediately
- 6: Mostly direct, one minor hedge
- 4: Some hedging or roundabout phrasing
- 0: Vague, indirect, buries the lede

**Pressure (8 pts):**
- 8: Clear, specific CTA with appropriate urgency
- 6: CTA present but could be more specific
- 4: Vague CTA like "let me know"
- 0: No CTA or passive ending

**Confidence (8 pts):**
- 8: Assertive authority—specific claims, clear expertise
- 6: Confident but slightly tentative in places
- 4: Either too humble or too boastful
- 0: No clear authority

**"Sounds like V" (6 pts):**
- 6: Would use this verbatim
- 4: Close, minor tweaks needed
- 2: Recognizable but needs work
- 0: Doesn't match V's voice

---

### Meeting Context Integration (20 pts total) ⭐ NEW

**Specific details from B01/B21 (8 pts):**
- 8: Uses verbatim quotes or specific moments from meeting
- 6: References meeting context generally
- 3: Generic opener that could fit any meeting
- 0: No meeting context

**Stakeholder relationship from B08 (6 pts):**
- 6: Reflects relationship depth and recipient's interests
- 4: Some awareness of recipient context
- 2: Generic audience assumptions
- 0: Wrong audience or context

**References commitments from B02 (6 pts):**
- 6: "Here's what I promised" or similar explicit callback
- 4: Implicit reference to commitments
- 2: No reference to commitments
- 0: Contradicts what was committed

---

### Audience Fit (20 pts total)

**Tailored to recipient (10 pts):**
- 10: Clearly customized for this specific person/company
- 7: General but appropriate for audience type
- 4: Generic, could be for anyone
- 0: Wrong audience or context

**Technical depth (6 pts):**
- 6: Perfect level for audience
- 4: Slightly off (too technical or too simple)
- 2: Significantly wrong level
- 0: Incomprehensible or condescending

**Addresses likely questions (4 pts):**
- 4: Anticipates and answers recipient's probable questions
- 2: Addresses some questions
- 0: Leaves obvious gaps

---

### Specificity (15 pts total)

**Concrete proof (6 pts):**
- 6: Multiple specific numbers, names, or proof points
- 4: At least one strong proof point
- 2: Vague claims without evidence
- 0: No proof or specifics

**Human detail (5 pts):**
- 5: 1-2 human details (perfect balance)
- 3: Zero OR too many human details
- 0: Completely impersonal or overly personal

**Avoids puffery (4 pts):**
- 4: No marketing cliches or vague intensifiers
- 2: Minor puffery present
- 0: Heavy marketing language

---

### Email Wrapper Quality (15 pts total) ⭐ NEW

**Personalized opener (6 pts):**
- 6: References specific meeting moment (quote, topic, shared interest)
- 4: References meeting generally ("Great talking yesterday")
- 2: Generic opener ("Hope you're well")
- 0: No personalization

**CTA specificity (5 pts):**
- 5: Specific ask with day/time suggestion
- 3: Clear ask but generic ("Let me know")
- 1: Weak or passive ask
- 0: No CTA

**Subject line format (4 pts):**
- 4: Follows `Intro – [Subject] | [Value]` exactly
- 2: Close but missing element
- 0: Generic or wrong format

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

- **v2.1 (2026-01-03):** Anti-hallucination update
  - ⭐ **CRITICAL: Added PHASE 1.1: Anti-Hallucination Gate**
  - Positioning file (`Knowledge/current/careerspan-positioning.md`) now REQUIRED for Careerspan blurbs
  - Added PLACEHOLDER MODE for when positioning file is incomplete
  - Added Fact Verification Status table to output
  - Claims must be sourced from: positioning file, transcript, or intelligence blocks
  - FORBIDDEN: Inventing metrics, fabricating customers, making up timelines

- **v2.0 (2026-01-03):** Major enhancement
  - ⭐ Added PHASE 0: Selectivity gate (generate only when needed)
  - ⭐ Enhanced PHASE 1: Full meeting context (B01, B21, B08 required)
  - ⭐ Added PHASE 1.5: Semantic memory enrichment
  - ⭐ Enhanced PHASE 4: Updated voice dials (more direct, more pressure)
  - ⭐ Enhanced PHASE 5: Always generates forwardable email wrapper
  - ⭐ Updated quality rubric: Added Meeting Context (20pt) and Email Wrapper (15pt)
  - Voice changes: Directness 0.8 (up from implicit), Pressure 0.6 (up from 0.2)
  - Examples updated to reflect more direct, pressureful tone

- v1.0 (2025-11-17): Initial Blurb Generator with Type 1/Type 2 support, flexible subject detection

---

**Ready to generate. Invoke with meeting intelligence or provide B14 block directly.**

**v2.0 Output Format:**
```
## Raw Blurb (Type [1|2])
[Generated blurb content]

---

## Forwardable Email Wrapper
**Subject:** Intro – [Subject] | [Value Prop]

---

[Full email with personalized opener, embedded blurb, specific CTA]

---

**Quality Score:** XX/100
- Voice: X/30
- Context: X/20
- Audience: X/20
- Specificity: X/15
- Wrapper: X/15
```



