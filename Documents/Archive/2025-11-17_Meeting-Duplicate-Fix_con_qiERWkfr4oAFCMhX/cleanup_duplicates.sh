#!/bin/bash
# Cleanup script for duplicate meeting folders
# Run AFTER confirming fix works

set -e

INBOX="/home/workspace/Personal/Meetings/Inbox"

echo "===== Duplicate Folder Cleanup ====="
echo "This script will remove raw folders that have [M] or [P] duplicates"
echo ""

# Find raw folders with [M] duplicates
echo "Finding raw folders with [M] duplicates..."
for raw_folder in "$INBOX"/2025-*; do
    # Skip if has suffix
    if [[ "$raw_folder" =~ _\[M\]$ ]] || [[ "$raw_folder" =~ _\[P\]$ ]]; then
        continue
    fi
    
    # Check if [M] version exists
    m_folder="${raw_folder}_[M]"
    p_folder="${raw_folder}_[P]"
    
    if [ -d "$m_folder" ] || [ -d "$p_folder" ]; then
        echo ""
        echo "Found duplicate:"
        echo "  Raw: $raw_folder"
        [ -d "$m_folder" ] && echo "  [M]: $m_folder"
        [ -d "$p_folder" ] && echo "  [P]: $p_folder"
        
        # Show file comparison
        echo "  Files in raw:"
        ls "$raw_folder" | head -5
        
        echo "  Action: Will remove raw folder (keeping [M]/[P] version)"
    fi
done

echo ""
echo "===== DRY RUN COMPLETE ====="
echo "To execute cleanup, uncomment the rm -rf lines in the script"
echo ""

# UNCOMMENT TO EXECUTE:
# for raw_folder in "$INBOX"/2025-*; do
#     if [[ "$raw_folder" =~ _\[M\]$ ]] || [[ "$raw_folder" =~ _\[P\]$ ]]; then
#         continue
#     fi
#     m_folder="${raw_folder}_[M]"
#     p_folder="${raw_folder}_[P]"
#     if [ -d "$m_folder" ] || [ -d "$p_folder" ]; then
#         echo "Removing: $raw_folder"
#         rm -rf "$raw_folder"
#     fi
# done

