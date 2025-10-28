#!/bin/bash
cd /home/workspace

meetings=(
    "2025-09-23_external-stephanie"
    "2025-09-22_external-mihir-makwana"
    "2025-09-22_external-heather-wixson"
    "2025-09-22_external-giovanna-ventola_164439"
    "2025-09-22_external-giovanna-ventola_164409"
    "2025-09-22_external-giovanna-ventola"
    "2025-09-22_external-ayush-jain"
    "2025-09-21_external-unknown"
    "2025-09-19_external-shujaat-x-logan"
    "2025-09-19_external-david-x-careerspan_180755"
)

echo "Processing 10 meetings for GTM aggregation..."
for meeting in "${meetings[@]}"; do
    echo ""
    echo "========================================" 
    echo "Processing: $meeting"
    echo "========================================"
    python3 N5/scripts/aggregate_b31_insights.py --meeting-id "$meeting"
    if [ $? -eq 0 ]; then
        echo "✓ Successfully processed $meeting"
    else
        echo "✗ Failed to process $meeting"
    fi
done

echo ""
echo "Done! Check aggregated_insights_GTM.md for results."
