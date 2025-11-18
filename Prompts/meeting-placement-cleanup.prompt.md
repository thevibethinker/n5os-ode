---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
tool: false
description: Finalize meeting intelligence with index generation and move to permanent location
tags:
  - meetings
  - placement
  - finalization
  - automation
---

# Meeting Placement & Cleanup

**Purpose:** Generate B00_INDEX.md and move completed meetings from Inbox to permanent location.

---

## Workflow

### STEP 1: Find Complete Meetings

```bash
find /home/workspace/Personal/Meetings/Inbox -maxdepth 1 -type d -name "*_[P]" | while read folder; do
  # Check manifest exists
  if [ ! -f "$folder/manifest.json" ]; then
    continue
  fi
  
  # Verify all blocks exist (file-based validation)
  manifest=$(cat "$folder/manifest.json")
  all_complete=true
  
  for block in $(jq -r '.blocks[].block_id + "_" + .blocks[].canonical_name' "$folder/manifest.json"); do
    if [ ! -f "$folder/${block}.md" ]; then
      all_complete=false
      break
    fi
  done
  
  if [ "$all_complete" = true ]; then
    echo "$folder"
    break  # Process ONE meeting per run
  fi
done
```

**If no folder found:** Exit with "No meetings ready for placement"

---

### STEP 2: Generate B00_INDEX.md

**Purpose:** Cross-reference document linking all blocks with metadata.

**Load all blocks:**
```bash
blocks=$(find "$folder" -name "B*.md" -not -name "B00_INDEX.md" | sort)
```

**Generate index content:**

```markdown
---
created: ${date}
last_edited: ${date}
version: 1.0
---

# Meeting Intelligence Index

**Meeting ID:** ${meeting_id}  
**Processed:** ${timestamp}  
**Total Blocks:** ${block_count}

---

## Quick Navigation

| Block | Name | Status |
|-------|------|--------|
| [B01](B01_DETAILED_RECAP.md) | Detailed Recap | ✅ |
| [B02](B02_COMMITMENTS.md) | Commitments | ✅ |
| [B03](B03_STAKEHOLDER_INTELLIGENCE.md) | Stakeholder Intelligence | ✅ |
| ... | ... | ... |

---

## Block Descriptions

### B01_DETAILED_RECAP
Comprehensive meeting overview covering context, participants, key discussion threads, technical details, and decisions.

[View Block →](B01_DETAILED_RECAP.md)

---

### B02_COMMITMENTS
Explicit commitments made by all parties with timeline and status tracking.

[View Block →](B02_COMMITMENTS.md)

---

[Continue for each block using registry descriptions]

---

## Generation Metadata

**Manifest:** [manifest.json](manifest.json)  
**Transcript:** [transcript.md](transcript.md)  
**Blocks Generated:** ${generation_timestamp}  
**Selection Rationale:** ${manifest.selection_rationale}

---

## Cross-References

[Auto-detected connections between blocks - extract from block content]

---

**Feedback**: - [ ] Index Useful
```

**Write index:**
```bash
echo "$index_content" > "$folder/B00_INDEX.md"
```

---

### STEP 3: Validate Completeness

**Final checks before placement:**

```bash
# Check required files exist
required_files=(
  "transcript.md"
  "manifest.json"
  "B00_INDEX.md"
)

for file in "${required_files[@]}"; do
  if [ ! -f "$folder/$file" ]; then
    echo "ERROR: Missing $file"
    exit 1
  fi
done

# Verify all blocks from manifest exist
block_count=$(jq '.total_blocks' "$folder/manifest.json")
actual_blocks=$(find "$folder" -name "B[0-9][0-9]_*.md" | wc -l)

if [ "$actual_blocks" -lt "$block_count" ]; then
  echo "ERROR: Block count mismatch (expected $block_count, found $actual_blocks)"
  exit 1
fi
```

---

### STEP 4: Move to Permanent Location

