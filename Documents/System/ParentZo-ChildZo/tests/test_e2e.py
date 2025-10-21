#!/usr/bin/env python3
"""E2E test harness for ParentZo<->ChildZo message processing."""
import pytest, json, asyncio, logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from handler_template import handle, store, TransientError, PermanentError, process_message

logging.basicConfig(level=logging.INFO)

FIXTURES = Path(__file__).parent / "fixtures"

def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())

@pytest.fixture
def reset_store():
    """Reset idempotency store between tests."""
    store._data = {}  # stub reset
    yield
    store._data = {}

@pytest.mark.asyncio
async def test_happy_path_current(reset_store, monkeypatch):
    """Happy path with current schema."""
    msg = load_fixture("valid_current.json")
    monkeypatch.setattr("handler_template.process_message", AsyncMock())
    
    result = await handle(msg)
    assert result == "processed"

@pytest.mark.asyncio
async def test_happy_path_n1(reset_store, monkeypatch):
    """Happy path with N-1 schema."""
    msg = load_fixture("valid_n1.json")
    monkeypatch.setattr("handler_template.process_message", AsyncMock())
    
    result = await handle(msg)
    assert result == "processed"

@pytest.mark.asyncio
async def test_duplicate_suppression(reset_store, monkeypatch, caplog):
    """Duplicate delivery → exactly one effect."""
    msg = load_fixture("valid_current.json")
    monkeypatch.setattr("handler_template.process_message", AsyncMock())
    
    # First delivery
    result1 = await handle(msg)
    assert result1 == "processed"
    
    # Second delivery (duplicate)
    result2 = await handle(msg)
    assert result2 == "duplicate"
    assert "duplicate_suppressed" in caplog.text

@pytest.mark.asyncio
async def test_transient_retry_then_success(reset_store, monkeypatch, caplog):
    """Transient failure → retries then success."""
    msg = load_fixture("transient_fail.json")
    
    call_count = 0
    async def mock_process(m):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise TransientError("downstream_unavailable")
    
    monkeypatch.setattr("handler_template.process_message", mock_process)
    
    result = await handle(msg)
    assert result == "processed"
    assert call_count == 3
    assert "retry" in caplog.text

@pytest.mark.asyncio
async def test_permanent_failure_dlq(reset_store, monkeypatch):
    """Permanent failure → raise for DLQ."""
    msg = load_fixture("permanent_fail.json")
    
    async def mock_process(m):
        raise PermanentError("invalid_operation")
    
    monkeypatch.setattr("handler_template.process_message", mock_process)
    
    with pytest.raises(PermanentError, match="invalid_operation"):
        await handle(msg)

@pytest.mark.asyncio
async def test_invalid_schema(reset_store):
    """Invalid schema → permanent error."""
    msg = load_fixture("invalid_schema.json")
    
    with pytest.raises(PermanentError, match="missing_field"):
        await handle(msg)

@pytest.mark.asyncio
async def test_replay_from_dlq(reset_store, monkeypatch, caplog):
    """Replay from DLQ → idempotent re-apply."""
    msg = load_fixture("permanent_fail.json")
    
    # First attempt: fail
    async def mock_fail(m):
        raise PermanentError("temporary_issue")
    
    monkeypatch.setattr("handler_template.process_message", mock_fail)
    
    with pytest.raises(PermanentError):
        await handle(msg)
    
    # Replay: succeed
    monkeypatch.setattr("handler_template.process_message", AsyncMock())
    
    result = await handle(msg)
    assert result == "processed"
    assert "replay_attempt" in caplog.text

@pytest.mark.asyncio
async def test_checksum_conflict(reset_store, monkeypatch):
    """Different payload with same message_id → conflict error."""
    msg1 = load_fixture("valid_current.json")
    monkeypatch.setattr("handler_template.process_message", AsyncMock())
    
    await handle(msg1)
    
    # Modify payload
    msg2 = msg1.copy()
    msg2["payload"] = {"op": "different", "value": 999}
    
    with pytest.raises(PermanentError, match="idempotency_conflict"):
        await handle(msg2)

# TODO: Add tests for slow downstream (visibility extension) and restart mid-flight when real queue integration exists

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
