# N5 Architectural System Overview

**Version:** 3.0  
**Updated:** 2025-11-02  
**Status:** Production

---

## What This Is

N5 is V's personal AI operating system. The architectural redesign (Oct-Nov 2025) transformed N5 from ad-hoc guidelines into a structured, principle-driven system with 37 codified principles, 8 specialized personas, and 27 operational protocols.

This isn't theoretical architecture. It's working infrastructure that governs every AI interaction, file operation, and workflow execution.

---

## Three-Layer Architecture

### Layer 1: Principles (37 YAML files)
**Location:** N5/prefs/principles/

Core rules that govern system behavior. Each principle is a YAML file with unique ID, trigger conditions, pattern specification, examples, and anti-patterns.

**Categories:**
- Core (P0.1-P4): LLM-first, SSOT, voice integration, ontology weighting
- Safety (P5-P7, P11, P19, P21, P23): Anti-overwrite, dry-run, error handling, trap doors
- Quality (P15-P16, P18, P20, P28, P30, P33): Complete before claiming, state verification, plan DNA
- Design (P8-P10, P13-P14, P22, P35): Context efficiency, naming, language selection
- Execution (P24-P27, P29, P31-P32, P34): Simulation, feedback loops, nemawashi, simple over easy
- Advanced (P36-P37): Orchestration, refactor patterns

**Schema:** All principles validate against N5/schemas/principle.schema.json

### Layer 2: Cognitive Prompts (3 active)
**Location:** N5/prefs/operations/ and N5/prefs/strategic/

Mental models and frameworks for complex work:

1. **Planning Prompt** (planning_prompt.md) - Think-Plan-Execute framework
2. **Thinking Prompt** (thinking_prompt.md) - Strategic analysis patterns
3. **Navigator Prompt** (navigator_prompt.md) - N5 structure and organization

### Layer 3: Personas (8 specialized)
**Status:** All personas v2.0+ with full integration

1. Vibe Operator (v1.1) - Execution, navigation, persona routing, risk assessment
2. Vibe Strategist (v2.2) - Pattern extraction, strategic frameworks
3. Vibe Builder (v2.0) - Script/workflow execution, infrastructure
4. Vibe Teacher (v2.1) - Technical explanation, learning facilitation
5. Vibe Writer (v2.1) - V-voice content, documentation
6. Vibe Architect (v1.2) - Persona design, prompt engineering
7. Vibe Debugger (v2.0) - Verification, principle compliance, testing
8. Vibe Researcher (v2.0) - Information gathering, synthesis

**Each persona includes:** Core identity, pre-flight protocol (5 steps), 8 embedded principles, cognitive prompt references, routing rules, quality standards.

---

## How It Works

### Pre-Flight Protocol
Before substantial work, personas execute 5-step protocol:

1. Identify work type (build, research, documentation, strategy, investigation)
2. Load prompts (relevant cognitive frameworks)
3. Review principles (embedded principles, load extended if needed)
4. Apply context (use loaded frameworks and principles)
5. Execute (proceed with full understanding)

### Principle Application
Principles activate automatically via trigger conditions defined in YAML when_to_apply field.

### Persona Routing
Operator acts as implicit quarterback, routing to specialists:
- Builder: Script/system implementation
- Architect: Design work, persona creation
- Strategist: Strategic analysis
- Writer: Documentation, V-voice content
- Teacher: Technical explanation
- Debugger: Verification, testing
- Researcher: Information gathering

### Risk Assessment
Before destructive operations:
1. Run N5/scripts/risk_scorer.py
2. Check file protections (n5_protect.py)
3. Assess dependencies
4. Show blast radius if high-risk
5. Require confirmation

---

## Migration History

Phase 1 (Conv 1-2): Bootstrap foundation + template system  
Phase 2 (Conv 3): Full persona updates to v2.0+  
Phase 3 (Conv 4): Safety & quality principles (13 principles)  
Phase 4 (Conv 5): Design & execution principles (10 principles)  
Phase 5 (Conv 6): Advanced principles + system testing (14 principles)  
Phase 6 (Conv 7): Documentation + integration

**Result:** 37 principles codified, 8 personas integrated, 3 cognitive prompts active

See N5/projects/architectural-redesign/MIGRATION_HISTORY.md for detailed timeline

---

## Integration Points

### System Integration
- Zo system prompts - Personas define AI behavior
- User rules - Conditional rules reference principles by name
- Scripts - Validate against principles (safety checks, risk scoring)
- Workflows - Execute with principle compliance

### File Organization
N5/prefs/principles/ (37 YAML principle files)
N5/prefs/operations/ (27 operational protocols)
N5/schemas/ (JSON schemas for validation)
N5/scripts/ (Enforcement tools)
Knowledge/architectural/ (This documentation layer)

---

## Key Design Decisions

**Why YAML for Principles?**
Human-readable (P1), machine-parseable, schema-validated, version-controlled, cross-reference support.

**Why Pre-Flight Protocol?**
Ensures context loading before work, prevents working without frameworks, maintains principle awareness.

**Why Persona Specialization?**
Clear domain boundaries, efficient context usage (P8), quality standards per domain, intelligent routing (P36).

**Why Three Layers?**
Principles = What (rules), Prompts = How (frameworks), Personas = Who (specialists). Separation enables independent evolution.

---

## Quality Standards

All architecture components must:
- Follow P1 (human-readable first)
- Maintain P2 (single source of truth)
- Support P8 (minimal context, maximal clarity)
- Enable P15 (complete before claiming)
- Document assumptions (P21)

---

## Future Evolution

Planned: Automated principle compliance testing, cross-principle dependency mapping, usage analytics per principle, persona performance metrics.

Principles: New principles added via structured process. Existing principles evolve with changelog. Deprecated principles archived, not deleted. Schema versioning for backward compatibility.

---

## Quick Reference

Find principles: ls N5/prefs/principles/P*.yaml
Validate principle: Check against N5/schemas/principle.schema.json
Switch persona: set_active_persona with persona_id
Check protection: python3 N5/scripts/n5_protect.py check <path>
Assess risk: python3 N5/scripts/risk_scorer.py

---

Related Documentation:
- Knowledge/architectural/PRINCIPLE_USAGE_GUIDE.md
- Knowledge/architectural/README.md
- N5/prefs/system/nuance-manifest.md
- N5/projects/architectural-redesign/BUILD_STATUS.md

---

Last updated: 2025-11-02 21:09 ET
