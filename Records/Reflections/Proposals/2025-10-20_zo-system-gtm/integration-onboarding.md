# E2E Test Plan (Essential)

Scenarios

- Happy path (current + N-1 schema)
- Duplicate delivery (same message_id) → exactly one effect; log duplicate_suppressed
- Transient failure → retries then success; backoff bounds observed
- Permanent failure → DLQ with reason + metadata
- Slow downstream → visibility extension; no double-processing
- Restart mid-flight → safe reprocessing; no lost ACKs
- Replay from DLQ → idempotent re-apply; no duplicates

Fixtures

- valid_current.json, valid_n1.json, invalid_schema.json, transient_fail.json, permanent_fail.json

CI

- Run each scenario, assert metrics/logs conditions; archive golden logs

---

## Detailed Scenarios and Assertions

Legend: E2E-### test IDs, MI = metrics increment, LG = log assertion

### E2E-001 Happy path (current + N-1 schema)

Given: producer publishes valid_current.json and valid_n1.json\
When: consumer processes messages\
Then:

- Exactly one successful effect per message (idempotent apply) \[MI: processed_success_total += 2\]
- LG: level=info event=processed message_id= schema_version in {current, n-1}
- No DLQ entries \[MI: dlq_total unchanged\]

### E2E-002 Duplicate delivery (same message_id)

Given: two messages with identical message_id and payload valid_current.json\
When: both are delivered (in any order)\
Then:

- Exactly one effect applied \[MI: processed_success_total += 1\]
- Second delivery suppressed \[MI: duplicates_suppressed_total += 1\]
- LG: event=duplicate_suppressed message_id=

### E2E-003 Transient failure → retries then success

Given: transient_fail.json causes first N attempts to fail with retriable error\
When: consumer retries with backoff\
Then:

- LG: event=retry attempt=1..N backoff_ms within \[MIN_BACKOFF_MS, MAX_BACKOFF_MS\]
- Final attempt succeeds \[MI: processed_success_total += 1\]
- \[MI: processed_retry_total += N\]

### E2E-004 Permanent failure → DLQ

Given: permanent_fail.json triggers non-retriable error\
When: processed once\
Then:

- Message moved to DLQ with reason and metadata captured \[MI: dlq_total += 1\]
- LG: event=dlq message_id= reason=` metadata.contains(keys: schema_version, first_seen_at)`

### `E2E-005 Slow downstream → visibility extension; no double-processing`

`Given: handler sleeps > initial_visibility_timeout`\
`When: processing in-flight`\
`Then:`

- `Visibility extended at least once [MI: visibility_extensions_total += 1]`
- `No concurrent second consumer instance processes the same message [LG: no duplicate processing logs]`

### `E2E-006 Restart mid-flight → safe reprocessing; no lost ACKs`

`Given: consumer is terminated mid-processing (SIGTERM)`\
`When: service restarts`\
`Then:`

- `In-flight message becomes available again after visibility timeout`
- `Exactly one final successful effect [MI: processed_success_total += 1]`
- `No lost ACKs [LG: event=ack_success appears exactly once]`

### `E2E-007 Replay from DLQ → idempotent re-apply; no duplicates`

`Given: one message in DLQ (from E2E-004)`\
`When: DLQ replay tool republishes to main topic`\
`Then:`

- `If root cause fixed, exactly one effect; no duplicate side-effects`
- `[MI: dlq_replayed_total += 1] and [MI: processed_success_total += 1]`
- `LG: event=dlq_replay_success message_id=`

---

## `Metrics and Log Keys (Contract)`

- `Metrics (counters): `
  - `processed_success_total`
  - `processed_retry_total`
  - `duplicates_suppressed_total`
  - `dlq_total`
  - `dlq_replayed_total`
  - `visibility_extensions_total`
- `Gauges/Timers (optional): `
  - `handler_duration_ms`
  - `backoff_last_ms`
- `Logs (structured): `
  - `Common fields: ts, level, event, message_id, schema_version, attempt, backoff_ms, reason, metadata`

`Env for backoff bounds:`

- `MIN_BACKOFF_MS (e.g., 100)`
- `MAX_BACKOFF_MS (e.g., 5000)`
- `MAX_RETRY_ATTEMPTS (e.g., 5)`

---

## `Test Fixtures Mapping`

- `valid_current.json → schema=current, effect: create/update succeeds`
- `valid_n1.json → schema=n-1, backward compatibility`
- `invalid_schema.json → schema invalid, expect reject before processing`
- `transient_fail.json → handler raises retriable error N times then succeeds`
- `permanent_fail.json → handler raises non-retriable error immediately`

---

## `Test Harness Requirements`

- `Toggleable handler behavior based on fixture name`
- `Idempotency key: message_id`
- `DLQ interface: enqueue, list, replay`
- `Visibility control: configurable timeout + extension hook`
- `Deterministic logging with JSON lines`

---

## `CI Execution`

`Commands:`

```markdown
# Run all e2e tests
pytest -q -m e2e_proce

# Or run individually
pytest -q -k E2E_001
pytest -q -k E2E_002

# Archive golden logs (per run)
RUN_DIR="Documents/System/ParentZo-ChildZo/tests/golden/$(date -u +%Y%m%dT%H%M%SZ)" \
&& mkdir -p "$RUN_DIR" \
&& cp -r /var/log/proce/* "$RUN_DIR" || true
```

`Pytest markers (suggested):`

- `@pytest.mark.e2e_proce`
- `@pytest.mark.flaky(reruns=0)  # should be stable`

`Assertions (examples):`

- `Metrics: scrape /metrics endpoint and assert deltas`
- `Logs: jq filter for event keys and counts`
- `DLQ: count after scenario, then after replay`

---

## `Acceptance Criteria (Per Scenario)`

- `E2E-001: 2 successes, 0 DLQ, no retries`
- `E2E-002: 1 success, 1 duplicate_suppressed`
- `E2E-003: 1 success, processed_retry_total == N, backoff within bounds`
- `E2E-004: 0 success, 1 DLQ with reason+metadata`
- `E2E-005: visibility_extensions_total >= 1, no double-processing artifacts`
- `E2E-006: graceful restart, 1 final success, single ack_success`
- `E2E-007: dlq_replayed_total += 1, exactly one side-effect, no duplicates`

---

## `Notes`

- `Golden logs must be archived per CI run with timestamped directory`
- `For invalid_schema.json, ensure schema validation fails pre-handler and does not increment retries`
- `Ensure all IDs and timestamps are present for provenance`