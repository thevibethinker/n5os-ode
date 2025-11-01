# Architecture Enforcement Mechanism

**Purpose:** Ensure architectural principles are always referenced during major system changes

**Created:** 2025-10-12  
**Status:** Active

---

## The Problem

Architectural principles exist but aren't consistently referenced during major system work, leading to:
- Repeated mistakes
- Principle violations
- Incomplete implementations
- Missing error handling

---

## The Solution: Multi-Layered Enforcement

### Layer 1: User Rules (System Prompt)

Added to V's user rules:

```markdown
CONDITION: When building, refactoring, or modifying significant system components
RULE: Load 'Knowledge/architectural/architectural_principles.md' FIRST before any design or implementation work
```

### Layer 2: Command System

Created standardized workflow:
- `file 'N5/commands/system-design-workflow.md'`
- Includes architectural principles as mandatory Phase 0
- Referenced in major system work

### Layer 3: Architectural Principles Self-Reference

Updated architectural principles document (v2.0):
- Added "For Major System Changes" checklist
- First item: "ALWAYS load this file first"
- Explicit about when to reference

### Layer 4: Documentation Links

Key system documents now reference architectural principles:
- `N5/prefs/prefs.md` - References principles
- Thread export documentation - Includes principles compliance
- Test cycle documents - References principles

### Layer 5: Command Registration

```bash
# Add to Prompts/ (self-executing)
{
  "name": "LOAD_ARCH_PRINCIPLES",
  "file": "Knowledge/architectural/architectural_principles.md",
  "description": "Load architectural principles before major system work",
  "trigger_keywords": ["build", "refactor", "create system", "modify infrastructure"],
  "mandatory_for": ["system design", "script development", "infrastructure changes"]
}
```

---

## Usage Patterns

### Pattern 1: Explicit User Request

When V says:
```
Build a new [system component]
```

Zo should respond:
```
Before we begin, I'll load the architectural principles to ensure 
we design this correctly.

[Loads file 'Knowledge/architectural/architectural_principles.md']

Now, let's design [system component] following our established principles.
What are the requirements?
```

### Pattern 2: V References Workflow

When V says:
```
Follow the system design workflow for [component]
```

Zo loads:
1. `file 'Knowledge/architectural/architectural_principles.md'`
2. `command 'N5/commands/system-design-workflow.md'`

### Pattern 3: Mid-Project Check

When partway through implementation, V can say:
```
Check this against architectural principles
```

Zo reloads principles and validates design.

---

## Detection Keywords

**Trigger automatic principle loading when V says:**

- "build a new script"
- "create a system"
- "refactor [component]"
- "modify infrastructure"
- "design a workflow"
- "create automation"
- "implement [major feature]"

**Do NOT trigger for:**
- Small bug fixes
- Documentation updates
- Content creation
- Research tasks

---

## Compliance Checklist

### Before Starting Major Work

- [ ] Architectural principles loaded
- [ ] System design workflow referenced
- [ ] Requirements clear
- [ ] Success criteria defined

### During Implementation

- [ ] Following relevant principles (5, 7, 11, 15-20)
- [ ] Error handling included
- [ ] Dry-run mode supported
- [ ] State verification planned

### Before Claiming Complete

- [ ] All stated objectives met
- [ ] Tested with production configuration
- [ ] Error paths tested
- [ ] Documentation complete
- [ ] State writes verified

---

## Enforcement by File Type

### Scripts (`.py`, `.sh`, `.js`)
**Must follow:**
- Principle 7 (dry-run mode)
- Principle 11 (error handling)
- Principle 19 (explicit error paths)

### Workflows (commands, automation)
**Must follow:**
- Principle 8 (minimal context)
- Principle 12 (test in fresh thread)
- Principle 17 (production config testing)

### Infrastructure (system components)
**Must follow:**
- Principle 5 (anti-overwrite)
- Principle 13 (naming and placement)
- Principle 18 (state verification)

### Large Documents (specs, exports)
**Must follow:**
- Principle 1 (human-readable first)
- Principle 2 (single source of truth)
- Principle 20 (modular design)

---

## Maintenance

### Review Cycle
- **Quarterly:** Review if enforcement is working
- **After incidents:** Update if principles were violated
- **Version updates:** Sync with architectural principles updates

### Metrics to Track
- How often principles are loaded during major work
- How often violations occur
- Whether lessons learned are being applied

---

## Example: Thread Export Refactoring

**What happened:**
1. V requested evaluation of thread export system
2. Zo loaded architectural principles
3. Identified violations (SSOT, modular design)
4. Refactored with principles in mind
5. Added lessons learned back to principles document

**This is the model.**

---

## Integration with N5.md

`Documents/N5.md` should include reference to this enforcement mechanism:

```markdown
## Architectural Principles

N5 system design follows architectural principles documented in 
'Knowledge/architectural/architectural_principles.md'.

Before any major system work (scripts, workflows, infrastructure), 
ALWAYS load the architectural principles first.

See: file 'N5/prefs/system/architecture-enforcement.md'
```

---

## Status

✅ **Active as of 2025-10-12**

- Architectural principles updated to v2.0
- System design workflow created
- Enforcement mechanism documented
- User rules update recommended

**Next steps:**
1. V to review and approve
2. Add conditional rule to user rules (if desired)
3. Test enforcement in next major system work
4. Iterate based on effectiveness

---

**File:** `N5/prefs/system/architecture-enforcement.md`  
**Version:** 1.0  
**Maintenance:** Quarterly review + incident-driven updates
