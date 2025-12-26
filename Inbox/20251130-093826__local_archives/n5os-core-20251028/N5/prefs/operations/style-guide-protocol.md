# Style Guide Protocol

**Version:** 1.0  
**Created:** 2025-10-17  
**Purpose:** Define how style guides are applied during output generation

---

## Overview

Style guides are **generative constraints** that shape outputs from the start, not post-hoc review tools. They define structure, tone, length, and validation criteria for recurring output types.

---

## Output Detection

### Primary Method: Keywords
Detect output type from user request keywords:
- "warm intro email" → `warm-intro-email`
- "meeting summary" → `meeting-summary`
- "status update" → `status-update`
- etc.

### Backup Method: Pattern Matching
If no explicit keywords, infer from context:
- Request structure (mentions of introducing people)
- Target audience cues
- Format requirements

---

## Style Guide Application Workflow

### 1. Detection
When user requests output generation:
```
User: "Draft a warm intro email..."
→ Detect output_type: warm-intro-email
→ Check if style guide exists
```

### 2. Load & Apply
If style guide exists:
```
→ Load style guide (e.g., file 'N5/style_guides/warm-intro-email.md')
→ Load exemplars from N5/exemplars/[output-type]/
→ Apply constraints during generation
```

### 3. Generate
Create output following:
- Structure requirements
- Length bounds
- Tone specifications
- Required elements checklist

### 4. Validate
Check output against validation criteria:
- Length within bounds
- Required elements present
- Tone consistent
- Structure followed

### 5. Handle Failures
**If output fails validation:**
- ❌ DON'T: Immediately regenerate
- ✅ DO: Evaluate the process that led to failure
  - Was the style guide unclear?
  - Did constraints conflict?
  - Was user request ambiguous?
  - Do we need more exemplars?

**Then:**
- Report findings to user
- Propose fix (update style guide, clarify request, etc.)
- Regenerate with corrected process

### 6. Offer Exemplar Selection
After every successful generation:
```
"Would you like to save this as an exemplar for {output_type}?"
- User explicitly approves
- Save to N5/exemplars/{output_type}/[timestamp]-[name].md
```

---

## Style Guide Creation Workflow

### Triggered When:
1. First output of a new type is generated
2. User explicitly requests style guide creation
3. Pattern suggests recurring output type

### Process:
1. **Auto-extract criteria** from output:
   - Structure (sections, order)
   - Length (word count, paragraph count)
   - Tone (analyze language patterns)
   - Style (sentence structure, voice)

2. **Prompt user for feedback:**
   ```
   "I detected this is a [output_type]. Would you like to create 
   a style guide? Here's what I extracted:
   
   - Length: ~X words
   - Structure: [sections]
   - Tone: [characteristics]
   
   Any adjustments?"
   ```

3. **Generate style guide** with user refinements

4. **Save system:**
   - Style guide → `N5/style_guides/{output_type}.md`
   - Mapping → `N5/config/output_type_mapping.jsonl`
   - First exemplar → `N5/exemplars/{output_type}/`

---

## Integration Points

### Priority 1: General LLM Generations
Apply to any direct output generation request in conversation

### Priority 2: Workflow Outputs
Apply simultaneously to workflow-generated outputs:
- Meeting ingestion → meeting summaries, deliverables
- Email drafting → various email types
- Document creation → reports, briefs, etc.

**Rule:** Any workflow output that could be an exemplar should be treated as such - always offer selection.

---

## Example Management

### Storage:
- Location: `N5/exemplars/{output_type}/`
- Naming: `[timestamp]-[descriptive-name].md`
- All approved examples are kept (no limits)

### Selection Criteria:
- User explicitly approves: "Yes, use this as an example"
- Or: User says "This is great" after generation
- Always offer option after successful generation

### Usage:
- Reference during generation for style/tone
- Include in style guide as concrete examples
- Use for pattern learning

---

## File Structure

```
N5/
├── style_guides/
│   ├── warm-intro-email.md
│   ├── meeting-summary.md
│   └── [output-type].md
├── exemplars/
│   ├── warm-intro-email/
│   │   ├── 2025-10-17-2203-original.md
│   │   ├── 2025-10-17-2204-approved-jabari-ben.md
│   │   └── ...
│   └── [output-type]/
│       └── [timestamp]-[name].md
├── config/
│   └── output_type_mapping.jsonl
└── scripts/
    └── style_guide_manager.py
```

---

## Commands

### Create style guide
```bash
python3 N5/scripts/style_guide_manager.py create \
  --output-type [type] \
  --source-file [path]
```

### Add exemplar
```bash
python3 N5/scripts/style_guide_manager.py add-exemplar \
  --output-type [type] \
  --file [path] \
  --name [descriptive-name]
```

### Validate output
```bash
python3 N5/scripts/style_guide_manager.py validate \
  --output-type [type] \
  --file [path]
```

### List all style guides
```bash
python3 N5/scripts/style_guide_manager.py list
```

### Show style guide details
```bash
python3 N5/scripts/style_guide_manager.py show \
  --output-type [type]
```

---

## Principles Applied

- **P0 (Rule-of-Two):** Load only style guide + max 2 exemplars during generation
- **P1 (Human-Readable):** Style guides are markdown, easily editable
- **P2 (SSOT):** One style guide per output type
- **P7 (Dry-Run):** All operations support --dry-run
- **P8 (Minimal Context):** Only load what's needed for current generation
- **P15 (Complete Before Claiming):** Don't mark output complete until validated
- **P18 (Verify State):** Always validate against style guide before claiming success
- **P19 (Error Handling):** Evaluate process on failure, don't just retry

---

## Evolution

Style guides should evolve:
- Update based on user feedback
- Refine criteria as more exemplars are added
- Document edge cases and exceptions
- Track what works vs. what doesn't

**Update workflow:**
1. User provides feedback on output
2. Identify if issue is style guide problem or generation problem
3. Update style guide if needed
4. Document change in style guide notes section

---

## Notes

- Not every output needs a style guide - only recurring types
- User can override style guide per-generation
- System should be transparent about when applying style guides
- Style guides are tools for consistency, not rigid rules
- Quality > adherence to rules

---

**Last Updated:** 2025-10-17 18:04 ET
