# ARCHITECTURAL REDESIGN PLAN - VETTING REPORT
Date: 2025-11-02
Architect: Vibe Architect
Status: Pre-Implementation Review

## VETTING CHECKLIST

### ✅ PASSES - Core Design
- [x] Solves stated problem (principles not in context)
- [x] Dual cognitive bootstrap aligns with V's vision
- [x] P36 + P37 address LLM code editing risks
- [x] Three-prompt structure has clear separation
- [x] YAML migration strategy is sound
- [x] Persona integration is logical

### ⚠️ NEEDS REFINEMENT - Implementation Details

#### 1. CHARACTER COUNT CONCERNS

**Issue:** Three prompts + principles might exceed context limits

**Current estimates:**
- planning_prompt.md: ~8-10k chars (estimated)
- thinking_prompt.md: ~8-10k chars (estimated)  
- navigator_prompt.md: ~5-7k chars (estimated)
- 8 principles (Builder): ~3-4k chars
- Total per Builder session: ~19-24k chars

**Gemini 2.0 Flash context:** 1M tokens ≈ 4M chars → NOT a problem
**BUT:** We should still optimize for cognitive load, not just technical limits

**Fix:** Keep prompts focused, use references not full content

#### 2. NAVIGATOR PROMPT SCOPE CREEP

**Issue:** "System knowledge" is vague and could become massive

**Risk:** navigator_prompt.md becomes a 50k char monster

**Fix needed:** Define specific boundaries:
- N5 directory structure (high-level only)
- File naming conventions
- Script purposes (one-line each)
- Persona switching logic
- Common patterns (references, not full docs)

**Character budget:** <7k chars (enforced)

#### 3. PRE-FLIGHT PROTOCOL UNCLEAR

**Issue:** "Load planning_prompt.md" - how exactly?

**Missing specifications:**
- Does persona include prompt content inline?
- Or does persona reference prompt and load separately?
- What's the loading mechanism?
- How do we ensure it happens?

**Fix needed:** Explicit pre-flight protocol in persona design

#### 4. PRINCIPLE LOADING MECHANISM

**Issue:** "Load core 8 principles" - mechanically, how?

**Options:**
A) Embed principle YAML directly in persona prompt
B) Persona references principles, loads them separately  
C) Hybrid: Names in persona, full content loaded on-demand

**Decision needed:** Which approach? (I recommend A for reliability)

#### 5. PHASE 1 DEPENDENCIES

**Issue:** Phase 1 requires creating 3 prompts + 2 principles + decision matrix
That's 6 artifacts with interdependencies

**Risk:** Order matters. Creating them wrong order = rework

**Fix needed:** Explicit build order within Phase 1:
1. P36 YAML (needed for planning_prompt)
2. P37 YAML (needed for planning_prompt)
3. Decision matrix (needed for planning_prompt)
4. planning_prompt.md (references P36, P37, matrix)
5. thinking_prompt.md (independent)
6. navigator_prompt.md (independent)

#### 6. TESTING STRATEGY INCOMPLETE

**Issue:** Phase 4 lists test scenarios but not validation criteria

**Missing:**
- How do we know if a test passed?
- What constitutes success?
- Who runs the tests (automated or V manual)?
- How do we fix failures?

**Fix needed:** Explicit test validation protocol

#### 7. PRINCIPLE OVERLAP WITH PROMPTS

**Issue:** planning_prompt.md includes Think→Plan→Execute framework
BUT that overlaps with principles like P24 (Simulation Over Doing)

**Risk:** Redundancy or conflicting guidance

**Fix needed:** Clear hierarchy:
- Prompts = Cognitive frameworks (how to think)
- Principles = Operational rules (what to do)
- Prompts reference principles, not duplicate them

#### 8. BEN'S VELOCITY PRINCIPLES NOT FULLY INTEGRATED

**Issue:** We extracted Ben's wisdom but didn't integrate all of it

**Missing from planning_prompt.md:**
- "Prompting is a dark art" (experiment and iterate)
- "Don't say 'use an LLM', instruct directly"
- "Scripts calling Zo API for agentic steps"
- "Explicit job queues (like Huey) over file scanning"
- "SQLite + YAML over folder structures"

**Fix needed:** Add Ben's specific technical guidance to planning_prompt

#### 9. RUBRIC QUALITY CHECKPOINTS

**Issue:** P37 requires "V reviews rubric" but no criteria given

**Missing:**
- What makes a rubric "good enough"?
- What red flags should V look for?
- How detailed should rubric be?
- Can V request rubric regeneration?

**Fix needed:** Rubric quality checklist in P37

#### 10. VERSION CONTROL IMPLICATIONS

**Issue:** P37 says "version increment signals regeneration"
But we're in Git - need Git best practices

**Missing:**
- Commit message conventions for P37 usage
- Branch strategy (main vs feature branches)
- How to preserve v3 while testing v4
- Rollback procedure

**Fix needed:** Git workflow guidance in planning_prompt

### ✅ PASSES - Structural Design

- [x] Six-phase sequence is logical
- [x] Dependencies are manageable
- [x] Effort estimates are reasonable (~14 hours)
- [x] Success metrics are measurable
- [x] Risk mitigation is addressed

### ❌ FAILS - Critical Gaps

#### 11. WHAT TRIGGERS PRINCIPLE LOADING?

**Critical gap:** Personas have "pre-flight checklists" but WHO/WHAT enforces them?

**The fundamental question:**
If Builder persona says "Load planning_prompt.md before starting"...
...but current Builder persona doesn't have that instruction yet...
...how does the NEW instruction get loaded?

**This is a bootstrap problem.**

