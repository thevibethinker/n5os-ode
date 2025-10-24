# Warm Intro Generator - Implementation Plan

**Status:** Planning Phase  
**Date:** 2025-10-22  
**Version:** 1.0

---

## Discovery Summary

### 1. Does a warm intro command exist?
**NO** - No existing warm intro generation command found.

Related commands exist:
- `follow-up-email-generator` (sophisticated email generation with voice calibration)
- `deliverable-generate` (auto-generates meeting deliverables)
- `crm-find` and `crm-query` (CRM lookup tools)

### 2. Where is CRM data stored?
**Location:** `file 'Knowledge/crm/individuals/'`
**Database:** `file 'Knowledge/crm/crm.db'` (57 profiles indexed)
**Query Tool:** `python3 N5/scripts/crm_query_helper.py`

**Current Status:**
- Logan Curry: NOT in CRM (needs profile creation)
- Erica Underwood: NOT in CRM (needs profile creation)
- Camina: NOT in CRM (needs profile creation)
- Bennett Lee: NOT in CRM (needs profile creation)

### 3. Details to Pull
**Primary Source:** B07 WARM_INTRO_BIDIRECTIONAL block
- Who/To Whom/Why Relevant
- Context to Include (bullet points)
- Status (Committed/Tentative)

**Secondary Sources:**
- B01_DETAILED_RECAP.md - Call specifics, quotes
- B08_STAKEHOLDER_INTELLIGENCE.md - Detailed person info
- B21_KEY_MOMENTS.md - Resonant details
- CRM profiles (when available) - Historical context

### 4. Output Formats
**Blurb (Default):** Body text only, no headers
**Forwardable Email (Specify):** Full email with To/From/Subject + body

---

## System Architecture

```
INPUT: B07 block + meeting folder path
  ↓
PROCESS:
  1. Parse B07 → Extract all intros (outbound + inbound)
  2. For each intro:
     a. Query CRM for person profiles
     b. Extract resonant details from B01/B08/B21
     c. Calculate relationship depth (warmth + familiarity scores)
     d. Load voice.md calibration
     e. Generate intro text (blurb or email)
  3. Save outputs to DELIVERABLES/intros/
  ↓
OUTPUT: 
  - Multiple intro files (one per intro)
  - Intro manifest (summary of all generated intros)
```

---

## Technical Components

### A. Core Script: `warm_intro_generator.py`
**Location:** `N5/scripts/warm_intro_generator.py`

**Responsibilities:**
1. Parse B07 block structure
2. Extract intro data (who/whom/why/context/status)
3. Query CRM for profiles
4. Pull resonant details from meeting files
5. Calculate relationship depth (warmth/familiarity)
6. Generate intro text using LLM with voice calibration
7. Output blurb or forwardable email format
8. Save to DELIVERABLES/intros/

**Key Functions:**
- `parse_b07_block(file_path)` → IntroData[]
- `get_crm_profile(name)` → Profile | None
- `extract_resonant_details(meeting_folder, person_name)` → ResonantDetails
- `calculate_relationship_depth(intro_data, meeting_context)` → RelationshipScore
- `generate_intro_text(intro_data, format='blurb')` → str
- `save_intro_output(intro_text, output_path)`

### B. Command: `warm-intro-generate`
**Location:** `N5/commands/warm-intro-generate.md`

**Usage:**
```bash
N5: warm-intro-generate <meeting_folder> [--format blurb|email] [--intro-number N]
```

**Options:**
- `meeting_folder` - Path to meeting folder containing B07 block
- `--format` - Output format: `blurb` (default) or `email` (forwardable)
- `--intro-number` - Generate specific intro only (1-indexed), or all if omitted
- `--dry-run` - Preview without writing files

**Examples:**
```bash
# Generate all intros as blurbs (default)
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee

# Generate all intros as forwardable emails
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee --format email

# Generate only intro #1 (Logan → Bennett)
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee --intro-number 1

# Dry run to preview
N5: warm-intro-generate N5/records/meetings/2025-10-20_external-bennett-lee --dry-run
```

