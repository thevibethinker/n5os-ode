---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# Skills as Executable Memory Pattern

## What It Is

- Package workflows as Skills with bundled context and scripts
- Reusable procedures that preserve decision-making knowledge
- Executable documentation that runs the same way every time

## When to Use

- Complex procedures need consistent execution
- Multiple people must follow same process
- Domain knowledge must be preserved and shared
- Workflows combine AI reasoning with tool execution

## Minimal Build Recipe

- Create `Skills/name/SKILL.md` with frontmatter
- Document procedure in markdown body
- Add scripts to `scripts/` folder with CLI interface
- Include examples and edge case handling
- Test skill runs independently of creator knowledge

## Example Prompts

- "Build skill that packages our client onboarding procedure"
- "Create skill that handles contract review workflow consistently"

## Common Failure Modes

- Instructions too vague for others to execute
- Missing dependencies or environment setup
- No error handling when tools fail
- Skill assumes knowledge not in documentation