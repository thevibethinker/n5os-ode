---
created: 2026-01-19
last_edited: 2026-01-19
version: 2.0
type: build_plan
status: ready
provenance: con_PsffYknEXs0T7a81
---

# Plan: Zo Take Heed - Verbal Cue System

**Objective:** Create a "prompt bomb" system where V says "Zo take heed: [instruction]" during meetings to either (a) inject directives that influence block generation, or (b) spawn discrete work requests (emails, blurbs, research) that execute or queue based on task type.

**Trigger:** V wants real-time control over meeting outputs without post-processing intervention, plus the ability to plant work requests that detonate during processing.

**Key Design Principle:** ZTH cues are deferred intents. They get captured during transcription and explode into action during MG-2 processing.

---

## Open Questions

<!-- All resolved -->
- [x] Trigger phrase? → "Zo take heed" (case-insensitive, with variants)
- [x] Output format? → B00.jsonl (machine) + worker files for spawn triggers
- [x] Auto-execute vs queue? → Task-type dependent (see Execution Policy below)
- [x] What happens to existing MG-3/MG-5 agents? → Deprecate (disable), retain prompts as on-demand triggers

---

## Execution Policy (Task Type → Behavior)

| Task Type | Example ZTH | Behavior |
|-----------|-------------|----------|
| **Directive** | "omit pricing from recap" | Influences B01/B14 generation inline |
| **Blurb** | "generate a blurb for this call" | **Auto-execute** via Blurb-Generator.prompt.md |
| **Follow-up Email** | "prep a follow-up email" | **Auto-execute** via Follow-Up Email Generator.prompt.md + voice system |
| **Warm Intro** | "draft warm intro to [person]" | **Auto-execute** via warm intro prompt |
| **Research** | "research [topic]" | **Queue** → generates worker file, does NOT execute |
| **Custom/Unknown** | anything else | **Queue** → generates worker file for HITL review |