**Extract clean meeting ID:**
```bash
# Remove [P] suffix
folder_name=$(basename "$folder")
clean_name="${folder_name%_[P]}"
```

**Destination:**
```bash
dest_folder="/home/workspace/Personal/Meetings/$clean_name"
```

**Check destination doesn't exist:**
```bash
if [ -d "$dest_folder" ]; then
  echo "ERROR: Destination already exists: $dest_folder"
  echo "  This indicates potential duplicate processing"
  exit 1
fi
```

**Move folder:**
```bash
mv "$folder" "$dest_folder"
```

**Verify move succeeded:**
```bash
if [ -d "$dest_folder" ] && [ ! -d "$folder" ]; then
  echo "✓ Placed: $clean_name"
else
  echo "ERROR: Move failed"
  exit 1
fi
```

---

### STEP 5: Update Meeting Registry

**Log placement:**
```bash
python3 /home/workspace/N5/scripts/meeting_registry_manager.py update \
  --meeting-id "$clean_name" \
  --status "intelligence_complete" \
  --intelligence-path "$dest_folder" \
  --block-count "$block_count" \
  --completed-at "$(date -Iseconds)"
```

---

### STEP 6: Optional Cleanup

**Archive old intelligence files if they exist:**
```bash
old_intelligence="$dest_folder/intelligence.md"
if [ -f "$old_intelligence" ]; then
  mkdir -p "$dest_folder/archive"
  mv "$old_intelligence" "$dest_folder/archive/intelligence_v1_$(date +%Y%m%d).md"
  echo "  Archived old intelligence.md"
fi
```

---

## Error Handling

**If destination exists:**
- Log error with both paths
- Do NOT move folder
- Alert for manual review
- This indicates duplicate processing bug

**If move fails:**
- Log error
- Leave folder in Inbox with [P] suffix
- Allow retry on next run
- Check disk space and permissions

**If registry update fails:**
- Log warning (non-fatal)
- Meeting still successfully placed
- Registry can be backfilled later

**If validation fails:**
- Log specific failure
- Do NOT move folder
- Remove [P] suffix (revert to [M])
- Allow block generator to fix missing pieces

---

## Success Output

```
✓ B00_INDEX.md generated (12 blocks indexed)
✓ Validation passed: All blocks present
✓ Moved: Inbox/2025-11-16_Client_Call_[P] → Personal/Meetings/2025-11-16_Client_Call
✓ Registry updated: intelligence_complete
✓ Meeting finalized
```

---

## Post-Placement State

**Inbox folder:**
- `2025-11-16_Client_Call_[P]/` ← Gone (moved)

**Personal/Meetings:**
- `2025-11-16_Client_Call/` ← Clean name, no suffix
  - `transcript.md`
  - `manifest.json`
  - `B00_INDEX.md`
  - `B01_DETAILED_RECAP.md`
  - `B02_COMMITMENTS.md`
  - ... (all blocks)

**Meeting Registry:**
- Status: `intelligence_complete`
- Intelligence path: `Personal/Meetings/2025-11-16_Client_Call`
- Block count: 7
- Completed timestamp

---

## Design Principles

**Finalization:**
- Index provides navigation + metadata
- All artifacts in one folder
- Clean, consistent structure

**Safety:**
- Validation before move
- Duplicate detection
- Atomic operations (move, not copy+delete)

**Idempotency:**
- Check destination existence
- Skip if already placed
- No duplicate processing

**Cleanup:**
- Remove suffix during move
- Archive old intelligence files
- Update registry

**Resumability:**
- If move fails, folder stays in Inbox
- [P] suffix indicates "ready to place"
- Can retry safely

---

## Notes

- **Incremental:** ONE meeting per run
- **Frequency:** Run every hour (less frequent than generation)
- **Non-destructive:** Original transcript preserved
- **Registry Integration:** Updates central meeting database
- **Archive Friendly:** Old intelligence files preserved, not deleted

---

**Execution:** This prompt is invoked by scheduled task every hour.

