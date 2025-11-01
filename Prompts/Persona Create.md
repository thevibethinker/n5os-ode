---
description: Create reusable persona instruction sets (like Vibe Builder) for specialized
  Zo behaviors.
tags:
- persona
- template
- documentation
---
# `persona-create`

**Summary:** Generate a new AI persona instruction set using standard template

**Workflow:** documentation

---

## Purpose

Create reusable persona instruction sets (like Vibe Builder) for specialized Zo behaviors.

---

## Process

1. **Start with template:**
   - Load `file 'Documents/System/persona_creation_template.md'`
   - Identify persona purpose and scope

2. **Gather source material:**
   - Relevant principles from `Knowledge/architectural/`
   - Relevant lessons from `N5/lessons/archive/`
   - Relevant workflows from `N5/commands/`
   - Key anti-patterns and standards

3. **Fill template sections:**
   - Core identity (who is this persona?)
   - Pre-flight requirements (what to load before starting)
   - Critical principles (which apply most)
   - Anti-patterns (what mistakes to avoid)
   - Quality standards (what defines good work)
   - Self-check (validation checklist)

4. **Optimize for size:**
   - Target: 4,000-6,000 characters
   - Maximum: 10,000 characters
   - Run character count validation
   - Tighten while preserving critical info

5. **Place and validate:**
   - Save to `Documents/System/[name]_persona.md`
   - Test with example invocation
   - Extract lesson to `N5/lessons/pending/`

6. **Commit:**
   - Git commit with both persona file and lesson
   - Separate from other changes

---

## Example Invocation

```
Create a "Meeting Prep" persona that specializes in:
- Pre-meeting research
- Stakeholder analysis
- Question preparation
- Context gathering

Use the persona template and keep under 6,000 characters.
```

---

## Outputs

- `Documents/System/[name]_persona.md` (persona file)
- `N5/lessons/pending/[date]_[thread].lessons.jsonl` (lesson)
- Git commit

---

## Related

- Template: `file 'Documents/System/persona_creation_template.md'`
- Example: `file 'Documents/System/vibe_builder_persona.md'`
- Workflow: `file 'N5/commands/persona-documentation-workflow.md'`

---

**Version:** 1.0  
**Created:** 2025-10-13
