---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
pattern_type: system_design
extracted_from: con_B9UYEfyQZiOdHC7F (Blurb Generator build)
---

# Reasoning Pattern: Context-Driven Generator with Type Branching

## Pattern Overview

A design pattern for building content generators that:
1. Load intelligence from structured blocks (not raw transcripts)
2. Detect subject/context from primary block with multi-tier fallback
3. Support multiple output types via explicit branching
4. Apply voice transformation with style guide + automatic system
5. Validate against rubric before delivery

**Applicable to:** Multi-format content generators, communications systems, any context-driven output requiring quality assurance

---

## Problem Statement

When building content generators (emails, blurbs, summaries, proposals), common failure modes:
- **Brittleness:** Single-method subject detection fails on edge cases
- **Type confusion:** Trying to infer output format leads to wrong structure
- **Voice inconsistency:** Manual voice application diverges from examples
- **Quality uncertainty:** No validation before delivery leads to iteration loops

**Core challenge:** Balance flexibility (works for many subjects/types) with quality (consistent voice, appropriate structure).

---

## Solution Components

### 1. Structured Intelligence Loading

**Principle:** Load from structured blocks, not raw transcripts

**Implementation:**
```
Primary source: Specific intelligence block (e.g., B14: BLURBS_REQUESTED)
Context sources: Related blocks (B08, B21, B25, B01)
Knowledge base: Subject-specific reference files
Style guide: Output type specifications
```

**Why this works:**
- Structured blocks pre-filter signal from noise
- Multiple context sources enable graceful degradation
- Knowledge base provides consistent proof points
- Style guide ensures format compliance

**Fallback hierarchy:**
1. If primary block exists → Use it
2. If primary missing → Check context blocks
3. If context incomplete → Parse raw transcript
4. If all else fails → Ask user for input

---

### 2. Multi-Tier Subject Detection

**Principle:** Don't rely on single detection method

**Implementation:**
```
Tier 1: Explicit field check (B14 "subject" or "key_focus")
  ↓ (if unclear)
Tier 2: Semantic analysis (parse "purpose" field)
  ↓ (if still unclear)
Tier 3: Contextual analysis (parse B21 KEY_MOMENTS for dominant theme)
  ↓ (if still unclear)
Tier 4: User clarification (ask explicitly)
```

**Why this works:**
- Explicit check handles 80% of cases (fast, accurate)
- Semantic analysis handles ambiguous phrasing
- Contextual analysis handles implicit subjects
- User clarification prevents guessing

**Anti-pattern:** Single keyword matching ("Careerspan" → Careerspan blurb)  
**Problem:** Fails when subject is implied, synonyms used, or multiple subjects present

---

### 3. Explicit Type Branching (Not Inference)

**Principle:** Make output type an explicit parameter, not inferred

**Implementation:**
```
IF type = "short":
  Load Short Blurb template
  Target length: 50-80 words
  Structure: 4-line punchy format
ELSE IF type = "email":
  Load Email Blurb template
  Target length: 150-250 words
  Structure: Opening + Context + Proof + Closing
ELSE:
  Error: Unknown type, ask user
```

**Why this works:**
- No ambiguity about intended format
- Each type has distinct structure (not just length)
- Templates ensure consistency
- User controls output explicitly

**Anti-pattern:** Trying to infer type from context ("seems like they want email version")  
**Problem:** Inference fails, leads to wrong structure, requires regeneration

---

### 4. Voice Transformation (Manual + Automatic)

**Principle:** Load style guide for context, leverage automatic transformation for polish

**Implementation:**
```
1. Load style guide explicitly (examples, voice dials, patterns)
2. Generate style-free draft (facts only, no voice)
3. Apply voice dials (warmth, confidence, precision, edge)
4. Let automatic voice transformation polish
5. Validate against examples
```

**Why this works:**
- Style guide provides concrete examples (few-shot learning)
- Style-free draft separates content from presentation
- Voice dials enable precise control
- Automatic transformation ensures consistency across all communications

**Anti-pattern:** Purely manual voice ("write it like V would say")  
**Problem:** Diverges from actual examples, inconsistent across outputs

---

### 5. Rubric-Based Quality Validation

**Principle:** Score output against rubric before delivery, iterate if needed

**Implementation:**
```
Rubric categories:
- Voice Fidelity (40 points)
- Audience Fit (30 points)
- Specificity (20 points)
- Technical Excellence (10 points)

Threshold: ≥85/100

Process:
1. Generate output
2. Score against rubric
3. IF score < threshold → Identify lowest category, revise, re-score
4. IF score ≥ threshold → Deliver
```

**Why this works:**
- Objective scoring prevents subjective "good enough"
- Category breakdown enables targeted revision
- Threshold ensures minimum quality
- Real-time scoring prevents post-delivery iteration

**Anti-pattern:** Generate and hope ("this looks good, ship it")  
**Problem:** Quality inconsistent, high iteration rate after delivery

---

## Application Example: Blurb Generator

**Context:** Build generator for Short Blurbs (50-80 words) and Email Blurbs (150-250 words)

**Pattern application:**

