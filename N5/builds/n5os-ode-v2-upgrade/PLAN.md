---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_KsG8Cyc7SlXm5lHr
---

# N5OS-Ode v2 Upgrade Plan

**Objective:** Upgrade n5os-ode export from v1 to v2, incorporating build orchestrator v2, content library v5, conversation close v5.5, and voice system template.

**Estimated effort:** 2-3 hours across 5 workers
**Target:** `N5/export/n5os-ode/`

---

## Open Questions

1. ~~Should voice system be fully included or just template?~~ → **Template only** (per V)
2. ~~Include deals/CRM scripts?~~ → **No** (V-specific, not distributable)

---

## Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **A: Full sync (copy everything)** | Complete parity | Includes V-specific data, bloat | ❌ Rejected |
| **B: Selective upgrade (chosen)** | Clean, distributable | Manual selection work | ✅ Selected |
| **C: Automated diff/patch** | Less manual | Complex, error-prone | ❌ Rejected |

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Notes |
|----------|--------------|-------|
| Remove V-specific file refs | Easy to re-add | Safe |
| Update schema versions | Forward-only | **TRAP DOOR** - document old schema |
| LICENSE choice | Can change later | Safe |

---

## Phase Checklist

### Phase 1: Build Orchestrator v2 (W1.1)
- [ ] Copy `build_lesson_ledger.py`
- [ ] Sync `build_status.py`
- [ ] Sync `init_build.py`
- [ ] Sync `update_build.py`
- [ ] Add `mece-worker-framework.md`
- [ ] Add `build-lesson-criteria.md`
- [ ] Sync `orchestrator-protocol.md`
- [ ] Update `Build Capability.prompt.md`
- [ ] Update `Spawn Worker.prompt.md`
- [ ] Sanitize paths/references

### Phase 2: Content Library v5 (W1.2)
- [ ] Sync `content_ingest.py`
- [ ] Sync `content_library.py`
- [ ] Update `DEPENDENCIES.md` if needed
- [ ] Sanitize paths/references

### Phase 3: Conversation Close v5.5 (W1.3)
- [ ] Sync `Close Conversation.prompt.md`
- [ ] Add `conversation-end-v5.md` to docs
- [ ] Verify referenced scripts exist
- [ ] Sanitize paths/references

### Phase 4: Voice System Template (W1.4)
- [ ] Create `N5/scripts/retrieve_voice_lessons.py` (generic template)
- [ ] Create `N5/prefs/communication/voice-lessons.md` (empty template)
- [ ] Create `N5/prefs/communication/voice-system-prompt.md` (template)
- [ ] Update docs to mention voice system capability
- [ ] Sanitize - remove V-specific lessons/patterns

### Phase 5: Context Manifest + Docs (W2.1) — depends on W1.*
- [ ] Reconcile `context_manifest.yaml` with actual files
- [ ] Fix broken markdown links in `prefs.md`
- [ ] Replace PROJECT_REPO placeholders in all scripts
- [ ] Add LICENSE file (MIT)
- [ ] Update README with v2 features
- [ ] Run verification checks

---

## Scope Matrix (MECE Validation)

| Scope Item | Worker | Status |
|------------|--------|--------|
| `N5/scripts/build_lesson_ledger.py` | W1.1 | ✓ |
| `N5/scripts/build_status.py` | W1.1 | ✓ |
| `N5/scripts/init_build.py` | W1.1 | ✓ |
| `N5/scripts/update_build.py` | W1.1 | ✓ |
| `N5/prefs/operations/mece-worker-framework.md` | W1.1 | ✓ |
| `N5/prefs/operations/build-lesson-criteria.md` | W1.1 | ✓ |
| `N5/prefs/operations/orchestrator-protocol.md` | W1.1 | ✓ |
| `Prompts/Build Capability.prompt.md` | W1.1 | ✓ |
| `Prompts/Spawn Worker.prompt.md` | W1.1 | ✓ |
| `N5/scripts/content_ingest.py` | W1.2 | ✓ |
| `N5/scripts/content_library.py` | W1.2 | ✓ |
| `docs/DEPENDENCIES.md` | W1.2 | ✓ |
| `Prompts/Close Conversation.prompt.md` | W1.3 | ✓ |
| `docs/conversation-end-v5.md` | W1.3 | ✓ |
| `N5/scripts/retrieve_voice_lessons.py` | W1.4 | ✓ |
| `N5/prefs/communication/voice-lessons.md` | W1.4 | ✓ |
| `N5/prefs/communication/voice-system-prompt.md` | W1.4 | ✓ |
| `N5/prefs/context_manifest.yaml` | W2.1 | ✓ |
| `N5/prefs/prefs.md` | W2.1 | ✓ |
| `README.md` | W2.1 | ✓ |
| `LICENSE` | W2.1 | ✓ |
| All PROJECT_REPO placeholders | W2.1 | ✓ |

**Gaps:** None
**Overlaps:** None

---

## Wave Structure

```
Wave 1 (parallel):
  W1.1: Build Orchestrator v2
  W1.2: Content Library v5
  W1.3: Conversation Close v5.5
  W1.4: Voice System Template
         ↓
Wave 2 (depends on Wave 1):
  W2.1: Context Manifest + Docs + Verification
```

**Critical path:** 2 waves (4 parallel + 1 sequential)

---

## Success Criteria

1. All Python scripts compile without errors: `python3 -m py_compile *.py`
2. No broken file references in prompts or context_manifest
3. No V-specific paths (careerspan, deals.db, positions.db)
4. PROJECT_REPO replaced with `vrijenattawar/n5os-ode`
5. BOOTLOADER.prompt.md workflow runs without missing files
6. LICENSE file present
7. README documents v2 features

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Script has V-specific imports | Medium | Medium | Workers verify imports exist in ode |
| Context manifest references missing files | High | Low | W2.1 reconciles after W1.* complete |
| Voice lessons contain personal patterns | Medium | High | Template uses placeholders only |

---

## Token Estimates

| Worker | Files | Est. Tokens | % Context |
|--------|-------|-------------|-----------|
| W1.1 | 9 files | ~8,000 | ~4% |
| W1.2 | 3 files | ~3,500 | ~2% |
| W1.3 | 2 files | ~2,500 | ~1.5% |
| W1.4 | 3 files | ~2,000 | ~1% |
| W2.1 | 5 files | ~3,000 | ~2% |

All workers well under 40% budget. ✓
