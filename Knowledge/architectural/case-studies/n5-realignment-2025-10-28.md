# N5 Platonic Ideal Realignment Plan
**Version:** 1.0  
**Created:** 2025-10-28 10:18 EST  
**Strategy:** Extended Minimal + Aggressive with Symlinks  
**Expected Duration:** 3-4 hours (intermittent execution)

---

## Executive Summary

**Current State:**
- N5/ has 42 subdirectories (platonic ideal: 6)
- 3805 total files in N5/
- 233MB of backups scattered across 4 locations
- 72 dated export folders cluttering Inbox/
- 36 scheduled tasks with path dependencies
- Heavy path references: scripts/ (58 refs), prefs/ (34), records/ (38), logs/ (25)

**Target State:**
- N5/ reduced to ~12 "earned" directories
- Single centralized backup archive
- Clean Inbox/ triage area
- Symlink compatibility layer with tracking
- All paths updated, documented, verified

---

## TRAP DOORS (P23 Critical)

### Irreversible Decisions
1. **N5/services/** (166MB): Contains ZoBridge and possibly other running services
   - **TRAP DOOR:** If we move/delete and service is running, could break production
   - **MITIGATION:** Check running user services first, protect active services
   
2. **N5/records/meetings/** (protected): Meeting processing directory
   - **TRAP DOOR:** Has `.n5protected` marker
   - **MITIGATION:** Keep in place or move carefully with protection

3. **Scheduled task path references** (36 tasks)
   - **TRAP DOOR:** Tasks run on schedule, will fail if paths break
   - **MITIGATION:** Create symlinks, test all tasks, document each

4. **Database paths** (conversations.db, system_bulletins.jsonl, etc.)
   - **TRAP DOOR:** Scripts expect these at specific paths
   - **MITIGATION:** Keep data/ intact, only archive old exports

---

## Phase 1: Survey & Protect (30 min)

### 1.1: Check Running Services
```bash
# Check for running user services
curl -s http://localhost:8080/list-services || echo "No services API"

# Check ZoBridge status
ls -la /home/workspace/N5/services/zobridge/
```

### 1.2: Create Pre-Migration Snapshot
```bash
# Full system snapshot via Zo system page (manual)
# Or quick backup:
cd /home/workspace
tar czf /tmp/n5_premigration_$(date +%Y%m%d_%H%M%S).tar.gz N5/ Knowledge/ Lists/ Records/ Documents/N5.md
```

### 1.3: Document Protected Paths
```bash
find /home/workspace -name ".n5protected" -type f > /tmp/protected_paths.txt
```

---

## Phase 2: N5 Directory Rationalization (90 min)

### 2.1: Proposed "Extended Minimal" Structure

**KEEP (Platonic + Earned):**
```
N5/
├── commands/         # [Platonic] Empty now, keep for future
├── config/           # [Platonic] 126KB, 38 files - ESSENTIAL
├── data/             # [Platonic] 6.7MB, DBs and state - ESSENTIAL
├── prefs/            # [Platonic] 646KB, 109 files - ESSENTIAL
├── schemas/          # [Platonic] 67KB, 24 files - ESSENTIAL
├── scripts/          # [Platonic] 5.5MB, 523 files - ESSENTIAL
├── logs/             # [Earned] 26.6MB, 2896 files - thread exports, audit trails
├── templates/        # [Earned] 5KB, session templates
├── workflows/        # [Earned] 10KB, reusable workflows
├── backups/          # [Earned] 894KB, system backups (keep recent only)
├── services/         # [Earned] 166MB, ZoBridge (if active)
└── lib/              # [Earned] 14KB, shared Python modules
```

**ARCHIVE (Move to .n5_archive_{timestamp}):**
```
N5_ARCHIVE/
├── Documentation/    # 6KB - merge to Documents/System/
├── Documents/        # 32KB - merge to Documents/System/
├── docs/             # 18KB - merge to Documents/System/
├── digests/          # 85KB - old meeting prep digests
├── exemplars/        # 2KB - example files
├── exports/          # 1.8MB - old system exports
├── inbox/            # 9.9MB - deprecated, use Records/
├── instructions/     # 2.5KB - one-off instructions
├── intelligence/     # 16KB - single JSON, move to data/
├── knowledge/        # 118KB - merge to /workspace/Knowledge/
├── lessons/          # 64KB - keep or merge to Knowledge/
├── lists/            # 32KB - deprecated, use /workspace/Lists/
├── maintenance/      # 20KB - old maintenance docs
├── modules/          # 5KB - deprecated modules
├── orchestration/    # 417KB - old orchestration logic
├── records/          # 47MB - merge to /workspace/Records/
├── registries/       # Empty - delete
├── registry/         # 0.5KB - minimal, merge to data/
├── runtime/          # 152KB - execution logs, archive old
├── sessions/         # 27KB - session metadata, merge to data/
├── specs/            # 16KB - old specs
├── strategy-evolution/ # 3KB - single JSON, move to data/
├── style_guides/     # 2KB - merge to Knowledge/
├── telemetry/        # 42KB - merge to data/ or logs/
├── test/             # 6KB - test artifacts
└── tests/            # 247KB - keep tests/ if active, else archive
```

### 2.2: Decision Matrix

| Directory | Size | Files | Keep? | Rationale |
|-----------|------|-------|-------|-----------|
| commands | 0 | 0 | ✅ Yes | Platonic, future use |
| config | 126KB | 38 | ✅ Yes | Essential configs |
| data | 6.7MB | 19 | ✅ Yes | DBs, bulletins, state |
| prefs | 646KB | 109 | ✅ Yes | User preferences |
| schemas | 67KB | 24 | ✅ Yes | Validation schemas |
| scripts | 5.5MB | 523 | ✅ Yes | Core automation |
| logs | 26.6MB | 2896 | ✅ Yes | Thread exports, audit trails |
| templates | 5KB | 6 | ✅ Yes | Session templates |
| workflows | 10KB | 2 | ✅ Yes | Reusable workflows |
| backups | 894KB | 62 | ✅ Yes | Recent backups only |
| services | 166MB | 1748 | ⚠️  Maybe | Check if ZoBridge active |
| lib | 14KB | 2 | ✅ Yes | Shared Python modules |
| tests | 247KB | 72 | ⚠️  Maybe | Keep if tests run, else archive |
| **ALL OTHERS** | | | ❌ Archive | See archive list above |

### 2.3: Path Dependency Analysis

**High-Impact Paths (must symlink):**
- `N5/scripts/` - 58 references
- `N5/records/` - 38 references (PROTECTED)
- `N5/prefs/` - 34 references
- `N5/config/` - 40 references
- `N5/logs/` - 25 references
- `N5/inbox/` - 11 references

**Medium-Impact:**
- `N5/sessions/` - 6 references
- `N5/runtime/` - 6 references
- `N5/timeline/` - 7 references

**Resolution:**
1. For `records/` - already at `/workspace/Records/`, create symlink `N5/records` → `/workspace/Records`
2. For `inbox/` - archive N5/inbox/, use `/workspace/Inbox/`
3. For `sessions/`, `runtime/`, `timeline/` - merge to data/, symlink temporarily

---

## Phase 3: Backup Consolidation (30 min)

### 3.1: Current Backup Inventory

| Location | Size | Contents |
|----------|------|----------|
| `.migration_backups/` | 385KB | CRM unification, phase5/6 backups |
| `.n5-ats-backups/` | 735KB | ZoATS history rewrite backup |
| `.n5_backups/` | 232MB | N5 merge backup (10/27) |
| `N5/backups/` | 942KB | System backups (5 subdirs) |

### 3.2: Consolidation Strategy

```bash
# Create archive directory
mkdir -p /home/workspace/.archive_2025-10-28

# Archive old backups
cd /home/workspace
tar czf .archive_2025-10-28/migration_backups.tar.gz .migration_backups/
tar czf .archive_2025-10-28/ats_backups.tar.gz .n5-ats-backups/
tar czf .archive_2025-10-28/n5_backups_20251027.tar.gz .n5_backups/

# Keep N5/backups/ for recent system backups (last 30 days)
find N5/backups/ -type f -mtime +30 -exec tar czf .archive_2025-10-28/n5_old_backups.tar.gz {} +

# Remove archived directories
rm -rf .migration_backups/ .n5-ats-backups/ .n5_backups/

# Update .gitignore if needed
echo ".archive_*/" >> /home/workspace/.gitignore
```

---

## Phase 4: Inbox Cleanup (20 min)

### 4.1: Current State
- 76 total items in Inbox/
- 72 dated export folders (format: `20251027-HHMMSS_*`)
- These are from Oct 27 mass workspace cleanup

### 4.2: Cleanup Strategy

```bash
cd /home/workspace/Inbox

