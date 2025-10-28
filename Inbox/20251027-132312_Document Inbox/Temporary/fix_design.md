# Internal Meeting Processing Fix - Design

## Problem Statement

Meeting requests are routed to subdirectories (`/internal/`, `/failed/`, `/skipped/`, etc.) but the scheduled task only scans the root directory, leaving internal meetings unprocessed.

## Success Criteria

1. All pending internal meetings are processed
2. Scanner handles subdirectories properly
3. No duplicates remain
4. Clear routing logic documented

## Architecture Review

### Current (Broken)
```
/N5/inbox/meeting_requests/
├── *.json (root - scanned by scheduled task ✓)
├── internal/ (NOT scanned ✗)
├── processed/ (archive)
├── failed/ (archive)
├── excluded/ (archive)
└── skipped/ (archive)
```

### Proposed (Fixed)
```
/N5/inbox/meeting_requests/
├── *.json (pending requests - scanned recursively)
├── internal/ (DEPRECATED - move to root)
├── processed/ (archive - success)
├── failed/ (archive - errors)
├── excluded/ (archive - intentionally skipped)
└── skipped/ (archive - not meeting criteria)
```

## Design Decisions

### Option A: Eliminate /internal/ subdirectory
- **Pro**: Simpler structure (P8 - Minimal Context)
- **Pro**: Single scan location (P2 - SSOT)
- **Pro**: No routing logic needed
- **Con**: Loses classification hint in directory structure

### Option B: Make scanner recursive
- **Pro**: Preserves existing routing
- **Pro**: Can add more subdirectories later
- **Con**: More complex scanning logic
- **Con**: Harder to reason about state

**DECISION: Option A** - Eliminate `/internal/` subdirectory, move all pending requests to root. Simpler is better (P8).

## Implementation Plan

### Phase 1: Audit & Document Current State (5 min)
- [x] List all subdirectories
- [x] Count files in each
- [x] Identify duplicates
- [ ] Document what each subdirectory means

### Phase 2: Deduplication (10 min)
- [ ] Find all duplicate meeting_ids across subdirectories
- [ ] Keep newest version in appropriate location
- [ ] Move duplicates to `/failed/` with explanation

### Phase 3: Consolidate Structure (10 min)
- [ ] Move all pending requests from `/internal/` to root
- [ ] Update any scripts that write to `/internal/`
- [ ] Add deprecation notice to `/internal/README.md`

### Phase 4: Reprocess Pending (15 min)
- [ ] Trigger scheduled task or manual process for each pending internal meeting
- [ ] Verify successful processing
- [ ] Move processed requests to `/processed/`

### Phase 5: Documentation (5 min)
- [ ] Document final directory structure
- [ ] Update any relevant scripts/commands
- [ ] Create routing policy document

## Error Handling

**If deduplication fails:**
- Move all conflicts to `/failed/duplicates/`
- Log details to `dedup_errors.jsonl`
- Continue with rest of fix

**If reprocessing fails:**
- Keep failed requests in root with error log
- Don't move to `/failed/` until investigated
- Alert user to manual review needed

## Testing

- [ ] Dry-run all moves
- [ ] Verify no data loss
- [ ] Test scanner finds files in root
- [ ] Verify scheduled task picks up pending requests

## Rollback Plan

**If fix causes issues:**
1. Keep backup of original structure in `/tmp/meeting_requests_backup_YYYYMMDD/`
2. Can restore by copying back
3. Revert scanner changes

## Principle Compliance

- **P0 (Rule-of-Two)**: Only loading this design doc + architectural principles
- **P2 (SSOT)**: Eliminates duplicate locations
- **P5 (Anti-Overwrite)**: Dry-run before moving files
- **P7 (Dry-Run)**: All operations support --dry-run
- **P8 (Minimal Context)**: Simpler directory structure
- **P15 (Complete)**: Will verify ALL internal meetings processed
- **P18 (State Verification)**: Check files moved successfully
- **P19 (Error Handling)**: Explicit error paths defined
