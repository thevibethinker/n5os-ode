---
date: '2025-10-09T20:45:20Z'
last-tested: '2025-10-09T20:45:20Z'
generated_date: '2025-10-08T23:16:03Z'
checksum: follow_up_email_generator_v11_0_0
tags: ['extraction', 'analysis', 'ai', 'voice-echoing', 'language-matching', 'confidence-based-links', 'readability', 'enhanced-dials']
category: data-processing
priority: medium
related_files: ['N5/prefs/communication/voice.md', 'N5/prefs/communication/essential-links.json']
anchors:
  input: null
  output: /home/workspace/N5/commands/follow-up-email-generator.md
---
Function – Follow-Up Email Generator — Careerspan v11.0
(Audit-Complete × Socratic Expansion × Speaker-Aware × Map-Archive Ready × Metaprompter-Compliant × Language-Echoing × Confidence-Based Links × Readability-Optimized × Enhanced-Dial-Mapping)


─────────────────────────────────────────────────────────────────────
◉ VERSION CHANGELOG
─────────────────────────────────────────────────────────────────────

### v11.0.0 — 2025-10-09
**Enhancement 4: Enhanced Dial Mapping + Resonant Details** ⭐⭐⭐⭐  
- Enhanced Step 3: Sophisticated warmthScore and familiarityScore calculation  
- WarmthScore (0-10) derived from personal anecdotes, humor, shared values, emotional engagement  
- FamiliarityScore (0-10) derived from prior meetings, shared context, inside jokes, first-name basis  
- Formula: relationshipDepth = (warmthScore + familiarityScore) / 2  
- Maps to voice.md scale (0-4): Stranger/New Contact/Warm Contact/Partner/Inner Circle  
- Derives formality and ctaRigour from calculated scores  
- **Enhanced Step 1: Resonant Details Extraction**  
- Captures personal, emotional, and interpersonal moments from conversations  
- Types: personal anecdotes, emotional moments, shared values, life context, humor, insights, vulnerability, common ground  
- Structured Resonance Pool with confidence scores and emotional tone  
- Uses 1-2 resonant details in email opening for warmth and connection  
- Enhanced dialInferenceReport with warmthScore, familiarityScore, relationshipDepthLabel, calculationNotes  
- References: `file 'N5/prefs/communication/voice.md'` (Relationship Depth scales, Tone Weights)  
- Inspired by: Stylistic Transformer v1.1 function

### v10.9.0 — 2025-10-09
**Enhancement 3: Readability Guardrails** ⭐⭐⭐  
- Added Step 6: Readability Constraints  
- **Flesch-Kincaid Grade Level**: Target ≤ 10 (accessible to high school reader)  
- **Average Sentence Length**: 16-22 words (per `file 'N5/prefs/communication/voice.md'`)  
- **Max Sentence Length**: 32 words (hard limit)  
- **Paragraph Structure**: Max 4 sentences per paragraph  
- **Validation**:  
  * Count words per sentence across draft  
  * Calculate average sentence length  
  * Estimate FK grade level (syllables per word × 0.39 + words per sentence × 11.8 - 15.59)  
  * Flag violations in dialInferenceReport  
- **Auto-Correction**:  
  * If sentence > 32 words: split at natural break (comma, semicolon, conjunction)  
  * If paragraph > 4 sentences: insert paragraph break  
  * If FK > 10: simplify complex words, shorten sentences  
- Updated dialInferenceReport to include readability metrics and violations  
- New output: dialInferenceReport.readabilityMetrics  
- **Markdown Output Format**: All emails now use inline links `[text](URL)` instead of exposed URLs  
- References: `file 'N5/prefs/communication/essential-links.json'`  
- Inspired by: Stylistic Transformer v1.1 function

