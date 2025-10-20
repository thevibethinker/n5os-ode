# `meeting-process`

**Version**: 5.1.0\
**Category**: Meeting Intelligence\
**Workflow**: AI-Driven Processing (Guidance-Based)\
**Registry Version**: 1.5+\
**Philosophy**: Natural language guidance, contextual intelligence, strategic depth, CRM integration, Howie harmonization

---

## Purpose

Process meeting transcripts into structured, strategically valuable intelligence blocks. Each block should provide actionable insight, not just information extraction. You are transforming raw conversation into decision-support tools with integrated CRM enrichment and Howie scheduling harmonization.

---

## Core Principles

### 1. **Strategic Depth Over Rigid Formatting**

- Don't just extract - interpret and contextualize
- Ask yourself: "How does this help Vrijen make better decisions?"
- Include narrative sections when they add value (Strategic Context, Critical Next Action, etc.)
- Balance structure with intelligence

### 2. **Proactive Value Generation**

- Generate useful content even when not explicitly "requested" in transcript
- Example: Create messaging blurbs after founder meetings even if no intro was promised
- Example: Identify implicit questions and tensions even if not verbalized
- Your job is to surface what's strategically important, not just what was said

### 3. **Contextual Intelligence**

- Use the guidance principles in the registry as starting points, not rigid templates
- Adapt based on the meeting context - founder meeting vs. investor pitch vs. networking call
- Add sections, structure, or analysis when it makes the output more useful
- Follow the spirit of each block's purpose, not just the letter of the guidance

### 4. **No Placeholders or Invented Content**

- Extract from the transcript, don't simulate
- If information isn't present, note it as "\[Unknown\]" or omit the field
- Never copy placeholder text from guidance (like "\[specific outcome with context\]")
- Real content only

### 5. **CRM & Howie Integration** ⭐ NEW in v5.1

- Auto-create CRM profiles for FOUNDER, INVESTOR, CUSTOMER, COMMUNITY, NETWORKING stakeholders
- Skip CRM for JOB_SEEKER (recruitment workflow)
- Generate Howie V-OS tag recommendations for ALL stakeholders for future scheduling
- Mark enrichment priorities (HIGH/MEDIUM/LOW) based on deal stage and relationship
- LinkedIn enrichment is READ-ONLY (never post, message, or interact)

---

## Processing Steps

### Step 1: Load the Registry

Load `file N5/prefs/block_type_registry.json`  (v1.5 or later).

This registry defines:

- **All available blocks** with guidance principles
- **Stakeholder combinations** (which blocks for which meeting types)
- **Priority levels** (REQUIRED, HIGH, CONDITIONAL)
- **Output order** (how to sequence the blocks)

The registry provides **guidance, not templates**. Use your intelligence to create high-quality outputs.

**v1.5 Changes:**

- 15 blocks total (down from 19)
- B08 now includes CRM + Howie integration
- B21 combines quotes + questions
- B25 includes follow-up email generation
- B31 is NEW (stakeholder research/landscape insights)

---

### Step 2: Analyze the Transcript

Read the full transcript and determine:

1. **Stakeholder Type**: Who is this meeting with?

   - FOUNDER: Exploring partnership/collaboration with another founder
   - INVESTOR: Fundraising or investor relationship
   - NETWORKING: General networking, informational
   - CUSTOMER: User research, sales meeting, customer discovery
   - COMMUNITY: Alumni group, professional community, network partner
   - CANDIDATE: Individual job seeker (skip CRM, use recruitment workflow)
   - (If unclear, use best judgment)

2. **Meeting Dynamics**: What was the vibe?

   - Strategic depth (exploratory, detailed, ready to act)?
   - Energy level (enthusiastic, reserved, tense)?
   - Decision made or still exploring?

3. **Content Triggers**: What blocks are relevant?

   - Were 3+ substantive metrics discussed? (→ B11)
   - Pilot details? (→ B06)
   - Warm intros promised? (→ B07, B14)
   - Product ideas surfaced? (→ B24)
   - Complex plan emerging? (→ B13)
   - Partnership/deal signals? (→ momentum section in B13)

---

### Step 3: Select Blocks to Generate

Use this 3-tier logic:

#### Tier 1: REQUIRED Blocks (Always Generate)

