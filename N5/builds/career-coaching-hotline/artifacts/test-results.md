---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: con_nynLDLuDcCOLw8XD
drop_id: D4.1
---

# D4.1 Integration Test Results

**Run date:** 2026-02-14 03:55 ET  
**Test file:** `Skills/career-coaching-hotline/tests/integration-tests.ts`  
**Result:** 51 pass / 0 fail / 152 expect() calls / 4.43s

---

## 1. Server Startup Prerequisites (10/10 pass)

| Test | Status |
|------|--------|
| System prompt file exists and loads | ✅ |
| System prompt YAML frontmatter strips cleanly | ✅ |
| Concept map loads and parses as JSON | ✅ |
| Tool specs loads and has expected 6 tools | ✅ |
| Career stages doc exists | ✅ |
| Diagnostic questions doc exists | ✅ |
| Value prop tree doc exists | ✅ |
| Knowledge base has all 9 categories | ✅ |
| All concept map file references resolve to existing files | ✅ |
| Concept map resolves 10+ different aliases (actual: 150+ aliases → 20+ unique files) | ✅ |

## 2. Tool Handler Logic (11/11 pass)

| Test | Status |
|------|--------|
| assessCareerStage: early career → groundwork | ✅ |
| assessCareerStage: resume-focused → materials | ✅ |
| assessCareerStage: actively applying → outreach | ✅ |
| assessCareerStage: interviewing → performance | ✅ |
| assessCareerStage: career change → transition | ✅ |
| assessCareerStage: detects pain points (not_tailoring_resume, over_relying_on_ai_tools) | ✅ |
| assessCareerStage: detects calibration needed (student wanting VP role) | ✅ |
| getCareerRecommendations: returns actions for all 5 stages | ✅ |
| explainCareerConcept: resolves 11 known concepts to existing files | ✅ |
| explainCareerConcept: unknown concept returns graceful error | ✅ |
| collectFeedback: data structure validation | ✅ |

## 3. Database Tests (11/11 pass)

### career-coaching-calls DB (6 tables)

| Test | Status |
|------|--------|
| All 6 tables exist (caller_insights, caller_profiles, calls, daily_analysis, escalations, feedback) | ✅ |
| Insert + query: calls | ✅ |
| Insert + query: escalations | ✅ |
| Insert + query: feedback | ✅ |
| Insert + query: caller_profiles | ✅ |
| Phone index works for caller_profiles lookup | ✅ |

### career-hotline-calls DB (5 tables)

| Test | Status |
|------|--------|
| All 5 tables exist (caller_insights, caller_lookup, calls, escalations, feedback) | ✅ |
| Insert + query: calls | ✅ |
| Insert + query: caller_lookup | ✅ |
| Insert + query: escalations | ✅ |
| Insert + query: feedback | ✅ |

## 4. Webhook Integration (6/6 pass)

| Test | Status |
|------|--------|
| assistant-request payload structure valid (6 tools, system prompt, server messages) | ✅ |
| tool-calls routing: known tools identified, unknown tools handled | ✅ |
| tool-calls response format matches VAPI expectation (results array, toolCallId, stringified result) | ✅ |
| Auth: missing secret blocks request | ✅ |
| Auth: correct secret allows request | ✅ |
| Auth: no secret configured (open) allows all requests | ✅ |

## 5. Intake Pipeline (10/10 pass)

| Test | Status |
|------|--------|
| Phone normalization: 10-digit US → E.164 | ✅ |
| Phone normalization: with country code | ✅ |
| Phone normalization: formatted (555) 123-4567 | ✅ |
| Phone normalization: with dots 555.123.4567 | ✅ |
| Phone normalization: with spaces | ✅ |
| Phone normalization: invalid → null | ✅ |
| Fillout payload field extraction (name, phone, email, stage, help topic) | ✅ |
| Career stage resolution from Fillout answers (5 stages + null) | ✅ |
| Caller profile stored and queryable in DuckDB | ✅ |
| lookupCaller returns null for unknown numbers | ✅ |

## 6. Caller Lookup Module (3/3 pass)

| Test | Status |
|------|--------|
| generateUUID produces valid v4 UUIDs | ✅ |
| normalizePhone handles international + varied US formats | ✅ |
| lookupCaller with stored profile returns correct data | ✅ |

---

## Observations

1. **Two DuckDB files in use:** `career-hotline-calls/data.duckdb` (webhook server, call-logger) and `career-coaching-calls/data.duckdb` (intake-webhook). Both function correctly. The webhook server's `initDb()` creates tables in `career-hotline-calls`, while the intake webhook's `ensureTable()` creates `caller_profiles` in `career-coaching-calls`.

2. **Schema divergence:** The `escalations` table has different columns between the two DBs — `career-hotline-calls` has `pain_points`, `career-coaching-calls` has `booking_link_sent`. The `feedback` table also differs — `career-hotline-calls` has `helpful/rating/feedback_text/would_recommend`, `career-coaching-calls` has `caller_name/satisfaction/comment`.

3. **All concept map references resolve:** Every alias in the 150+ entry concept map points to an existing file on disk.

4. **Test data cleanup:** All tests clean up after themselves (DELETE after INSERT), leaving no test artifacts in the databases.
