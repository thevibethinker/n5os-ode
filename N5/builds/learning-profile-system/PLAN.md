---
created: 2026-01-13
last_edited: 2026-01-13
version: 1.0
type: build_plan
status: complete
provenance: con_ADRk5LpNvaHYxv1y
---

# Plan: Learning Profile + Conversation Close Intelligence

**Objective:** Create a persistent learning profile for V that the Vibe Teacher references on activation, with a scalable conversation-end hook that prompts commit options to multiple artifact destinations (learning profile, content library, voice library, git).

**Trigger:** V wants the system to remember what he's learned across conversations, similar to how Vibe Trainer maintains coaching notes. Plus, conversation-end should suggest commits to multiple destinations, not just git.

**Key Design Principle:** LLM-first detection. Scripts gather mechanical context; LLM applies semantic understanding to determine what's worth committing where. This is the same philosophy as conversation-end v3.0.

---

## Open Questions

<!-- All resolved through conversation with V -->
- [x] Where should learning profile live? → `Personal/Learning/my-learning-profile.md`
- [x] Should commits be automatic or prompted? → **Prompted** (triggering options, not auto-commits)
- [x] Should system be scalable for future categories? → **Yes** (registry-based design)
- [x] Voice Library categorization? → **Worker spawned** (`WORKER_xv1y_20260113_163016`) to design schema
- [x] Learning Profile focus? → Present understanding + future learning areas + cross-disciplinary integration opportunities
- [x] Content Library threshold? → **HIGH bar**: deep engagement + positive response; system should push back when inclusion would weaken coherence or add redundancy

---

## Alternatives Considered (Nemawashi)

| Alternative | Description | Decision |
|-------------|-------------|----------|
| Centralized Commit Registry | Single JSON config with detection heuristics per category | Rejected — heuristics are brittle |
| Per-Category Hooks | Separate scripts for each commit target | Rejected — harder to add new categories |
| **LLM-First Detection** | Scripts gather context, LLM decides relevance semantically | **Selected** — aligns with conversation-end v3.0 philosophy |

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| Learning profile file path | Low cost | Can move file later if needed |
| Commit target registry format | Medium cost | Schema should be designed for extension |
| Vibe Teacher persona update | Low cost | Persona prompts are easily edited |

**No major trap doors identified.** All decisions are reversible.

---

## Checklist

### Phase 1: Learning Profile Foundation
- ☑ Create `Personal/Learning/my-learning-profile.md` with initial structure
- ☑ Create `N5/config/commit_targets.json` registry
- ☑ Test: File exists and is valid

### Phase 2: Vibe Teacher Integration
- ☑ Update Vibe Teacher persona to reference learning profile
- ☑ Update `N5/prefs/workflows/teacher_workflow.md` with Phase 0 loader
- ☑ Test: Teacher workflow contains load context step

### Phase 3: Conversation-End Commit Options
- ☑ Update `Close Conversation.prompt.md` with commit target workflow (Step 5)
- ☑ Added semantic detection table and quality gates
- ☑ Test: Close Conversation contains Commit Target Suggestions section

---

## Phase 1: Learning Profile Foundation

### Affected Files
- `Personal/Learning/my-learning-profile.md` - CREATE - V's persistent learning record
- `N5/config/commit_targets.json` - CREATE - Registry of all commit destinations

### Changes

**1.1 Create Learning Profile:**

Create `Personal/Learning/my-learning-profile.md` with structure:

```markdown
---
created: 2026-01-13
last_edited: 2026-01-13
version: 1.0
---

# V's Learning Profile

> **Purpose:** A living document maintained across conversations. Updated when V learns something significant. Referenced by Vibe Teacher to calibrate teaching.

---

## Current Technical Level

| Area | Level | Notes |
|------|-------|-------|
| System architecture | Solid | Workflows, SSOT, modular design |
| Data structures | Solid | JSONL, schemas, file organization |
| High-level abstractions | Solid | APIs as contracts, state management |
| Implementation mechanics | Learning | async/await, error handling, HTTP |
| Developer tooling | Learning | git workflows, debugging, testing |
| Low-level programming | Gap | Memory, concurrency, networking internals |

---

## Areas for Future Learning

*Explicit gaps and next frontiers. Updated as topics surface in conversations.*

- [ ] Deep understanding of async/await patterns
- [ ] Git branching strategies beyond basics
- [ ] Database query optimization
- [ ] HTTP internals and request lifecycle

---

## Cross-Disciplinary Opportunities

*Places where concepts from different domains could integrate. Spotted patterns for "aha moments."*

| Domain A | Domain B | Potential Connection |
|----------|----------|---------------------|
| Career coaching | System design | Both involve stakeholder discovery → requirements → deliverable |
| Meeting workflows | Event-driven systems | Triggers, state transitions, async processing |
| Voice transformation | NLP/LLM prompting | Both shape output through structured constraints |

---

## Learning Timeline

*Milestone understanding shifts, organized chronologically. Updated at conversation-end when genuine learning occurs.*

### 2026-01

<!-- Entries added via conversation-end commit -->

---

## Analogies That Clicked

*Reference for future teaching. When an analogy lands, record it here.*

| Concept | Analogy | Why It Worked |
|---------|---------|---------------|
| APIs | Career coaching intake forms | Familiar domain, clear parallel |

---

## Learning Style Notes

- Responds well to "why before how"
- Needs 10-15% stretch, not 50% jumps
- Analogies from career coaching and N5 architecture work best
- Prefers application questions over recall

---

*This document is maintained by the Vibe Teacher persona and updated via conversation-end workflow.*
```

**1.2 Create Commit Targets Registry:**

Create `N5/config/commit_targets.json`:

```json
{
  "version": "1.0",
  "description": "Registry of destinations for conversation-end commit suggestions",
  "targets": [
    {
      "id": "learning_profile",
      "name": "Learning Profile",
      "destination": "Personal/Learning/my-learning-profile.md",
      "description": "Record concepts learned or technical understanding gained",
      "detection_hints": [
        "teaching session",
        "vibe teacher active",
        "learned about",
        "now understand",
        "technical explanation"
      ],
      "commit_prompt": "What concepts or technical understanding did V gain in this conversation?",
      "section_to_update": "## Learning Timeline"
    },
    {
      "id": "content_library",
      "name": "Content Library",
      "destination": "Knowledge/content-library/",
      "description": "Save excellent articles, papers, or resources worth preserving",
      "detection_hints": [
        "deep engagement with resource",
        "positive response from V",
        "returned to multiple times"
      ],
      "quality_gate": {
        "threshold": "HIGH",
        "criteria": [
          "We dug deeply into the resource (not just skimmed)",
          "V responded positively or expressed value",
          "Inclusion would NOT weaken or create redundancy with existing library"
        ],
        "pushback_allowed": true,
        "pushback_examples": [
          "This overlaps significantly with [existing item] — skip unless it adds something distinct",
          "We only skimmed this; revisit before committing",
          "This is good but not reference-grade — consider Knowledge/notes instead"
        ]
      },
      "commit_prompt": "Were any resources discovered that meet the HIGH bar for Content Library inclusion?",
      "ingest_script": "python3 N5/scripts/content_ingest.py"
    },
    {
      "id": "voice_library",
      "name": "Voice Library",
      "destination": "Knowledge/voice-library/",
      "description": "Capture phrases, writing patterns, or style elements to preserve V's voice",
      "detection_hints": [
        "writing style",
        "phrase",
        "voice",
        "tone",
        "how V would say"
      ],
      "commit_prompt": "Were any distinctive phrases or writing patterns worth adding to the Voice Library?"
    },
    {
      "id": "git",
      "name": "Git Repository",
      "destination": "/home/workspace/.git",
      "description": "Commit code or configuration changes to version control",
      "detection_hints": [
        "code changes",
        "script created",
        "configuration updated"
      ],
      "commit_prompt": "Are there code or configuration changes worth committing?"
    }
  ]
}
```

### Unit Tests
- `ls Personal/Learning/my-learning-profile.md` returns file
- `cat N5/config/commit_targets.json | jq .targets` returns 4 targets
- JSON is valid: `python3 -c "import json; json.load(open('N5/config/commit_targets.json'))"`

---

## Phase 2: Vibe Teacher Integration

### Affected Files
- Vibe Teacher persona - UPDATE - Add learning profile reference
- `N5/prefs/workflows/teacher_workflow.md` - UPDATE - Add profile loading step

### Changes

**2.1 Update Vibe Teacher Persona:**

Add to the Vibe Teacher persona prompt (after the existing content):

