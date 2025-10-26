# ParentZo ↔ ChildZo Production Checklist Proposal

Status: Draft v0.2 (2025-10-20)
Owner: Vibe Builder (worker)
Parent Thread: con_5eArZZYx1rzSFEmv

---

## Scope
Productionize the ParentZo ↔ ChildZo link: finalize processor handlers, ACK semantics, monitoring/alerting, and E2E test matrix. Output: checklists + clear acceptance criteria.

## Decisions (YAGNI-optimized)
- Transport: AWS SQS FIFO (managed, simple, durable)
  - FIFO, content-based dedup = ON
  - VisibilityTimeout = 60s; long polling = 20s; redrive maxReceiveCount = 5 → DLQ
  - MessageGroupId: natural key only if strict ordering required; otherwise a single group is acceptable
- Idempotency store: Postgres table in primary DB; TTL 30 days; nightly cleanup
- Observability: basic metrics + JSON logs only (no tracing/runbooks initially)
- Schema: in-repo JSON Schema validation + version field; no external schema registry
- E2E: essential scenarios only (see below)

## Architecture Summary
- Producer (ParentZo) → SQS FIFO → Consumer (ChildZo processors) → Side-effects (DB/API)
- DLQ for unrecoverable messages; lightweight replay CLI later (not in v0)
- Observability: metrics + JSON logs; SLOs with alerts

---

## Processor Handlers (Checklist)
- [ ] Input contract: schema version header + correlation/message IDs
- [ ] Validation: JSON Schema; on failure → DLQ with reason
- [ ] Idempotency: deterministic key (message_id or natural key)
- [ ] Exactly-once effect via idempotency record (key, handler, status, checksum, ttl)
- [ ] Retries: exponential backoff with jitter; classify retryable vs non-retryable
- [ ] Ordering: per-key ordering only if strictly required
- [ ] Timeouts: per call; cancel on shutdown
- [ ] Error taxonomy: normalized exceptions; no compensation hooks (defer)
- [ ] Poison detection: retry budget exceeded → DLQ with context
- [ ] Telemetry: handler timers, result counters
- [ ] Structured JSON logs: correlation_id, message_id, handler, attempt, outcome
- [ ] Health endpoints: liveness/readiness; dependency checks

## ACK Flow (Design)
- Receive → Validate → Process → Persist side-effects → Record idempotency → ACK
- NACK on transient failures to requeue with backoff; final fail → DLQ
- Duplicates: fast path drop via idempotency record; log duplicate_suppressed
- For long-running work, extend visibility; cap total processing window at 5× base

### ACK Checklist
- [ ] ACK only after all effects persisted and idempotency stored
- [ ] NACK on transient; include error class for telemetry
- [ ] Idempotency check before side-effects
- [ ] Visibility extension policy documented
- [ ] Backpressure guardrails (max concurrency; queue depth thresholds)

## Monitoring & Alerting (Minimal)

### Metrics
- ingest rate; success/fail; retry_count; dlq_count
- queue_depth; oldest_message_age; in_flight
- handler_latency p50/p95/p99
- idempotency_hits/misses; duplicate_rate

### Logs
- JSON logs; include message_id, correlation_id, handler, attempt, outcome

### SLOs & Alerts
- Availability: ≥ 99.9% per 10-min window
  - Page: < 99.5% for 15 min; Ticket: < 99.9% for 60 min
- Latency (receive→ACK): p95 < 1s, p99 < 3s
  - Page: p95 > 2s for 15 min; Ticket: p95 > 1.5s for 60 min
- DLQ rate: < 0.1%
  - Page: ≥ 1% for 10 min or > 50/min sustained; Ticket: ≥ 0.3% for 60 min
- Queue health: Page when oldest_message_age > 60s under steady-state

Checklist
- [ ] Overview dashboard: throughput, success, latency, DLQ, depth
- [ ] Alert rules as above
- [ ] Runbooks deferred (post-GA)

## E2E Tests (Essential Matrix)
- [ ] Happy path (current + N-1 schema)
- [ ] Duplicate delivery (same message_id) → single effect
- [ ] Transient failure → retry succeeds; verify backoff bounds
- [ ] Permanent failure → DLQ with reason + metadata
- [ ] Slow downstream → visibility extension; no double-processing
- [ ] Restart mid-flight → safe reprocessing, no lost ACKs
- [ ] Replay from DLQ → idempotent re-apply; no duplicates

Artifacts
- [ ] Fixtures (valid/invalid, N-1)
- [ ] Golden logs for regression
- [ ] CI job with per-scenario assertions

## Rollout & Ops
- [ ] Dark launch consumer on mirror queue
- [ ] Gradual traffic ramp (1% → 10% → 50% → 100%) with holds
- [ ] Error budget guardrails; manual rollback trigger
- [ ] Post-launch 7-day heightened monitoring

## Retention & Redaction
- DLQ: retain 14 days; include error taxonomy + minimal context
- Logs: 30 days; mask PII at emission (emails, phone, names)
- Idempotency records: 30 days; store checksum + identifiers only

## References
- file 'Documents/N5.md'
- file 'N5/prefs/prefs.md'