### C. Output Structure
**Directory:** `<meeting_folder>/DELIVERABLES/intros/`

**Files:**
```
DELIVERABLES/intros/
├── 01_logan-curry_to_bennett-lee_blurb.txt
├── 02_erica-underwood_to_bennett-lee_blurb.txt
├── 03_camina_to_bennett-lee_blurb.txt
├── 04_bennett-lee_to_vrijen_blurb.txt
├── 05_bennett-lee_zo-circulation_blurb.txt
└── intros_manifest.md
```

**Manifest Format:**
```markdown
# Warm Intros - Generated 2025-10-22

## Outbound Intros (Vrijen Making)
1. **Logan Curry → Bennett Lee** (Committed)
   - File: `01_logan-curry_to_bennett-lee_blurb.txt`
   - Status: Ready to send
   - Deadline: Within 48 hours

2. **Erica Underwood → Bennett Lee** (Tentative)
   - File: `02_erica-underwood_to_bennett-lee_blurb.txt`
   - Status: Awaiting Erica confirmation
   
...
```

---

## Data Flow

### Input Sources Priority
1. **B07 Block** (structured intro data) - PRIMARY
2. **B08 Stakeholder Intelligence** - Person background
3. **B01 Detailed Recap** - Call specifics, quotes
4. **B21 Key Moments** - Resonant details, emotional moments
5. **CRM Profiles** - Historical context (if exists)
6. **voice.md** - Communication style calibration

### Resonant Details Extraction
From meeting files, extract:
- Personal anecdotes mentioned in call
- Shared values or commonalities
- Humor or inside references
- Specific pain points discussed
- Direct quotes from conversation
- Emotional moments or vulnerability

**Example from Bennett call:**
- "Lazy person who needs strong value prop" (self-description)
- "Stretching that muscle" (GTM focus)
- "Empathetic but pushy" (desired sales style)
- "Over-indexed on building for 1.5 years"
- 10 years teaching CS at USC

### Relationship Depth Calculation
Following `follow-up-email-generator.md` methodology:

**Warmth Score (0-10):** Derived from:
- Personal anecdotes shared
- Humor or emotional engagement
- Shared values mentioned
- Vulnerability displayed

**Familiarity Score (0-10):** Derived from:
- Prior meetings count
- Inside jokes or references
- First-name basis usage
- Shared context depth

**Relationship Depth = (warmth + familiarity) / 2**

Maps to voice.md scale:
- 0-2: Stranger
- 2-4: New Contact
- 4-6: Warm Contact
- 6-8: Partner
- 8-10: Inner Circle

---

## Output Formats

### Format 1: Blurb (Default)
**Characteristics:**
- Body text only, no email headers
- 2-3 paragraphs max
- Casual, conversational tone
- Copy-paste ready
- Includes resonant details from call

**Example Structure:**
```
[Opening: warm greeting + resonant detail]

[Body: why this intro matters, specific context from call, mutual benefit]

[Close: soft CTA or next step]
```

**Sample Blurb:**
```
Hey Bennett! Wanted to connect you with Logan Curry, my co-founder at Careerspan. 

Logan has direct access to Transcend Network, which I know resonated with you during our call. Since your team is "stretching that muscle" on GTM after overbuilding for the last 1.5 years, Transcend's specialized support for ed tech companies could be exactly what you need. They focus on refining go-to-market motion and market understanding—right where you're pivoting now.

Logan can facilitate the intro and give you the lay of the land. Given your technical depth (10 years teaching CS at USC) combined with 50 pilots across K-12 and higher ed, I think Transcend could help you translate that foundation into GTM momentum. Let me know if you want the connection!
```

### Format 2: Forwardable Email
**Characteristics:**
- Full email structure with headers
- To/From/Subject lines
- Slightly more formal than blurb
- Double-opt-in friendly format
- Can be forwarded directly