# Archive all dated export folders
mkdir -p /home/workspace/.archive_2025-10-28/inbox_exports
mv 2025* /home/workspace/.archive_2025-10-28/inbox_exports/
tar czf /home/workspace/.archive_2025-10-28/inbox_exports_20251027.tar.gz inbox_exports/
rm -rf /home/workspace/.archive_2025-10-28/inbox_exports/

# Result: Clean Inbox/ for active triage
```

---

## Phase 5: Meetings Consolidation (20 min)

### 5.1: Current State
- `/home/workspace/Meetings/` - Does not exist (checked with ls)
- `/home/workspace/Personal/Meetings/` - 1KB (minimal)
- `/home/workspace/Records/Company/` - 1.3MB
- Scheduled tasks reference `/home/workspace/Records/Company/Meetings/`

### 5.2: Strategy
**Decision:** Keep meetings in Records/Company/Meetings (already correct per N5 flow)
- Personal meetings → Records/Personal/Meetings/ (not split yet)
- Company meetings → Records/Company/Meetings/ (current)
- NO centralization needed - already in correct flow structure

---

## Phase 6: Migration Execution (60 min)

### 6.1: Pre-Flight Checklist
```bash
[ ] System snapshot created
[ ] Protected paths documented
[ ] User services checked
[ ] All scheduled tasks documented
[ ] Migration scripts tested in dry-run mode
```

### 6.2: Execution Script

```python
#!/usr/bin/env python3
"""N5 Realignment Migration Script v1.0"""
import shutil
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
N5 = WORKSPACE / "N5"
ARCHIVE_DIR = WORKSPACE / f".archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
SYMLINK_LOG = ARCHIVE_DIR / "symlinks_created.txt"

