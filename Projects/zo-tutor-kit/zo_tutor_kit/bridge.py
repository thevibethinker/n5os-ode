"""Minimal live bridge implementation for the Tutor Protocol (Phase 5B).

This module provides async helpers for:
- Listening for a single inbound bridge message on a TCP socket.
- Sending a single demo teaching package over the bridge.

The goal is to exercise:
- Live network I/O
- TTL enforcement using `SessionStart`
- Forensics logging via `log_message`

This is intentionally minimal and demo-focused. It is **not** a
production-ready transport and currently assumes a trusted environment.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from .tutor_protocol import SessionMode, SessionStart
from .logging_forensics import log_message


async def listen_once(host: str = "0.0.0.0", port: int = 62001) -> None:
    """Listen for **one** bridge message, then exit.

    This is a small, blocking helper intended to be driven from the CLI
    for demos. It accepts a single TCP connection, reads exactly one
    JSON-line message, enforces TTL based on the embedded `session_start`
    metadata, logs the message via `log_message`, and then exits.
    """

    done = asyncio.Event()

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            data = await reader.readline()
            if not data:
                return

            try:
                envelope: Dict[str, Any] = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                # Log malformed payload under an anonymous session.
                sha = hashlib.sha256(data).hexdigest()
                log_message(
                    session_id="unknown-session",
                    direction="inbound",
                    message_type="MALFORMED_ENVELOPE",
                    payload=data,
                    payload_sha256=sha,
                )
                return

            sess_info = envelope.get("session_start") or {}
            session_id = sess_info.get("session_id", "unknown-session")
            try:
                created_raw = sess_info["created_at"]
                created_at = datetime.fromisoformat(created_raw)
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                ttl_seconds = int(sess_info.get("ttl_seconds", 600))
                mode = sess_info.get("mode", "capability")  # type: ignore[assignment]
                peer_zo_id = sess_info.get("peer_zo_id", "unknown")
                session = SessionStart(
                    session_id=session_id,
                    peer_zo_id=peer_zo_id,
                    mode=mode,
                    ttl_seconds=ttl_seconds,
                    created_at=created_at,
                )
            except Exception:
                session = None

            message_type = envelope.get("message_type", "DEMO_PACKAGE")
            sha = hashlib.sha256(data).hexdigest()

            if session is not None and session.is_expired():
                log_message(
                    session_id=session_id,
                    direction="inbound",
                    message_type=f"EXPIRED_{message_type}",
                    payload=data,
                    payload_sha256=sha,
                )
                print(f"Received message for expired session {session_id}; logged and closing.")
            else:
                log_message(
                    session_id=session_id,
                    direction="inbound",
                    message_type=message_type,
                    payload=data,
                    payload_sha256=sha,
                )
                print(f"Received bridge message for session {session_id} (type={message_type}).")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            finally:
                done.set()

    server = await asyncio.start_server(handle, host, port)
    addrs = ", ".join(str(sock.getsockname()) for sock in (server.sockets or []))
    print(f"Listening for a single Tutor bridge message on {addrs}...")

    async with server:
        await done.wait()

    print("Bridge listener processed one message; exiting.")


async def send_demo_package(
    *,
    host: str,
    port: int,
    mode: SessionMode,
    ttl_seconds: int,
    package: Dict[str, Any],
    protocol_version: str,
) -> None:
    """Send a single demo teaching package over the bridge.

    This constructs a `SessionStart`, wraps the given `package` in a
    simple envelope, logs the outbound bytes, and sends them as one
    JSON-line message over TCP.
    """

    now = datetime.now(timezone.utc)
    session_id = f"bridge-demo-{mode}-{int(now.timestamp())}"

    session = SessionStart(
        session_id=session_id,
        peer_zo_id="remote-unknown",
        mode=mode,
        ttl_seconds=ttl_seconds,
        created_at=now,
    )

    envelope = {
        "protocol_version": protocol_version,
        "session_start": {
            "session_id": session.session_id,
            "peer_zo_id": session.peer_zo_id,
            "mode": session.mode,
            "ttl_seconds": session.ttl_seconds,
            "created_at": session.created_at.isoformat(),
        },
        "message_type": "DEMO_PACKAGE",
        "payload": {
            "mode": mode,
            "package": package,
        },
    }

    payload_bytes = json.dumps(envelope, separators=(",", ":")).encode("utf-8") + b"\n"
    sha = hashlib.sha256(payload_bytes).hexdigest()

    log_message(
        session_id=session_id,
        direction="outbound",
        message_type="DEMO_PACKAGE",
        payload=payload_bytes,
        payload_sha256=sha,
    )

    reader, writer = await asyncio.open_connection(host, port)
    try:
        writer.write(payload_bytes)
        await writer.drain()
        print(f"Sent demo {mode} package over bridge (session_id={session_id}).")
    finally:
        writer.close()
        await writer.wait_closed()

