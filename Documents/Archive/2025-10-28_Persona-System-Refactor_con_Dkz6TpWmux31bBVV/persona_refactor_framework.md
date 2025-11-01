# Persona Refactor Framework
## Operator Core + Specialist Modes Architecture

**Created:** 2025-10-28  
**Purpose:** Systematic framework for deconstructing standalone personas into Operator-activated specialist modes

---

## Analysis: Current State

### Common Structure Across All Personas
Every current persona contains:
1. **Core Identity** - Role definition, mindset
2. **Pre-Flight (MANDATORY)** - Context loading requirements
3. **Methodology** - Phase-based workflows
4. **Critical Anti-Patterns** - What NOT to do
5. **Quality Standards** - Success criteria
6. **When to Invoke** - Invocation conditions
7. **Self-Check** - Pre-delivery validation
8. **Meta** - Version, philosophy

### Redundancy Map (Information Repeated Across Personas)

**HIGH redundancy:**
- N5 file system topology (Builder, Debugger, Operator)
- Architectural principles loading (All personas)
- Pre-flight context loading (All personas)
- Anti-pattern recognition (All personas)
- Quality self-checks (All personas)
- Integration with N5 (Builder, Debugger, Operator)

**MEDIUM redundancy:**
- Think→Plan→Execute framework (Builder, Strategist)
- Principle compliance checking (Builder, Debugger)
- Session state management (Builder, Operator)
- V's preferences/values (Strategist, Writer, Teacher)

**LOW redundancy (essential reinforcement):**
- P28 Plan DNA (Builder, Debugger - different angles)
- P32 Simple/Easy (Builder, Strategist - different contexts)
- Skepticism requirement (Debugger only)
- Voice preservation (Writer only)

---

## Novel Principles for Core + Specialist Architecture

### **MP1: Single Responsibility Principle**
**Core contains:** Operational baseline that ALL specialists need  
**Specialists contain:** ONLY domain-specific expertise

**Corollary:** If information appears in 2+ specialists, elevate to Core.

---

### **MP2: Activation Interface Contract**
**Every specialist MUST define:**
1. **Activation signals** - Keywords/patterns that trigger this mode
2. **Required context** - What Operator must provide in handoff
3. **Success criteria** - How to know specialist work is complete
4. **Return payload** - What specialist gives back to Operator

**Corollary:** Specialists are functions; Operator is the orchestrator.

---

### **MP3: Zero Assumption Handoffs**
**Specialists CANNOT assume:**
- File system state
- Session context
- Previous conversation history
- V's current objectives

**Specialists CAN assume:**
- Operator has loaded Core operational knowledge
- Handoff template includes all required context
- Operator will monitor execution
- Operator will handle operational glitches

**Corollary:** Handoff = complete transfer of control; specialist is self-contained.

---

### **MP4: Stateless Specialists**
**Specialists don't maintain:**
- Squawk logs (Operator handles)
- Architectural lessons tracking (Operator handles)
- Session state (Operator handles)
- Cross-mode memory (Operator handles)

**Specialists DO maintain:**
- Domain-specific methodologies
- Internal phase tracking during activation
- Validation protocols
- Quality standards

**Corollary:** Specialists are pure functions; Operator is the state machine.

---

