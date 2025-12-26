"""Simple sandbox manager for Tutor sessions.

For now this only creates per-session directories under a fixed root.
Later we can extend this with stricter isolation and cleanup policies.
"""

from __future__ import annotations

from pathlib import Path


SANDBOX_ROOT = Path("/home/workspace/TutorSandboxes")


def get_session_sandbox(session_id: str) -> Path:
    """Return the sandbox path for a given session ID.

    This does **not** create the directory; callers can use
    :func:`ensure_session_sandbox` when they need it.
    """

    return SANDBOX_ROOT / session_id


def ensure_session_sandbox(session_id: str) -> Path:
    """Ensure the sandbox directory for this session exists and return it."""

    path = get_session_sandbox(session_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sandbox_exists(session_id: str) -> bool:
    """Return True if a sandbox for this session already exists."""

    return get_session_sandbox(session_id).exists()

