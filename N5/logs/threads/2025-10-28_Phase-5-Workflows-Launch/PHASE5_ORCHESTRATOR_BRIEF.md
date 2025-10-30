# N5OS Core - Phase 5 Orchestrator Brief

**Project**: N5 OS (Cesc v0.1)  
**Phase**: 5 - Workflows  
**Status**: Ready to Launch  
**Prerequisites**: Phases 0-4 Complete ✅  
**Build Location**: Demonstrator account

---

## What You're Building

**Phase 5: Workflows** - The self-maintaining knowledge system that makes N5 OS autonomous.

### Components

1. **Conversation End Workflow** (REBUILD - current Main version flawed)
   - Review → Classify → Propose → Execute
   - Knowledge extraction
   - List/task generation
   
2. **Knowledge Management**
   - SSOT enforcement
   - Portable knowledge structures
   - Migration patterns (Records → Knowledge → Lists)

**Output**: Self-maintaining knowledge system that organizes itself as artifact of use

---

## Critical Context: Why REBUILD?

From spec: "REBUILD ON DEMONSTRATOR" not "port from Main"

**What's wrong with Main's conversation-end?**
- Too complex (9 phases)
- Heavy dependencies (lesson extraction, AAR, personal intelligence)
- Not graduated automation (all-or-nothing)
- Coupling between cleanup and knowledge management

**What N5 OS Core needs:**
- Lightweight (3-4 phases max)
- Modular (cleanup separate from knowledge extraction)
- Graduated automation (confidence-based)
- Zero external dependencies

---

## Planning Prompt Applied

### Design Values for Phase 5

**1. Simple Over Easy**
- Don't port Main's workflow (easy but complex)
- Build fresh with fewer interwoven concepts (simple)
- Each phase independent and testable

**2. Flow Over Pools**
- Conversation workspace → Temp files expire after 7 days
- Records → Process → Knowledge/Lists → Archive
- Every file has destination and time limit

**3. Maintenance Over Organization**
- System proposes moves (AI-automated)
- V reviews exceptions only (<15% touch rate)
- Detect failures automatically

**4. Code Is Free, Thinking Is Expensive**
- Spend 70% planning what this workflow should do
- Identify trap doors (file format? database?)
- Execute fast once design is solid

**5. Nemawashi: Explore Alternatives**
- Should cleanup be separate command from knowledge extraction?
- Should we use database or JSONL for conversation log?
- Should we enforce schemas or use freeform markdown?

---

## Trap Doors to Identify

Before you start coding, answer these:

1. **File formats**: Markdown? JSON? JSONL? SQLite?
   - Trap door: Hard to migrate later
   - Consider: Portability, human-readability, AI-parsability

2. **Automation confidence**: How much autoconfirm vs user review?
   - Trap door: Too automated = data loss, too manual = friction
   - Consider: Graduated automation based on confidence

3. **Knowledge structure**: How do we represent extracted knowledge?
   - Trap door: Schema changes are expensive
   - Consider: Flexible vs structured

4. **Dependency on Main**: What can we learn vs what must we avoid?
   - Trap door: Tight coupling to V-specific components
   - Consider: What's universal vs personal

---

## Phase 5 Sub-Phases (Proposed)

### Phase 5.1: Conversation Cleanup (2h)
**Minimal viable cleanup workflow**

**Scope**:
- Scan conversation workspace
- Classify files (images, scripts, docs, temp)
- Propose moves to standard locations
- Execute with confirmation
- Log actions

**Exclusions**:
- No knowledge extraction yet
- No Records processing
- No AAR generation

**Success**: User can type `conversation-end` and workspace gets cleaned

---

### Phase 5.2: Knowledge Extraction (3h)
**Extract reusable knowledge from conversations**

**Scope**:
- Detect significant conversations (system work, decisions, patterns)
- Extract key insights/decisions
- Format as portable markdown
- Save to Knowledge/ with metadata

**Exclusions**:
- No complex NLP/embeddings
- No personal intelligence layer
- No automatic categorization (user tags)

**Success**: Conversations → Knowledge entries automatically

---

### Phase 5.3: Records Pipeline (2h)
**Formalize Records → Knowledge flow**

**Scope**:
- Define Records structure (Company/, Personal/, Temporary/)
- Build processing script (classify → extract → archive)
- Enforce time limits (Temporary/ expires after 7 days)
- SSOT validation

**Success**: Files in Records/ flow to final destinations automatically

---

## What to Learn from Main (and What NOT to Copy)

### ✅ Learn From Main

