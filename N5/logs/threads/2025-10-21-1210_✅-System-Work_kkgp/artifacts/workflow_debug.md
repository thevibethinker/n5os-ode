# Social Post Generation — Workflow Debug & Improvement

**Date:** 2025-10-20  
**Context:** Demo script development → need reliable social content generation

---

## Problem Statement

Current `n5_linkedin_post_generate.py` script:
- ❌ Ingested wrong source (demo script instead of reflection)
- ❌ Generated 2,524-word output (should be 200-300)
- ❌ No knowledge enrichment layer
- ❌ No angle selection mechanism
- ❌ Single-execution multi-variant approach (splits attention)

---

## Root Cause Analysis

### Issue 1: Script Input Handling

**Current behavior:**
```bash
python3 script.py --target-length 300 < source.md
```
Reads stdin, but may have ingested wrong file or included markdown formatting that bloated output.

**Fix needed:**
- Add `--source-file` argument to explicitly pass file path
- Validate source file exists and is readable
- Strip markdown metadata before processing

### Issue 2: No Length Enforcement

Script has `--target-length 300` but generated 2,524 words.

**Hypothesis:** Voice engine expansion without hard limits.

**Fix needed:**
- Add hard truncation at target_length * 1.2 (360 words max for 300 target)
- Log warnings when approaching limit
- Preserve complete sentences (don't truncate mid-sentence)

### Issue 3: No Knowledge Enrichment

Script generates from seed content only, no context from Knowledge/.

**Fix needed:**
- Add knowledge scanner module
- Scan stable sources: `Knowledge/personal-brand/`, `voice.md`, recent digests
- Extract 3-5 enrichment details
- Inject into generation prompt

### Issue 4: No Angle Selection

Script assumes single angle, no mechanism for exploring multiple perspectives.

**Fix needed:**
- Add angle identification step (analyze source → propose 3-5 angles)
- Add `--angle` argument to select specific angle for generation
- Save angle metadata with output

### Issue 5: Multi-Variant in One Execution

Generating 3 variants simultaneously splits LLM attention.

**Fix needed:**
- Enforce one angle per execution
- Document sequential workflow (generate → review → next angle)
- Add conversation workspace pattern for multi-angle campaigns

---

## Proposed Solution Architecture

### New Workflow (3-stage)

**Stage 1: Analyze & Propose**
```bash
python3 n5_social_analyze.py --source reflection.md --output angles.json
```
Output:
```json
{
  "angles": [
    {"id": "founder-pain", "description": "Tool sprawl hurts context", "hook": "..."},
    {"id": "technical", "description": "Files > databases for personal AI", "hook": "..."},
    {"id": "build-story", "description": "Why I built my own AI OS", "hook": "..."}
  ],
  "enrichment": [
    "decade coaching founders",
    "4 years Careerspan",
    "77 stakeholder profiles",
    "11 automated agents"
  ]
}
```

**Stage 2: Generate (One Angle)**
```bash
python3 n5_social_generate.py \
  --angles angles.json \
  --select founder-pain \
  --target-length 250 \
  --output post.md
```

**Stage 3: Review & Iterate**
- Read output
- Approve or regenerate
- Move to next angle in fresh session

### File Structure

```
N5/scripts/
├── n5_social_analyze.py         # Stage 1: Analyze source, propose angles, scan knowledge
├── n5_social_generate.py        # Stage 2: Generate post for selected angle
├── n5_social_review.py          # Stage 3: Review checklist automation
└── modules/
    ├── knowledge_scanner.py     # Scan Knowledge/ for enrichment
    ├── angle_analyzer.py        # Identify angles from source
    └── voice_engine.py          # Apply voice.md rules
```

### Command Integration

```markdown
# N5/commands/social-post-generate.md

1. Analyze source: `n5_social_analyze.py --source {file}`
2. Review proposed angles
3. Select angle: "Generate angle #2 (technical)"
4. Execute: `n5_social_generate.py --angles angles.json --select technical`
5. Review output
6. Repeat steps 3-5 for additional angles
```

---

## Implementation Plan

### Priority 1: Create analyzer script
- [x] Document workflow in command `N5/commands/social-post-generate-multi-angle.md`
- [ ] Create `N5/scripts/n5_social_analyze.py`
- [ ] Create `N5/scripts/modules/knowledge_scanner.py`
- [ ] Create `N5/scripts/modules/angle_analyzer.py`

### Priority 2: Fix generator script
- [ ] Add `--source-file` argument
- [ ] Add hard length truncation
- [ ] Integrate knowledge enrichment
- [ ] Add angle selection

### Priority 3: Test end-to-end
- [ ] Test with `2025-10-20_zo-system-gtm` reflection
- [ ] Generate 3 angles sequentially
- [ ] Validate quality checklist
- [ ] Document lessons

---

## Immediate Next Action

Generate demo posts manually (via chat) using new workflow, then build scripts based on pattern.

**Test case:**
- Source: `N5/records/reflections/incoming/2025-10-20_zo-system-gtm.txt.transcript.jsonl`
- Angles: Founder pain, Technical diff, Build story
- Objective: Prime audience for demo booking

---

## Success Criteria

- [ ] Posts are 200-300 words (not 2,500+)
- [ ] At least 1 enrichment detail from Knowledge/ per post
- [ ] Angle is clear and distinct from other variants
- [ ] CTA aligns with objective (demo booking)
- [ ] Workflow documented and repeatable
- [ ] Scripts exist and work reliably

---

**Status:** In progress  
**Next:** Generate example posts manually, then script
