# N5OS Core - Phase 5 Orchestrator Kickoff

**Project**: N5 OS (Cesc v0.1)  
**Phase**: 5 - Workflows  
**Status**: Ready to Execute  
**Prerequisites**: Phases 0-4 Complete

---

## Context for Orchestrator

You are building **Phase 5: Workflows** for N5 OS Core distribution.

**What this is**: Creating self-maintaining workflow systems that:
- Process conversation outputs into structured knowledge
- Enforce SSOT (Single Source of Truth) principles
- Extract tasks and commitments automatically
- Maintain portable knowledge structures

**Critical**: This is a **REBUILD**, not a port. The current conversation-end workflow on Main has flaws. Build fresh with lessons learned.

**Where you're building**: Demonstrator Zo account

**What you have access to**:
- Full specification: `file '/home/workspace/N5/logs/threads/2025-10-28-0136_N5-OS-Core-Phase-0-Complete_MANUAL/n5os_core_spec.md'`
- Planning prompt: `file '/home/workspace/Knowledge/architectural/planning_prompt.md'`
- Architectural principles: `file '/home/workspace/Knowledge/architectural/architectural_principles.md'`

---

## Phase 5 Components

### 5.1: Conversation End Workflow (REBUILD)

**Purpose**: Review → Classify → Propose → Execute pattern for conversation outputs

**What it does**:
1. **Review**: Scan conversation for deliverables, insights, decisions
2. **Classify**: Determine what goes where (Knowledge vs Lists vs Archives)
3. **Propose**: Show user destinations and ask for confirmation
4. **Execute**: Move files, create knowledge entries, extract tasks

**Current flaws to fix** (from Main system):
- Too complex/heavyweight for simple conversations
- Unclear about what triggers full workflow vs lightweight cleanup
- Missing confidence scoring (when to auto-execute vs ask)
- Poor handling of already-organized conversations

**Rebuild approach**:
```markdown
SIMPLE pattern:
- If conversation workspace is empty → Nothing to do
- If < 3 substantial files → Lightweight (just ask where to move)
- If >= 3 substantial files OR complex topic → Full workflow

GRADUATED automation:
- High confidence moves (logs, obvious temp files) → Auto
- Medium confidence → Preview + one-click approve
- Low confidence → Manual review required
```

**Key scripts**:
- `/N5/scripts/conversation_end.py` - Main orchestrator
- `/N5/scripts/classify_output.py` - AI-powered classification
- `/N5/scripts/knowledge_extract.py` - Extract insights to Knowledge/
- `/N5/scripts/task_extract.py` - Extract tasks to Lists/

---

### 5.2: Knowledge Management

**Purpose**: Maintain SSOT for structured knowledge

**What it does**:
1. **Ingestion**: Convert raw Records → structured Knowledge
2. **Validation**: Enforce schemas, prevent duplicates
3. **Migration**: Handle updates without breaking references
4. **Portable structures**: JSON/JSONL that travels between systems

**Key patterns**:
```markdown
Records/ (raw intake)
  ↓ [process + validate]
Knowledge/ (structured, portable)
  ↓ [reference]
Lists/ (actionable tasks)
```

**Key scripts**:
- `/N5/scripts/knowledge_ingest.py` - Records → Knowledge pipeline
- `/N5/scripts/knowledge_validate.py` - Schema validation
- `/N5/scripts/knowledge_dedupe.py` - Detect and merge duplicates

---

## Phase 5 Breakdown (3 Sub-Phases)

### Phase 5.1: Lightweight Conversation Cleanup
**Deliverables**:
- Simple file mover with preview
- Handles empty or minimal conversations
- No heavy processing for simple cases

**Test**: Empty conversation → No action. 2-file conversation → Quick move proposal.

---

### Phase 5.2: Full Conversation End Workflow
**Deliverables**:
- Classification engine (AI-powered)
- Knowledge extraction
- Task extraction
- Confidence-based automation

**Test**: Complex conversation with mixed outputs → Correctly classifies, proposes destinations, executes cleanly.

---

### Phase 5.3: Knowledge Management System
**Deliverables**:
- Ingestion pipeline (Records → Knowledge)
- Schema validation
- Deduplication logic
- Portable structure templates

**Test**: Raw meeting notes → Structured knowledge entry. Duplicate detection works. Schema violations caught.

---

## Design Constraints

### From Spec
- **P1 (Human-Readable)**: All knowledge files must be readable markdown/JSONL
- **P2 (SSOT)**: One canonical location per fact
- **P5 (Anti-Overwrite)**: Never destroy without explicit confirmation
- **P8 (Minimal Context)**: Don't load entire Knowledge/ to make decisions
- **P15 (Complete Before Claiming)**: Test thoroughly before declaring done

### From Planning Prompt
- **Simple Over Easy**: Choose disentangled workflows over convenient shortcuts
- **Flow Over Pools**: Design for streaming, not batching
- **Think→Plan→Execute**: 40% Think, 30% Plan, 10% Execute, 20% Review

---

## What to Learn from Main System

