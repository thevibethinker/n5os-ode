---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
type: build_plan
status: ready
orchestration: multi-worker
---

# Plan: N5OS Ode Feature Upgrade

**Objective:** Upgrade the public N5OS Ode repo with 5 missing capabilities that represent the core "operating system" sophistication.

**Trigger:** Semantic gap analysis revealed the repo has functional tools but lacks the choreography, principles, and workflows that make N5 actually work as an OS.

**Key Design Principle:** Each phase = 1 worker conversation. Workers execute independently, then orchestrator integrates.

---

## Open Questions

- [x] Should principles be YAML or Markdown in the public repo? → **YAML** (maintains structure, parseable, your local format)
- [x] Include all 37 principles or curate to ~15 essential? → **Curate to ~15-20 most universally applicable** (some are V-specific)
- [x] Where does routing contract live? → `docs/ROUTING.md` (user-facing) + `N5/prefs/system/persona_routing_contract.md` (internal)

---

## Checklist

### Worker 1: Conversation End System
- ☐ Replace stub router with full 424-line version
- ☐ Upgrade Close Conversation prompt to v5.1
- ☐ Add conversation_end_tiers.md documentation
- ☐ Test: Router returns correct JSON for mock inputs

### Worker 2: Persona Routing Contract
- ☐ Create docs/ROUTING.md (user-facing)
- ☐ Create N5/prefs/system/persona_routing_contract.md
- ☐ Update docs/PERSONAS.md to reference routing
- ☐ Test: Routing examples cover all personas

### Worker 3: Principles Library
- ☐ Create N5/prefs/principles/ directory
- ☐ Port 15-20 curated principles as YAML
- ☐ Create principles_index.yaml
- ☐ Add docs/PRINCIPLES.md overview
- ☐ Test: YAML files parse correctly

### Worker 4: Specialist Workflows
- ☐ Create N5/prefs/workflows/ directory
- ☐ Port researcher_workflow.md
- ☐ Port strategist_workflow.md
- ☐ Port debugger_workflow.md
- ☐ Port writer_workflow.md
- ☐ Test: Workflows reference correct personas

### Worker 5: Context Loading Upgrade
- ☐ Upgrade n5_load_context.py with category system
- ☐ Create context_manifest.yaml
- ☐ Document categories in README or docs
- ☐ Test: `python3 n5_load_context.py build` returns expected files

---

## Worker 1: Conversation End System

**Scope:** The heart of N5's session hygiene. Replace stub with full implementation.

### Affected Files
- `N5/scripts/conversation_end_router.py` - REPLACE - Full 424-line tier detection
- `Prompts/Close Conversation.prompt.md` - REPLACE - v5.1 with Worker/Full mode detection
- `docs/CONVERSATION_END.md` - CREATE - Document the tiered system

### Source Files (copy from local)
- `/home/workspace/N5/scripts/conversation_end_router.py`
- `/home/workspace/Prompts/Close Conversation.prompt.md`

### Changes

**1.1 Replace Router:**
Copy `/home/workspace/N5/scripts/conversation_end_router.py` to repo. This version:
- Parses SESSION_STATE.md for type, focus, artifacts
- Counts artifacts in conversation workspace
- Detects build markers and debug markers
- Returns structured JSON with tier + reasoning

**1.2 Replace Close Prompt:**
Copy `/home/workspace/Prompts/Close Conversation.prompt.md` to repo. Key features:
- Worker vs Full mode detection (build_id/worker_num in frontmatter)
- Scripts handle mechanics, LLM handles semantics
- 3-slot emoji title generation (State | Type | Content)
- Tiered close based on router output

**1.3 Add Documentation:**
Create `docs/CONVERSATION_END.md` explaining:
- Why conversation hygiene matters
- The 3 tiers and when each applies
- How Worker Close differs from Full Close
- Integration with SESSION_STATE

### Unit Tests
- `python3 N5/scripts/conversation_end_router.py --convo-id test_123 --help` → Shows usage
- Router with mock SESSION_STATE returns valid JSON

---

## Worker 2: Persona Routing Contract

**Scope:** The "operating system kernel" — how personas choreograph.

### Affected Files
- `docs/ROUTING.md` - CREATE - User-facing routing guide
- `N5/prefs/system/persona_routing_contract.md` - CREATE - Full contract
- `docs/PERSONAS.md` - UPDATE - Add reference to routing

### Source Files
- `/home/workspace/N5/prefs/system/persona_routing_contract.md`

### Changes

**2.1 Create Internal Contract:**
Copy full routing contract. Sanitize any V-specific persona IDs — use placeholder format `{PERSONA_ID:operator}` with note that users set their own.

**2.2 Create User-Facing Guide:**
Create `docs/ROUTING.md` with:
- "Home Base" concept (Operator as default)
- When to route to specialists (semantic mapping table)
- Return-to-Operator rule
- Examples of good vs. bad routing decisions

**2.3 Update PERSONAS.md:**
Add section: "How Personas Work Together" pointing to ROUTING.md

### Unit Tests
- ROUTING.md has all 6 core personas mentioned
- Contract references Operator as home base

---

## Worker 3: Principles Library

**Scope:** The accumulated architectural wisdom in parseable format.

### Affected Files
- `N5/prefs/principles/` - CREATE directory
- `N5/prefs/principles/principles_index.yaml` - CREATE
- `N5/prefs/principles/P01_*.yaml` through `P20_*.yaml` - CREATE (~15-20 files)
- `docs/PRINCIPLES.md` - CREATE - Overview and how to use

### Principles to Include (Curated)
From analysis, these are universally applicable:

