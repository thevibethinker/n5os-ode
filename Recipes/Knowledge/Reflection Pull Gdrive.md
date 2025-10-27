---
description: 'Command: reflection-pull-gdrive'
tags: []
---
# isaneReflection Pull — Google Drive

Pulls new files from the configured Google Drive folder and saves them into `N5/records/reflections/incoming/`.

## Folder

- Name: Stream Of Consciousness Reflections
- ID: 1S_tNsIGzkRt21b9uiydUjX9LmZFid3XS

## Usage

```markdown
Use google_drive-list-files to list files in the folder, then google_drive-download-file to /tmp and move to incoming.
```

## Notes

- This step is intentionally command-level (no API keys in scripts)
- Supports Google Docs export via tool configuration (set mimeType)