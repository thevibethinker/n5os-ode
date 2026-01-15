---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_KGkdxFqpqncEQyuu
---

# Worker A: System Improvements

**Project:** vrijenattawar-domain-transition
**Worker ID:** A-system-improvements
**Estimated Time:** 15 minutes
**Dependencies:** None

---

## Objective

Establish two system-level improvements:
1. A new rule preventing arbitrary folder creation
2. Convert the frontend-design skill to a proper prompt

---

## Task 1: Create Folder-Creation Rule

**Background:** V noticed that Zo (me) tends to create random folders without thinking through whether they belong. This leads to filesystem sprawl.

**Action:** Use `create_rule` tool to add a new rule:

- **Condition:** `When creating a new folder or directory`
- **Instruction:** Something like:
  > Never create a folder unless you have absolute confidence in where it should go. If there's any doubt about the canonical location, ask V first. Over time, established protocols and patterns should guide folder placement—when in doubt, check existing structure and conventions before creating.

---

## Task 2: Convert Frontend Skill to Prompt

**Background:** I mistakenly saved a "Claude Code skill" as a standalone file. In the Zo ecosystem, skills = prompts.

**Source File:** `/home/workspace/N5/skills/frontend-design/SKILL.md`

**Action:**
1. Read the source file
2. Convert it to proper `.prompt.md` format with frontmatter:
   - title: "Frontend Design"
   - description: A concise description
   - tags: [frontend, design, css, ui, web]
   - tool: true
3. Save to `/home/workspace/Prompts/Frontend Design.prompt.md`
4. Delete the source directory `/home/workspace/N5/skills/` (it was created in error)

---

## Deliverables

- [ ] New rule created via `create_rule`
- [ ] `/home/workspace/Prompts/Frontend Design.prompt.md` exists with proper frontmatter
- [ ] `/home/workspace/N5/skills/` directory deleted

---

## Completion

When done, report back with confirmation of all deliverables.