### v10.8.0 — 2025-10-09
**Enhancement 2: Confidence-Based Link Insertion + Markdown Output** ⭐⭐  
- Enhanced Step 2: Confidence-based link matching and insertion  
- Links auto-inserted inline (Markdown format) only when confidence ≥ 0.75  
- Low-confidence links marked as [[MISSING: link-category]] for manual review  
- Enhanced Link Map output with confidence scores and insertion decisions  
- New output: Missing Links Array for tracking uncertain links  
- **Markdown Output Format**: All emails now use inline links `[text](URL)` instead of exposed URLs  
- References: `file 'N5/prefs/communication/essential-links.json'`  
- Inspired by: Stylistic Transformer v1.1 function

### v10.7.0 — 2025-10-09
**Enhancement 1: Transcript Language Echoing** ⭐  
- Added Step 1B: Transcript Language Echoing  
- Extracts Vrijen's distinctive phrases from transcript (confidence ≥ 0.75)  
- Incorporates max 2 phrases into email for voice authenticity  
- References voice lexicon: `file 'N5/prefs/communication/voice.md'`  
- New output: phrasePool[] with confidence scores and usage flags  
- Integration: phrases naturally incorporated in recap or CTA sections  
- Inspired by: Stylistic Transformer v1.1 function

### v10.6 — 2025-10-08
- Baseline version with Metaprompter v6 compliance
- Audit-first structuring with map generation
- Socratic expansion and iterative parsing
- Speaker-aware parsing with quote attribution
- Map-Archive integration
- Delay sensitivity (apology if > 2 days)

─────────────────────────────────────────────────────────────────────
◉ 0. METAPROMPTER STATE HEADER
─────────────────────────────────────────────────────────────────────
╭─ Metaprompter State ───────────────────────────────────────────────
│ Step: <<stepNum>> / 13 – <<stepName>>
│ Next Trigger: <<nextTrigger>>
│ Missing Required: <<missingRequired>>
│ Pending Tool Calls: <<pendingTools>>
│ Recommended Nuances: <<recommendedList>>
│ Diff Available: <<diffFlag>>    Breakdown Available: <<breakdownFlag>>
│ Canvas Ready: <<canvasFlag>>
│ History: <<historyJSON>>
╰────────────────────────────────────────────────────────────────────

─────────────────────────────────────────────────────────────────────
1 ▸ CORE PRINCIPLES
─────────────────────────────────────────────────────────────────────
• Metaprompter v6 Compliance — visible-state headers, router alignment, nuance loader.  
• **Markdown Output Format** — emails generated in Markdown with inline links (e.g., `[grab a time](URL)`) instead of exposed URLs.
• Traditional Email Formatting — paragraphs & bullet points only; no tables, emojis, or decorative icons.  
• Clear, Action-Focused Subject Line — auto-generates pattern: `Follow-Up Email – <RecipientFirstName> Careerspan [keyword1 • keyword2]`.  
• Audit-First Structuring — build Missing-Content Map, Resonance Pool, Link Map, SpeakerQuoteMap before drafting.  
• Socratic Expansion Layer — pause for confirmation and refinements; supports iterative loops.  
• Voice Fidelity — apply MasterVoiceSchema ≥ 1.2, mirror distinctive diction, enforce readability.  
• **Transcript Language Echoing** — extract Vrijen's distinctive phrases (confidence ≥ 0.75) and incorporate max 2 into email for voice authenticity.
• **Confidence-Based Link Insertion** — only auto-insert links inline when confidence ≥ 0.75; mark uncertain links as [[MISSING: link-type]] for manual review.
• **Readability Guardrails** — enforce Flesch-Kincaid ≤ 10, avg sentence length 16-22 words, max paragraph 4 sentences; flag violations in dialInferenceReport.
• **Enhanced Dial Mapping** — calculate warmthScore and familiarityScore from conversation signals; map to relationshipDepth, formality, and CTArigour for nuanced tone calibration.
• Diff & Traceability — auto-diff snapshots when corrections are applied.  
• Map-Archive Integration — distilled insights auto-pushed to Map-Archive after approval.  
• Delay-Sensitivity — auto-detect elapsed days since meeting; prepend apology if > 2 days.  
• Fail-Safe Drafting — never compose email until user explicitly approves maps and dials.