### Study these (but don't copy):
- `/home/workspace/N5/scripts/n5_conversation_end.py` - See current approach
- `/home/workspace/N5/prefs/operations/conversation-end.md` - See current protocol
- `/home/workspace/Knowledge/architectural/ingestion_standards.md` - See SSOT rules

### Key lessons to apply:
1. **Graduated automation** is better than all-or-nothing
2. **Confidence scoring** prevents over-automation
3. **Preview before execute** builds user trust
4. **Empty state handling** prevents unnecessary prompts

### What NOT to replicate:
- Overly complex classification logic
- Assumptions about folder structure
- Tight coupling to V's specific workflow
- Missing documentation

---

## Success Criteria (Phase 5 Complete)

- [ ] Empty conversation → No annoying prompts
- [ ] Simple conversation (2 files) → Quick move in < 30 seconds
- [ ] Complex conversation (5+ files) → Intelligent classification + extraction
- [ ] Knowledge ingestion preserves SSOT
- [ ] Schema validation catches errors
- [ ] Duplicate detection works reliably
- [ ] All workflows have dry-run mode
- [ ] Documentation explains when to use what
- [ ] Fresh user can understand and customize

---

## First Steps

### Before You Start
1. **CRITICAL**: Load `file '/home/workspace/Knowledge/architectural/planning_prompt.md'`
2. Load N5OS spec to understand overall architecture
3. Study Main system's conversation-end workflow (learn from it, don't copy it)
4. Ask 3+ clarifying questions if ANY doubt

### Start With Phase 5.1 (Lightweight Cleanup)
Build the simple case first. Don't try to handle every edge case on day 1.

**Think → Plan → Execute**:
- **Think (40%)**: What makes a conversation "simple" vs "complex"? What's the minimal action needed?
- **Plan (30%)**: Design the lightweight workflow. Document decision tree.
- **Execute (10%)**: Build the script.
- **Review (20%)**: Test edge cases, refine thresholds.

---

## Architecture Diagram

```
Conversation End Trigger
  ↓
Check conversation workspace
  ↓
Empty? → Done
  ↓
< 3 files? → Lightweight flow
  |  ↓
  |  Preview → User confirms → Move
  ↓
>= 3 files? → Full workflow
  ↓
  AI Classification
    ↓
  Extract Knowledge (if applicable)
    ↓
  Extract Tasks (if applicable)
    ↓
  Preview all actions
    ↓
  User confirms → Execute
    ↓
  Verify state → Done
```

---

## Testing Strategy

### Unit Tests (Per Component)
- File classifier: Does it correctly identify temp vs permanent?
- Knowledge extractor: Does it create valid knowledge entries?
- Task extractor: Does it parse tasks correctly?

### Integration Tests (Full Flow)
- End-to-end: Real conversation → Correct destinations
- Edge cases: Empty, massive, mixed content
- Error handling: Invalid files, schema violations

### User Acceptance
- Time to complete: < 2 minutes for typical conversation
- Error rate: < 5% misclassifications
- User clarity: Can understand why AI made each choice

---

## Documentation Requirements

### Files to Create

1. **/docs/phase5_workflows.md**
   - When conversation end runs
   - How classification works
   - How to customize

2. **/docs/knowledge_management.md**
   - Records → Knowledge pipeline
   - Schema documentation
   - How to add custom schemas

3. **/N5/templates/knowledge.template.md**
   - Example knowledge entry
   - Required fields
   - Optional fields

4. **CHANGELOG.md update**
   - Phase 5 features
   - Breaking changes (if any)
   - Migration guide

---

## Handoff to Next Phase

### When Phase 5 is Complete
1. Document lessons learned (what worked/didn't in rebuild)
2. Create handoff for Phase 6 (if applicable) or final polish
3. Update main spec with any design changes
4. Report to planning thread

### What Comes After Phase 5
Per spec, Phase 5 is the last core phase. After this:
- Final integration testing across all phases
- Polish documentation
- Community testing
- Release v0.2 (first feature-complete version)

---

## Communication Protocol

### Report Progress
- Complete each sub-phase before moving on
- Document decisions and trade-offs
- Note any deviations from plan

### Ask for Help
- If Main system patterns unclear
- If design decisions need V's input
- If you discover fatal flaws in approach

---

## Key Principles

**From Planning Prompt**:
- **Nemawashi**: Explore 2-3 workflow alternatives before choosing
- **Trap Doors**: Document irreversible decisions (like classification thresholds)
- **Maintenance Over Organization**: Design for easy updates, not perfect hierarchy

**From Architectural Principles**:
- **P0 (Rule-of-Two)**: Don't load entire Knowledge base to classify one file
- **P7 (Dry-Run)**: Every workflow has --dry-run flag
- **P11 (Failure Modes)**: Handle corrupted files, network issues, schema errors
- **P18 (Verify State)**: Check that moves succeeded before claiming done

---

## Ready?

1. Load planning prompt ✅
2. Load N5OS spec ✅
3. Study Main conversation-end workflow ✅
4. Think about lightweight vs full workflow distinction ⏳
5. Start Phase 5.1 ⏳

**Remember**: Rebuild, don't port. Apply lessons learned. Simple > Easy.

---

*Created: 2025-10-28 05:16 ET*
