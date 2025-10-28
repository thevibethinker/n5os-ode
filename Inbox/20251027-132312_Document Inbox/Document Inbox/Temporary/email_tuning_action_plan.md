# Follow-Up Email Generation: Tuning Action Plan

**Date:** 2025-10-12 18:10:00 ET  
**Purpose:** Practical guide for improving email writing quality and style  
**Based On:** Complete system analysis (see `file '/home/.z/workspaces/con_euHtayU1MFKWEqBr/email_generation_impact_map.md'`)

---

## Quick Summary

The follow-up email system has **two critical files** that control writing quality:

1. **`N5/prefs/communication/voice.md`** (v3.0.0) - Controls tone, lexicon, readability
2. **`N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md`** (v1.1.0) - Controls compression and structure

These files are **easy to tune** and have **immediate impact** on output quality.

---

## Understanding the Test Email

Looking at `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/follow_up_email_v11-1_TEST.md'`:

**What Worked Well:**
- ✅ Clear structure with headers (What it is / How it works / Why it matters)
- ✅ Professional tone maintained
- ✅ Specific details preserved (200K users, 100+ data points)
- ✅ Good compression (485 words vs. 600+ baseline)
- ✅ Resonant opening ("thoughtfulness about not creating unnecessary cycles")
- ✅ Inline Calendly link with confidence 0.90

**Potential Issues to Evaluate:**
- Opening paragraph warmth level (5/10) - is this right for the relationship?
- Formality level (Balanced) - could it be more casual given the humor in conversation?
- Use case descriptions - are they too detailed or just right?
- CTA structure - is the "If This Resonates" section clear enough?

---

## Phase 1: Voice File Tuning (Immediate Impact)

### Target File: `N5/prefs/communication/voice.md`

**Current Settings:**
```yaml
Tone Weights:
  Warmth: 0.80-0.85
  Confidence: 0.72-0.80
  Humility: 0.55-0.65

Readability:
  Flesch-Kincaid: 10-12
  Avg Sentence: 16-22 words
  Max Sentence: 32 words

Lexicon (Avoid):
  - get, make, take, go, have, do
  - leverage → use
  - reach out → get in touch
  - ASAP → absolute date
```

**Tuning Questions:**

1. **Are the tone weights right?**
   - Does warmth 0.80-0.85 produce the right level of friendliness?
   - Is humility 0.55-0.65 distinctive enough?
   - Test: Adjust warmth ±0.05 and regenerate

2. **Is the lexicon complete?**
   - Are there other verbs to avoid?
   - Are there preferred verbs missing?
   - Review recent emails for patterns

3. **Are readability targets optimal?**
   - FK 10-12: Is this accessible enough?
   - Avg 16-22 words: Does this feel natural?
   - Test with actual stakeholders

**Action Items:**

```markdown
[ ] Review 3-5 recent follow-up emails
[ ] Identify specific lexicon issues (words that feel off)
[ ] Test warmth adjustment: try 0.82-0.87 for warm contacts
[ ] Test readability: try FK 9-11 for more accessible tone
[ ] Document specific examples of voice inconsistencies
```

---

## Phase 2: Compression Tuning (Structure & Conciseness)

### Target File: `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md`

**Current Targets:**
```
Opening paragraph: 40-60 words
Use case description: 100-120 words each
Integration options: 60-80 words
Next steps: 60-80 words
Closing: 20-30 words
Total: 400-550 words
Compression: 20-30% reduction
```

**Tuning Questions:**

1. **Are use cases too detailed?**
   - Hamoon email: 115 words and 110 words per use case
   - Is "What/How/Why" structure too verbose?
   - Could you compress further without losing professionalism?

2. **Is bullet usage optimal?**
   - 4 bullets per use case: too many or just right?
   - Could some bullets be combined?

3. **Is the opening too long?**
   - Hamoon email: 58 words
   - Does it establish warmth quickly enough?

**Action Items:**

```markdown
[ ] Test 15-25% compression (more aggressive)
[ ] Test 25-35% compression (less aggressive)
[ ] Experiment with 3 bullets per use case instead of 4
[ ] Try shorter opening (30-40 words) for warm contacts
[ ] Compare outputs side-by-side
```

---

## Phase 3: Relationship Dial Calibration

### Target File: `N5/commands/follow-up-email-generator.md` (Step 3)

