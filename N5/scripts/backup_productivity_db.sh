#!/bin/bash
# Daily backup of productivity tracker database
# Run by Daily File Guardian

BACKUP_DIR="/home/workspace/N5/backups/productivity-dashboard"
DB_FILE="/home/workspace/productivity_tracker.db"
DATE=$(date +%Y%m%d)

# Create backup directory if missing
mkdir -p "$BACKUP_DIR"

# Only backup if database exists and has content
if [ -f "$DB_FILE" ] && [ -s "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/productivity_tracker_$DATE.db"
    echo "✅ Backed up productivity database: $DATE"
    
    # Keep last 30 days of backups
    find "$BACKUP_DIR" -name "productivity_tracker_*.db" -mtime +30 -delete
else
    echo "⚠️ WARNING: Database missing or empty at $DB_FILE"
    exit 1
fi
