# Follow-Up Email Generation System: Impact Map

**Purpose:** Map all functionality, files, and logic affecting follow-up email text generation  
**Goal:** Optimize writing quality, style, and voice  
**Date:** 2025-10-12 18:07:00 ET

---

## Executive Summary

The follow-up email generation system is a multi-layered pipeline with:
- **1 Master Command** (follow-up-email-generator.md)
- **1 Python Implementation** (follow_up_email_generator.py - basic LLM wrapper)
- **5 Core Voice/Style Files** that define text output
- **3 Reference Documents** for links and constraints
- **Multiple Enhancement Layers** (v11.0: resonance, language echoing, compression)

**Key Finding:** The command file (`.md`) is the actual specification with sophisticated logic. The Python implementation is a basic LLM wrapper that doesn't implement most v11.0 features.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER REQUEST                          │
│         "Generate follow-up email for meeting"           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         COMMAND SPECIFICATION (Master Logic)             │
│   N5/commands/follow-up-email-generator.md (v11.0)      │
│   • 13-step process with enhancement layers              │
│   • Metaprompter v6 compliant                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            VOICE & STYLE LAYER (Input)                   │
│   Defines HOW text should be written                     │
├─────────────────────────────────────────────────────────┤
│ 1. voice.md (v3.0.0) - Master voice specification       │
│ 2. executive-snapshot.md - Quick reference              │
│ 3. templates.md - Structural patterns                   │
│ 4. nuances.md - Fine-tuning toggles                     │
│ 5. essential-links.json - URL references                │
│ 6. EMAIL_GENERATOR_STYLE_CONSTRAINTS.md - Compression   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         IMPLEMENTATION LAYER (Execution)                 │
│   N5/scripts/blocks/follow_up_email_generator.py        │
│   • Basic LLM wrapper                                    │
│   • Does NOT implement v11.0 features                   │
│   • Passes context to generic LLM prompt                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              TEXT GENERATION (LLM)                       │
│   Anthropic Claude or similar                            │
│   • Receives system + user prompt                        │
│   • Generates draft email text                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            OUTPUT (Email Draft)                          │
│   Markdown file with:                                    │
│   • Subject line                                         │
│   • Email body                                           │
│   • Metadata (word count, dial settings)                │
└─────────────────────────────────────────────────────────┘
```

---

## Component Breakdown: Files That Affect Email Text

### 1. MASTER SPECIFICATION (Command)

**File:** `N5/commands/follow-up-email-generator.md` (v11.0.0)

**Impact on Text:** 🔴 CRITICAL - This is the primary logic specification

**Key Features Affecting Text:**
1. **Step 1 - Resonant Details Extraction**
   - Captures personal moments, humor, shared values
   - Types: personal_anecdote, emotional_moment, shared_values, life_context, humor, insight
   - Output: Resonance Pool with confidence scores
   - **Impact:** Creates warm, human opening paragraphs

2. **Step 1B - Transcript Language Echoing**
   - Extracts V's distinctive phrases (2-5 words)
   - Confidence scoring (≥0.75 threshold)
   - Max 2 phrases per email
   - **Impact:** Maintains authentic voice from transcript

3. **Step 2 - Confidence-Based Link Insertion**
   - Matches keywords to essential-links.json
   - Confidence scoring (0.0-1.0)
   - Auto-inserts links when confidence ≥0.75
   - Uses Markdown inline format: `[text](URL)`
   - **Impact:** Professional link formatting

4. **Step 3 - Enhanced Dial Inference**
   - Calculates `warmthScore` (0-10) from conversation signals
   - Calculates `familiarityScore` (0-10) from relationship history
   - Derives `relationshipDepth` = (warmth + familiarity) / 2
   - Maps to formality and CTA rigor
   - **Impact:** Calibrates tone to relationship depth

5. **Step 6 - Master Voice Engine**
   - Applies voice.md settings
   - Incorporates resonant details (1-2 per email)
   - Places in email opening
   - **Impact:** Personal connection in greeting

6. **Step 6B - Compression Pass (MODERATE)**
   - Target: 20-30% reduction (NOT 40-50%)
   - Keeps section headers and bullet structure
   - Removes hedge phrases, redundancy
   - Maintains formal tone
   - **Impact:** Concise but professional style

**Version History:**
- v11.0: Enhanced dial mapping + resonant details
- v10.9: Readability guardrails
- v10.8: Confidence-based link insertion
- v10.7: Transcript language echoing

---

### 2. VOICE SPECIFICATION FILES

#### A. `N5/prefs/communication/voice.md` (v3.0.0)

**Impact on Text:** 🔴 CRITICAL - Defines voice parameters

**Content Affecting Text:**

1. **Relationship Depth Scale (0-4)**
   - 0: Stranger
   - 1: New Contact
   - 2: Warm Contact (baseline for email: 2.0-2.5)
   - 3: Partner
   - 4: Inner Circle

2. **Formality Levels**
   - Casual | Balanced | Formal
   - Default: Balanced
   - Shifts based on context (exec = formal, internal = casual)

3. **CTA Rigor**
   - Soft | Balanced | Direct
   - Default: Balanced
   - Direct for high stakes/time pressure

4. **Tone Weights (0-1 scale)**
   - Warmth: 0.80-0.85 (high warmth, approachable)
   - Confidence: 0.72-0.80 (competent, assured)
   - Humility: 0.55-0.65 (coachable, open) ← **Distinctive**

5. **Writing Guidelines**
   - Flesch-Kincaid: 10-12
   - Avg sentence: 16-22 words
   - Max sentence: 32 words

6. **Lexicon**
   - **Preferred verbs:** surface, distill, scaffold, tighten, instrument, calibrate
   - **Preferred nouns:** yardstick, ledger, brief, rubric, shortlist
   - **Avoid verbs:** get, make, take, go, have, do
   - **Replace:** "leverage" → "use", "reach out" → "get in touch"

7. **Greetings/Sign-offs by Depth**
   - Depth 0-1: "Hi {{name}}," / "Best regards,"
   - Depth 2-3: "Hey {{name}}," / "Warmly,"
   - Depth 4: "Hey {{name}}—" / "Cheers,"

8. **CTA Library**
   - Info Request: "Could you share...?" (Soft)
   - Calendar Invite: "Feel free to grab a slot..." (Soft)
   - Decision Prompt: "Let's decide by {{date}}..." (Balanced/Direct)

**How It's Used:**
- Step 6 (Master Voice Engine) applies these settings
- Step 3 (Dial Inference) references relationship depth scales
- Compression pass uses readability metrics

---

#### B. `N5/prefs/communication/executive-snapshot.md` (v1.0)

**Impact on Text:** 🟡 MODERATE - Quick reference summary

**Content:**
- Voice summary: "Warm, candid, precise"
- Tone weights: Warmth 0.80-0.85, Confidence 0.72-0.80, Humility 0.55-0.65
- Anti-patterns: ambiguous timing, vague asks, overwrought prose

**How It's Used:**
- Quick reference for tone calibration
- Reminder of key voice characteristics

---

#### C. `N5/prefs/communication/templates.md` (v2.0.0)

**Impact on Text:** 🟡 MODERATE - Structural patterns

**Content Affecting Text:**

1. **Email Structure Pattern:**
   ```
   Gratitude → Reiterate outcome → Single concrete ask (owner+when) → Close
   ```

2. **CTA Patterns:**
   - Two-step CTA (primary + fallback)
   - Owner + Date format
   - Max 2 CTAs per message

3. **Opening Lines by Context:**
   - Cold outreach: "I'm [role] at [company]..."
   - Warm follow-up: "Thanks for [specific interaction]..."
   - Status check: "Checking in on [item]..."

4. **Closing Lines by Formality:**
   - Formal: "Best regards," "Thank you,"
   - Balanced: "Best," "Thanks,"
   - Casual: "Cheers," "Talk soon,"

**How It's Used:**
- Step 6 (Master Voice Engine) applies structural patterns
- Step 7B (Draft Email) uses template skeleton

---

#### D. `N5/prefs/communication/nuances.md` (v1.0)

**Impact on Text:** 🟢 LOW - Fine-tuning toggles

**Content:**
- ClarityOverVerbosity: ON
- Reversible-First Decisions: ON
- Evidence-First bias for research
- Rails-not-rules, bad-first-version

**How It's Used:**
- Background preferences for tone
- Not directly mapped to generation logic

---

#### E. `N5/prefs/communication/essential-links.json` (v1.7.0)

**Impact on Text:** 🟡 MODERATE - URL insertion

**Content:**
- Meeting booking links (Calendly)
- Trial codes
- Demos, marketing assets
- Proposals, reports

**How It's Used:**
- Step 2 (Link Autofill) matches keywords to categories
- Confidence-based insertion into email body
- Inline Markdown format

---

### 3. STYLE CONSTRAINT FILES

#### A. `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` (v1.1.0)

**Impact on Text:** 🔴 CRITICAL - Compression rules

**Content Affecting Text:**

1. **Core Principle:** Professional, structured, concise

2. **Moderate Compression Target:** 20-30% reduction (not 40-50%)

3. **What to KEEP:**
   - Section headers ("What it is / How it works / Why it matters")
   - Bullet points (4-5 per section is fine)
   - Professional structure
   - Formal tone
   - Complete sentences

4. **What to CUT:**
   - Hedge phrases: "essentially", "basically", "in order to"
   - Redundant explanations
   - Obvious statements
   - Filler words: "would then", "directly", "actual"

5. **Target Metrics:**
   - Opening: 40-60 words
   - Use case: 100-120 words each
   - Integration options: 60-80 words
   - Next steps: 60-80 words
   - Closing: 20-30 words
   - **Total: 400-550 words**

6. **Sentence Constraints:**
   - Average: 16-20 words
   - Max: 30 words

**How It's Used:**
- Step 6B (Compression Pass) applies these rules
- Validation against word count targets

---

### 4. IMPLEMENTATION (Python)

**File:** `N5/scripts/blocks/follow_up_email_generator.py`

**Impact on Text:** 🟡 MODERATE - But doesn't implement v11.0 features

**Current Implementation:**
```python
system_prompt = """You are an expert at writing professional follow-up emails.

Context:
- Meeting type: {meeting_type_str}
- Relationship stage: {relationship_stage}

Write email that:
1. Thanks them
2. Recaps key points
3. Confirms next steps
4. Maintains appropriate tone
5. Is concise and actionable
"""
```

**What's Missing:**
- ❌ Resonant details extraction
- ❌ Language echoing
- ❌ Confidence-based link insertion
- ❌ Enhanced dial inference (warmth/familiarity scoring)
- ❌ Compression pass logic
- ❌ Readability validation

**What It Does:**
- ✅ Passes basic context to LLM
- ✅ Reads action items and decisions
- ✅ Determines relationship stage (new/developing/established)
- ✅ Formats output as markdown

---

## Text Generation Pipeline: Step-by-Step

### INPUT STAGE

**Sources:**
1. Meeting transcript (raw text)
2. Meeting metadata (date, participants, stakeholder)
3. Meeting history (previous meetings with stakeholder)
4. Email history (optional - previous exchanges)
5. Action items file (if exists)
6. Decisions file (if exists)

### PROCESSING STAGE

**Step 1: Extract Resonant Details** [v11.0 feature]
- Scan transcript for personal moments
- Build Resonance Pool with confidence scores
- Select 1-2 highest-confidence details for opening

**Step 1B: Extract Language Patterns** [v11.0 feature]
- Scan Vrijen's turns for distinctive phrases
- Score phrases (≥0.75 threshold)
- Select max 2 for incorporation

**Step 2: Match Links** [v11.0 feature]
- Scan for keywords (calendly, schedule, demo, etc.)
- Match against essential-links.json
- Assign confidence scores
- Auto-insert if ≥0.75, else mark [[MISSING: category]]

**Step 3: Calculate Relationship Dials** [v11.0 feature]
- Calculate warmthScore (0-10) from conversation signals
- Calculate familiarityScore (0-10) from history
- Derive relationshipDepth = (warmth + familiarity) / 2
- Map to formality and CTA rigor

**Step 4: Socratic Confirmation** [Interactive]
- Display maps to user
- User approves or requests iteration

**Step 5: Calibration Confirmation** [Interactive]
- Confirm tone, CTA density
- User approves settings

**Step 6: Apply Voice Engine**
- Load voice.md settings
- Apply relationshipDepth → formality mapping
- Incorporate resonant details in opening
- Incorporate language patterns in recap/CTA
- Insert links (inline Markdown)
- Structure email: Greeting → Resonance → Gratitude → Recap → CTAs → Sign-off

**Step 6B: Compression Pass**
- Apply EMAIL_GENERATOR_STYLE_CONSTRAINTS.md rules
- Target 20-30% reduction
- Keep structure, remove redundancy
- Validate against word count targets

**Step 7: Generate Subject Line**
- Extract recipient first name
- Extract 2-3 keywords from CTAs
- Format: "Follow-Up Email – {{FirstName}} x Careerspan [kw1 • kw2]"

**Step 7B: Draft Email**
- Apply all settings
- Generate markdown output

**Step 8: Self-Review**
- Validate formatting
- Check subject line ≤90 chars
- Verify readability metrics

### OUTPUT STAGE

**Generated Files:**
1. Email draft (markdown)
   - Subject line
   - Body text
   - Signature
2. Metadata report
   - Word count by section
   - Dial settings used
   - Compression details
   - Resonant details used
   - Links inserted
   - Readability metrics

---

## Quality Control: What Affects Writing Quality

### 1. VOICE CONSISTENCY

**Controlled By:**
- `voice.md` → Tone weights (warmth 0.80-0.85, humility 0.55-0.65)
- `voice.md` → Lexicon (preferred/avoid verbs)
- Step 1B → Language echoing (V's distinctive phrases)

**Tuning Opportunities:**
- Adjust tone weight ranges
- Expand lexicon lists
- Improve phrase extraction confidence scoring

---

### 2. RELATIONSHIP CALIBRATION

**Controlled By:**
- Step 3 → Dial inference (warmth/familiarity calculation)
- `voice.md` → Relationship depth scale (0-4)
- `voice.md` → Formality mapping

**Tuning Opportunities:**
- Refine warmth scoring algorithm (what signals = warmth?)
- Adjust familiarity scoring (weight of prior meetings)
- Test edge cases (high warmth but first meeting)

---

### 3. STRUCTURAL QUALITY

**Controlled By:**
- `templates.md` → Email skeleton (Gratitude → Recap → CTAs → Close)
- `EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` → Section structure rules
- Step 6 → Master Voice Engine (structure application)

**Tuning Opportunities:**
- Test alternative structures for different contexts
- Refine section ordering
- Optimize bullet vs. prose decisions

---

### 4. CONCISENESS

**Controlled By:**
- `EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` → Compression targets (20-30%)
- `EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` → Word count targets per section
- Step 6B → Compression pass

**Tuning Opportunities:**
- Adjust target word counts
- Refine "what to cut" vs. "what to keep" rules
- Test compression at different relationship depths

---

### 5. READABILITY

**Controlled By:**
- `voice.md` → Readability metrics (FK 10-12, avg 16-22 words)
- Step 6 → Sentence length validation
- Step 6B → Auto-correction for violations

**Tuning Opportunities:**
- Adjust FK target
- Refine sentence splitting logic
- Test paragraph constraints

---

### 6. PERSONALIZATION

**Controlled By:**
- Step 1 → Resonant details extraction
- Step 1 → Resonance Pool (types, confidence scoring)
- Step 6 → Resonant detail placement (email opening)

**Tuning Opportunities:**
- Expand resonance types
- Refine confidence scoring
- Test placement strategies (opening vs. closing)

---

## Priority Areas for Tuning

### 🔴 HIGH IMPACT: Voice Files

**Files to Tune:**
1. `N5/prefs/communication/voice.md` (v3.0.0)
2. `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` (v1.1.0)

**Why:**
- These are directly referenced by generation logic
- Changes here affect all email outputs
- Well-structured for tuning (clear sections, numeric targets)

**What to Tune:**
- Tone weights (warmth, confidence, humility)
- Lexicon (expand preferred/avoid lists)
- Readability targets (FK grade, sentence length)
- Compression targets (word counts per section)
- Relationship depth mappings

---

### 🟡 MEDIUM IMPACT: Command Logic

**Files to Tune:**
1. `N5/commands/follow-up-email-generator.md` (v11.0.0)

**Why:**
- This is the master specification
- Defines all enhancement logic (resonance, language echoing, dial inference)

**What to Tune:**
- Resonance extraction logic (what counts as "resonant"?)
- Language echoing confidence thresholds
- Warmth/familiarity scoring algorithms
- Link insertion confidence thresholds
- Compression pass rules

---

### 🟢 LOW IMPACT (But Important): Templates & Nuances

**Files to Tune:**
1. `N5/prefs/communication/templates.md` (v2.0.0)
2. `N5/prefs/communication/nuances.md` (v1.0)

**Why:**
- Provide structural patterns
- Fine-tuning toggles

**What to Tune:**
- CTA patterns
- Opening/closing variations
- Context-specific templates

---

## Implementation Gap Analysis

### What v11.0 Specifies vs. What Python Implements

| Feature | v11.0 Spec | Python Implementation | Gap |
|---------|------------|----------------------|-----|
| Resonant details extraction | ✅ Step 1 | ❌ Not implemented | **HIGH** |
| Language echoing | ✅ Step 1B | ❌ Not implemented | **HIGH** |
| Confidence-based links | ✅ Step 2 | ❌ Not implemented | **HIGH** |
| Enhanced dial inference | ✅ Step 3 | ⚠️ Basic (3 stages) | **MEDIUM** |
| Voice engine application | ✅ Step 6 | ⚠️ Generic prompt | **HIGH** |
| Compression pass | ✅ Step 6B | ❌ Not implemented | **MEDIUM** |
| Readability validation | ✅ Step 6 | ❌ Not implemented | **LOW** |
| Subject line generation | ✅ Step 7 | ⚠️ Basic format | **LOW** |

**Recommendation:**
The Python implementation is a placeholder. The real logic is in the command file. To tune the system, you should:
1. **Focus on tuning the voice/style files** (they affect LLM prompt context)
2. **Refine the command specification** (v11.0 logic)
3. **Consider whether to implement v11.0 features in Python** or rely on LLM prompt engineering

---

## Tuning Workflow Recommendations

### Phase 1: Voice File Optimization (Quick Wins)

**Goal:** Improve writing quality by refining voice parameters

**Steps:**
1. Review example outputs (like Hamoon email)
2. Identify style issues (too formal? too casual? wrong tone?)
3. Adjust voice.md parameters:
   - Tone weights
   - Lexicon preferences
   - Readability targets
4. Test with same transcript, compare outputs

**Files to Edit:**
- `N5/prefs/communication/voice.md`
- `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md`

---

### Phase 2: Resonance & Personalization (Medium Effort)

**Goal:** Improve warmth and human connection

**Steps:**
1. Refine resonance extraction logic in command file
2. Test resonance confidence scoring
3. Experiment with placement (opening vs. closing)
4. Validate with stakeholder feedback

**Files to Edit:**
- `N5/commands/follow-up-email-generator.md` (Step 1)

---

### Phase 3: Compression & Conciseness (Medium Effort)

**Goal:** Optimize word count without losing professionalism

**Steps:**
1. Review compression rules in EMAIL_GENERATOR_STYLE_CONSTRAINTS.md
2. Test different target percentages (20%, 25%, 30%)
3. Compare outputs for clarity and tone
4. Adjust "what to cut" vs. "what to keep" rules

**Files to Edit:**
- `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md`

---

### Phase 4: Implementation Parity (High Effort)

**Goal:** Implement v11.0 features in Python

**Steps:**
1. Implement resonance extraction
2. Implement language echoing
3. Implement confidence-based link insertion
4. Implement enhanced dial inference
5. Implement compression pass
6. Test end-to-end

**Files to Edit:**
- `N5/scripts/blocks/follow_up_email_generator.py`
- Create new modules for each feature

---

## File Dependency Graph

```
USER REQUEST
    │
    ▼
