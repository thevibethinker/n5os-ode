---
description: 'Command: zo-troubleshoot-add'
tool: true
tags:
- zo
- troubleshooting
- errors
- debugging
---
# Zo Troubleshooting Quick-Add

When you encounter any issue with Zo, use this command to capture it with full context.

## What Gets Captured Automatically

1. **Timestamp** - When the issue occurred
2. **Conversation ID** - Which conversation workspace
3. **Working Directory** - Where you were
4. **User Context** - System user
5. **Command History** - Recent commands (optional)

## What You Should Provide

1. **Title**: Brief, descriptive issue title
2. **Details**: What went wrong, what was expected
3. **Error Code**: Any error messages displayed (optional)
4. **Stack Trace**: If available (optional)
5. **Tool Calls**: Which tools were involved (optional)
6. **Files**: Files affected (optional)
7. **Tags**: For categorization
8. **Reproducibility**: Can it be reproduced? Steps?
9. **Impact**: blocking, workaround-available, or minor
10. **Workaround**: If you found one (optional)

## Basic Command

```bash
python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py \
  "Brief issue title" \
  --details "Full description with context" \
  --tags "category" "component" \
  --impact "blocking"
```

## Full Example with All Options

```bash
python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py \
  "edit_file_llm failed on large file" \
  --details "Attempted to edit Documents/large-doc.md (50KB). Tool returned 'token_limit_exceeded'. No graceful fallback to edit_file provided." \
  --error-code "token_limit_exceeded" \
  --tool-calls "edit_file_llm" \
  --files "Documents/large-doc.md" \
  --tags "edit-file-llm" "token-limit" \
  --reproducible \
  --reproduce-steps "1. Create 50KB+ file 2. Call edit_file_llm 3. Observe error" \
  --impact "blocking" \
  --workaround "Manually use edit_file instead"
```

## Quick Examples

### Simple Error
```bash
python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py \
  "Tool timeout on web_search" \
  --details "web_search timed out after 30s, no results returned" \
  --tags "web-search" "timeout" \
  --impact "minor"
```

### With Stack Trace
```bash
python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py \
  "Python script crashed" \
  --details "Meeting processor threw exception" \
  --stack-trace "$(cat error.log)" \
  --tags "meeting-processor" "crash" \
  --impact "blocking"
```

### Without Command History (for privacy)
```bash
python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py \
  "Issue title" \
  --details "Details" \
  --tags "tag" \
  --no-history
```

## Quick Access Alias

Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias zoissue='python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py'
```

Then simply:
```bash
zoissue "Tool failed" --details "Description" --tags "tool-name" --impact "minor"
```

## View Issues

View all logged issues:
```bash
cat /home/workspace/N5/lists/zo-troubleshooting.md
```

Or programmatically:
```bash
python3 /home/workspace/N5/scripts/n5_lists_find.py zo-troubleshooting
```

## Impact Levels

- **blocking**: Prevents work from continuing, no workaround
- **workaround-available**: Annoying but can work around it
- **minor**: Small issue, doesn't significantly impact workflow

## Tips

1. **Be specific**: Include exact error messages, file paths, tool names
2. **Include context**: What were you trying to do?
3. **Add reproduction steps**: Helps dev team fix it
4. **Tag appropriately**: Use tool names, error types as tags
5. **Note workarounds**: If you found one, share it!
