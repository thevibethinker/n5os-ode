---
date: "2025-10-08T22:41:14Z"
last-tested: "2025-10-16T19:00:00Z"
generated_date: "2025-10-08T22:41:14Z"
checksum: conversation_end_v1_1_0
tags:
  - conversation
  - workflow
category: productivity
priority: medium
related_files:
  - N5/scripts/n5_conversation_end.py
  - N5/scripts/build_tracker.py
anchors:
  - object Object
---
# `conversation-end`

**Version**: 1.1.0\
**Summary**: Formal conversation end-step - review temp files, propose organization, execute cleanup, archive build tracker

---

## Purpose

The **conversation end-step** is a formal phase (like Magic: The Gathering's end step) where all conversation effects are resolved:

- Review files created in conversation workspace
- Propose permanent locations based on file type and context
- Execute batch file moves with user confirmation
- Cleanup conversation workspace
- Log conversation artifacts
- Archive conversation if requested

This is NOT just the conversation ending naturally - it's an **intentional command** that triggers the resolution phase.

---

## When to Use

**Explicit triggers**:

- User says: "End conversation", "Close thread", "Wrap up", "conversation-end"
- User exports conversation (export includes end-step)
- User marks conversation as "closed"

**Implicit triggers** (with confirmation):

- Conversation inactive for 24+ hours
- User starts new conversation on unrelated topic
- System detects natural conversation completion

---

## End-Step Workflow

### Phase -1: Lesson Extraction

**Auto-detect significant conversations and extract reusable lessons**

- Scans conversation for system work, troubleshooting, patterns
- Generates lesson entries for N5/lessons/
- Non-blocking (continues even if extraction times out)

### Phase 0: After-Action Report (AAR)

**Capture conversation context before cleanup**

- Runs `thread-checkpoint` (alias: `thread-export`) with auto-confirm
- Generates AAR JSON + modular markdown files (INDEX, RESUME, DESIGN, etc.)
- Archives to `N5/logs/threads/{date}_{title}_{id}/`
- **Non-destructive** - creates checkpoint before cleanup phases
- Non-blocking (skips if unavailable)

This phase ensures conversation state is preserved before any file moves or cleanup occur.

---

### Phase 0.5: Artifact Symlinking (NEW)

**Link deliverables to AAR artifacts folder**

**Purpose**: Maintain provenance between conversation and deliverables without duplicating files. All significant outputs from a conversation should be accessible from its AAR folder via symlinks.

**What Qualifies as Artifact**:

- **Created deliverables**: Scripts, commands, documents, reports, social posts
- **Modified critical files**: Updated N5 infrastructure, knowledge files
- **Workflow docs**: Debug notes, next-steps documents, design docs
- **NOT artifacts**: Temp files, scratch work, conversation state (already in AAR)

**Process**:

1. **Identify** all deliverables created/modified during conversation
2. **Verify** they're in correct N5 locations (Documents/, Knowledge/, N5/commands/, etc.)
3. **Symlink** to `N5/logs/threads/{date}_{title}_{id}/artifacts/`
4. **Use descriptive names** for symlinks (not just original filename)

**Symlink Naming Conventions**:

```bash
# Original location → Symlink name pattern
Documents/Drafts/X.md → artifact-name.md
Documents/Social/LinkedIn/*.md → social_angle-description.md
N5/commands/*.md → command_name.md
N5/scripts/*.py → script_name.py
Knowledge/**/*.md → category_name.md
N5/digests/*.md → digest_name.md
```

**Example**:

```bash
cd /home/workspace/N5/logs/threads/2025-10-21-1210_✅-System-Work_kkgp/artifacts/

# Demo materials
ln -sf /home/workspace/Documents/Drafts/zo_demo_script.md ./demo_script.md
ln -sf /home/workspace/N5/digests/COMPARISON-baseline-vs-enhanced.md ./comparison_materials.md

# Social content (multiple angles)
ln -sf /home/workspace/Documents/Social/LinkedIn/2025-10-20_zo-gtm_ANGLE1-founder-pain.md ./social_angle1_founder-pain.md
ln -sf /home/workspace/Documents/Social/LinkedIn/2025-10-20_zo-gtm_ANGLE2-technical.md ./social_angle2_technical.md

# Infrastructure
ln -sf /home/workspace/Knowledge/personal-brand/bio.md ./bio.md
ln -sf /home/workspace/N5/commands/social-post-generate-multi-angle.md ./command_social-multi-angle.md
ln -sf /home/workspace/N5/scripts/modules/knowledge_scanner.py ./script_knowledge_scanner.py
```

**Verification**:

```bash
# Check all artifacts are symlinked
ls -lah artifacts/
# Should show: symlinks pointing to actual file locations, not copies

# Verify originals are in correct N5 structure
# Documents/Drafts/, Documents/Social/, Knowledge/, N5/commands/, N5/scripts/, etc.
```

**Benefits**:

- ✅ Single source of truth (no file duplication)
- ✅ AAR folder provides complete provenance
- ✅ Files stay in correct N5 locations
- ✅ Easy to see all outputs from a conversation
- ✅ Symlinks survive file moves (absolute paths)

**Enforcement**: P5 (Anti-Overwrite) - never copy files to AAR, always symlink.

---

## Command Relationship (clarification)

- conversation-end is the orchestrator for formal thread closure. 
  - It invokes Phase -1 (lessons extraction via `file N5/scripts/n5_lessons_extract.py`).
  - It invokes Phase 0 (AAR generation via `thread-export`, i.e., `file N5/scripts/n5_thread_export.py`).
- thread-export can be run standalone for mid-thread checkpoints or quick AARs without the full end-step.
- If you are closing a thread, prefer running conversation-end; it will call thread-export for you.
- If you only need an AAR snapshot during an ongoing thread, run thread-export directly.

---

### Phase 1: File Organization

**Inventory & classify conversation files**

1. **Scan** conversation workspace for all files
2. **Classify** by type and content: 
   - Images → Images/
   - Transcripts → Document Inbox/Company/meetings/
   - Reports → Documents/
   - Scripts → Keep or delete based on name
   - Data exports → Exports/
   - Documents → Document Inbox/Temporary/
3. **Propose** moves/deletions with rationale
4. **Confirm** with user (Y/n)
5. **Execute** batch file operations
6. **Log** all actions to N5/runtime/conversation_ends.log

### Phase 2: Workspace Root Cleanup

**Remove conversation artifacts from workspace root**

- Runs `n5_workspace_root_cleanup.py --execute`
- Removes temporary files, logs, caches
- Preserves intentional files (marked or documented)

### Phase 2.5: Placeholder & Stub Detection

**Enforce P16 (Accuracy) and P21 (Document Assumptions)**

- Runs `file n5_placeholder_scan.py`
- Detects TODO, FIXME, placeholder comments
- Flags incomplete implementations
- **Requires resolution** before continuing (or acknowledgement)
- User options: Fix now, Document as intentional, Acknowledge & log

### Phase 3: Personal Intelligence Update

**Update personal intelligence layer (autonomous)**

- Runs `file update_personal_intelligence.py`
- Processes conversation artifacts
- Updates knowledge graph/embeddings
- Non-blocking (continues on error)

### Phase 3.5: Build Tracker Archival **\[NEW\]**

**Archive completed tasks from build tracker**

- **Detects** BUILD_MAP.md in conversation workspace
- **Checks** if build session is already closed
- **Generates archive** of completed tasks to `file N5/logs/build-sessions/archive/{convo_id}_completed.jsonl`
- **Closes session** by logging `session_closed` event
- **Refreshes BUILD_MAP** to hide completed tasks (only shows active/open)
- **Non-destructive**: Full session log preserved for audit trail
- **Result**: Tracker stays focused, completed work archived

**Archive Format:**

```jsonl
{"type": "session_archive", "convo_id": "con_XXX", "archived_at": "2025-10-16T19:00:00Z", "task_count": 3}
{"type": "task_completed", "task": "Feature Implementation", "added_at": "...", "completed_at": "...", "state": "complete"}
```

**Impact:**

- Completed tasks no longer appear in BUILD_MAP after conversation-end
- Tracker can hold more than 5 items without getting cluttered
- Historical record maintained in session log + archive
- Future conversations see clean, focused task list

### Phase 4: Git Status Check

**Ensure work is saved**

- Runs `git status --short`
- If changes detected: 
  - Shows uncommitted files
  - Runs `git-check` audit for staged changes
  - Prompts user to commit (Y/n)
  - Executes `git add -A` and `git commit` if confirmed
- Logs commit to conversation_ends.log
- Skipped in --auto mode

### Phase 5: Thread Title Generation

**Auto-generate descriptive thread title**

- Analyzes conversation content
- Generates concise, descriptive title
- Updates thread metadata
- Future feature (placeholder)

### Phase 6: Optional Archive

**Archive conversation for long-term storage**

- Compress conversation workspace
- Move to N5/archive/{date}/
- Only if requested or conversation is significant
- Future feature (placeholder)

---

### Phase 1: Inventory

```bash
# List all files created during conversation
find /home/.z/workspaces/con_[ID]/ -type f -newer [CONVERSATION_START]

# Categorize by type and directory
- scripts/
- data/
- images/
- documents/
- exports/
- temp/
```

### Phase 2: Classification

For each file, determine:

- **File type**: Extension, content analysis
- **Purpose**: What was it created for? (from conversation context)
- **Value**: Permanent vs temporary
- **Destination**: Where should it live permanently?

Classification matrix:

| Pattern | Type | Destination | Action |
| --- | --- | --- | --- |
| \*.png, \*.jpg | Generated image | Images/ | Move with date prefix |
| *.png (temp\_*, chart\_\*) | Temp visualization | \- | Delete |
| *meeting*.md, *transcript*.md | Meeting record | Records/Company/meetings/ | Move with date |
| *analysis*.md, *report*.md | Analysis/report | Documents/ | Move with date |
| \*.py (user-requested) | Permanent script | Code/ | Move |
| \*.py (temporary) | Temp automation | \- | Delete |
| \*.csv, \*.json (export) | Data export | Exports/ | Move |
| \*.csv, \*.json (intermediate) | Processing temp | \- | Delete |
| *article*.md, saved_page.md | Saved article | Articles/ | Move |
| \*.md (draft) | Temporary note | \- | Delete or ask |

**Propose Moves**:

```markdown
## Conversation End-Step: File Resolution

### Files Created: [N] total

#### Images ([X] files)
✓ concept_design.png → Images/concept_design_20251008.png
✓ wireframe.png → Images/wireframe_20251008.png
✗ temp_chart.png → DELETE (temporary visualization)

#### Documents ([Y] files)
✓ meeting_notes.md → Records/Company/meetings/2025-10-08-board-meeting.md
✓ analysis_report.md → Documents/Market_Analysis_20251008.md
? draft_ideas.md → AMBIGUOUS - Keep or delete?

#### Scripts ([Z] files)
✗ data_processor.py → DELETE (one-time script)

### Summary
- Move: [N] files
- Delete: [M] files
- Ambiguous: [K] files (require decision)

**Proceed with moves? (Y/n)**
If ambiguous files exist, resolve those first.
```

**Execute File Organization**:

```bash
# Move permanent files
for file in permanent_files:
    mv [conversation_workspace]/[file] [destination]
    echo "Moved [file] → [destination]" >> N5/runtime/file_moves.log

# Delete temporary files
for file in temp_files:
    rm [conversation_workspace]/[file]
    echo "Deleted [file] (temporary)" >> N5/runtime/file_moves.log

# Log conversation artifacts
echo "Conversation [ID] closed: [N] files moved, [M] deleted" >> N5/runtime/conversations.log
```

**Workspace Root Cleanup**:

```bash
# Clean up conversation artifacts from workspace root
n5_workspace_root_cleanup.py --execute
```

### Phase 2.5: Placeholder & Stub Detection (NEW)

**Script:** `file N5/scripts/n5_placeholder_scan.py`

**Purpose:** Scan conversation workspace for incomplete code before it leaves conversation context

**Enforces:** P16 (Accuracy), P21 (Document Assumptions)

**Detection patterns:**

- Comment placeholders (TODO, FIXME without explanation)
- Fake data ([test@example.com](mailto:test@example.com), 555-1234)
- Function stubs without docstrings
- Invented constraints ("API limit of 5 messages" without citation)
- Hardcoded paths (/Users/john/)
- Empty exception handlers (P19 violation)

**Exit codes:**

- 0 = Clean, continue workflow
- 1 = Issues found, BLOCK conversation-end
- 2 = Scan error, continue with warning

**User options when issues found:**

1. **Fix now** - Return to conversation, abort conversation-end
2. **Document as intentional** - Add `# DOCUMENTED:` prefix
3. **Acknowledge & continue** - Log issues for later follow-up

**Blocking behavior:**

- User MUST choose option before conversation-end can proceed
- Prevents incomplete work from leaving conversation context
- Maintains quality standards at critical transition point

**Auto mode:** If `--auto` flag present, issues are logged but don't block

See: `file N5/commands/placeholder-scan.md` for full details

---

### Phase 3: Personal Intelligence Update (Autonomous)

**Purpose**: Update the personal intelligence layer (`file N5/intelligence/personal-understanding.json`) with observations from this conversation. Track V's intellectual, behavioral, emotional, and cognitive patterns.

**What to Track:**

- **Intellectual patterns**: Problem-solving approaches, learning style, knowledge gaps revealed, technical/non-technical boundary pushing
- **Behavioral patterns**: Decision-making in action, speed vs. perfection tradeoffs, system-building vs. execution ratio
- **Emotional patterns**: Energy levels, frustration triggers, excitement indicators, late-night work patterns
- **Cognitive patterns**: How V processes information, asks questions, handles ambiguity, responds to feedback
- **Hypothesis tracking**: Evidence that confirms or disconfirms active hypotheses about V's patterns

**Analysis Framework:**

1. **Conversation Context**

   - What was V working on?
   - What was the nature of the work? (strategic, tactical, system-building, execution)
   - Time of day and duration
   - V's energy and engagement level

2. **Decision Points**

   - What choices did V make?
   - Speed vs. perfection: Did V ship quickly or build infrastructure first?
   - Technical approach: Did V push technical boundaries or stay comfortable?
   - Feedback response: How did V respond to suggestions or pushback?

3. **Pattern Signals**

   - **Confirming evidence**: Behaviors that match existing hypotheses
   - **Disconfirming evidence**: Behaviors that contradict hypotheses
   - **Novel observations**: New patterns not yet tracked

4. **Hypothesis Updates**

   - Review active hypotheses in `hypothesis_tracking.active_hypotheses`
   - Add evidence_for or evidence_against based on conversation
   - Update confidence levels
   - Move to confirmed_patterns or disconfirmed_patterns if threshold reached

**Execution:**

```bash
# Run personal intelligence update script
python3 /home/workspace/N5/scripts/update_personal_intelligence.py \
  --conversation-id $CONVERSATION_ID \
  --auto

# Script should:
# 1. Analyze conversation workspace for artifacts
# 2. Review conversation context (if available)
# 3. Extract behavioral/intellectual/emotional signals
# 4. Update hypothesis tracking with new evidence
# 5. Append new observation to observations_log
# 6. Update meta.last_updated timestamp
```

**Output Example:**

```markdown
======================================================================
PHASE 3: PERSONAL INTELLIGENCE UPDATE
======================================================================

Analyzing conversation patterns...

📊 Observations from this conversation:
- V initiated intelligence layer population at 3 AM (energy pattern)
- Requested honest feedback with no glazing (openness to criticism)
- Remembered forgotten system existed, persisted until found (persistence)
- Explicitly requested dynamic hypothesis tracking (systems thinking)

🔬 Hypothesis Updates:
H004: V's growth responsiveness → CONFIRMING EVIDENCE
  - Requested to track behavioral changes
  - "hopefully you'll start seeing behavior that evidences I'm making better decisions"
  - Confidence: medium → high

✅ Personal intelligence updated
   New observations: 2
   Hypothesis updates: 1
   Total conversations analyzed: 13
```

**Privacy Note**: This update is autonomous and private. V can request to see the intelligence layer anytime but it's not shown by default.

---

### Phase 3.5: Build Tracker Archival **\[NEW\]**

**Archive completed tasks from build tracker**

- **Detects** BUILD_MAP.md in conversation workspace
- **Checks** if build session is already closed
- **Generates archive** of completed tasks to `file N5/logs/build-sessions/archive/{convo_id}_completed.jsonl`
- **Closes session** by logging `session_closed` event
- **Refreshes BUILD_MAP** to hide completed tasks (only shows active/open)
- **Non-destructive**: Full session log preserved for audit trail
- **Result**: Tracker stays focused, completed work archived

**Archive Format:**

```jsonl
{"type": "session_archive", "convo_id": "con_XXX", "archived_at": "2025-10-16T19:00:00Z", "task_count": 3}
{"type": "task_completed", "task": "Feature Implementation", "added_at": "...", "completed_at": "...", "state": "complete"}
```

**Impact:**

- Completed tasks no longer appear in BUILD_MAP after conversation-end
- Tracker can hold more than 5 items without getting cluttered
- Historical record maintained in session log + archive
- Future conversations see clean, focused task list

---

### Phase 4: Git Status Check (Interactive)

**Purpose**: Ensure all work is committed to git before closing the conversation - prevents losing progress between threads.

**Workflow**:

1. Check git status for uncommitted changes
2. If changes detected: 
   - Display `git status --short` output
   - Run `git-check` audit to check for overwrites/data loss
   - Prompt user: "Commit changes before ending conversation? (Y/n)"
3. If user confirms: 
   - Prompt for commit message (default: "conversation-end: save progress")
   - Stage all changes with `git add -A`
   - Commit with provided message
   - Display commit summary
4. If no changes: Report clean status and continue

**Rationale**:

- Adds intentional friction to prevent losing uncommitted work
- Works with assumption that lessons/context carry over via thread-export
- Every conversation-end becomes a checkpoint for git state
- User explicitly confirms commit, no auto-commit surprises

**Example output**:

```markdown
======================================================================
PHASE 4: GIT STATUS CHECK
======================================================================

Checking for uncommitted changes...

📝 Uncommitted changes detected:

 M N5/scripts/n5_conversation_end.py
 M N5/commands/conversation-end.md
?? N5/temp_notes.md

----------------------------------------------------------------------
Running git-check audit...

✅ No obvious overwrites or major losses detected in staged changes.
----------------------------------------------------------------------

⚠️  You have uncommitted changes.
Commit changes before ending conversation? (Y/n): y

Enter commit message (or press Enter for default):
> Add git check to conversation-end workflow

Staging all changes...
✓ Changes staged
Committing with message: 'Add git check to conversation-end workflow'...
✅ Changes committed successfully

[main abc1234] Add git check to conversation-end workflow
 2 files changed, 95 insertions(+), 5 deletions(-)
```

**Decision point:** Commit changes now or defer?

### Phase 5: Thread Title Generation (NEW)

After git check, automatically generate thread titles:

**Instructions:**

1. Load `file N5/prefs/operations/thread-titling.md` for format rules
2. Load `file N5/config/emoji-legend.json` for emoji selection
3. **Analyze conversation deeply:**
   - Review ALL deliverables/artifacts created
   - Extract 2-3 concrete nouns that describe what was built
   - Identify the primary system/feature/component worked on
   - Be SPECIFIC: "Content Library System" not "System Work"
   - Include key integrations if relevant: "X + Y Integration"
4. Generate TWO titles: 
   - **Current thread title**: For this conversation
   - **Next thread title**: For continuation (increment #N or add #2 if current has #1 or no number)
   - Use 🔗 chain emoji for linked threads
5. Display both titles prominently

**Title Format (REQUIRED):**

```markdown
MMM DD | {emoji} {Specific-Entity} {Action/Type} {optional: #N}
```

**Entity Guidelines:**

- **Specific system names:** "Content Library", "Email Validator", "CRM Sync Engine"
- **Not generic terms:** Avoid "System", "Tool", "Feature" alone
- **Combined systems:** Use "X + Y" for dual implementations
- **Include key components:** "Meeting Parser", "B-Block Extractor"

**Good Examples:**

```markdown
Oct 22 | ✅ Content Library + Email Validation Systems
Oct 16 | 🔧 Meeting Intelligence Multi-Block Generator  
Oct 14 | 🔗 CRM Consolidation Phase 2
Oct 13 | 📰 GTM Strategy Docs & Market Research
```

**Bad Examples (Too Generic):**

```markdown
Oct 22 | ✅ System Work              ← What system?
Oct 16 | ✅ Implementation           ← What implementation?
Oct 14 | 🔧 Refactor                ← Refactor of what?
```

**Display Format:**

```markdown
======================================================================
📋 THREAD TITLES GENERATED
======================================================================

Current Thread:
  Oct 22 | ✅ Content Library + Email Validation Systems

Next Thread (for continuation):
  Oct 22 | 🔗 Content Library Enhancement #2

💡 Use these when naming threads in the Zo interface.
======================================================================
```

**Rules:**

- Always include date prefix ("MMM DD | ")
- Use centralized emoji legend
- Follow noun-first principle with SPECIFIC nouns
- Extract key deliverable names from artifacts
- Respect UI constraints (collapsed sidebar \~24 chars visible)
- Include sequence numbers for linked work
- Prioritize clarity over brevity (within constraints)

---

### Phase 4.5: System Timeline Check (NEW)

**Purpose**: Automatically detect and capture timeline-worthy system changes during conversation-end.

**Workflow**:

1. Scan workspace for high-signal file changes
2. Detect new commands, modified scripts, critical infrastructure changes
3. Generate suggested timeline entry if significant work detected
4. Prompt user to review and optionally add to system timeline

**Detection Signals**:

- New command files in N5/commands/ (created in last hour)
- Multiple modified scripts in N5/scripts/ (≥2 files)
- Recent changes to critical infrastructure files

**User Options**:

- Y - Add to timeline as-is
- e - Edit entry before adding
- n - Skip timeline update

**Example output**:

```markdown
======================================================================
PHASE 4.5: SYSTEM TIMELINE CHECK
======================================================================

Scanning for timeline-worthy changes...

📊 SYSTEM TIMELINE UPDATE DETECTED

Source: conversation-end

Suggested timeline entry:
  Title:       New command(s): timeline-automation
  Category:    command
  Impact:      medium
  Status:      completed
  Description: Created 1 new command(s): timeline-automation
  Components:  1 affected
    - N5/commands/timeline-automation.md

----------------------------------------------------------------------
Options:
  Y - Add to timeline as-is
  e - Edit before adding
  n - Skip (don't add to timeline)
----------------------------------------------------------------------

Add to system timeline? (Y/e/n): Y

✅ System timeline updated: New command(s): timeline-automation
   Entry ID: 46f2c4c2-eae1-4ff7-8871-3aeba65def70
```

**Rationale**:

- Lightweight check that catches high-impact changes
- Runs during natural workflow pause (conversation end)
- Complements thread-export's deeper AAR-based detection
- User always has final say

---

### Phase 5: Archive (Optional)

```bash
# If user requested conversation export/archive
conversation_summary.md → Documents/Conversations/2025-10-08-[topic].md
conversation_metadata.json → N5/runtime/conversations/con_[ID].json

# Include:
- Conversation topic/summary
- Files created and their destinations
- Key decisions made
- Commands executed
- Duration, message count
```

### Phase 6: Cleanup (Optional)

```bash
# Remove conversation workspace (optional - done manually or via system cleanup)
rm -rf /home/.z/workspaces/con_[ID]/

# Verify cleanup
test -d /home/.z/workspaces/con_[ID]/ || echo "✓ Workspace cleaned"
```

## Version History

### 1.1.0 (2025-10-16)

- **Added Phase 3.5:** Build Tracker Archival
- Integration with build_tracker.py for task cleanup
- Completed tasks archived, BUILD_MAP updated
- Non-destructive archival with full audit trail
- Addresses V's requirement: "tracker won't get full as long as it drops items once end-command has been fully run"

### 1.0.0 (2025-10-08)

- Initial implementation
- 6-phase workflow
- File organization, workspace cleanup
- Placeholder detection, git checks
- AAR generation, lesson extraction

## Phases

1. **Phase -1**: Lesson extraction (reflection-worker if available)
2. **Phase 0**: AAR Generation (n5_thread_export.py)
3. **Phase 0.5**: Thread Title Generation & Registry Update
4. **Phase 1-2**: (Interactive file organization - currently streamlined)
5. **Phase 2.75**: Output Review Check (review_manager integration)
6. **Phase 3**: Build Task Check (build-companion integration)
7. **Phase 4**: Git Status Check (uncommitted changes alert)
8. **Phase 4.5**: Timeline Update Check (auto-add significant events)
9. **Phase 5**: Registry Closure (mark conversation complete)
10. **Phase 6**: Archive Promotion (auto-copy to Documents/Archive if tagged)

## Archive System

**Two-tier architecture** (as of 2025-10-26):

1. **N5/logs/threads/** - Complete archive (SSOT), all conversations, permanent
2. **Documents/Archive/** - Curated portfolio (~20%), auto-promoted by tags

**Promotion triggers**: `#worker`, `#deliverable`, `#shipped` tags

See: `file 'N5/docs/archive-promotion-system.md'` for details