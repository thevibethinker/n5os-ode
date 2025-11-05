# BUILD WORKER 2: Core Workflows

Build Orchestrator: con_L3ITnGAwWvfxEKz3
Task: W2-WORKFLOWS
Time: 40-50 minutes
Depends On: Worker 1 Complete

## Mission
Implement 8 core workflows for content processing and management.

## Context Files (MUST READ)
- /home/.z/workspaces/con_L3ITnGAwWvfxEKz3/media_documents_architecture_v2.md (Section 5 - Workflows)
- WORKER_1_COMPLETION_REPORT.md (database status)

## Deliverables

All scripts in: /home/workspace/N5/scripts/media_documents/

### 1. process_content.py
Full content processing pipeline:
- Input: content_item_id OR url/file
- Steps: Capture → Read → Summarize (AI) → Extract key insights (AI) → Tag taxonomy → Set status
- Output: Updated content_item with summary, insights, tags

### 2. curate_content.py
V's reflection and curation workflow:
- Query ready_for_review items
- Interactive prompt for V's reflection
- Update importance_rating, v_reflection, action_items
- Set status='curated'

### 3. internalize_content.py
Move curated content into Knowledge/:
- Query high-importance curated items
- Determine Knowledge/ subdirectory
- Create/update knowledge file with bidirectional link
- Update internalized_to field
- Set status='internalized'

### 4. generate_weekly_review.py
Generate weekly review report:
- Query this week's activity
- Group by: Inbox, Ready for Review, Curated, Action Items
- Export markdown report
- Send via email (use send_email_to_user tool)

### 5. archive_content.py
Archive old/low-priority content:
- Query: last_accessed > 180 days AND importance < 5
- Create timestamped archive: Archives/media_docs_YYYY-MM-DD.tar.gz
- Create manifest file alongside: Archives/media_docs_YYYY-MM-DD_manifest.json
- Update status='archived'
- Preserve database records

### 6. link_to_meeting.py
Link content to meetings:
- Input: content_id, meeting_id
- Create meeting_references entry
- Update both records

### 7. search_content.py
Rich search interface:
- Full-text search across title, summary, insights
- Filter by taxonomy tags, status, importance
- Sort by relevance, date, importance
- Output: formatted results

### 8. export_content.py
Export content for external use:
- Format: JSON, CSV, Markdown
- Filters: by status, tags, date range
- Include: metadata + content

## Success Criteria
- All 8 workflows functional
- process_content pipeline works end-to-end
- curate_content tested with 1 item
- Weekly review generates valid report
- Archive creates manifest correctly (outside archive)
- All workflows have --dry-run (P7)
- Error handling (P11, P19)

## Testing Protocol
# Process test content
python3 /home/workspace/N5/scripts/media_documents/process_content.py --id 1

# Curate (interactive)
python3 /home/workspace/N5/scripts/media_documents/curate_content.py

# Generate weekly review
python3 /home/workspace/N5/scripts/media_documents/generate_weekly_review.py

# Test archive (dry-run)
python3 /home/workspace/N5/scripts/media_documents/archive_content.py --dry-run

# Search test
python3 /home/workspace/N5/scripts/media_documents/search_content.py --query "strategy"

## Handoff
Create WORKER_2_COMPLETION_REPORT.md with workflow test results.

## Critical Principles
- P0.1: Use AI (me) for summarization and insight extraction
- P7: All scripts --dry-run
- P15: Report "X/Y (Z%)"
- P21: Document AI prompt patterns used

Created: 2025-11-03 21:00 ET
