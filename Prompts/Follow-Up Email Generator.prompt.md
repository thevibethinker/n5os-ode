---
created: 2025-11-16
last_edited: 2025-11-17
version: 2.1
tool: true
description: Generate high-quality follow-up emails from meeting intelligence using voice transformation system
tags:
  - email
  - communications
  - meetings
  - voice-transformation
  - essential-links
---

# Follow-Up Email Generator v2.0

**Purpose:** Generate authentic, high-quality follow-up emails from meeting intelligence  
**Quality Bar:** Must score ≥90/100 on rubric (voice fidelity, organization, deliverables)  
**Voice System:** Uses V's voice transformation with style constraints

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

**Database:** `file 'N5/data/content_library.db'`  
**Script:** `python3 /home/workspace/N5/scripts/content_library_db.py`

**CRITICAL:** Whenever deliverables/commitments mention links or resources, query the content library to auto-populate the correct URLs.

**Usage patterns:**
```bash
# Search for trial links
python3 /home/workspace/N5/scripts/content_library_db.py search --query "trial" --type link

# Search by tags
python3 /home/workspace/N5/scripts/content_library_db.py search --tag purpose=scheduling

# Get specific item by ID
python3 /home/workspace/N5/scripts/content_library_db.py get --id trial_code_general
```

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

### PHASE 2: VOICE TRANSFORMATION (Load + Apply)

**Load voice system files:**
1. file 'N5/prefs/communication/voice-system-prompt.md'
2. file 'N5/prefs/communication/style-guides/follow-up-email-style-guide.md'
3. file 'N5/prefs/communication/email.md'

**Infer transformation dials:**
- **Formality:** 4/10 (warm professional, not corporate)
- **Energy:** 7/10 (energized, forward momentum)
- **Specificity:** 9/10 (precise details, numbers, quotes)
- **Structure:** 8/10 (heavy use of bullets, headers, organization)
- **Pressure:** 2/10 (low-pressure, collaborative, "when convenient")

**Apply voice constraints from style guide:**
- Default greeting: "Hi [Name]" (use "Hey" only if warm/established)
- Opening: Resonant moment callback (specific detail from meeting)
- Body: Organized with bold headers + bullets
- Closing: "Best,"
- Length: 10-15 sentences typical when delivering multiple items

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
- **Timeline** if not immediate

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
- **If link mentioned but not in database:** Flag for V to add it

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

### PHASE 4: FINALIZATION (Quality Check + Save)

#### Quality Scoring Rubric (Target: ≥90/100)

**Voice Fidelity (40 points):**
- [ ] 10pts: Resonant opener references specific conversation moment
- [ ] 10pts: Uses V's signature phrases ("energized by", "would love to", "let's X together")
- [ ] 10pts: Low-pressure collaborative tone (not transactional)
- [ ] 10pts: Specific details (quotes, numbers, named concepts)

**Organization (20 points):**
- [ ] 10pts: Deliverables organized with bold headers + bullets
- [ ] 5pts: Clear sections (opener, deliverables, next steps, close)
- [ ] 5pts: Easy to scan (structure makes reading effortless)

**Completeness (20 points):**
- [ ] 10pts: Every promised deliverable included
- [ ] 5pts: Links/access provided (not "coming soon")
- [ ] 5pts: Timeline specifics given where applicable

**Technical Excellence (20 points):**
- [ ] 5pts: Subject line follows format exactly
- [ ] 5pts: Greeting appropriate (Hi default)
- [ ] 5pts: "Best," closing
- [ ] 5pts: No typos, correct em dashes (–), proper formatting

**Score interpretation:**
- 90-100: Send-ready, authentic V voice
- 80-89: Good but needs polish (revise)
- <80: Regenerate with more context

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
---

# Follow-Up Email

**To:** [Recipient name]
**From:** Vrijen Attawar
**Subject:** [Full subject line]

---

[Email body]

---

**Generation metadata:**
- Intelligence sources: B02, B25, B21, B26
- Voice dials: Formality 4/10, Energy 7/10, Specificity 9/10
- Quality score: XX/100
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

### Voice transformation is NON-NEGOTIABLE:
- Load style guide BEFORE generating
- Apply dials as specified
- Use signature phrases from guide
- Follow structure patterns exactly

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

**Version:** 2.1  
**Date:** 2025-11-17  
**Updates:** 
- Integrated Essential Link System (Content Library Database)
- Links now pulled from `/home/workspace/N5/data/content_library.db`
- Deprecated JSON-based link storage
- Added database query instructions to Phase 1

**Architect:** Vibe Architect + Vibe Operator  
**Migration Status:** Complete - Database initialized with 66 items (59 links, 7 snippets)