**Current Algorithm:**
```
warmthScore (0-10):
  - Personal anecdotes: +2
  - Humor instances: +1.5 each (max +3)
  - Compliments: +1 each (max +2)
  - Shared values: +1.5
  - First meeting: cap at 6.0

familiarityScore (0-10):
  - Prior meetings: +2 each (max +4)
  - Shared context: +2
  - Inside jokes: +1.5 each (max +3)

relationshipDepth = (warmth + familiarity) / 2
Map to 0-4 scale:
  0-2.0 → Stranger (0)
  2.1-4.0 → New Contact (1)
  4.1-6.0 → Warm Contact (2)
  6.1-8.0 → Partner (3)
  8.1-10.0 → Inner Circle (4)
```

**Tuning Questions:**

1. **Are the scoring weights right?**
   - Is humor worth +1.5 per instance?
   - Should shared values be weighted higher?

2. **Is the mapping accurate?**
   - Hamoon: warmth 6.5, familiarity 5.0 → depth 5.75 → Warm Contact (2)
   - Does "Warm Contact" feel right for first follow-up with shared values?

3. **Should first meetings have different rules?**
   - Current: warmth capped at 6.0 for first meetings
   - But Hamoon had high warmth (shared values, humor) - should this override?

**Action Items:**

```markdown
[ ] Review dial calibration for Hamoon email
[ ] Test alternative mapping: 4.0-5.5 → New Contact, 5.6-7.0 → Warm Contact
[ ] Experiment with removing first-meeting cap if warmth is high
[ ] Document edge cases (high warmth + first meeting)
```

---

## Phase 4: Resonance & Personalization

### Target File: `N5/commands/follow-up-email-generator.md` (Step 1)

**Current Logic:**
```
Resonance Types:
  - personal_anecdote
  - emotional_moment
  - shared_values
  - life_context
  - humor
  - insight
  - vulnerability
  - common_ground

Selection: 1-2 highest-confidence details
Placement: Email opening
```

**Tuning Questions:**

1. **Is resonance placement optimal?**
   - Hamoon email: "thoughtfulness about not creating unnecessary cycles"
   - Does this create enough warmth?
   - Should resonance also appear in closing?

2. **Are resonance types complete?**
   - Are there other personal moments to capture?
   - Should technical insights be weighted differently?

3. **Is confidence scoring accurate?**
   - What makes a detail "high confidence"?
   - Should shared values be weighted higher than humor?

**Action Items:**

```markdown
[ ] Review resonance extraction from Hamoon transcript
[ ] Test placing resonance in closing as well as opening
[ ] Experiment with 2-3 resonant details instead of 1-2
[ ] Document which resonance types create best connection
```

---

## Recommended Tuning Sequence

### Week 1: Quick Wins (Voice & Compression)

**Day 1-2: Baseline Assessment**
1. Generate 3-5 test emails with current settings
2. Review with stakeholders (internal team)
3. Document specific style issues

**Day 3-4: Voice Tuning**
1. Adjust tone weights based on feedback
2. Expand lexicon (avoid/prefer lists)
3. Test readability targets
4. Regenerate test emails

**Day 5: Compression Tuning**
1. Adjust word count targets
2. Test different compression percentages
3. Experiment with bullet usage
4. Compare outputs

### Week 2: Relationship & Resonance

**Day 1-2: Dial Calibration**
1. Review warmth/familiarity scoring
2. Test alternative mappings
3. Document edge cases
4. Refine algorithm

**Day 3-4: Resonance Enhancement**
1. Review resonance extraction
2. Test placement strategies
3. Experiment with multiple resonant details
4. Gather stakeholder feedback

**Day 5: Integration & Testing**
1. Combine all tuning changes
2. Generate full test suite
3. Compare against baseline
4. Document improvements

---

## Measurement Framework

### Quantitative Metrics

**Readability:**
- Flesch-Kincaid Grade Level (target: 10-12)
- Average sentence length (target: 16-22 words)
- Max sentence length (hard limit: 32 words)
- Paragraph structure (max 4 sentences)

**Structure:**
- Total word count (target: 400-550)
- Section word counts (opening, use cases, CTAs, closing)
- Compression percentage (20-30%)
- Bullet point count (per section)

**Voice:**
- Lexicon adherence (% preferred verbs used, % avoided verbs present)
- Tone consistency (warmth/confidence/humility ratings)

### Qualitative Metrics

**Voice Consistency:**
- Does it sound like V?
- Are distinctive phrases present?
- Is the tone appropriate for relationship?

**Effectiveness:**
- Does the opening create connection?
- Are use cases clear and compelling?
- Are CTAs actionable?
- Is the closing warm?

**Recipient Response:**
- Response rate
- Response time
- Quality of response (engagement level)
- Meeting booking rate (if applicable)

---

