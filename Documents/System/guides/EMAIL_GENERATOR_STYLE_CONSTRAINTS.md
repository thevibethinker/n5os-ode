# Email Generator Style Constraints

**Version:** 1.1.0  
**Date:** 2025-10-12  
**Purpose:** Style guidelines for follow-up email generation

---

## Core Principle

**Professional, structured, and concise.**

V's emails are well-organized with clear sections, but economical with words. Maintain formal structure while cutting unnecessary elaboration.

---

## Writing Style Rules

### 1. **Natural Compression (V's Baseline)**

**Target:** Match V's natural style = 200-300 words for standard follow-ups

**V's style is ALREADY compressed.** No need for aggressive compression—just match his natural conciseness:
- Remove redundant sentences, not entire structures
- Keep bullets and short prose
- Maintain professional tone
- Remove hedge phrases and filler words
- Keep specificity (numbers, details)

**Compression from verbose baseline:** 50-60% reduction  
**But this is NOT aggressive**—it's V's natural voice.

**Key insight:** V writes concisely by default. Don't add verbosity that needs compression.

### 2. **Bullets with Short Prose (V's Natural Format)**

V's actual structure:
- **Use case title** (bold, no "What it is:" header)
- 1-2 sentence description
- "How it works:" + 3-4 bullets (em-dash format: "Item — detail")
- "Why this matters:" Single paragraph (2-3 sentences), NOT bullets
- "Ready:" [list] and "Needs work:" [brief note] on same or adjacent lines

**Avoid:**
- Formal "What it is / How it works / Why it matters" section headers WITHIN use cases
- Paragraph exposition where bullets work better
- More than 4 bullets per section

**Key:** Bullets with short prose > paragraph exposition

**Natural Flow (Avoid Over-Scaffolding):**
- Don't over-label sections with explicit "Why this matters:" headers (can feel condescending)
- Let benefits flow naturally after technical description
- Use headers sparingly—only when needed for scannability
- Balance: Maintain structure but avoid pedagogical tone

**Example:**

Too scaffolded:
```
**What it is:** [description]
**How it works:** [bullets]
**Why this matters:** [benefits]
```

More natural (PREFERRED):
```
**[Title]**

[1-2 sentence description]

**How it works:** [bullets]

[Benefits stated directly without label—flows naturally from description]
```

### 3. **Smart Bullet Usage**
- Keep bullets for multi-step processes
- Keep bullets for feature lists
- 4-5 bullets per section is fine if information-dense
- Don't force inline text if bullets are clearer

### 4. **Remove Redundancy, Not Structure**
- Cut repeated benefit statements
- Remove obvious explanations
- Eliminate hedge phrases ("essentially", "basically")
- But keep section headers and formal structure

### 5. **Voice Principles**
- Maintain professional formality
- Keep specificity (numbers, concrete details)
- Use colloquialisms sparingly
- This is business correspondence, not casual messaging

### 6. **Em-Dash Usage (V's Signature)**

V uses em-dashes (—) extensively:

**In bullets:**
```
- Kamina Singh intro — She's been instrumental in getting us into universities
- Career/HR tech founder roundtable — You'll love this crew
```

**In prose:**
```
"Apologies for the radio silence — interacting with talent leads like yourself gave us a lot of food for thought as far as our strategy is concerned."
```

**After greetings (warm contexts):**
```
"Hey Mark—"
"Hey Hilary—"
```

**Rule:** Use em-dash liberally where others would use commas, colons, or parentheses. This creates V's distinctive rhythm.

---

## Before/After Examples

### BAD (Too Verbose - Original)
```
**What it is:** A 5-8 minute conversational AI flow embedded directly in 
FutureFit's platform that helps users articulate their career story, 
values, and strengths in a structured but flexible way that allows for 
organic exploration while maintaining data consistency.

**How it works:**
- FutureFit would pass basic candidate data (resume, target role) via our API
- The user would then engage with Careerspan's conversational interface 
  (iframe embed or white-labeled widget)
- We would return a structured profile containing 100+ data points across 
  biographical facts, soft skills, values, mindset, and work style preferences
- The user would then continue in FutureFit platform with their enriched 
  profile—maintaining a seamless experience with no navigation friction

**Why this matters for FutureFit:**
- This directly addresses the gap between basic profiling and actionable 
  candidate insights that hiring managers can actually use
- It gives your 200K users access to deeper self-articulation capabilities 
  without requiring you to build this sophisticated tech in-house
- The data schema we provide can feed directly into your existing career 
  pathways, job matching algorithms, or training recommendations
```