**Example Structure:**
```
To: [Recipient Email]
From: Vrijen Attawar <vrijen@careerspan.com>
Subject: [Context-driven subject line]

[Opening: personalized greeting]

[Body: intro context, why relevant, specific details from conversation]

[Close: next steps, permission-based]

Best,
Vrijen
```

**Sample Email:**
```
To: logan@careerspan.com
From: Vrijen Attawar <vrijen@careerspan.com>
Subject: Intro to Bennett Lee - Transcend Network Connection

Hey Logan,

Quick intro to Bennett Lee, founder of an AI grading platform I met with yesterday. Technical founder (10 years teaching CS at USC) with strong product but now pivoting to GTM after 1.5 years of overbuilding—sound familiar? 

Bennett has 50 pilots across K-12 and higher ed (USC, UCLA, SoCal universities) and is explicitly seeking GTM support. When I mentioned Transcend Network, it landed hard. He's looking for strategic advisors or founding team additions with sales focus, and knows he needs that "empathetic but pushy" ed sales approach that Transcend specializes in.

Figured you could facilitate a Transcend intro since you're already in that network. He's committed to exploring this (not just browsing), and timing is solid—his team is actively stretching their GTM muscle right now.

Let me know if you want more context before I make the intro!

Best,
Vrijen
```

---

## Integration with Existing Systems

### Leverage `follow-up-email-generator.md` Components
**Reuse:**
- Resonant details extraction (Step 1)
- Relationship depth calculation (Step 3)
- Voice calibration logic (voice.md integration)
- Readability constraints (Flesch-Kincaid, sentence length)
- Link verification (content-library.json)
- Markdown formatting

**Adapt:**
- Target audience = intro recipient (not meeting attendee)
- Purpose = warm intro (not follow-up recap)
- Tone = slightly warmer, relationship-building focus

### CRM Integration
**Query Pattern:**
```python
# Check if profiles exist
logan_profile = crm_query("Logan Curry")
bennett_profile = crm_query("Bennett Lee")

# If missing, extract from B08 or create placeholder
if not logan_profile:
    logan_profile = extract_from_stakeholder_intel(meeting_folder, "Logan Curry")
```

**Data Usage:**
- Pull historical context if CRM profile exists
- Use B08 as fallback source
- Flag missing profiles for future CRM addition

### Deliverable System Integration
**Auto-generation:** Add to `meeting-process` workflow
- After B07 is generated, auto-trigger `warm-intro-generate`
- Save to DELIVERABLES/intros/ alongside other deliverables
- Include in deliverable summary

---

## Implementation Phases

### Phase 1: Core Script (Priority 1)
**Tasks:**
1. Create `warm_intro_generator.py` script
2. Implement B07 parser
3. Implement CRM query integration
4. Implement resonant details extraction
5. Implement LLM-based intro generation
6. Add blurb format output
7. Add forwardable email format output
8. Implement dry-run mode
9. Add error handling (P19)
10. Add state verification (P18)

**Deliverables:**
- `N5/scripts/warm_intro_generator.py`
- Unit tests for B07 parsing
- Sample outputs (blurb + email)

**Estimated Effort:** 2-3 hours

### Phase 2: Command Interface (Priority 2)
**Tasks:**
1. Create `warm-intro-generate.md` command doc
2. Add command to `commands.jsonl`
3. Implement CLI argument parsing
4. Add format selection (blurb/email)
5. Add intro-number filtering
6. Create manifest generator

**Deliverables:**
- `N5/commands/warm-intro-generate.md`
- Command registered in system
- Usage documentation

**Estimated Effort:** 1 hour

### Phase 3: Meeting Workflow Integration (Priority 3)
**Tasks:**
1. Add warm-intro-generate to `meeting-process` workflow
2. Update `deliverable-generate.md` to include intros
3. Add intros to deliverable summary template
4. Test end-to-end meeting processing

