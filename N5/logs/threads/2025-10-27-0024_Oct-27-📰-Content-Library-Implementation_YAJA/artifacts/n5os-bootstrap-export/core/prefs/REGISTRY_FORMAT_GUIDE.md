# Block Type Registry - Format String Guide

**Version**: 1.0  
**For**: `N5/prefs/block_type_registry.json`  
**Audience**: AI processors (Zo instances) generating Smart Blocks

---

## Understanding Format Strings

Each block in the registry has a `"format"` field that specifies the **exact structure** of the output markdown. This guide explains how to interpret format strings correctly.

### What `[Brackets]` Mean

**IMPORTANT:** Text in `[square brackets]` within format strings are **NOT placeholder text to copy verbatim**. They are **extraction instructions** telling you what KIND of content to extract from the transcript and place in that position.

### Example Interpretation

**Format string:**
```
"format": "Key decisions and agreements:\n• We aligned on [specific outcome with context]"
```

**CORRECT interpretation:**
- Extract the actual outcome/alignment from the transcript
- Provide the full context of why it matters
- Replace `[specific outcome with context]` with real content

**CORRECT output:**
```markdown
Key decisions and agreements:
• We aligned on launching a pilot with 50 users starting March 1st, using their existing onboarding flow as the baseline
```

**INCORRECT output (copying placeholder verbatim):**
```markdown
Key decisions and agreements:
• We aligned on [specific outcome with context]
```

---

## Format String Elements

### 1. Literal Text (Keep As-Is)
Text outside brackets should appear exactly in the output:
- Headers: `###`, `**bold**`
- Separators: `---`, `→`
- Bullets: `•`, `-`
- Table syntax: `|`, `---`

### 2. Extraction Placeholders (Replace with Content)
Text in `[brackets]` indicates what to extract:

| Placeholder Pattern | What to Extract | Example Output |
|---|---|---|
| `[specific outcome]` | Exact decision/outcome from meeting | "launching beta in Q2 with 10 pilot customers" |
| `[Name]` | Actual person's name | "Sarah Chen" |
| `[Date]` | Actual date mentioned | "March 15" or "EOD Friday" |
| `[why it matters]` | Strategic importance/context | "this unblocks the enterprise sales pipeline" |
| `[quote]` | Verbatim quote from transcript | "We need to solve this before Series A" |
| `[metric]` | Actual number/measurement | "45% conversion rate" |

### 3. Choice Options (Pick One)
Format: `[Option1 / Option2 / Option3]`

Example: `[Hypothetical / Outlined / Detailed]`

**Your task:** Analyze the transcript and select the most accurate option.

**Example:**
- Format: `Specificity: [Hypothetical / Outlined / Detailed]`
- Output: `Specificity: Detailed`

### 4. Status Flags (Use Exact Text)
Some blocks specify exact status values:

**Example from B02 (COMMITMENTS_CONTEXTUAL):**
- Format: `Status: [HAVE/NEED]`
- Rule: "HAVE if link/file resolved; else NEED"
- Output must be exactly: `HAVE` or `NEED` (not "have" or "we have it")

### 5. Conditional Text (Include If Applicable)
Format: `[Optional context bullets]`

**Your task:** Include this section only if relevant content exists in transcript.

---

## Common Patterns

### Pattern 1: Structured Lists
**Format:**
```
• [Question]
  → Owner: [Name]
  → Needed by: [Date/Trigger]
```

**Interpretation:**
- Main bullet: Extract the question
- Sub-items with arrows: Extract owner name and deadline
- Preserve indentation and arrow symbols

### Pattern 2: Tables
**Format:**
```
| Owner | Deliverable | Context/Why |
|-------|------------|-------------|
```

**Interpretation:**
- Keep table header exactly as shown
- Keep separator row exactly as shown
- Add rows with extracted content for each deliverable
- Ensure all columns are filled (use "TBD" or "[Unknown]" if truly missing)

### Pattern 3: Multi-Part Extraction
**Format:**
```
"[quote]" ([speaker], [timestamp])
```

