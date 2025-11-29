---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# CRM V3 Enrichment Build Orchestration

**Mission:** Replace stub enrichment with real data sources (Aviato API + Gmail tools)

**Context:** Worker 7 discovered 9 queued enrichment jobs with stub data. Infrastructure exists but needs real integrations.

## Build Status

**Current State:**
- ✅ 61 profiles migrated
- ✅ 9 enrichment jobs queued
- ❌ Stub data (Aviato, Gmail, LinkedIn)
- ✅ Worker infrastructure operational

**Target State:**
- ✅ Real Aviato API calls
- ✅ Real Gmail thread analysis
- ⚠️ LinkedIn (stub with improvement)
- ✅ 9 jobs processed with real intelligence
- ✅ Production-ready enrichment system

## Worker Allocation

### Worker 1: Aviato Integration
**File:** `WORKER_1_AVIATO.md`
**Mission:** Replace Aviato stubs with real API calls using existing `/home/workspace/Integrations/Aviato/` SDK

**Deliverables:**
1. `/home/workspace/N5/scripts/enrichment/aviato_enricher.py` - Tool-based Aviato enrichment
2. Update `crm_enrichment_worker.py` to use real Aviato client
3. Test on 2-3 profiles with real API
4. Document API usage/costs

**Key Resources:**
- `file 'Integrations/Aviato/aviato_client.py'` - Working SDK
- `file 'Integrations/Aviato/crm_mapper.py'` - Field mapping
- API key ready in `.env`

### Worker 2: Gmail Integration
**File:** `WORKER_2_GMAIL.md`
**Mission:** Replace Gmail stubs with real `use_app_gmail` tool calls via prompts

**Deliverables:**
1. `/home/workspace/N5/workflows/gmail_thread_analyzer.prompt.md` - LLM prompt for Gmail analysis
2. `/home/workspace/N5/scripts/enrichment/gmail_enricher.py` - Wrapper invoking prompt
3. Update `crm_enrichment_worker.py` to use real Gmail tool
4. Test on profiles with known Gmail history

**Key Resources:**
- `use_app_gmail` tool (already connected)
- `gmail-find-email` for searching threads
- V's Gmail accounts connected

### Worker 3: LinkedIn Strategy
**File:** `WORKER_3_LINKEDIN.md`
**Mission:** Determine LinkedIn enrichment approach (defer scraping, improve stub, or API alternative)

**Deliverables:**
1. Decision document on LinkedIn approach
2. Improved stub with realistic fallback messaging
3. Future roadmap for LinkedIn data

**Approaches:**
- Option A: Keep stub, document as "Future enhancement"
- Option B: Use Aviato LinkedIn fields (many LinkedIn datapoints in Aviato)
- Option C: Defer to future worker with scraping infrastructure

### Worker 4: Integration Execution
**File:** `WORKER_4_EXECUTION.md`
**Mission:** Run enrichment worker with real integrations, process 9 queued jobs

**Deliverables:**
1. Execute enrichment on queued profiles
2. Validate intelligence quality in YAML files
3. Update database status tracking
4. Generate enrichment report

**Validation Criteria:**
- Real Aviato data in YAML (not stub)
- Real Gmail threads analyzed (not stub)
- Intelligence blocks properly formatted
- Database sync maintained

### Worker 5: Production Certification
**File:** `WORKER_5_CERTIFICATION.md`
**Mission:** Validate end-to-end enrichment, document system, certify production readiness

**Deliverables:**
1. Integration test suite (semantic, not just scripts)
2. Enrichment system documentation
3. Cost/usage tracking setup
4. Production sign-off

## Orchestration Flow

```
ORCHESTRATOR (Worker 7)
    │
    ├─→ Worker 1 (Aviato) ──────┐
    ├─→ Worker 2 (Gmail) ───────┤
    ├─→ Worker 3 (LinkedIn) ────┤
    │                            ↓
    │                      Worker 4 (Execute)
    │                            ↓
    └─→ Worker 5 (Certify) ←────┘
```

**Parallel:** Workers 1-3 can work concurrently
**Sequential:** Worker 4 waits for 1-3, Worker 5 waits for 4

## Success Criteria

**P0 - Must Have:**
- [ ] Real Aviato enrichment working
- [ ] Real Gmail thread analysis working
- [ ] 9 queued jobs processed
- [ ] No stub data in production profiles

**P1 - Should Have:**
- [ ] Cost tracking for API calls
- [ ] Error handling for API failures
- [ ] Rate limiting awareness
- [ ] Enrichment quality metrics

**P2 - Nice to Have:**
- [ ] LinkedIn enrichment (future)
- [ ] Automated enrichment triggers
- [ ] Enrichment scheduling optimization

## Architecture Principles

**Tool-First (P25):**
- Use existing tools (`use_app_gmail`, Aviato SDK)
- Invoke via prompts where possible
- Scripts only for orchestration

**LLM for Semantics:**
- Gmail thread synthesis → LLM prompt
- Intelligence formatting → LLM prompt
- Profile analysis → LLM understanding

**Scripts for Mechanics:**
- Database queries → SQL
- File operations → Python helpers
- Queue processing → Worker script

## Timeline

**Phase 1:** Workers 1-3 (Parallel) - 1 conversation each
**Phase 2:** Worker 4 (Sequential) - 1 conversation  
**Phase 3:** Worker 5 (Final) - 1 conversation

**Total:** 5 worker conversations orchestrated by this session

## Handoff Instructions

Each worker file contains:
1. **Mission statement** - Clear objective
2. **Context** - What exists, what's needed
3. **Deliverables** - Specific files/outputs
4. **Validation** - How to test completion
5. **Handoff** - What to pass to next worker

---

**Orchestrator:** Vibe Builder (con_rMaSw6rzVNkWvsQ4)
**Created:** 2025-11-18 00:04 EST

