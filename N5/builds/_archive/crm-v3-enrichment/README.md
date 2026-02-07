---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# CRM V3 Enrichment Build Orchestration

**Mission:** Eliminate stub enrichment data, implement real integrations (Aviato + Gmail)

**Orchestrator:** Vibe Builder (con_rMaSw6rzVNkWvsQ4)

## Quick Start

### For V: How to Execute This Build

**Step 1:** Start 3 parallel conversations (Workers 1-3)

Open 3 new Zo conversations and paste these commands:

**Conversation 1:**
```
I am Worker 1 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/builds/crm-v3-enrichment/WORKER_1_AVIATO.md'
```

**Conversation 2:**
```
I am Worker 2 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/builds/crm-v3-enrichment/WORKER_2_GMAIL.md'
```

**Conversation 3:**
```
I am Worker 3 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/builds/crm-v3-enrichment/WORKER_3_LINKEDIN.md'
```

**Step 2:** Wait for all 3 to complete (marked ✅)

**Step 3:** Start Worker 4 (Sequential)
```
I am Worker 4 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/builds/crm-v3-enrichment/WORKER_4_EXECUTION.md'
```

**Step 4:** After Worker 4, start Worker 5 (Final)
```
I am Worker 5 in the CRM V3 Enrichment build orchestration.

Load and execute: file 'N5/builds/crm-v3-enrichment/WORKER_5_CERTIFICATION.md'
```

**Step 5:** Review production certification

Check: file '/home/.z/workspaces/{Worker 5 convo}/PRODUCTION_CERTIFICATION.md'

## What This Build Does

**Problem:** Worker 7 discovered 9 enrichment jobs with stub data:
```
⚠️ STUB DATA - Aviato API not yet integrated
⚠️ STUB DATA - use_app_gmail tool not yet integrated
⚠️ STUB DATA - LinkedIn API not yet integrated
```

**Solution:** Build real integrations

**Outcome:** Production-ready enrichment with real Aviato + Gmail data

## Worker Overview

| # | Mission | Input | Output |
|---|---------|-------|--------|
| **1** | Aviato API | Existing SDK | `aviato_enricher.py` |
| **2** | Gmail Tool | `use_app_gmail` | `gmail_enricher.py` + prompt |
| **3** | LinkedIn | Strategy decision | LinkedIn via Aviato |
| **4** | Execute | Workers 1-3 | 9 jobs processed |
| **5** | Certify | Worker 4 report | Production sign-off |

## Architecture

**Tool-First (P25):**
- Use existing Aviato SDK (already built)
- Use `use_app_gmail` tool (already connected)
- Prompts for LLM work (Gmail thread analysis)

**Division of Labor:**
- **Scripts:** API calls, file operations, queue processing
- **LLM:** Gmail thread synthesis, intelligence formatting
- **Semantic validation:** Profile quality assessment (not automated tests)

**Enrichment Flow:**
```
Profile → Queue → Worker → [Aviato API] → [Gmail Tool] → [LinkedIn via Aviato]
                               ↓              ↓              ↓
                          Intelligence → Intelligence → Intelligence
                               ↓              ↓              ↓
                          Append to YAML (append-only, chronological)
                                         ↓
                                   Update Database
```

## Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This file - quick start guide |
| `ORCHESTRATOR_PLAN.md` | Build strategy and worker allocation |
| `ORCHESTRATOR_MONITOR.md` | Live status tracking and coordination |
| `WORKER_1_AVIATO.md` | Aviato integration build spec |
| `WORKER_2_GMAIL.md` | Gmail integration build spec |
| `WORKER_3_LINKEDIN.md` | LinkedIn strategy build spec |
| `WORKER_4_EXECUTION.md` | Enrichment execution build spec |
| `WORKER_5_CERTIFICATION.md` | Production validation build spec |

## Success Criteria

**Must achieve:**
- ✅ Real Aviato data (not stubs)
- ✅ Real Gmail analysis (not stubs)
- ✅ LinkedIn strategy clear
- ✅ 9 jobs processed successfully
- ✅ Production certification issued

**Metrics:**
- Enrichment success rate: >80%
- Intelligence quality: Useful for CRM
- No hallucination: Verified semantically
- Cost tracking: Implemented

## Timeline Estimate

**Phase 1** (Parallel): 3 conversations, ~30min each
**Phase 2** (Sequential): 1 conversation, ~20min
**Phase 3** (Final): 1 conversation, ~20min

**Total:** ~2 hours orchestrated build time

## Key Resources

**Existing Infrastructure:**
- `file 'Integrations/Aviato/'` - Working SDK and API key
- `use_app_gmail` tool - Connected accounts
- `file 'N5/scripts/crm_enrichment_worker.py'` - Stub locations
- `file 'N5/data/crm_v3.db'` - Queue and profiles

**Documentation:**
- Aviato API: https://docs.data.aviato.co/
- Gmail tool: `list_app_tools("gmail")`

## For Orchestrator (Internal)

**Status tracking:** Update `ORCHESTRATOR_MONITOR.md` as workers complete

**Handoff verification:**
- Workers 1-3: Test commands run successfully
- Worker 4: Enrichment report generated
- Worker 5: Production certification issued

**Blocker resolution:** Orchestrator can directly fix issues if workers blocked

---

**Created:** 2025-11-18 00:04 EST
**Orchestrator:** con_rMaSw6rzVNkWvsQ4 (Vibe Builder)
**Status:** Ready to spawn workers

