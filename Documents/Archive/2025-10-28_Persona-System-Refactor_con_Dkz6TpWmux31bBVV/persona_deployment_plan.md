# Persona System Deployment Plan
**Date:** 2025-10-28  
**Objective:** Deploy Core + Specialist mode architecture system-wide

---

## Phase 1: System Settings

### 1.1 Update Default Persona
**Action:** Set Vibe Operator as default persona in Zo settings  
**Location:** https://va.zo.computer/settings

**Current:** No default (loads base system)  
**New:** Vibe Operator v1.2

**V must do manually:**
1. Go to Settings → Persona
2. Set default: `vibe_operator_persona.md`
3. Save

---

### 1.2 Add Conditional Rules

**Current rules:** Load N5.md, prefs.md, initialize SESSION_STATE  
**New rules:** Add persona activation enforcement

**Draft rules to add:**

```markdown
CONDITION: When V requests building, implementing, or creating systems/scripts → RULE:  
Automatically activate Builder mode unless already active. Load architectural/planning_prompt.md for complex builds. Never build directly as Operator—always hand off to specialist.

CONDITION: When V requests verification, debugging, or testing → RULE:  
Automatically activate Debugger mode. Load architectural principles index. Never claim "looks good" without systematic testing.

CONDITION: When V requests research, investigation, or analysis → RULE:  
Automatically activate Researcher mode with appropriate lens (academic/challenge/intel). Never provide surface-level synthesis—go deep.

CONDITION: When V requests strategy, decision-making, or framework development → RULE:  
Automatically activate Strategist mode. Always provide 2-3 distinct options with clear tradeoffs.

CONDITION: When V requests writing external communications (emails, posts, articles) → RULE:  
Automatically activate Writer mode. Load voice transformation system and relevant style guides. Never write in generic AI voice.

CONDITION: When V uses the word "persona" in reference to Zo behavior → RULE:  
Understand V means "specialist mode" in Core + Specialist architecture. Operator is always active, specialists are activated as needed.
```

**Question for V:** Do you want these as explicit rules or trust Operator's signal detection?

---

## Phase 2: Update References

### 2.1 Protocol Files

**Files to update:**

1. **`N5/prefs/operations/scheduled-task-protocol.md`** (line 501)
   - Current: "via Vibe Builder persona"
   - Update: "via Operator activating Builder mode"

2. **`N5/prefs/operations/distributed-builds/protocol.md`** (line 347)
   - Current: "Activate Vibe Builder persona"
   - Update: "Operator: activate Builder mode"

3. **`N5/prefs/operations/distributed-builds/decision-tree.md`** (line 206)
   - Current: "Activate Vibe Builder persona"
   - Update: "Operator: activate Builder mode"

4. **`N5/prefs/operations/persona-management-protocol.md`**
   - Update to explain Core + Specialist architecture
   - Add section on creating new specialist modes
   - Update examples to reference modes not standalone personas

---

### 2.2 Command Files

**Files that reference personas:**

1. **`N5/commands/persona-create.md`**
   - Rename to `specialist-mode-create.md`?
   - Or update to explain mode vs persona distinction
   - Add MP1-MP7 compliance checklist

---

### 2.3 Documentation

**Update or create:**

1. **`Documents/System/personas/README.md`**
   - Explain Core + Specialist architecture
   - How to activate modes
   - How to create new specialists
   - Migration from v1.x personas

2. **`Documents/System/personas/quick_reference.md`**
   - Signal keywords for each mode
   - Activation confidence thresholds
   - Mode combination patterns

---

## Phase 3: Integration Points

### 3.1 Content Creation Workflows

**Affected workflows:**
- LinkedIn post generation
- Email follow-ups
- Voice transformation system

**Current:** Load Writer persona manually or implicitly  
**New:** Operator auto-activates Writer mode on signals: "write", "draft", "email", "post"

**Test cases:**
- "Write a LinkedIn post about X" → Should activate Writer, load voice system
- "Draft email to Y" → Should activate Writer, load templates
- "Reply to Z's message" → Should activate Writer with appropriate warmth

---

### 3.2 Build Orchestrator

**Current system:** Distributed builds protocol references "Vibe Builder persona"  
**New system:** Operator activates Builder mode, Builder loads planning prompt

**Integration:**
- Builder mode already includes Think→Plan→Execute
- Builder mode already includes P28 (plan-first)
- Builder mode already loads planning prompt when specified in handoff

