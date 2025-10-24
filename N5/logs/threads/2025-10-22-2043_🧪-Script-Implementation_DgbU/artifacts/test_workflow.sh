#!/bin/bash
# Test Content Library workflow against multiple meetings

set -e

WORKSPACE="/home/workspace"
SCRIPT="$WORKSPACE/N5/scripts/n5_follow_up_email_generator.py"
OUTPUT_DIR="/home/.z/workspaces/con_frSxWyuzF9e9DgbU/test_results"
LOG_FILE="$OUTPUT_DIR/test_log.txt"

mkdir -p "$OUTPUT_DIR"

echo "==================================" | tee "$LOG_FILE"
echo "Content Library Workflow Test Suite" | tee -a "$LOG_FILE"
echo "$(date)" | tee -a "$LOG_FILE"
echo "==================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test meetings
MEETINGS=(
    "N5/records/meetings/2025-10-14_strategic-session-pt2-skeleton-crew-1209"
    "N5/records/meetings/2025-10-14_strategic-session-pt3-dual-brand-plan"
)

test_count=0
success_count=0
fail_count=0

for meeting in "${MEETINGS[@]}"; do
    meeting_path="$WORKSPACE/$meeting"
    meeting_name=$(basename "$meeting")
    
    echo "=== Testing: $meeting_name ===" | tee -a "$LOG_FILE"
    
    if [ ! -d "$meeting_path" ]; then
        echo "❌ SKIP: Folder not found" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        continue
    fi
    
    test_count=$((test_count + 1))
    test_output="$OUTPUT_DIR/${meeting_name}_output"
    mkdir -p "$test_output"
    
    # Test 1: Legacy flow (baseline)
    echo "  → Running legacy flow..." | tee -a "$LOG_FILE"
    if python3 "$SCRIPT" \
        --meeting-folder "$meeting_path" \
        --output-dir "$test_output/legacy" \
        --dry-run \
        > "$test_output/legacy.log" 2>&1; then
        echo "  ✓ Legacy flow: PASS" | tee -a "$LOG_FILE"
    else
        echo "  ⚠ Legacy flow: FAIL (see ${meeting_name}_output/legacy.log)" | tee -a "$LOG_FILE"
    fi
    
    # Test 2: Content Library flow
    echo "  → Running Content Library flow..." | tee -a "$LOG_FILE"
    if python3 "$SCRIPT" \
        --meeting-folder "$meeting_path" \
        --output-dir "$test_output/content_library" \
        --use-content-library \
        --dry-run \
        > "$test_output/content_library.log" 2>&1; then
        echo "  ✓ Content Library flow: PASS" | tee -a "$LOG_FILE"
        success_count=$((success_count + 1))
    else
        echo "  ⚠ Content Library flow: FAIL (see ${meeting_name}_output/content_library.log)" | tee -a "$LOG_FILE"
        fail_count=$((fail_count + 1))
    fi
    
    # Extract key metrics
    if [ -f "$test_output/content_library.log" ]; then
        echo "  → Extracting metrics..." | tee -a "$LOG_FILE"
        grep -E "(resources_explicit|resources_suggested|eloquent_lines|✓|❌)" "$test_output/content_library.log" 2>/dev/null | head -10 >> "$LOG_FILE" || true
    fi
    
    echo "" | tee -a "$LOG_FILE"
done

echo "==================================" | tee -a "$LOG_FILE"
echo "Test Results Summary" | tee -a "$LOG_FILE"
echo "==================================" | tee -a "$LOG_FILE"
echo "Total Meetings Tested: $test_count" | tee -a "$LOG_FILE"
echo "Successful: $success_count" | tee -a "$LOG_FILE"
echo "Failed: $fail_count" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Full logs: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "==================================" | tee -a "$LOG_FILE"

exit 0
