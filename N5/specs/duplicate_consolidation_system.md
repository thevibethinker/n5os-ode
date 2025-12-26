# Duplicate Consolidation System v1.0

Date: 2025-11-03
Status: Ready for Builder

## Problem
11+ duplicate folder sets in Inbox (timestamped copies from Root Clearinghouse)

## Solution
Weekly sweep: Detect 																																																																																	

## Implementation

Script: N5/scripts/maintenance/consolidate_duplicates.py
Config: N5/config/canonical_locations.json
Schedule: Weekly (Monday 7AM ET)

## Behavior

1. Detection: Scan Inbox for YYYYMMDD-HHMMSS_basename pattern
2. Consolidation: Keep latest timestamp only (Latest Wins)
3. Archive: Zip old copies to N5/data/consolidation_archives/YYYY-MM-DD/
4. Move: Send to canonical location per config mapping

## Canonical Mappings

Prompts  Prompts/
Sites  Sites/
Deliverables  Records/deliverables/
Meetings  Personal/Meetings/
marvin_jobs_data  projects/marvin/data/
Unknown  SKIP

## Safety

- Dry-run mode (--dry-run)
- Skip if destination exists
- Log all operations
- Archive includes manifest.json

## Acceptance Criteria

✅ Finds all duplicates
✅ Keeps latest version only
✅ Moves to canonical locations
✅ Archives old copies with metadata
✅ Dry-run preview works
✅ Weekly automation

See file '/home/.z/workspaces/con_vZXuYopL1ViXiSRW/duplicate_consolidation_spec.md' for detailed spec.

Ready for Builder implementation.