- **B26** - Meeting Metadata Summary (includes V-OS tags)
- **B01** - Detailed Recap
- **B02** - Commitments Contextual (action items - elevated to REQUIRED in v1.5)
- **B08** - Stakeholder Intelligence (profile + resonance + CRM + Howie)
- **B21** - Key Moments (quotes + questions merged in v1.5)
- **B31** - Stakeholder Research (landscape insights - NEW in v1.5)
- **B25** - Deliverable Content Map + Follow-Up Email

**Total: 7 REQUIRED blocks** (always generate these)

#### Tier 2: Stakeholder-Specific HIGH Priority

Consult `stakeholder_combinations` in registry for the detected stakeholder type.

**FOUNDER** meetings (13 blocks total):

- B26, B01, B02, B08, B21, B31, B25 (required)
- B05, B24, B13, B07, B14, B27 (high priority)

**INVESTOR** meetings (11 blocks total):

- B26, B01, B02, B08, B21, B31, B25 (required)
- B05, B13, B07, B27 (high priority)

**NETWORKING** meetings (9 blocks total):

- B26, B01, B02, B08, B21, B31, B25 (required)
- B07, B05 (high priority)

**CUSTOMER** meetings (11 blocks total):

- B26, B01, B02, B08, B21, B31, B25 (required)
- B24, B05, B13, B27 (high priority)

**COMMUNITY** meetings (9 blocks total):

- B26, B01, B02, B08, B21, B31, B25 (required)
- B05, B07 (high priority)

#### Tier 3: CONDITIONAL Blocks

Generate these ONLY when explicitly triggered:

- **B06** (Pilot Intelligence): Only if pilot was explicitly discussed with specifics
- **B11** (Metrics Snapshot): Only if 3+ substantive metrics were discussed
- **B15** (Stakeholder Map): Only if multiple stakeholders with complex dynamics

---

### Step 4: Generate Each Block

For each selected block:

1. **Read the guidance principles** in the registry for that block
2. **Apply contextual intelligence** - don't follow guidance robotically
3. **Add structure as needed** - sections, tables, bullet formats that enhance clarity
4. **Extract with depth** - include context, rationale, strategic implications
5. **Make it actionable** - how does this help Vrijen act on the information?

---

## Block-Specific Guidance (v1.5 Updates)

### B01 - DETAILED_RECAP ✅ REQUIRED

- Structure with 3 sections: "Key Decisions and Agreements" + "Strategic Context" + "Critical Next Action"
- Each decision bullet: specific outcome + why it matters + rationale
- Strategic Context: narrative about positioning, pain points, competitive landscape
- Critical Next Action: Owner, Deliverable, Timeline, Purpose (make it crystal clear)
- This is your most important block - invest time in quality

### B02 - COMMITMENTS_CONTEXTUAL ✅ REQUIRED (elevated in v1.5)

- Table format: Owner | Deliverable | Context/Why | Due Date | Dependencies
- Owner classification: "We" (Vrijen/team) vs. their name
- If no action items: note "No explicit action items or commitments discussed"
- This is now REQUIRED because action items are critical for every meeting

### B08 - STAKEHOLDER_INTELLIGENCE ✅ REQUIRED (major enhancement in v1.5)

**Four Sections:**

**1. FOUNDATIONAL PROFILE** (replaces old B28)

- Company/Organization, Product/Service, Motivation, Funding Status, Key Challenges, Standout Quote
- Make it comprehensive enough to brief someone who's never met them

**2. WHAT RESONATED** (old B08 content)

- 3-5 moments of genuine enthusiasm, energy, or strong reaction
- For each: quote + why it resonated + what it signals
- Balance positives with negatives (concerns, hesitations)

**3. CRM INTEGRATION** ⭐ NEW

- **Auto-create profile** for: FOUNDER, INVESTOR, CUSTOMER, COMMUNITY, NETWORKING
- **Skip for**: JOB_SEEKER (goes to recruitment workflow)
- Profile path: `file Knowledge/crm/individuals/[firstname-lastname].md` 
- Status: Note if profile was created
- Mutual Acquaintances: List if identified, mark \[None identified - needs enrichment\]
- **Enrichment Priority**: 
  - HIGH = active partnership/investment discussion
  - MEDIUM = warm contact, potential future value
  - LOW = networking contact, no immediate follow-up
- **Next Actions**: 2-3 enrichment tasks (LinkedIn research, company research, mutual connections)

**4. HOWIE INTEGRATION** ⭐ NEW

