# Style Guide System Specification

**Version:** 1.0  
**Created:** 2025-10-17  
**Status:** Design Phase

---

## Purpose

Automated system to ensure consistent output quality by:
1. Applying style guides during generation (generative constraints)
2. Validating outputs against established standards
3. Building library of approved exemplars over time

**Key Insight:** Style guides are not post-hoc review tools — they're part of the generation pipeline.

---

## Core Workflow

### First Time Output Type Generated
```
1. Generate output naturally
2. User approves output
3. System creates style guide FROM that output
4. Store approved output as exemplar
```

### Subsequent Generations
```
1. Detect/identify output type
2. Load corresponding style guide
3. Generate output WITH style guide constraints
4. Validate output against style guide
5. If validation passes → optionally add to exemplars
6. If validation fails → regenerate with feedback
```

---

## Architecture

### Directory Structure
```
N5/
├── config/
│   └── output_type_mapping.jsonl      # output_type → style_guide_path
├── style_guides/
│   ├── warm-intro-email.md
│   ├── meeting-summary.md
│   └── [output-type].md
└── exemplars/
    ├── warm-intro-email/
    │   ├── 2025-10-17-jabari-ben.md
    │   └── [timestamp]-[slug].md
    └── meeting-summary/
        └── ...
```

### Components

**1. Style Guide Manager** (`N5/scripts/style_guide_manager.py`)
- CRUD operations for style guides
- Mapping management
- Validation logic

**2. Generator Wrapper** (`N5/scripts/generate_with_style.py`)
- Callable from other scripts
- Applies style guide during generation
- Validates output
- Stores exemplars

**3. Integration Points**
- Meeting ingestion (warm intros, summaries)
- Email drafts
- Any "standard output type"

---

## Style Guide Schema

```markdown
---
output_type: warm-intro-email
version: 1.0
created: 2025-10-17
updated: 2025-10-17
source_output: /path/to/original/output
---

# Style Guide: [Output Type Name]

## Purpose
What this output type is for (1-2 sentences)

## Structure
Required sections/components in order

## Length
- Target: X words / Y paragraphs
- Maximum: Z words
- Minimum: A words

## Tone
Voice characteristics (casual, formal, warm, direct, etc.)

## Style
- Sentence structure preferences
- Paragraph length
- Formatting conventions

## Required Elements
Must-have components (checklist)
- [ ] Element 1
- [ ] Element 2

## Forbidden Elements
What to avoid explicitly
- ❌ Thing 1
- ❌ Thing 2

## Validation Criteria
Pass/fail checklist with specific thresholds
- [ ] Length within bounds
- [ ] Required elements present
- [ ] Tone consistent
- [ ] Structure followed

## Examples
Brief inline examples or references to exemplar files

## Notes
Additional context, edge cases, when to deviate
```

---

## Mapping Schema

**File:** `N5/config/output_type_mapping.jsonl`

```json
{"output_type": "warm-intro-email", "style_guide": "N5/style_guides/warm-intro-email.md", "enabled": true, "auto_detect_keywords": ["intro", "introduction", "connect"], "created": "2025-10-17T18:00:00Z"}
{"output_type": "meeting-summary", "style_guide": "N5/style_guides/meeting-summary.md", "enabled": true, "auto_detect_keywords": ["meeting", "summary", "notes"], "created": "2025-10-17T18:00:00Z"}
```

**Fields:**
- `output_type` (str): Unique identifier (kebab-case)
- `style_guide` (str): Path to style guide file
- `enabled` (bool): Whether to apply this style guide
- `auto_detect_keywords` (list): Keywords for automatic detection
- `created` (str): ISO timestamp
- `updated` (str, optional): ISO timestamp of last update

---

## Script Interfaces

### 1. Style Guide Manager

```bash
# Create new style guide from output
python3 N5/scripts/style_guide_manager.py create \
  --output-type warm-intro-email \
  --source-file /path/to/output.md \
  --interactive

# Update existing style guide
python3 N5/scripts/style_guide_manager.py update \
  --output-type warm-intro-email \
  --field tone \
  --value "casual, warm"

# Validate output against style guide
python3 N5/scripts/style_guide_manager.py validate \
  --output-type warm-intro-email \
  --file /path/to/output.md

# List all style guides
python3 N5/scripts/style_guide_manager.py list

# Show style guide details
python3 N5/scripts/style_guide_manager.py show \
  --output-type warm-intro-email
```

