# Session State
Auto-generated | Scheduled Task

## Metadata
- Conversation ID: con_Hg3oewLgGW2DBsMW
- Status: active
- Type: discussion

## Focus
Run the weekly list health check across all JSONL lists, validating schema, identifying stale items (>30 days), detecting duplicates, computing health scores, and logging results.

## Objective
- STEP 1: Use command-first approach; verify any registered command for list health; proceed with the specified weekly maintenance script
- STEP 2: Execute /home/workspace/N5/scripts/maintenance/weekly_list_health.py
- STEP 3: Confirm logs written to N5/logs/maintenance/weekly/ and capture summary counts
- STEP 4: Report list totals, stale/duplicate counts, and average health score

## Tags
#scheduled #lists #health #jsonl #maintenance #automation #n5

## Run Summary
- Lists checked: 16 | Successful: 16 | Avg health: 89.8/100
- Stale items: 14 across 6 lists (notably ideas.jsonl: 4; system-upgrades.jsonl: 4)
- Duplicates: 5 groups across 2 lists (system-upgrades.jsonl: 2; output_reviews.jsonl: 3)
- Schema warnings: index.jsonl, organizations_queue.jsonl, output_reviews.jsonl, output_reviews_comments.jsonl
- Log: file 'N5/logs/maintenance/weekly/lists_2025-10-27.log'
- Updated: 2025-10-26 20:04 ET
