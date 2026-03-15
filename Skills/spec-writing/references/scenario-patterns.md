---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: n5os-ode-export
---

# Scenario Patterns by Build Type

Common scenario patterns to seed the spec-writing interview. Not exhaustive — use as starting points.

## API / Webhook Build

**Happy path:**
```
S1: Successful request
  Given: Service is running on port XXXX
  When: POST /endpoint with valid payload
  Then: Returns 200 with expected response shape
  Verify: curl -s -X POST -H "Content-Type: application/json" -d '{"key":"value"}' localhost:XXXX/endpoint | jq .status
```

**Common edge cases:**
```
S2: Malformed input
  Given: Service is running
  When: POST /endpoint with invalid JSON
  Then: Returns 400 with descriptive error message
  Verify: curl -s -X POST -d '{bad' localhost:XXXX/endpoint | jq .error

S3: Missing required field
  Given: Service is running
  When: POST /endpoint with payload missing required field
  Then: Returns 400 listing which fields are missing
  Verify: curl -s -X POST -H "Content-Type: application/json" -d '{}' localhost:XXXX/endpoint | jq .missing_fields

S4: Duplicate request (idempotency)
  Given: Request X was already processed
  When: Same request X arrives again
  Then: Returns same response, no duplicate side effects
  Verify: LLM: Send same request twice, verify database/state only reflects one operation
```

**Common failure modes:**
```
S5: Upstream dependency down
  Given: External API is unreachable
  When: Request arrives that requires external call
  Then: Returns 503 with retry-after header, logs error
  Verify: LLM: Check error handling code path exists and returns appropriate status

S6: Request timeout
  Given: Processing takes longer than threshold
  When: Request triggers slow operation
  Then: Returns within timeout, operation continues async or is cancelled
  Verify: timeout 5 curl -s localhost:XXXX/slow-endpoint; echo "exit: $?"
```

## Data Pipeline Build

**Happy path:**
```
S1: Full pipeline run
  Given: Source data exists at expected location
  When: Pipeline executes
  Then: Output data exists with expected row count and schema
  Verify: duckdb data.duckdb -c "SELECT count(*) FROM output_table"

S2: Incremental run
  Given: Pipeline has run before, new data added to source
  When: Pipeline executes again
  Then: Only new data processed, no duplicates
  Verify: duckdb data.duckdb -c "SELECT count(*) FROM output_table WHERE created_at > 'YYYY-MM-DD'"
```

**Common edge cases:**
```
S3: Empty source data
  Given: Source file exists but has 0 records
  When: Pipeline executes
  Then: Completes without error, output is empty or unchanged
  Verify: LLM: Check that empty input doesn't crash or corrupt existing data

S4: Malformed records
  Given: Source contains rows with missing/corrupt fields
  When: Pipeline executes
  Then: Valid rows processed, malformed rows logged to error table
  Verify: duckdb data.duckdb -c "SELECT count(*) FROM error_log WHERE run_date = 'YYYY-MM-DD'"

S5: Schema drift
  Given: Source adds a new column not in expected schema
  When: Pipeline executes
  Then: Pipeline handles gracefully (ignores extra columns or adapts)
  Verify: LLM: Check that pipeline doesn't fail on unexpected columns
```

## Frontend / Page Build

**Happy path:**
```
S1: Page renders
  Given: Service is running
  When: Browser navigates to /page
  Then: Page loads with expected content visible
  Verify: curl -s localhost:XXXX/page | grep -c "expected-text"

S2: Interactive element works
  Given: Page is loaded
  When: User clicks primary action button
  Then: Expected state change occurs (modal opens, data submits, navigation happens)
  Verify: LLM: Check that click handler exists and triggers correct state update
```

**Common edge cases:**
```
S3: Empty state
  Given: No data exists yet
  When: Page loads
  Then: Shows helpful empty state, not blank page or error
  Verify: LLM: Check for empty state rendering logic

S4: Mobile viewport
  Given: Screen width < 768px
  When: Page renders
  Then: Layout adapts, no horizontal scrolling, touch targets adequate
  Verify: LLM: Check for responsive CSS (media queries, flex/grid, min-width handling)
```

## Integration Build (connecting two systems)

**Happy path:**
```
S1: End-to-end flow
  Given: Both System A and System B are running
  When: Trigger event in System A
  Then: Expected effect in System B within timeout
  Verify: <check System B state after trigger>

S2: Data consistency
  Given: Record exists in System A
  When: Sync runs
  Then: Matching record exists in System B with correct field mapping
  Verify: LLM: Compare records in both systems for field-level consistency
```

**Common failure modes:**
```
S3: System B is down
  Given: System A is running, System B is unreachable
  When: Trigger event occurs
  Then: Event is queued/retried, not lost. System A doesn't crash.
  Verify: LLM: Check for retry logic or queue mechanism

S4: Conflicting updates
  Given: Same record modified in both systems
  When: Sync runs
  Then: Conflict resolved deterministically (last-write-wins, or flagged for review)
  Verify: LLM: Check conflict resolution strategy exists
```

## Hotline / Voice Build

**Happy path:**
```
S1: Successful call flow
  Given: Caller dials the number
  When: VAPI webhook receives call data
  Then: System prompt loaded, caller greeted, conversation flows
  Verify: LLM: Check webhook handler processes inbound call event correctly

S2: Post-call processing
  Given: Call ended with transcript available
  When: End-of-call webhook fires
  Then: Analysis runs, recap sent, data stored
  Verify: LLM: Check end-of-call handler triggers analysis pipeline
```

**Common edge cases:**
```
S3: Caller hangs up immediately
  Given: Call connects
  When: Caller disconnects within 5 seconds
  Then: No crash, minimal resources consumed, event logged
  Verify: LLM: Check that short-call scenario doesn't trigger full analysis pipeline

S4: Concurrent calls
  Given: Multiple callers active simultaneously
  When: Second call arrives while first is active
  Then: Both handled independently, no state bleed between calls
  Verify: LLM: Check for per-call state isolation (no shared mutable state)
```

## Skill / Automation Build

**Happy path:**
```
S1: Skill invocation
  Given: Skill exists at Skills/<name>/SKILL.md
  When: User says "run <skill>" or skill triggers match
  Then: SKILL.md instructions followed, expected output produced
  Verify: LLM: Check that SKILL.md body has clear, executable instructions

S2: Script execution
  Given: Script exists with --help
  When: Script runs with valid arguments
  Then: Expected output, exit code 0
  Verify: python3 Skills/<name>/scripts/<script>.py --help && echo "exit: $?"
```

---

## Writing Good Verify Clauses

**Prefer executable checks** (Zone 3 — deterministic):
- `curl -s URL | jq .field` — API response checks
- `duckdb data.duckdb -c "SELECT ..."` — Data state checks
- `test -f /path/to/file && echo "exists"` — File existence
- `python3 script.py --help` — Script runnability
- `grep -c "pattern" file` — Content checks

**Use LLM judgment** (Zone 2 — structured but semantic) when:
- Checking code quality or pattern adherence
- Evaluating error message quality
- Assessing UX/design decisions
- Verifying complex state that needs semantic understanding

**Format for LLM Verify:**
```
Verify: LLM: <Specific instruction for what to check and what "good" looks like>
```

Bad: `Verify: LLM: Check if it works`
Good: `Verify: LLM: Read the error handler in webhook.ts and verify it returns HTTP 400 for malformed payloads with a JSON error body containing a "message" field`
