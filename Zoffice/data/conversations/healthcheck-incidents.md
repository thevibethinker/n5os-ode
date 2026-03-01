## 2026-02-22 04:15 UTC - Layer 2 Healthcheck
**Status: DEGRADED**
| Check | Result |
|-------|--------|
| office.db readable | OK |
| webhook /api/zoffice/webhooks/vapi | OK |
| webhook /api/zoffice/webhooks/github | OK |
| webhook /api/zoffice/webhooks/stripe | OK |
| office.yaml | MISSING |
| integration.yaml | MISSING |
| routing.yaml | MISSING |
| security.yaml | MISSING |
**Action Required**: Core config files not found at `/home/workspace/Zoffice/`. Verify Zoffice deployment or restore from backup.
---
2026-02-22T04:50:03Z | healthcheck | OK | office.db readable, webhooks verified (vapi,github,stripe), configs valid (office,integration,routing,security)
2026-02-22T05:20:00Z | healthcheck | OK | office.db readable (DuckDB v64, 16MB), webhooks verified (vapi,github,stripe), configs parsed (office.yaml,integration.yaml,routing.yaml,security.yaml)
2026-02-22T06:21:25+00:00 | HEALTHCHECK OK | office.db readable, 3/3 webhooks present, 4/4 configs valid
2026-02-22T06:50:00+00:00 | HEALTHCHECK OK | office.db readable (DuckDB, 5 tables), 3/3 webhooks present, 4/4 configs valid
[2026-02-22T07:20:24Z] HEALTHCHECK OK - office.db readable, 3/3 webhooks present, 4/4 configs valid
- [OK] 2026-02-22T07:50:50Z - All checks passed: office.db readable (DuckDB), 3 webhook routes verified, 4 config files valid
[2026-02-22 08:19:40 UTC] LAYER2_HEALTHCHECK: All systems OK - office.db readable, 3 webhooks present, 4 configs valid
2026-02-22 08:50:31 UTC | HEALTHCHECK OK | DB readable, 3/3 webhooks present, 4/4 configs parse valid

2026-02-22 04:20 ET | HEALTHCHECK OK | DB readable (DuckDB), 3/3 webhooks present, 4/4 configs valid
- [2026-02-22 04:51:02 ET] ✅ All checks passed: office.db readable, webhooks (vapi/github/stripe) present, configs (office/integration/routing/security) valid.
2026-02-22 05:20 ET | Layer 2 Healthcheck OK | office.db (DuckDB), webhooks (vapi/github/stripe), configs (office/integration/routing/security) all verified
2026-02-22 10:50:30 UTC | HEALTHCHECK OK | office.db readable, all 3 webhook routes present, all 4 configs parsed
2026-02-22T11:22:31Z | HEALTHCHECK_L2 | ALL_OK | DB:readable WEBHOOKS:vapi+github+stripe CONFIGS:office+integration+routing+security
- [2026-02-22 11:49:39 UTC] ✓ All checks passed: DB readable, webhooks present, configs valid
2026-02-22T12:20:25+00:00 [OK] All healthchecks passed: office.db readable (DuckDB, 5 tables), webhooks verified (vapi, github, stripe), configs parsed (office.yaml, integration.yaml, routing.yaml, security.yaml)
2026-02-22T12:50:00+00:00 [OK] All healthchecks passed: office.db readable (DuckDB), webhooks verified (vapi, github, stripe), configs parsed (office.yaml, integration.yaml, routing.yaml, security.yaml)
2026-02-22T13:24:15Z | L2-HEALTHCHECK | OK | DB readable, webhooks present, configs valid
2026-02-22T13:51:31Z | HEALTHCHECK | OK | All checks passed: office.db readable, 3 webhook routes exist, 4 configs valid
- [2026-02-22 09:15 ET] INCIDENT: Core config files missing (office.yaml, integration.yaml, routing.yaml, security.yaml) - expected at /home/workspace/Zoffice/
2026-02-22 14:51:31 UTC | Healthcheck OK | DB: readable | Webhooks: vapi,github,stripe present | Configs: all 4 YAML valid
2026-02-22T15:20:12Z | HEALTHCHECK OK | office.db readable (DuckDB, 5 tables) | all 3 webhook routes present | all 4 configs valid
2026-02-22T16:45:00-05:00 | HEALTHCHECK OK | office.db readable | 3/3 webhooks present (vapi,github,stripe) | 4/4 configs valid (office,integration,routing,security)
2026-02-22T17:15:00-05:00 | HEALTHCHECK OK | office.db readable (DuckDB, 5 tables) | 3/3 webhooks present (vapi,github,stripe) | 4/4 configs valid (office,integration,routing,security)
- [OK] 2026-02-22T22:45:00Z - All checks passed: office.db readable, 3 webhook routes verified, 4 config files valid
2026-02-22T23:19:46Z | LAYER2_HEALTHCHECK | OK | DB readable, webhooks present (vapi/github/stripe), configs valid (office/integration/routing/security)

