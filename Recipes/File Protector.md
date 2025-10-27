---
description: 'Command: file-protector'
tags: []
---
# file-protector command

Check file safety before overwrite operations to prevent accidental data loss.

## Usage

```bash
# Check if file modification is safe
N5: run file-protector file=/home/workspace/somefile.md

# Protect critical files
N5: run file-protector file=/home/workspace/N5.md operation=modify

# Test protection on prefs
N5: run file-protector file=/home/workspace/N5/prefs.md operation=edit
```

## Protection Behavior

- **Critical Files**: N5.md, prefs.md, commands.jsonl automatically protected
- **Git Check**: Files modified in Git are also protected
- **Content Check**: Non-empty files get enhanced warnings
- **Blocks Operation**: Returns exit code 1 if operation should be prevented
- **Integration Use**: Call before any file edit/rewrite operation

## Examples

```bash
# Safe check before edit
N5: run file-protector file=/home/workspace/safe.txt

# Check with custom operation name
N5: run file-protector file=config.json operation=replace
```

## System Integration

The file-protector should be called by other N5 commands before they:
- Edit critical configuration files
- Rewrite existing files with significant content
- Modify Git-tracked files

This creates defense-in-depth protection when combined with git-check for staged changes.