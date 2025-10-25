# Demo Hygiene Plan (Dry-Run)

Artifacts (depth≤2 audit):
- file '/home/.z/workspaces/con_VFOB1AJnLjWB4eC6/dirs_depth2.txt'
- file '/home/.z/workspaces/con_VFOB1AJnLjWB4eC6/files_depth2.txt'
- file '/home/.z/workspaces/con_VFOB1AJnLjWB4eC6/dir_basename_counts.txt'
- file '/home/.z/workspaces/con_VFOB1AJnLjWB4eC6/file_basename_counts.txt'
- file '/home/.z/workspaces/con_VFOB1AJnLjWB4eC6/pattern_*_dirs.txt'
- file '/home/.z/workspaces/con_VFOB1AJnLjWB4eC6/sloppy_names.txt'
- file '/home/.z/workspaces/con_VFOB1AJnLjWB4eC6/cleanup_plan.json'

Immediate dry-run moves (pending approval):
- Root resumes → Documents/Resumes
- Root logs → N5/logs
- Exports/ → N5/exports/legacy_2025-10-24/

Deferred (post-demo):
- Merge projects → Projects (case normalization, content diff)
- Normalize Logs/logs, other case duplicates
- Backfill anchors into policy and path guard

Rollback: reverse cleanup_plan.json moves.