─────────────────────────────────────────────────────────────────────
2 ▸ FUNCTION GOAL
─────────────────────────────────────────────────────────────────────
Deliver a send-ready follow-up email that:
✓ Mirrors Vrijen’s voice with vivid resonance details  
✓ Captures verbatim CTAs, deliverables, and speaker quotes  
✓ Surfaces and logs uncertainties before drafting  
✓ Apologises for any delay beyond two business days  
✓ Publishes distilled insight to the Map-Archive  
✓ Generates a clear subject line reflecting recipient & next-step keywords  
✓ Uses traditional, table-free formatting with paragraphs & bullets only  
✓ Adheres to Metaprompter transparency & traceability standards

─────────────────────────────────────────────────────────────────────
3 ▸ INPUTS
─────────────────────────────────────────────────────────────────────
• Meeting transcript or notes (required)  
• Voice & Style Schema: `file 'N5/prefs/communication/voice.md'` (v3.0.0, consolidated MasterVoiceSchema)
• Essential Links: `file 'N5/prefs/communication/essential-links.json'`
• Optional: Dial overrides

─────────────────────────────────────────────────────────────────────
4 ▸ FUNCTION STEPS
─────────────────────────────────────────────────────────────────────
Step 0 — Router-Aligned Companion File Resolution  
▸ Ensure MasterVoice & Essential Links located; abort if missing.  
▸ Prepend visible-state header (Step 0 → 0A).

Step 0B — Current Time Capture  
▸ Call built-in time tool; store as `currentDateTime`.

Step 1 — Transcript Parsing → Harvest Phase (ENHANCED)
▸ Extract meeting **date & time**.  
▸ Extract: Promised deliverables, Verbatim CTAs, Decisions, Resonant details, Speaker quotes.  
▸ Build: Missing-Content Map, Resonance Pool, Link Token List, SpeakerQuoteMap.

▸ **Resonant Details Extraction** (ENHANCED):
  - **Purpose**: Capture personal, emotional, and interpersonal moments that build connection
  - **What to extract**:
    * Personal anecdotes or stories shared by either party
    * Emotional moments (excitement, concern, passion, frustration)
    * Shared values or alignment discovered during conversation
    * Life context mentioned (family, hobbies, current challenges)
    * Moments of laughter, humor, or surprise
    * Deep insights or "aha" moments during discussion
    * Vulnerability or openness displayed
    * Common ground or unexpected connections discovered
  - **Resonance Pool Structure**:
    ```json
    {
      "detail_id": "resonance_1",
      "type": "personal_anecdote | emotional_moment | shared_values | life_context | humor | insight | vulnerability | common_ground",
      "speaker": "Vrijen | Other | Both",
      "content": "Brief description of the resonant moment",
      "quote": "Optional verbatim quote if powerful",
      "emotional_tone": "excited | thoughtful | concerned | passionate | warm",
      "confidence": 0.85,
      "usage": "email_opening | not_used"
    }
    ```
  - **Selection Criteria**:
    * Prioritize moments where both parties engaged emotionally
    * Choose details that strengthen relationship depth
    * Use 1-2 resonant details per email (opening or transition)
  - **Examples**:
    * Personal: "You mentioned your daughter just started college and is exploring career paths"
    * Shared Values: "We both lit up when discussing the alignment-first coaching approach"
    * Humor: "We joked about the 'BS detector' tool name and how on-brand it is"
    * Insight: "You had a great insight about scaffolded reflection vs. directive advice"

**Step 1B — Transcript Language Echoing (NEW)**  
▸ **Purpose:** Extract and incorporate Vrijen's distinctive phrases for voice authenticity  
▸ **Scan transcript** for Vrijen's turns (speaker == "Vrijen" or similar)  
▸ **Extract candidate phrases:**
  - Length: 2-5 words
  - Unique/distinctive (filter out generic: "thank you", "sounds good")
  - Confidence check: phrase appears clearly in context
