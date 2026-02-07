---
created: 2026-01-31
last_edited: 2026-01-31
version: 1.0
provenance: con_mzmorv1rSBgdsdfl
purpose: Pre-Memory-as-Reasoning baseline snapshot
---

# Semantic Memory Baseline

**Snapshot Date:** 2026-01-31T21:45:00 ET
**Build:** memory-as-reasoning
**Status:** Pre-upgrade baseline

## Database Statistics

| Metric | Value |
|--------|-------|
| Resources | 5,393 |
| Blocks | 52,626 |
| Vectors | 52,540 |
| Database Size | ~260MB |

## Embedding Configuration

| Setting | Value |
|---------|-------|
| Model | `all-MiniLM-L6-v2` |
| Dimensions | 384 |
| Provider | Local (sentence-transformers) |

## Backup Reference

- **Backup File:** `N5/cognition/backups/brain_pre-reasoning_20260131_141310.db`
- **Manifest:** `N5/cognition/backups/manifest.json`

## Rollback Instructions

```bash
# To rollback to this baseline:
cp N5/cognition/backups/brain_pre-reasoning_20260131_141310.db N5/cognition/brain.db
rm -f N5/cognition/reasoning.db
rm -f N5/cognition/vectors_v2.db
# Set feature flag:
jq '.N5_REASONING_ENABLED = false' N5/config/feature_flags.json > tmp && mv tmp N5/config/feature_flags.json
```
