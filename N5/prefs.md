# N5 OS Preferences (Global)

This governs defaults and rules. Workflow sub-preferences may override; project _prefs.md overrides those.

## Command Index (top)

- `docgen` — Generate command catalog and update prefs Command Index from commands.jsonl (see ./commands/docgen.md)
- `git-check` — Quick audit for overwrites or data loss in staged Git changes (see ./commands/git-check.md)
- `lists-add` — Add an item to a list with intelligent assignment (see ./commands/lists-add.md)

## Review & Safety

- Never schedule anything without explicit consent.
- Always support --dry-run; sticky safety may enforce it.
- Require explicit approval for side-effect actions (email, external API, creating services, deleting files).
- Always search for existing protocols or processes for categorizing/storing documents before creating new ones. Prefer placing under existing structure (e.g., lists) to avoid bloat.

## Git Governance

- Track these paths explicitly:
  - N5/prefs.md
  - N5/commands.jsonl
  - N5/lists/*.jsonl
  - N5/knowledge/**/*.md
  - N5/modules/**/*.md
  - N5/flows/**/*.md
  - N5/schemas/**/*.json
  - N5/scripts/**/*.py
  - N5/examples/**/*.md

- Ignore generated and transient files:
  - N5/commands.md
  - N5/commands/*.md
  - N5/lists/*.md
  - N5/index.md
  - N5/index.jsonl
  - N5/runtime/**
  - N5/exports/**

- Use the command `N5: git-audit` regularly after adding new workflows or files to detect untracked important files.
- This will print exact shell commands to add missing files to Git.
- No automatic changes are made; manual approval is required to add files.

## Scheduling
- Enabled: false
- Max Retries: 2
- Backoff Seconds: 60, 300
- Lock Timeout: 3600
- Missed Run Policy: skip
- Timezone: UTC

## Resolution Order

Project _prefs.md > Workflow sub-pref > Global prefs.md. Knowledge informs, does not override.

## Knowledge Lookup

- Topic: career spans / Careerspan — Always check ./N5/knowledge before answering; prefer facts from there and update if gaps are found.

## Google Drive Access

- **Preference**: Always first try to access Google Drive related content through the integration first, versus through a web browser or consumer access.
- **Steps for Accessing Google Drive Files**:
  1. Verify the Google Drive app integration is connected using `list_app_tools(app_slug="google_drive")`.
  2. Retrieve file metadata using `use_app_google_drive` with `tool_name="google_drive-get-file-by-id"` and the file ID.
  3. Download the file content using `use_app_google_drive` with `tool_name="google_drive-download-file"`, specifying the file ID, filePath (e.g., "/tmp/filename.txt"), and mimeType (e.g., "text/plain" for Google Docs export).
  4. If the tool returns a download URL, use `run_bash_command` with curl to fetch it to the workspace (e.g., "/home/workspace/filename.txt").
  5. Read the downloaded file using `read_file` with the absolute path.