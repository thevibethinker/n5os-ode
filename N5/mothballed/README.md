---
created: 2026-01-27
last_edited: 2026-01-27
version: 1.0
provenance: con_2SVJsADxKFtm54Db
---

# Mothballed Scripts

Scripts in this folder are **deactivated** pending system upgrades. They should not be called by any scheduled agents or workflows.

## Contents

| Script | Mothballed | Reason |
|--------|------------|--------|
| `deal_sync_external.py` | 2026-01-27 | DB compatibility issues with unified `n5_core.db` |
| `deal_meeting_router.py` | 2026-01-27 | References old `deals.db`, not updated for unified DB |
| `notion_deal_sync.py` | 2026-01-27 | Missing `deals` table in legacy path, needs refactor |
| `email_deal_scanner.py` | 2026-01-27 | Part of deal sync system, mothballed together |

## Reactivation Plan

See `N5/SYSTEM_UPGRADES.md` for the reactivation roadmap.

**Required before reactivation:**
1. Update all scripts to use `from db_paths import get_db_connection`
2. Ensure `deals` table exists in `n5_core.db` with correct schema
3. Test each script with `--dry-run` before re-enabling agent
4. Recreate scheduled agent with corrected instructions

## Associated Agent

- **Agent ID:** `806f7fcc-be16-4666-a8f5-2e3c9c7ad4ab`
- **Name:** Deal Sync Hub
- **Status:** DEACTIVATED (2026-01-27)