**Good patterns**:
- Phase-based execution (clear gates between steps)
- Proposal → Confirmation → Execute flow
- Logging all actions for audit trail
- File classification by type and content
- Non-blocking for optional components

**Reference files**:
- file 'n5os-core/N5/commands/conversation-end.md' - See structure
- file 'N5/scripts/n5_conversation_end.py' - See implementation
- file 'N5/prefs/operations/conversation-end.md' - See protocol

### ❌ Don't Copy From Main

**Avoid**:
- Lesson extraction (too V-specific, belongs in paid module)
- AAR generation (thread-export is separate concern)
- Personal intelligence layer (paid module)
- 9-phase complexity (too much)
- Placeholder detection (belongs in safety system, not workflow)
- Build tracker integration (Build System is Phase 3, not Phase 5)

**Why**: N5 OS Core is minimal foundation. These are value-add modules.

---

## Architecture Principles to Apply

**Critical for Phase 5**:

- **P0 (Rule-of-Two)**: Max 2 config files loaded at once
- **P1 (Human-Readable)**: Markdown > JSON, clear file names
- **P2 (SSOT)**: One source of truth for each piece of knowledge
- **P5 (Anti-Overwrite)**: Never destroy data without confirmation
- **P7 (Dry-Run)**: Preview all moves before executing
- **P8 (Minimal Context)**: Don't load full conversation history
- **P11 (Failure Modes)**: Graceful degradation if phases fail
- **P15 (Complete Before Claiming)**: Verify all files moved successfully
- **P18 (Verify State)**: Check destination exists after move
- **P19 (Error Handling)**: Try/except with logging
- **P21 (Document Assumptions)**: Why these file type classifications?
- **P22 (Language Selection)**: Python for logic, shell for glue

---

## Success Criteria

### Phase 5.1 (Cleanup)
- [ ] Command `conversation-end` triggers workflow
- [ ] Scans conversation workspace (file count logged)
- [ ] Classifies files by type (classification rules documented)
- [ ] Proposes moves (shows user preview)
- [ ] Executes on confirmation (Y/n)
- [ ] Logs all actions to conversation_ends.log
- [ ] Handles errors gracefully (partial moves OK)
- [ ] Dry-run mode works (--dry-run flag)
- [ ] Fresh Zo instance can run it (<10 min setup)

### Phase 5.2 (Knowledge)
- [ ] Detects significant conversations (criteria documented)
- [ ] Extracts key insights (format specified)
- [ ] Saves to Knowledge/ with metadata (schema defined)
- [ ] Non-blocking (continues if extraction fails)
- [ ] User can search extracted knowledge (grep-able)

### Phase 5.3 (Records)
- [ ] Records/ structure exists (Company/, Personal/, Temporary/)
- [ ] Processing script classifies files (rules documented)
- [ ] Enforces time limits (Temporary/ > 7 days deleted)
- [ ] SSOT validation (no duplicate knowledge)
- [ ] Archive flow works (processed files → Archive/)

---

## Think → Plan → Execute Framework

### THINK Phase (40% of time)

**Questions to answer before coding**:

1. **What are we building and why?**
   - Minimal workflow that makes N5 OS self-maintaining
   - Users shouldn't manage files manually
   - Knowledge should organize as artifact of use

2. **What are the trap doors?**
   - File format choices (markdown vs JSON)
   - Automation confidence (when to autoconfirm)
   - Knowledge schema (flexible vs rigid structure)

3. **What are the alternatives? (Nemawashi)**
   - Alternative 1: Separate commands (cleanup, extract, process)
   - Alternative 2: Single workflow with flags (--cleanup-only, --extract)
   - Alternative 3: Graduated workflow (Phase 1 always, Phase 2-3 optional)

4. **What's simple vs easy?**
   - Easy: Copy Main's workflow (familiar, lots of code)
   - Simple: Fresh build with 3 independent phases (fewer concepts)

5. **What are the failure modes?**
   - File move fails mid-batch → Partial state
   - Knowledge extraction times out → Skip gracefully
   - User cancels mid-workflow → Rollback? Continue? Log?

### PLAN Phase (30% of time)

**Write specification in prose**:

1. **Phase 5.1 Specification** (conversation cleanup)
   - Input: Conversation workspace path
   - Process: Scan → Classify → Propose → Execute
   - Output: Clean workspace + action log
   - Error handling: Continue on individual file failures
   - User interaction: Show preview, Y/n confirmation

2. **Phase 5.2 Specification** (knowledge extraction)
   - Input: Conversation context (title, artifacts, decisions)
   - Process: Detect significance → Extract insights → Format → Save
   - Output: Knowledge/[topic]/[date]_[title].md
   - Error handling: Non-blocking, log failures

