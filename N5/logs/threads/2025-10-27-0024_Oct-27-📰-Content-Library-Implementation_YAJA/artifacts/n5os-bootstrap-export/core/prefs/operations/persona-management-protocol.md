# Persona Management Protocol

**Purpose:** Standardized workflow for creating, updating, and maintaining Zo personas  
**Version:** 1.1  
**Updated:** 2025-10-22

---

## Overview

Personas are specialized Zo configurations that activate different operational modes. This protocol ensures consistency, version control, and quality across all personas.

---

## Persona Structure

Every persona MUST include:

### Required Sections

1. **Header Block**
   - Purpose (one-line description)
   - Version number (semantic: major.minor)
   - Last updated date

2. **Core Identity**
   - Role description
   - Key capabilities
   - Watch-fors/anti-patterns

3. **Operational Guidelines**
   - When to use this persona
   - Key workflows or methods
   - Decision criteria

4. **Quality Standards**
   - Success metrics
   - Validation requirements
   - Self-check items

5. **Meta Section**
   - Invocation pattern
   - Version history (in footer)

### Optional Sections

- Context files to reference
- Examples or case studies
- Integration with other personas
- Technical calibration (for specialized personas)

---

## File Conventions

**Location:** `/home/workspace/Documents/System/`

**Naming:** `{persona_name}_persona.md` (lowercase, underscores)
- Examples: `vibe_teacher_persona.md`, `vibe_builder_persona.md`

**Version Format:** `v{major}.{minor}` 
- Increment minor for updates (content refinements, clarifications)
- Increment major for structural changes or significant capability additions

---

## Creation Workflow

### Phase 1: Discovery

**Before creating a persona, answer:**

1. **What gap does this fill?** What can't current personas do well?
2. **What's the core identity?** Role in one sentence
3. **When would V invoke it?** Specific trigger scenarios
4. **What are the anti-patterns?** What should this persona NOT do?
5. **How do we measure success?** Quality indicators

**Template:** Use `file 'Documents/System/persona_creation_template.md'`

### Phase 2: Drafting

1. Start from template
2. Fill required sections completely
3. Add optional sections if needed
4. Include 2-3 concrete examples
5. Write self-check checklist

**Quality bar:**
- Clear invocation pattern
- No jargon without definition
- Specific, actionable guidance
- Measurable quality standards

### Phase 3: Testing

**Test in 3-5 conversations:**
- Does V need to clarify/correct often?
- Does output match expectations?
- Are anti-patterns avoided?
- Is it distinct from other personas?

**Document:**
- Thread IDs where tested
- What worked well
- What needs refinement

### Phase 4: Finalization

1. Incorporate test feedback
2. Set version to 1.0
3. Add to persona index
4. Commit to Git (see Git Protocol below)
5. Announce in conversation or via email

---

## Update Workflow

### Minor Updates (v1.0 → v1.1)

**Triggers:**
- Clarifying existing guidance
- Adding examples
- Fixing typos or formatting
- Refining existing sections

**Process:**
1. Make changes
2. Increment minor version
3. Update "Last Updated" date
4. Add changelog entry at bottom
5. Commit to Git with descriptive message

### Major Updates (v1.0 → v2.0)

**Triggers:**
- Adding new capabilities or sections
- Restructuring content
- Changing core identity or purpose
- Merging/splitting personas

**Process:**
1. Document rationale for major change
2. Test changes in 2-3 threads
3. Increment major version
4. Update all references in other docs
5. Commit to Git with detailed message
6. Consider announcing to V

---

## Git Protocol

### Initial Commit (New Persona)

```bash
git add Documents/System/{persona_name}_persona.md
git add Documents/System/PERSONAS_README.md  # if updated
git commit -m "feat(personas): Add {Persona Name} v1.0

Purpose: {one-line description}
Fills gap: {what problem it solves}
Tested in: {thread IDs or 'pending testing'}"
```

### Update Commits