KEEP_DIRS = [
    "commands", "config", "data", "prefs", "schemas", "scripts",
    "logs", "templates", "workflows", "backups", "services", "lib"
]

ARCHIVE_DIRS = [
    "Documentation", "Documents", "docs", "digests", "exemplars",
    "exports", "inbox", "instructions", "intelligence", "knowledge",
    "lessons", "lists", "maintenance", "modules", "orchestration",
    "records", "registries", "registry", "runtime", "sessions",
    "specs", "strategy-evolution", "style_guides", "telemetry",
    "test", "tests", "timeline"
]

def main(dry_run=True):
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Starting N5 realignment")
    
    # Create archive directory
    if not dry_run:
        ARCHIVE_DIR.mkdir(exist_ok=True)
        SYMLINK_LOG.touch()
    
    # Phase 1: Archive directories
    archived_count = 0
    for dirname in ARCHIVE_DIRS:
        src = N5 / dirname
        if not src.exists():
            continue
        
        dst = ARCHIVE_DIR / "N5_ARCHIVE" / dirname
        logger.info(f"Archive: {src} -> {dst}")
        
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        archived_count += 1
    
    logger.info(f"Archived {archived_count} directories")
    
    # Phase 2: Create symlinks for high-impact paths
    symlinks = [
        (N5 / "records", WORKSPACE / "Records"),
        (N5 / "lists", WORKSPACE / "Lists"),
        (N5 / "sessions", N5 / "data" / "sessions"),
    ]
    
    for link_path, target_path in symlinks:
        if link_path.exists() and link_path.is_symlink():
            logger.info(f"Symlink exists: {link_path} -> {target_path}")
            continue
        
        logger.info(f"Create symlink: {link_path} -> {target_path}")
        if not dry_run:
            link_path.symlink_to(target_path)
            with SYMLINK_LOG.open("a") as f:
                f.write(f"{link_path} -> {target_path}\n")
    
    # Phase 3: Verify essential directories
    for dirname in KEEP_DIRS:
        path = N5 / dirname
        if not path.exists():
            logger.warning(f"Essential directory missing: {path}")
    
    logger.info(f"✓ {'[DRY RUN] ' if dry_run else ''}Migration complete")
    return 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true", help="Actually execute migration")
    args = parser.parse_args()
    
    exit(main(dry_run=not args.execute))
```

---

## Phase 7: Verification & Testing (45 min)

### 7.1: Verification Checklist

```bash
# Verify N5 structure
ls -1 /home/workspace/N5/
# Expected: 12 directories (keep list)

# Verify symlinks
ls -la /home/workspace/N5/ | grep "^l"

# Verify essential scripts
python3 /home/workspace/N5/scripts/session_state_manager.py --version

# Test scheduled task paths (sample)
python3 /home/workspace/N5/scripts/maintenance/daily_guardian.py --dry-run

# Verify backups archived
du -sh /home/workspace/.archive_*/

# Check N5.md still loads
cat /home/workspace/Documents/N5.md | head -20
```

### 7.2: Scheduled Task Testing

Create test script to verify all 36 scheduled tasks can find their paths:

```python
#!/usr/bin/env python3
"""Test scheduled task path dependencies."""
import json
import subprocess
from pathlib import Path

