---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_2FrBvAsCrp7EntR3
build_slug: ode-cleanup
---

# N5OS Ode Version Cleanup & Sync Hardening

## Open Questions

1. ~~What caused the GitHub force push?~~ **ANSWERED:** Devin wiki work pushed fresh repo (1 commit) over existing 36-commit history
2. ~~Which version has the most complete content?~~ **ANSWERED:** GitHub has Skills/, Local has history. Need both.
3. Should we restore git history from local? **DECISION NEEDED** — see Alternatives below

---

## Executive Summary

**Root Cause:** A force push to GitHub (commit `773efa8`, Jan 26 21:46 UTC) replaced the entire 36-commit history with a single mega-commit. The push came from Devin's wiki work and included new Skills/ content, but **obliterated all git history**.

**Current State:**
- **GitHub:** 184 files, 1 commit (fresh init), has Skills/meeting-ingestion + Skills/pulse
- **Local Export:** 160 files, 36 commits (full history), missing new Skills/
- **Root n5os-ode/:** 17 files, orphan fragment (NOT a git repo) — DELETE

**Required Actions:**
1. Delete orphan `/home/workspace/n5os-ode/`
2. Merge GitHub content into local export (preserve local history)
3. Force push corrected repo to GitHub (restore history + add new content)
4. Clean up stale Inbox artifacts
5. Add safeguards to prevent future force pushes

---

## Alternatives Analysis (Nemawashi)

### Option A: GitHub as Source of Truth (Accept History Loss) ❌
- Pull GitHub, accept single-commit history
- **Pro:** Simple, matches what's published
- **Con:** Lose 36 commits of audit trail, makes future debugging harder
- **REJECTED:** History has value for understanding evolution

### Option B: Local as Source, Merge New Content ✅ RECOMMENDED
- Keep local 36-commit history
- Cherry-pick/merge the new Skills/ content from GitHub
- Force push corrected history to GitHub
- **Pro:** Preserves history, adds new content
- **Con:** Requires force push (but we control the repo)
- **SELECTED:** Best of both worlds

### Option C: Start Fresh, Document History
- Archive current state, start clean v2.0
- **Pro:** Clean slate
- **Con:** Unnecessary complexity, loses continuity
- **REJECTED:** Overkill for this situation

---

## Trap Doors ⚠️

