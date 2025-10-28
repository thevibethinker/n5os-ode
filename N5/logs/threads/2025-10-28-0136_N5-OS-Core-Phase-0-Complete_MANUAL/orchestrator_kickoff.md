# N5OS Core - Phase 0 Orchestrator Kickoff

**Project**: N5 OS (Sesc v0.1)  
**Phase**: 0 - Foundation  
**Planning Thread**: con_HuaTrPlhVJRg9c9m  
**Status**: Ready to Execute

---

## Context for Orchestrator

You are building **Phase 0: Foundation** for N5 OS Core distribution.

**What this is**: Creating a minimal, deployable productivity system for Zo that can:
- Make AI think correctly (via rules)
- Maintain itself (via scheduled tasks)
- Handle updates safely (via config template system)

**Where you're building**: Demonstrator Zo account (TBD - V will specify)

**What you have access to**:
- Full specification: `file '/home/.z/workspaces/con_HuaTrPlhVJRg9c9m/n5os_core_spec.md'`
- Detailed Phase 0 plan: `file '/home/.z/workspaces/con_HuaTrPlhVJRg9c9m/phase0_detailed_plan.md'`
- Empty structure ref: `file '/home/.z/workspaces/con_HuaTrPlhVJRg9c9m/demonstrator_empty_structure.md'`

---

## Phase 0 Breakdown (4 Sub-Phases)

### Phase 0.1: Directory Structure + Init Script
**Deliverables**:
- `/N5/templates/` directory
- `/N5/config/` directory (initially empty)
- `/N5/scripts/n5_init.py` (config generator)
- `.gitignore` configured correctly
- Basic `/docs/` structure

**Test**: Running `n5_init.py` creates config files from templates

---

### Phase 0.2: Core Rules Template
**Deliverables**:
- `/N5/templates/rules.template.md` 
- Extracted from Main system, redacted for general use
- Include: Safety rules, troubleshooting protocol, pre-flight checks
- Exclude: V-specific personal preferences

**Test**: AI loads rules and applies them correctly

---

### Phase 0.3: Scheduled Tasks
**Deliverables**:
- Cleanup script (`/N5/scripts/cleanup.py`)
- Self-description generator (`/N5/scripts/self_describe.py`)
- Scheduled tasks registered in Zo
- Documentation for each schedule

**Test**: Scripts run without error, produce expected output

---

### Phase 0.4: Testing & Documentation
**Deliverables**:
- `/docs/phase0_setup.md` - User setup guide
- `/docs/phase0_architecture.md` - Component documentation
- Test report confirming all Phase 0 success criteria met
- README.md for repo root

**Test**: Fresh Zo → follow setup guide → working foundation in < 15 min

---

## Your Approach

### 1. One Sub-Phase Per Conversation
**Don't try to do everything at once.** Complete 0.1, confirm it works, move to 0.2.

### 2. Extract → Redact → Test
For each component:
1. **Extract** from Main system (V will provide access if needed)
2. **Redact** V-specific details (names, personal prefs, secret sauce)
3. **Test** on Demonstrator
4. **Document** what it does and how to use it

### 3. Non-Technical Documentation
Remember: Target user is **non-technical**. Documentation must:
- Assume no terminal comfort
- Explain every step
- Include examples
- Provide troubleshooting

### 4. Config Template Pattern
Every config file needs:
- `/N5/templates/X.template.md` (from GitHub)
- `/N5/config/X.md` (user-generated, git-ignored)
- Logic in `n5_init.py` to generate config from template

---

## Success Criteria (Phase 0 Complete)

- [ ] Fresh Zo loads rules template
- [ ] Cleanup schedule runs automatically  
- [ ] Self-description generator provides accurate system summary
- [ ] Config system generates user configs from templates without overwriting
- [ ] Zero manual file creation required (all automated via init script)
- [ ] Documentation lets non-technical user set up in < 15 min

---

## First Steps

### Before You Start
1. Confirm Demonstrator Zo account access
2. Load full specification
3. Load Phase 0 detailed plan
4. Ask 3+ clarifying questions if ANY doubt

### Start With Phase 0.1
Create directory structure and init script. This is the foundation for everything else.

**Don't proceed to 0.2 until 0.1 is tested and confirmed working.**

---

## Communication Protocol

### With V (Planning Thread)
- Report completion of each sub-phase
- Ask for clarification on redaction decisions
- Request access to Main system files if needed

### With Yourself (Orchestrator Thread)
- Document decisions in thread
- Keep notes on what works/doesn't work
- Track deviations from plan with reasoning

---

## Key Principles

From planning prompt:
- **Simple Over Easy**: Choose disentangled over convenient
- **Think→Plan→Execute**: 40% Think, 30% Plan, 10% Execute, 20% Review
- **Nemawashi**: Explore 2-3 alternatives before choosing
- **Trap Doors**: Document irreversible decisions explicitly

From architectural principles:
- **P15**: Complete Before Claiming
- **P18**: Verify State (always check your work)
- **P7**: Dry-Run First
- **P21**: Document Assumptions

---

## Handoff to Next Phase

### When Phase 0 is Complete
1. Create handoff document for Phase 1 orchestrator
2. List all assumptions made
3. Document any deviations from plan
4. Update specification if design changed
5. Report to planning thread

### What Phase 1 Needs
- Working Phase 0 foundation
- Documentation of file structure
- Lessons learned from Phase 0
- Updated success criteria

---

## Files You'll Create

```
/home/workspace/
├── N5/
│   ├── templates/
│   │   └── rules.template.md
│   ├── config/
│   │   └── .gitkeep
│   └── scripts/
│       ├── n5_init.py
│       ├── cleanup.py
│       └── self_describe.py
├── docs/
│   ├── phase0_setup.md
│   ├── phase0_architecture.md
│   └── README.md
└── .gitignore
```

---

## Ready?

Load the specification, load the detailed plan, and start with Phase 0.1.

**Remember**: One sub-phase at a time. Complete → Test → Document → Move on.

---

*Created: 2025-10-28 00:07 ET*
