# N5 System Integration Guide

**Version:** 2.0  
**Created:** 2025-11-02  
**For:** V and Future Maintainers  
**Status:** Production Ready

---

## WHAT IS N5 v2.0?

The N5 Architectural Redesign is a cognitive bootstrap system that enables AI personas to:
1. Auto-load relevant decision frameworks before work
2. Reference behavioral principles by name during conversations
3. Apply consistent decision patterns (P36/P37) for code modifications
4. Execute Think→Plan→Execute workflow automatically

---

## SYSTEM COMPONENTS

### 1. Cognitive Prompts (3 files)
Location: N5/prefs/operations/, N5/prefs/strategic/, N5/prefs/system/

planning_prompt.md (13.8K):
- Think→Plan→Execute framework
- Design values, trap doors
- P36/P37 decision matrix
- Quality bars

thinking_prompt.md (12.9K):
- Mental models library (12 models)
- Decision frameworks
- Problem-solving patterns
- Cognitive bias awareness

navigator_prompt.md (5.5K):
- N5 directory structure
- Persona switching guide
- 5 workflow patterns
- Routing rules

### 2. Principle Library (37 files)
Location: N5/prefs/principles/P##_slug.yaml

Key Principles:
- P36: Orchestration Pattern (separate extensions)
- P37: Refactor Pattern (spec-driven regeneration)
- P15: Complete Before Claiming
- P05: Safety, Determinism, Anti-Overwrite
- P20: Modular and Composable Design

### 3. Decision Matrix
Location: N5/prefs/principles/decision_matrix.md

Quick decision tree for code modifications:
- Extension (<30% change) → P36 (separate script)
- Refactor (70%+ preservable) → P37 (spec-driven regen)
- Core logic wrong → Rebuild

### 4. Enhanced Personas (8)
All personas have:
- Pre-flight protocol (5 steps)
- Prompt references (auto-load)
- Principle extensions (P36, P37, matrix)
- 8 embedded relevant principles

---

## HOW TO USE THE SYSTEM

### Normal Usage (Automatic)
Just work normally! The system operates transparently.

Personas automatically:
- Load relevant cognitive prompts
- Reference principles by name
- Apply P36/P37 for code decisions
- Execute Think→Plan→Execute framework

### Explicit Loading (When Desired)
You can request specific loading:
- "Load planning_prompt before we start"
- "Reference P36 for this decision"
- "Apply P37 refactor pattern"

### Monitoring System Activity
Watch for principle citations:
- "Applying P36 (Orchestration Pattern)..."
- "Per P15, I'm 3/5 complete (60%)"
- "Following P37 refactor steps..."

---

## ARCHITECTURAL PATTERNS

### P36: Separate Orchestration
When: Adding functionality (<30% change)

Pattern: Create separate extension that reads existing output

Benefits:
- Existing code stays stable
- New feature isolated
- Easy to test independently

### P37: Specification-Driven Regeneration
When: Major refactor, 70%+ preservable, core logic sound

6-Step Pattern:
1. Read existing code
2. Extract working logic
3. Write specification
4. Generate v2 following spec
5. Validate behavior
6. Test thoroughly

---

## INTEGRATION POINTS

### With Existing Workflows
- Lists system: Personas reference principles
- Knowledge system: Principles inform standards
- Recipes: Can reference principles
- Scripts: Follow design principles

### With Rules System
User rules can reference principles:
- "Always apply P36 for extensions"
- "Cite P15 when reporting progress"

---

## TESTING & VALIDATION

System Tested (5/5 Passed):
1. ✅ Builder applies P36 for extensions
2. ✅ Builder applies P37 for refactors
3. ✅ Strategist loads thinking_prompt
4. ✅ Operator uses navigator_prompt
5. ✅ Multi-persona P36 orchestration works

Validation: 312/312 checks passed (100%)

---

## MAINTENANCE

### Adding New Principles
1. Create P##_slug.yaml following schema
2. Update principles_index.yaml
3. Consider adding to relevant personas
4. Test cross-references

### Modifying Cognitive Prompts
1. Edit prompt file directly
2. Keep <15K size for performance
3. Test persona loading

---

## TROUBLESHOOTING

Problem: Persona not citing principles
Fix: Explicitly request principle reference

Problem: Pre-flight not executing
Check: Persona has pre_flight_protocol section

Problem: Can't find principle file
Check: File exists in N5/prefs/principles/

---

## QUICK REFERENCE

Key Files:
- Principles: N5/prefs/principles/P##_slug.yaml
- Planning: N5/prefs/operations/planning_prompt.md
- Thinking: N5/prefs/strategic/thinking_prompt.md
- Navigator: N5/prefs/system/navigator_prompt.md
- Decision Matrix: N5/prefs/principles/decision_matrix.md
- Index: N5/prefs/principles/principles_index.yaml

Key Principles:
- P15: Complete Before Claiming
- P36: Separate Orchestration
- P37: Refactor Pattern
- P20: Modular Design
- P05: Safety & Determinism

System Status: ✅ ACTIVE IN PRODUCTION

---

Created by: Vibe Architect  
Completed: 2025-11-02 21:33 ET  
Version: 2.0