## Testing Protocol

### For Each Tuning Change:

1. **Generate Test Suite**
   - 3 emails with different relationship depths
   - 3 emails with different meeting types
   - 1 edge case (high warmth + first meeting)

2. **Compare Outputs**
   - Side-by-side with baseline
   - Quantitative metrics (word count, FK grade)
   - Qualitative assessment (tone, clarity)

3. **Gather Feedback**
   - Internal review (Logan, V)
   - Stakeholder response (if possible)
   - Document learnings

4. **Iterate**
   - Adjust parameters
   - Regenerate
   - Repeat

---

## Edge Cases to Test

1. **High Warmth + First Meeting**
   - Example: Hamoon (shared values, humor, but first interaction)
   - Question: Should formality stay balanced or shift casual?

2. **Low Context Meeting**
   - No clear action items or decisions
   - Question: How to structure follow-up?

3. **Multiple Stakeholders**
   - Email to group vs. individual
   - Question: How to calibrate tone for multiple recipients?

4. **Follow-Up After Long Gap**
   - Meeting was weeks/months ago
   - Question: How much context to re-establish?

5. **High Stakes Decision**
   - Partnership decision, funding, critical hire
   - Question: When to override warmth for directness?

---

## Documentation Template

### For Each Tuning Session:

```markdown
## Tuning Session: [Date]

**Target File:** [filename]
**Parameter Changed:** [specific parameter]
**Change:** [old value] → [new value]
**Rationale:** [why this change]

### Test Results

**Email 1: [Context]**
- Before: [metrics]
- After: [metrics]
- Assessment: [qualitative]

**Email 2: [Context]**
- Before: [metrics]
- After: [metrics]
- Assessment: [qualitative]

### Stakeholder Feedback
- [Feedback 1]
- [Feedback 2]

### Decision
- [ ] Keep change
- [ ] Revert change
- [ ] Iterate further

### Next Steps
- [Action 1]
- [Action 2]
```

---

## Quick Reference: Files to Tune

| Priority | File | What to Tune | Impact | Ease |
|----------|------|--------------|--------|------|
| 🔴 1 | `N5/prefs/communication/voice.md` | Tone weights, lexicon, readability | High | Easy |
| 🔴 2 | `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` | Word counts, compression rules | High | Easy |
| 🟡 3 | `N5/commands/follow-up-email-generator.md` (Step 3) | Dial calibration algorithm | Medium | Medium |
| 🟡 4 | `N5/commands/follow-up-email-generator.md` (Step 1) | Resonance extraction | Medium | Medium |
| 🟢 5 | `N5/prefs/communication/templates.md` | Structural patterns | Low | Easy |

---

## Next Immediate Actions

**Today (30 minutes):**
1. ✅ Review Hamoon email thoroughly
2. ✅ Document 3-5 specific improvements you want
3. ✅ Prioritize which aspect to tune first (voice? compression? dials?)

**Tomorrow (2 hours):**
1. Make first tuning changes to voice.md
2. Regenerate Hamoon email with new settings
3. Compare side-by-side
4. Document learnings

**This Week (5-7 hours):**
1. Complete voice and compression tuning
2. Generate test suite (5-7 emails)
3. Review with team
4. Document baseline improvements

---

## Tools & Commands

**To regenerate email with current settings:**
```bash
# Command structure (adapt to actual implementation)
python N5/scripts/generate_followup_email_draft.py \
  --transcript [path] \
  --output [path]
```

**To compare outputs:**
```bash
# Use diff or visual comparison
diff -u email_v1.md email_v2.md
```

**To validate metrics:**
```bash
# Check word count
wc -w email_draft.md

# Check readability (if textstat installed)
python -c "import textstat; print(textstat.flesch_kincaid_grade(open('email_draft.md').read()))"
```

---

## Success Criteria

**After tuning, you should see:**
- ✅ Voice consistency across different relationship depths
- ✅ Appropriate tone calibration (warm but professional)
- ✅ Optimal compression (concise but not terse)
- ✅ Strong openings (resonance + warmth)
- ✅ Clear CTAs (actionable, not vague)
- ✅ Stakeholder feedback improvement
- ✅ Higher response rates (if measurable)

---

## Resources

- **Full Impact Map:** `file '/home/.z/workspaces/con_euHtayU1MFKWEqBr/email_generation_impact_map.md'`
- **System Diagram:** `file '/home/workspace/Images/email_generation_impact_map.png'`
- **Test Email:** `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/follow_up_email_v11-1_TEST.md'`

---

*Generated: 2025-10-12 18:10:00 ET*