### GOOD (Moderate Compression - Target)
```
**What it is:** A 5-8 minute conversational AI flow embedded in FutureFit's 
platform that helps users articulate their career story, values, and strengths.

**How it works:**
- FutureFit passes basic candidate data (resume, target role) via API
- User engages with Careerspan's conversational interface (iframe embed or 
  white-labeled widget)
- We return structured profile: 100+ data points across biographical facts, 
  soft skills, values, mindset, work style preferences
- User continues in FutureFit platform with enriched profile—no navigation friction

**Why this matters for FutureFit:**
- Addresses the gap between basic profiling and actionable candidate insights
- Gives your 200K users deeper self-articulation without building this tech in-house
- Data schema can feed your existing career pathways, job matching, or training 
  recommendations
```

### TOO TIGHT (Over-Compressed - Avoid)
```
5-8 minute conversational flow embedded in FutureFit. Users articulate 
career story, values, strengths. We return 100+ structured data points. 
Feeds your pathways/matching without building in-house.
```

**Word count:** 150 → 110 (-27%) → 35 (-77%)  
**Target:** Middle version (110 words, -27%)

---

## Target Metrics (REVISED)

### Word Count Targets (V's Natural Style)

**V's actual emails: 200-300 words (NOT 400-550)**

**Targets:**
- **Opening paragraph:** 20-40 words (NOT 40-60)
- **Use case description:** 70-90 words each (NOT 100-120)
- **Integration options:** 30-50 words total (NOT 60-80)
- **Next steps:** 40-60 words (NOT 60-80)
- **Closing:** 10-20 words (NOT 20-30)

**Total email target:**
- **Standard follow-up:** 200-300 words
- **Complex partnership (2+ use cases):** 300-400 words
- **Maximum:** 450 words (rare, only for dense technical content)

**Rationale:** V's actual follow-up emails are 40-50% shorter than current AI outputs. This reflects his natural, already-compressed style.

### Sentence Constraints
- **Average:** 16-20 words (not 18-24)
- **Max:** 30 words (not 35+)
- **Prefer:** Clear declarative sentences

### Paragraph Constraints
- **Max sentences per paragraph:** 3-4 sentences
- **Keep:** Structured sections with headers
- **Keep:** Bullet points where appropriate

---

## Operational Integration

### v11.0 Generator Updates Needed

1. **Step 6B (Compression Pass):**
   - Target 20-30% word count reduction (not 40-50%)
   - **Keep** "What it is / How it works / Why it matters" structure
   - **Keep** bullet points for processes and lists
   - **Remove** redundant explanations and hedge phrases
   - **Maintain** professional formal tone

2. **What to Cut:**
   - Redundant benefit statements
   - Hedge phrases ("essentially", "basically", "in order to")
   - Obvious explanations
   - Repetitive phrasing

3. **What to KEEP:**
   - Section headers
   - Bullet points (4-5 per section is fine)
   - Professional structure
   - Formal tone
   - Complete sentences

---

## Quick Compression Checklist

Before finalizing any email, run this checklist:

- [ ] Is each section 20-30% tighter without losing clarity?
- [ ] Are there redundant benefit statements to cut?
- [ ] Can any hedge phrases be removed?
- [ ] Is the professional structure maintained?
- [ ] Does it still sound formal, not casual?
- [ ] Is total word count 400-550?
- [ ] Would this work as-is in a business context?

---

## Key Principle

**Moderate compression, not aggressive compression.**

The goal is a well-structured, professional email that respects the recipient's time—not a casual text message.

---

---

## Implementation Status

**Command File Integration:** ✅ COMPLETE
- **File:** `N5/commands/follow-up-email-generator.md` (v11.0)
- **Location:** Step 6B — Compression Pass
- **Status:** All style constraints fully integrated
- **Last updated:** 2025-10-09

**Python Script:** ❌ DELETED (2025-10-12)
- **Reason:** Maintained single source of truth (SSOT)
- **Backup:** `N5/scripts/blocks/_ARCHIVE_follow_up_email_generator.py.backup-20251012`
- **See:** `file 'N5/docs/EMAIL-GENERATOR-REFACTOR-COMPLETE.md'`

**Deliverable Orchestrator:** ✅ REFACTORED
- **File:** `N5/scripts/generate_deliverables.py`
- **Status:** References command file (SSOT)
- **Workflow:** Creates placeholder → user invokes command

**Architecture:** Single Source of Truth ✅
- All email generation uses command file
- Style constraints always applied
- No duplication or risk of divergence

---

*Updated: 2025-10-12 22:55 ET*
