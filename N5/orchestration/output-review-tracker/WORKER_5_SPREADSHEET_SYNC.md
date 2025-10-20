# Worker 5: Spreadsheet Sync

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Task ID:** W5-SPREADSHEET-SYNC  
**Estimated Time:** 30 minutes  
**Dependencies:** Worker 2 (review_manager.py must work)

---

## Mission

Build bidirectional sync between JSONL (source of truth) and spreadsheet view. Users can edit status, sentiment, and tags in spreadsheet; sync pushes changes back to JSONL.

---

## Context

V requested hybrid storage: JSONL as SSOT + companion spreadsheet for quick scanning/editing. Spreadsheet edits are limited to: status, sentiment, tags (per V's decision). All other fields are read-only in spreadsheet.

---

## Deliverable

**File:** `N5/scripts/review_sync.py`

### Requirements

1. **Sync JSONL → Spreadsheet** (rebuild spreadsheet from JSONL)
2. **Sync Spreadsheet → JSONL** (detect edits, validate, update JSONL)
3. **Editable columns:** status, sentiment, tags only
4. **Read-only columns:** ID, type, reference, title, provenance, created date, comment count
5. **Validation:** Ensure status/sentiment values are valid before syncing back
6. **Logging:** Clear output showing what changed
7. **Dry-run mode:** Preview changes without writing

---

## Code Template

```python
#!/usr/bin/env python3
"""
Output Review Spreadsheet Sync

Bidirectional sync between output_reviews.jsonl (SSOT) and 
output_reviews.sheet.json (spreadsheet view).

Usage:
    python3 N5/scripts/review_sync.py jsonl-to-sheet  # Rebuild sheet from JSONL
    python3 N5/scripts/review_sync.py sheet-to-jsonl  # Apply sheet edits to JSONL
    python3 N5/scripts/review_sync.py --dry-run sheet-to-jsonl  # Preview changes
"""

import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
REVIEWS_JSONL = Path("/home/workspace/Lists/output_reviews.jsonl")
REVIEWS_SHEET = Path("/home/workspace/Lists/output_reviews.sheet.json")

# Valid enums for validation
VALID_STATUSES = ["pending", "in_review", "approved", "issue", "training", "archived"]
VALID_SENTIMENTS = ["excellent", "good", "acceptable", "issue", ""]

# Column mapping (0-indexed positions in spreadsheet data array)
COL_ID = 0
COL_STATUS = 1
COL_SENTIMENT = 2
COL_TYPE = 3
COL_TAGS = 4
COL_REFERENCE = 5
COL_TITLE = 6
COL_CONVERSATION = 7
COL_THREAD = 8
COL_CREATED = 9
COL_COMMENTS = 10


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL, skipping comment lines."""
    entries = []
    if not path.exists():
        return entries
    
    with path.open('r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                entries.append(json.loads(line))
    
    return entries


def load_sheet(path: Path) -> Dict[str, Any]:
    """Load spreadsheet JSON."""
    if not path.exists():
        return {"tabs": True, "toolbar": True, "worksheets": [{"worksheetName": "Output Reviews", "minDimensions": [11, 10], "columns": [], "data": []}]}
    
    with path.open('r') as f:
        return json.load(f)


def save_sheet(path: Path, sheet: Dict[str, Any], dry_run: bool = False):
    """Save spreadsheet JSON."""
    if dry_run:
        logger.info(f"[DRY RUN] Would write {len(sheet['worksheets'][0]['data'])} rows to {path}")
        return
    
    with path.open('w') as f:
        json.dump(sheet, f, indent=2)
    
    logger.info(f"✓ Wrote {len(sheet['worksheets'][0]['data'])} rows to {path}")


def save_jsonl(path: Path, entries: List[Dict[str, Any]], dry_run: bool = False):
    """Save JSONL with header."""
    if dry_run:
        logger.info(f"[DRY RUN] Would write {len(entries)} entries to {path}")
        return
    
    with path.open('w') as f:
        f.write("# N5 Output Reviews Registry (JSONL)\n")
        f.write("# Schema: file N5/schemas/output-review.schema.json\n")
        f.write("# Each line after this header is a JSON object representing one output review entry\n")
        f.write("# Format: {\"id\": \"out_XXXXXXXXXXXX\", \"created_at\": \"...\", \"title\": \"...\", ...}\n")
        f.write("# Do not edit manually - use: n5 review add|status|comment commands\n")
        
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    logger.info(f"✓ Wrote {len(entries)} entries to {path}")


def jsonl_to_sheet(dry_run: bool = False) -> int:
    """Rebuild spreadsheet from JSONL (SSOT)."""
    logger.info("Syncing JSONL → Spreadsheet...")
    
    try:
        # Load JSONL
        reviews = load_jsonl(REVIEWS_JSONL)
        logger.info(f"Loaded {len(reviews)} reviews from JSONL")
        
        # Load sheet structure
        sheet = load_sheet(REVIEWS_SHEET)
        
        # Build data rows
        rows = []
        for review in reviews:
            row = [
                review['id'],                                          # COL_ID
                review['review']['status'],                           # COL_STATUS
                review['review'].get('sentiment') or '',              # COL_SENTIMENT
                review['type'],                                       # COL_TYPE
                ','.join(review.get('tags', [])),                     # COL_TAGS
                review['reference'],                                  # COL_REFERENCE
                review['title'],                                      # COL_TITLE
                review['provenance']['conversation_id'],              # COL_CONVERSATION
                review['provenance'].get('thread_name') or '',        # COL_THREAD
                review['created_at'],                                 # COL_CREATED
                review.get('comment_count', 0)                        # COL_COMMENTS
            ]
            rows.append(row)
        
        # Update sheet
        sheet['worksheets'][0]['data'] = rows
        
        # Save
        save_sheet(REVIEWS_SHEET, sheet, dry_run=dry_run)
        
        logger.info(f"✓ Synced {len(rows)} rows to spreadsheet")
        return 0
    
    except Exception as e:
        logger.error(f"Failed to sync JSONL → Sheet: {e}", exc_info=True)
        return 1


def sheet_to_jsonl(dry_run: bool = False) -> int:
    """Apply spreadsheet edits (status, sentiment, tags) back to JSONL."""
    logger.info("Syncing Spreadsheet → JSONL...")
    
    try:
        # Load both
        reviews = load_jsonl(REVIEWS_JSONL)
        sheet = load_sheet(REVIEWS_SHEET)
        
        # Build lookup by ID
        review_map = {r['id']: r for r in reviews}
        
        # Track changes
        changes = []
        
        # Process each sheet row
        sheet_rows = sheet['worksheets'][0]['data']
        logger.info(f"Processing {len(sheet_rows)} spreadsheet rows...")
        
        for row in sheet_rows:
            output_id = row[COL_ID]
            
            if output_id not in review_map:
                logger.warning(f"Skipping unknown ID in spreadsheet: {output_id}")
                continue
            
            review = review_map[output_id]
            changed = False
            change_desc = []
            
            # Check status
            new_status = row[COL_STATUS].strip()
            if new_status and new_status != review['review']['status']:
                if new_status not in VALID_STATUSES:
                    logger.error(f"Invalid status '{new_status}' for {output_id}, skipping")
                    continue
                
                old = review['review']['status']
                review['review']['status'] = new_status
                review['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                
                # Set archived_at if moving to archived
                if new_status == 'archived' and not review.get('archived_at'):
                    review['archived_at'] = review['updated_at']
                
                change_desc.append(f"status: {old} → {new_status}")
                changed = True
            
            # Check sentiment
            new_sentiment = row[COL_SENTIMENT].strip()
            old_sentiment = review['review'].get('sentiment') or ''
            
            if new_sentiment != old_sentiment:
                if new_sentiment and new_sentiment not in VALID_SENTIMENTS:
                    logger.error(f"Invalid sentiment '{new_sentiment}' for {output_id}, skipping")
                    continue
                
                review['review']['sentiment'] = new_sentiment if new_sentiment else None
                review['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                change_desc.append(f"sentiment: {old_sentiment or 'none'} → {new_sentiment or 'none'}")
                changed = True
            
            # Check tags
            new_tags_str = row[COL_TAGS].strip()
            new_tags = [t.strip() for t in new_tags_str.split(',') if t.strip()] if new_tags_str else []
            old_tags = review.get('tags', [])
            
            if set(new_tags) != set(old_tags):
                review['tags'] = new_tags
                review['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                change_desc.append(f"tags: {old_tags} → {new_tags}")
                changed = True
            
            if changed:
                changes.append({
                    'id': output_id,
                    'changes': change_desc
                })
        
        # Report changes
        if not changes:
            logger.info("No changes detected in spreadsheet")
            return 0
        
        logger.info(f"Detected {len(changes)} changed review(s):")
        for change in changes:
            logger.info(f"  {change['id']}: {', '.join(change['changes'])}")
        
        # Save updated JSONL
        save_jsonl(REVIEWS_JSONL, reviews, dry_run=dry_run)
        
        # Rebuild spreadsheet to ensure consistency
        if not dry_run:
            logger.info("Rebuilding spreadsheet from updated JSONL...")
            jsonl_to_sheet(dry_run=False)
        
        logger.info(f"✓ Applied {len(changes)} changes from spreadsheet")
        return 0
    
    except Exception as e:
        logger.error(f"Failed to sync Sheet → JSONL: {e}", exc_info=True)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Sync between output_reviews.jsonl and output_reviews.sheet.json"
    )
    parser.add_argument(
        "direction",
        choices=["jsonl-to-sheet", "sheet-to-jsonl"],
        help="Sync direction"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing"
    )
    
    args = parser.parse_args()
    
    if args.direction == "jsonl-to-sheet":
        return jsonl_to_sheet(dry_run=args.dry_run)
    else:
        return sheet_to_jsonl(dry_run=args.dry_run)


if __name__ == "__main__":
    exit(main())
```

---

## Success Criteria

- ✅ JSONL → Sheet sync rebuilds spreadsheet correctly
- ✅ Sheet → JSONL sync detects and applies edits
- ✅ Only status, sentiment, tags are editable
- ✅ Invalid values are rejected with clear errors
- ✅ Timestamps updated on changes
- ✅ archived_at set when status changes to archived
- ✅ Dry-run mode works
- ✅ Clear logging of all changes

---

## Testing

```bash
# Test JSONL → Sheet sync
python3 N5/scripts/review_sync.py jsonl-to-sheet --dry-run
python3 N5/scripts/review_sync.py jsonl-to-sheet

# Verify spreadsheet has data
cat Lists/output_reviews.sheet.json | jq '.worksheets[0].data | length'

# Manually edit spreadsheet (change a status or sentiment)

# Test Sheet → JSONL sync
python3 N5/scripts/review_sync.py sheet-to-jsonl --dry-run
python3 N5/scripts/review_sync.py sheet-to-jsonl

# Verify changes applied
cat Lists/output_reviews.jsonl | jq 'select(.id=="out_XXXXXXXXXXXX") | .review.status'

# Test invalid value rejection
# Edit spreadsheet with invalid status "invalid_status"
python3 N5/scripts/review_sync.py sheet-to-jsonl
# Should error and skip that row
```

---

## Integration Test

After completion, test full workflow:

```bash
# 1. Add review via CLI
python3 N5/scripts/review_cli.py add file /tmp/test.md --title "Test" --type file

# 2. Sync to spreadsheet
python3 N5/scripts/review_sync.py jsonl-to-sheet

# 3. Edit status in spreadsheet (open in Zo app)

# 4. Sync back to JSONL
python3 N5/scripts/review_sync.py sheet-to-jsonl

# 5. Verify via CLI
python3 N5/scripts/review_cli.py show <output_id>
```

---

## Report Back

1. Both sync directions work
2. Validation prevents invalid edits
3. Integration test passes
4. System complete and ready for deployment

---

**Orchestrator:** con_YSy4ld4J113LZQ9A  
**Created:** 2025-10-17 21:03 ET