**Deliverables:**
- Updated `meeting-process` workflow
- Intros auto-generated with other deliverables

**Estimated Effort:** 1 hour

### Phase 4: CRM Enhancement (Priority 4)
**Tasks:**
1. Create CRM profiles for Logan, Erica, Camina, Bennett
2. Backfill profiles from B08 blocks
3. Update CRM with interaction history

**Deliverables:**
- 4 new CRM profiles
- Updated CRM database

**Estimated Effort:** 30 minutes

---

## Testing Checklist

### Functional Tests
- [ ] Parse B07 block correctly (all intros extracted)
- [ ] Query CRM for existing profiles
- [ ] Extract resonant details from B01/B08/B21
- [ ] Calculate relationship depth accurately
- [ ] Generate blurb format (body text only)
- [ ] Generate email format (full headers + body)
- [ ] Filter by intro number (--intro-number flag)
- [ ] Dry-run mode works (no files written)
- [ ] Handle missing CRM profiles gracefully
- [ ] Handle missing meeting files (B08, B21) gracefully

### Quality Tests
- [ ] Voice calibration matches voice.md
- [ ] Resonant details appropriately included (1-2 per intro)
- [ ] Readability: Flesch-Kincaid ≤ 10
- [ ] Readability: Avg sentence length 16-22 words
- [ ] Readability: Max sentence length ≤ 32 words
- [ ] No fabricated information (P16)
- [ ] All context sourced from meeting files
- [ ] Links verified (if any included)

### Integration Tests
- [ ] Command registered and callable
- [ ] Outputs saved to correct directory
- [ ] Manifest generated correctly
- [ ] Integration with meeting-process workflow

### Principle Compliance
- [ ] P5: Anti-overwrite (files versioned/timestamped)
- [ ] P7: Dry-run available
- [ ] P15: Complete before claiming (all intros generated)
- [ ] P16: No invented facts (all context sourced)
- [ ] P18: State verification (files written successfully)
- [ ] P19: Error handling (graceful failures)

---

## Open Questions

### ✅ RESOLVED (2025-10-22 17:47 ET)

1. **Email Address Sourcing:** ~~Where to get email addresses for To/From fields?~~
   - **RESOLVED:** Don't include To/From addresses. Just address the person and provide core email body.
   
2. **Subject Line Generation:** ~~Formula for subject lines?~~
   - **RESOLVED:** LLM-generated based on intro context (not template-based)

3. **CRM Profile Creation:** ~~Auto-create from B08, or manual?~~
   - **RESOLVED:** Auto-create profiles from B08/meeting context

4. **Intro Prioritization:** ~~Sort order in manifest?~~
   - **RESOLVED:** Sort by importance (default ordering)

---

## Success Criteria

✅ **System generates both blurb and email formats**  
✅ **All context sourced from B07 + meeting files (no fabrication)**  
✅ **Resonant details from call appropriately included**  
✅ **Voice calibration matches established style**  
✅ **Output is copy-paste ready (blurb) or forwardable (email)**  
✅ **Dry-run mode works for preview**  
✅ **Command registered and documented**  
✅ **Integration with meeting-process workflow**  
✅ **Principle-compliant (P5, P7, P15, P16, P18, P19)**

---

## Next Steps

**Immediate (This Session):**
1. Confirm implementation approach with V
2. Clarify open questions (email addresses, subject lines, CRM creation)
3. Get approval to proceed with Phase 1

**Phase 1 Execution:**
1. Create `warm_intro_generator.py` script
2. Test with Bennett meeting B07 block
3. Generate sample outputs (both formats)
4. Review with V for voice calibration accuracy

**Future Sessions:**
1. Complete Phases 2-4
2. Backfill CRM profiles
3. Test end-to-end workflow
4. Deploy to production

---

**Document Status:** ✅ Ready for Review  
**Next Action:** Await V's feedback and clarifications  
**Estimated Total Implementation:** 4-5 hours across phases

