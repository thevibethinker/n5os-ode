#!/bin/bash
# Verify Meeting Auto-Processing System Setup

echo "=== Meeting Auto-Processing System Verification ==="
echo ""

# Check processing log exists
echo "1. Processing Log:"
if [ -f "/home/workspace/N5/logs/meeting-processing/processed_transcripts.jsonl" ]; then
    COUNT=$(wc -l < /home/workspace/N5/logs/meeting-processing/processed_transcripts.jsonl)
    echo "   ✅ Log exists: $COUNT entries"
    echo "   Last entry:"
    tail -1 /home/workspace/N5/logs/meeting-processing/processed_transcripts.jsonl | jq -r '"\(.file_name) - \(.status)"'
else
    echo "   ❌ Log not found"
fi
echo ""

# Check duplicate detector script
echo "2. Duplicate Detector:"
if [ -x "/home/workspace/N5/scripts/meeting_duplicate_detector.py" ]; then
    echo "   ✅ Script exists and is executable"
else
    echo "   ❌ Script not found or not executable"
fi
echo ""

# Check directories
echo "3. Directory Structure:"
for dir in "/home/workspace/Documents/Meetings/_staging" \
           "/home/workspace/Meetings" \
           "/home/workspace/N5/logs/meeting-processing"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir"
    else
        echo "   ❌ $dir (missing)"
    fi
done
echo ""

# Check metadata schema
echo "4. N5 Schema Integration:"
if [ -f "/home/workspace/N5/schemas/meeting-metadata.schema.json" ]; then
    echo "   ✅ meeting-metadata.schema.json exists"
else
    echo "   ❌ Schema file not found"
fi
echo ""

# Check command registration
echo "5. Command Registration:"
if grep -q "meeting-auto-process" /home/workspace/N5/config/commands.jsonl 2>/dev/null; then
    echo "   ✅ meeting-auto-process registered"
else
    echo "   ⚠️  Command not in registry"
fi
echo ""

# Count processed meetings
echo "6. Processed Meetings:"
if [ -d "/home/workspace/Meetings" ]; then
    MEETING_COUNT=$(ls -1 /home/workspace/Meetings | wc -l)
    echo "   📊 $MEETING_COUNT meeting folders"
    if [ $MEETING_COUNT -gt 0 ]; then
        echo "   Recent:"
        ls -1t /home/workspace/Meetings | head -3 | sed 's/^/      - /'
    fi
else
    echo "   ❌ Meetings directory not found"
fi
echo ""

# Check for duplicates in log
echo "7. Duplicate Detection Status:"
if [ -f "/home/workspace/N5/logs/meeting-processing/processed_transcripts.jsonl" ]; then
    DUP_COUNT=$(grep -c 'duplicate_skipped' /home/workspace/N5/logs/meeting-processing/processed_transcripts.jsonl || echo "0")
    echo "   📊 $DUP_COUNT duplicates detected and skipped"
fi
echo ""

echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "  - Check scheduled task at: https://va.zo.computer/schedule"
echo "  - View full documentation: AUTOMATED_MEETING_SYSTEM_COMPLETE.md"
echo "  - Test duplicate detector: python3 N5/scripts/meeting_duplicate_detector.py <filename>"
