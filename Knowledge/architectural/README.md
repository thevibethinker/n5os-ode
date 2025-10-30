# Knowledge: Architectural Layer

This directory contains **meta-knowledge** about how N5 OS operates.

---

## Purpose

Architectural knowledge defines the principles and standards governing the system:
- Core operating principles
- Voice and communication policy
- Information ingestion standards
- System design patterns

---

## Files

- `file 'planning_prompt.md'` — Design philosophy and thinking framework
- `file 'research_frameworks.md'` — Research methodologies & quality standards (used by Vibe Researcher)
- `file 'architectural_principles.md'` — Index of principles

- **`architectural_principles.md`**: Core principles (HARD protection)

  - Single Source of Truth (SSOT)
  - Composability principles
  - Safety-first design

- **`ingestion_standards.md`**: How to process information
  - Direct processing (LLM-based)
  - API-based processing
  - Manual entry standards
  - Validation requirements

- **`voice_policy.md`**: Communication standards
  - How Zo should communicate with V
  - Tone, style, verbosity guidelines
  - Persona consistency

---

## Characteristics

- **HARD Protection**: Manual edit only (critical system definitions)
- **Prescriptive**: Defines how system should behave
- **Stable**: Changes via deliberate design decisions only
- **Authoritative**: Source of truth for system behavior

---

## Usage

Referenced by:
- AI system prompts and persona
- Script validation logic
- Command design patterns
- Safety enforcement rules

**Not Directly Modified By Scripts**: These files define how scripts should behave.

---

## Key Principles

Triangulate information from multiple sources before accepting as fact.

### Single Source of Truth (SSOT)
Each fact lives in one canonical location, referenced everywhere else.

### Safety First
Tiered protection prevents accidental modification of critical files.

### Composability
Build complex operations from simple, reusable primitives.

---

## Related

- **Safety Layer**: `/home/workspace/N5/scripts/n5_safety.py`
- **Preferences**: `/home/workspace/N5/prefs/prefs.md`
- **List Governance**: `/home/workspace/Lists/POLICY.md`

---

*Part of Knowledge Layer - Meta-knowledge about N5 OS*

## Case Studies

Real-world applications of architectural principles:

- [N5 Realignment 2025-10-28](case-studies/n5-realignment-2025-10-28.md) - System restructuring using build orchestrator pattern (42→20 directories, parallel workers, zero breaking changes)

See: file 'Knowledge/architectural/case-studies/README.md'
