#!/bin/bash
#
# Database Backup Script
# Created: 2025-11-03
# Purpose: Daily snapshots of operational databases with rotation
#

set -euo pipefail

# Configuration
BACKUP_DIR="/home/workspace/N5/backups/databases"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup a database
backup_db() {
    local db_path="$1"
    local db_name=$(basename "$db_path")
    local backup_name="${db_name%.db}_${TIMESTAMP}.db"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    if [ -f "$db_path" ] && [ -s "$db_path" ]; then
        cp "$db_path" "$backup_path"
        echo "[$(date -Iseconds)] Backed up: $db_path → $backup_path"
    else
        echo "[$(date -Iseconds)] Skipped (empty/missing): $db_path"
    fi
}

# Critical N5 databases
echo "=== Database Backup Started: $(date -Iseconds) ==="

backup_db "/home/workspace/N5/data/executables.db"
backup_db "/home/workspace/N5/data/conversations.db"
backup_db "/home/workspace/N5/data/meeting_pipeline.db"
backup_db "/home/workspace/N5/data/profiles.db"
backup_db "/home/workspace/N5/data/block_registry.db"
backup_db "/home/workspace/N5/data/zo_feedback.db"
backup_db "/home/workspace/N5/data/zobridge.db"

# Knowledge databases
backup_db "/home/workspace/Knowledge/crm/crm.db"
backup_db "/home/workspace/Knowledge/linkedin/linkedin.db"
backup_db "/home/workspace/Knowledge/market_intelligence/gtm_intelligence.db"

# Intelligence databases
backup_db "/home/workspace/Intelligence/blocks.db"
backup_db "/home/workspace/Intelligence/intelligence.db"

# Workspace databases
backup_db "/home/workspace/productivity_tracker.db"

# Cleanup old backups (older than retention period)
echo "=== Cleaning up backups older than $RETENTION_DAYS days ==="
find "$BACKUP_DIR" -name "*.db" -type f -mtime +$RETENTION_DAYS -delete -print

# Summary
backup_count=$(find "$BACKUP_DIR" -name "*_${TIMESTAMP}.db" -type f | wc -l)
total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "=== Backup Complete: $backup_count databases backed up ==="
echo "=== Total backup directory size: $total_size ==="
echo "=== Finished: $(date -Iseconds) ==="
