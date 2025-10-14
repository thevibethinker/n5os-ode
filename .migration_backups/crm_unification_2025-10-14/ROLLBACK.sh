#!/bin/bash
# CRM Unification Rollback Script
# Created: 2025-10-14 00:37 ET
# Use: ./ROLLBACK.sh to restore pre-migration state

set -e

BACKUP_DIR="/home/workspace/.migration_backups/crm_unification_2025-10-14"
WORKSPACE="/home/workspace"

echo "🔄 Rolling back CRM unification..."

# Reset to pre-migration commit
cd "$WORKSPACE"
git reset --hard 9cf28bd

# Restore from tarballs (if git reset insufficient)
echo "📦 Restoring N5/stakeholders from backup..."
rm -rf "$WORKSPACE/N5/stakeholders"
tar -xzf "$BACKUP_DIR/N5_stakeholders_backup.tar.gz" -C "$WORKSPACE"

echo "📦 Restoring Knowledge/crm from backup..."
rm -rf "$WORKSPACE/Knowledge/crm"
tar -xzf "$BACKUP_DIR/Knowledge_crm_backup.tar.gz" -C "$WORKSPACE"

echo "✅ Rollback complete. Verify with: git status"