**Solution needed:** 
- Update ALL current personas FIRST with pre-flight instructions
- THEN build the new prompts and principles
- Phase sequence needs adjustment

**Revised Phase 1:**
1a. Update existing personas with pre-flight protocol (meta-step)
1b. Create planning_prompt.md
1c. Create thinking_prompt.md  
1d. Create navigator_prompt.md
1e. Create P36 + P37 YAML
1f. Create decision matrix

#### 12. COGNITIVE LOAD ON V

**Issue:** V will need to approve rubrics (P37 step 2)

**Missing:**
- How much time will this take V?
- How often will P37 be used?
- Is this sustainable long-term?

**Fix needed:** 
- Rubric review should be <5 min per instance
- Provide rubric quality heuristics to speed review
- Consider AI-assisted rubric validation before V sees it

#### 13. PRINCIPLE VERSIONING

**Issue:** Principles will evolve. How do we track versions?

**Missing:**
- Principle version numbers (P36 v1.0)
- Change history
- Deprecation strategy
- When to update vs create new principle

**Fix needed:** Add versioning metadata to YAML schema

### ⚠️ NEEDS REFINEMENT - Persona Strategy

#### 14. ARCHITECT PERSONA PARADOX

**Issue:** Architect persona designs personas
But Architect needs thinking_prompt.md to do this well
But thinking_prompt.md doesn't exist yet
But Architect is designing it

**This is a self-reference paradox.**

**Solution:** 
- Architect creates thinking_prompt v0.1 from research
- V reviews and refines
- thinking_prompt v1.0 becomes official
- Future Architects use v1.0 to improve it

#### 15. OPERATOR OVERLOAD

**Issue:** Operator loads planning_prompt + navigator_prompt

**Risk:** Too much to process before orchestrating

**Fix needed:** navigator_prompt must be extremely lean
Focus on "where things are" not "how to think"
Operator already has planning_prompt for thinking

## SCORING SUMMARY

**Design Quality:** 9/10 (excellent core design)
**Implementation Readiness:** 6/10 (needs refinement)
**Completeness:** 7/10 (missing critical details)
**Feasibility:** 8/10 (achievable with fixes)

**Overall:** 7.5/10 - GOOD but needs fixes before implementation

## CRITICAL FIXES REQUIRED

### Priority 1 (Blocking)
1. Fix bootstrap problem (#11) - Update existing personas first
2. Define principle loading mechanism (#4) - Embed vs reference
3. Specify pre-flight protocol (#3) - Exact mechanism
4. Add rubric quality criteria (#9) - V review guidelines

### Priority 2 (Important)
5. Bound navigator_prompt scope (#2) - <7k char limit
6. Integrate Ben's technical guidance (#8) - Complete velocity wisdom
7. Add Git workflow guidance (#10) - Version control best practices
8. Add principle versioning (#13) - Track changes over time

### Priority 3 (Nice to have)
9. Explicit Phase 1 build order (#5)
10. Complete testing strategy (#6)
11. Clarify prompt/principle hierarchy (#7)
12. Estimate V cognitive load (#12)

## RECOMMENDED CHANGES

### Change 1: Revise Phase 1 to Address Bootstrap

**OLD Phase 1:**
1. Create planning_prompt.md
2. Create thinking_prompt.md
3. Create navigator_prompt.md
4. Migrate P36 to YAML
5. Migrate P37 to YAML
6. Create decision matrix

**NEW Phase 1:**
1a. Update ALL existing personas with pre-flight protocol stub
1b. Create P36 YAML
1c. Create P37 YAML  
1d. Create decision matrix
1e. Create planning_prompt.md (refs P36, P37, matrix)
1f. Create thinking_prompt.md
1g. Create navigator_prompt.md (<7k chars)
1h. Update personas again with full pre-flight (loads prompts)

### Change 2: Add Explicit Loading Mechanism

**Decision: Embed principles in persona prompts**

Why: Reliability. References can fail. Embedding guarantees availability.

Implementation:


Lightweight: Just name, trigger, pattern (not full YAML)
Full YAML: Available in /Knowledge/architectural/principles/ for reference

### Change 3: Rubric Quality Heuristics

Add to P37 YAML:



### Change 4: Navigator Scope Definition



### Change 5: Pre-Flight Protocol Specification

**In each persona prompt, add:**



## FINAL RECOMMENDATIONS

### Recommendation 1: Implement Fixes Before Building

Do NOT start Phase 1 until Priority 1 fixes are incorporated.

**Rationale:** Bootstrap problem (#11) will cause failure if not fixed first.

### Recommendation 2: Pilot Test with One Persona

After Phase 1, test with Builder only before rolling out to all personas.

**Rationale:** Validate loading mechanism works before scaling.

### Recommendation 3: Iterate on Prompts

Treat planning/thinking/navigator prompts as v0.1 initially.
Refine based on actual usage.

**Rationale:** Ben's wisdom - "experiment and iterate"

### Recommendation 4: Measure Cognitive Load on V

Track time V spends on rubric reviews in P37.
If >10 min per review, add AI-assisted pre-validation.

**Rationale:** System should help V, not burden V.

## CONCLUSION

**The plan is GOOD but needs FIXES before implementation.**

Core design is sound. P36 + P37 are solid. Three-prompt structure makes sense.

But critical details are missing (bootstrap problem, loading mechanism, rubric quality).

**Status: NOT READY for immediate implementation**
**Action: Apply Priority 1 fixes, then proceed**

**Estimated fix time:** 2 hours of planning refinement
**Benefit:** Prevents 5-10 hours of rework during build

## NEXT STEP

V decides:
A) Apply fixes now, then authorize Phase 1
B) Start Phase 1 and fix issues as encountered (riskier)
C) Request further clarification on any fix

