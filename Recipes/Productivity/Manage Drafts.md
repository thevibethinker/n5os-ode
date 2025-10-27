---
description: 'Command: manage-drafts'
tags:
- drafts
- review
- cleanup
- productivity
---
# Manage Drafts

**Purpose**: Review, clean up, and manage generated drafts in `Records/Personal/drafts/`.

---

## Quick Actions

### List All Pending Drafts

```bash
find Records/Personal/drafts/ -type f -name "*.md" | sort
```

### List Drafts by Type

```bash
# Emails only
ls -lht Records/Personal/drafts/emails/

# Documents only
ls -lht Records/Personal/drafts/documents/

# Other
ls -lht Records/Personal/drafts/other/
```

### Find Old Drafts (&gt;7 days)

```bash
find Records/Personal/drafts/ -type f -mtime +7 -ls
```

### Count Pending Drafts

```bash
find Records/Personal/drafts/ -type f -name "*.md" | wc -l
```

---

## Cleanup Actions

### Delete Single Draft (after sending)

```bash
rm Records/Personal/drafts/emails/YYYY-MM-DD-name.md
```

### Delete All Drafts Older Than 7 Days

```bash
# Dry run (preview)
find Records/Personal/drafts/ -type f -mtime +7 -print

# Execute
find Records/Personal/drafts/ -type f -mtime +7 -delete
```

### Archive Draft (if needed for reference)

```bash
# Move to external archive or Documents/ if permanent reference
mv Records/Personal/drafts/emails/important-draft.md Documents/Archive/
```

---

## Review Workflow

### 1. List Pending Drafts

```bash
ls -lht Records/Personal/drafts/emails/
```

### 2. Review Each Draft

Open in editor, verify content, make edits if needed

### 3. Take Action

- **Send email**: Copy content, send via client or Gmail tool
- **Publish document**: Share, distribute, or publish
- **Save for later**: If not ready, leave in drafts/

### 4. Clean Up

After action taken:

```bash
# Delete
rm Records/Personal/drafts/emails/2025-10-17-sent-email.md

# Or archive if important
mv Records/Personal/drafts/emails/2025-10-17-important.md Documents/Archive/
```

---

## Style Guide Integration

If draft was generated with a style guide, consider adding as exemplar:

```markdown
# Validate against style guide
python3 N5/scripts/style_guide_manager.py validate \
  --output-type [type] \
  --
```

`file Records/Personal/drafts/emails/draft.md`    # Add as exemplar if excellent python3 N5/scripts/style_guide_manager.py add-exemplar \\   --output-type \[type\] \\   --`file Records/Personal/drafts/emails/draft.md`   \\   --name descriptive-name

---

## Automation Opportunities

### Weekly Draft Review Reminder

Set up scheduled task to remind you to review drafts:

- List all pending drafts
- Highlight old drafts (&gt;7 days)
- Summary count by type

### Auto-Cleanup

Optional: Set up scheduled task to auto-delete drafts older than 30 days\
(with manual review first)

---

## Best Practices

- **Review daily**: Check drafts/ each morning
- **Act quickly**: Send/publish within 24-48 hours
- **Clean immediately**: Delete/archive right after sending
- **Use descriptive names**: Easy to scan and identify
- **Don't hoard**: Drafts are temporary by design

---

## Related Commands

- `command "Commands/Quick Classify.md"`   - Classify and organize files
- `command N5/commands/conversation-end.md`   - End-of-conversation cleanup
- `command N5/commands/workspace-maintenance.md`   - General workspace cleanup

---

## Related Documentation

- file 'Records/Personal/drafts/README.md' - Drafts directory guide
- file 'N5/prefs/operations/style-guide-protocol.md' - Style guide usage
- file 'N5/style_guides/' - Output standards

---

**Invocation**: Type `/manage-drafts` or reference this file in conversation