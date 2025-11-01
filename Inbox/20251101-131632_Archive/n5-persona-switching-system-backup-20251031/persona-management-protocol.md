# Persona Management Protocol

**Purpose:** Standardized workflow for managing Core + Specialist mode architecture  
**Version:** 2.0  
**Updated:** 2025-10-28

---

## Overview

**Architecture:** Core + Specialist Modes (v2.0)

- **Vibe Operator** (Core) = Always-active baseline that coordinates specialists
- **Specialist Modes** = Domain experts activated by Operator on demand (Builder, Debugger, Researcher, Strategist, Writer, Teacher)
- **Activation:** Automatic via signal detection or explicit "Operator: activate [Mode]"

This protocol covers creating, updating, and maintaining specialist modes within this architecture.

---

## Specialist Mode Structure

Every specialist mode MUST include:

### Required Sections

1. **Header Block**
   - Type: Specialist Mode (Operator-activated)
   - Version number (semantic: major.minor)
   - Predecessor reference (if refactored from v1.x persona)

2. **Activation Interface** (MP2: Interface Contract)
   - Signals (auto-detection keywords)
   - Context required
   - Success criteria
   - Handoff template

3. **Core Methodology**
   - Phase-based workflow (numbered steps)
   - Decision frameworks
   - Output specifications

4. **Return Payload**
   - What Operator receives back
   - Format/structure
   - Exit conditions

5. **Critical Principle Reinforcement** (MP6: max 3)
   - Which principles reinforced and why
   - Different angle than Operator core

6. **Integration Points**
   - How this mode chains with others
   - Common workflows

### Optional Sections
- Advanced techniques
- Edge case handling
- Historical context

---

## Creating New Specialist Modes

### Before You Start (MP1: Single Responsibility)

**Answer these questions:**

1. **What gap does this fill?** What can't current modes do well?
2. **What's the  trigger?** What signals activate this mode?
3. **What does it return?** Clear payload to Operator?
4. **How does it integrate?** Chains with existing modes?

**Template:** Use `file 'Documents/System/personas/persona_creation_template.md'` (adapt for mode structure)

---

### Creation Process

**Phase 1: Define Activation Interface**

```markdown
## Activation Interface

### Signals (Auto-Detection)
**Primary:** [main keywords that trigger this mode]
**Secondary:** [context clues, phrases]
**Disambiguation:** [how to distinguish from similar signals]

### Context Required
- File: [what files Operator should load before handoff]
- State: [required system state]
- Constraints: [known limitations]

### Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]

### Handoff Template
[Operator uses this to activate mode]
```

**Phase 2: Define Core Methodology**

- Keep phase-based (Phase 1, Phase 2, etc.)
- Make each phase actionable
- Include decision points
- Specify outputs

**Phase 3: Define Return Payload**

- What does Operator get back?
- Structured data? Narrative? Both?
- Exit conditions (when is mode "done")?

**Phase 4: Identify Critical Principles** (MP6: max 3)

- Which principles are most violated in this domain?
- Reinforce from different angle than Operator

**Phase 5: Test Mode Purity** (MP7)

- Can specialist function with just Operator handoff?
- No hidden dependencies?
- Clear entry/exit?

---

### Naming Convention

**File:** `vibe_[name]_mode.md` (lowercase, underscores)  
**Examples:** `vibe_builder_mode.md`, `vibe_debugger_mode.md`

**Location:** `/home/workspace/Documents/System/personas/`

---

## Updating Existing Modes

### Minor Updates (bump minor version)

**When:**
- Clarify existing behavior
- Fix typos/formatting
- Add examples
- Update references

**Process:**
1. Edit mode file
2. Update version (e.g., 2.0 → 2.1)
3. Add note in version history
4. Test activation still works
5. Commit with message: `docs(personas): Update [Mode] v[X.Y]`

### Major Updates (bump major version)

**When:**
- Change activation signals
- Modify core methodology
- Add/remove phases
- Change return payload format