**Minor updates:**
```bash
git add Documents/System/{persona_name}_persona.md
git commit -m "docs(personas): Update {Persona Name} v{X.Y}

Changes:
- {bullet list of changes}
"
```

**Major updates:**
```bash
git add Documents/System/{persona_name}_persona.md
git commit -m "feat(personas): Major update {Persona Name} v{X.0}

Breaking changes:
- {what changed significantly}

Rationale:
- {why this was needed}

Tested in: {thread IDs}"
```

### Deprecation

```bash
git mv Documents/System/{old}_persona.md Documents/System/Archive/{old}_persona.md
git commit -m "chore(personas): Deprecate {Old Persona}

Reason: {why deprecated}
Replacement: {new persona or 'none'}
Last used: {date}"
```

---

## Maintenance Schedule

### Quarterly Review (Every 3 months)

**For each persona:**
- [ ] Usage frequency - Is it being used?
- [ ] Effectiveness - Is it working as intended?
- [ ] Conflicts - Does it overlap with other personas?
- [ ] Gaps - Are there unaddressed scenarios?

**Actions:**
- Update if needed (minor version bump)
- Deprecate if unused
- Split if doing too much
- Merge if overlapping

### Annual Review (Yearly)

**System-level:**
- [ ] Do personas cover V's needs?
- [ ] Is the taxonomy clear?
- [ ] Are invocation patterns intuitive?
- [ ] Should any be retired or created?

**Document findings in:** `Documents/System/persona_review_YYYY.md`

---

## Current Active Personas

| Persona | Version | Purpose | Primary Use Cases |
|---------|---------|---------|-------------------|
| **Vibe Teacher** | 1.0 | Technical learning | Explaining concepts, debugging mental models |
| **Vibe Builder** | 1.1 | System building | Architecture, scripts, automation |
| **Vibe Strategist** | 2.0 | Strategic intelligence | Pattern analysis, ideation, decision frameworks |
| **Vibe Writer** | 1.0 | Content creation | LinkedIn, newsletters, email campaigns |

**Index:** `file 'Documents/System/PERSONAS_README.md'`

---

## Quality Checklist

Before finalizing any persona (new or updated):

- [ ] All required sections present and complete
- [ ] Clear invocation pattern stated
- [ ] Specific examples or case studies included
- [ ] Self-check list present
- [ ] Anti-patterns explicitly called out
- [ ] Version and date updated
- [ ] No references to deprecated principles (e.g., Rule-of-Two)
- [ ] Tested in at least 2 real conversations
- [ ] Committed to Git with proper message
- [ ] Index/README updated if needed

---

## Anti-Patterns

**❌ Vague guidance:** "Be helpful" → ✅ "Start with analogy from V's domain"  
**❌ No examples:** Abstract theory only → ✅ Include 2-3 concrete examples  
**❌ Overlapping personas:** Unclear when to use which → ✅ Distinct invocation triggers  
**❌ No version control:** Direct edits without tracking → ✅ Git commits with changelog  
**❌ Untested:** Deploy without validation → ✅ Test in 3-5 threads first  
**❌ Stale personas:** Never reviewed or updated → ✅ Quarterly maintenance  

---

## References

- **Template:** `file 'Documents/System/persona_creation_template.md'`
- **Index:** `file 'Documents/System/PERSONAS_README.md'`
- **Git Workflow:** `file 'Knowledge/architectural/operational_principles.md'` (P14: Change Tracking)
- **Examples:** All active personas in `Documents/System/`

---

## Version History

### v1.1 (2025-10-22)
- Updated Current Active Personas table to reflect Vibe Strategist v2.0 (merged from Vibe Thinker + Vibe Analyst)
- Added Vibe Writer persona to active roster

### v1.0 (2025-10-16)
- Initial protocol
- Defined creation, update, and maintenance workflows
- Established Git conventions
- Created quality checklist
- Documented three active personas

---

**Maintained by:** V + Zo (collaborative)  
**Next review:** 2025-11-16  
**Protocol status:** Active

*v1.0 | 2025-10-16*
