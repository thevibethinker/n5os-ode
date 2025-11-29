---
description: 
tool: true Formal conversation end-step - resolve all conversation effects. Reviews files, proposes organization, executes cleanup, generates AAR, archives build tracker.
tags:
  - session
  - cleanup
  - organization
  - aar
  - conversation
---
# Close Conversation

Runs the formal **conversation-end workflow** - like Magic: The Gathering's end step, where all conversation effects are resolved.

## Flags

- `--require-confirm`: If set, the recipe runs interactively requiring user confirmations.
  Otherwise, it runs in semi-interactive mode where prompts are minimized and only critical confirmations are requested.

## What This Does

**6-Phase Workflow:**

1. **Phase -1:** Lesson Extraction - Captures reusable patterns
2. **Phase 0:** AAR Generation - Creates after-action report with thread export
3. **Phase 0.5:** Artifact Symlinking - Links deliverables to AAR folder
4. **Phase 1-2:** File Organization - Reviews and moves conversation files
5. **Phase 2.5:** Placeholder Detection - Enforces P16 (Accuracy) & P21 (Document Assumptions)
6. **Phase 2.75:** Capability Registry Check (build/orchestrator threads only) - Captures capability changes for the N5 Capability Registry
7. **Phase 3:** Personal Intelligence Update - Updates your behavioral patterns
8. **Phase 3.5:** Build Tracker Archival - Archives completed tasks from BUILD_MAP
9. **Phase 4:** Git Status Check - Prompts to commit uncommitted changes
10. **Phase 4.5:** System Timeline Check - Auto-detects timeline-worthy changes
11. **Phase 5:** Thread Title Generation - Creates descriptive thread title
12. **Phase 6:** Archive & Cleanup - Cleans workspace, archives if significant

## When to Use

**Invoke when:**
- Wrapping up a conversation
- Marking work as complete
- Want formal AAR and cleanup
- Ready to archive conversation artifacts

**Commands:**
- `/close-conversation`
- "End conversation"
- "Wrap up"
- "conversation-end"

## What You Get

✅ Complete AAR with thread export  
✅ Files organized to permanent locations  
✅ Build tracker tasks archived  
✅ Git changes committed (if confirmed)  
✅ System timeline updated  
✅ Thread title generated  
✅ Clean workspace ready for next conversation

## Full Documentation

`file N5/prefs/operations/conversation-end.md`

## Execution

**CRITICAL: Before presenting final results to the user, you MUST:**
1. Load `file 'N5/prefs/operations/conversation-end-output-template.md'`
2. **YOU do the actual analysis** - Read conversation files, understand what was built/discussed
3. **Scripts only provide structure** - Use their file lists, but YOU write descriptions/summaries
4. **No placeholder/stub data** - All content must be real, specific to THIS conversation
5. Follow template structure EXACTLY - no improvisation, no reordering
6. Use specified emojis and formatting precisely

**Scripts give you mechanics (file paths, git status), YOU provide semantics (understanding, meaning, context).**

### Capability Registry Integration (Worker 5)

This recipe is wired into the **N5 Capability Registry** for build-oriented orchestrator threads. After you have a clear understanding of what was built and how files were organized, you MUST run a capability checkpoint before finalizing the closure output.

1. **Decide if this is a build/orchestrator thread**
   - Treat the conversation as a **build/orchestrator thread** if the primary work was:
     - Designing or implementing a system, workflow, orchestrator, or agent (e.g., meeting pipeline, CRM v3, media/doc systems, MG-series agents, capability-registry builds), or
     - Making substantial, persistent changes to N5 scripts, prompts, or capabilities.
   - Treat it as **non-build/ephemeral** if it was primarily:
     - A small bug fix, lightweight investigation, ad-hoc research, or short coaching thread, and
     - Did **not** create or meaningfully change an ongoing capability.

2. **If NOT a build/orchestrator thread**
   - Do **not** touch the registry.
   - In the final closure output, set the **Capability Registry Updates** section to a single bullet:
     - `- None – No capability changes logged for this conversation (non-build or ephemeral thread).`

3. **If this IS a build/orchestrator thread – ask explicitly about capabilities**
   - Ask V directly:
     - **Q1:** "Did this conversation create a new major capability or significantly change an existing N5 capability? (yes / no / unsure)"
   - If V answers **no**, do not touch the registry and explicitly state in the final output:
     - `- None – No capability changes logged for this conversation (build/orchestrator work, explicitly confirmed).`
   - If V answers **yes** or **unsure but leaning yes**, proceed to gather structured metadata.

4. **Gather minimal structured metadata**
   Ask V for concise, structured answers:
   - **Q2 – Capability name:** Human-readable name.
   - **Q3 – Category:** One of `integration`, `internal`, `workflow`, `orchestrator`, `agent`, `site`.
   - **Q4 – New vs update:**
     - `new` – entirely new capability
     - `update` – significantly extending or changing an existing capability
   - **Q5 – If update:** "Which existing capability does this correspond to? (capability_id and/or capability file path under `N5/capabilities/**` – e.g., `meeting-pipeline-v2` or `N5/capabilities/internal/meeting-pipeline-v2.md`)"
   - **Q6 – Short description:** 2–4 sentences summarizing what this capability does and what changed in this conversation.
   - **Q7 – Entry points:** Bullet list of key entry points with type + id, following the capability template:
     - `- type: prompt, id: "Prompts/...prompt.md"`
     - `- type: script, id: "N5/scripts/...py"`
     - `- type: url, value: "https://..."`
     - `- type: agent, id: "[scheduled-task-id-or-name]"`
   - **Q8 – Associated files:** Bullet list of important implementation files using `file '...'` paths (prompts, scripts, specs, configs).