```markdown
## Learning Profile Reference

**On activation:** Load V's learning profile from `file 'Personal/Learning/my-learning-profile.md'`

This profile contains:
- V's current technical level by domain
- Concepts previously mastered (don't re-teach)
- Analogies that have worked before
- Known knowledge gaps to address

**Teaching is cumulative.** Reference prior learning. Build on foundations.
```

**2.2 Update Teacher Workflow:**

Add to `N5/prefs/workflows/teacher_workflow.md` at the beginning of Phase 1:

```markdown
### 1.0 Load Learning Context (MANDATORY)

Before any teaching, load the learning profile:

```bash
# Read the current profile
cat Personal/Learning/my-learning-profile.md
```

Use this to:
- Skip re-explaining concepts already mastered
- Reference analogies that previously clicked
- Target known gaps if relevant to current topic
```

### Unit Tests
- Vibe Teacher persona contains "Learning Profile Reference" section
- Teacher workflow contains "Load Learning Context" step
- Activating Vibe Teacher with `set_active_persona` and asking about a topic should reference the profile

---

## Phase 3: Conversation-End Commit Options

### Affected Files
- `Prompts/Close Conversation.prompt.md` - UPDATE - Add commit target workflow
- `N5/prefs/operations/conversation-end-v3.md` - UPDATE - Add commit target section (if exists)

### Changes

**3.1 Update Close Conversation Prompt:**

Add new section after "Step 4: Final Checks" in `Prompts/Close Conversation.prompt.md`:

```markdown
### Step 5: Commit Target Suggestions

**Load the commit targets registry:**
```bash
cat N5/config/commit_targets.json
```

**For each target, evaluate if the conversation produced relevant artifacts:**

Present options to V as a checklist (do NOT auto-commit):

```markdown
## Commit Opportunities

Based on this conversation, you may want to commit to:

☐ **Learning Profile** — [Specific concepts learned, if any]
☐ **Content Library** — [Articles/resources saved, if any]
☐ **Voice Library** — [Distinctive phrases captured, if any]
☐ **Git** — [Code changes detected, if any]

Reply with which items to commit, or skip to close.
```

**For each confirmed commit:**
- Learning Profile: Append entry to `## Learning Timeline` section with date and concept
- Content Library: Run `python3 N5/scripts/content_ingest.py <path> --type <type> --move`
- Voice Library: Append to appropriate section in `Knowledge/voice-library/`
- Git: Run standard git add/commit flow

**Important:** These are triggering options, not automatic. V must confirm before any commit.
```

**3.2 LLM Semantic Detection (Not Script-Based):**

The LLM (Librarian) uses semantic understanding to determine relevance:

- **Learning Profile**: Did V ask questions? Did I explain technical concepts? Did understanding demonstrably increase?
- **Content Library**: Were articles read via `save_webpage` or `read_webpage`? Did V express this was valuable?
- **Voice Library**: Did V use distinctive phrasing I should capture? Did we discuss voice/tone?
- **Git**: Did the conversation produce code changes visible in `git status`?

This is NOT heuristic matching — it's semantic reasoning by the LLM based on conversation context.

### Unit Tests
- `Close Conversation.prompt.md` contains "Commit Target Suggestions" section
- Running conversation-end on a teaching conversation shows Learning Profile option
- Committing to Learning Profile appends a dated entry

---

## Success Criteria

1. ✓ `Personal/Learning/my-learning-profile.md` exists with V's baseline technical levels
2. ✓ Vibe Teacher activation loads the learning profile for context
3. ✓ Conversation-end shows commit options for all 4 targets when relevant
4. ✓ Committing to Learning Profile appends a dated entry
5. ✓ System is scalable: adding a new target only requires JSON registry update + LLM prompt awareness

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Commit suggestions become noise (too many prompts) | LLM only suggests when semantically relevant; V can dismiss |
| Learning profile becomes stale | Vibe Teacher reminds to update; periodic review suggested |
| New targets require code changes | Design for LLM-first detection; new targets are mostly config |

---

## Level Upper Review

*Skipped for this build — scope is clear and risk is low.*

---

## Handoff

**When plan is approved:** Hand off to Builder (`set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")`) with:
- Plan file: `N5/builds/learning-profile-system/PLAN.md`
- Starting phase: 1
- Context: This integrates with existing conversation-end system (v3.0)








