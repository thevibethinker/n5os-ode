# /n5-principles

Display N5OS architectural principles for reference during work.

## Instructions

When the user invokes `/n5-principles` or asks about N5 principles:

Display the embedded principles below. These are the core architectural principles that guide all N5OS work.

---

## Core Architectural Principles

### P02: Single Source of Truth (SSOT)
**Purpose:** Maintain exactly one canonical location for each piece of information.

- Each fact lives in exactly one canonical location
- All other references link to the canonical source rather than duplicating
- Update only the single source; never sync duplicates manually

**Anti-pattern:** Same information appears verbatim in multiple files
**Fix:** Choose canonical location, replace other instances with links

---

### P05: Safety, Determinism, Anti-Overwrite
**Purpose:** Prevent data loss through protections, versioning, and audit logging.

- Never overwrite protected files without explicit confirmation
- Auto-version on filename conflict: `_v2`, `_v3`, etc.
- Keep rolling backup and write audit line per operation

**Anti-pattern:** Files being overwritten without warning or backup
**Fix:** Implement auto-versioning and explicit confirmation

---

### P08: Minimal Context, Maximal Clarity
**Purpose:** Keep prompts self-contained while avoiding excessive file loading.

- Include essential information inline
- Load only what's needed for precision execution
- Balance completeness with efficiency

**Anti-pattern:** Loading entire file trees for simple tasks
**Fix:** Identify minimal necessary context; load only relevant files

---

### P15: Complete Before Claiming Complete
**Purpose:** Report accurate progress, never claim completion prematurely.

- Track progress with quantitative metrics ("13/23 complete, 56%")
- Test all success criteria before marking complete
- If blocked, state what remains rather than claiming done

**Anti-pattern:** Claiming "done" while significant work remains
**Fix:** Use explicit progress metrics and remaining work lists

---

### P16: Accuracy Over Sophistication
**Purpose:** Trustworthy information beats impressive speculation.

- When uncertain, state facts conservatively
- Make assumptions explicit and flag them
- If you don't know, say so—don't fill gaps with plausible-sounding content
- NEVER invent technical limitations that don't exist

**Anti-pattern:** Adding strategic context that sounds smart but isn't grounded
**Fix:** State only what is explicitly documented or confirmed

---

### P22: Language Selection
**Purpose:** Choose programming languages based on task requirements, not familiarity.

Decision Framework:
- **Python**: Default for scripts, data analysis, automation, AI/ML
- **JavaScript/TypeScript**: Web frontends, Node backends
- **Bash**: Simple file operations, system tasks
- **SQL**: Data queries and transformations
- **Go**: Performance-critical services, CLI tools

Always consider V's maintenance burden (non-technical founder).

---

### P07: Idempotence and Dry-Run
**Purpose:** Every operation should be safely repeatable and previewable.

- Support `--dry-run` for all destructive operations
- Running same operation twice should produce same result
- Preview before execute

---

### P18: State Verification is Mandatory
**Purpose:** Never assume state; always verify before acting.

- Check current state before making changes
- Verify expected conditions are met
- Don't assume previous operations succeeded

---

### P21: Document All Assumptions
**Purpose:** Make implicit knowledge explicit.

- State assumptions clearly in code and documentation
- Flag when proceeding based on incomplete information
- Document "why" not just "what"

---

### P25: Code is Free
**Purpose:** Don't over-optimize developer time at expense of clarity.

- Write clear code even if slightly more verbose
- Premature optimization is the root of all evil
- Readable > clever

---

### P32: Simple Over Easy
**Purpose:** Prefer simple solutions that may require more initial effort over easy solutions that create complexity later.

- Simple = fewer moving parts, easier to understand
- Easy = quick to implement but may hide complexity
- Invest upfront in simplicity

---

## Quick Reference

| Principle | One-liner |
|-----------|-----------|
| P02 | One canonical source per fact |
| P05 | Never overwrite without backup |
| P08 | Load only what's needed |
| P15 | Verify complete before claiming |
| P16 | Accuracy beats sophistication |
| P22 | Right language for the task |
| P07 | Always support dry-run |
| P18 | Verify state before acting |
| P21 | Document your assumptions |
| P25 | Clarity over cleverness |
| P32 | Simple over easy |

---

## Loading More Principles

For the complete principle set (38 principles):
```bash
ls N5/prefs/principles/*.yaml
```

Or load specific principles:
```
file 'N5/prefs/principles/P<ID>_<name>.yaml'
```