### **MP5: Escalation > Expansion**
**When specialist encounters:**
- Operational blocker → Return to Operator (don't solve operationally)
- Cross-domain requirement → Return to Operator (don't activate other specialists)
- Missing context → Return to Operator (don't guess)

**Corollary:** Specialists stay in lane; Operator handles coordination.

---

### **MP6: Reinforcement Budget**
**Essential information can appear in Core + 1 specialist IF:**
- Viewed from different angle (e.g., P28 Plan DNA: Builder uses it, Debugger validates it)
- Critical to specialist success (e.g., P5 Anti-Overwrite in Builder for safety)
- Reinforces under-followed principle (e.g., P32 Simple/Easy in Builder and Strategist)

**Budget:** Max 3 principles can be reinforced per specialist.

**Corollary:** Repetition is expensive; use strategically.

---

### **MP7: Mode Purity Test**
**A specialist passes purity test if:**
- Remove Core from context → specialist still functions (assumes handoff complete)
- Remove other specialists → specialist still functions (no cross-dependencies)
- Activate on day 1 with new user → specialist still functions (no hidden state)

**Corollary:** Specialists are plugins; Core is the platform.

---

## Builder Enhancement: Trap Doors & Design Values

**Applied:** Planning Prompt + Architectural Principles lens

### Trap Door Analysis

**TRAP DOOR 1: Specialist Interface Contract (MP2)**
- **Risk:** If we get the activation interface wrong, every specialist needs rewriting
- **Mitigation:** Prototype with Builder first, iterate interface before touching others
- **Irreversibility:** High (touches all 6 specialists)
- **Decision:** Start with flexible interface, lock down after 2-3 specialist tests

**TRAP DOOR 2: Core vs Specialist Boundary**
- **Risk:** Move too much to Core → bloat; too little → duplication
- **Mitigation:** Apply 3-specialist rule (if 3+ need it, elevate to Core)
- **Irreversibility:** Medium (can move content, but expensive)
- **Decision:** Conservative first pass, track duplications in squawk log

**TRAP DOOR 3: Reinforcement Budget (MP6)**
- **Risk:** Under-reinforce → critical info missed; over-reinforce → token waste
- **Mitigation:** Track which principles are frequently violated post-refactor
- **Irreversibility:** Low (easy to add/remove reinforcement)
- **Decision:** Start with 3-principle budget, adjust based on real usage

**TRAP DOOR 4: Stateless Specialists (MP4)**
- **Risk:** If specialists can't maintain ANY state, complex workflows break
- **Mitigation:** Allow internal phase tracking during activation, but no cross-activation memory
- **Irreversibility:** Medium (changes specialist methodology structure)
- **Decision:** Stateless between activations, stateful within activation

### Design Values Validation

**1. Simple Over Easy** ✅
- **Simple:** 1 Core + N pure specialists (low coupling, clear boundaries)
- **Easy:** Keep standalone personas (familiar, but duplicative)
- **Choice:** Simple—fewer interwoven concepts, better for AI generation

**2. Flow Over Pools** ✅
- **Flow:** Specialist activates → works → returns → Operator continues
- **Pool:** Keep all personas loaded simultaneously (context bloat)
- **Choice:** Flow—clear entry/exit, time-bounded activations

**3. Maintenance Over Organization** ✅
- **Maintenance:** Operator auto-detects mode needs, activates specialist
- **Organization:** V manually selects persona per conversation
- **Choice:** Maintenance—system tells V when it's working vs broken

**4. Code Is Free, Thinking Is Expensive** ⚠️
- **Application:** Spend 70% time on THIS framework (thinking), 10% on refactor execution
- **Validation:** Are we rushing to refactor or thinking through trap doors?
- **Status:** GOOD—created framework first, now enhancing before execution

**5. Nemawashi: Explore Alternatives** ⚠️ 
- **Alternative 1:** Core + Specialist Modes (current plan)
- **Alternative 2:** Keep standalone personas, add Operator as coordinator only
- **Alternative 3:** Fully dynamic LLM-generated personas per task (no files)
- **Evaluation needed:** Have we explicitly compared trade-offs?

### Think → Plan → Execute Checklist

**THINK Phase (Current)**
- [x] What are we building? → Core + Specialist mode system
- [x] What are trap doors? → Interface contract, Core boundary, state management
- [ ] What are alternatives? → **NEED TO EXPLICITLY EVALUATE ALT 2 & 3**
- [x] What are failure modes? → Token efficiency, activation reliability, V confusion
- [x] Simple or easy? → Simple (validated above)

**PLAN Phase (Current)**
- [x] Prose specification → This framework document
- [x] Success criteria → Token efficiency, mode purity, operational testing
- [x] Verification steps → MP7/MP2/MP4/MP5/MP6 tests
- [x] Information flows → V request → Operator → Specialist → Operator → V
- [ ] Confidence thresholds → **NEED TO DEFINE: When does Operator auto-activate vs ask V?**
- [x] Document assumptions → MP3 (Zero Assumption Handoffs)

**EXECUTE Phase (Blocked)**
- [ ] Generate code from plan → BLOCKED pending Nemawashi completion
- [ ] Move fast, don't break things → Will apply after alternatives evaluated
- [ ] Goal is velocity → Ready once THINK phase complete

**REVIEW Phase (Not Started)**
- [ ] Production test → Test with real build task
- [ ] Error paths → Test missing context, cross-domain needs
- [ ] Fresh thread → Can new Operator instance understand specialists?
- [ ] State verification → Validate specialists are truly stateless

### Nemawashi: Alternative Evaluation

**Alternative 1: Core + Specialist Modes (Current Plan)**
- **Pros:** Token efficient, clear boundaries, extensible, V doesn't manage
- **Cons:** Upfront refactor cost, activation reliability unknown, trap doors
- **Trap Doors:** Interface contract, Core boundary (HIGH cost to change)
- **Best for:** Long-term maintainability, adding new specialists

**Alternative 2: Coordinator-Only Operator**
- **Pros:** No persona refactor needed, familiar standalone structure, lower risk
- **Cons:** Token inefficiency continues, duplication remains, V still manages personas
- **Trap Doors:** None (reversible)
- **Best for:** Conservative approach, avoiding refactor risk

**Alternative 3: Dynamic LLM-Generated Personas**
- **Pros:** Ultimate flexibility, no file management, always optimal for task
- **Cons:** No consistency, expensive token usage, unpredictable behavior, no refinement loop
- **Trap Doors:** Irreversible if we delete all persona files (HIGH risk)
- **Best for:** Experimental, not production

**RECOMMENDATION: Alternative 1 (Core + Specialist)**
- **Why:** Aligns with "Simple Over Easy" + "Maintenance Over Organization"
- **Mitigation:** Prototype with Builder first, validate interface, iterate before full refactor
- **Checkpoint:** After Builder refactor, evaluate: Does activation work? Is token savings real?

### Confidence Thresholds for Auto-Activation

**HIGH confidence (Operator auto-activates):**
- Request contains 2+ strong specialist signals (e.g., "build", "implement", "create")
- Context is complete (objective, constraints, success criteria clear from request)
- No ambiguity in domain (clearly Builder vs Researcher vs Writer)

**MEDIUM confidence (Operator proposes activation):**
- Request contains 1 strong signal or 2+ weak signals
- Context is partial (needs 1-2 clarifying questions)
- Domain is 80%+ clear

**LOW confidence (Operator asks V):**
- Request ambiguous (could be multiple specialists)
- Context insufficient (>2 missing pieces)
- Cross-domain work detected (needs multiple specialists)

**FORMULA:** `confidence = (signal_strength × context_completeness × domain_clarity)`  
**Thresholds:** >0.8 auto-activate, 0.5-0.8 propose, <0.5 ask

---

## Deconstruction Protocol

### Phase 1: Identify Core vs Specialist Content

**For each section in current persona:**

```
CORE if:
- Operational knowledge (file paths, command patterns)
- Cross-specialist principle (applies to 3+ domains)
- State management (squawk log, session tracking)
- Troubleshooting protocols (general debugging)
- V's baseline preferences (workflow, communication style)

SPECIALIST if:
- Domain methodology (5-phase research, Think→Plan→Execute)
- Domain-specific principles (P28 more relevant to Builder/Debugger)
- Specialized validation (code testing, source credibility)
- Domain anti-patterns (specific to that work type)
- Output templates (research synthesis, build plans)

DELETE if:
- Already in Core (and not essential reinforcement)
- Redundant with another specialist (and not justifiable)
- Operational protocol now handled by Operator
- Meta-information about persona system itself
```

---

### Phase 2: Extract to Core

**Move to Operator Core:**
1. N5 file system topology
2. All P0-P40 principles (lightweight reference)
3. Session state management
4. Squawk log protocol
5. Architectural lessons integration
6. Troubleshooting protocol
7. V's baseline preferences

**Already in Operator Core:** ✅ Complete

---

### Phase 3: Define Activation Interfaces

**For each specialist, create:**

```markdown
## Activation Interface

**Signals:** [Keywords that trigger this mode]
- Primary: "build", "implement", "create", "script"
- Secondary: "setup", "deploy", "develop"
- Context: Request implies construction of new system/component

**Required Context (Operator provides):**
- Objective: What to build
- Constraints: Tech stack, dependencies, limitations
- Success criteria: Definition of done
- Relevant files: Existing code, configs, docs
- Principles emphasis: Which P-rules apply most

**Success Criteria (Specialist exits when):**
- System functional (happy path works)
- Tests passing (if applicable)
- Documented (inline + README if needed)
- Principles validated (self-check passed)

**Return Payload (Specialist gives Operator):**
- Created files: Absolute paths
- Status: Complete | Partial | Blocked
- Issues: Any problems encountered (for squawk log)
- Recommendations: Follow-up work needed
```

---

### Phase 4: Purify Specialist Content

**For each specialist:**

1. **Remove Pre-Flight** → Replaced by Activation Interface
2. **Remove "When to Invoke"** → Now Operator's job
3. **Remove operational protocols** → Operator handles
4. **Remove N5 integration** → Operator handles
5. **Keep methodology** → Core specialist expertise
6. **Keep domain anti-patterns** → Specialist-specific
7. **Keep quality standards** → Specialist-specific
8. **Keep validation protocols** → Specialist-specific

**Validate with Mode Purity Test (MP7)**

---

### Phase 5: Add Mode-Specific Sections

**Every refactored specialist gets:**

```markdown
## Mode Context

**Activated by:** Vibe Operator  
**Assumes:** Operator Core active, handoff complete, context provided  
**Scope:** [Domain] work only  
**Escalation:** Return to Operator for: [specific conditions]

## [Domain] Methodology

[Phase-based workflow - specialist's core expertise]

## [Domain] Anti-Patterns

[Specific to this work type]

## [Domain] Quality Standards

[Success criteria for this domain]

## Return to Operator

**Completion checklist:**
- [ ] [Domain-specific success criteria]
- [ ] Issues logged (if any)
- [ ] Recommendations documented
- [ ] Self-check passed

**Handoff payload:**
[Template showing what specialist returns]
```

---

## Refactor Order (Dependency-Sorted)

1. **Builder** - Most complex, most N5-specific
2. **Debugger** - References Builder work
3. **Researcher** - Independent domain
4. **Strategist** - References research/analysis patterns
5. **Writer** - References strategic context
6. **Teacher** - References all other domains

---

## Quality Validation (Post-Refactor)

**For each refactored specialist:**

### MP7 Mode Purity Test
- [ ] Remove Core → still functions?
- [ ] Remove other specialists → still functions?
- [ ] Day 1 activation → still functions?

### MP2 Interface Contract Test
- [ ] Activation signals defined?
- [ ] Required context specified?
- [ ] Success criteria clear?
- [ ] Return payload structured?

### MP4 Stateless Test
- [ ] No squawk log management?
- [ ] No cross-mode memory?
- [ ] No session state tracking?
- [ ] Only domain methodology?

### MP5 Escalation Test
- [ ] Operational blockers → return to Operator?
- [ ] Cross-domain needs → return to Operator?
- [ ] Missing context → return to Operator?

### MP6 Reinforcement Budget Test
- [ ] Max 3 principles reinforced?
- [ ] Each reinforcement justified?
- [ ] Different angle from Core?

---

## Success Criteria

**Refactor succeeds when:**

1. **Token efficiency:** 50%+ reduction in specialist size
2. **Clarity:** Single specialist = single expertise domain
3. **Modularity:** Specialists interchangeable/addable
4. **Operator orchestration:** V can ignore specialist details
5. **Mode purity:** All tests pass (MP7, MP2, MP4, MP5, MP6)
6. **Operational:** Test with real task shows proper activation/handoff

---

## Next Actions

1. Apply protocol to Builder first (most complex)
2. Test Builder as specialist mode with real build task
3. Iterate framework based on learnings
4. Apply to remaining specialists in order
5. Update INDEX.md with new architecture explanation

---

*Framework v1.0 | 2025-10-28 | Novel principles: MP1-MP7*
