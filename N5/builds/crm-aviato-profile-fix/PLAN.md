---
created: 2025-12-17
last_edited: 2025-12-17
version: 2
provenance: con_qi7Us8bou9rFtSYf
---
# Plan: CRM v3 — Fix Aviato Enrichment Pipeline + Add Adam Alpert Profile

## V's Inputs (Resolved)
- **Email:** adam@pangea.app
- **Categories:** NETWORKING + COMMUNITY (dual-tag in markdown, single DB row)
- **Context:** Fellow member + founder of NYC Founders Club
- **Storage:** CRM profile stores distilled summary; full Aviato JSON stored separately
- **Action:** Delete incorrect profile (team@kairoshq.com), recreate correctly

---

## Open Questions
*All resolved by V's input above.*

---

## Architecture Study Findings

### Current CRM v3 Data Flow
```
Profile Creation (crm_cli.py create)
       ↓
YAML file → N5/crm_v3/profiles/<Name>_<slug>.yaml
       ↓
SQLite row → N5/data/crm_v3.db (profiles table)
       ↓
Enrichment job queued → enrichment_queue table
       ↓
Worker processes → crm_enrichment_worker.py
       ↓
Intel appended → Personal/Knowledge/CRM/individuals/<slug>.md
```

### Current State of System
| Metric | Value |
|--------|-------|
| Total profiles | 77 |
| Enrichment jobs queued | 15 |
| Jobs completed | 15 |
| Jobs failed | 8 |
| Intelligence sources written | 0 |

### Root Cause of Failures

**Bug #1: API mismatch between worker and enricher**
- `crm_enrichment_worker.py` line 255 expects: `aviato_data, aviato_error = await enrich_via_aviato(email)`
- But `aviato_enricher.py` returns: `{'success': bool, 'data': dict|None, 'error': str|None, 'markdown': str}`
- Error: `too many values to unpack (expected 2)`

