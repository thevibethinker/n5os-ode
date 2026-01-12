---
created: 2025-11-16
last_edited: 2026-01-12
version: 3.2
tool: true
description: Generate high-quality follow-up emails from meeting intelligence using voice transformation and semantic memory (with anti-hallucination)
tags:
  - email
  - communications
  - meetings
  - voice-transformation
  - essential-links
  - semantic-memory
mg_stage: MG-5
status: canonical
---
# Follow-Up Email Generator v3.2

**Purpose:** Generate authentic, high-quality follow-up emails from meeting intelligence
**Quality Bar:** Must score ≥90/100 on rubric (voice fidelity, semantic enrichment, organization, deliverables)
**Voice System:** Uses V's voice transformation with style constraints
**Semantic Memory:** Pulls context from CRM, meeting history, and V's positions
**Anti-Hallucination:** All URLs, metrics, and company claims must be sourced from positioning file or content library

**v3.2 Key Change:**
- ⭐ PHASE 2.5: Voice Injection Layer (auto-applies V's linguistic primitives)

**v3.1 Key Change:**
- ⭐ PHASE 1.1: Anti-hallucination gate (prevents fabricated URLs, metrics, company claims)

---

## EXECUTION SEQUENCE

### PHASE 1: HARVEST (Load Intelligence Blocks)

**Load these files from meeting folder:**
1. `B02_COMMITMENTS.md` - Promises made, deliverables committed
2. `B25_DELIVERABLE_CONTENT_MAP.md` - Specific items to deliver
3. `B21_KEY_MOMENTS.md` - Resonant/memorable moments from conversation
4. `B26_METADATA.md` - Meeting participants, context, timing
5. `transcript.md` - Full conversation (if needed for context)

**Load Essential Links from Content Library Database:**

**Database:** `file 'Personal/Knowledge/ContentLibrary/content-library-v3.db'`  
**Script:** `python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py`

**CRITICAL:** Whenever deliverables/commitments mention links or resources, query the content library to auto-populate the correct URLs.

**Usage patterns:**
```bash
# Search for trial links
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py search --query "trial" --type link

# List by type
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py list --type link --limit 20

# Get specific item by ID
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py get trial_code_general
```
**Short.io Integration (Traceability):**
If a deliverable requires a traceable link (e.g., Google Drive folder, deck, proposal) and isn't already in the Content Library:
1. Use `python3 N5/scripts/shortio_link_service.py create --url <long_url> --title <title>` to generate a short link.
2. This automatically registers the link in `shortio_links.jsonl` AND the Content Library database.
3. Use the generated `shortURL` in the email body.


**Common promise → query mapping:**
- "I'll send you a trial link" → `search --query "trial"`
- "Here's my calendar link" → `search --tag purpose=scheduling`
- "I'll share our demo" → `search --query "demo"`
- "I'll send the deck" → `search --query "deck pitch"`
- "Here's our website" → `search --query "homepage"`

**After querying, enrich deliverables map with actual URLs:**
```
{
  "promised_deliverables": [
    {
      "item": "Trial access link",
      "status": "ready",
      "url": "[actual URL from content_library.db]",
      "id": "trial_code_general"
    }
  ]
}
```

**Extract semantically:**
- **CTAs:** Specific actions V committed to take
- **Deliverables:** Links, intros, documents promised
- **Essential Links:** Query database for relevant links mentioned in commitments
- **Resonant moments:** Memorable quotes, concepts discussed, human context
- **Timeline commitments:** When things will be delivered

**Build internal maps:**
```
{
  "promised_deliverables": [
    {"item": "Intro to Kamina Singh", "status": "pending", "timeline": "this week"},
    {"item": "Trial access link", "status": "ready", "url": "[from database]", "db_id": "trial_code_general"}
  ],
  "essential_links": [
    {"id": "trial_code_general", "title": "Careerspan Trial (General)", "url": "https://..."},
    {"id": "vrijen_work_30m_primary", "title": "Vrijen Work Meeting (30m)", "url": "https://..."}
  ],
  "resonant_moments": [
    "conversation on walk through the city",
    "humble bundle concept",
    "your elimination of upfront fees removes biggest friction point"
  ],
  "recipient_context": {
    "name": "Mark",
    "company": "Approximate Experience",
    "relationship": "warm/new partnership"
  }
}
```

---

### PHASE 1.1: ANTI-HALLUCINATION GATE ⭐ NEW in v3.1

**Purpose:** Prevent fabrication of URLs, metrics, or company claims. All factual content must be sourced.

**⚠️ FUNDAMENTAL RULE: NEVER INVENT FACTS**

```
ALLOWED sources for claims:
├── Knowledge/current/careerspan-positioning.md (REQUIRED for any Careerspan claims)
├── Content Library database (for URLs, links, assets)
├── Meeting transcript / intelligence blocks (for conversation-specific facts)
├── CRM profile (for relationship context)
└── N5/prefs/communication/deprecated/essential-links.json (fallback for URLs)

FORBIDDEN:
├── Inventing URLs (trial links, calendar links, demo links)
├── Fabricating metrics (user counts, engagement rates, revenue)
├── Making up company descriptions not in positioning file
├── Creating proof points without source
└── Guessing email addresses or contact info
```

**Pre-Generation Checklist:**

| Content Type | Source Required | If Missing |
|--------------|-----------------|------------|
| Trial/signup URLs | Content Library OR Positioning file | Use `[VERIFY: URL]` placeholder |
| Calendar links | Content Library OR Positioning file | Use `[VERIFY: calendar URL]` |
| Company metrics | Positioning file only | Omit or use qualitative language |
| Careerspan description | Positioning file | Use generic "AI career coaching" |
| Contact email | Positioning file | Use `[VERIFY: email]` |
| Demo/deck links | Content Library | Use `[VERIFY: link]` |

**Positioning File Check:**

```
IF email mentions Careerspan product/metrics:
  ↓
  Load file 'Knowledge/current/careerspan-positioning.md'
  ↓
  Is file present AND populated?
    ├─ YES → Extract verified claims only
    └─ NO → Use ONLY generic descriptions, mark specifics as [VERIFY]
```

**URL Verification Flow:**

```
For each URL/link in email:
  ↓
  1. Check Content Library: python3 .../content_library_v3.py search --query "[topic]"
  2. If not found → Check Positioning file Contact & Links section
  3. If not found → Check essential-links.json (deprecated but valid)
  4. If still not found → Use [VERIFY: description of needed link]
```

**Output Requirement:**
Include a **Fact Verification Status** section in the email metadata showing source for each claim/URL.

---

### PHASE 1.5: SEMANTIC MEMORY ENRICHMENT ⭐ NEW in v3.0

**Purpose:** Pull relevant context from past meetings, CRM profiles, and V's positions before generating.

**Memory Client:**
```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()
```

**Query Patterns:**

**1. CRM Profile (Relationship History):**
```python
crm_context = client.search_profile(
    profile="crm",
    query=f"{recipient_name} {recipient_company}",
    limit=5
)
```
- Prior interactions, relationship depth, communication history
- Use to calibrate formality dial

**2. Meeting History (Prior Conversations):**
```python
meeting_history = client.search_profile(
    profile="meetings",
    query=f"{recipient_name} {key_topics}",
    limit=5,
    recency_weight=0.3
)
```
- Past meetings with this person
- Enables callbacks: "Building on our October conversation about..."

**3. V's Positions (Strategic Context):**
```python
positions = client.search_profile(
    profile="positions",
    query=f"{key_partnership_topics}",
    limit=3
)
```
- V's strategic positions on relevant topics
- Use for complex partnerships where positioning matters

**4. Similar Emails (Style Reference):**
```python
similar_emails = client.search(
    query=f"follow-up email {meeting_type} high engagement",
    metadata_filters={"path": ("contains", "FOLLOW_UP_EMAIL")},
    limit=3
)
```
- Past high-quality emails as style exemplars
- Match meeting type (investor, founder, customer, etc.)

**Build Semantic Context Map:**
```json
{
  "prior_relationship": {
    "meetings_count": 3,
    "last_meeting": "2025-10-14",
    "topics_discussed": ["humble bundle", "FOHE pilot"],
    "relationship_depth": "warm"
  },
  "v_positions_relevant": [
    {"topic": "B2U go-to-market", "key_point": "community-first distribution"},
    {"topic": "career coaching scale", "key_point": "AI + human hybrid"}
  ],
  "shared_history": "3 previous meetings, collaboration on FOHE pilot, discussed humble bundle concept"
}
```

**Usage in Generation:**
- Reference prior context in opener: "Building on our October conversation about [X]..."
- Use relationship depth to calibrate dials (warm → lower formality)
- Incorporate V's positions when relevant to deliverables
- Reference shared history naturally: "As we discussed when you first introduced..."

---

### PHASE 2: VOICE TRANSFORMATION (Enhanced in v3.0)

**Load voice system files:**
1. file 'N5/prefs/communication/voice-system-prompt.md'
2. file 'N5/prefs/communication/style-guides/follow-up-email-style-guide.md'
3. file 'N5/prefs/communication/email.md'

**Load style exemplars from semantic memory:**
Use the `similar_emails` results from PHASE 1.5 as few-shot examples for voice matching.

**Context-Aware Dial Calibration (Updated for Directness + Pressure):**

| Relationship Type | Formality | Energy | Specificity | Directness | Pressure |
|-------------------|-----------|--------|-------------|------------|----------|
| New external      | 5/10      | 6/10   | 8/10        | 7/10       | 5/10     |
| Established partner| 3/10     | 8/10   | 9/10        | 8/10       | 6/10     |
| VC/Investor       | 5/10      | 7/10   | 9/10        | 8/10       | 7/10     |
| Coaching client   | 4/10      | 7/10   | 8/10        | 7/10       | 4/10     |
| First meeting     | 5/10      | 6/10   | 8/10        | 7/10       | 5/10     |
| Warm repeat       | 3/10      | 8/10   | 9/10        | 8/10       | 6/10     |
| Partnership/Deal  | 4/10      | 8/10   | 9/10        | 9/10       | 7/10     |

**Directness:** Get to the point, no hedging, clear value statement upfront
**Pressure:** Clear CTAs, gentle urgency, make asks explicit (socially acceptable push)

**Use `prior_relationship.relationship_depth` from PHASE 1.5 to select row.**

**Signature Phrases Bank (MUST use naturally, not forced):**
- **Opener energy:** "energized by", "excited about", "appreciated", "grateful for"
- **Collaboration:** "let's [X] together", "would love to", "looking forward to"
- **Specificity markers:** "specifically", "the [exact concept] you mentioned", "your point about"
- **Progress indicators:** "I've already reached out to", "speaking with X tomorrow about", "working on"
- **Connectives:** em-dashes (–), "which means", "that's why", "because"
- **Direct CTAs (NEW):** "Can we do [day]?", "Let's find 20 minutes", "What's your calendar like?", "I'd suggest we..."
- **Pressure (socially acceptable):** "Given our conversation", "timing works well because", "I think there's real synergy here"

**Avoid hedging phrases:**
- ❌ "If you're interested" → ✓ "I'd love to show you"
- ❌ "Let me know if that works" → ✓ "Can we do Thursday?"
- ❌ "No rush" → ✓ "When works this week?"
- ❌ "Whenever you have time" → ✓ "Can we find 15 minutes?"

**Resonant Opener Templates (with semantic memory):**

*Pattern 1 - Prior Context Callback (if meeting_history exists):*
> "Building on our [date] conversation about [specific topic from memory], I wanted to follow up on [today's discussion]..."

*Pattern 2 - Specific Detail Reference (from B21):*
> "Your insight about [verbatim or near-verbatim from B21] really resonated..."

*Pattern 3 - Progress Since Last Meeting:*
> "Since we last spoke about [topic from prior meeting], I've [concrete progress]..."

*Pattern 4 - Standard Resonant (no prior history):*
> "Great chatting [timeframe]. I'm excited about [specific concept from this meeting]..."

**Apply voice constraints from style guide:**
- Default greeting: "Hi [Name]" (use "Hey" only if warm/established)
- Opening: Resonant moment callback (specific detail from meeting)
- Body: Organized with bold headers + bullets
- Closing: "Best,"
- Length: 10-15 sentences typical when delivering multiple items

---

### PHASE 2.5: VOICE INJECTION LAYER ⭐ NEW in v3.2

**Purpose:** Auto-inject V's distinctive linguistic patterns. Fully automatic — no human review.

**Implementation:**
```python
from N5.scripts.voice_layer import VoiceContext, inject_voice

# Build context from meeting
ctx = VoiceContext(
    content_type="email",
    platform="email",
    purpose="follow-up",
    topic_domains=extracted_domains_from_meeting,  # e.g., ["hiring", "career", "partnership"]
)

# Auto-inject (happens before generation)
enhanced_prompt = inject_voice(base_generation_prompt, ctx)
```

**What happens automatically:**
1. Layer retrieves 3 relevant primitives from `voice_library.db`
2. Primitives injected as context into generation prompt
3. LLM weaves patterns naturally (never forced)
4. Usage tracked to prevent repetition

**Example injected fragment:**
```
## Voice Enhancement (Auto-Applied)

Weave these V-distinctive patterns naturally into your writing:

1. [metaphor] "talent optionality" — framing career moves as options
2. [signature_phrase] "provenanced work history"
3. [syntactic_pattern] "X isn't Y, it's Z"

Guidelines:
- Use what fits naturally, skip what doesn't
- One distinctive element per paragraph max
- Never force — if it feels mechanical, leave it out
```

**Domain Extraction (from meeting context):**
- From B06_BUSINESS_CONTEXT: industry, sector
- From B26_METADATA: meeting type, company sector
- From conversation topics: inferred domains

---

### PHASE 3: COMPOSITION (Generate Email)

#### Step 1: Generate Subject Line

**Format:** `Follow-up Email – [Name] x [Company] [Topic • Topic • Topic]`

**Rules:**
- Em dash (–) after "Follow-up Email"
- Bullet separators (•) between topics
- Capitalize key nouns
- Extract topics from B26 or infer from context

**Example:** `Follow-up Email – Fei x Careerspan [Humble Bundle • FOHE Pilot]`

---

#### Step 2: Craft Opening (Resonant Callback)

**Priority: HIGH** - This sets tone for entire email

**Pattern:** Reference specific, memorable moment from meeting

**Extract from B21_KEY_MOMENTS.md:**
- Look for verbatim quotes
- Human context (walk, call timing, setting)
- Concepts discussed that excited both parties

**Templates:**
- "Great chatting [timeframe]. Thanks for [specific human context]."
- "I'm excited about [specific concept]. Your [specific insight] really resonated..."
- "I can't thank you enough for that stellar call. Your insights on [X and Y] were spot-on..."

**Anti-patterns to avoid:**
- ❌ Generic: "Hope this finds you well"
- ❌ Corporate: "Per our conversation"
- ❌ Empty: "Just wanted to follow up"

---

#### Step 3: Show Progress (Optional but powerful)

**Pattern:** Demonstrate action taken since meeting (1-2 sentences)

**Examples:**
- "I've reached out to [person] this week about [thing discussed]"
- "Speaking with [person] tomorrow about [pilot/partnership]"
- "We're actively building out [thing] right now"

**Why this works:** Proves you're not just talking, you're doing

---

#### Step 4: Organized Deliverables (Core Section)

**Use deliverables from B02 + B25**

Assume that anything you talk about in the email body as a deliverable (slides, articles, 1-pagers, etc.) is something that will be **attached or linked in this email** by the time V sends it, even if it is not yet present in the content library. V will do the custom work to acquire/create it before sending.

**Structure:**
```
*Here's what I promised:*

* *[Deliverable 1]* – [Description with context/value]
* *[Deliverable 2]* – [Description with why it matters]
* *[Deliverable 3]* – [Link or timeline for completion]
```

**For each deliverable:**
- **Bold header** for item name
- **Em dash (–)** after header
- **Context/value prop** explaining why it matters to them
- **Specific details:** numbers, names, URLs
- **Timeline** if the core action truly happens **after** this email (e.g., future intro, project milestone). For assets that are included in this email (slides, articles, 1-pagers), no timeline is needed beyond the fact that they are included now.
- **Tense & framing:** Write as if the deliverable is included in this email, not something you will send later. Prefer patterns like "I've included…", "Here's…", "You'll find a link below…". Avoid defaulting to "I'll send over…" / "I'll send this separately…" unless the plan genuinely requires delivery after this email (rare case).
- **Checklist mapping:** For every deliverable you mention in the body, create a corresponding item in the **Promised Deliverables Checklist (for V before sending)** section at the end of the file.

**Example from Mark email:**
```
*Here's what I promised:*

* *Kamina Singh intro* – She's been instrumental in getting us into a dozen+ universities and knows career centers inside-out. She'll be a tremendous ally for your pilots.

* *Career/HR tech founder roundtable* – You'll love this crew. We have 20+ founders tackling adjacent problems, including several doing B2U go-to-market. Register here: [link]

* *Careerspan trial access* – Here's a trial link for you and your team: [link]. Tinker around, test it with your use cases, and once you've scoped out what works, let me know how many licenses you'd like.
```

**Rules:**
- Always include links/access when available
- If intro is pending, say "incoming" or "coming via LinkedIn"
- Mix immediate value with future value
- Make their life easy (provide blurbs if needed for intros)
- **Query database for promised links:** Use `content_library_db.py search` to find exact URLs
- **Never hardcode links:** Always pull from database (single source of truth)
- **If link mentioned but not in database:** Still write as if it is included in this email, and mark it in the Promised Deliverables Checklist as `content library: candidate to add`.

---

#### Step 5: Forward-Looking Next Steps

**Pattern:** Clear, actionable coordination

**Templates:**
- "Let me know if [timeframe] works"
- "Let's compare notes after you [milestone]"
- "I'll have [deliverable] ready by [day], plus [bonus item]"
- "Once we [achieve X], let's [next step] together"

**Example:**
"I'll have the formalized concept ready by Friday, plus notes from Ray. Once we gauge the soft interest, let's co-pitch their leadership together."

**Rules:**
- Be specific about timelines
- Make coordination easy (offer options, times, links)
- Position as collaborative ("let's do X together")
- Low-pressure language ("when convenient", "whenever makes sense")

---

#### Step 6: Warm Closing

**Pattern:** Optional appreciation + "Best,"

**Optional line before close:**
- "Looking forward to collaborating on this!"
- "Really appreciate you being in our corner as we build..."
- "Excited to see where this goes"

**Always end with:** "Best,"

**Signature:** Email system handles automatically

---

### PHASE 4: FINALIZATION (Enhanced in v3.0)

#### Quality Scoring Rubric (Target: ≥90/100)

**Voice Fidelity (35 points):**
- [ ] 10pts: Resonant opener references specific conversation moment
- [ ] 10pts: Uses V's signature phrases naturally (not forced)
- [ ] 10pts: Low-pressure collaborative tone (not transactional)
- [ ] 5pts: Greeting/closing match relationship depth

**Semantic Enrichment (15 points):** ⭐ NEW
- [ ] 5pts: References prior relationship context appropriately (if exists)
- [ ] 5pts: Incorporates relevant meeting history when available
- [ ] 5pts: Uses V's positions/strategies when applicable to deliverables

**Organization (20 points):**
- [ ] 10pts: Deliverables organized with bold headers + bullets
- [ ] 5pts: Clear sections (opener, deliverables, next steps, close)
- [ ] 5pts: Easy to scan (structure makes reading effortless)

**Completeness (15 points):**
- [ ] 8pts: Every promised deliverable included
- [ ] 4pts: Links/access provided (not "coming soon")
- [ ] 3pts: Timeline specifics given where applicable

**Technical Excellence (15 points):**
- [ ] 5pts: Subject line follows format exactly
- [ ] 3pts: Clean markdown (pasteable to email client)
- [ ] 3pts: No typos, correct em dashes (–)
- [ ] 2pts: Greeting appropriate
- [ ] 2pts: "Best," closing

**Score interpretation:**
- 90-100: Send-ready, authentic V voice
- 80-89: Good but needs polish (revise)
- <80: Regenerate with more context

---

#### Clean Markdown Output (Pasteable to Email Client)

**CRITICAL:** Output must be pasteable into Gmail/Outlook without formatting issues.

**Allowed Markdown in Email Body:**
- ✅ Bold: `**text**` or `*text*` (italics)
- ✅ Bullets: `* item` or `- item`
- ✅ Em-dash: `–` (actual character)
- ✅ Line breaks

**Avoid in Email Body:**
- ❌ Headers (`#`, `##`) - use bold instead
- ❌ Code blocks (` ``` `)
- ❌ Tables
- ❌ Markdown links `[text](url)` - use plain text or hyperlink manually

---

#### Save Email

**Create file:** `FOLLOW_UP_EMAIL.md` in meeting folder

**Format:**
```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
quality_score: XX/100
semantic_enrichment: true
---

# Follow-Up Email

**To:** [Recipient name]
**From:** Vrijen Attawar
**Subject:** [Full subject line]

---
<!-- BEGIN EMAIL BODY - Copy from here -->

Hi [Name],

[Email body with clean markdown only - bold, bullets, em-dashes allowed]

Best,

<!-- END EMAIL BODY -->
---

**Generation metadata:**
- Intelligence sources: B02, B25, B21, B26
- Semantic memory sources: [crm, meetings, positions - list which were used]
- Voice dials: Formality X/10, Energy X/10, Specificity X/10
- Quality score: XX/100

---

**Promised Deliverables Checklist (for V before sending)**

List **every deliverable or asset you referenced in the email body**, regardless of whether it came from the content library or is a custom/one-off item V will create. For each item, include a short reminder of what needs to be attached or linked, plus whether it is already in the content library.

- [ ] [Deliverable 1] – [short reminder of what to attach/link; e.g., "SPC info overload slide(s)"; content library: id=`...` or `candidate to add`]
- [ ] [Deliverable 2] – [...]
- [ ] [Deliverable 3] – [...]

This checklist is **for V only** and is meant to be satisfied before the email is sent. It should be complete and concrete enough that V can quickly verify each promised item is actually included (as attachment or link) and optionally promote missing assets into the content library.
```

---

## IMPORTANT NOTES FOR AI EXECUTION

### This prompt MUST be executed by Vibe Writer persona
**Why:** Writer excels at voice fidelity, tone, structure

### This prompt works in BOTH modes:
1. **Interactive:** Generate email, show to V, get approval
2. **Agentic:** Generate email, score, save to meeting folder (V reviews later)

### Context sources priority:
1. **B25** = Primary source for deliverables
2. **B02** = Source for commitments/promises
3. **B21** = Source for resonant moments (CRITICAL for opener)
4. **B26** = Meeting metadata (participants, context)
5. **transcript.md** = Fallback if blocks insufficient
6. **Knowledge/current/careerspan-positioning.md** = REQUIRED for any Careerspan claims/metrics
7. **Content Library** = REQUIRED for all URLs/links

### Voice transformation is NON-NEGOTIABLE:
- Load style guide BEFORE generating
- Apply dials as specified
- Use signature phrases from guide
- Follow structure patterns exactly

### Promised Deliverables Checklist behavior:
- Always include a **Promised Deliverables Checklist (for V before sending)** section at the end of `FOLLOW_UP_EMAIL.md`.
- For every deliverable or asset mentioned in the body (Step 4), create a corresponding checklist item.
- If the deliverable came from the content library, note the content library id or a clear reference (e.g., `content library: id=trial_code_general`).
- If the deliverable is not yet in the content library, mark it as `content library: candidate to add` in the checklist.
- Treat the checklist as an internal TODO list for V: the outward-facing copy should assume the items are included in this email; the checklist ensures that happens before sending.

### Quality bar is HIGH:
- Target ≥90/100 on rubric
- If first attempt scores <90, revise
- If revision still <90, request more context from V

---

## EXAMPLE OUTPUT (Target Quality)

**Subject:** Follow-up Email – Fei x Careerspan [Humble Bundle • FOHE Pilot]

---

Hi Fei,

I'm excited about the humble bundle concept we mapped out. Your elimination of upfront onboarding fees removes the biggest friction point for budget-conscious communities.

*Next Steps:*

* *Bundle formalization:* I'll document our offering this week – Nira for networking, Careerspan for career development, plus Warmer Jobs and Practice Interviews

* *FOHE pilot:* Speaking with Ray tomorrow about testing with FOHE's 5,000 members (they're perfect – highly active but limited by Slack's 90-day history)

* *Partner alignment:* Scheduling with Asher and Jeff to coordinate implementation

Logan and I are particularly energized by how this addresses the real pain point – jobs being posted only to trusted communities. Your networking layer plus our career readiness creates that essential one-two punch.

I'll have the formalized concept ready by Friday, plus notes from Ray. Once we gauge the soft interest in our idea, let's co-pitch their leadership together.

Looking forward to collaborating on this!

Best,

---

**Quality Score:** 95/100
- Voice Fidelity: 39/40 (authentic, energized, specific)
- Organization: 20/20 (perfect structure)
- Completeness: 18/20 (timelines given, all items present)
- Technical: 18/20 (excellent formatting, one minor em dash)

---

**Version:** 3.1
**Date:** 2026-01-03
**Updates:**
- ⭐ **v3.1: Added PHASE 1.1: Anti-Hallucination Gate**
  - All URLs must come from Content Library or Positioning file
  - All metrics/claims must be sourced from Positioning file
  - Includes Fact Verification Status table in output
  - Uses `[VERIFY: ...]` placeholders when source unavailable
- ⭐ v3.0: Added PHASE 1.5: Semantic Memory Enrichment (CRM, meetings, positions, similar emails)
- ⭐ v3.0: Enhanced PHASE 2: Context-aware dial calibration table, signature phrases bank, semantic opener templates
- ⭐ v3.0: Enhanced PHASE 4: Clean markdown output with BEGIN/END markers for email client compatibility
- ⭐ v3.0: Updated quality rubric: Added 15pt Semantic Enrichment category, rebalanced other categories
- Previous (v2.3): Migrated to Content Library v3
- Previous (v2.3): Added Promised Deliverables Checklist section

**Architect:** Vibe Architect + Vibe Operator
**Migration Status:** Complete - Anti-Hallucination + Semantic Memory Integration (Jan 2026)











