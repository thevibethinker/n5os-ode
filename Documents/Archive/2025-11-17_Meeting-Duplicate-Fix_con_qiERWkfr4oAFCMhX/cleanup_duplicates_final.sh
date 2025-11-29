#!/bin/bash
# Final cleanup script for duplicate meeting folders
# Analysis confirmed safe to delete - no data loss

set -e

INBOX="/home/workspace/Personal/Meetings/Inbox"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/home/.z/workspaces/con_qiERWkfr4oAFCMhX/cleanup_log_${TIMESTAMP}.txt"

echo "===== Meeting Folder Duplicate Cleanup =====" | tee "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Folders to delete (confirmed safe via analysis)
declare -a FOLDERS_TO_DELETE=(
    "2025-11-17_ilsetheapplyairochelmycareerspancom_ilsetheapplyai_rochelmycareerspancom"
    "2025-11-17_daveyunghansgmailcom"
)

echo "Folders to delete:" | tee -a "$LOG_FILE"
for folder in "${FOLDERS_TO_DELETE[@]}"; do
    full_path="$INBOX/$folder"
    if [ -d "$full_path" ]; then
        echo "  ✓ $folder" | tee -a "$LOG_FILE"
        echo "    Files:" | tee -a "$LOG_FILE"
        ls -lh "$full_path" | tail -n +2 | awk '{print "      - " $9 " (" $5 ")"}' | tee -a "$LOG_FILE"
    else
        echo "  ⚠️  $folder (NOT FOUND)" | tee -a "$LOG_FILE"
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "Corresponding [M] folders (will be kept):" | tee -a "$LOG_FILE"
for folder in "${FOLDERS_TO_DELETE[@]}"; do
    m_folder="${folder}_[M]"
    full_path="$INBOX/$m_folder"
    if [ -d "$full_path" ]; then
        file_count=$(ls -1 "$full_path" | wc -l)
        echo "  ✓ ${m_folder} (${file_count} files)" | tee -a "$LOG_FILE"
    else
        echo "  ⚠️  ${m_folder} (NOT FOUND - ABORT!)" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "ERROR: [M] folder missing! Aborting cleanup for safety." | tee -a "$LOG_FILE"
        exit 1
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "===== Executing Cleanup =====" | tee -a "$LOG_FILE"

for folder in "${FOLDERS_TO_DELETE[@]}"; do
    full_path="$INBOX/$folder"
    if [ -d "$full_path" ]; then
        echo "Deleting: $folder" | tee -a "$LOG_FILE"
        rm -rf "$full_path"
        if [ ! -d "$full_path" ]; then
            echo "  ✅ Successfully deleted" | tee -a "$LOG_FILE"
        else
            echo "  ❌ Deletion failed!" | tee -a "$LOG_FILE"
        fi
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "===== Cleanup Complete =====" | tee -a "$LOG_FILE"
echo "Remaining folders in Inbox:" | tee -a "$LOG_FILE"
ls -1 "$INBOX" | grep "^2025-" | head -20 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "Log saved to: $LOG_FILE"