**Test cases:**
- "Build a SQLite task tracker" → Operator → Builder → Planning Prompt → Build
- "Refactor session_state_manager.py" → Operator → Builder (or Debugger for verification after)

---

### 3.3 Verification & Testing

**Current:** Manual "Load Vibe Debugger"  
**New:** Operator auto-activates on signals: "verify", "check", "test", "audit"

**Integration with build workflow:**
1. V: "Build X"
2. Operator → Builder
3. Builder completes
4. V: "Verify it works"
5. Operator → Debugger
6. Debugger runs 5-phase verification

---

## Phase 4: Testing Protocol

### 4.1 Activation Testing

**Test each specialist:**

```bash
# Builder
"Build a Python script that lists all markdown files"
→ Expected: Operator activates Builder, creates script, tests it

# Debugger
"Verify the N5 session_state_manager works correctly"
→ Expected: Operator activates Debugger, runs 5-phase verification

# Researcher
"Research best practices for SQLite in Python CLIs"
→ Expected: Operator activates Researcher, 5-phase workflow

# Strategist
"Help me decide between approach A and B for feature X"
→ Expected: Operator activates Strategist, provides framework + options

# Writer
"Draft an email to Jeff about our meeting"
→ Expected: Operator activates Writer, loads voice system
```

### 4.2 Mode Transition Testing

**Test handoffs:**

```bash
# Research → Strategist
"Research options for hosting, then help me pick one"
→ Expected: Researcher → Strategist with findings

# Builder → Debugger
"Build a task CLI then verify it works"
→ Expected: Builder → Debugger with system context

# Strategist → Builder
"Analyze these approaches, pick best, then implement"
→ Expected: Strategist → Builder with strategic direction
```

### 4.3 Edge Case Testing

**Ambiguous signals:**

```bash
# "check" could be Debugger or simple Operator task
"Check if PostgreSQL is installed"
→ Expected: Operator handles directly (simple verify)

"Check if this codebase follows our principles"
→ Expected: Operator → Debugger (systematic verification)
```

---

## Phase 5: Migration Support

### 5.1 Old Persona References

**Handle gracefully:**

- If V says "Load Vibe Builder persona" → Interpret as activating Builder mode
- If V references old file names → Map to new mode files
- Explain architecture change first time it comes up

### 5.2 Communication

**What to tell V:**

"I've deployed the new persona system. Here's what changed:

- **Always active:** Vibe Operator is now your default
- **Automatic activation:** When you ask to build/verify/research/strategize/write, I automatically activate the right specialist
- **No manual switching:** You don't need to load personas anymore—I detect what you need and activate it
- **Seamless:** You probably won't notice the difference, but responses should be more consistent and specialized

**How to use it:**
- Just ask for what you want—I'll activate the right mode
- If you want specific mode: 'Operator: activate [Mode]'
- To see what's active: 'What mode are you in?'"

---

## Phase 6: Continuous Improvement

### 6.1 Squawk Log Monitoring

**Check weekly:**
```bash
# Pattern analysis
grep '"type":"glitch"' N5/logs/squawk_log.jsonl | jq -r '.description' | sort | uniq -c | sort -rn

# Mode activation issues
grep 'specialist' N5/logs/squawk_log.jsonl | jq -r '.description'
```

### 6.2 Refinement

**Based on squawk log patterns:**
- Adjust activation confidence thresholds
- Add signal keywords
- Refine disambiguation logic
- Update specialist handoff templates

---

## Success Criteria

✅ **Operator constraint:** ≤10,000 chars  
✅ **All specialists refactored:** Builder, Debugger, Researcher, Strategist, Writer  
✅ **Signal detection working:** Auto-activation >80% accuracy  
✅ **Mode transitions smooth:** No jarring switches  
✅ **V satisfaction:** "I don't think about personas anymore"  

---

## Next Actions

1. **V:** Set default persona to vibe_operator_persona.md in settings
2. **V:** Decide on conditional rules (explicit or trust signal detection)
3. **Operator:** Update protocol files (scheduled-task, distributed-builds)
4. **Operator:** Update documentation (README, quick_reference)
5. **V + Operator:** Run test protocol together
6. **Operator:** Monitor squawk log for issues

---

*Deployment plan v1.0 | 2025-10-28 | Ready for execution*
