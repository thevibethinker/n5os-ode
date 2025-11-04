---
description: Scan workspace root and move unprotected items to Inbox/ for processing.
tool: true
  Part of the root clearinghouse system.
tags: []
---
# cleanup-root

**Category:** Maintenance  
**Version:** 1.0.0  
**Created:** 2025-10-27

---

## Purpose

Scan workspace root and move unprotected items to Inbox/ for processing. Part of the root clearinghouse system.

---

## Prerequisites

- Config exists: `file 'N5/config/root_cleanup_config.json'`
- Inbox directory exists (created automatically if missing)
- Protected directories defined in config

---

## Execution

```bash
python3 /home/workspace/N5/scripts/root_cleanup.py
```

**Dry-run mode:**
```bash
python3 /home/workspace/N5/scripts/root_cleanup.py --dry-run
```

---

## What It Does

1. Scans `/home/workspace/` root directory
2. Identifies items not in protected list:
   - Knowledge/, Lists/, Records/, N5/, Documents/
   - Careerspan/, Personal/, Articles/, Images/
   - projects/, Recipes/, Inbox/, .git
3. Moves unprotected items to `Inbox/` with timestamp prefix
4. Logs all operations to `N5/logs/.cleanup_log.jsonl`

---

## Success Criteria

- All unprotected items moved to Inbox/
- Root directory contains only protected directories
- All moves logged with metadata
- No errors in operation log

---

## Error Handling

- **Config missing:** Exits with error, requires config creation
- **Move fails:** Logs error, continues with remaining items
- **Permission denied:** Logs error, skips item

---

## Output

**Log file:** `N5/logs/.cleanup_log.jsonl`

**Example log entry:**
```json
{
  "timestamp": "2025-10-27T01:30:00",
  "operation": "move_to_inbox",
  "source": "/home/workspace/example.pdf",
  "destination": "/home/workspace/Inbox/20251027-013000_example.pdf",
  "status": "success",
  "item_type": "file",
  "size_bytes": 154832
}
```

---

## Integration

**Part of clearinghouse workflow:**
1. **cleanup-root** (this command) → Moves to Inbox/
2. **inbox-process** → Analyzes and routes files
3. **inbox-review** → Generates human review document

**Scheduled:** Daily at 11pm ET

---

## Related

- `file 'N5/commands/inbox-process.md'` - Process Inbox files
- `file 'N5/commands/inbox-review.md'` - Generate review document
- `file 'N5/config/root_cleanup_config.json'` - Configuration
- `file 'N5/scripts/root_cleanup.py'` - Implementation
