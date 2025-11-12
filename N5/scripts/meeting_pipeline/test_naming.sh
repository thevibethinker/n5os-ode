#!/bin/bash
# Test the LLM-powered naming on existing meetings

echo "Testing LLM-powered meeting folder naming..."
echo ""

# Test on Allie/Greenlight meeting
echo "=== Test 1: Allie Cialeo / Greenlight ==="
echo "Current name: 2025-09-12_greenlight_recruiting-discovery_sales"
echo "Expected: 2025-09-12_AllieCialeo-greenlight_sales"
echo ""

# Test on a few other meetings
for dir in /home/workspace/Personal/Meetings/2025-*/; do
    if [ -f "$dir/B26_metadata.md" ] && [ -f "$dir/B28_strategic_intelligence.md" ]; then
        current_name=$(basename "$dir")
        echo "Current: $current_name"
        
        # Would invoke LLM here
        # python3 /home/workspace/N5/scripts/meeting_pipeline/generate_folder_name.py \
        #   "$dir/B26_metadata.md" \
        #   "$dir/B28_strategic_intelligence.md"
        
        echo ""
    fi
done

echo "Test complete. To enable LLM naming, update name_normalizer.py to call B99 prompt."
