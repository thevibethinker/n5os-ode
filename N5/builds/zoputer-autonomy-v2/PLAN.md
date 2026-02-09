---
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
type: build_plan
status: draft
provenance: con_SWTbq4MHoLlrrcsM
---

# Plan: Zoputer Autonomy v2

**Objective:** Establish bidirectional Zo-to-Zo communication with GitHub as shared substrate, human escalation paths, and medium autonomy for zoputer.

**Trigger:** V completed manual setup (account + API keys) and wants seamless operation without constant intervention.

**Builds On:** `consulting-zoffice-stack` (completed 2026-02-06)

---

## Open Questions

- [x] Does zoputer.zo.computer exist? → YES (V confirmed)
- [x] Is ZOPUTER_API_KEY set on va? → YES (ping works)
- [ ] **TRAP DOOR:** What GitHub repo name for shared substrate? Recommend: `zoputer-substrate` (private)
- [ ] Where should pending decisions be stored for cross-thread access? Options:
  - A) `N5/data/pending_decisions/` with JSON files
  - B) SQLite table in existing DB
  - C) Dedicated `decisions.db`
  - **Recommendation:** Option A (simple files, easy to read from any thread)
- [ ] What's the escalation confidence threshold? (Currently 0.7 per localization-protocol.md — keep or change?)

---

## Nemawashi: Alternatives Considered

### GitHub Sync Approach

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| A) Push on change (inotify/fswatch) | Real-time | Complex, fragile in container | ❌ |
| B) Scheduled push (every N minutes) | Simple, robust | Slight delay | ✅ Recommended |
| C) Manual trigger only | Most control | Defeats automation goal | ❌ |

**Decision:** Scheduled sync (every 15 min) + manual trigger option.

### Context Bridging for Escalation

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| A) JSON files in N5/data/pending_decisions/ | Simple, portable, readable | Need cleanup logic | ✅ Recommended |
| B) conversations.db extension | Centralized | Schema changes, coupling | ❌ |
| C) External service (Airtable/Notion) | Accessible anywhere | External dependency | ❌ |

**Decision:** JSON files with unique IDs, referenced in SMS.

---

## Trap Doors Identified

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| GitHub repo name | MEDIUM (can rename but breaks links) | Choose carefully upfront |
| Branch protection rules | LOW (easily changed) | Start permissive |
| VA_API_KEY on zoputer | LOW (can rotate) | Document rotation process |
| Autonomy threshold (0.7) | LOW (config change) | Make it configurable |

---

## Checklist

### Phase 1: GitHub Infrastructure
- ☐ Create `vrijenattawar/zoputer-substrate` repo (private)
- ☐ Set up branch protection on `main`
- ☐ Create initial folder structure (Skills/, Prompts/, Documents/)
- ☐ Build `Skills/git-sync/` with push/pull scripts
- ☐ Create scheduled agent for 15-min sync (va-side)
- ☐ Test: va pushes skill → appears in repo

### Phase 2: Bidirectional Communication
- ☐ Document VA_API_KEY setup for zoputer (manual step for V)
- ☐ Create `Skills/mentor-escalation/` for zoputer → va calls
- ☐ Build escalation prompt template
- ☐ Build va-side escalation handler
- ☐ Test: zoputer calls va with test question → gets response

### Phase 3: Human Escalation System
- ☐ Create `N5/data/pending_decisions/` structure
- ☐ Build `Skills/decision-bridge/` for packaging context
- ☐ Build SMS formatter with decision reference ID
- ☐ Build resolution handler (reads any-thread response, routes to origin)
- ☐ Test: va packages decision → texts V → V responds in different thread → decision resolved

### Phase 4: Zoputer Autonomy Rules
- ☐ Create `Documents/consulting/autonomy-config.yaml` 
- ☐ Build `Skills/learning-logger/` for zoputer self-edits
- ☐ Create GitHub Actions workflow for auto-PR on learning branch push
- ☐ Build va-side PR review prompt
- ☐ Test: zoputer commits learning → PR created → va reviews

---

## Phase 1: GitHub Infrastructure

### Affected Files
- `vrijenattawar/zoputer-substrate` repo - CREATE - new GitHub repo
- `Skills/git-sync/SKILL.md` - CREATE - skill definition
- `Skills/git-sync/scripts/sync_to_github.py` - CREATE - push logic
- `Skills/git-sync/scripts/sync_from_github.py` - CREATE - pull logic
- `N5/config/git_sync_config.yaml` - CREATE - sync configuration
- Scheduled agent `GIT_SYNC_ZOPUTER` - CREATE - 15-min interval

