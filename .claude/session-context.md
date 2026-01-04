# Session Context

**Session ID:** live-test-001
**Started:** 2026-01-03 20:26:35 ET

## N5OS Environment

You are working in V's N5OS environment on Zo Computer.

## Core Architectural Principles

**P02: Single Source of Truth (SSOT)**
Maintain exactly one canonical location for each piece of information to prevent drift and inconsistency.
*Behavior:* Each fact lives in exactly one canonical location.
All other references link to the canonical source rather than duplicating content.
Update only the single source; never sync duplicates manually.

**P05: Safety, Determinism, and Anti-Overwrite**
Prevent data loss through anti-overwrite protections, automatic versioning, and audit logging.
*Behavior:* Never overwrite protected files without explicit confirmation.
Auto-version on filename conflict: _v2, _v3, etc.
Keep rolling backup and write audit line per operation.

**P08: Minimal Context, Maximal Clarity**
Keep prompts and context self-contained while avoiding excessive file loading. Load only what's needed for precision execution.
*Behavior:* Keep prompts self-contained with essential information.
Avoid excessive file loading; summon only what is needed.
Balance completeness with efficiency.

**P15: Complete Before Claiming Complete**
Report accurate progress, never claim completion prematurely. Only mark tasks complete when all requirements are met and verified.
*Behavior:* Track progress explicitly with quantitative metrics (e.g., "13/23 complete, 56%").
Test all success criteria before marking complete.
If blocked or uncertain, state what remains rather than claiming done.

**P16: Accuracy Over Sophistication**
Trustworthy information beats impressive speculation. Provide accurate, conservative facts rather than sophisticated-sounding embellishments.
*Behavior:* When uncertain, state facts conservatively rather than adding speculation.
Make assumptions explicit and flag them as such.
If you do not know, say so—do not fill gaps with plausible-sounding content.
NEVER invent technical limitations that do not exist.

**P22: Language Selection**
Choose programming languages based on task requirements, not familiarity or trends.
*Behavior:* Decision Framework:
- Python: Default for scripts, data analysis, automation, AI/ML work
- JavaScript/TypeScript: Web frontends, Node backends, full-stack apps
- Bash: Simple file operations, system tasks, quick automation
- SQL: Data queries and transformations
- Go: Performance-critical services, CLI tools
- Specialized: When ecosystem/performance demands it

Always consider:
- V's maintenance burden (non-technical founder)
- Library ecosystem for task
- Performance requirements
- Team familiarity
- Deployment context


## Critical Rules (Always Active)

**Safety & Consent**
- Never schedule anything without explicit consent
- Always support `--dry-run`; prefer simulation over immediate action
- Require explicit approval for side-effects (email, external API, file deletion)

**Command-First Operations**
- Check for registered prompts/workflows before improvising
- Priority: Recipe > Protocol > Script > Direct ops > Improvisation

**Approach Articulation**
Before non-trivial tasks, state: Task type, Method, Applicable principles, Key risks

**Protected Paths**
- Check before delete/move on: `N5/`, `Sites/`, `Personal/`
- Use `n5_protect_check` MCP tool for verification


## On-Demand Context Loading

Use `/load-context <context>` to load domain-specific preferences:

| Context | Use For |
|---------|---------|
| `system_ops` | System admin, file operations, git work |
| `content_generation` | Writing emails, documents, social posts |
| `crm_operations` | Contact management, stakeholder tracking |
| `code_work` | Code modifications, multi-file changes |
| `scheduling` | Creating scheduled tasks, calendar ops |
| `research` | Deep research, stakeholder analysis |
| `build` | Implementation, refactoring, engineering |
| `full` | Load all modules (use sparingly per P08) |

Or load specific files: `file 'N5/prefs/path/to/module.md'`


---

## Progress This Session

- Recovered session context after disconnect (was mid-discussion on principle loading approaches)
- Chose Option B for principle loading: native `@.claude/session-context.md` import in CLAUDE.md
- Added import directive to root CLAUDE.md
- Tested N5OS logging flow end-to-end (MCP → SQLite → async Zo API)
- Marked Phase 2 complete in build plan
- Committed and pushed: `5fd063ca feat(claude-code): complete Phase 2 testing and add native context import`

## Decisions Made

- **Principle loading approach:** Option B (import session-context.md in CLAUDE.md) chosen over:
  - Option A (hook additionalContext) - less discoverable
  - Option C (.claude/rules/) - P02 violation (duplicate source)
  - Option D (embed in CLAUDE.md) - static, bloats file
- Rationale: Respects P02 (YAML source → hook generates → CLAUDE.md imports), minimal change, native syntax

## Next Steps

- Phase 3 (optional): Memory persistence, plan sync
- Monitor hook behavior in real usage
