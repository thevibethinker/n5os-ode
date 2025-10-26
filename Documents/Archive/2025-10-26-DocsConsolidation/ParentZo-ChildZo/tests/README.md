# E2E Tests for ParentZo-ChildZo Message Processing

## Overview

Comprehensive E2E test suite covering idempotency, retries, DLQ, visibility extensions, and replay scenarios.

## Test IDs

- **E2E-001**: Happy path (current + N-1 schema)
- **E2E-002**: Duplicate delivery suppression
- **E2E-003**: Transient failure → retries with backoff
- **E2E-004**: Permanent failure → DLQ
- **E2E-005**: Slow handler → visibility extension
- **E2E-006**: Restart mid-flight → safe reprocessing
- **E2E-007**: DLQ replay → idempotent re-apply

## Prerequisites

### 1. Start Localstack (SQS)

```bash
docker run -d -p 4566:4566 --name localstack localstack/localstack
```

### 2. Create Queues

```bash
bash Documents/System/ParentZo-ChildZo/scripts/create_sqs_queues.sh
```

### 3. Install Dependencies

```bash
pip install pytest requests boto3
```

### 4. Start Consumer Service

```bash
python3 Documents/System/ParentZo-ChildZo/scripts/consumer.py &
```

Make sure it exposes:
- Metrics endpoint: `http://localhost:9090/metrics`
- Health check: `http://localhost:8080/health`
- Logs to: `/var/log/proce/consumer.log`

## Running Tests

### Run All E2E Tests

```bash
cd Documents/System/ParentZo-ChildZo
pytest -m e2e_proce
```

### Run Individual Test

```bash
pytest tests/test_e2e_proce.py::TestE2EProcessing::test_e2e_001_happy_path_current_and_n1_schema -v
```

### Run Specific Test IDs

```bash
pytest -k E2E_001
pytest -k E2E_002
pytest -k "E2E_003 or E2E_004"
```

### Run with Detailed Output

```bash
pytest -m e2e_proce -vv --log-cli-level=DEBUG
```

### Run and Generate Coverage

```bash
pytest -m e2e_proce --cov=scripts --cov-report=html
```

## Test Fixtures

Located in `tests/fixtures/`:

- `valid_current.json` - Current schema version
- `valid_n1.json` - N-1 schema (backward compatibility)
- `invalid_schema.json` - Invalid schema (should reject)
- `transient_fail.json` - Triggers retriable errors
- `permanent_fail.json` - Triggers non-retriable error → DLQ

## Test Helpers

`test_helpers.py` provides:

- **MetricsChecker**: Query Prometheus metrics, compute deltas
- **LogValidator**: Parse and query structured JSON logs
- **MessagePublisher**: Publish messages to SQS
- **DLQManager**: Inspect and replay DLQ messages
- **ConsumerManager**: Start/stop/restart consumer service

## Metrics Contract

Tests expect these Prometheus metrics:

- `processed_success_total` (counter)
- `processed_retry_total` (counter)
- `duplicates_suppressed_total` (counter)
- `dlq_total` (counter)
- `dlq_replayed_total` (counter)
- `visibility_extensions_total` (counter)

## Log Contract

Tests expect structured JSON logs with fields:

- `ts` - Timestamp
- `level` - Log level (info, warn, error)
- `event` - Event type (processed, retry, dlq, etc.)
- `message_id` - Message identifier
- `schema_version` - Schema version
- `attempt` - Retry attempt number
- `backoff_ms` - Backoff duration in milliseconds
- `reason` - Error/failure reason
- `metadata` - Additional context

## Environment Variables

Configure these for consumer service:

- `MIN_BACKOFF_MS=100`
- `MAX_BACKOFF_MS=5000`
- `MAX_RETRY_ATTEMPTS=5`
- `VISIBILITY_TIMEOUT_SECONDS=30`
- `SQS_QUEUE_URL=http://localhost:4566/000000000000/proce-main`
- `DLQ_URL=http://localhost:4566/000000000000/proce-dlq`

## Golden Logs

After each CI run, logs are archived to:

```
tests/golden/YYYYMMDDTHHMMSSZ/
  consumer.log
  metrics.txt
```

To archive manually:

```bash
RUN_DIR="tests/golden/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN_DIR"
cp /var/log/proce/consumer.log "$RUN_DIR/"
curl -s http://localhost:9090/metrics > "$RUN_DIR/metrics.txt"
```

## Troubleshooting

### Localstack not responding

```bash
docker ps | grep localstack
docker logs localstack
```

### Consumer not starting

```bash
python3 Documents/System/ParentZo-ChildZo/scripts/consumer.py
# Check logs for startup errors
```

### Tests hanging

- Check if consumer is processing messages: `tail -f /var/log/proce/consumer.log`
- Check queue depth: `aws sqs get-queue-attributes --endpoint-url http://localhost:4566 --queue-url http://localhost:4566/000000000000/proce-main --attribute-names All`

### Metrics not available

- Verify metrics endpoint: `curl http://localhost:9090/metrics`
- Check consumer is exposing metrics server

## CI Integration

Add to your CI pipeline:

```yaml
test_e2e:
  script:
    - docker run -d -p 4566:4566 localstack/localstack
    - sleep 5  # Wait for localstack
    - bash Documents/System/ParentZo-ChildZo/scripts/create_sqs_queues.sh
    - python3 Documents/System/ParentZo-ChildZo/scripts/consumer.py &
    - sleep 2  # Wait for consumer
    - pytest -m e2e_proce --junitxml=report.xml
    - mkdir -p golden/$(date -u +%Y%m%dT%H%M%SZ)
    - cp -r /var/log/proce/* golden/$(date -u +%Y%m%dT%H%M%SZ)/
  artifacts:
    paths:
      - report.xml
      - golden/
```

## Next Steps

1. Implement consumer service (`scripts/consumer.py`)
2. Add metrics export (Prometheus format)
3. Implement handler logic with test config support
4. Run tests and validate all scenarios pass
5. Archive first golden logs as baseline

---

**Test Infrastructure Version:** 1.0  
**Last Updated:** 2025-10-20  
**Status:** Ready for implementation
