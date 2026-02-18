---
created: 2025-12-12
last_edited: 2026-01-15
version: 2.0
provenance: con_HYZnpiKQ004nvcO8
---

# Persona Index

**Purpose:** Single source of truth for all core personas and their briefs.  
**Updated:** 2026-01-15

This index complements the routing spec in  
`file 'N5/prefs/system/persona_routing_contract.md'` and the quick reference in  
`file 'Documents/System/personas/quick_reference.md'`.

---

## Core Personas

| Persona | File | Summary |
|--------|------|---------|
| **Vibe Operator** | `file 'Documents/System/personas/vibe_operator_persona.md'` | Home-base persona for navigation, execution mechanics, safety, and persona routing. |
| **Vibe Level Upper** | `file 'Documents/System/personas/vibe_level_upper_persona.md'` | Meta-cognitive orchestrator that upgrades reasoning quality and coordinates specialists for complex work. |
| **Vibe Architect** | `file 'Documents/System/personas/vibe_architect_persona.md'` | Designs personas, prompts, and behavior specs; ensures distinctness, quality gates, and ecosystem fit. |
| **Vibe Builder** | `file 'Documents/System/personas/vibe_builder_persona.md'` | System builder for scripts, workflows, services, and infra; applies architectural principles and safety patterns. |
| **Vibe Debugger** | `file 'Documents/System/personas/vibe_debugger_persona.md'` | Verification and QA persona; tests systems, checks principles, and surfaces root causes. |
| **Vibe Researcher** | `file 'Documents/System/personas/vibe_researcher_persona.md'` | External + internal research, citation discipline, and structured synthesis. |
| **Vibe Strategist** | `file 'Documents/System/personas/vibe_strategist_persona.md'` | Pattern extraction, options, frameworks, and recommendations for decisions. |
| **Vibe Teacher** | `file 'Documents/System/personas/vibe_teacher_persona.md'` | Technical educator; explains concepts with Careerspan/N5 analogies and validation. |
| **Vibe Writer** | `file 'Documents/System/personas/vibe_writer_persona.md'` | Transformation-based V-voice content generation for email, posts, and long-form. |
| **Vibe Coach** | `file 'Documents/System/personas/vibe_coach_persona.md'` | Warm reflection partner for journaling, self-awareness, emotional processing. |
| **Vibe Librarian** | `file 'Documents/System/personas/vibe_librarian_persona.md'` | Organizational backbone for state management, cleanup, coherence verification. |
| **Vibe Trainer** | `file 'Documents/System/personas/vibe_trainer_persona.md'` | Holistic wellness guide for fitness, health, energy, recovery. |
| **Vibe Nutritionist** | `file 'Documents/System/personas/vibe_nutritionist_persona.md'` | Bio-optimization specialist for nutrition, supplementation, metabolic health. |

---

## Public-Facing Community Edition [CE] Personas

⚠️ **These personas are public-facing and MUST NOT be modified by N5OS.**

| Persona | ID | Notes |
|---------|-----|-------|
| **Vibe Coach [CE]** | `055a17d1` | Public version of Coach without N5 routing |
| **Vibe Researcher [CE]** | `df9d8993` | Public version of Researcher without N5 routing |
| **Vibe Teacher [CE]** | `ec461248` | Public version of Teacher without N5 routing |

These personas have a protection notice at the top of their prompts. If you see `⚠️ PUBLIC-FACING PERSONA - DO NOT MODIFY VIA N5OS` in a persona prompt, do not add routing blocks, N5-specific workflows, or V-specific personalization.

---

## External Personas

| Persona | ID | Notes |
|---------|-----|-------|
| **Edward Tufte - Data Visualizer** | `0ee3d883` | Data visualization expert; external persona, can be edited normally |

---

## Legacy / Archived Personas

| Persona | File | Status |
|--------|------|--------|
| **Vibe Thinker v1.0** | `file 'Documents/System/personas/vibe_thinker_persona_v1.0_archived_2025-10-22.md'` | Archived; replaced by Vibe Strategist v2.0. |
| **Vibe Thinker (compat shell)** | `file 'Documents/System/personas/vibe_thinker_persona_v1.0_REPLACED_BY_STRATEGIST.md'` | Compatibility stub pointing to Vibe Strategist. |

---

## Usage Notes

- For **routing decisions**, prefer the system-level contract:
  - `file 'N5/prefs/system/persona_routing_contract.md'`
- For **daily usage patterns and auto-activation signals**, see:
  - `file 'Documents/System/personas/quick_reference.md'`
- For **designing or upgrading personas**, use:
  - `file 'Documents/System/personas/vibe_architect_persona.md'`
  - `file 'Documents/System/personas/persona_creation_template.md'`

---

## Meta

This index should be updated whenever:

- A new persona is added or an old one is retired.
- A persona is significantly upgraded or renamed.
- Routing rules or core responsibilities change.

*Index v2.0 | 2026-01-15*

---

## Routing Compliance Requirements

All internal N5OS personas MUST include:

1. **Routing & Handoff section** with:
   - Reference to routing contract: `N5/prefs/system/persona_routing_contract.md`
   - Explicit `set_active_persona("<persona_id>")` calls for handoffs
   - **When work is complete:** line with explicit return to Operator

2. **Standard routing block format:**
```markdown
## Routing & Handoff

**Routing contract:** `N5/prefs/system/persona_routing_contract.md`

**When to hand off:**
- [Condition] → [Persona]: `set_active_persona("<id>")`

**When work is complete:** Return to Operator: `set_active_persona("{{OPERATOR_ID}}")`
```

**Persona IDs (canonical):**
- Operator: `{{OPERATOR_ID}}`
- Strategist: `{{STRATEGIST_ID}}`
- Builder: `{{PERSONA_ID}}`
- Teacher: `{{PERSONA_ID}}`
- Writer: `{{PERSONA_ID}}`
- Debugger: `{{PERSONA_ID}}`
- Architect: `{{PERSONA_ID}}`
- Researcher: `{{PERSONA_ID}}`
- Level Upper: `{{PERSONA_ID}}`
- Coach: `{{PERSONA_ID}}`
- Librarian: `{{PERSONA_ID}}`