**Bug #2: Missing raw JSON storage**
- Aviato enricher formats data into markdown but doesn't persist the raw JSON anywhere
- If we want full Aviato JSON stored (per V's request), we need to add a storage location

**Bug #3: YAML ↔ Markdown split is incomplete**
- CRM has TWO markdown locations:
  1. `N5/crm_v3/profiles/<slug>.yaml` — identity + frontmatter (used by crm_cli)
  2. `Personal/Knowledge/CRM/individuals/<slug>.md` — intel log (used by enrichment worker)
- The `_append_intel_log()` function writes to #2, but profiles created via `crm create` only make #1
- Result: enrichment intel has nowhere to go for new profiles

**Bug #4: Slug derivation is brittle**
- `_load_profile_slug()` derives slug from yaml_path stem (e.g., `Adam_Alpert_team`)
- But intel markdown uses different naming (e.g., `adam-alpert.md`)
- No guaranteed mapping between the two

### Files Involved
| File | Role |
|------|------|
| `N5/scripts/crm_cli.py` | CLI tool, creates profiles + queues enrichment |
| `N5/scripts/crm_enrichment_worker.py` | Processes enrichment_queue, calls Aviato, writes intel |
| `N5/scripts/enrichment/aviato_enricher.py` | Aviato API wrapper, returns structured dict |
| `Integrations/Aviato/aviato_client.py` | Raw API client |
| `Integrations/Aviato/crm_mapper.py` | Maps Aviato response → CRM fields |
| `N5/crm_v3/profiles/*.yaml` | YAML identity files |
| `Personal/Knowledge/CRM/individuals/*.md` | Intel markdown files |
| `N5/data/crm_v3.db` | SQLite: profiles, enrichment_queue tables |

### Where Raw Aviato JSON Should Live
Options:
1. **`N5/data/staging/aviato/<person_id>.json`** — ephemeral staging (recommended)
2. **`Personal/Knowledge/CRM/individuals/<slug>.aviato.json`** — alongside markdown
3. **Inside the CRM markdown as a fenced JSON block** — queryable but bloated

**Recommendation:** Option 1 (staging dir) + symlink or reference in intel log.

---

## Checklist (Phases)

### Phase 1: Fix Enrichment Pipeline (System Fix)
**Affected Files:**
- `N5/scripts/crm_enrichment_worker.py`
- `N5/scripts/enrichment/aviato_enricher.py` (verify)
- `N5/data/staging/aviato/` (create dir)

**Changes:**
- [ ] Fix `enrich_profile_via_tools()` to unpack the dict return correctly
- [ ] Add raw JSON persistence to `N5/data/staging/aviato/<email_hash>.json`
- [ ] Ensure intel markdown file is created if missing before appending

**Unit Tests:**
- [ ] `python3 N5/scripts/crm_enrichment_worker.py --test --dry-run` reports next job without error
- [ ] `python3 N5/scripts/crm_enrichment_worker.py --test` processes one job successfully

---

### Phase 2: Delete Incorrect Profile + Create Correct One
**Affected Files:**
- `N5/data/crm_v3.db` (DELETE from profiles, enrichment_queue)
- `N5/crm_v3/profiles/Adam_Alpert_team.yaml` (DELETE)
- `N5/crm_v3/profiles/Adam_Alpert_adam.yaml` (CREATE)
- `Personal/Knowledge/CRM/individuals/adam-alpert.md` (CREATE)

**Changes:**
- [ ] Delete profile ID 77 (team@kairoshq.com) from DB
- [ ] Delete associated enrichment_queue entries
- [ ] Delete YAML file
- [ ] Create new profile with email=adam@pangea.app, category=NETWORKING
- [ ] Create intel markdown file with proper frontmatter
- [ ] Add notes: "Fellow member + founder of NYC Founders Club. Categories: NETWORKING, COMMUNITY."

**Unit Tests:**
- [ ] `crm search --email adam@pangea.app` returns the new profile
- [ ] `ls N5/crm_v3/profiles/ | grep -i adam` shows only one file
- [ ] `cat Personal/Knowledge/CRM/individuals/adam-alpert.md` shows proper structure

---

### Phase 3: Enrich Adam's Profile via Aviato
**Affected Files:**
- `N5/data/staging/aviato/` (raw JSON stored here)
- `Personal/Knowledge/CRM/individuals/adam-alpert.md` (intel appended)
- `N5/data/crm_v3.db` (enrichment_status updated)

**Changes:**
- [ ] Queue manual enrichment: `crm enrich adam-alpert`
- [ ] Run enrichment worker: `python3 N5/scripts/crm_enrichment_worker.py --test`
- [ ] Verify intel appended to markdown file
- [ ] Verify raw JSON saved to staging

**Unit Tests:**
- [ ] `cat Personal/Knowledge/CRM/individuals/adam-alpert.md | grep -i aviato` shows intel block
- [ ] `ls N5/data/staging/aviato/ | grep adam` shows raw JSON file
- [ ] `sqlite3 N5/data/crm_v3.db "SELECT enrichment_status FROM profiles WHERE email='adam@pangea.app'"` returns 'succeeded'

---

### Phase 4: Delete One-Off DD Artifacts
**Affected Files:**
- `/home/workspace/Documents/DD_Adam_Alpert_Pangea.md` (DELETE)
- `/home/.z/workspaces/con_qi7Us8bou9rFtSYf/DD_Adam_Alpert_Pangea.md` (DELETE)
- `/home/.z/workspaces/con_qi7Us8bou9rFtSYf/DD_Adam_Alpert_Pangea_raw.json` (MOVE to staging, then delete)
- `/home/.z/workspaces/con_qi7Us8bou9rFtSYf/aviato_dd_adam_alpert.py` (DELETE)

**Changes:**
- [ ] Move raw JSON to `N5/data/staging/aviato/adam-alpert_bootstrap.json` (preserve data)
- [ ] Delete markdown reports
- [ ] Delete ad-hoc script

**Unit Tests:**
- [ ] `ls /home/workspace/Documents/ | grep -i alpert` returns nothing
- [ ] `ls N5/data/staging/aviato/ | grep adam` shows preserved JSON

---

## Success Criteria
1. ✅ `crm` CLI runs without import errors
2. ✅ Enrichment worker processes jobs without "too many values to unpack" error
3. ✅ Adam Alpert profile exists with correct email (adam@pangea.app)
4. ✅ Adam's intel markdown contains Aviato enrichment block
5. ✅ Raw Aviato JSON is persisted in staging
6. ✅ One-off DD artifacts are deleted
7. ✅ No duplicate profiles for Adam

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing enrichment jobs | Test with --dry-run first; only modify worker return handling |
| Losing raw Aviato data | Create staging dir BEFORE deleting conversation artifacts |
| Duplicate CRM markdown files | Check for existing adam*.md before creating |
| DB/YAML desync | Run `crm stats` after changes to verify counts match |

---

## Trap Doors Identified
1. **Schema change to profiles table** — NOT proposed (would require migration)
2. **Changing CRM markdown canonical path** — NOT proposed (keep Personal/Knowledge/CRM/)
3. **Changing Aviato enricher return signature** — Already changed; we adapt worker to match

---

## Alternatives Considered

### Alternative 1: Re-run DD script and import manually
- ❌ Doesn't fix the underlying enrichment pipeline
- ❌ Next contact would hit same bugs

### Alternative 2: Fix only the return value unpacking
- ⚠️ Partial fix — wouldn't add raw JSON storage
- ⚠️ Wouldn't create intel markdown file if missing

### Alternative 3 (Recommended): Full pipeline fix + correct profile creation
- ✅ Fixes root cause
- ✅ Adds raw JSON persistence per V's request
- ✅ Ensures intel markdown created alongside YAML profile
- ✅ Adam's profile done correctly as proof-of-fix

---

## Execution Readiness

**Pre-execution checklist:**
- [x] V confirmed email: adam@pangea.app
- [x] V confirmed categories: NETWORKING + COMMUNITY
- [x] V confirmed: delete incorrect profile, recreate
- [x] V confirmed: store distilled summary in CRM, full JSON elsewhere
- [x] V confirmed: delete one-off DD artifacts after fix
- [x] Architecture study complete
- [x] Plan reviewed

**Ready for execution:** YES (awaiting V's "go" command)

