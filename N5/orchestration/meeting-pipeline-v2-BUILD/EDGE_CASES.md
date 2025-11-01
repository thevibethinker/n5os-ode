# Meeting Pipeline V2 - Edge Case Handling

Convention: Earlier meeting always wins (is first)

## Edge Case 1: Duplicate Detection (Automated)

System: duplicate_detector_v2.py

Convention-Based Logic:
1. When duplicate detected, compare timestamps
2. Earlier meeting = first (wins)
3. Later meeting = second (should merge)

Auto Actions:
- If processing second → SKIP + auto-merge after
- If processing first → Continue, flag other for merge

## Edge Case 2: Manual Meeting Merge

System: merge_meetings_v2.py

Convention: _2 Suffix for Second Meeting Blocks

Usage:
  python3 merge_meetings_v2.py meeting-A meeting-B --dry-run

Block Naming:
  First meeting blocks: meeting_B01, meeting_B02, meeting_B08
  Second meeting blocks become: meeting_B01_2, meeting_B02_2, meeting_B08_2

Result: First meeting has TWO versions of each block (original + _2)

Why This Works:
1. No ambiguity (timestamp determines order)
2. No loss (both block sets preserved)
3. Human readable (_2 is obvious)
4. Query friendly (filter by suffix)
5. Reversible (extract _2 blocks if needed)

Created: 2025-11-01 22:31 ET
