---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
type: build_plan
status: ready
provenance: con_thiVbfdLjmmBE7ol
---

# Plan: Spawn Worker LLM-First Refactor

**Objective:** Refactor spawn_worker.py to be pure plumbing (IDs, file I/O, linkage) while the LLM handles all semantic work (context reading, scoping, assignment writing).

**Trigger:** Worker assignment `WORKER_ASSIGNMENT_..._ZGQv` was useless because the script generated garbage content from template fallback, while the LLM-authored `WORKER_RESEARCH_ASSIGNMENT.md` was excellent.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

**Core Insight:** Spawning workers is a *deliberate decomposition act*. The LLM:
1. Reads immediate context (what was asked)
2. Reads SESSION_STATE (larger context)
3. Consciously scopes and divvies work
4. Writes complete worker assignment(s)
5. Script saves the file(s)

---

## Open Questions

<!-- All resolved -->
- [x] Should we keep `--context` JSON mode? → **No.** Replace with `--content-file` that takes raw markdown.
- [x] Should SESSION_STATE parsing remain? → **No.** Remove all parsing. LLM reads SESSION_STATE directly if needed.
- [x] Where should worker assignments live? → Keep `Records/Temporary/` for now (existing convention).

---

## Checklist

### Phase 1: Strip spawn_worker.py to Pure Plumbing
- ☑ Delete `create_worker_assignment()` function
- ☑ Delete `parse_session_state()` function
- ☑ Delete all `_extract_*` and `_clean_*` helper functions
- ☑ Delete `gather_recent_artifacts()` function
- ☑ Add `--content-file` parameter (required unless `--generate-ids`)
- ☑ Remove `--context` and `--instruction` parameters
- ☑ Update `main()` to fail loudly if no content provided
- ☑ Test: `--generate-ids` still works
- ☑ Test: `--content-file` saves content correctly
- ☑ Test: Missing `--content-file` fails with clear error
- ☑ Test: Short content fails

### Phase 2: Rewrite Spawn Worker Prompt
- ☑ Rewrite prompt to enforce deliberate decomposition workflow
- ☑ Add structural template (not content template) for worker assignments
- ☑ Add examples of good vs bad assignments
- ☑ Test: Prompt reads naturally and is actionable

### Phase 3: Integration Verification
- ☑ Test end-to-end: LLM writes assignment → script saves → file opens correctly
- ☑ Verify parent SESSION_STATE linkage still works
- ☑ Update STATUS.md with completion

---

## Phase 1: Strip spawn_worker.py to Pure Plumbing

### Affected Files
- `N5/scripts/spawn_worker.py` - UPDATE - Remove all semantic logic, keep only mechanics

### Changes

**1.1 Delete semantic functions:**

Remove these functions entirely (lines ~60-165 in current file):
- `_clean_value()`
- `_is_placeholder()`
- `_extract_field_multi()`
- `_extract_progress()`
- `parse_session_state()`
- `gather_recent_artifacts()`
- `create_worker_assignment()`

**1.2 Update argument parser:**

Replace the current arguments with:

```python
parser.add_argument("--parent", required=True, help="Parent conversation ID")
parser.add_argument("--content-file", help="Path to markdown file with worker assignment content")
parser.add_argument("--generate-ids", action="store_true", help="Only generate IDs, don't create files")
parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
```

Remove these arguments:
- `--context`
- `--context-file` 
- `--instruction`

**1.3 Rewrite main() logic:**

The new main() should be:

```python
def main():
    parser = argparse.ArgumentParser(
        description="Save LLM-written worker assignment and link to parent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
IMPORTANT: The LLM writes the worker assignment content.
This script only handles:
  1. Generate unique IDs
  2. Save the markdown file
  3. Update parent SESSION_STATE with worker reference

Example workflow:
  1. LLM reads context and writes assignment to temp file
  2. LLM calls: python3 spawn_worker.py --parent con_XXX --content-file /path/to/assignment.md
  3. Script saves to Records/Temporary/ and links to parent

ID-only mode (for LLM to write file manually):
  python3 spawn_worker.py --parent con_XXX --generate-ids
"""
    )
    parser.add_argument("--parent", required=True, help="Parent conversation ID")
    parser.add_argument("--content-file", help="Path to markdown file with worker assignment content")
    parser.add_argument("--generate-ids", action="store_true", help="Only generate IDs, output JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    
    args = parser.parse_args()
    
    # Handle --generate-ids mode
    if args.generate_ids:
        ids = generate_ids(args.parent)
        ids["parent_workspace"] = str(Path(f"/home/.z/workspaces/{args.parent}"))
        ids["worker_updates_dir"] = str(Path(f"/home/.z/workspaces/{args.parent}/worker_updates"))
        ids["parent_id"] = args.parent
        print(json.dumps(ids, indent=2))
        return 0
    
    # Require --content-file for actual spawning
    if not args.content_file:
        logging.error("--content-file is required (unless using --generate-ids)")
        logging.error("")
        logging.error("The LLM must write the worker assignment content.")
        logging.error("This script only saves the file and links to parent.")
        logging.error("")
        logging.error("Workflow:")
        logging.error("  1. LLM reads context (SESSION_STATE, immediate request)")
        logging.error("  2. LLM writes complete worker assignment to a temp file")
        logging.error("  3. LLM calls: python3 spawn_worker.py --parent con_XXX --content-file /path/to/file.md")
        return 1
    
    # Read content
    content_path = Path(args.content_file)
    if not content_path.exists():
        logging.error(f"Content file not found: {content_path}")
        return 1
    
    content = content_path.read_text()
    if len(content.strip()) < 50:
        logging.error(f"Content file seems too short ({len(content)} chars). Worker assignments need substance.")
        return 1
    
    # Generate IDs
    ids = generate_ids(args.parent)
    
    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Would save to: {ids['output_path']}")
        print(f"Content length: {len(content)} chars")
        print(f"First 500 chars:\n{content[:500]}")
        return 0
    
    # Write file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(ids['output_path'])
    output_path.write_text(content)
    logging.info(f"✓ Worker assignment saved: {output_path}")
    
    # Update parent SESSION_STATE
    update_parent_session_state(args.parent, ids['filename'], ids['timestamp'])
    
    # Create worker_updates directory
    worker_updates_path = create_worker_updates_dir(args.parent)
    
    # Output for LLM
    result = {
        "success": True,
        "worker_id": ids['worker_id'],
        "output_path": str(output_path),
        "relative_path": f"Records/Temporary/{ids['filename']}",
        "worker_updates_dir": str(worker_updates_path),
    }
    print(json.dumps(result, indent=2))
    
    logging.info(f"\n✓ Worker saved!")
    logging.info(f"📄 Open this file in a new conversation: {output_path}")
    
    return 0
```

**1.4 Keep these functions unchanged:**
- `generate_ids()` - Pure ID generation
- `update_parent_session_state()` - Parent linkage
- `create_worker_updates_dir()` - Directory creation

**1.5 Update module docstring:**

Replace the current docstring with:

```python
"""
Spawn Worker v3.0 - Pure Plumbing

The LLM writes all worker assignment content.
This script handles ONLY:
1. Generate unique worker ID and timestamp
2. Save the LLM-written markdown file
3. Update parent SESSION_STATE with worker reference
4. Create worker_updates/ directory for communication

Usage:
    # LLM writes assignment, script saves it
    python3 spawn_worker.py --parent con_XXX --content-file /path/to/assignment.md
    
    # Generate IDs only (LLM will save file manually)
    python3 spawn_worker.py --parent con_XXX --generate-ids

IMPORTANT: This script does NOT generate content. The LLM must:
1. Read context (SESSION_STATE, immediate request)
2. Deliberately scope the work
3. Write a complete worker assignment
4. Call this script to save it
"""
```

**1.6 Update VERSION constant:**

```python
VERSION = "3.0"
```

### Unit Tests

After completing Phase 1, run these tests:

**Test 1: --generate-ids works**
```bash
python3 N5/scripts/spawn_worker.py --parent con_TEST123 --generate-ids
```
Expected: JSON output with worker_id, timestamp, filename, output_path, parent_workspace, worker_updates_dir, parent_id

**Test 2: --content-file saves correctly**
```bash
# Create test content
echo "# Test Worker Assignment

This is a test worker assignment with sufficient content to pass the length check.
The worker should do X, Y, and Z.

## Deliverables
- Item 1
- Item 2
" > /tmp/test_worker.md

# Save it
python3 N5/scripts/spawn_worker.py --parent con_TEST123 --content-file /tmp/test_worker.md --dry-run
```
Expected: Dry run output showing where file would be saved, content length, preview

**Test 3: Missing --content-file fails clearly**
```bash
python3 N5/scripts/spawn_worker.py --parent con_TEST123 2>&1
```
Expected: Clear error message explaining that LLM must write content, workflow explanation, exit code 1

**Test 4: Short content fails**
```bash
echo "Too short" > /tmp/short.md
python3 N5/scripts/spawn_worker.py --parent con_TEST123 --content-file /tmp/short.md 2>&1
```
Expected: Error about content being too short

