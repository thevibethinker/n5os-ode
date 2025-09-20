# Golden Templates - One-Command Recovery

This directory contains golden templates of critical engine-layer files that can be auto-restored if they become corrupted or lost.

## Files in this Directory
- `direct-knowledge-ingest.md` - Command documentation
- `core_audit.py` - Audit engine code
- `hygiene_preflight.py` - Preventive guard code

## One-Command Recovery
If a core manifest file becomes corrupted or missing, run:
```bash
N5: run core-restore --from_golden
```

This will auto-restore all golden templates and run the audit to confirm recovery.

## Updating Golden Templates
When engine-layer files are upgraded, run:
```bash
N5: run core-backup-golden --reason "Upgrade to version X"
```

Logs will be created in runtime/backup/core_restore.log