**Interpretation:**
- Extract verbatim quote
- Identify who said it
- Approximate timestamp (or use "unknown" if diarization unavailable)

**Output:**
```
"We should focus on retention before acquisition" (Sarah Chen, 14:32)
```

---

## Special Rules

### Rule 1: Preserve Markdown Structure
All markdown elements in format strings are structural:
- `###` headers → Keep exactly
- `**bold**` → Keep bold formatting
- `---` separators → Keep exactly
- `•` bullets → Use these bullet characters
- `→` arrows → Use these arrow symbols

### Rule 2: Never Generate Fake Data
If transcript doesn't contain information for a placeholder:
- Use `[Unknown]`, `[Not discussed]`, or `[TBD]` 
- Do NOT invent or simulate content
- Do NOT use placeholder text from format string

### Rule 3: Apply Block-Specific Rules
Many blocks have a `"rules"` field with specific instructions:

**Example from B02:**
```json
"rules": {
  "owner_classification": "Vrijen/Logan/Careerspan team = 'We', Others = Name (your side)",
  "date_format": "Preserve as stated (EOD Friday, early next week, etc.)"
}
```

**Application:**
- If Vrijen commits to something → Owner column = "We"
- If external stakeholder commits → Owner column = "Sarah Chen (your side)"
- If someone said "end of day Friday" → Use "EOD Friday" (not "2025-03-15")

### Rule 4: Respect Conditional Generation
Format strings show structure, but blocks should only be generated if their `"when"` condition is met.

**Example:**
- Block B06 (PILOT_INTELLIGENCE) has `"when": "ONLY if pilot explicitly discussed"`
- Even though format string exists, DO NOT generate this block unless pilot was actually discussed

---

## Validation Checklist

Before saving a block, verify:

- [ ] No `[placeholder]` text copied verbatim from format string
- [ ] All markdown structure preserved (headers, bullets, tables)
- [ ] All extracted content is from actual transcript (not invented)
- [ ] Block-specific rules from registry applied correctly
- [ ] Feedback checkbox included if `"feedback_enabled": true`
- [ ] Unknown/missing information marked appropriately (not simulated)

---

## Example: Full Block Generation

**Registry Format (B01 - DETAILED_RECAP):**
```
"format": "### DETAILED_RECAP\n---\n**Feedback**: - [ ] Useful\n---\nKey decisions and agreements:\n• We aligned on [specific outcome with context]\n• You confirmed [exact commitment with rationale]\n• Both sides agreed that [mutual understanding]\n• Next critical step is [specific milestone]"
```

**Correct Generated Block:**
```markdown
### DETAILED_RECAP
---
**Feedback**: - [ ] Useful
---
Key decisions and agreements:
• We aligned on implementing the new candidate scoring algorithm by end of Q1, using the existing resume parser as the foundation to minimize technical risk
• You confirmed you'll provide 50 anonymized candidate profiles by March 10th to train the initial model, with the understanding that more diverse data improves accuracy
• Both sides agreed that protecting candidate privacy is non-negotiable and that any PII must be encrypted at rest and in transit
• Next critical step is Vrijen to share the technical spec by Friday for your engineering team's review
```

**Note:** Every bullet point contains real content extracted from the meeting transcript. No placeholders remain.

---

## Common Mistakes to Avoid

❌ **Copying format placeholders verbatim:**
```markdown
• We aligned on [specific outcome with context]
```

❌ **Inventing content not in transcript:**
```markdown
• We aligned on a $2M Series A at 8M pre-money
```
*(If this wasn't discussed, don't add it)*

❌ **Ignoring block-specific rules:**
```markdown
Owner: Vrijen
```
*(Should be "We" per B02 rules)*

❌ **Changing markdown structure:**
```markdown
Key decisions and agreements:
- We aligned on...
```
*(Format specified `•` bullets, not `-` bullets)*

✅ **Correct approach:**
- Extract real content from transcript
- Preserve format structure exactly
- Apply block-specific rules
- Mark unknowns appropriately

---

**Remember:** Format strings are TEMPLATES showing structure. Your job is to extract REAL content from transcripts and format it according to these templates. Never copy placeholder text. Never invent content.
