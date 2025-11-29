# N5 Navigator
**Quick Reference for N5 System Structure**

**Version:** 2.0 | Created: 2025-11-02 | Limit: <7k chars

---

## Purpose

Quick reference for navigating N5. Load when you need WHERE things are, HOW to switch personas, or WHICH workflows to use.

---

## N5 Directory Structure

```
N5/
├── prefs/
│   ├── operations/      # planning_prompt, debug-logging, protocols
│   ├── strategic/       # thinking_prompt
│   ├── system/          # navigator (this), nuance-manifest, risk-scoring
│   ├── principles/      # P36, P37, decision_matrix
│   └── communication/
├── scripts/             # executable_manager.py, debug_logger.py, n5_protect.py, risk_scorer.py
├── data/                # executables.db
├── schemas/             # index.schema.json
├── builds/
└── logs/threads/

Knowledge/
├── architectural/       # planning_prompt.md (master), architectural_principles.md
├── technical/
└── domain/

Prompts/                 # recipes.jsonl
Personal/Meetings/       # Meeting records ONLY
Careerspan/
Inbox/                   # Temporary staging
Archive/
```

---

## Key Files

**Cognitive Prompts:**
- `N5/prefs/operations/planning_prompt.md` - HOW to build
- `N5/prefs/strategic/thinking_prompt.md` - HOW to think
- `N5/prefs/system/navigator_prompt.md` - WHERE things are

**Principles:**
- `N5/prefs/principles/P36_orchestration_pattern.yaml`
- `N5/prefs/principles/P37_refactor_pattern.yaml`
- `N5/prefs/principles/decision_matrix.md`

**Key Scripts:**
- `N5/scripts/executable_manager.py search "<query>"`
- `N5/scripts/debug_logger.py [append|recent|patterns]`
- `N5/scripts/n5_protect.py check <path>`
- `N5/scripts/risk_scorer.py <path>`

**Capability Registry:**
- `N5/capabilities/index.md` – authoritative index of integrations, internal systems, workflows, and agents. Start here when asked "what can you do?".

---

## Persona System

**Vibe Operator** (Base) - ID: 90a7486f-46f9-41c9-a98c-21931fa5c5f6  
Execution mechanics, routing, risk assessment

**Vibe Builder** - ID: 567cc602-060b-4251-91e7-40be591b9bc3  
Execute designs, build infrastructure (not design)

**Vibe Architect** - ID: 74e0a70d-398a-4337-bcab-3e5a3a9d805c  
Meta-design, persona/prompt creation

**Vibe Strategist** - ID: 39309f92-3f9e-448e-81e2-f23eef5c873c  
Pattern extraction, strategic frameworks

**Vibe Teacher** - ID: 88d70597-80f3-4b3e-90c1-da2c99da7f1f  
Technical explanation, learning facilitation

**Vibe Writer** - ID: 5cbe0dd8-9bfb-4cff-b2da-23112572a6b8  
Content in V-voice (direct, concise)

**Vibe Debugger** - ID: 17def82c-ca82-4c03-9c98-4994e79f785a  
Verification, testing, compliance

**Vibe Researcher** - ID: d0f04503-3ab4-447f-ba24-e02611993d90  
Research, synthesis, fact-finding

**Switching:**
`set_active_persona` with persona_id from above  
**Return to Operator:** ID 90a7486f-46f9-41c9-a98c-21931fa5c5f6  
**Auto-switchback:** Specialists return to Operator after completing work

---

## Workflow Patterns

### Building (Simple)
1. Load planning_prompt
2. Think→Plan→Execute (70/20/10)
3. Builder executes

### Building (Complex - P36)
**When:** Multi-domain, context limits, distinct cognitive modes

**Pattern:**
```
Coordinator (Operator/Strategist)
  ↓ spawns specialists with objectives
  ↓ handoffs via structured formats (YAML/CSV)
Specialists work independently
  ↓ produce artifacts
Coordinator integrates
```

### Strategic Analysis
1. Load thinking_prompt
2. Apply mental models
3. Nemawashi (2-3 alternatives)
4. Document decision

### Refactoring (P37)
**Decision Matrix:**
- 70%+ preservable → Refactor (wrapper)
- <50% preservable → Rewrite
- 50-70% → Try wrapper, switch if fighting

**Steps:** Read → Preserve working → One concern → Test → Commit

### Debugging
1. Load Debugger
2. Reconstruct system
3. Test systematically
4. Validate vs. plan
5. Check principles

---

## Common Operations

**Before destructive ops:**
```bash
python3 /home/workspace/N5/scripts/n5_protect.py check <path>
python3 /home/workspace/N5/scripts/risk_scorer.py <path>
```

**Find prompts:**
```bash
python3 /home/workspace/N5/scripts/executable_manager.py search "<keywords>"
```

**Debug logging:**
```bash
python3 /home/workspace/N5/scripts/debug_logger.py [append|recent|patterns]
```

---

## Integration Points

**Prompt load order (complex work):**
1. navigator (if unclear structure)
2. thinking (strategic decisions)
3. planning (execution framework)
4. Apply P36/P37

**When each applies:**
- **planning:** Building, refactoring, infrastructure
- **thinking:** Strategy, trade-offs, mental models
- **navigator:** Finding files, persona switching, workflows

---

## Quick Task Reference

| Task | Action |
|------|--------|
| Build script | planning_prompt → Builder → Think→Plan→Execute |
| Strategic decision | thinking_prompt → Strategist → Mental models |
| Find tool | executable_manager.py search |
| Multi-domain | P36 → Operator coordinates |
| Refactor | P37 matrix → Builder |
| Verify build | Debugger → Test + compliance |
| Learn X | Teacher → Explanation |
| Write content | Writer → V-voice |

---

## Routing Rules

**Operator handles:** File ops, workflow execution, routing, risk, state  
**Operator routes to:** Builder (build), Architect (design), Strategist (strategy), Teacher (learn), Writer (content), Debugger (verify), Researcher (info)

**Red flags:**
- Operator/Builder attempting design → Architect
- Any persona stuck → Operator

---

*v2.0 | 2025-11-02 | Expanded with personas, workflows, patterns - under 7k limit*