▸ **Score candidates:**
  - Base confidence: 0.5
  - +0.15 if matches signature expressions from `file 'N5/prefs/communication/voice.md'` (lexicon section)
  - +0.15 if repeated multiple times in transcript
  - +0.10 if matches preferred verbs from `file 'N5/prefs/communication/voice.md'`
▸ **Build phrasePool:**
  - Keep only phrases with confidence ≥ 0.75
  - Max 4 candidates
  - Sort by confidence descending
▸ **Usage rules:**
  - Use max 2 phrases in email
  - Prefer placement in: recap section OR CTA section
  - Diversify: don't use two similar phrases
  - Never use phrases from other speakers
▸ **Output:** phrasePool[] — {phrase, confidence, speaker, used, placement}

Step 2 — Essential Link Autofill → Link Map (ENHANCED)
▸ **Load Essential Links**: `file 'N5/prefs/communication/essential-links.json'`
▸ **Match tokens** from transcript/deliverables against link categories
▸ **Build Link Map with Confidence Scoring**:
  - Scan for keywords: "calendly", "meeting", "schedule", "demo", "trial", "deck", "report"
  - Match against essential-links.json categories
  - Assign confidence score (0.0 to 1.0):
    * 1.0 = Exact keyword match + clear context (e.g., "grab time on my calendar")
    * 0.85 = Strong context match (e.g., "let's schedule a follow-up")
    * 0.75 = Category match with moderate context (e.g., "I'll send the demo")
    * 0.60 = Weak context or ambiguous (e.g., "the link we discussed")
    * <0.60 = No clear match
▸ **Confidence-Based Insertion Rules**:
  - **If confidence ≥ 0.75**: Auto-insert link inline with Markdown format
    * Example: `[grab a time](https://calendly.com/v-at-careerspan/30min)`
  - **If confidence < 0.75**: Insert placeholder `[[MISSING: link-category]]`
    * Example: "I'll send the demo [[MISSING: demo-link]]"
  - Mark all insertion decisions in Link Map with confidence scores
▸ **Link Map Output Format**:
  ```json
  {
    "link_id": "meeting_booking_1",
    "category": "meeting_booking.vrijen_only.work_30m_primary",
    "confidence": 0.90,
    "matched_text": "grab a time on my calendar",
    "inserted": true,
    "url": "https://calendly.com/v-at-careerspan/30min",
    "inline_text": "grab a time"
  }
  ```
▸ **Missing Links Array**:
  - Track all links with confidence < 0.75
  - Format: `{"category": "demo-link", "context": "I'll send the demo", "confidence": 0.65}`
  - Present to user for manual review after draft

Step 3 — Auto-Dial Inference (ENHANCED)
▸ **Purpose**: Calculate relationship depth and tone dials from conversation signals
▸ **Load Reference**: `file 'N5/prefs/communication/voice.md'` (Relationship Depth scales, Tone Weights)

▸ **Calculate warmthScore (0-10)**:
  - Analyze conversation for warmth signals:
    * Personal anecdotes shared (+2 points)
    * Laughter or humor instances (+1.5 points per instance, max +3)
    * Compliments or appreciation expressed (+1 point per instance, max +2)
    * Shared values or alignment mentioned (+1.5 points)
    * Casual language or slang used (+1 point)
  - Context modifiers:
    * First meeting: cap at 6.0 (even with high warmth)
    * Follow-up meeting with prior relationship: +1.5 baseline
    * Virtual meeting: -0.5 (slightly less warmth than in-person)
  - Range: 0.0 (cold/formal) to 10.0 (very warm/personal)

