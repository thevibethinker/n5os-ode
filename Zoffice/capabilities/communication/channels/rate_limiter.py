"""
Communication — Rate Limiter

In-memory deduplication and rate limiting for outbound messages.
Blocks duplicate messages (same recipient + same content hash) within a time window.
Not persistent across restarts (Layer 1).
"""

import time

# In-memory store: {(recipient, content_hash): timestamp}
_send_log: dict[tuple[str, str], float] = {}

DEFAULT_WINDOW_SECONDS = 300


def check_rate_limit(
    recipient: str,
    content_hash: str,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
) -> dict:
    """
    Check if a message should be rate-limited.

    Args:
        recipient: The recipient identifier (email, phone, etc.).
        content_hash: Hash of the message content.
        window_seconds: Time window in seconds for deduplication.

    Returns:
        dict with keys: allowed (bool), reason (str)
    """
    key = (recipient, content_hash)
    now = time.time()

    if key in _send_log:
        last_sent = _send_log[key]
        elapsed = now - last_sent
        if elapsed < window_seconds:
            return {
                "allowed": False,
                "reason": f"Duplicate message within rate limit window ({int(elapsed)}s ago)",
            }

    return {
        "allowed": True,
        "reason": "No recent duplicate found",
    }


def record_send(recipient: str, content_hash: str) -> None:
    """Record that a message was sent (for future rate limit checks)."""
    _send_log[(recipient, content_hash)] = time.time()


def clear() -> None:
    """Clear the send log (for testing)."""
    _send_log.clear()