### Changes

**1.1 Create GitHub Repository:**
```bash
gh repo create vrijenattawar/zoputer-substrate --private --description "Shared substrate for zoputer.zo.computer"
```

Initialize with:
```
zoputer-substrate/
├── README.md
├── Skills/           # Receives exports from va
├── Prompts/          # Receives exports from va
├── Documents/
│   └── System/       # Receives exports from va
├── Learnings/        # zoputer writes here (own branch)
└── .github/
    └── workflows/
        └── learning-pr.yaml  # Auto-PR on learning push
```

**1.2 Branch Protection:**
- `main`: Require PR, no direct push (except va's sync bot)
- `zoputer/learnings`: zoputer can push directly

**1.3 Git Sync Skill:**
- `sync_to_github.py`: Commits and pushes changed skills from va
- `sync_from_github.py`: Pulls latest from main (for zoputer)
- Config specifies what paths to sync, ignore patterns

**1.4 Scheduled Agent:**
- Runs every 15 minutes
- Checks for changes since last sync
- Pushes if changes exist
- Logs to audit system

### Unit Tests
- `gh repo view vrijenattawar/zoputer-substrate` returns repo info
- After push: file appears in GitHub within 1 minute
- Sync script is idempotent (running twice doesn't duplicate commits)

---

## Phase 2: Bidirectional Communication

### Affected Files
- `Documents/consulting/va-api-setup-for-zoputer.md` - CREATE - manual setup guide
- `Skills/mentor-escalation/SKILL.md` - CREATE - skill for zoputer
- `Skills/mentor-escalation/scripts/ask_mentor.py` - CREATE - va call logic
- `Skills/mentor-escalation/assets/escalation_prompt.md` - CREATE - prompt template
- `N5/scripts/zoputer_client.py` - UPDATE - add handler for inbound escalations

### Changes

**2.1 VA_API_KEY Setup Guide:**
Document for V to execute manually on zoputer:
- Go to va.zo.computer Settings > Developers
- Create API key named `VA_CONSULTING_API`
- On zoputer: add secret `VA_API_KEY` with the key

**2.2 Mentor Escalation Skill (for zoputer):**
```python
# ask_mentor.py - runs on zoputer
def ask_mentor(question: str, context: dict) -> str:
    """Call va for guidance when uncertain."""
    prompt = f"""
    [ESCALATION FROM ZOPUTER]
    
    Question: {question}
    
    Context:
    - Confidence: {context.get('confidence', 'unknown')}
    - Client: {context.get('client', 'unknown')}
    - What I've tried: {context.get('attempted', 'nothing yet')}
    
    Please advise. If this needs V's input, package it for human escalation.
    """
    
    response = call_va(prompt)
    return response
```

**2.3 Va-Side Handler:**
Add rule/behavior: when receiving `[ESCALATION FROM ZOPUTER]` prefix, enter mentor mode:
- Assess if va can answer directly
- If not, trigger human escalation (Phase 3)
- Log all escalations to audit system

### Unit Tests
- `python3 ask_mentor.py --test` returns va's response
- Audit log shows both outbound and response entries
- Failed call triggers retry with backoff

---

## Phase 3: Human Escalation System

### Affected Files
- `N5/data/pending_decisions/` - CREATE - directory for decision context
- `Skills/decision-bridge/SKILL.md` - CREATE - skill definition
- `Skills/decision-bridge/scripts/package_decision.py` - CREATE - context packager
- `Skills/decision-bridge/scripts/resolve_decision.py` - CREATE - resolution handler
- `Skills/decision-bridge/assets/sms_template.md` - CREATE - SMS format

### Changes

**3.1 Pending Decisions Structure:**
```
N5/data/pending_decisions/
├── active/
│   └── dec_abc123.json   # Active decisions awaiting V
├── resolved/
│   └── dec_xyz789.json   # Resolved decisions (30-day retention)
└── index.json            # Quick lookup
```

**Decision JSON schema:**
```json
{
  "id": "dec_abc123",
  "created_at": "2026-02-07T12:00:00Z",
  "origin": "va" | "zoputer",
  "origin_conversation": "con_xxx",
  "summary": "Brief description for SMS",
  "full_context": {
    "question": "...",
    "options": ["A", "B"],
    "recommendation": "A",
    "reasoning": "...",
    "relevant_files": ["path/to/file.md"]
  },
  "status": "pending" | "resolved",
  "resolved_at": null,
  "resolution": null,
  "resolved_in_conversation": null
}
```

**3.2 Package Decision Script:**
- Creates decision JSON with unique ID
- Saves to `active/`
- Returns ID for SMS reference

**3.3 SMS Template:**
```
🔔 Decision needed: {summary}

Ref: {id}
From: {origin}

Reply here or any thread with "n5 decide {id} [your choice]"
```

**3.4 Resolution Handler:**
- New rule: When V sends "n5 decide {id} {choice}", load decision context
- Route resolution back to origin (va or zoputer)
- Move JSON to `resolved/`
- If origin was zoputer, call zoputer with resolution via /zo/ask

### Unit Tests
- Package creates valid JSON with unique ID
- SMS sends successfully with ID reference
- "n5 decide dec_xxx A" resolves and moves to resolved/
- Resolution reaches zoputer if origin was zoputer

---

## Phase 4: Zoputer Autonomy Rules

### Affected Files
- `Documents/consulting/autonomy-config.yaml` - CREATE - autonomy settings
- `Skills/learning-logger/SKILL.md` - CREATE - skill for zoputer
- `Skills/learning-logger/scripts/log_learning.py` - CREATE - commit logic
- `.github/workflows/learning-pr.yaml` - CREATE - auto-PR workflow
- `N5/scripts/review_learning_pr.py` - CREATE - va-side review prompt

### Changes

**4.1 Autonomy Config:**
```yaml
# autonomy-config.yaml
version: 1.0
autonomy_level: medium

thresholds:
  escalate_to_va: 0.7      # Confidence below this → ask va
  escalate_to_human: 0.5   # Confidence below this → ask V
  auto_adapt: 0.9          # Confidence above this → do it

allowed_self_edits:
  - Learnings/*
  - Runtime/*
  
forbidden_self_edits:
  - Skills/*
  - Documents/System/*
  - anything with .n5protected

learning_branch: zoputer/learnings
require_pr_for_main: true
```

**4.2 Learning Logger (for zoputer):**
```python
# log_learning.py
def log_learning(learning: str, source: str, category: str):
    """Commit a learning to zoputer's branch."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Learnings/{category}/{timestamp}_{slugify(learning[:30])}.md"
    
    content = f"""---
created: {date.today()}
source: {source}
category: {category}
---

# Learning

{learning}
"""
    
    # Write file
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    Path(filename).write_text(content)
    
    # Commit and push to learning branch
    git_commit(filename, f"Learning: {learning[:50]}")
    git_push("zoputer/learnings")
```

**4.3 GitHub Actions Workflow:**
```yaml
# .github/workflows/learning-pr.yaml
name: Auto-PR for Learnings
on:
  push:
    branches: [zoputer/learnings]
    paths: [Learnings/**]

jobs:
  create-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          branch: zoputer/learnings
          base: main
          title: "[Zoputer Learning] New insights from client interactions"
          body: "Auto-generated PR from zoputer's learning branch. Review before merging."
```

**4.4 Va-Side PR Review:**
- Scheduled check for open PRs from zoputer
- Load PR diff, assess quality
- Either approve/merge or request changes
- Notify V if unsure

### Unit Tests
- zoputer commits learning → file appears in repo
- Push to learning branch → PR created automatically
- va reviews PR → merge or comment

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Drop | Status |
|------------|------|--------|
| GitHub repo creation | D1.1 | ✓ |
| Branch protection setup | D1.1 | ✓ |
| `Skills/git-sync/` | D1.2 | ✓ |
| `N5/config/git_sync_config.yaml` | D1.2 | ✓ |
| Scheduled agent `GIT_SYNC_ZOPUTER` | D1.3 | ✓ |
| VA_API_KEY setup guide | D2.1 | ✓ |
| `Skills/mentor-escalation/` | D2.2 | ✓ |
| va escalation handler | D2.3 | ✓ |
| `N5/data/pending_decisions/` structure | D3.1 | ✓ |
| `Skills/decision-bridge/` | D3.2 | ✓ |
| SMS rule for "n5 decide" | D3.3 | ✓ |
| `Documents/consulting/autonomy-config.yaml` | D4.1 | ✓ |
| `Skills/learning-logger/` | D4.2 | ✓ |
| GitHub Actions workflow | D4.3 | ✓ |
| va PR review script | D4.3 | ✓ |

### Token Budget Summary

| Drop | Brief (est.) | Files (est.) | Total % | Status |
|------|--------------|--------------|---------|--------|
| D1.1 | ~1,500 | ~2,000 | ~2% | ✓ |
| D1.2 | ~2,000 | ~4,000 | ~3% | ✓ |
| D1.3 | ~1,000 | ~2,000 | ~1.5% | ✓ |
| D2.1 | ~1,000 | ~1,000 | ~1% | ✓ |
| D2.2 | ~2,000 | ~3,000 | ~2.5% | ✓ |
| D2.3 | ~1,500 | ~3,000 | ~2% | ✓ |
| D3.1 | ~1,500 | ~1,500 | ~1.5% | ✓ |
| D3.2 | ~2,000 | ~4,000 | ~3% | ✓ |
| D3.3 | ~1,500 | ~2,000 | ~1.5% | ✓ |
| D4.1 | ~1,000 | ~1,500 | ~1% | ✓ |
| D4.2 | ~2,000 | ~3,000 | ~2.5% | ✓ |
| D4.3 | ~1,500 | ~3,000 | ~2% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE drop (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All drops within 40% token budget
- [ ] Wave dependencies validated (see below)
- [ ] `python3 N5/scripts/mece_validator.py zoputer-autonomy-v2` passes

---

## Streams & Drops

### Stream 1: GitHub Infrastructure (Sequential - foundation)

| Wave | Drop | Name | Depends On | Spawn |
|------|------|------|------------|-------|
| 1 | D1.1 | GitHub Repo Setup | - | manual (needs gh auth) |
| 1 | D1.2 | Git Sync Skill | D1.1 | auto |
| 1 | D1.3 | Sync Scheduled Agent | D1.2 | auto |

### Stream 2: Bidirectional Communication (After Stream 1)

| Wave | Drop | Name | Depends On | Spawn |
|------|------|------|------------|-------|
| 2 | D2.1 | VA_API_KEY Setup Guide | D1.1 | auto |
| 2 | D2.2 | Mentor Escalation Skill | D2.1 | auto |
| 2 | D2.3 | Va Escalation Handler | D2.2 | auto |

### Stream 3: Human Escalation (After D2.3)

| Wave | Drop | Name | Depends On | Spawn |
|------|------|------|------------|-------|
| 3 | D3.1 | Pending Decisions Structure | - | auto |
| 3 | D3.2 | Decision Bridge Skill | D3.1 | auto |
| 3 | D3.3 | SMS Rule + Resolution | D3.2 | auto |

### Stream 4: Autonomy Rules (After D3.3)

| Wave | Drop | Name | Depends On | Spawn |
|------|------|------|------------|-------|
| 4 | D4.1 | Autonomy Config | - | auto |
| 4 | D4.2 | Learning Logger Skill | D4.1, D1.2 | auto |
| 4 | D4.3 | GitHub Actions + Review | D4.2 | auto |

---

## Success Criteria

1. ✅ `gh repo view vrijenattawar/zoputer-substrate` returns repo info
2. ✅ va pushes skill change → appears in repo within 15 min
3. ✅ zoputer pulls from repo → has latest skills
4. ✅ zoputer calls va via /zo/ask → gets mentor response
5. ✅ va/zoputer packages decision → V gets SMS with reference ID
6. ✅ V responds "n5 decide {id} A" → decision routes back to origin
7. ✅ zoputer commits learning → PR auto-created → va reviews
8. ✅ Full audit trail for all inter-Zo and human-in-loop comms

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| GitHub rate limits | Batch commits, 15-min interval (not real-time) |
| API key exposure | Keys in secrets, never in code/commits |
| Decision context too large for SMS | SMS has ID only; full context in JSON file |
| zoputer escalates too often | Tunable threshold, start at 0.7 |
| PR backlog overwhelms va | Weekly digest, batch reviews |
| Cross-thread resolution fails | Unique ID + JSON files = thread-agnostic |

---

## Level Upper Review

*To be completed before finalizing.*

### Counterintuitive Suggestions Received:
1. (pending)

### Incorporated:
- (pending)

### Rejected (with rationale):
- (pending)

---

## Manual Steps Required (V)

1. **After D1.1:** Confirm repo created, review branch protection
2. **After D2.1:** Execute VA_API_KEY setup on zoputer manually
3. **After D3.3:** Test SMS escalation end-to-end
4. **After D4.3:** Review first auto-PR from zoputer

---

## Handoff Notes

When plan is approved:
1. Run MECE validator: `python3 N5/scripts/mece_validator.py zoputer-autonomy-v2`
2. Generate worker briefs in `N5/builds/zoputer-autonomy-v2/workers/`
3. Route to Builder for execution
