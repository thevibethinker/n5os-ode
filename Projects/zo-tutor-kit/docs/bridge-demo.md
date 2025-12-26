---
created: 2025-12-01
last_edited: 2025-12-01
version: 1.0
---

# Bridge demo (Phase 5B)

Phase 5B introduces a minimal "live bridge" implementation using real
TCP sockets. It is still demo-focused and only processes **one**
message, but it exercises:

- SessionStart metadata and TTL handling
- Outbound + inbound logging via `log_message`
- Concrete network I/O over a host/port

## Commands

Two CLI commands drive the demo:

- `bridge-listen` – start a one-shot listener on a TCP port.
- `bridge-send-demo` – send a single demo teaching package over the
  bridge.

## Running the end-to-end demo

In one terminal (listener):

```bash
cd Projects/zo-tutor-kit
python3 tutor_cli.py bridge-listen --host 127.0.0.1 --port 62001
```

This will bind to the given host/port and wait for a single message.

In another terminal (sender), after the listener is up:

```bash
cd Projects/zo-tutor-kit
python3 tutor_cli.py bridge-send-demo \
  --host 127.0.0.1 \
  --port 62001 \
  --mode capability \
  --ttl 10
```

This will:

1. Construct a `SessionStart` with the requested mode and TTL.
2. Wrap a synthetic Teaching Package (same shape as `local-demo`) in a
   simple JSON envelope.
3. Log the outbound bytes via the forensics logger.
4. Send the envelope as a single JSON-line message over TCP.

On the listener side, the bridge will:

1. Read the JSON-line envelope.
2. Reconstruct a `SessionStart` from the embedded metadata.
3. Check whether the session is expired.
4. Log the inbound bytes via `log_message`.
5. Print a short summary including the session ID and message type.

All logs are written under `/home/workspace/Logs/tutor_sessions/`, with
one log file per `session_id`.