TASKS = [
    "/home/workspace/N5/scripts/maintenance/daily_guardian.py",
    "/home/workspace/N5/scripts/maintenance/weekly_cleanup.py",
    "/home/workspace/N5/scripts/session_state_manager.py",
    # ... add all from scheduled tasks list
]

for script in TASKS:
    path = Path(script)
    if not path.exists():
        print(f"❌ MISSING: {script}")
    else:
        print(f"✅ EXISTS: {script}")
```

---

## Phase 8: Documentation Update (30 min)

### 8.1: Update N5.md

```markdown
## N5 Structure (Post-Realignment)

N5/ now follows "Extended Minimal" architecture:

**Core (Platonic Ideal):**
- commands/ - Command definitions (reserved)
- config/ - System configuration
- data/ - Databases and persistent state
- prefs/ - User preferences and protocols
- schemas/ - JSON validation schemas
- scripts/ - Automation and tools

**Earned Directories:**
- logs/ - Thread exports and audit trails
- templates/ - Session and document templates
- workflows/ - Reusable workflow definitions
- backups/ - System backups (30-day retention)
- services/ - Hosted services (ZoBridge)
- lib/ - Shared Python modules

**Archived:** 33 legacy directories → .archive_2025-10-28/

**Symlinks (temporary compatibility):**
- N5/records → /workspace/Records
- N5/lists → /workspace/Lists
- N5/sessions → N5/data/sessions

See .archive_2025-10-28/symlinks_created.txt for full list.
```

### 8.2: Create Migration Log

Document:
- Directories archived (with sizes)
- Symlinks created
- Scripts updated
- Verification results
- Rollback procedure

---

## Phase 9: Symlink Phaseout Plan (ongoing)

### 9.1: Symlink Registry

Track in `/home/workspace/N5/data/symlink_registry.jsonl`:

```json
{"path": "N5/records", "target": "Records/", "created": "2025-10-28", "reason": "38 script references", "status": "active"}
{"path": "N5/lists", "target": "Lists/", "created": "2025-10-28", "reason": "13 recipe references", "status": "active"}
```

### 9.2: Phaseout Strategy

1. **Week 1-2:** Monitor for breakage, stabilize
2. **Week 3:** Begin updating scripts to use direct paths
3. **Week 4:** Update recipes
4. **Week 5:** Test with symlinks removed (temporary)
5. **Week 6:** Permanently remove symlinks if stable

---

## Rollback Strategy

If migration fails or causes issues:

```bash
# Stop all scheduled tasks (manual in Zo UI)

# Restore from pre-migration backup
cd /home/workspace
tar xzf /tmp/n5_premigration_*.tar.gz

# Or use Zo system snapshot restore (preferred)

# Verify restoration
python3 N5/scripts/session_state_manager.py --version
```

---

## Success Criteria

1. ✅ N5/ reduced from 42 to ~12 directories
2. ✅ All backups consolidated to single archive location
3. ✅ Inbox/ clean and usable for triage
4. ✅ All 36 scheduled tasks execute without path errors
5. ✅ Session state manager initializes correctly
6. ✅ No data loss (all archived, not deleted)
7. ✅ Symlink compatibility layer functional
8. ✅ Documentation updated (N5.md, architectural principles)

---

## Timeline

| Phase | Duration | Can Pause? |
|-------|----------|------------|
| 1. Survey & Protect | 30 min | ✅ Yes |
| 2. N5 Rationalization | 90 min | ⚠️  After dry-run |
| 3. Backup Consolidation | 30 min | ✅ Yes |
| 4. Inbox Cleanup | 20 min | ✅ Yes |
| 5. Meetings (skip) | 0 min | N/A |
| 6. Migration Execution | 60 min | ❌ No - complete once started |
| 7. Verification | 45 min | ⚠️  After verification |
| 8. Documentation | 30 min | ✅ Yes |
| **TOTAL** | **4h 45min** | |

---

## Next Steps

1. **V: Review this plan** - Confirm approach, adjust if needed
2. **Zo: Create migration script** - Write and test in dry-run
3. **V: Authorize execution** - Explicit go/no-go decision
4. **Zo: Execute phases 1-5** - Can pause between phases
5. **Zo: Execute phase 6** - Non-stop once started
6. **Zo: Verify and document** - Phases 7-8
7. **Monitor** - Watch for breakage over next week

---

**Status:** PLANNING COMPLETE, AWAITING V'S REVIEW

*Plan created: 2025-10-28 10:18 EST*
