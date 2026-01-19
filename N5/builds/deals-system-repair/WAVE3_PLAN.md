---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_1oLxG6Z1OMdnfDOr
---

# Wave 3: Process Fixes & Data Remediation

## Context
Wave 3 addresses issues discovered during V's data review session. These are **process gaps** that allowed incorrect data to persist, plus immediate data fixes.

**Key principle:** Fix the underlying process first, then remediate data.

## Issues from Review Session

| # | Issue | Type | Root Cause |
|---|-------|------|------------|
| 1 | Jeffrey Botteron name wrong ("Jeffery Bot" in Notion) | Data | Manual entry error |
| 2 | Calendly misclassified as leadership, should be acquirer + Tope as leader | Process | Classification rules unclear |
| 3 | Ivor Stratford → Handshake link missing | Process | Meeting intel not flowing to contact records |
| 4 | Vir → Handshake link missing | Process | Broker angle_strategy not populated |
| 5 | Ray angle_strategy shows "Handshake" but meeting is Calendly/Future Fit | Data | Stale or incorrect Notion data |
| 6 | Future Fit deal missing (via Hamoon, meeting Tuesday) | Data | New deal not created |

## Process Gaps to Fix

### Gap 1: Leadership vs Acquirer Classification
**Problem:** Calendly classified as `leadership` instead of `careerspan_acquirer` with Tope as associated leader.

**Current behavior:** If entry point is a person, system creates leadership deal.  
**Correct behavior:** If company is potential acquirer, create acquirer deal + link person as leader.

**Fix:** Update `N5/config/notion_field_mapping.json` comments or create `N5/docs/deal-classification-rules.md` with explicit rules:
- `careerspan_acquirer` = Company that might buy Careerspan
- `leadership` = Person relationship without company context
- If both exist → acquirer deal + leader linked via notes or relation

### Gap 2: Meeting → Broker Linkage Extraction
**Problem:** Meeting B36 files identify deals but don't extract "[Person] will introduce to [Company]" patterns.

**Fix:** Enhance meeting processing to:
1. Detect intro offers in meeting content
2. Update `deal_contacts.angle_strategy` with target companies
3. Log to deal activities

### Gap 3: Calendar → Deal System Integration
**Observation:** V has Hamoon/Future Fit meeting Tuesday but deal doesn't exist.

**Consider:** Tighter calendar integration so upcoming meetings with unknown contacts trigger deal creation prompts.

## Checklist

### Phase 1: Process Documentation (W3.1)
- [ ] Create `N5/docs/deal-classification-rules.md` with explicit rules
- [ ] Document broker→acquirer linkage protocol
- [ ] Add examples for edge cases (Calendly = acquirer, Tope = leader)

### Phase 2: Data Remediation (W3.2)
- [ ] Correct Jeffrey Botteron name in Notion (`broker-jefferybot` → "Jeffrey Botteron")
- [ ] Reclassify Calendly: Create `cs-acq-calendly` acquirer, link Tope, archive `cs-lead-calendly`
- [ ] Update Ivor Stratford `angle_strategy` → "Handshake"
- [ ] Update Vir `angle_strategy` → "Handshake"  
- [ ] Verify Ray's angle_strategy (is Handshake correct or stale?)
- [ ] Create Future Fit deal (`cs-acq-futurefit`) with Hamoon as contact

### Phase 3: Verification (Orchestrator)
- [ ] Run deal_cli.py summary
- [ ] Verify Calendly shows as acquirer with Tope linked
- [ ] Verify broker→Handshake links visible in table
- [ ] V confirms data matches expectations

## Worker Structure

### W3.1: Process Documentation
**Scope:** Create classification rules doc, document broker linkage protocol
**Deliverables:** 
- `N5/docs/deal-classification-rules.md`
- Updated comments in relevant config files

### W3.2: Data Remediation
**Scope:** Fix all 6 data issues
**Deliverables:**
- Notion updates (Jeffrey Botteron, broker angle_strategies)
- Calendly reclassification
- Future Fit deal creation
- deals.db updates via deal_cli.py or direct SQL

## Affected Files
- `N5/docs/deal-classification-rules.md` (new)
- `N5/data/deals.db` (updates)
- `N5/config/notion_field_mapping.json` (comments)
- Notion databases: deal_brokers, acquirer_targets, careerspan_leadership

## Dependencies
- W3.1 should complete before W3.2 (rules inform data fixes)
- Notion API access required for W3.2

## Open Question
- **Calendar integration:** Should upcoming meetings auto-trigger deal creation? Flag for future enhancement or include in this wave?
