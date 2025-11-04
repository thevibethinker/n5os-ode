# N5 ARCHITECTURAL REDESIGN - FINAL IMPLEMENTATION PLAN v2.0

**Status:** READY FOR EXECUTION
**Date:** 2025-11-02
**Architect:** Vibe Architect

## ALL VETTING FIXES APPLIED ✅

Priority 1 (Blocking):
✅ Bootstrap problem - Two-stage update
✅ Loading mechanism - Hybrid embed+reference  
✅ Pre-flight protocol - 5-step explicit process
✅ Rubric quality - <5min checklist

Priority 2 (Important):
✅ Navigator scope - <7k hard limit
✅ Ben integration - Complete
✅ Git workflow - Added to planning_prompt
✅ Principle versioning - YAML schema

Priority 3 (Nice to have):
✅ Build order - Explicit sequence
✅ Testing strategy - 5 scenarios
✅ Hierarchy clarified - Prompts vs principles
✅ V cognitive load - Estimated

## CORE COMPONENTS

1. **planning_prompt.md** (~8-9k chars)
   - Think→Plan→Execute framework
   - Ben's velocity principles (COMPLETE)
   - P36+P37 patterns
   - Git workflow guidance

2. **thinking_prompt.md** (~8-9k chars)
   - First principles thinking
   - 46 mental models
   - Decision frameworks
   - Systems thinking

3. **navigator_prompt.md** (<7k chars HARD LIMIT)
   - Directory structure (3 levels)
   - Script inventory
   - Persona switching
   - Workflow patterns

4. **P36 + P37 Principles**
   - Separate orchestration (extensions)
   - Spec-driven regeneration (refactors)
   - Decision matrix between them

5. **29 Principles in YAML**
   - Version-tracked
   - Changelogged
   - Referenced from personas

6. **5 Updated Personas**
   - Pre-flight protocol embedded
   - Lightweight principle summaries
   - Prompt loading instructions

## EXECUTION: 6 PHASES, 13.5 HOURS

### Phase 1: Foundation + Bootstrap (4 hrs, 11 artifacts)
1A: Update 5 personas with loading stub (30 min)
1B: Build P36, P37, matrix, 3 prompts (2.5 hrs)
1C: Update 5 personas with full protocol (1 hr)

### Phase 2: Principle Migration (3 hrs, 27 principles)
Convert to YAML with versioning

### Phase 3: Persona Integration (2 hrs)
Embed principle summaries in 5 personas

### Phase 4: System Testing (1.5 hrs, 5 scenarios)
Validate all components work

### Phase 5: Documentation (2 hrs)
Guides, diagrams, reports

### Phase 6: Validation & Rollout (1 hr)
Final checks, go live

## KEY DESIGN DECISIONS

**Hybrid Embedding:**
- Name + Trigger + Pattern in persona (~300 chars each)
- Full YAML via reference when needed
- Total: ~2.4k chars for 8 principles (manageable)

**Pre-Flight Protocol (5 steps):**
1. Identify work type
2. Load appropriate prompt(s)
3. Review embedded principles
4. Load full YAML if triggered
5. Proceed with context

**Bootstrap Sequence:**
Phase 1A (stub) → Phase 1B (build) → Phase 1C (full)
Solves chicken-and-egg problem

## SUCCESS METRICS

Week 1:
- 90%+ correct prompt loading
- 60%+ principle citations
- Pre-flight automatic

Month 1:
- 50% fewer violations
- 5+ citations per conversation
- 95%+ pre-flight rate
- 30% less V clarification

## CODE MODIFICATION MATRIX

Extension (<30% change) → P36 (separate script)
Refactor (>50% change) → P37 (rubric regen)
Uncertain → P36 (safer default)

## NEXT STEPS

1. V reviews FINAL PLAN
2. V approves
3. V authorizes Phase 1
4. Architect → Builder handoff
5. Execute Phase 1 (4 hours)
6. Test bootstrap works
7. Continue to Phase 2

---

PLAN COMPLETE | ALL FIXES APPLIED | READY FOR IMPLEMENTATION
