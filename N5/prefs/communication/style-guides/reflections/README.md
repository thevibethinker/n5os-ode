# Reflection Style Guides

**Purpose:** Transform raw voice reflections into publication-ready content across 11 block types (B50-B99)

**Registry:** `file 'N5/prefs/reflection_block_registry.json'`  
**Voice Profile:** `file 'N5/prefs/communication/voice.md'`  
**Transformation Library:** `file 'N5/prefs/communication/style-guides/transformation-pairs-library.md'`

---

## Block Type Index

### Internal Reflection (Personal/Professional)

- **B50** — `file 'B50-personal-reflection.md'` — Stream-of-consciousness self-reflection
- **B60** — `file 'B60-learning-synthesis.md'` — Insights from research, reading, conversations
- **B70** — `file 'B70-thought-leadership.md'` — Original thinking for professional audiences
- **B71** — `file 'B71-market-analysis.md'` — Market trends, competitive landscape
- **B72** — `file 'B72-product-analysis.md'` — Product decisions, feature prioritization, UX
- **B73** — `file 'B73-strategic-thinking.md'` — High-level strategy, positioning, vision

### External Communication

- **B80** — `file 'B80-linkedin-post.md'` → `file '../linkedin-posts.md'` — LinkedIn posts (symlink to main guide)
- **B81** — `file 'B81-blog-post.md'` — Long-form blog posts (800-2000 words)
- **B82** — `file 'B82-executive-memo.md'` — Formal memos for stakeholders

### Meta-Cognitive

- **B90** — `file 'B90-insight-compound.md'` — Connect insights across multiple reflections
- **B91** — `file 'B91-meta-reflection.md'` — Reflection on reflection practice itself

---

## Style Guide Structure

Each guide follows a consistent template:

1. **Header** — Block ID, domain, voice profile, auto-approve threshold
2. **Purpose** — What this block type is for
3. **Structure** — Typical flow and organization
4. **Tone & Voice** — Core characteristics, what to avoid
5. **Lexicon** — Block-specific vocabulary and phrases
6. **Templates** — 2-3 structural templates
7. **Transformation Guidance** — Raw → Refined transforms
8. **Examples** — 2-3 concrete before/after examples
9. **QA Checklist** — Quality assurance before publishing

---

## Usage Guidelines

### Auto-Approve Thresholds

| Block Type | Threshold | Rationale |
|------------|-----------|-----------|
| B50, B60, B71-73, B90-91 | 10 blocks | Internal reflections, lower risk |
| B70, B82 | 5 blocks | External-facing professional, moderate review |
| B80, B81 | 0 blocks | Always review before publishing |

**Threshold meaning:** AI can auto-approve after N blocks of demonstrated quality. Below threshold, requires human review.

### Processing Workflow

1. **Capture:** Write raw reflection in preferred medium (voice note, Zo chat, text)
2. **Classify:** Identify block type (B50-B99) based on content and purpose
3. **Transform:** Apply style guide to refine raw → publication-ready
4. **Review:** Human review if below auto-approve threshold
5. **Publish:** Internal (Knowledge) or external (LinkedIn, blog, memo)

### Choosing the Right Block Type

**Decision tree:**

- **Personal growth, emotions, self-awareness?** → B50
- **Learning from external sources?** → B60
- **Professional thought leadership?** → B70
- **Market/competitive analysis?** → B71
- **Product decisions?** → B72
- **Company strategy?** → B73
- **Short-form social post?** → B80
- **Long-form article?** → B81
- **Formal stakeholder communication?** → B82
- **Connecting multiple past reflections?** → B90
- **Thinking about the reflection system itself?** → B91

---

## Quality Standards

### Universal Requirements (All Blocks)

- **Specificity:** Concrete details over abstractions
- **Voice consistency:** Matches V's voice profile
- **Structure clarity:** Easy to scan and navigate
- **Honest:** No false polish or performative vulnerability
- **Actionable:** Leads to insight, decision, or next question

### Domain-Specific Standards

**Internal blocks (B50-73, B90-91):**
- Preserves raw thinking and uncertainty
- Includes context and "why this matters now"
- Documents questions, not just answers
- Honest about what's unclear or evolving

**External blocks (B70, B80-82):**
- Publication-ready (no placeholders or TODOs)
- Professional but conversational
- Clear value for reader
- Strong examples/evidence
- Passes "would I actually post this?" test

---

## System Integration

### Related Files

- **Block Registry:** `file 'N5/prefs/reflection_block_registry.json'` — Canonical definition of all block types
- **Voice Profile:** `file 'N5/prefs/communication/voice.md'` — V's communication patterns and preferences
- **Transformation Library:** `file 'N5/prefs/communication/style-guides/transformation-pairs-library.md'` — Common raw → refined patterns
- **Other Style Guides:**
  - `file '../linkedin-posts.md'`
  - `file '../follow-up-emails.md'`
  - `file '../blurbs.md'`

### Processing Scripts

- **Session State Manager:** `file 'N5/scripts/session_state_manager.py'` — Manages conversation context
- **Reflection Processor:** (Future) Automated transformation pipeline

---

## Maintenance

### Version History

- **v1.0** (2025-10-26) — Initial style guides for all 11 block types
  - Created full guides for B50, B60, B70-73, B81-82, B90-91
  - Linked B80 to existing LinkedIn posts guide
  - Established template structure and quality standards

### Future Improvements

- [ ] Usage analytics (which blocks used most/least)
- [ ] A/B testing of transformation approaches
- [ ] User feedback on publication-ready quality
- [ ] Automated style guide suggestions based on patterns
- [ ] Cross-block pattern detection (insight mining)

### Monthly Review

Meta-reflection (B91) should evaluate:
- Which style guides are working?
- Which need adjustment?
- Are thresholds set correctly?
- Is the 11-block taxonomy still useful, or should it evolve?

---

## Success Criteria

The style guide system is successful when:

1. ✅ **Capture friction low:** Easy to write raw reflections without worrying about structure
2. ✅ **Transformation clear:** Obvious how to refine raw → publication-ready using guides
3. ✅ **Quality consistent:** Output matches V's voice and professional standards
4. ✅ **System invisible:** Focus on thinking, not on "doing the system correctly"
5. ✅ **Insights actionable:** Reflections inform decisions and behavior

**Current Status:** System complete, ready for production use

---

**Last Updated:** 2025-10-26  
**Maintainer:** V  
**System:** N5 Operating System