**✅ Phase 1 complete: spawn_worker.py refactored to pure plumbing. All 4 tests passing.**

---

## Phase 2: Rewrite Spawn Worker Prompt

### Affected Files
- `Prompts/Spawn Worker.prompt.md` - UPDATE - Complete rewrite for LLM-first workflow

### Changes

**2.1 Replace entire prompt content with:**

```markdown
---
created: 2025-10-15
last_edited: 2025-12-26
version: 3.0
description: |
  Spawn parallel worker threads through deliberate decomposition.
  
  YOU (the LLM) write the complete worker assignment.
  The script ONLY saves the file and links to parent.
  
  This is a CONSCIOUS process:
  1. Read context (SESSION_STATE + immediate request)
  2. Scope the work deliberately
  3. Write complete worker assignment(s)
  4. Call script to save
tool: true
tags:
  - workers
  - parallel
  - orchestration
  - decomposition
---

# Spawn Worker Thread

## Philosophy

Spawning a worker is a **deliberate decomposition act**, not a mechanical handoff.

You already have:
- **Immediate context:** What was just asked
- **SESSION_STATE:** The larger context of what's being built

Your job is to:
1. **Read and understand** both contexts
2. **Scope the work** - What exactly should this worker do?
3. **Write a complete assignment** - Everything the worker needs
4. **Save via script** - Pure plumbing

## The Workflow

### Step 1: Gather Context

Read the parent's SESSION_STATE:
```bash
cat /home/.z/workspaces/con_XXXXX/SESSION_STATE.md
```

Combine with the immediate request from the conversation.

### Step 2: Scope the Work

Ask yourself:
- What is the discrete unit of work?
- What does the worker need to know?
- What are the deliverables?
- What are the success criteria?

### Step 3: Write the Assignment

Write a complete worker assignment file. Use this structure:

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: con_PARENT_ID
---

# WORKER ASSIGNMENT: [Descriptive Title]

**Assigned to:** Zo ([Mode: Builder/Researcher/Writer/etc.])
**Objective:** [One clear sentence describing the mission]

## Context from Parent

[Brief summary of parent context - what larger thing is being built, key decisions already made, relevant constraints]

## Your Mission

[Detailed description of what this worker should accomplish]

## Information Containers / Deliverables

[Specific, structured outputs the worker should produce]

### 1. [Deliverable Name]
- [Specific items to include]

### 2. [Deliverable Name]
- [Specific items to include]

## Success Criteria

1. [Measurable criterion]
2. [Measurable criterion]
3. [Measurable criterion]

## Reference Files

- `file 'path/to/relevant/file'`
- `file 'path/to/another/file'`

---

**INSTRUCTION FOR SUB-AGENT:**
[Direct, actionable instruction for the worker. Be specific about tools to use, approach to take, and how to report completion.]
```

### Step 4: Save via Script

Write your assignment to a temp file, then call the script:

```bash
# Write assignment to conversation workspace
cat > /home/.z/workspaces/con_XXXXX/worker_assignment_draft.md << 'EOF'
[Your complete assignment content]
EOF

# Save and link to parent
python3 N5/scripts/spawn_worker.py \
    --parent con_XXXXX \
    --content-file /home/.z/workspaces/con_XXXXX/worker_assignment_draft.md
```

### Step 5: Report

Tell the user:
- What worker was spawned
- Where the assignment file is
- How to start the worker (open file in new conversation)

## Good vs Bad Assignments

### ❌ BAD: Template Garbage
```markdown
# Worker Assignment - Parallel Thread

**Parent Focus:** _Not specified_
**Parent Objective:** TBD

## Your Mission
No specific instruction provided
```
This is useless. The worker has no idea what to do.

### ✅ GOOD: Deliberate Assignment
```markdown
# WORKER ASSIGNMENT: Zorg Research Phase

**Assigned to:** Zo (Researcher Mode)
**Objective:** Research best practices for puzzle-based adventures.

## Context from Parent
Building "Zorg" - an ARG/puzzle game for N5 onboarding. Core elements locked in CORE_ELEMENTS_LOCKDOWN.md. Need research on game design patterns before implementation.

## Your Mission
Research DEF CON CTF and ARG design patterns. Focus on puzzle taxonomy, player flow, and scaffolding.

## Deliverables
### 1. Puzzle Taxonomy
- Ciphers, file mechanics, logic puzzles, social engineering

### 2. Flow & Scaffolding
- The "Aha!" moment, failure handling, skip paths

## Success Criteria
1. Create RESEARCH_DOSSIER.yaml with findings
2. Provide reflection on what's missing from current plan
3. 3-paragraph executive summary

## Reference Files
- `file 'N5/builds/vibe-arg/CORE_ELEMENTS_LOCKDOWN.md'`
- `file 'N5/builds/vibe-arg/PLAN.md'`

---
**INSTRUCTION FOR SUB-AGENT:**
Use web_research and web_search. Focus on "Game Design for CTFs" and "ARG narrative scaffolding." Write the dossier, then respond with reflection.
```