N5/commands/follow-up-email-generator.md (v11.0)
    ├─→ N5/prefs/communication/voice.md (CRITICAL)
    │   └─→ Tone weights, lexicon, readability
    │
    ├─→ N5/prefs/communication/essential-links.json
    │   └─→ URL references for link insertion
    │
    ├─→ N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md (CRITICAL)
    │   └─→ Compression rules, word count targets
    │
    ├─→ N5/prefs/communication/templates.md
    │   └─→ Structural patterns
    │
    ├─→ N5/prefs/communication/executive-snapshot.md
    │   └─→ Quick reference
    │
    └─→ N5/prefs/communication/nuances.md
        └─→ Fine-tuning toggles
    │
    ▼
N5/scripts/blocks/follow_up_email_generator.py
    ├─→ LLM client
    └─→ Output formatting
    │
    ▼
EMAIL DRAFT OUTPUT
```

---

## Next Steps for Tuning

### Immediate Actions (Today)

1. **Review Hamoon email output** (test case provided)
   - What's working well?
   - What feels off?
   - Specific style issues?

2. **Identify 3-5 specific improvements** you want
   - Example: "Too formal for warm contacts"
   - Example: "Opening lacks personal touch"
   - Example: "Too verbose in use case descriptions"

3. **Map improvements to files**
   - Which voice parameters need adjustment?
   - Which compression rules need refinement?

### Short-Term (This Week)

1. **Tune voice.md**
   - Adjust tone weights if needed
   - Expand lexicon (preferred/avoid verbs)
   - Refine readability targets

2. **Tune EMAIL_GENERATOR_STYLE_CONSTRAINTS.md**
   - Adjust word count targets per section
   - Refine "what to cut" vs. "what to keep"
   - Test compression percentages

3. **Test with multiple transcripts**
   - Different relationship depths
   - Different meeting types
   - Compare outputs

### Medium-Term (Next 2 Weeks)

1. **Refine command specification**
   - Improve resonance extraction logic
   - Enhance dial inference algorithms
   - Test link insertion confidence thresholds

2. **Build feedback loop**
   - Track stakeholder responses to emails
   - Identify patterns in successful vs. unsuccessful emails
   - Iteratively tune parameters

3. **Consider implementation parity**
   - Decide whether to implement v11.0 in Python
   - Or rely on prompt engineering with command spec

---

## Summary: Critical Files for Voice Tuning

| File | Priority | What It Controls | Ease of Tuning |
|------|----------|------------------|----------------|
| `N5/prefs/communication/voice.md` | 🔴 CRITICAL | Tone, lexicon, readability, structure | ⭐⭐⭐ Easy |
| `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` | 🔴 CRITICAL | Compression, word counts, what to cut | ⭐⭐⭐ Easy |
| `N5/commands/follow-up-email-generator.md` | 🟡 MEDIUM | Logic, algorithms, enhancement layers | ⭐⭐ Medium |
| `N5/prefs/communication/templates.md` | 🟢 LOW | Structural patterns, CTAs | ⭐⭐⭐ Easy |
| `N5/prefs/communication/essential-links.json` | 🟢 LOW | URL references | ⭐⭐⭐ Easy |
| `N5/scripts/blocks/follow_up_email_generator.py` | 🟡 MEDIUM | Implementation (but basic) | ⭐ Hard |

---

**Recommendation:** Start with tuning the two CRITICAL files. They're easy to edit, well-structured, and have immediate impact on output quality.

---

*Generated: 2025-10-12 18:07:00 ET*
