---
created: 2026-02-03
last_edited: 2026-02-03
version: 1.3
provenance: con_NJlvnFnzUY6KsX9t
---

# Meta Resume Generator v2: Schema Alignment + Design Evolution

## Status

- ☑ **Phase 1**: Schema Alignment (COMPLETE)
- ⏸ **Phase 2**: Design Evolution (BLOCKED - awaiting synthesis layer)
- 🔄 **Phase 3**: Candidate Synthesis Skill (IN PROGRESS)

## Open Questions

1. ~~**Behavioral pills extraction**~~ → RESOLVED: Using "Spikes" instead. Extract from `skills[]` array — upward spikes (Excellent rating, high importance) and downward spikes (Gap/Fair rating, high importance). No LLM needed for extraction.

2. ~~**Section ordering**~~ → RESOLVED: V confirmed: (1) Spikes at top, (2) Verdict, (3) Risks/Gaps (trust-building), (4) Strengths, (5) Interview Questions, (6) Patterns, (7) Signal Strength.

3. **Two-page target**: With spikes added, may need to compress. Options: (a) reduce behavioral signals from 3→2, (b) reduce patterns, (c) accept 2.5 pages. V says going beyond 2 pages is fine but try to limit first.

## Checklist

### Phase 1: Schema Alignment (COMPLETE)
- [x] P1.1: Create input adapter that reads all decomposer outputs
- [x] P1.2: Update TypeScript interface to match decomposer schema
- [x] P1.3: Create mapping layer: decomposer outputs → generator input
- [x] P1.4: Add validation for required fields
- [x] P1.5: Test with hardik-flowfuse decomposer output

### Phase 2: Design Evolution (BLOCKED)
*Waiting on Phase 3 synthesis layer to provide deduplicated, narrative-ready content*

- [ ] P2.1: Add spikes section at top (5-10 spikes, 5 words max each)
- [ ] P2.2: Color-code spikes by importance
- [ ] P2.3: Indicate story-verified vs resume-only in spike styling
- [ ] P2.4: Reorder sections per Alex feedback
- [ ] P2.5: Compress whitespace while maintaining consistency
- [ ] P2.6: Generate test PDF, review with V

### Phase 3: Candidate Synthesis Skill (NEW)
*Multi-step pipeline that synthesizes candidate intelligence into employer-focused narratives*

- [x] P3.1: Create skill scaffold (`Skills/candidate-synthesis/`)
- [x] P3.2: Define pipeline architecture (5 steps)
- [x] P3.3: Create LLM prompts for each step
- [x] P3.4: Implement step1_gather.py (input collection)
- [x] P3.5: Implement step2_hiring_pov.py (POV generation)
- [x] P3.6: Implement step3_cluster.py (story clustering)
- [x] P3.7: Implement step4_resume_diff.py (resume comparison)
- [x] P3.8: Implement step5_narrate.py (final narrative)
- [ ] P3.9: Implement GDrive storage for Hiring POVs
- [ ] P3.10: Implement Airtable field updates
- [ ] P3.11: Test pipeline end-to-end with hardik-flowfuse
- [ ] P3.12: Update meta-resume-generator to consume synthesized_narrative.json

## Phases

### Phase 1: Schema Alignment

**Objective**: Make meta-resume-generator consume decomposer outputs directly instead of hand-crafted JSON.

**Affected Files**:
- `Skills/meta-resume-generator/scripts/generate-decoded.ts` (major refactor)
- `Skills/meta-resume-generator/scripts/adapter.ts` (NEW - input adapter)
- `Skills/meta-resume-generator/SKILL.md` (update usage docs)

**Changes**:

1. **Create `adapter.ts`** - Reads decomposer output directory:
   ```
   Input: /Careerspan/meta-resumes/inbox/<candidate>-<company>/
   Reads: scores_complete.json, overview.yaml, jd.yaml, profile.yaml
   Output: CandidateDecodedData object
   ```

2. **Field mappings**:
   | Decomposer Field | Generator Field |
   |-----------------|-----------------|
   | `overview.yaml → careerspan_score.overall` | `confidenceScore` |
   | `overview.yaml → recommendation.verdict` | `verdictText` |
   | `overview.yaml → recommendation.summary` | `verdictSummary` |
   | `scores_complete.json → skills[].skill_name` | Extract for spikes |
   | `scores_complete.json → skills[].rating` | Filter: Excellent→upSpikes, Gap/Fair→downSpikes |
   | `scores_complete.json → skills[].importance` | Sort order for spikes |
   | `scores_complete.json → skills[].evidence_type` | ✓✓ vs ✓ marker |
   | `scores_complete.json → signal_strength` | `signalStrength` |
   | `jd.yaml → title` | `candidateRole` |
   | `profile.yaml → candidate_name` | `candidateName` |

