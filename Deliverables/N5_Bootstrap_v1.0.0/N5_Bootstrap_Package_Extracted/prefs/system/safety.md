# Safety & Review Requirements

**Module:** System Governance  
**Version:** 2.0.0  
**Date:** 2025-10-09  
**Priority:** CRITICAL — These rules cannot be overridden

---

## Core Safety Rules

### Explicit Consent Required

**Never perform these actions without explicit user approval:**

1. **Scheduling**
   - Creating calendar events
   - Scheduling tasks or recurring jobs
   - Setting up cron jobs or timers

2. **External Communications**
   - Sending emails
   - Posting to external APIs
   - Making webhooks calls
   - SMS or other notifications

3. **Service Management**
   - Creating user services
   - Registering web services
   - Opening network ports
   - Starting background processes

4. **Destructive Operations**
   - Deleting files or folders
   - Overwriting protected files (see `file 'N5/prefs/system/file-protection.md'`)
   - Dropping database tables or collections
   - Git force-push or reset operations

---

## Dry-Run Requirements

### Always Support Dry-Run Mode

Every operation that modifies state must support `--dry-run` flag:

```bash
# Example
command lists-add --dry-run "New item" --list tasks
```

**Dry-run output should show:**
- Exact changes that would be made
- Files that would be created/modified
- External calls that would be triggered
- Rollback procedure if needed

### Sticky Safety

For high-risk operations, **enforce dry-run by default** until user confirms with explicit flag:

```bash
# Requires explicit confirmation
command lists-delete --confirm item-id
```

---

## Protocol Search Requirement

**Always search for existing protocols or processes before creating new ones.**

### Search Locations

Before creating new structures:

1. **Check commands registry:**
   ```bash
   grep -i "keyword" /home/workspace/N5/config/commands.jsonl
   ```

2. **Check existing folders:**
   - Is there a POLICY.md that defines placement?
   - Do similar files already exist in a category folder?

3. **Check schemas:**
   - Does a schema exist for this data type?
   - Should this fit into an existing structure?

4. **Check lists:**
   - Is there an existing list for this category?
   - Should this be added to a list vs. new file?

### Prefer Existing Structure

- **Add to existing** rather than create new
- **Extend existing** rather than duplicate
- **Reference existing** rather than copy

This prevents:
- File bloat
- Scattered information
- Duplicate structures
- Synchronization drift

---

## File Creation Protocol

**Whenever a new file is created, always ask me where the file should be located.**

### Questions to Ask

1. **Category:** What type of content is this? (knowledge, list, document, script)
2. **Existing structure:** Does a folder already exist for this category?
3. **Naming:** What naming convention applies to this location?
4. **Policy:** Is there a POLICY.md that governs this folder?

### Do Not Assume

- Do not create files in `/home/workspace` root without permission
- Do not create new category folders without discussion
- Do not bypass POLICY.md rules for convenience

---

## Validation Requirements

### Before State Changes

1. **Read current state** (for files, configs, data)
2. **Show diff** of proposed changes
3. **Validate against schema** if applicable
4. **Check for conflicts** (duplicates, overwrites)
5. **Require confirmation** from user

### After State Changes

1. **Verify success** (file exists, content correct)
2. **Log the change** (timeline, audit log)
3. **Report outcome** to user
4. **Provide rollback** instructions if needed

---

## Related Files

- **File Protection:** `file 'N5/prefs/system/file-protection.md'`
- **Folder Policy:** `file 'N5/prefs/system/folder-policy.md'`
- **Operational Principles:** `file 'Knowledge/architectural/operational_principles.md'`
- **Lists Policy:** `file 'Lists/POLICY.md'`

---

## Emergency Procedures

### If Accidental Deletion Occurs

1. **Stop immediately** — do not make further changes
2. **Check Git history:**
   ```bash
   git log --oneline -10 -- [file]
   git show [commit]:[file] > [file].recovered
   ```
3. **Notify user** with full details
4. **Document incident** in timeline
5. **Restore from backup** if Git unavailable

### If Overwrite Occurs

1. **Preserve current state:**
   ```bash
   cp [file] [file].backup.$(date +%Y%m%d_%H%M%S)
   ```
2. **Check Git for previous version**
3. **Show diff** between versions
4. **Let user decide** which version to keep
5. **Document in timeline**

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Added explicit consent categories
- Added dry-run requirements and sticky safety
- Added protocol search workflow
- Added file creation protocol (ask for location)
- Added validation requirements
- Added emergency procedures
