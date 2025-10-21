#!/usr/bin/env python3
import os, json, time, logging, hashlib, random
from typing import Any, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
log = logging.getLogger("handler")

class IdempotencyStore:
    def __init__(self):
        self.enabled = True  # replace with real DB wiring
        self._data = {}  # stub for testing

    def checksum(self, payload: Dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def get(self, key: str, handler: str) -> Optional[Tuple[str, str]]:
        # return (status, checksum) or None; stub
        composite = f"{key}:{handler}"
        return self._data.get(composite)

    def put(self, key: str, handler: str, status: str, checksum: str) -> None:
        # insert or update; stub
        composite = f"{key}:{handler}"
        self._data[composite] = (status, checksum)

    def complete(self, key: str, handler: str, checksum: str) -> None:
        self.put(key, handler, "succeeded", checksum)

    def fail(self, key: str, handler: str, checksum: str) -> None:
        self.put(key, handler, "failed", checksum)

store = IdempotencyStore()

class RetryPolicy:
    def __init__(self, max_attempts: int = 5, base: float = 2.0, cap: float = 60.0, jitter: float = 0.2):
        self.max_attempts, self.base, self.cap, self.jitter = max_attempts, base, cap, jitter

    def backoff(self, attempt: int) -> float:
        delay = min(self.base * (2 ** (attempt - 1)), self.cap)
        j = delay * self.jitter
        return max(0.0, delay + random.uniform(-j, j))

retry = RetryPolicy()

REQUIRED_FIELDS = ("message_id", "schema_version", "correlation_id", "payload")
HANDLER_NAME = os.getenv("HANDLER_NAME", "childzo.processor")

class TransientError(Exception):
    pass

class PermanentError(Exception):
    pass

def validate(msg: Dict[str, Any]) -> None:
    for f in REQUIRED_FIELDS:
        if f not in msg:
            raise PermanentError(f"missing_field:{f}")

async def process_message(msg: Dict[str, Any]) -> None:
    # implement business logic; raise TransientError or PermanentError as needed
    return

async def handle(msg: Dict[str, Any]) -> str:
    validate(msg)
    key = msg.get("message_id") or msg.get("correlation_id")
    payload = msg.get("payload", {})
    csum = store.checksum(payload)

    existing = store.get(key, HANDLER_NAME)
    if existing:
        status, prev_csum = existing
        if prev_csum != csum:
            raise PermanentError("idempotency_conflict")
        if status == "succeeded":
            log.info(json.dumps({"event":"duplicate_suppressed","message_id":key,"handler":HANDLER_NAME}))
            return "duplicate"
        # status in {'failed','in_progress'} → allow reprocess
        log.info(json.dumps({"event":"replay_attempt","message_id":key,"handler":HANDLER_NAME,"prev_status":status}))
    else:
        store.put(key, HANDLER_NAME, "in_progress", csum)

    attempt = 0
    while True:
        attempt += 1
        try:
            t0 = time.time()
            await process_message(msg)
            dt = time.time() - t0
            store.complete(key, HANDLER_NAME, csum)
            log.info(json.dumps({"event":"processed","message_id":key,"handler":HANDLER_NAME,"latency_ms":int(dt*1000),"attempt":attempt}))
            return "processed"
        except TransientError as e:
            if attempt >= retry.max_attempts:
                store.fail(key, HANDLER_NAME, csum)
                raise
            delay = retry.backoff(attempt)
            log.warning(json.dumps({"event":"retry","message_id":key,"attempt":attempt,"delay_s":round(delay,2),"error":str(e)}))
            time.sleep(delay)
        except PermanentError as e:
            store.fail(key, HANDLER_NAME, csum)
            raise

# Integration hints (pseudo):
# - On receive: call await handle(msg). If it returns/does not raise → ACK. If TransientError bubbles and queue supports NACK → NACK to requeue. If PermanentError → send to DLQ.
