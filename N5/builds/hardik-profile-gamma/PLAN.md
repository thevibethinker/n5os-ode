---
created: 2026-01-29
last_edited: 2026-01-29
version: 1.0
provenance: con_zJrgL9dNFQim8Fdg
---

# PLAN: Hardik Candidate Profile Gamma Site

## Build Metadata
- **Slug**: `hardik-profile-gamma`
- **Type**: `content`
- **Goal**: Create a shareable Gamma webpage showcasing candidate H. for FlowFuse employer review
- **Source**: `N5/builds/careerspan-profile-output-v1/output/hardik-profile-v3.md`

---

## Open Questions

☑ **Resolved: Careerspan styling** — Use professional dark/light modern aesthetic with teal/blue accent colors based on www.mycareerspan.com visual identity
☑ **Resolved: PII handling** — First name/initial only (H.), no full name, email, phone, address
☑ **Resolved: Content length** — Shorten significantly for visual impact; prioritize for busy founder decision-making

---

## Alternatives Considered (Nemawashi)

| Alternative | Description | Decision |
|-------------|-------------|----------|
| Full Pulse multi-Drop | 3+ parallel workers | ❌ Overkill for single artifact |
| Single-thread all phases | One conversation, two phases | ✅ **Selected** — Clean, low overhead |
| Manual Gamma UI | Build in browser | ❌ Less reproducible |

**Decision**: Single-thread execution with 2 sequential phases. No Pulse orchestration needed for this scope.

---

## Checklist

### Phase 1: Content Optimization
- ☑ Read source profile document
- ☑ Remove PII (keep first initial only)
- ☑ Prioritize content by visual importance for founder audience
- ☑ Condense sections significantly (target 50% reduction) → achieved 60% reduction
- ☑ Reorder for "above the fold" impact
- ☑ Output optimized markdown ready for Gamma

### Phase 2: Gamma Generation
- ☑ Check Gamma API key availability
- ☑ Configure generation parameters (webpage, professional tone)
- ☑ Apply Careerspan styling direction
- ☑ Generate page with --wait
- ☑ Verify output, capture URL → https://gamma.app/docs/wte8uh7gme8fnfa
- ☑ Return shareable link to V

---

## Phase 1: Content Optimization

**Objective**: Transform the 700+ word analysis document into a punchy, visually-prioritized webpage optimized for a busy founder making a 30-second "should I meet this person" decision.

### Content Priority Stack (Visual Hierarchy)

1. **HERO**: One-sentence verdict + candidate identifier (H. | AI Engineer)
2. **IMMEDIATE VALUE**: What you're buying (3-4 bullets max, quantified)
3. **HONEST RISKS**: What you're NOT buying (2-3 bullets max)
4. **DECISION FRAMEWORK**: Simple yes/no conditions
5. **MEETING QUESTIONS**: 3-4 must-ask questions (if they decide to meet)
6. **FOOTER**: Careerspan + CorridorX branding

### Content Transformations

| Original Section | Action | Rationale |
|------------------|--------|-----------|
| "Should You Take This Meeting?" | **PROMOTE** to hero headline | First thing founder sees |
| "What You're Buying" table | **CONDENSE** to 4 tight bullets | Tables don't render well in Gamma cards |
| "What You're NOT Buying" table | **CONDENSE** to 3 bullets | Keep balance |
| "Risk Profile" section | **MERGE** into "What You're NOT Buying" | Reduce section count |
| "What The Meeting Will Reveal" | **TRIM** to 3-4 questions only | Remove verbose preamble |
| "Decision Framework" table | **SIMPLIFY** to yes/no checklist | Clean decision logic |
| "Bottom Line" | **DEMOTE** to subtle footer | Hero already has verdict |

### Affected Files
- Input: `N5/builds/careerspan-profile-output-v1/output/hardik-profile-v3.md`
- Output: `N5/builds/hardik-profile-gamma/artifacts/optimized-content.md`

### Success Criteria
- [ ] No PII beyond first initial
- [ ] Content ≤350 words (50% reduction)
- [ ] All sections fit single-screen mental model
- [ ] Founder can decide "meet or pass" in <30 seconds reading

---

## Phase 2: Gamma Webpage Generation

**Objective**: Generate a professional, shareable Gamma webpage with Careerspan visual identity.

### Gamma Configuration

```bash
bun run Skills/gamma/scripts/gamma.ts generate "<optimized_content>" \
  --mode generate \
  --format webpage \
  --tone "confident and professional" \
  --audience "startup founders and hiring managers" \
  --amount brief \
  --images aiGenerated \
  --image-model flux-1-quick \
  --image-style "professional tech aesthetic, dark mode, teal accents" \
  --visibility unlisted \
  --instructions "Careerspan candidate profile for employer review. Clean, modern design. Dark background preferred. Teal/blue accent colors. Minimal but impactful visuals. Professional recruiter tone." \
  --wait
```

### Styling Direction (from mycareerspan.com)
- **Colors**: Dark background (#1a1a2e-ish), teal/cyan accents
- **Typography**: Clean, modern sans-serif
- **Layout**: Card-based sections, generous whitespace
- **Imagery**: Professional, tech-forward, minimal
- **Tone**: Confident, data-driven, decisive

### Affected Files
- Input: `N5/builds/hardik-profile-gamma/artifacts/optimized-content.md`
- Output: Gamma-hosted URL (captured in artifacts)

### Success Criteria
- [ ] Gamma page generated successfully
- [ ] Visual style matches Careerspan aesthetic
- [ ] Page is shareable (unlisted visibility)
- [ ] URL captured and returned to V

---

## Trap Doors

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| Gamma visibility: unlisted | **Easy** — Can change via Gamma UI | Safe default |
| Image model choice | **Easy** — Regenerate if needed | Using budget model for speed |
| Content condensation | **Medium** — Original preserved | Can regenerate from source |

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Gamma API failure | Low | Check key exists before generation |
| Styling mismatch | Low | Can regenerate with different instructions |
| Over-condensation | Low | V can request more detail added back |

---

## Execution Mode

**Single-thread sequential execution** — No Pulse orchestration needed.

Builder can execute both phases in one conversation:
1. Optimize content → save to artifacts
2. Generate Gamma → return URL

---

## Success Criteria (Build-Level)

- [ ] Shareable Gamma URL delivered to V
- [ ] Page persuasively presents candidate H. without PII
- [ ] Employer can make "meet/pass" decision in <30 seconds
- [ ] Visual design consistent with Careerspan brand

---

*Plan created by Architect | Ready for execution*