3. **Phase 5.3 Specification** (Records pipeline)
   - Input: Records/ directory
   - Process: Classify → Extract → Archive
   - Output: Processed files in Knowledge/Lists/Archive
   - Error handling: Skip unclassifiable files, log

**Define success criteria explicitly** (see above section)

### EXECUTE Phase (10% of time)

Once plan is solid:
- Generate Phase 5.1 script
- Test on Demonstrator workspace
- Generate Phase 5.2 script
- Test knowledge extraction
- Generate Phase 5.3 script
- Test Records flow
- Integration test (full workflow)

### REVIEW Phase (20% of time)

**Testing checklist**:
- [ ] Fresh Zo instance test (can someone else run this?)
- [ ] Production config test (not just dev environment)
- [ ] Error path test (what if file move fails?)
- [ ] Dry-run verification (no actual moves in dry-run)
- [ ] State verification (files actually at destination)
- [ ] Principle compliance (P0-P22 checklist)
- [ ] Documentation complete (README, command docs)

---

## Implementation Strategy

### Recommended Order

1. **Start with Phase 5.1** (Conversation Cleanup)
   - Smallest, most concrete
   - Immediate user value
   - Foundation for other phases

2. **Then Phase 5.2** (Knowledge Extraction)
   - Builds on 5.1 (uses same file scanning)
   - Can reuse classification logic

3. **Finally Phase 5.3** (Records Pipeline)
   - Requires Knowledge structure from 5.2
   - Most complex (time limits, SSOT validation)

### Modular Design

Each phase should be:
- **Runnable standalone** (separate script + command)
- **Testable in isolation** (no dependencies on other phases)
- **Optional** (conversation-end works even if one phase fails)

```
conversation-end
├── n5_cleanup.py (Phase 5.1)
├── n5_extract.py (Phase 5.2)
└── n5_process_records.py (Phase 5.3)
```

User can call individually or all at once via `conversation-end` command.

---

## Files to Reference (Selectively)

**DO load** (learn patterns):
- file 'Knowledge/architectural/planning_prompt.md' (loaded ✅)
- file 'n5os_core_spec.md' section on Phase 5 (loaded ✅)
- file 'n5os-core/N5/commands/conversation-end.md' (for structure)

**DON'T load full scripts** (too much context):
- Main's n5_conversation_end.py (250+ lines, too complex)
- Personal intelligence layer (not relevant)

**Load specific snippets as needed**:
- File classification logic
- Batch move implementation
- Logging patterns

---

## Anti-Patterns to Avoid

**❌ Premature Completion (P15)**
- Don't claim "done" until all files verified at destination

**❌ False API Limits (P16)**
- Don't invent rules like "max 10 files per batch"

**❌ Skip Planning (P22)**
- Don't jump straight to coding
- Think → Plan → Execute framework mandatory

**❌ External Dependencies**
- Don't require Main's lesson extraction
- Don't require AAR generation
- Don't require personal intelligence layer

**❌ Tight Coupling**
- Don't make cleanup depend on knowledge extraction
- Don't make knowledge extraction depend on Records processing

---

## Questions for V Before Starting

1. **Automation confidence**: How much autoconfirm vs user review?
   - Always confirm file moves?
   - Autoconfirm if confidence > 90%?
   - Different thresholds for different file types?

2. **Knowledge structure**: Freeform markdown or structured schema?
   - Flexible (easy to write, hard to query)
   - Structured (upfront work, better searchability)

3. **Records time limits**: 7 days for Temporary/ seems right?
   - Too aggressive?
   - Warnings before deletion?

4. **Phase independence**: Should these be separate commands?
   - Pro: Modular, user control
   - Con: More commands to document

5. **Starting point**: Build all 3 sub-phases or start with 5.1?

---

## Ready to Execute

**Pre-flight checklist**:
- [✅] Planning prompt loaded
- [✅] Phase 5 spec understood
- [✅] Trap doors identified
- [✅] Success criteria defined
- [✅] Think phase complete
- [ ] V's input on questions above
- [ ] Start with Phase 5.1

**When V gives go-ahead**:
1. Confirm answers to questions
2. Write Phase 5.1 specification in prose
3. Review spec with V
4. Execute Phase 5.1 build
5. Test and validate
6. Move to Phase 5.2

---

**Status**: READY FOR V'S INPUT

**Next**: Answer questions above, then launch Phase 5.1

---

*Created: 2025-10-28 05:18 ET*
*Thread: con_E4Qo1a8XsHzOqtGy*
