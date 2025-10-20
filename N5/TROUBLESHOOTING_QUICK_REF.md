# Zo Troubleshooting - Quick Reference

## Report an Issue

```bash
python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py \
  "Issue title" \
  --details "What went wrong" \
  --tags "category" \
  --impact "blocking"
```

## Optional Alias

```bash
alias zoissue='python3 /home/workspace/N5/scripts/zo_troubleshoot_add.py'
```

## Common Scenarios

### Tool Error
```bash
zoissue "Tool X failed" \
  --details "Error message: Y" \
  --tags "tool-x" \
  --impact "minor"
```

### With Error Code
```bash
zoissue "API timeout" \
  --details "Request timed out after 30s" \
  --error-code "ETIMEDOUT" \
  --tags "api" "timeout" \
  --impact "workaround-available" \
  --workaround "Retry manually"
```

### Reproducible Bug
```bash
zoissue "File edit fails on large files" \
  --details "edit_file_llm fails on 50KB+ files" \
  --tags "edit-file-llm" "bug" \
  --reproducible \
  --reproduce-steps "1. Create 50KB file 2. Edit it" \
  --impact "blocking"
```

## View Issues

```bash
cat /home/workspace/N5/lists/zo-troubleshooting.md
```

## All Options

- `--details` (required): Full description
- `--error-code`: Error message or code
- `--stack-trace`: Stack trace if available
- `--tool-calls`: Which tools involved
- `--files file1 file2`: Files affected
- `--tags tag1 tag2`: Categories
- `--reproducible`: Can reproduce
- `--reproduce-steps`: How to reproduce
- `--impact`: blocking|workaround-available|minor
- `--workaround`: If found
- `--no-history`: Don't capture command history

---

**Full docs**: file 'N5/commands/zo-troubleshoot-add.md'