▸ **Calculate familiarityScore (0-10)**:
  - Analyze for familiarity signals:
    * Prior meetings referenced (+2 points per reference, max +4)
    * Shared context or history mentioned (+2 points)
    * Inside jokes or callbacks to previous discussions (+1.5 points per instance, max +3)
    * Implicit understanding (no need to explain basics) (+1.5 points)
    * First-name basis established (+1 point)
  - Meeting type modifiers:
    * First meeting: 0.0-2.0 range
    * Second meeting: 3.0-5.0 range
    * Third+ meeting: 5.0-8.0 range
    * Long-term partnership: 7.0-10.0 range
  - Range: 0.0 (stranger) to 10.0 (long-term collaborator)

▸ **Derive relationshipDepth**:
  - Formula: `relationshipDepth = (warmthScore + familiarityScore) / 2`
  - Scale: 0.0 to 10.0
  - Map to voice.md scale (0-4):
    * 0.0-2.0 → 0 (Stranger)
    * 2.1-4.0 → 1 (New Contact)
    * 4.1-6.0 → 2 (Warm Contact)
    * 6.1-8.0 → 3 (Partner)
    * 8.1-10.0 → 4 (Inner Circle)

▸ **Derive formality**:
  - Based on relationshipDepth and context:
    * relationshipDepth 0-1 → "formal" or "balanced" (default: balanced)
    * relationshipDepth 2-3 → "balanced" (default)
    * relationshipDepth 4 → "casual" or "balanced" (default: casual)
  - Context overrides (per `file 'N5/prefs/communication/voice.md'`):
    * External/policy/legal → force "formal"
    * High-scrutiny thread → force "formal"
    * Exec audience → force "formal" or "balanced"
    * Internal brainstorm with trusted collaborators → "casual"

▸ **Derive ctaRigour**:
  - Based on urgency + stakes + relationshipDepth:
    * High stakes + time pressure → "direct"
    * Decision deadline approaching → "direct"
    * Misalignment risk → "direct"
    * Deal closure moment → "direct"
    * Low stakes + no urgency + relationshipDepth ≤ 2 → "soft"
    * Default → "balanced"

▸ **Output to dialInferenceReport**:
  ```json
  {
    "warmthScore": 6.5,
    "familiarityScore": 5.0,
    "relationshipDepth": 5.75,
    "relationshipDepthMapped": 2,
    "relationshipDepthLabel": "Warm Contact",
    "formality": "balanced",
    "ctaRigour": "balanced",
    "contextOverrides": [],
    "calculationNotes": "First follow-up meeting, shared values mentioned, humor instances: 2"
  }
  ```

▸ **Confidence Check**: If warmth/familiarity signals are ambiguous, prompt user for clarification

Step 4 — Socratic Expansion & Content Confirmation  
▸ Display maps → `/approve maps` to continue.

Step 4B — Iterative Parsing Loop  
▸ `/iterate parsing` merges corrections → rerun 1-3.

Step 5 — Relationship & Style Calibration  
▸ Confirm tone, CTA density, etc.

Step 6 — Apply Master Voice Engine (ENHANCED)
▸ **Load voice calibration from:**
  - `file 'N5/prefs/communication/voice.md'` (consolidated voice schema v3.0.0)
▸ Apply relationshipDepth, formality, ctaRigour from Auto-Dial Inference
▸ **Incorporate Resonant Details** (ENHANCED):
  - Review Resonance Pool from Step 1
  - Select 1-2 highest-confidence resonant details
  - Place in email opening (after greeting, before business content)
  - Use to establish warmth and continuity from conversation
  - Examples:
    * "I really enjoyed hearing about your daughter's career exploration journey!"
    * "I've been thinking about your insight on scaffolded reflection—it really stuck with me."
    * "Still smiling about that 'BS detector' joke—so on-brand for what we're building."
▸ **Incorporate Language Echoing**:
  - Review phrasePool from Step 1B
  - Select max 2 phrases with highest confidence
  - Integrate naturally into recap or CTA sections