5. **Construct a capability update spec (YAML)**
   - From the answers above, construct a single YAML block named `capability_update` with at least:

     ```yaml
     capability_update:
       capability_id: [kebab-case-id]
       name: "[Human-readable name]"
       category: [integration|internal|workflow|orchestrator|agent|site]
       status: [active|experimental|deprecated]
       confidence: [high|medium|low]
       last_verified: [YYYY-MM-DD]
       tags:
         - [primary-domain]
       entry_points:
         - type: prompt
           id: "Prompts/...prompt.md"
         # ...
       owner: "V"
       change_type: [new|update]
       capability_file: "N5/capabilities/.../[capability_id].md"
       description: |
         [2–4 sentence description]
       associated_files:
         - "relative/path/from/workspace.md"
         - "N5/scripts/example.py"
     ```

   - Determine `capability_file` using the category → directory mapping in `file 'N5/capabilities/index.md'`:
     - `integration` → `N5/capabilities/integrations/`
     - `internal` → `N5/capabilities/internal/`
     - `workflow`, `orchestrator`, `agent`, `site` → `N5/capabilities/workflows/`

6. **Apply the update (mechanics vs semantics)**
   - **Semantics (YOU):** You are responsible for choosing good names, accurate descriptions, realistic tags, and correct entry points based on the actual work in this conversation.
   - **Mechanics (scripts/tools):**
     - If a helper script `N5/scripts/capability_registry_update.py` exists and is configured, you MAY:
       - Write the YAML block to a temporary spec file (e.g., `/tmp/[capability_id]_spec.yaml`).
       - Run (conceptually):
         - `python3 /home/workspace/N5/scripts/capability_registry_update.py --spec /tmp/[capability_id]_spec.yaml`
       - Then summarize what the script reports as created/updated.
     - If no helper script is available, treat the YAML block as a **precise editing spec** and use normal Zo tooling to:
       - Create or update the corresponding capability markdown file under `N5/capabilities/**` following `CAPABILITY_TEMPLATE.md`.
       - Append or adjust the relevant line in `file 'N5/capabilities/index.md'` so the index stays in sync.

7. **Populate the final "Capability Registry Updates" section**
   - In the final conversation-end output (using `conversation-end-output-template.md`), the **Capability Registry Updates** section MUST show one of:
     - For non-build/ephemeral threads: the standard `None` line.
     - For build/orchestrator threads with **no** registry changes (explicitly confirmed): the explicit `None` line with explanation.
     - For threads with changes: one bullet per change, e.g.:
       - `- New capability: meeting-pipeline-v3 – Meeting pipeline refactor with MG-2 integration (file 'N5/capabilities/internal/meeting-pipeline-v3.md').`
       - `- Updated capability: crm-v3 – Added Akiflow actions bridge entry point (file 'N5/capabilities/internal/crm-v3.md').`
   - Never leave this section implicit or blank; it must always either enumerate real capability changes or clearly state that none were logged.

This recipe uses the **conversation-end orchestrator** - a 3-phase pipeline that analyzes, proposes, and executes cleanup operations.

### Quick Run (Recommended)

```bash
# Auto-detect conversation ID and run full pipeline
CONVO_ID=$(basename "$(pwd)")
WORKSPACE_DIR=$(pwd)
python3 /home/workspace/N5/scripts/conversation_end_analyzer.py --workspace "$WORKSPACE_DIR" --convo-id "$CONVO_ID" --output /tmp/analysis.json
python3 /home/workspace/N5/scripts/conversation_end_proposal.py --analysis /tmp/analysis.json --output /tmp/proposal.json
```

Review the proposal, then execute:

```bash
# Dry-run first (preview changes)
python3 /home/workspace/N5/scripts/conversation_end_executor.py --proposal /tmp/proposal.json --dry-run

# Execute for real
python3 /home/workspace/N5/scripts/conversation_end_executor.py --proposal /tmp/proposal.json
```

### Manual Phase-by-Phase

**Phase 1: Analyze**
```bash
python3 /home/workspace/N5/scripts/conversation_end_analyzer.py \
  --workspace /home/.z/workspaces/con_XXXXX \
  --convo-id con_XXXXX \
  --output /tmp/conv_analysis.json
```

**Phase 2: Generate Proposal**
```bash
python3 /home/workspace/N5/scripts/conversation_end_proposal.py \
  --analysis /tmp/conv_analysis.json \
  --format markdown \
  --output /tmp/conv_proposal.md
```

**Phase 3: Execute**
```bash
# Dry-run (preview)
python3 /home/workspace/N5/scripts/conversation_end_executor.py \
  --proposal /tmp/conv_analysis.json \
  --dry-run

# Real execution
python3 /home/workspace/N5/scripts/conversation_end_executor.py \
  --proposal /tmp/conv_analysis.json
```

### Rollback

If something goes wrong:
```bash
python3 /home/workspace/N5/scripts/conversation_end_executor.py \
  --rollback /tmp/transaction_TIMESTAMP.json
```

---

**Related:**
- `recipe 'Meetings/Export Thread.md'` - AAR only (Phase 0 standalone)
- `recipe 'Meetings/Analyze Meeting.md'` - Meeting-specific processing

