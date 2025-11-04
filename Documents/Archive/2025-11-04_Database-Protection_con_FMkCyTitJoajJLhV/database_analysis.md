---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Database Inventory & Git Tracking Analysis

## Current Situation

**CRITICAL FINDING**: You have **30 databases currently tracked in Git**, which is extremely dangerous for the exact reason you experienced—data loss when databases get overwritten or "nuked."

## All Databases Found (45 total)

### 1. System Infrastructure Databases (NOT for Git)
**Location**: `.config/syncthing/`
- `folder.0001-vjhr6c6j.db` through `folder.0009-f2wuzxon.db` (8 files)
- `main.db`
- **Status**: ✅ Should NOT be in Git (Syncthing internal state)
- **Current**: ⚠️ TRACKED IN GIT (WRONG!)
- **Action**: Add `.config/` to .gitignore

### 2. N5 System Databases 
**Location**: `N5/data/`

#### Currently Tracked (HIGH RISK):
- ✅ `executables.db` (588KB) - Registered prompts/commands
- ✅ `conversations.db` (700KB) - Conversation metadata
- ✅ `block_registry.db` (24KB) - Content blocks
- ✅ `meeting_pipeline.db` (52KB) - Meeting processing state
- ✅ `profiles.db` (72KB) - Profile data
- ✅ `meetings.db` (0KB) - Meeting records
- ✅ `scheduled_tasks.db` (0KB) - Task scheduling
- ✅ `zo_feedback.db` (28KB) - Feedback tracking
- ✅ `zobridge.db` (3.8MB) - Bridge service data
- ✅ `productivity_tracker.db` (20KB) - Productivity metrics

**Status**: ⚠️ **ALL TRACKED IN GIT - EXTREMELY DANGEROUS**

These are **operational databases** that change constantly. They should NEVER be in Git because:
- They contain runtime state
- They get modified by running processes
- Git conflicts can corrupt them
- Overwrites destroy data permanently

### 3. Knowledge/Intelligence Databases
**Location**: Various knowledge directories

#### Currently Tracked:
- ✅ `Knowledge/crm/crm.db` (108KB) - CRM data
- ✅ `Knowledge/linkedin/linkedin.db` (196KB) - LinkedIn contacts
- ✅ `Knowledge/market_intelligence/gtm_intelligence.db` (124KB) - Market intel
- ❌ `Intelligence/blocks.db` (260KB) - Intelligence blocks (not tracked)
- ❌ `Intelligence/intelligence.db` (0KB) - Intelligence data (not tracked)

**Status**: ⚠️ **PARTIALLY TRACKED - RISKY**

### 4. Personal/Workspace Databases
- ❌ `Personal/profiles.db` (0KB) - Not tracked
- ✅ `productivity_tracker.db` (92KB) - Tracked
- ✅ `Records/Personal/productivity_tracker.db` - Tracked

### 5. Inbox/Backup Databases (Temporary)
**Location**: `Inbox/` and `N5/data/backups/`
- Multiple dated productivity tracker backups
- Conversation backups
- **Status**: Some tracked, some not—these should NEVER be tracked

## Should Databases Be Tracked in Git?

### ❌ NO - For Operational/Runtime Databases

**Reasons NOT to track operational databases:**

1. **Data Loss Risk**: Git merge conflicts can corrupt binary SQLite files
2. **Race Conditions**: Multiple processes updating = instant corruption
3. **Size Bloat**: Every change creates a full copy in Git history
4. **Wrong Tool**: Git is for source code versioning, not data versioning
5. **Unrecoverable**: A bad merge or overwrite = data gone forever

### ✅ MAYBE - For Reference/Config Databases (With Strict Rules)

**When it MIGHT be acceptable:**
- Small, infrequently updated reference data
- Manually curated content only
- No automated writes
- Clear ownership (no concurrent access)
- Export to human-readable format alongside (JSON/SQL dumps)

**Example candidates:**
- `executables.db` - IF exported to JSON for human review
- Empty schema templates

### ✅ YES - For Database Schemas (As SQL)

**What SHOULD be in Git:**
- Schema definitions (`.sql` files)
- Migration scripts
- Sample/seed data
- Documentation

## Recommended Solution Architecture

### 1. Immediate Actions

```bash
# Add to .gitignore
echo "
# === DATABASES (should NEVER be in Git) ===
*.db
*.sqlite
*.sqlite3
*.db-shm
*.db-wal

# Config directories with runtime state
.config/

# But allow schema/migration files
!**/schema.sql
!**/migrations/*.sql
!**/seeds/*.sql
" >> .gitignore

# Remove databases from Git tracking (keep files locally)
git rm --cached **/*.db
git rm --cached .config/syncthing/index-v2/*.db
git commit -m "Remove databases from Git tracking (operational data)"
```

### 2. Proper Database Backup Strategy

**Instead of Git, use:**

#### A. Automated Snapshots
```bash
# Daily snapshots with rotation
0 2 * * * /home/workspace/N5/scripts/backup_databases.sh
```

#### B. Export to Human-Readable Formats
```bash
# Convert critical DBs to JSON for Git
sqlite3 executables.db ".dump" > executables.schema.sql
python3 export_db_to_json.py executables.db > executables.data.json
```

#### C. Separate Backup Repository (Optional)
- Use `git-annex` or similar for large binary files
- Or use dedicated backup tools (restic, borg)

### 3. Protection System

Create `.n5protected` files in critical directories:
```bash
echo "operational_databases" > N5/data/.n5protected
echo "system_config" > .config/.n5protected
```

## Database Classification Matrix

| Database | Size | Change Freq | Git? | Backup Strategy |
|----------|------|-------------|------|-----------------|
| **N5 Operational** |
| executables.db | 588KB | High | ❌ NO | JSON export + daily snapshot |
| conversations.db | 700KB | Very High | ❌ NO | Daily snapshot only |
| meeting_pipeline.db | 52KB | High | ❌ NO | Daily snapshot |
| zobridge.db | 3.8MB | High | ❌ NO | Daily snapshot |
| **Knowledge** |
| crm.db | 108KB | Medium | ⚠️ MAYBE | JSON export + snapshot |
| linkedin.db | 196KB | Medium | ⚠️ MAYBE | JSON export + snapshot |
| gtm_intelligence.db | 124KB | Medium | ⚠️ MAYBE | JSON export + snapshot |
| **System** |
| syncthing/*.db | Various | Very High | ❌ NO | Managed by Syncthing |

## Implementation Priority

### 🔴 CRITICAL (Do Now)
1. Add `*.db` to .gitignore
2. Remove all `.db` files from Git tracking
3. Create automated backup script
4. Add `.n5protected` to N5/data/

### 🟡 HIGH (This Week)
1. Implement JSON export for critical DBs
2. Set up daily snapshot rotation
3. Document which DBs contain what
4. Create restore procedures

### 🟢 MEDIUM (This Month)
1. Migrate to schema + data separation
2. Implement proper database migration system
3. Add database health monitoring

## Root Cause of the Incident

The database was likely nuked because:
1. Database was tracked in Git
2. A Git operation (pull/merge/reset) overwrote it
3. Or an AI operation assumed it could be recreated since it was "in Git"
4. SQLite files are binary—Git can't merge them safely

**Prevention**: Remove ALL databases from Git tracking immediately.