| ID | Name | Why Include |
|----|------|-------------|
| P01 | Human-Readable First | Universal |
| P02 | Single Source of Truth | Universal |
| P05 | Safety/Determinism | Universal |
| P07 | Idempotence/Dry-Run | Universal |
| P08 | Minimal Context | AI-specific |
| P11 | Failure Modes | Universal |
| P13 | Naming/Placement | Universal |
| P15 | Complete Before Claiming | **Critical** |
| P16 | Accuracy Over Sophistication | Universal |
| P18 | State Verification | Universal |
| P19 | Error Handling | Universal |
| P20 | Modular Design | Universal |
| P21 | Document Assumptions | Universal |
| P23 | Identify Trap Doors | Architect-specific |
| P27 | Nemawashi Mode | Architect-specific |
| P28 | Plans as Code DNA | **Critical** |
| P32 | Simple Over Easy | Hickey principle |
| P36 | Orchestration Pattern | Multi-worker |

### Changes

**3.1 Create Directory Structure:**
```
N5/prefs/principles/
├── principles_index.yaml
├── P01_human_readable_first.yaml
├── P02_single_source_truth.yaml
...
```

**3.2 Port Principles:**
Copy from `/home/workspace/N5/prefs/principles/`. For each:
- Keep YAML structure (id, name, category, purpose, when_to_apply, pattern, examples, anti_patterns, related)
- Remove V-specific examples if any
- Ensure examples are generic/universal

**3.3 Create Index:**
`principles_index.yaml` listing all principles with one-line descriptions.

**3.4 Create Overview Doc:**
`docs/PRINCIPLES.md` explaining:
- What principles are and why they matter
- How to read YAML principle files
- How to add custom principles
- Links to individual principle files

### Unit Tests
- All YAML files parse without error: `python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"`
- Index lists same count as directory contents

---

## Worker 4: Specialist Workflows

**Scope:** How each persona actually operates (not just "what they're good at").

### Affected Files
- `N5/prefs/workflows/` - CREATE directory
- `N5/prefs/workflows/researcher_workflow.md` - CREATE
- `N5/prefs/workflows/strategist_workflow.md` - CREATE
- `N5/prefs/workflows/debugger_workflow.md` - CREATE
- `N5/prefs/workflows/writer_workflow.md` - CREATE
- `docs/PERSONAS.md` - UPDATE - Reference workflows

### Source Files
- `/home/workspace/N5/prefs/workflows/*.md`

### Changes

**4.1 Port Workflows:**
Copy each workflow file. Review for V-specific content and generalize.

**4.2 Update PERSONAS.md:**
For each persona section, add: "See [workflow](../N5/prefs/workflows/X_workflow.md) for detailed operation."

### Unit Tests
- Each workflow mentions its corresponding persona
- Links in PERSONAS.md resolve correctly

---

## Worker 5: Context Loading Upgrade

**Scope:** Dynamic context injection by task category.

### Affected Files
- `N5/scripts/n5_load_context.py` - REPLACE - Full category system
- `N5/prefs/context_manifest.yaml` - CREATE - Category definitions
- `docs/CONTEXT_LOADING.md` - CREATE - User documentation

### Source Files
- `/home/workspace/N5/scripts/n5_load_context.py`
- `/home/workspace/N5/prefs/context_manifest.yaml`

### Changes

**5.1 Replace Context Loader:**
Copy full version with categories: build, strategy, system, safety, scheduler, writer, research.

**5.2 Create Manifest:**
Copy `context_manifest.yaml` defining what files each category loads.

**5.3 Create Documentation:**
Explain categories, usage, how to customize.

### Unit Tests
- `python3 n5_load_context.py build --help` works
- `python3 n5_load_context.py build --dry-run` lists expected files

---

## Success Criteria

1. **Conversation End:** Router returns valid tier JSON; Close prompt has Worker/Full detection
2. **Routing:** Contract exists; ROUTING.md covers all 6 personas with examples
3. **Principles:** 15-20 YAML files parse correctly; index matches directory
4. **Workflows:** 4 workflow files exist; PERSONAS.md references them
5. **Context Loading:** Category system works; manifest defines all categories
6. **Integration:** README.md updated with new capabilities; all docs linked from main nav

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| V-specific content leaks into public repo | Each worker reviews for personal info before commit |
| Persona IDs hardcoded (won't work for other users) | Use placeholder format or document "set your own IDs" |
| Workers create conflicts in same files | Workers have distinct file scopes; orchestrator integrates |
| Principles too abstract without examples | Keep concrete examples in YAML; use generic scenarios |

---

## Orchestration Plan

```
Orchestrator (this conversation)
├── Worker 1: Conversation End System  [independent]
├── Worker 2: Persona Routing Contract [independent]
├── Worker 3: Principles Library       [independent]
├── Worker 4: Specialist Workflows     [independent]
└── Worker 5: Context Loading Upgrade  [independent]
    │
    └── Integration Phase (orchestrator)
        ├── Update README.md with new features
        ├── Verify cross-references
        ├── Final commit and push
```

Workers can run in **any order** — no dependencies between them.

After all workers complete, orchestrator:
1. Pulls all changes
2. Updates README.md feature list
3. Verifies cross-doc links
4. Final push to GitHub

---

## Level Upper Review

*Skipping for this build — scope is clear, alternatives already considered in gap analysis.*

---

## Ready for Execution

**Plan Status:** READY

**Next Step:** Use build orchestrator to spawn Worker 1.

```bash
python3 N5/scripts/build_orchestrator_v2.py spawn \
  --build-id n5os-ode-upgrade \
  --worker-num 1 \
  --title "Conversation End System" \
  --instruction "Execute Worker 1 from PLAN.md: Replace conversation_end_router.py, upgrade Close Conversation prompt, add documentation. Commit changes to local repo clone at /home/.z/workspaces/con_TU8sAIUts3Mzvqq6/n5os-ode/"
```
