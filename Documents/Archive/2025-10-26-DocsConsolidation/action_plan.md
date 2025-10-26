# ParentZo ↔ ChildZo Action Plan

Status: Draft v0.2 (2025-10-20)
Owner: Vibe Builder (worker)
Parent Thread: con_5eArZZYx1rzSFEmv

---

## Objectives
- Ship handlers, ACK semantics, minimal observability, and essential E2E tests.
- Keep ops simple (SQS FIFO + Postgres idempotency) with clear SLOs and rollback.

## Phases

### Phase 0 — Preconditions (0.5d)
- Decide transport: SQS FIFO (approved by default)
- Confirm schema approach: in-repo JSON Schema + version field
- Define SLOs and alert thresholds as per proposal
- Approve Postgres idempotency table design (below)

Exit: decisions documented; tickets created.

### Phase 1 — Handlers & Idempotency (1–2d)
- Implement validation + schema version gate
- Add idempotency store (key: message_id or natural key; handler; checksum)
- Error taxonomy + retry/backoff policy (exp 2→4→8→16→32→60s, jitter ±20%, max 5)
- Structured JSON logging with correlation fields

Exit: unit/integration tests pass; duplicate suppression validated.

### Phase 2 — ACK Semantics (0.5–1d)
- Explicit ACK/NACK wiring
- Visibility extension when elapsed > 50% of timeout; cap total window at 5× base
- Poison message → DLQ with full context

Exit: redelivery and DLQ scenarios verified.

### Phase 3 — Observability (0.5–1d)
- Metrics: throughput, success/fail, retries, DLQ, depth, p50/p95/p99 handler latency
- Dashboards: overview panel with the above
- Alerts: apply thresholds from proposal (availability, p95, DLQ rate, queue age)

Exit: dashboard live; alert dry-run validated.

### Phase 4 — E2E Test Matrix (1–2d)
- Fixtures (valid/invalid; N-1)
- Scenarios: happy path, duplicate, transient fail→retry, permanent fail→DLQ, slow downstream, restart mid-flight, DLQ replay
- CI job + coverage gate

Exit: green CI; reproducible runs.

### Phase 5 — Rollout (0.5–1d)
- Dark launch → mirror queue
- Ramp plan with holds (1%→10%→50%→100%)
- Manual rollback switch + announcement template

Exit: 100% traffic; 7-day hypercare.

## Concrete Tasks
- SQS
  - Create FIFO + DLQ; set VisibilityTimeout=60s, ReceiveWait=20s, maxReceiveCount=5
  - Producer: set MessageGroupId (natural key only if strict ordering needed)
- Idempotency (Postgres)
  - DDL:
    - idempotency_key TEXT not null
    - handler TEXT not null
    - checksum TEXT not null
    - status TEXT not null check (status in ('in_progress','succeeded','failed'))
    - occurred_at TIMESTAMPTZ not null default now()
    - ttl_at TIMESTAMPTZ not null default (now() + interval '30 days')
    - details JSONB null
    - unique (idempotency_key, handler)
    - index on ttl_at
  - Nightly cleanup job: delete where ttl_at < now()
- Alerts
  - Implement thresholds from proposal (availability, p95, DLQ rate, queue age)
- Tooling (later)
  - DLQ replay CLI and smoke generator (post-GA)

## Risks & Mitigations
- Hidden duplicate keys → checksum + natural key fallback
- Downstream flakiness → backoff + circuit breaker
- Schema drift → versioned schema; consumer-first deployment
- Alert fatigue → paging only on user-impacting symptoms

## Ownership
- Tech lead: TBD
- Handlers: TBD
- Observability: TBD
- QA/E2E: TBD

## References
- file 'Documents/System/ParentZo-ChildZo/production_proposal.md'
- file 'Documents/N5.md'
- file 'N5/prefs/prefs.md'
