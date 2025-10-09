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

- **`architectural_principles.md`**: Core principles (HARD protection)
  - Rule-of-Two (triangulate sources)
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

### Rule-of-Two
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
