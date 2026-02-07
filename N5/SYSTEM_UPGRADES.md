---
created: 2026-01-27
last_edited: 2026-01-27
version: 1.0
provenance: con_2SVJsADxKFtm54Db
---

# N5 System Upgrades

Pending upgrades and reactivation plans for mothballed capabilities.

---

## 🔴 Deal Tracking System (Mothballed 2026-01-27)

**Status:** DEACTIVATED  
**Agent:** `806f7fcc-be16-4666-a8f5-2e3c9c7ad4ab` (Deal Sync Hub)  
**Scripts:** `N5/mothballed/` (4 scripts)

### Problem
The deal sync scripts reference the old `deals.db` structure but the system migrated to unified `n5_core.db` on 2026-01-19. Scripts fail with:
- `sqlite3.OperationalError: no such table: deals`
- `sqlite3.OperationalError: database is locked`

### Scripts Affected
- `deal_sync_external.py` — External source sync (Notion, Google Sheets)
- `deal_meeting_router.py` — Meeting → deal routing
- `notion_deal_sync.py` — Bidirectional Notion sync
- `email_deal_scanner.py` — Email signal detection

### Reactivation Requirements

1. **Schema Alignment**
   - [ ] Verify `deals` table exists in `n5_core.db` with required columns
   - [ ] Ensure `deal_activities`, `deal_roles`, `deal_contacts` tables are present
   - [ ] Update `db_paths.py` if needed

2. **Script Refactoring**
   - [ ] `deal_sync_external.py` — Update to use `get_db_connection()` throughout
   - [ ] `deal_meeting_router.py` — Replace hardcoded `/home/workspace/N5/data/deals.db`
   - [ ] `notion_deal_sync.py` — Remove legacy `DB_DEFAULT`, use unified DB
   - [ ] `email_deal_scanner.py` — Verify compatibility

3. **Testing**
   - [ ] Run each script with `--dry-run`
   - [ ] Verify no DB lock conflicts
   - [ ] Test Notion sync with `--cache-dir` or `NOTION_TOKEN`

4. **Agent Restoration**
   - [ ] Recreate or edit scheduled agent with corrected instructions
   - [ ] Set schedule (was 4x/day)
   - [ ] Monitor first few runs

### Priority
Medium — Deal tracking is useful but not critical path. Can be restored when bandwidth allows.

---

## Template for Future Entries

```markdown
## 🟡 [Capability Name] (Mothballed YYYY-MM-DD)

**Status:** DEACTIVATED  
**Agent:** `agent-id` (Agent Name)  
**Scripts:** `path/to/scripts`

### Problem
[Description of why it was mothballed]

### Reactivation Requirements
- [ ] Requirement 1
- [ ] Requirement 2

### Priority
[High/Medium/Low] — [Rationale]
```
