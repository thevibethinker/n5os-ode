#!/usr/bin/env bash
# Verification script for reflection ingestion system

set -e

echo "=========================================="
echo "  Reflection Ingestion Verification"
echo "=========================================="
echo ""

# Check directories
echo "📁 Checking directories..."
if [ -d "/home/workspace/N5/records/reflections/incoming" ]; then
    echo "  ✓ incoming/ directory exists"
else
    echo "  ✗ incoming/ directory missing"
    exit 1
fi

# Check state file
echo ""
echo "📋 Checking state file..."
if [ -f "/home/workspace/N5/records/reflections/.state.json" ]; then
    echo "  ✓ .state.json exists"
    PROCESSED_COUNT=$(jq '.processed_file_ids | length' /home/workspace/N5/records/reflections/.state.json)
    echo "  ✓ Processed files: $PROCESSED_COUNT"
else
    echo "  ✗ .state.json missing"
    exit 1
fi

# Check scripts
echo ""
echo "🔧 Checking scripts..."
if [ -f "/home/workspace/N5/scripts/reflection_ingest_v2.py" ]; then
    echo "  ✓ reflection_ingest_v2.py exists"
else
    echo "  ✗ reflection_ingest_v2.py missing"
    exit 1
fi

# Count files
echo ""
echo "📊 File counts..."
TEXT_COUNT=$(find /home/workspace/N5/records/reflections/incoming -name "*.txt" 2>/dev/null | wc -l)
AUDIO_COUNT=$(find /home/workspace/N5/records/reflections/incoming -name "*.m4a" 2>/dev/null | wc -l)
TRANSCRIPT_COUNT=$(find /home/workspace/N5/records/reflections/incoming -name "*.transcript.jsonl" 2>/dev/null | wc -l)
METADATA_COUNT=$(find /home/workspace/N5/records/reflections/incoming -name "*.json" -not -name ".*.json" 2>/dev/null | wc -l)

echo "  Text files: $TEXT_COUNT"
echo "  Audio files: $AUDIO_COUNT"
echo "  Transcripts: $TRANSCRIPT_COUNT"
echo "  Metadata files: $METADATA_COUNT"

# Verify metadata structure
echo ""
echo "🔍 Verifying metadata structure..."
SAMPLE_META=$(find /home/workspace/N5/records/reflections/incoming -name "*.json" -not -name ".*.json" 2>/dev/null | head -1)
if [ -n "$SAMPLE_META" ]; then
    if jq -e '.drive_file_id and .original_name and .downloaded_at_iso and .file_type' "$SAMPLE_META" > /dev/null 2>&1; then
        echo "  ✓ Metadata structure valid"
    else
        echo "  ✗ Metadata structure invalid"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "  ✅ ALL VERIFICATION CHECKS PASSED"
echo "=========================================="
echo ""
echo "System is ready for Worker 2"