- **Recommended V-OS Tags** for future Howie scheduling
- Format: `[LD-XXX] [GPT-X] [A-X]`
- Tag categories: 
  - **LD** (Lead type): INV (investor), NET (networking), COM (community), CUS (customer), FND (founder)
  - **GPT** (Goal/Phase/Timeline): E (exploratory), M (mid-stage), C (critical/closing)
  - **A** (Accommodation level): 1 (rigid), 2 (flexible), 3 (accommodating), 4 (highly flexible)
- **Rationale**: Explain why each tag applies
- **Priority**: Critical / Important / Non-critical
- Generate for ALL stakeholders prophylactically

### B21 - KEY_MOMENTS ✅ REQUIRED (merged B29 + B21 in v1.5)

**Two Sections:**

**1. MEMORABLE QUOTES**

- 3-5 most impactful verbatim quotes
- For each: Quote + Who said it + When + Context (why it mattered, what it reveals)
- Good quotes reveal values, show enthusiasm, express concerns, provide insights

**2. SALIENT QUESTIONS**

- 3-5 most strategically important questions (asked or implied)
- For each: Question + Why it matters + Who asked + Action hint
- Action hints should be SPECIFIC: "Demo the hiring manager AI" not "follow up"
- Prioritize strategic implications over tactical clarifications

### B31 - STAKEHOLDER_RESEARCH ✅ REQUIRED (NEW in v1.5)

**Purpose:** Capture landscape insights - intelligence about the WORLD, not just about THEM

**What to Extract:**

- When they speak for their **ORGANIZATION**: strategy, priorities, internal challenges, decision-making
- When they speak for their **INDUSTRY**: trends, competitive dynamics, emerging patterns, market shifts
- When they speak as **STAKEHOLDER TYPE**: what they care about, decision criteria, common objections, patterns

**Structure:**

- Perspective: Speaking as \[career tech founder / early-stage investor / etc\]
- 3-5 key insights per meeting
- For each: Observation + Implication + Strategic Value

**Focus on Non-Obvious Info:**

- Things you couldn't get from Google
- Inside perspective on how decisions are made
- Unwritten rules or hidden dynamics
- Emerging trends not yet widely known

**Examples:**

- "Most career platforms getting acquired" → Window for independent players narrowing
- "Integration tax is brutal" → Being data layer more defensible than platform
- "Series A valuations compressed 40%" → Need stronger traction for funding

### B25 - DELIVERABLE_CONTENT_MAP + FOLLOW-UP EMAIL ✅ REQUIRED (dual-purpose in v1.5)

**Section 1: Deliverable Content Map (TABLE)**

- Format: Item | Promised By | Promised When | Status | Link/File | Send with Email
- Status: HAVE (ready) or NEED (must create)
- Include items promised by BOTH parties

**Section 2: Follow-Up Email Draft** ⭐ ENHANCED