### 2. Generator Wrapper (Python API)

```python
from N5.scripts.generate_with_style import generate_with_style_guide

# Generate output with style guide
result = generate_with_style_guide(
    output_type="warm-intro-email",
    content_context={
        "recipient": "Jabari",
        "subject": "Ben Guo",
        "relationship": "AI Collective"
    },
    save_as_exemplar=True,
    exemplar_name="jabari-ben"
)

# Returns:
# {
#   "output": "generated content",
#   "validation": {"passed": True, "score": 0.95, "issues": []},
#   "exemplar_path": "/path/to/exemplar" or None,
#   "style_guide_used": "/path/to/style_guide.md"
# }
```

---

## Integration Points

### Meeting Ingestion
- Warm intros → `warm-intro-email` style guide
- Meeting summaries → `meeting-summary` style guide
- Deliverables → `meeting-deliverable` style guide

### Email Drafts
- Auto-detect email type (intro, follow-up, etc.)
- Apply corresponding style guide
- Validate before presenting to user

### Command Outputs
- Any command that generates structured output
- Check mapping for output type
- Apply style guide if exists

---

## Implementation Phases

### Phase 1: Core Infrastructure (This session)
- [x] Spec complete
- [ ] Directory structure
- [ ] Schema validation
- [ ] `style_guide_manager.py` core CRUD
- [ ] `output_type_mapping.jsonl` with first entry
- [ ] Create first style guide: `warm-intro-email`

### Phase 2: Generation Integration
- [ ] `generate_with_style.py` wrapper
- [ ] Validation logic
- [ ] Exemplar storage
- [ ] Feedback loop for regeneration

### Phase 3: Auto-Detection
- [ ] Content analysis for type detection
- [ ] Keyword matching
- [ ] Confidence scoring

### Phase 4: Integrations
- [ ] Meeting ingestion
- [ ] Email draft commands
- [ ] Other output generators

---

## Open Design Questions

1. **Integration approach:**
   - Wrapper function that other scripts call?
   - Or each integration point checks mapping independently?
   - **Recommendation:** Wrapper function (DRY, consistent validation)

2. **Output type detection:**
   - Explicit declaration (required parameter)?
   - Auto-detect from content/context?
   - Both (explicit preferred, auto as fallback)?
   - **Recommendation:** Both, explicit takes priority

3. **Validation failure handling:**
   - Auto-regenerate with feedback?
   - Present to user with issues flagged?
   - Configurable per style guide?
   - **Recommendation:** Configurable, default to present with issues

4. **Exemplar selection criteria:**
   - User approval required?
   - Automatic if validation score > threshold?
   - **Recommendation:** User approval for now, automate later

---

## Success Criteria

**Phase 1 Complete:**
- [ ] Can create style guide from existing output
- [ ] Can update style guide fields
- [ ] Can validate output against style guide
- [ ] Can list/show style guides
- [ ] First style guide created: `warm-intro-email`
- [ ] Jabari-Ben email stored as first exemplar

**System Working:**
- [ ] New outputs automatically use style guides
- [ ] Validation catches quality issues
- [ ] Exemplar library grows over time
- [ ] Output consistency improves measurably

---

## Principles Applied

- **P2 (SSOT):** Style guides are single source for output standards
- **P20 (Modular):** Integrates without tight coupling
- **P8 (Minimal Context):** Focused, specific guidelines
- **P15 (Complete Before Claiming):** Build core before expanding
- **P5 (Anti-Overwrite):** Careful file operations, backups
- **P7 (Dry-Run):** All file operations support dry-run
- **P19 (Error Handling):** Comprehensive validation and error paths

---

## Notes

- Style guides should evolve over time as we learn what works
- Not every output needs a style guide — only recurring types
- User can override/disable style guides per-generation if needed
- System should be transparent about when style guides are applied