1. **Structured Intelligence Loading**
   - Primary: B14 (BLURBS_REQUESTED)
   - Context: B08, B21, B25, B01
   - Knowledge base: careerspan-positioning.md
   - Style guide: blurbs.md

2. **Multi-Tier Subject Detection**
   - Tier 1: Check B14 "subject" field → "Careerspan" found
   - Subject = Careerspan → Load careerspan-positioning.md
   - (If not found, fall through to Tier 2, 3, 4)

3. **Explicit Type Branching**
   - User specifies: type = "short"
   - Load Short Blurb template (50-80 words, 4-line format)
   - Generate following structure

4. **Voice Transformation**
   - Load blurbs.md (examples, voice dials)
   - Generate style-free: "Careerspan is a platform for career development..."
   - Apply voice dials: warmth=0.8, confidence=0.7, precision=0.9
   - Result: "Careerspan is a career development platform that combines AI workflows with human coaching—delivering personalized guidance at enterprise scale..."

5. **Rubric-Based Quality Validation**
   - Score: Voice=37/40, Audience=28/30, Specificity=20/20, Technical=10/10
   - Total: 95/100 (≥85 threshold) ✓
   - Deliver output

**Result:** High-quality output (95/100), subject correctly detected (Careerspan), appropriate type (short), voice matched (warmth/confidence/precision), no iteration needed.

---

## Reusable Components

### Subject Detection Logic (Generalized)

```python
def detect_subject(primary_block, context_blocks, fallback_source):
    # Tier 1: Explicit field
    if primary_block.has_field("subject"):
        return primary_block.get("subject")
    
    # Tier 2: Semantic analysis
    semantic_subject = analyze_semantic(primary_block.get("purpose"))
    if semantic_subject.confidence > 0.75:
        return semantic_subject.value
    
    # Tier 3: Contextual analysis
    dominant_theme = parse_context_blocks(context_blocks)
    if dominant_theme:
        return dominant_theme
    
    # Tier 4: User clarification
    return ask_user("What is the subject of this output?")
```

### Type Branching Logic (Generalized)

```python
def generate_with_type(type_param, content, templates):
    if type_param not in templates:
        raise ValueError(f"Unknown type: {type_param}")
    
    template = templates[type_param]
    output = apply_template(content, template)
    
    # Validate structure
    if not matches_template_structure(output, template):
        raise ValueError(f"Output doesn't match {type_param} structure")
    
    return output
```

### Rubric Validation (Generalized)

```python
def validate_with_rubric(output, rubric, threshold=85):
    score = 0
    breakdown = {}
    
    for category, criteria in rubric.items():
        category_score = score_category(output, criteria)
        breakdown[category] = category_score
        score += category_score
    
    if score < threshold:
        lowest_category = min(breakdown, key=breakdown.get)
        return {
            "passed": False,
            "score": score,
            "breakdown": breakdown,
            "action": f"Revise {lowest_category}"
        }
    
    return {
        "passed": True,
        "score": score,
        "breakdown": breakdown
    }
```

---

## When to Use This Pattern

**Ideal scenarios:**
- Building multi-format content generators (emails, blurbs, proposals)
- Subject-flexible systems (works for multiple people/products/topics)
- Quality-critical outputs (recipient-facing communications)
- Systems requiring consistent voice across many outputs

**Not ideal for:**
- Single-format, single-subject generators (pattern overkill)
- Exploratory/creative writing (rubric too constraining)
- Systems where speed > quality (validation adds overhead)

---

## Success Indicators

**Pattern is working when:**
- Subject detection accuracy > 95%
- Quality scores consistently ≥ threshold
- Iteration rate < 10% (outputs rarely need editing)
- Voice consistency across all subjects/types
- User satisfaction: "Sounds right, ready to use"

**Pattern needs adjustment when:**
- Subject detection failing regularly (add tier or improve semantic analysis)
- Quality scores below threshold often (adjust rubric or style guide)
- High iteration rate (check if rubric matches actual quality needs)
- Voice inconsistency (strengthen style guide examples)

---

## Related Patterns

- **Few-Shot Voice Transformation:** Load examples, apply pattern
- **Graceful Degradation:** Primary source → fallback → ask user
- **Rubric-Driven Quality:** Score, iterate, deliver
- **Explicit Over Inferred:** Make parameters explicit, not guessed

---

## Anti-Patterns to Avoid

1. **Single-method subject detection:** Brittle, fails on edge cases
2. **Inferred output types:** Leads to wrong structures
3. **Purely manual voice:** Inconsistent, diverges from examples
4. **Generate-and-hope quality:** High iteration rate post-delivery
5. **Hardcoded subjects:** Not reusable for other topics

---

## Version History

- **v1.0 (2025-11-17):** Extracted from Blurb Generator build (con_B9UYEfyQZiOdHC7F)

---

## Further Applications

Consider applying this pattern to:
- Warm intro generators (multiple relationship types, multiple formats)
- Proposal generators (different proposal types: investor, partnership, customer)
- Summary generators (different lengths: executive, detailed, technical)
- Social media content (different platforms: LinkedIn, Twitter, blog)

**Key insight:** Any content generator with multiple subjects, types, and quality requirements benefits from this pattern.

