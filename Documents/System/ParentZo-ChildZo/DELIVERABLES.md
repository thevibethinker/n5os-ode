# ParentZo ↔ ChildZo Production Deliverables

**Status:** Phase 1 scaffolding complete (2025-10-20)  
**Owner:** Vibe Builder (worker)  
**Parent Thread:** con_5eArZZYx1rzSFEmv

---

## Artifacts

### Planning & Design
- file 'Documents/System/ParentZo-ChildZo/production_proposal.md' (v0.2, YAGNI-optimized)
- file 'Documents/System/ParentZo-ChildZo/action_plan.md' (v0.2, 4 phases, 5-6d estimate)

### Infrastructure
- file 'Documents/System/ParentZo-ChildZo/migrations/001_create_idempotency_records.sql'
  - Postgres table with unique constraint on (idempotency_key, handler)
  - TTL-based cleanup; 30-day retention
- file 'Documents/System/ParentZo-ChildZo/scripts/create_sqs_queues.sh'
  - Creates SQS FIFO main + DLQ
  - Content-based dedup, 60s visibility, maxReceiveCount=5

### Code
- file 'Documents/System/ParentZo-ChildZo/scripts/handler_template.py'
  - Idempotency check (checksum-based)
  - Retry with exponential backoff + jitter
  - Structured logging (JSON)
  - DLQ replay support (reprocess 'failed' status)
  - Stub IdempotencyStore for testing

### Tests
- file 'Documents/System/ParentZo-ChildZo/tests/e2e_test_plan.md'
- file 'Documents/System/ParentZo-ChildZo/tests/test_e2e.py' (pytest harness)
- file 'Documents/System/ParentZo-ChildZo/tests/fixtures/' (5 fixtures)
  - Covers: happy path (current + N-1), duplicates, transient/permanent errors, invalid schema, replays, checksum conflicts

---

## Acceptance Criteria

### ✅ Completed
- [x] Proposal with decisions (transport, idempotency, SLOs, retention)
- [x] Action plan with phases, tasks, exit criteria
- [x] SQL migration for idempotency table
- [x] SQS queue creation script
- [x] Handler template with retry, logging, idempotency
- [x] E2E test plan + pytest harness
- [x] Test fixtures for essential scenarios
- [x] Documentation (READMEs, inline comments)

### ⏳ Next Phase
- [ ] Wire handler to real Postgres + SQS clients
- [ ] Deploy CloudWatch metrics + alerts
- [ ] Run E2E suite in staging
- [ ] Dark launch + gradual rollout
- [ ] Post-launch monitoring + runbooks

---

## Key Decisions

**Transport:** SQS FIFO with content-based dedup  
**Idempotency:** Postgres table, checksum-based, 30d TTL  
**Observability:** JSON logs + basic metrics (success rate, latency, DLQ depth)  
**SLOs:** ≥99.9% success per 10min; p95 latency <1s  
**Deferred:** Distributed tracing, detailed runbooks (post-GA)

---

## Next Steps

1. Review deliverables with tech lead
2. Assign ownership (handlers, observability, QA)
3. Provision AWS resources (queues, DB)
4. Implement real IdempotencyStore with psycopg3
5. Wire SQS consumer loop with long polling
6. Deploy metrics + alerts to CloudWatch
7. Run E2E suite in staging
8. Execute rollout plan (Phase 4)

---

## References

- file 'Documents/N5.md'
- file 'N5/prefs/prefs.md'
- Architecture principles (SSOT, modular, error handling, verify state)
