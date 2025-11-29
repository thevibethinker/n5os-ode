---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Conversation-End Pipeline (Analyzer → Proposal → Executor)

Canonical operational view of the 3‑phase conversation closure pipeline.

Related docs:
- Schema: `file 'N5/prefs/operations/conversation_end_schema.md'`
- Canonical overview: `file 'N5/prefs/operations/conversation-end-CANONICAL.md'`
- Output template (final human summary): `file 'N5/prefs/operations/conversation-end-output-template.md'`

## 1. Phases and Responsibilities

### Phase 1 – ANALYZE (`conversation_end_analyzer.py`)

- **Input:**
  - Conversation ID (without `con_` prefix), e.g. `nKcbWQptDIBJKPUb`.
  - Root of conversation workspaces: `/home/.z/workspaces`.
- **Behavior:**
  - Scans `/home/.z/workspaces/con_{convo_id}` for files.
  - Emits `analysis.json` with:
    - `convo_id`
    - `artifacts`: relative paths + sizes
    - `documents`: selected persistent docs (currently `*Level_Upper*` in `Documents/`)
    - `summary`: reserved for future semantic summary
- **Example command:**

```bash
python3 N5/scripts/conversation_end_analyzer.py \
  --workspace /home/.z/workspaces \
  --convo-id nKcbWQptDIBJKPUb \
  --output /home/.z/workspaces/con_nKcbWQptDIBJKPUb/analysis.json
```

### Phase 2 – PROPOSE (`conversation_end_proposal.py`)

- **Input:**
  - `analysis.json` from Phase 1.
- **Behavior (current):**
  - Derives `conversation_id`, `title`, `thread_title` from `analysis`.
  - Computes archive root:
    - `/home/workspace/Documents/Archive/YYYY-MM-DD_con_{convo_id}`.
  - Generates `archive` actions for each artifact in the conversation workspace:
    - `source = /home/.z/workspaces/con_{convo_id}/{relative_path}`
    - `destination = /home/workspace/Documents/Archive/YYYY-MM-DD_con_{convo_id}/{relative_path}`
  - Marks all generated actions as `approved: true`.
  - Populates auxiliary metadata (see schema doc): `files_to_organize`, `archive_location`, `aar_required`, `tasks_to_close`, `git_changes`, `thread_title`.
  - If archive root already exists on disk, sets `requires_resolution = true` and adds a `conflicts` entry so executor will **refuse to run**.

- **Example command:**

```bash
python3 N5/scripts/conversation_end_proposal.py \
  --analysis /home/.z/workspaces/con_nKcbWQptDIBJKPUb/analysis.json \
  --output  /home/.z/workspaces/con_nKcbWQptDIBJKPUb/proposal.json
```

### Phase 3 – EXECUTE (`conversation_end_executor.py`)

- **Input:**
  - `proposal.json` from Phase 2.
- **Behavior (high level):**
  - Validates proposal structure (`conversation_id`, `title`, `actions`).
  - Aborts immediately if `requires_resolution` is `true`, logging all `conflicts`.
  - Filters `actions` to only `approved` non‑`ignore` entries.
  - Runs pre‑flight checks (existence, destination non‑existence, writeability, duplicate destinations).
  - Executes `move` / `archive` / `delete` actions with:
    - Transaction log in `/tmp/conversation_end_transaction_<conversation_id>.log`.
    - Backup copies for deletes under `/tmp/conversation_end_backups/<conversation_id>/`.
  - Supports rollback from transaction logs.

- **Dry‑run example (safe):**

```bash
python3 N5/scripts/conversation_end_executor.py \
  --proposal /home/.z/workspaces/con_nKcbWQptDIBJKPUb/proposal.json \
  --dry-run
```

This mode **never moves or deletes files**; it only runs validation and logs "Would move / Would delete" messages.

- **Real execution example (see safety below):**

```bash
python3 N5/scripts/conversation_end_executor.py \
  --proposal /home/.z/workspaces/con_nKcbWQptDIBJKPUb/proposal.json
```

## 2. Safety and N5 Protections

### Core Rules

1. **Never run real execution without explicit confirmation from V.**
2. **Always run a dry‑run first** and inspect logs.
3. **Honor `.n5protected` and n5 safety scripts** before any destructive change.

### `.n5protected` / Safety Script

Before any real execution affecting a path, run:

```bash
python3 /home/workspace/N5/scripts/n5_protect.py check /home/workspace
```

For bulk operations or when targeting specific trees, use the most specific path available, e.g.:

```bash
python3 /home/workspace/N5/scripts/n5_protect.py check /home/workspace/Documents/Archive
```

If the script reports a protected path, do **not** proceed without explicit sign‑off from V.

### Dry‑run vs Real Execution

**Dry‑run (`--dry-run`):**
- Validates proposal schema.
- Runs all pre‑flight checks.
- Logs each action as `"[DRY RUN] Would move ..."` / `"[DRY RUN] Would delete ..."`.
- Does **not** touch the filesystem.

**Real execution (no `--dry-run`):**
- Performs actual `move` / `archive` / `delete` operations.
- Writes transaction log (`/tmp/conversation_end_transaction_<conversation_id>.log`).
- Creates backups for deletes under `/tmp/conversation_end_backups/<conversation_id>/`.
- Can be rolled back using the `--rollback` option.

### Rollback Usage

Given a transaction log path:

```bash
python3 N5/scripts/conversation_end_executor.py \
  --rollback /tmp/conversation_end_transaction_nKcbWQptDIBJKPUb.log
```

The executor will walk the log in reverse and attempt to restore all prior moves/deletes.

## 3. How This Fits With Final Human Output

The executor handles **filesystem state** only. It does **not** generate the human‑readable closure report.

Final conversation closure output uses:
- Template: `file 'N5/prefs/operations/conversation-end-output-template.md'`
- Additional scripts/recipes to:
  - Scan archived artifacts.
  - Summarize what was built.
  - Present status and next steps.

The proposal/executor pipeline must ensure that:
- Conversation artifacts are archived into a stable, predictable folder:
  - `Documents/Archive/YYYY-MM-DD_con_{convo_id}/...`
- The final human summary can confidently reference real paths and filenames.

## 4. Minimal Operator Checklist

For a specific conversation ID `<CID>` (without `con_` prefix):

1. **Analyze**
   ```bash
   python3 N5/scripts/conversation_end_analyzer.py \
     --workspace /home/.z/workspaces \
     --convo-id <CID> \
     --output /home/.z/workspaces/con_<CID>/analysis.json
   ```

2. **Generate proposal**
   ```bash
   python3 N5/scripts/conversation_end_proposal.py \
     --analysis /home/.z/workspaces/con_<CID>/analysis.json \
     --output  /home/.z/workspaces/con_<CID>/proposal.json
   ```

3. **Dry‑run executor (safe)**
   ```bash
   python3 N5/scripts/conversation_end_executor.py \
     --proposal /home/.z/workspaces/con_<CID>/proposal.json \
     --dry-run
   ```

4. **If and only if V explicitly approves real execution:**
   - Run n5_protect checks for relevant paths.
   - Then execute without `--dry-run`.

This keeps the contract between analyzer → proposal → executor explicit, testable, and safe to extend.