**Process:**
1. Document rationale in `/home/.z/workspaces/con_*/refactor_analysis.md`
2. Create updated mode file
3. Test extensively (activation, execution, return)
4. Update Operator if signals changed
5. Update INDEX.md
6. Commit with message: `feat(personas): Major update [Mode] v[X.0]`

---

## Quality Checklist

### Before Finalizing Any Mode

**MP Compliance:**
- [ ] MP1: Single clear responsibility?
- [ ] MP2: Activation interface complete?
- [ ] MP3: No hidden assumptions in handoff?
- [ ] MP4: Stateless (no persistent state)?
- [ ] MP5: Escalation path defined?
- [ ] MP6: ≤3 principles reinforced, justified?
- [ ] MP7: Mode purity test passes?

**Functional:**
- [ ] Signals are distinct from other modes?
- [ ] Handoff template is complete?
- [ ] Methodology is actionable?
- [ ] Return payload is structured?
- [ ] Integration points documented?

**Quality:**
- [ ] Follows N5 conventions?
- [ ] No jargon without definition?
- [ ] Examples where helpful?
- [ ] Self-check at end?

---

## Integration with Operator

### Operator References Modes

**Operator knows:**
- All signal keywords
- When to activate each mode
- How to construct handoffs
- What to expect back

**When updating mode:**
- If signals change → Update Operator
- If handoff template changes → Update Operator
- If return format changes → Update Operator

### Modes Reference Operator

**Modes can:**
- Ask Operator to load files
- Ask Operator to execute commands
- Ask Operator to activate other modes
- Ask Operator to escalate to V

**Modes should NOT:**
- Execute system operations directly
- Make assumptions about Operator state
- Skip handoff contract

---

## Maintenance Workflow

### Weekly Review (Automated via Squawk Log)

```bash
# Check for activation issues
grep 'specialist' N5/logs/squawk_log.jsonl | jq -r '.description'

# Pattern detection
python3 /home/workspace/N5/scripts/analyze_squawk_log.py --patterns --days 7
```

### Monthly Deep Review (Manual)

**Questions:**
1. Are all modes still necessary?
2. Are signals distinct enough (no conflicts)?
3. Are methodologies still optimal?
4. Have any principles been consistently violated?
5. Do modes integrate smoothly?

**Action Items:**
- Refine activation logic
- Update methodologies
- Add new modes for gaps
- Deprecate redundant modes

---

## Common Anti-Patterns

**❌ Overlapping signals:** Builder and Debugger both trigger on "test"  
→ ✅ Disambiguation: "test X works" → Debugger; "test coverage" → Builder

**❌ Hidden assumptions:** Mode expects file loaded without requesting  
→ ✅ Explicit in handoff: "Context: file 'X' loaded"

**❌ Over-reinforcement:** Repeating 10+ principles  
→ ✅ Max 3, strategically chosen

**❌ No escalation path:** Mode stuck, doesn't know when to give up  
→ ✅ Clear escalation criteria

**❌ Stateful modes:** Mode remembers across activations  
→ ✅ Pure functions: input → output

---

## Reference

- **INDEX:** `file 'Documents/System/personas/INDEX.md'`
- **Template:** `file 'Documents/System/personas/persona_creation_template.md'`
- **Quick Ref:** `file 'Documents/System/personas/quick_reference.md'`
- **Framework:** `file '/.z/workspaces/con_Dkz6TpWmux31bBVV/persona_refactor_framework.md'`

---

## Version History

### v2.0 — 2025-10-28
- **BREAKING:** Refactored to Core + Specialist architecture
- All standalone personas → specialist modes
- Added MP1-MP7 principles
- Updated creation/maintenance workflows
- Operator always active, specialists on-demand

### v1.2 — 2025-10-22
- Added Vibe Writer persona to active roster

### v1.1 — 2025-10-16
- Clarified persona vs. system spec distinction

### v1.0 — 2025-10-12
- Initial protocol

---

*Protocol effective immediately for all persona/mode work.*