This tells the worker exactly what to do, why, and how to succeed.

## ID-Only Mode

If you want to generate IDs first and write the file yourself:

```bash
python3 N5/scripts/spawn_worker.py --parent con_XXXXX --generate-ids
```

Returns:
```json
{
  "worker_id": "WORKER_XXXXX_20251226_143000",
  "timestamp": "2025-12-26T14:30:00.000000+00:00",
  "filename": "WORKER_ASSIGNMENT_20251226_143000_000000_XXXXX.md",
  "output_path": "/home/workspace/Records/Temporary/WORKER_ASSIGNMENT_...",
  "parent_workspace": "/home/.z/workspaces/con_XXXXX",
  "worker_updates_dir": "/home/.z/workspaces/con_XXXXX/worker_updates"
}
```

Then write your assignment directly to `output_path`.

## Worker Communication

Workers write status to `{parent_workspace}/worker_updates/`:

| File | Purpose |
|------|---------|
| `WORKER_XXX_status.md` | Progress updates |
| `WORKER_XXX_completion.md` | Final summary |
| `WORKER_XXX_artifacts/` | Generated files |

## Version History

- **v3.0** (2025-12-26): LLM-first rewrite. Script is pure plumbing. LLM writes all content.
- **v2.1** (2025-12-10): Added --context JSON (deprecated)
- **v1.0**: Initial implementation
```

### Unit Tests

**Test: Prompt is readable and actionable**
- Read `Prompts/Spawn Worker.prompt.md`
- Verify structure section exists
- Verify good/bad examples exist
- Verify workflow steps are clear

---

## Phase 3: Integration Verification

### Affected Files
- `N5/builds/spawn-worker-refactor/STATUS.md` - UPDATE - Mark complete

### Changes

**3.1 End-to-end test:**

In a test conversation:
1. LLM reads this plan
2. LLM writes a test worker assignment
3. LLM calls `spawn_worker.py --content-file ...`
4. Verify file saved to `Records/Temporary/`
5. Verify parent SESSION_STATE updated
6. Verify file can be opened in new conversation

**3.2 Update STATUS.md:**

Mark build complete with timestamp.

### Unit Tests

- Verify `Records/Temporary/WORKER_ASSIGNMENT_*.md` exists after spawn
- Verify parent SESSION_STATE has "## Spawned Workers" section
- Verify worker_updates/ directory created

---

## Success Criteria

1. **spawn_worker.py** no longer generates any content - only saves LLM-written files
2. **spawn_worker.py** fails loudly with clear error if no `--content-file` provided
3. **Spawn Worker.prompt.md** enforces deliberate decomposition workflow
4. **End-to-end test** passes: LLM writes assignment → script saves → file works

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing workflows that use `--context` | Clear error message explains new workflow |
| LLM forgets to write complete assignment | Prompt has good/bad examples, structure template |
| Content too short check too aggressive | 50 char minimum is lenient; real assignments are 500+ chars |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. "What if we did the opposite?" → Script should NEVER generate content (incorporated)
2. "What's the laziest solution?" → Just accept raw markdown, no parsing (incorporated)
3. "What would break at 10x scale?" → Need orchestrator integration (deferred - not in scope)
4. "Silent fallbacks produce garbage" → Fail loudly, no fallback (incorporated)

### Incorporated:
- Complete removal of template generation
- Fail-fast with clear error messages
- LLM writes everything, script saves

### Rejected (with rationale):
- Orchestrator integration: Out of scope for this refactor. Can be added later if needed.

---

## Execution Instructions for Builder

1. **Read this entire plan first**
2. **Execute Phase 1** - All changes to spawn_worker.py
3. **Run Phase 1 tests** - All 4 tests must pass
4. **Execute Phase 2** - Complete prompt rewrite
5. **Run Phase 2 test** - Verify prompt structure
6. **Execute Phase 3** - End-to-end verification
7. **Update STATUS.md** - Mark complete

**Do not proceed to next phase until current phase tests pass.**




