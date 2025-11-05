# BUILD WORKER 4: Review System & Automation

Build Orchestrator: con_L3ITnGAwWvfxEKz3
Task: W4-REVIEW-AUTOMATION
Time: 30-40 minutes
Depends On: Workers 1, 2, & 3 Complete

## Mission
Implement weekly review system and automated internalization workflow.

## Context Files (MUST READ)
- /home/.z/workspaces/con_L3ITnGAwWvfxEKz3/media_documents_architecture_v2.md (Section 8)
- /home/.z/workspaces/con_L3ITnGAwWvfxEKz3/V_DECISIONS_RECORD.md
- All prior WORKER_N_COMPLETION_REPORT.md files

## Deliverables

### 1. Weekly Review Scheduled Task
Create scheduled task that runs every Sunday 9:00 AM ET:

Instruction for agent:
"Generate weekly Media & Documents review report. Query N5/data/media_documents.db for:
1. New items added this week (status='inbox')
2. Items ready for review (status='ready_for_review')
3. Items curated this week (status='curated', updated this week)
4. Action items pending (action_items NOT NULL, status='curated')
5. High-priority unreviewed (importance_rating >= 8, status IN ('inbox','curated'))

Format as markdown report and email to V. Use python3 /home/workspace/N5/scripts/media_documents/generate_weekly_review.py"

Register with: create_scheduled_task tool
RRULE: "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9;BYMINUTE=0"

### 2. Auto-Internalization Workflow
Location: /home/workspace/N5/scripts/media_documents/auto_internalize.py

Logic (per V decision):
- Query: status='curated' AND internalized_to IS NULL
- For each item:
  - Call internalize_content.py
  - Auto-internalize ALL curated content
  - Update status='internalized'

Should be callable from scheduled task OR manually.

### 3. Review Dashboard Script
Location: /home/workspace/N5/scripts/media_documents/review_dashboard.py

Generate interactive review dashboard:
- Current statistics (counts by status)
- Recent activity (last 7 days)
- Top priority items
- Action items summary
- Archive candidates

Output: Terminal-formatted dashboard OR web page (optional)

### 4. Scheduled Task for Auto-Internalization
Create scheduled task that runs every Sunday 9:30 AM ET (after review):

Instruction:
"Auto-internalize all curated content in Media & Documents system. Run: python3 /home/workspace/N5/scripts/media_documents/auto_internalize.py --execute. Report results via email."

RRULE: "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9;BYMINUTE=30"

### 5. Documentation
Location: /home/workspace/N5/docs/media_documents/

Create:
- USER_GUIDE.md - How to use the system (for V)
- WORKFLOWS.md - All workflows documented
- INTEGRATION_POINTS.md - How system connects to other components
- TROUBLESHOOTING.md - Common issues and solutions

## Success Criteria
- Weekly review scheduled task registered and tested
- Auto-internalization workflow functional
- Review dashboard displays correctly
- Auto-internalization scheduled task registered
- Documentation complete and clear
- Test full workflow: add → process → curate → auto-internalize

## Testing Protocol
# Test review generation
python3 /home/workspace/N5/scripts/media_documents/generate_weekly_review.py

# Test auto-internalization (dry-run)
python3 /home/workspace/N5/scripts/media_documents/auto_internalize.py --dry-run

# Test dashboard
python3 /home/workspace/N5/scripts/media_documents/review_dashboard.py

# Verify scheduled tasks
list_scheduled_tasks

# End-to-end test
# 1. Add test content
# 2. Process it
# 3. Curate it (manually)
# 4. Run auto-internalize
# 5. Verify in Knowledge/

## Scheduled Tasks Registration

Task 1 - Weekly Review:
- Name: "Media & Documents Weekly Review"
- RRULE: "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9;BYMINUTE=0"
- Delivery: email

Task 2 - Auto-Internalization:
- Name: "Auto-Internalize Curated Content"  
- RRULE: "FREQ=WEEKLY;BYDAY=SU;BYHOUR=9;BYMINUTE=30"
- Delivery: email

## Handoff to Orchestrator
Create WORKER_4_COMPLETION_REPORT.md with:
- Scheduled task IDs
- Test results
- Documentation locations
- Full system status
- Any issues or recommendations

## Final System Validation
Before completing, validate:
- All 8 workflows operational
- All 4 integrations working
- Database populated and queryable
- Scheduled tasks registered
- Documentation complete
- No P15 violations (everything actually done)

## Critical Principles
- P12: Test scheduled tasks in fresh thread
- P15: Report "X/Y (Z%)" - this is FINAL worker
- P28: Quality here determines user experience

Created: 2025-11-03 21:00 ET