- Use [follow-up-email-generator.md](http://follow-up-email-generator.md) command (v11.0.0) system
- **Structure**: Greeting → Resonant Detail → Recap → Next Steps (max 2 CTAs) → Sign-Off
- **Markdown links**: [text](URL) not raw URLs
- **Distinctive phrases**: Incorporate max 2 from transcript (confidence ≥ 0.75)
- **Relationship dials**: Calculate warmth + familiarity scores → formality/CTA rigour
- **Resonant details**: 1-2 from conversation (personal anecdotes, shared values, humor, insights)
- **Reference deliverables**: From Section 1 table
- **Readability**: FK ≤ 10, avg 16-22 words/sentence, max 32 words/sentence, max 4 sentences/paragraph
- **Delay sensitivity**: If &gt;2 days, include brief apology
- **Subject line**: "Follow-Up: \[Name\] x [COMPANY] \[keyword1 • keyword2\]"

### B14 - BLURBS_REQUESTED (split in v1.5)

- Now handles ONLY actual blurb requests (split from old dual-purpose B14)
- Detection phrases: "send me a blurb", "I'll introduce you", "forward me something about what you do"
- Generate forwarding-ready blurb (1-2 paragraphs) when detected
- If no blurb requested: note "No blurbs explicitly requested in this meeting"

### B27 - KEY_MESSAGING ⭐ NEW (split from old B14)

- Strategic messaging & talking points (proactive generation)
- Generate 5-10 reusable narrative blurbs after strategic meetings
- Types: Value prop, Technical credibility, Mission alignment, Specific fit, Differentiation, Stats/traction
- Tailor to what RESONATED in this meeting
- Label each with usage context
- Include "What Resonated" analysis section

### B13 - PLAN_OF_ACTION (enhanced in v1.5)

- Structure: Title with confidence + Immediate + Near-term + Checkpoint + End state
- **Add MOMENTUM section** when relevant (replaces old B16): 
  - Two subsections: Positive Signals + Watch Points
  - Positive: detailed questions, timeline compression, resource allocation, enthusiasm
  - Watch Points: blockers, hesitations, non-commitments, concerns
  - Focus on SIGNALS not just content

### B26 - MEETING_METADATA_SUMMARY ✅ REQUIRED (enhanced in v1.5)

- Generate: Title, Email subject, Delay sensitivity, Stakeholder type, **V-OS tags**, Confidence score, Transcript quality
- **V-OS Tags**: Apply Howie's tag system `[LD-XXX] [GPT-X] [A-X]` for categorization
- This enables harmonization with Howie's scheduling system

---

## v1.5 Deleted Blocks

These blocks have been removed in v1.5:

- **B04** (Links with Context) → Links now in B25 follow-up email
- **B16** (Momentum Markers) → Absorbed into B13 momentum section
- **B28** (Founder Profile) → Merged into B08 section 1
- **B29** (Key Quotes) → Merged into B21 section 1
- **B30** (Intro Email Template) → Generate ad-hoc when needed

---

## Output Format

### Output Location

**All meetings MUST be stored in:** `N5/records/meetings/{meeting_id}/`

Example: `N5/records/meetings/2025-10-14_external-jane-smith/`

### File Structure

```markdown
N5/records/meetings/{meeting_id}/
├── B26_MEETING_METADATA_SUMMARY.md
├── B01_DETAILED_RECAP.md
├── B02_COMMITMENTS_CONTEXTUAL.md
├── B08_STAKEHOLDER_INTELLIGENCE.md
├── B21_KEY_MOMENTS.md
├── B31_STAKEHOLDER_RESEARCH.md
├── B25_DELIVERABLE_CONTENT_MAP.md
├── B05_OUTSTANDING_QUESTIONS.md
├── ... (other blocks based on stakeholder type)
└── _metadata.json
```

### File Naming

- Pattern: `file B##_BLOCKNAME.md` 
- Two digits with leading zero (B01, not B1)
- UPPERCASE names with underscores
- Example: `file B08_STAKEHOLDER_INTELLIGENCE.md` 

### Feedback Checkboxes

For blocks with `feedback_enabled: true`:

```markdown
---
**Feedback**: - [ ] Useful
---
```

---

## Quality Checks

Before finalizing, verify:

 1. ✅ All REQUIRED blocks generated (7 total)
 2. ✅ Stakeholder-appropriate HIGH priority blocks included
 3. ✅ CONDITIONAL blocks only when triggered
 4. ✅ No placeholder text or invented content
 5. ✅ Strategic depth present (not just extraction)
 6. ✅ CRM profile created for eligible stakeholders (not JOB_SEEKER)
 7. ✅ Howie V-OS tags generated in B08 and B26
 8. ✅ Follow-up email included in B25
 9. ✅ Stakeholder research insights captured in B31
10. ✅ Feedback checkboxes on enabled blocks

---

## Example High-Quality Outputs

### B08 Example - Stakeholder Intelligence

```markdown
## STAKEHOLDER_INTELLIGENCE

---
**Feedback**: - [ ] Useful
---

### Foundational Profile

**Company:** FutureFit  
**Product/Service:** Career transition platform serving 200k+ users annually  
**Motivation:** Aggregate fragmented career supports, simplify integration for external tools  
**Funding Status:** [Unknown - needs enrichment]  
**Key Challenges:** User complexity from multiple front-ends, integration overhead for partners  
**Standout Quote:** "We're not chasing easy money—we're solving hard problems in career tech"

### What Resonated

1. **Data layer vision** - Hamoon lit up when discussing "becoming data layer for hiring ecosystem"
   - Why it mattered: Aligns with FutureFit's integration pain points
   - Signal: Asked detailed technical questions about API structure, data schemas

2. **Embedded point solutions** - Strong interest in "vibe check" widget concept
   - Why it mattered: Solves their UX fragmentation problem
   - Signal: Immediately sketched integration architecture on napkin, mentioned "this is exactly what we need"

3. **Alignment-first philosophy** - Connected deeply with scaffolded reflection approach
   - Why it mattered: Differentiates from directive career coaching
   - Signal: Referenced own product philosophy multiple times, said "we're building for the same user"

### CRM Integration

**Status:** ✅ Profile created at `Knowledge/crm/individuals/hamoon-ekhtiari.md`  
**Mutual Acquaintances:** [None identified - needs enrichment]  
**Enrichment Priority:** HIGH (active partnership exploration, strong product fit signals)  

**Next Actions:**
- [ ] LinkedIn research on Hamoon's background and FutureFit journey
- [ ] Company research: FutureFit funding status, traction metrics, recent news
- [ ] Scan mutual connections in career tech ecosystem

### Howie Integration

**Recommended Tags for Future Meetings:** `[LD-NET] [GPT-E] [A-2]`  

**Rationale:**
- `[LD-NET]`: Business partnership lead (not investor or customer yet)
- `[GPT-E]`: Exploratory phase (assessing fit, not critical deadline)
- `[A-2]`: Flexible accommodation (warm relationship, can reschedule if needed)

**Priority:** Important (strong fit signals warrant priority, but not yet critical)
```

### B31 Example - Stakeholder Research

```markdown
## STAKEHOLDER_RESEARCH

---
**Feedback**: - [ ] Useful
---

**Perspective:** Speaking as career tech founder (FutureFit)

### Industry Landscape Insights

1. **Career platform consolidation trend**
   - Observation: "Most career platforms are getting acquired by larger players like LinkedIn, Indeed"
   - Implication: Window for independent platforms is narrowing; need strong differentiation or niche
   - Strategic Value: Validates our aggregation/data layer positioning vs. trying to be another platform

2. **Integration complexity as competitive moat**
   - Observation: "Everyone wants to build the platform, but integration tax is brutal—that's why we have multiple front-ends"
   - Implication: Being the data layer is more defensible than being an end-user platform
   - Strategic Value: Confirms our API-first strategy; partners will pay to avoid building integrations themselves

3. **User sophistication in career tools**
   - Observation: "Users don't want directive advice anymore—they want tools that help them think through their own decisions"
   - Implication: Market shifting from expert-driven to scaffolded self-reflection
   - Strategic Value: Our alignment-first approach is ahead of the curve; this is where the market is going

4. **Partnership dynamics in HR tech**
   - Observation: "We're not competitive with tool providers—we're the distribution channel. They need us more than we need any single tool."
   - Implication: Aggregators like FutureFit hold power in partnership negotiations; need to offer clear value beyond just another integration
   - Strategic Value: We need to emphasize unique value prop (AI coaching, better matching) not just "another tool to integrate"
```

---

## v5.1.0 Changelog

**Release Date:** 2025-10-12

**Major Changes:**

- Updated for registry v1.5 (15 blocks, down from 19)
- Added CRM integration instructions for B08
- Added Howie V-OS tag harmonization guidance
- Added B31 stakeholder research guidance
- Updated block selection logic (7 REQUIRED blocks)
- Enhanced B25 with follow-up email generation details
- Added LinkedIn read-only restrictions
- Updated stakeholder combinations for CUSTOMER and COMMUNITY
- Documented deleted blocks (B04, B16, B28, B29, B30)

**Minor Changes:**

- Clarified B14/B27 split (blurbs vs. messaging)
- Enhanced B13 with momentum section guidance
- Updated B21 with merged quotes + questions structure
- Added enrichment priority definitions
- Improved quality checklist

---

**You are transforming meetings into strategic intelligence. Act accordingly.**

---

## FINAL STEP: Follow-Up Email Generation (External Meetings Only)

After completing all blocks above, automatically generate follow-up email draft for **external stakeholder meetings**:

```markdown
command 'email-post-process' for "{meeting_folder_name}"
```

**This command will:**

1. Detect if meeting is external (`_external-` prefix)
2. Check if email draft already exists
3. Generate draft if needed → `file DELIVERABLES/follow_up_email_copy_paste.txt` 
4. Send SMS notification when complete

**SMS Notification:**

```markdown
✅ Follow-up email ready: {meeting_name}

Draft: DELIVERABLES/follow_up_email_copy_paste.txt

Review and send when ready!
```

**For internal meetings:** Skipped automatically (no notification)

**If already exists:** Skipped (idempotent, no duplicate notifications)

**If generation fails:** SMS with error details

**Manual override:** Skip entirely (no SMS)

**Specification:** `command N5/commands/follow-up-email-generator.md`  (v11.0.1)

---

**Integration Notes:**

- Email generation is AUTOMATIC for all external meetings
- Manual review is REQUIRED before sending
- Idempotent: Safe to rerun if needed
- Non-blocking: Meeting processing completes successfully even if email generation fails