2026-02-23T01:57:00Z | LAYER2_HEALTHCHECK | OK | DB readable (DuckDB, 5 tables), webhooks present (vapi/github/stripe), configs valid (office/integration/routing/security)
2026-02-23T02:20:49Z HEALTHCHECK OK - All systems nominal: office.db readable, 3/3 webhook routes present, 4/4 configs valid
2026-02-23T02:50:00Z | HEALTHCHECK OK | DB readable, webhooks (vapi,github,stripe) present, configs valid
2026-02-22 22:15:00 ET | OK | All checks passed: office.db readable (DuckDB, 5 tables), webhooks present (vapi/github/stripe), configs valid (office/integration/routing/security)
2026-02-23 03:53:50 UTC | HEALTHCHECK OK | office.db readable, all 3 webhooks present, all 4 configs parse
2026-02-23T04:22:37Z | HEALTHCHECK OK | DB: readable (DuckDB, 5 tables) | Webhooks: vapi,github,stripe ✓ | Configs: office,integration,routing,security ✓
## 2026-02-22 23:50:00 ET — Healthcheck Failed

**Check 1 - office.db**: ✓ PASS (readable)

**Check 2 - Webhook routes**: ✓ PASS
- /api/zoffice/webhooks/vapi ✓
- /api/zoffice/webhooks/github ✓  
- /api/zoffice/webhooks/stripe ✓

**Check 3 - Core configs**: ✗ FAIL
- office.yaml: MISSING
- integration.yaml: MISSING
- routing.yaml: MISSING
- security.yaml: MISSING

**Action required**: Initialize Zoffice config files.

---

## 2026-02-23 05:20 UTC (Layer 2)
- **INCIDENT**: office.db not readable - "file is not a database" (sqlite3 error 26)
- Webhook routes: OK (vapi, github, stripe all present)
- Core configs: OK (office.yaml, integration.yaml, routing.yaml, security.yaml all parse)
2026-02-23T05:50:00Z | LAYER2_HEALTHCHECK | OK | DB readable (DuckDB, 5 tables), webhooks present (vapi/github/stripe), configs valid (office/integration/routing/security)
[2026-02-23T06:50:22Z] Zoffice Healthcheck Layer 2: ALL CHECKS PASSED - office.db readable (DuckDB), 3 webhooks present, 4 configs valid
2026-02-23T07:20:24Z | Zoffice Healthcheck | ALL OK | office.db (DuckDB, 5 tables), 3 webhook routes present, 4 configs valid
2026-02-23T07:50:40Z | HEALTHCHECK OK | DB: readable (DuckDB) | Routes: vapi/github/stripe ✓ | Configs: office/integration/routing/security ✓
2026-02-23T08:21:35Z [OK] All healthchecks passed: office.db readable, 3 webhooks present, 4 configs valid
2026-02-23T08:50:21Z [OK] All checks passed: office.db readable, 3 webhook routes present, 4 configs valid
2026-02-23T21:50:00Z [OK] All checks passed: office.db readable (DuckDB), 3 webhook routes present, 4 configs valid (config/office.yaml, integration.yaml, routing.yaml, security.yaml)
2026-02-23T22:20:48Z | HEALTHCHECK OK | office.db readable, all webhooks present, all configs valid
- [2026-02-23 22:50:00 UTC] **INCIDENT**: office.db not readable - sqlite3 reports "file is not a database". Webhook routes OK. Configs OK.
- [2026-02-23T23:19:33Z] OK - All checks passed (office.db readable, 3 webhook routes present, 4 configs valid)
2026-02-24T00:22:07+00:00 | HEALTHCHECK OK | office.db (DuckDB, 5 tables) | webhooks: vapi,github,stripe ✓ | configs: office,integration,routing,security ✓

## 2026-02-23 19:45:00 ET — Layer 2 Healthcheck

**Status: INCIDENTS DETECTED**

| Check | Result |
|-------|--------|
| office.db (DuckDB) | ✓ READABLE (5 tables: audit, contacts, conversations, decisions, evaluations) |
| /api/zoffice/webhooks/vapi | ✓ EXISTS |
| /api/zoffice/webhooks/github | ✓ EXISTS |
| /api/zoffice/webhooks/stripe | ✓ EXISTS |
| office.yaml | ✗ MISSING |
| integration.yaml | ✗ MISSING |
| routing.yaml | ✗ MISSING |
| security.yaml | ✗ MISSING |

**Action Required:** Core Zoffice configuration files missing from `/home/workspace/Zoffice/`. These may need to be created or restored from backup.
