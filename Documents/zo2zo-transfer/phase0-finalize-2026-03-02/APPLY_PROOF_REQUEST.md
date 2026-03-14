---
created: 2026-03-02
last_edited: 2026-03-02
version: 1.0
provenance: con_pLLTlqfVu4hKeKhT
---

# Phase 0 Apply-Proof Request (Finalization)

Please run the commands below after pulling the latest transfer drops.

## 1) Apply DB Bootstrap (empty schema-only DBs)

```bash
bash Documents/zo2zo-transfer/db-bootstrap-2026-03-02/bootstrap_empty_duckdbs.sh
```

## 2) Capture Proof Outputs

```bash
duckdb Skills/zode-moltbook/state/social_intelligence.db -c "SHOW TABLES"
duckdb Datasets/career-hotline-calls/data.duckdb -c "SHOW TABLES"
```

## 3) Confirm Localization Resolution

Validate that localized values are set for the following map groups:
- `paths`
- `ports`
- `services`
- `integrations`
- `personas`
- `policies`
- `memory`
- `content_library`
- `wisdom_system`

## 4) Reply Using Receipt JSON

Populate and return:
- `Documents/zo2zo-transfer/phase0-finalize-2026-03-02/APPLY_PROOF_RECEIPT_TEMPLATE.json`

Required: set `phase0_apply_proof_pass=true` only if all checks pass.

