# Migration Backup Plan

**Created**: 2026-02-09 05:10 ET  
**Build**: meeting-system-v3  
**Drop**: D5.2

## Full Backup Strategy

### Complete Snapshot
Before any migration operations, create a complete snapshot of `Personal/Meetings/`:

```bash
# Create timestamped backup
BACKUP_DIR="/home/workspace/Backups/meetings-migration-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r Personal/Meetings/ "$BACKUP_DIR/"

# Verify backup integrity
find Personal/Meetings/ -type f | wc -l > "$BACKUP_DIR/file_count_original"
find "$BACKUP_DIR/Meetings/" -type f | wc -l > "$BACKUP_DIR/file_count_backup"
diff "$BACKUP_DIR/file_count_original" "$BACKUP_DIR/file_count_backup" || echo "Backup count mismatch!"
```

### Incremental Rollback Points

1. **Pre-manifest-upgrade**: Before any manifest.json changes
2. **Pre-transcript-conversion**: Before JSONL → MD conversions
3. **Pre-archive-move**: Before moving folders to Week-of-* structure

## Recovery Commands

### Full Rollback
```bash
BACKUP_DIR="/path/to/backup"
rm -rf Personal/Meetings/
cp -r "$BACKUP_DIR/Meetings/" Personal/
```

### Partial Rollback
```bash
# Restore specific folder
FOLDER="2026-01-26_Collateral-Blitz_Logan"
rm -rf "Personal/Meetings/$FOLDER"
cp -r "$BACKUP_DIR/Meetings/$FOLDER" Personal/Meetings/
```

### Manifest Rollback
```bash
# Restore .legacy backup files
find Personal/Meetings/ -name "*.json.legacy" | while read legacy; do
    original="${legacy%.legacy}"
    cp "$legacy" "$original"
done
```

## Verification Checksums

The backup plan includes checksums for all files to verify integrity:

```bash
# Generate checksums before migration
find Personal/Meetings/ -type f -exec sha256sum {} \; > migration_checksums.txt
```

## Storage Location
Backups will be stored in:
- Primary: `/home/workspace/Backups/meetings-migration-YYYYMMDD_HHMMSS/`  
- Secondary: Git commit before migration (via git add/commit)