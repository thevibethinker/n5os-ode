# Worker 3: Style Guide Generation

**Mission:** Create specialized style guides for each reflection block type  
**Time Estimate:** 90 minutes  
**Dependencies:** Worker 2 (needs block registry)  
**Parallelizable:** No

---

## Objectives

1. ✅ Generate 11 style guides (one per reflection block type B50-B99)
2. ✅ Use voice extraction + transformation strategy
3. ✅ Follow existing style guide format
4. ✅ Integrate with voice routing system

---

## Context

**Existing Style Guide System:**
- Location: `N5/prefs/communication/style-guides/`
- Format: Markdown with structure, tone, lexicon, templates, QA checklist
- Examples: `linkedin-posts.md`, `follow-up-emails.md`, `blurbs.md`
- Foundation: `voice-transformation-system.md`, `transformation-pairs-library.md`

**Voice Profiles:**
- Internal/Professional: `N5/prefs/communication/voice.md`
- External Social: `N5/prefs/communication/social-media-voice.md`

---

## Deliverables

### Create 11 Style Guides

**Directory:** `N5/prefs/communication/style-guides/reflections/`

**Files to Create:**
1. `B50-personal-reflection.md`
2. `B60-learning-synthesis.md`
3. `B70-thought-leadership.md`
4. `B71-market-analysis.md`
5. `B72-product-analysis.md`
6. `B73-strategic-thinking.md`
7. `B80-linkedin-post.md` (or symlink to existing)
8. `B81-blog-post.md`
9. `B82-executive-memo.md`
10. `B90-insight-compound.md`
11. `B91-meta-reflection.md`

---

## Style Guide Template

Each guide should follow this structure:

```markdown
# [Block Name] Style Guide

**Block ID:** B[XX]  
**Domain:** internal | external_professional | external_social  
**Voice Profile:** `file 'path/to/voice.md'`  
**Auto-Approve Threshold:** [N blocks]

---

## Purpose

[1-2 sentence description of what this block type produces]

---

## Structure

[Typical structure/outline for this content type]

Example:
- Opening (context/hook)
- Analysis (core insights)
- Synthesis (patterns/implications)
- Closure (takeaways/next steps)

---

## Tone & Voice

**Core Characteristics:**
- [Attribute 1]: [description]
- [Attribute 2]: [description]
- [Attribute 3]: [description]

**Avoid:**
- [Anti-pattern 1]
- [Anti-pattern 2]

---

## Lexicon

**Preferred Terms:**
- Use X, not Y
- Use A, not B

**Domain-Specific Language:**
- [Technical terms appropriate for this block type]

---

## Templates

### Template 1: [Name]
```
[Structure outline with placeholders]
```

### Template 2: [Name]
```
[Alternative structure]
```

---

## Transformation Guidance

**Raw → Refined:**
- Stream-of-consciousness → [structured format]
- Informal language → [appropriate register]
- Incomplete thoughts → [complete ideas]

**Key Transforms:**
1. [Transform type 1]
2. [Transform type 2]
3. [Transform type 3]

---

## Examples

### Example 1: [Scenario]

**Raw Input:**
```
[Stream-of-consciousness reflection excerpt]
```

**Refined Output:**
```
[Polished version following this guide]
```

---

## QA Checklist

Before finalizing:
- [ ] Follows structural template
- [ ] Tone matches voice profile
- [ ] Uses preferred lexicon
- [ ] Length appropriate for block type
- [ ] Clear, actionable (if applicable)
- [ ] Free of jargon (unless domain-appropriate)
- [ ] Meets auto-approve threshold criteria

---

**Version:** 1.0  
**Created:** 2025-10-24
```

---

## Implementation Strategy

### Step 1: Study Existing Style Guides
Load and analyze:
- `N5/prefs/communication/style-guides/linkedin-posts.md`
- `N5/prefs/communication/style-guides/follow-up-emails.md`
- `N5/prefs/communication/style-guides/blurbs.md`

### Step 2: Extract Voice Principles
From:
- `N5/prefs/communication/voice.md`
- `N5/prefs/communication/social-media-voice.md`
- `N5/prefs/communication/voice-transformation-system.md`

### Step 3: Generate Each Style Guide
For each block type:
1. Determine domain (internal, external_professional, external_social)
2. Map to appropriate voice profile
3. Define structure specific to block type
4. Extract relevant lexicon and tone guidance
5. Create 2-3 templates
6. Write 1-2 examples with raw→refined transforms
7. Build QA checklist

### Step 4: Cross-Reference with Registry
Ensure each style guide aligns with block definition in `N5/prefs/reflection_block_registry.json`

---

## Special Cases

### B80 (LinkedIn Post)
- May already exist as `linkedin-posts.md`
- If so, create symlink or reference in registry
- If not, create following existing patterns

### B90 (Insight Compounding) & B91 (Meta-Reflection)
- More experimental block types
- Less rigid structure, more exploratory
- Focus on synthesis and pattern recognition
- Higher auto-approve threshold (10) due to internal nature

---

## Testing

For each style guide:
1. Verify follows template structure
2. Check voice profile reference is correct
3. Validate examples are clear
4. Ensure QA checklist is comprehensive

---

## Principles Applied

- **P1 (Human-Readable):** All guides in clear, accessible markdown
- **P2 (SSOT):** Each block type has exactly one style guide
- **P21 (Document Assumptions):** Examples show raw→refined transformation
- **P20 (Modular):** Each guide is standalone, can be used independently

---

## Success Criteria

Worker 3 is complete when:
1. ✅ All 11 style guides created
2. ✅ Each follows template structure
3. ✅ Voice profile references correct
4. ✅ Examples included in each
5. ✅ QA checklists complete
6. ✅ Cross-referenced with block registry

---

**Status:** Waiting for Worker 2  
**Created:** 2025-10-24
