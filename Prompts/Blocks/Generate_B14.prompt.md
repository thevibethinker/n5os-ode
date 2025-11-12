---
description: Generate B14 Blurbs Requested block - ONLY explicit blurb requests from meeting
tags:
  - meeting-intelligence
  - block-generation
  - b14
  - blurbs
  - deliverables
tool: true
---

# Generate Block B14: Blurbs Requested

**CRITICAL:** This block is ONLY for blurbs that were EXPLICITLY requested during the meeting. If no blurbs were requested, return "No blurbs requested in this meeting."

## Voice & Persona Activation

**MANDATORY FIRST ACTION - DO THIS BEFORE ANYTHING ELSE:**

1. **Call `set_active_persona` tool NOW** with persona_id: `5cbe0dd8-9bfb-4cff-b2da-23112572a6b8` (Vibe Writer)
   - This is a TOOL CALL, not just an instruction to read
   - You MUST execute this before proceeding

2. **After persona switch, load these files using `read_file` tool:**
   - `file 'N5/prefs/communication/voice.md'` - Voice calibration
   - `file 'N5/prefs/communication/style-guides/blurbs.md'` - Blurb style guide
   - `file 'N5/prefs/communication/voice-transformation-system.md'` - Transformation system

**Only after completing steps 1-2 above, proceed to Context-First Approach.**

## Context-First Approach

**Step 1: Scan transcript/meeting for explicit requests**
- Search for keywords: "blurb", "description", "bio", "write up", "can you send", "could you draft"
- Look for commitments where someone asks for written content about a person, product, or concept
- Check B02 (Commitments) and B25 (Deliverables) for blurb-related items

**Step 2: Extract full context from meeting**
- WHO requested the blurb (them or us)
- WHAT needs a blurb (person bio, product description, company overview, etc.)
- WHY it's needed (intro email, website, pitch deck, etc.)
- LENGTH mentioned (if any)
- TONE/AUDIENCE mentioned (if any)
- DEADLINE (if any)

**Step 3: Gather supporting intelligence**
- Check `file 'Knowledge/crm/individuals/[name].md'` if blurb is about a person
- Check `file 'Knowledge/domains/careerspan/'` for product/company blurbs
- Review B08 (Stakeholder Intelligence) for relevant background
- Review B27 (Key Messaging) for positioning to emphasize

**Step 4: Load style guide**
- Read `file 'N5/prefs/communication/style-guides/blurbs.md'`
- Apply voice knobs: warmth (0.7), confidence (0.8-0.9), precision (0.9), edge (0.2-0.4)
- Follow V's patterns: specificity > superlatives, one human detail, light aside with em-dash

## Output Format

For each requested blurb:

### [Blurb #N]: [Subject] for [Purpose]

**Requested by:** [Name/Party]  
**For:** [Usage context - email intro, website, pitch deck, etc.]  
**Length:** [Target word count or "flexible"]  
**Tone:** [professional, warm, technical, casual, etc.]  
**Deadline:** [Date or "flexible"]

**Context from meeting:**
> [Quote or paraphrase of the request from transcript]

**Draft Blurb:**

[Write the actual blurb here - 35-120 words typical]

**Sources used:**
- Transcript moments: [specific quotes/sections]
- System files: [list files referenced]
- Knowledge base: [list KB articles referenced]

**Why this framing:**
[1-2 sentences explaining strategic choices made in the blurb]

---

## Quality Standards

**Detection Precision (P11):**
- ✓ Only include if EXPLICITLY requested in meeting
- ✓ No speculative "they might want this" blurbs
- ✓ If uncertain, mark as [VERIFICATION NEEDED]

**Context Depth:**
- ✓ Mine transcript first for all relevant context
- ✓ Then supplement with CRM profiles, knowledge base
- ✓ Cite specific sources for each claim in blurb

**V Voice Application:**
- ✓ Concrete details over vague intensifiers
- ✓ One human detail per blurb
- ✓ Natural cadence, not marketing copy
- ✓ Specificity: "250k+ lines of code" not "extensive codebase"

**Minimum Standards:**
- At least 1 explicit blurb request detected OR return "No blurbs requested"
- Each blurb 35-120 words unless different length requested
- Sources cited for all factual claims
- Strategic rationale provided
- Min 300 bytes total

## Template

```markdown
# B14: Blurbs Requested

## Summary
[N blurb(s) requested during meeting / OR "No blurbs requested in this meeting"]

[For each blurb, use format above]

## Notes
- Review drafts before sending
- Confirm tone/length with requester if unclear
- Link to this block from B25 deliverables table
```

**Generate B14 now using the meeting transcript and intelligence provided in this conversation.**