3. **Spike extraction** (no LLM needed):
   - Filter skills by rating
   - Sort by importance descending
   - Take top N (5 up, 3 down)
   - Truncate skill_name to ≤5 words

4. **Update `generate-decoded.ts`**:
   - Accept directory path as input (not JSON file)
   - Call adapter to load data
   - Rest of pipeline unchanged

**Unit Tests**:
- [ ] Adapter correctly reads hardik-flowfuse directory
- [ ] Field mappings produce valid CandidateDecodedData
- [ ] Missing optional fields handled gracefully
- [ ] Output PDF generates without errors

---

### Phase 2: Design Evolution

**Objective**: Implement Alex's feedback on visual design and information hierarchy.

**Affected Files**:
- `Skills/meta-resume-generator/scripts/template-decoded.html` (major update)
- `Skills/meta-resume-generator/scripts/generate-decoded.ts` (update interface for spikes)

**Changes**:

#### 2.1 Spikes Component (Top of Page 1)

**Concept**: At-a-glance bidirectional signal — what STANDS OUT about this candidate.

**Visual Design**:
```
┌─────────────────────────────────────────────────────────────────┐
│  ▲ 0→1 AI builder ✓✓   ▲ High autonomy ✓✓   ▲ Fast learner ✓   │
│  ▼ Node.js ramp        ▼ SOC 2 ownership    ▼ Async fit        │
└─────────────────────────────────────────────────────────────────┘
```

**Extraction Logic**:
- **Upward spikes (▲)**: Top 3-5 skills where `rating = "Excellent"`, ordered by `importance` desc
- **Downward spikes (▼)**: Top 2-3 skills where `rating in ["Gap", "Fair"]`, ordered by `importance` desc
- **Evidence marker**: `✓✓` for `evidence_type = "Story+profile"`, `✓` for `evidence_type = "Profile"` or `"Resume"`
- **Label**: Skill name shortened to ≤5 words

**Styling**:
- Upward: Purple background (`#EDE9FE`), purple text (`#7C3AED`)
- Downward: Amber background (`#FEF3C7`), amber text (`#D97706`)
- Pills are rounded, inline, 8pt font

#### 2.2 Section Reorder

**Page 1** (new order):
1. Header + Hero (name, role, context)
2. **Spikes** (NEW - scannable at glance, trust-building)
3. Verdict Box (score + summary)
4. Risks/Gaps to Probe (promoted - trust signal per Alex)
5. Why This Candidate Is Interesting (strengths)

**Page 2** (new order):
1. Interview Questions That Matter
2. How They Operate (Patterns)
3. Signal Strength bars
4. Methodology/Footer

#### 2.3 Whitespace Compression

- Reduce section margins from 16px → 12px
- Reduce item margins from 8px → 6px
- Keep consistent spacing pattern throughout
- Target: Fit in 2 pages, accept 2.5 if needed

**Unit Tests**:
- [ ] Spikes render correctly with color coding
- [ ] Story-verified vs resume-only visually distinguishable
- [ ] PDF fits in 2-2.5 pages
- [ ] All sections present and readable

---

## Success Criteria

1. ✅ Generator accepts decomposer output directory as input
2. ✅ No manual JSON crafting required
3. ✅ Spikes (up + down) visible at top of document
4. ✅ Spikes ordered by relevance (importance field)
5. ✅ Story-verified vs resume-only visually indicated (✓✓ vs ✓)
6. ✅ Risks/Gaps section retained and prominent (page 1)
7. ✅ Interview Questions section retained
8. ✅ Output fits in 2-2.5 pages
9. ✅ Test PDF generated for hardik-flowfuse

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Decomposer schema changes break generator | Medium | High | Version schema, validate on load |
| Skill names too long for pills | Medium | Medium | Truncate to 5 words, use title case |
| 2-page constraint forces cutting valuable content | Low | Medium | Accept 2.5 pages if needed |
| Color contrast insufficient | Low | Low | Test accessibility, ensure WCAG compliance |

## MECE Worker Division

### Drop 1: Schema Adapter (Pulse)
**Scope**:
- `Skills/meta-resume-generator/scripts/adapter.ts` (NEW)
- `Skills/meta-resume-generator/scripts/generate-decoded.ts` (modify CLI + interface)
- `Skills/meta-resume-generator/SKILL.md` (update docs)
- Reading/parsing decomposer outputs
- Spike extraction logic

**Must NOT touch**:
- Template HTML styling
- Visual design decisions
- Section ordering

### Drop 2: Design Evolution (Manual)
**Scope**:
- `Skills/meta-resume-generator/scripts/template-decoded.html`
- CSS styling for spikes
- Section reordering
- Whitespace optimization

**Must NOT touch**:
- Adapter logic
- Field mappings
- Decomposer integration

---

## Handoff

**Phase 1 → Pulse**: Single drop, straightforward TypeScript work
**Phase 2 → Manual drop**: V wants close control over design decisions

Ready for orchestration.