**Default behavior:** If task type is ambiguous, **queue** (generate worker file, don't execute).

---

## Checklist

### Phase 1: B00 Extraction + Classification
- ☑ Create `Prompts/Blocks/Generate_B00.prompt.md` with extraction logic
- ☑ Create `N5/schemas/B00_ZO_TAKE_HEED.schema.json`
- ☑ Add task type classifier (directive vs spawn trigger)
- ☑ Test: Validation script passes (7/7 tests)

### Phase 2: Spawn Trigger System
- ☑ Create worker file generator: `N5/scripts/zth_spawn_worker.py`
- ☑ Define worker file schema: `N5/templates/zth_worker.md`
- ☐ Wire into MG-2 pipeline after B00 extraction (Phase 3)
- ☑ Test: spawn_worker.py passes 4/4 tests

### Phase 3: Pipeline Integration + Agent Deprecation
- ☑ Update MG-2 to process B00 first (v2.4)
- ☑ Disable MG-3 (blurb) scheduled agent
- ☑ Disable MG-5 (follow-up) scheduled agent
- ☑ Archive agent prompts to `Prompts/Archive/`
- ☑ Add `zo_take_heed_count` to manifest.json (in MG-2 prompt)
- ☐ Test: Full meeting processing with ZTH cues → correct outputs (manual verification)

---

## Phase 1: B00 Extraction + Classification

### Affected Files
- `Prompts/Blocks/Generate_B00.prompt.md` - CREATE - Extraction prompt
- `N5/schemas/B00_ZO_TAKE_HEED.schema.json` - CREATE - JSONL schema

### Changes

**1.1 Create B00 Extraction Prompt:**

The prompt should:
1. Scan transcript for trigger phrases: "zo take heed", "zo, take heed", "zo takeheed"
2. Extract the instruction that follows (until natural boundary: new speaker, topic shift, or next cue)
3. Capture approximate timestamp from transcript context
4. Classify into task type: `directive`, `blurb`, `follow_up_email`, `warm_intro`, `research`, `custom`
5. Determine execution policy: `auto_execute` or `queue`

**1.2 B00 Schema:**

```json
{
  "id": "ZTH-001",
  "timestamp": "00:14:32",
  "raw_cue": "Zo take heed, prep a follow-up email emphasizing our integration capabilities",
  "instruction": "prep a follow-up email emphasizing our integration capabilities",
  "task_type": "follow_up_email",
  "execution_policy": "auto_execute",
  "scope": ["follow_up_email"],
  "context": "Discussion about API integration with prospect"
}
```

**1.3 Task Type Classifier:**

Rules for classification:
- Contains "blurb" → `blurb`
- Contains "follow-up", "follow up", "email" (without specific recipient) → `follow_up_email`
- Contains "intro to", "introduce me to", "warm intro" → `warm_intro`
- Contains "research", "look into", "find out about" → `research`
- Contains modifiers only (omit, emphasize, don't mention, highlight) → `directive`
- Otherwise → `custom`

### Unit Tests
- Empty transcript → empty B00.jsonl (no errors)
- Transcript with "Zo take heed, omit pricing" → directive type, influences B01
- Transcript with "Zo take heed, prep follow-up" → follow_up_email, auto_execute
- Transcript with "Zo take heed, research their funding" → research, queue

---

## Phase 2: Spawn Trigger System

### Affected Files
- `N5/scripts/zth_spawn_worker.py` - CREATE - Generates worker files
- `N5/templates/zth_worker.md` - CREATE - Worker file template

### Changes

**2.1 Worker File Generator:**

Script that takes a B00 entry and generates a self-contained worker file:

```bash
python3 N5/scripts/zth_spawn_worker.py --meeting-folder <path> --zth-id ZTH-001
```

Output: `<meeting-folder>/workers/ZTH-001_follow_up_email.md`

**2.2 Worker File Structure:**

```markdown
---
created: 2026-01-19
type: zth_worker
zth_id: ZTH-001
task_type: follow_up_email
execution_policy: auto_execute
meeting_id: 2026-01-19_Jake-Smith
status: pending
---

# ZTH Worker: Follow-Up Email

## Original Cue
> "Zo take heed, prep a follow-up email emphasizing our integration capabilities"

## Context
Meeting: Jake Smith (Acme Corp) - Partnership Discussion
Key topics: API integration, pricing model, timeline

## Instruction
Generate a follow-up email for this meeting. Emphasize our integration capabilities.

## Execution
Run: `file 'Prompts/Follow-Up Email Generator.prompt.md'`
With context from: `file '<meeting-folder>/B01_DETAILED_RECAP.md'`

## Voice Requirements
Apply voice system: `python3 N5/scripts/retrieve_voice_lessons.py --content-type follow_up`
```

**2.3 Execution Logic:**

In MG-2, after B00 extraction:
1. For each B00 entry with `execution_policy: auto_execute`:
   - Generate worker file
   - Immediately execute the referenced prompt
   - Update worker status to `completed`
2. For each B00 entry with `execution_policy: queue`:
   - Generate worker file only
   - Update worker status to `queued`
   - These await manual trigger

### Unit Tests
- ZTH with auto_execute → worker generated AND executed
- ZTH with queue → worker generated, NOT executed
- Multiple ZTH in one meeting → multiple worker files, correct execution

---

## Phase 3: Pipeline Integration + Agent Deprecation

### Affected Files
- `Prompts/Meeting Block Generation.prompt.md` - UPDATE - Add B00 to block list
- Agent `5579f899-3b9a-41c6-9615-ba4a400ce053` - DISABLE - MG-3 Blurb Generation
- Agent `c7d010d5-02f5-4e5d-a0b5-2eb6a6565962` - DISABLE - MG-5 Follow-Up Generation
- `Prompts/Archive/MG-3_Blurb_Generation_DEPRECATED.md` - CREATE - Archive
- `Prompts/Archive/MG-4_FollowUp_Generation_DEPRECATED.md` - CREATE - Archive

### Changes

**3.1 Update MG-2 Pipeline:**

Add to Meeting Block Generation prompt:
```
FIRST, check for and process B00 (Zo Take Heed cues):
1. Run Generate_B00.prompt.md on transcript
2. For each spawn trigger with auto_execute, run the appropriate generator
3. For directives, carry them forward to influence subsequent blocks
```

**3.2 Deprecate Auto-Generation Agents:**

Disable scheduled agents:
- MG-3: `5579f899-3b9a-41c6-9615-ba4a400ce053` (blurb)
- MG-5: `c7d010d5-02f5-4e5d-a0b5-2eb6a6565962` (follow-up)

Archive their prompts to `Prompts/Archive/` with DEPRECATED suffix.

**Retained capability:** V can still manually run Blurb-Generator.prompt.md or Follow-Up Email Generator.prompt.md on any meeting. ZTH just makes it voice-triggered.

**3.3 Manifest Updates:**

Add to manifest.json after B00 processing:
```json
{
  "zo_take_heed_count": 3,
  "zo_take_heed_summary": [
    {"id": "ZTH-001", "type": "follow_up_email", "status": "executed"},
    {"id": "ZTH-002", "type": "directive", "status": "applied"},
    {"id": "ZTH-003", "type": "research", "status": "queued"}
  ]
}
```

### Unit Tests
- Meeting with no ZTH → pipeline works normally, no blurb/email auto-generated
- Meeting with "prep follow-up" ZTH → follow-up email generated
- Meeting with "research X" ZTH → worker queued, nothing auto-executed
- Directive ZTH → influences B01 content (verify manually)

---

## Success Criteria

1. "Zo take heed" phrases are reliably detected in transcripts (>95% recall)
2. Task type classification is correct (>90% accuracy)
3. Auto-execute tasks (blurb, email) complete without manual intervention
4. Queue tasks generate worker files without executing
5. Directives visibly influence downstream block content
6. MG-3 and MG-5 agents disabled; blurb/email only generated on ZTH trigger
7. Manual blurb/email generation still works for any meeting

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| ZTH phrase missed due to transcription errors | Support variants; consider fuzzy matching |
| Instruction boundary unclear | Use speaker change + topic shift as delimiters |
| Task type misclassified | Default to `queue` when uncertain |
| Auto-execute spam (V triggers 10 emails) | Soft warning if >3 auto-execute per meeting |
| Voice system not applied | Explicit voice retrieval step in worker template |

---

## Level Upper Review

### Incorporated:
- ✅ Manifest flag with `zo_take_heed_count` and summary
- ✅ Queue as default for uncertain task types
- ✅ Worker files as self-contained prompt documents

### Design Decision:
- ZTH replaces auto-generation agents; blurbs/emails are now opt-in via voice cue
- Retains manual trigger capability for any meeting
