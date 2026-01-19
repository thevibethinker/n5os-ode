---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_ZGBnCCZnbKMYnfcF
---

# Deals System Repair & Consolidation

## Open Questions
- [RESOLVED] Is the zo_partnerships.jsonl integrated with deals.db? → Yes, same system, staging files feed into DB
- [RESOLVED] What caused deal_sync_external.py to break? → Orphan code blocks after `main()` (lines 437+)
- [PENDING] Which of the 4 deal agents is the "canonical" one? Need to audit overlap

## Problem Statement
The deals tracking system has multiple issues:
1. `deal_sync_external.py` has a syntax error preventing external sync
2. 76/77 deals stuck at "identified" stage with no progression
3. Zero meeting→deal linkages exist
4. Zero `external_source` values populated
5. Four overlapping scheduled agents with unclear responsibilities

## Success Criteria
- [ ] All deal scripts pass syntax check
- [ ] External sync runs successfully (Google Sheet → deals.db)
- [ ] `external_source` populated for all 77 existing deals
- [ ] Meeting→deal linkage working (B36 files generated)
- [ ] Deal agents consolidated to 1-2 with clear responsibilities
- [ ] Documentation updated

## Worker Structure (3 Workers, MECE)

### Wave 1 (All parallel)

| Worker | Scope | Deliverables |
|--------|-------|--------------|
| W1.1 | Script Fix & Sync Execution | Fixed script, successful sync run, verification |
| W1.2 | Agent Audit & Consolidation | Analysis of 4 agents, consolidation proposal, implementation |
| W1.3 | Data Integrity & Linkage | Backfill external_source, fix meeting→deal linkage, verify activities |

## Risks & Mitigations
- **Risk:** Agents might be doing useful distinct work → **Mitigation:** W1.2 audits thoroughly before consolidating
- **Risk:** Backfill might create duplicates → **Mitigation:** W1.3 uses idempotent upserts
- **Risk:** Breaking working components → **Mitigation:** All workers test before applying changes

## Checklist

### Phase 1: Parallel Execution
- [ ] W1.1: Fix deal_sync_external.py syntax error
- [ ] W1.1: Run full sync with `--source all`
- [ ] W1.1: Verify deals.db updated correctly
- [ ] W1.2: Document what each of 4 agents does
- [ ] W1.2: Identify overlap and gaps
- [ ] W1.2: Propose consolidated agent structure
- [ ] W1.2: Implement consolidation (pause/delete redundant agents)
- [ ] W1.3: Backfill external_source for 77 deals
- [ ] W1.3: Test meeting→deal linkage with 1 meeting
- [ ] W1.3: Apply B36 routing to all unrouted meetings

### Phase 2: Verification (Orchestrator)
- [ ] All workers report completion
- [ ] Run deal_cli.py summary to verify
- [ ] Confirm agent list is streamlined
- [ ] Final commit