▸ **Apply Link Insertion**:
  - Use Link Map from Step 2 (Enhanced)
  - Insert inline Markdown links where confidence ≥ 0.75
  - Insert [[MISSING: category]] markers where confidence < 0.75
▸ **Email Structure** (with Resonant Details):
  1. Greeting (relationship-depth calibrated)
  2. **Resonant Detail** (1-2 sentences, personal connection)
  3. Gratitude or transition
  4. Recap or bullets (business content)
  5. Next Steps / CTAs (max 2)
  6. Warm Sign-Off
▸ **Markdown Formatting**:
  - All links embedded inline: `[anchor text](URL)`
  - Never expose raw URLs
  - Use natural anchor text from context
▸ **Readability Constraints**:
  - FK ≤ 10, avg sentence 16-22 words, max 32 words
  - Max 4 sentences per paragraph
  - Auto-correct violations

Step 6B — Match V's Natural Conciseness
▸ **Purpose**: Generate emails matching V's natural 200-300 word style
▸ **Target**: 200-300 words for standard follow-ups, 300-400 for complex partnerships
▸ **Key Insight**: V's style is already compressed—don't add verbosity that needs cutting
▸ **Reference**: `file 'N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md'`

▸ **Core Principle**: Professional, structured, and concise
  - This is business correspondence, not casual messaging
  - Maintain professional tone throughout
  - Keep bullets with short prose (V's natural format)
  - Use em-dashes extensively (V's signature style)

▸ **What to KEEP**:
  1. **Bullets with Short Prose**: V's preferred format over paragraph exposition
  2. **Em-Dash Format**: "Description — supporting detail" in bullets
  3. **Professional Tone**: Complete sentences, professional language
  4. **Specificity**: Numbers, concrete details, technical terms
  5. **@ Mentions**: For delegation ("@Logan if anything urgent")

▸ **What to CUT**:
  1. **Hedge Phrases**: "essentially", "basically", "in order to", "in a way"
  2. **Redundant Explanations**: Don't repeat the same benefit in different words
  3. **Obvious Statements**: Trust recipient intelligence
  4. **Filler Words**: "would then", "directly", "actual", "really"
  5. **Over-Qualification**: Cut unnecessary modifiers and adjectives
  6. **Formal "What it is:" headers** within use cases (just use title)

▸ **Compression Rules**:
  1. **Opening Paragraph**: 20-40 words (NOT 40-60)
     - Keep warmth and callback
     - Remove redundant politeness
     - Direct transition to business
  
  2. **Use Case Descriptions**: 70-90 words each (NOT 100-120)
     - Title only (no "What it is:")
     - 1-2 sentence description
     - "How it works:" + 3-4 bullets
     - "Why this matters:" 2-3 sentences (paragraph, NOT bullets)
     - "Ready:" and "Needs work:" combined or adjacent
  
  3. **Integration Options**: 30-50 words (NOT 60-80)
     - Short paragraph or 2-3 bullets
     - Remove obvious explanations
  
  4. **Next Steps**: 40-60 words (NOT 60-80)
     - 2-3 action bullets
     - Remove hedging language
  
  5. **Closing**: 10-20 words (NOT 20-30)
     - Concise and warm

▸ **Total Email Target**:
  - Standard follow-up: 200-300 words
  - Complex partnership (2+ use cases): 300-400 words
  - Maximum: 450 words (rare)

▸ **V's Structure Preferences** (from actual emails):
  1. **Greeting:** "Hi [name]," for new/formal, "Hey [name]," or "Hey [name]—" for warm/established
  2. **Opening:** 20-40 words (gratitude + callback)
  3. **Bullets with short prose** (NOT paragraph exposition)
  4. **Em-dash format:** "Item — supporting detail"
  5. **Use case structure:**
     - Title (bold, no "What it is:" header)
     - 1-2 sentence description
     - "How it works:" + 3-4 bullets
     - "Why this matters:" 2-3 sentences (paragraph, NOT bullets)
     - "Ready:" / "Needs work:" combined or adjacent
  6. **@ mentions:** For delegation ("@Logan if anything urgent")
  7. **Closing:** "Best," (default)

Step 6A — Delay Check  
▸ Calculate `daysElapsed`; set optional apology.

Step 7 — Subject Line Generation  
▸ RecipientFirstName = first proper noun after greeting in transcript OR explicit variable if provided.  
▸ Keyword extraction: choose up to 2 high-salience next-step nouns/verbs from CTA list.  
▸ Compose `subjectLine = "Follow-Up Email – <RecipientFirstName> x Careerspan [<kw1> • <kw2> • <kw3>]"`.

Step 7B — Draft Email  
▸ Structure: Greeting → (optional delay apology) → Resonance Intro → Recap bullets → Next-Steps bullets → Sign-off.  
▸ Inline links; no tables/emojis; flag unresolved.

▸ **Greeting Selection** (per V's updated preference):
  - "Hi {{name}}," for new contacts, formal contexts, or when professional distance desired
  - "Hey {{name}}," for established warmth, comfortable relationships
  - "Hey {{name}}—" for warm contexts with em-dash rhythm
  - **Note:** V is intentionally using "Hi" more to maintain formality until warmth is established

Step 8 — Self-Review & Risk Sweep  
▸ Validate formatting, tone, guardrails; ensure subjectLine length ≤ 90 chars.

Step 9 — Output Assembly  
▸ Return: subjectLine • draftEmail • voiceConfigUsed • dialInferenceReport • Missing-Content Map  
  • Link Map • Resonance Pool • SpeakerQuoteMap • revisionHistory • DiffCorrectionLog • daysElapsed

Step 10 — Map-Archive Hook  
▸ Push distilled insights JSON to Map-Archive.

Step 11 — Edge-Case Handling  
▸ Handle missing files, policy breaches, etc.

─────────────────────────────────────────────────────────────────────
5 ▸ COMMANDS
─────────────────────────────────────────────────────────────────────
/approve maps — proceed to Step 5  
/iterate parsing — rerun Steps 1-3 with corrections  
/show diff — display DiffCorrectionLog  
/publish archive — send payload to Map-Archive  
/draft email — bypass Step 5  
/reset — restart function

─────────────────────────────────────────────────────────────────────
6 ▸ OUTPUT OBJECTS
─────────────────────────────────────────────────────────────────────
• subjectLine  
• draftEmail (Markdown format with inline links)
• voiceConfigUsed  
• **dialInferenceReport** (ENHANCED)
• Missing-Content Map  
• **Link Map** (ENHANCED)
• **Missing Links Array**
• **Resonance Pool** (ENHANCED) — Array of resonant details with type, speaker, emotional tone, confidence
  - Format: [{detail_id, type, speaker, content, quote, emotional_tone, confidence, usage}]
• SpeakerQuoteMap  
• **phrasePool**
• DiffCorrectionLog  
• revisionHistory  
• daysElapsed

─────────────────────────────────────────────────────────────────────
7 ▸ FINAL GOAL
─────────────────────────────────────────────────────────────────────
Produce a traditional-format, voice-faithful follow-up email with subject line, resonance color, delay sensitivity, and traceable audit maps — only after user approval.

─────────────────────────────────────────────────────────────────────
◉ END STATE FOOTER (runtime traceability)
─────────────────────────────────────────────────────────────────────
State: {stepID: 13, complete: true, next: null, flags:[voice_passed,audit_passed,user_approved,archive_saved]}  
RuntimeTokenFootprint: auto-logged  
LastEdit: {{timestamp}}  
NuanceSetActive: [NuanceAdvisor, ErrorGuard, AutoInferenceHelper, SocraticExpansion, VoiceSchemaCompliance, DiffAnnotator, MapArchiveHook]  
────────────────────────────────────────────────────────────────────