1. **Force push to GitHub** — Irreversible once done. Mitigation: Create backup branch first.
2. **Deleting orphan folder** — Low risk (it's just Prompts/ fragment). Mitigation: List contents first.

---

## Checklist

### Stream 1: Cleanup & Sync (Sequential)
- [ ] **S1.1** Delete orphan `/home/workspace/n5os-ode/`
- [ ] **S1.2** Pull new content from GitHub into local export
- [ ] **S1.3** Verify merged repo integrity
- [ ] **S1.4** Push corrected repo to GitHub (with history)
- [ ] **S1.5** Clean Inbox artifacts

### Stream 2: Safeguards (Can run parallel after S1.4)
- [ ] **S2.1** Add `.github/workflows/protect-history.yml` to prevent force pushes
- [ ] **S2.2** Document sync protocol in `CONTRIBUTING.md`
- [ ] **S2.3** Create local sync-check script

### Stream 3: Validation (After all above)
- [ ] **S3.1** Verify GitHub matches local export
- [ ] **S3.2** Run `validate_repo.py`
- [ ] **S3.3** Test fresh clone + install.sh

---

## Phase 1: Cleanup & Merge (Drops D1.1-D1.3)

### Drop D1.1: Delete Orphan + Prepare Local
**Scope:** Filesystem cleanup, no git operations

**Affected Files:**
- DELETE: `/home/workspace/n5os-ode/` (entire directory)
- BACKUP: Create `/home/workspace/N5/export/n5os-ode-backup-pre-merge/`

**Changes:**
1. List contents of orphan folder (audit)
2. Delete orphan folder
3. Create backup of local export

**Verification:**
- `test ! -d /home/workspace/n5os-ode` (orphan gone)
- `test -d /home/workspace/N5/export/n5os-ode-backup-pre-merge` (backup exists)

---

### Drop D1.2: Merge GitHub Content
**Scope:** Git operations, content merge

**Affected Files:**
- ADD: `Skills/meeting-ingestion/` (entire directory from GitHub)
- ADD: `Skills/pulse/` (entire directory from GitHub)
- ADD: `N5/scripts/meeting_*.py` (5 files)
- ADD: `templates/configs/drive_locations.yaml.template`
- MODIFY: `README.md` (merge GitHub additions)
- MODIFY: `install.sh` (resolve local vs GitHub differences)

**Changes:**
1. Clone fresh GitHub repo to temp location
2. Copy new Skills/ directories to local export
3. Copy new N5/scripts/meeting_*.py files
4. Copy new template
5. Merge README.md changes (GitHub has updated content)
6. Resolve install.sh (local has uncommitted changes)
7. Commit merge locally

**Verification:**
- `find Skills/ -name "SKILL.md" | wc -l` returns 2+ (meeting-ingestion, pulse)
- `ls N5/scripts/meeting_*.py | wc -l` returns 5
- `git log --oneline | wc -l` shows 37+ commits

---

### Drop D1.3: Push to GitHub + Clean Inbox
**Scope:** Remote sync, Inbox cleanup

**Affected Files:**
- PUSH: GitHub repo (force push with history)
- DELETE: `Inbox/20251103-*_n5os-lite*`
- DELETE: `Inbox/20251105-*_n5os-lite*`
- DELETE: `Inbox/20251028-*_n5os_core_spec*.md`

**Changes:**
1. Create backup branch on GitHub: `git push origin main:backup-pre-restore`
2. Force push local to GitHub: `git push --force-with-lease origin main`
3. Delete stale Inbox artifacts

**Verification:**
- `git log origin/main --oneline | wc -l` returns 37+
- `ls Inbox/*n5os* 2>/dev/null` returns empty

---

## Phase 2: Safeguards (Drop D2.1)

### Drop D2.1: Add Protection Mechanisms
**Scope:** GitHub config, documentation

**Affected Files:**
- CREATE: `.github/workflows/protect-history.yml` (branch protection reminder)
- MODIFY: `docs/CONTRIBUTING.md` (add sync protocol)
- CREATE: `N5/scripts/ode_sync_check.py` (local pre-push validator)

**Changes:**
1. Add GitHub Actions workflow that warns on force push attempts
2. Document sync protocol: "Always pull before starting work"
3. Create script that compares local vs remote before push

**Verification:**
- `.github/workflows/protect-history.yml` exists
- `grep -q "sync protocol" docs/CONTRIBUTING.md`

---

## Phase 3: Validation (Drop D3.1)

### Drop D3.1: End-to-End Verification
**Scope:** Testing, validation

**Changes:**
1. Clone fresh from GitHub to /tmp
2. Run `install.sh` in simulated workspace
3. Run `validate_repo.py`
4. Verify file counts match between local and remote
5. Generate comparison report

**Verification:**
- `validate_repo.py` exits 0
- Fresh clone file count == local export file count
- No broken file references in prompts

---

## Success Criteria

1. ✅ Single source of truth: GitHub repo with full 37+ commit history
2. ✅ Local export matches GitHub exactly (except .pyc files)
3. ✅ New Skills/ content present (meeting-ingestion, pulse)
4. ✅ No orphan n5os-ode folders in workspace
5. ✅ Inbox cleaned of stale exports
6. ✅ Protection mechanisms in place
7. ✅ Fresh clone + install.sh works

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Force push breaks something | Low | High | Create backup branch first |
| Merge conflicts | Medium | Low | Manual resolution, small scope |
| Missing content | Low | Medium | Diff verification in D3.1 |

---

## MECE Worker Assignment

| Scope Item | Assigned Drop | 
|------------|---------------|
| Delete orphan folder | D1.1 |
| Create local backup | D1.1 |
| Merge Skills/ content | D1.2 |
| Merge meeting scripts | D1.2 |
| Merge README/install | D1.2 |
| Push to GitHub | D1.3 |
| Clean Inbox | D1.3 |
| GitHub Actions workflow | D2.1 |
| Update CONTRIBUTING.md | D2.1 |
| Create sync-check script | D2.1 |
| End-to-end validation | D3.1 |

No overlaps. All items assigned.

---

## Execution Mode

**Recommended:** Sequential execution (D1.1 → D1.2 → D1.3 → D2.1 → D3.1)

The git operations have dependencies, so parallel execution isn't safe here. However, D2.1 could potentially run parallel with D3.1 after D1.3 completes.

**Pulse configuration:**
- Stream 1: D1.1 → D1.2 → D1.3 (sequential)
- Stream 2: D2.1 (after S1 complete)
- Stream 3: D3.1 (after S1 and S2 complete)
