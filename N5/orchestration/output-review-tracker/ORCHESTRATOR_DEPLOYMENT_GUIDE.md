# Output Review Tracker - Orchestrator Deployment Guide

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Project:** Output Review Tracker  
**Status:** Worker Briefs Ready  
**Date:** 2025-10-17 21:04 ET

---

## 🎯 Quick Start

### For V: Launching Workers

1. **Create 5 new conversations** (one per worker)
2. **In each conversation**, paste the corresponding worker brief
3. **Launch order**: Sequential (Workers 1 → 2 → 3 → 4 → 5)
4. **Check back**: Each worker reports completion status

---

## 📋 Worker Briefs (Ready to Deploy)

All briefs are self-contained with context, requirements, code templates, and success criteria.

### Worker 1: Schemas & Data Infrastructure
**Brief:** `file '/home/.z/workspaces/con_YSy4ld4J113LZQ9A/WORKER_1_SCHEMAS.md'`  
**Time:** 30 min  
**Dependencies:** None  
**Deliverables:**
- output-review.schema.json
- output-review-comment.schema.json
- output_reviews.jsonl (initialized)
- output_reviews_comments.jsonl (initialized)
- output_reviews.sheet.json (initialized)
- Schema validation functions

**Launch:** Open new conversation, paste brief, worker executes.

---

### Worker 2: Core Review Manager
**Brief:** `file '/home/.z/workspaces/con_YSy4ld4J113LZQ9A/WORKER_2_CORE_MANAGER.md'`  
**Time:** 45 min  
**Dependencies:** Worker 1 complete  
**Deliverables:**
- review_manager.py (CRUD operations)
- All JSONL operations tested
- Import-ready module

**Launch:** After Worker 1 reports success.

---

### Worker 3: CLI Interface
**Brief:** `file '/home/.z/workspaces/con_YSy4ld4J113LZQ9A/WORKER_3_CLI.md'`  
**Time:** 40 min  
**Dependencies:** Worker 2 complete  
**Deliverables:**
- review_cli.py
- 6 commands (add, list, show, status, comment, export)
- Help text, error handling, output formatting

**Launch:** After Worker 2 reports success.

---

### Worker 4: Command Registration
**Brief:** `file '/home/.z/workspaces/con_YSy4ld4J113LZQ9A/WORKER_4_COMMANDS.md'`  
**Time:** 20 min  
**Dependencies:** Worker 3 complete  
**Deliverables:**
- 7 entries added to commands.jsonl
- Validation passed
- No duplicates

**Launch:** After Worker 3 reports success.

---

### Worker 5: Spreadsheet Sync
**Brief:** `file '/home/.z/workspaces/con_YSy4ld4J113LZQ9A/WORKER_5_SPREADSHEET_SYNC.md'`  
**Time:** 30 min  
**Dependencies:** Worker 2 complete  
**Deliverables:**
- review_sync.py
- Bidirectional JSONL ↔ Sheet sync
- Validation of editable fields

**Launch:** After Worker 2 reports success (can run parallel with Workers 3-4).

---

## 📊 Dependency Graph

```
Worker 1 (Schemas)
    ↓
Worker 2 (Core Manager)
    ↓ ↓
    ↓ Worker 5 (Spreadsheet Sync)
    ↓
Worker 3 (CLI)
    ↓
Worker 4 (Commands)
```

**Parallel Options:**
- Workers 3 and 5 can run in parallel after Worker 2
- Worker 4 depends on Worker 3 only

---

## ✅ Final Integration Test

After all workers complete, run this test:

```bash
# 1. Add a review
python3 N5/scripts/review_cli.py add file Documents/N5.md --title "N5 System Docs" --type file --tags docs,n5

# 2. List reviews
python3 N5/scripts/review_cli.py list

# 3. Show details
python3 N5/scripts/review_cli.py show <output_id>

# 4. Update status
python3 N5/scripts/review_cli.py status <output_id> in_review --reviewer V

# 5. Add comment
python3 N5/scripts/review_cli.py comment <output_id> --body "Excellent documentation"

# 6. Sync to spreadsheet
python3 N5/scripts/review_sync.py jsonl-to-sheet

# 7. Edit status/sentiment in spreadsheet (via Zo app)

# 8. Sync back to JSONL
python3 N5/scripts/review_sync.py sheet-to-jsonl

# 9. Verify changes
python3 N5/scripts/review_cli.py show <output_id>

# 10. Export excellent outputs
python3 N5/scripts/review_cli.py export --sentiment excellent --output /tmp/training.json
```

**Expected:** All operations succeed, data consistent across JSONL/spreadsheet.

---

## 🎓 System Summary

### What It Does
Tracks generated outputs (files, messages, images, etc.) for quality review with:
- Full provenance (conversation, thread, script, pipeline)
- Workflow states (pending → in_review → approved/issue → training/archived)
- Quality ratings (sentiment + 0-10 dimension scores)
- Threaded comments (max 3 levels)
- Hybrid storage (JSONL + spreadsheet)
- Export for training data

### Key Files After Deployment
```
Lists/
  output_reviews.jsonl              # SSOT
  output_reviews_comments.jsonl     # Comments
  output_reviews.sheet.json         # Spreadsheet view

N5/schemas/
  output-review.schema.json
  output-review-comment.schema.json

N5/scripts/
  review_manager.py                 # Core CRUD
  review_cli.py                     # User commands
  review_sync.py                    # JSONL ↔ Sheet sync

N5/config/
  commands.jsonl                    # Updated with 7 review commands
```

### Usage Patterns

**Add output for review:**
```bash
n5 review add file path/to/output.md --title "Description" --tags topic,type
```

**Filter and review:**
```bash
n5 review list --status pending
n5 review show <id> --with-comments
n5 review status <id> in_review
```

**Rate quality:**
```bash
n5 review sentiment <id> excellent --score tone=9 --score completeness=10
```

**Comment:**
```bash
n5 review comment <id> --body "Great intro section" --context "lines 1-20"
```

**Export for training:**
```bash
n5 review export --sentiment excellent --output training-data.json
```

**Spreadsheet workflow:**
1. `n5 review sync jsonl-to-sheet` - Rebuild spreadsheet
2. Edit status/sentiment/tags in Zo app
3. `n5 review sync sheet-to-jsonl` - Apply changes

---

## 🔧 Troubleshooting

**Worker fails:**
- Check dependencies completed
- Review error logs
- Re-run with corrected approach

**Integration test fails:**
- Verify all 5 workers completed
- Check file permissions
- Validate JSONL syntax

**Sync issues:**
- Ensure JSONL is valid (no syntax errors)
- Check spreadsheet column order
- Run with --dry-run first

---

## 📝 Design Decisions (Locked In)

Per V's approval:
1. ✅ Archive date separate from updated_at
2. ✅ No resolver tracking beyond reviewed_by
3. ✅ Max 3 comment thread levels
4. ✅ JSON export only (no CSV)
5. ✅ Spreadsheet edits: status, sentiment, tags only

---

## 🚀 Launch Checklist

- [ ] Worker 1: Schemas created
- [ ] Worker 2: Core manager tested
- [ ] Worker 3: CLI commands work
- [ ] Worker 4: Commands registered
- [ ] Worker 5: Sync bidirectional
- [ ] Integration test passes
- [ ] Documentation updated
- [ ] System ready for production use

---

**Orchestrator Contact:** con_YSy4ld4J113LZQ9A  
**Ready to Deploy:** Yes  
**Created:** 2025-10-17 21:04 ET
