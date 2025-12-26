---
created: 2025-12-01
last_edited: 2025-12-01
version: 1.0
---

# Live bridge MVP (Phase 5B)

Phase 5B introduces a minimal live "bridge" between Zos using a simple
TCP-based transport, time-to-live (TTL) metadata, and forensics logging.

This implementation is **demo-focused** and is not production-ready. It
runs in a trusted environment and only handles a single message per
listener invocation.

## Commands

From the Tutor Kit repo root (e.g. `Projects/zo-tutor-kit`):

### Start a bridge listener (Teacher side)

```bash
python3 tutor_cli.py bridge-listen --host 0.0.0.0 --port 62001
```

This will:

- Bind a TCP socket on the given host/port.
- Wait for exactly one JSON-line bridge message.
- Parse the embedded `session_start` metadata.
- Enforce TTL using the received `ttl_seconds` and `created_at`.
- Log the inbound bytes via the Tutor forensics logger.
- Exit after processing one message.

### Send a demo package (Student side)

In another shell (or on another Zo, pointing at the listener's host):

```bash
python3 tutor_cli.py bridge-send-demo --host 127.0.0.1 --port 62001 --mode capability --ttl 600
```

This will:

- Build a synthetic teaching package for the given mode
  (`capability`, `knowledge`, or `data`).
- Wrap it in a Tutor Protocol envelope that includes `session_start`
  metadata and a `DEMO_PACKAGE` message type.
- Log the outbound bytes via the forensics logger.
- Send the envelope as a single JSON-line over TCP to the listener.

## TTL behavior

The listener reconstructs a `SessionStart` from the received
`session_start` block and calls `is_expired()`.

- If the session is expired, the message is logged with an
  `EXPIRED_...` message type and a notice is printed.
- If the session is still valid, the message is logged under the normal
  `DEMO_PACKAGE` type.

In both cases, the bytes are accounted for via
`/home/workspace/Logs/tutor_sessions/<session_id>.log`.

## Notes

- This MVP does **not** yet use the peers registry or invites to
  automatically determine host/port.
- It is intended as a mechanical proof that:
  - we can send real Teaching Package payloads over a live bridge;
  - TTL enforcement works end-to-end; and
  - every byte is captured in the forensics logs.

