# BUILD WORKER 1: Foundation & Database

Build Orchestrator: con_L3ITnGAwWvfxEKz3
Task: W1-FOUNDATION
Time: 30-40 minutes

## Mission
Create database foundation, taxonomy system, and core tracking infrastructure.

## Context Files (MUST READ)
- /home/.z/workspaces/con_L3ITnGAwWvfxEKz3/media_documents_architecture_v2.md
- /home/.z/workspaces/con_L3ITnGAwWvfxEKz3/V_DECISIONS_RECORD.md

## Deliverables

1. Database: /home/workspace/N5/data/media_documents.db
   - content_items (35 fields, 8 indexes - see arch Section 3)
   - taxonomy_tags, content_tags, cross_references, access_log

2. Scripts: /home/workspace/N5/scripts/media_documents/
   - create_database.py (init with full schema)
   - taxonomy_manager.py (manage 50 core topics from arch Section 4)
   - add_content.py (CLI for ad hoc content addition)
   - query_content.py (query interface)
   - migrate_articles.py (migrate existing Articles/)

3. Taxonomy: Load 50 core topics from architecture Section 4
   - Business & Strategy (10)
   - Career & Talent (10)
   - Product & Technology (8)
   - Customer & Community (7)
   - Industry Insights (8)
   - Personal & Meta (7)

## Success Criteria
- Database created with all tables/indexes
- 50 taxonomy topics loaded
- Add/query CLIs work
- Articles/ migrated (preserve originals)
- All scripts have --dry-run mode (P7)
- Error handling everywhere (P11, P19)

## Testing
python3 /home/workspace/N5/scripts/media_documents/create_database.py
sqlite3 /home/workspace/N5/data/media_documents.db ".schema"
python3 /home/workspace/N5/scripts/media_documents/taxonomy_manager.py load
python3 /home/workspace/N5/scripts/media_documents/migrate_articles.py --dry-run
python3 /home/workspace/N5/scripts/media_documents/query_content.py --status inbox

## Handoff
Create WORKER_1_COMPLETION_REPORT.md with counts, test results, issues.

## Critical Principles
- P5: Never overwrite Articles/ - preserve originals
- P7: All scripts support --dry-run
- P15: Report "X/Y (Z%)" not "Done"
- P19: try/except everywhere
- P22: Python for database work

Created: 2025-11-03 21:00 ET
