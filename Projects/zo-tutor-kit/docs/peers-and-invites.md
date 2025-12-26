---
created: 2025-12-01
last_edited: 2025-12-01
version: 1.0
---

# Peers and invite blobs (Phase 5A)

Phase 5A introduces a simple, file-based peer registry and invite/accept
workflow. This does **not** open any network connections; it only
standardizes how two Zos identify each other and which Tutor modes are
permitted.

## Peer registry

Peers are stored in a JSON file at the Tutor Kit repo root:

- `peers.json` next to `tutor_config.yaml`

You can see the current registry with:

```bash
python3 tutor_cli.py status
```

If a registry exists, it will list known peers and their allowed modes.

## Generating an invite (Teacher side)

From the Tutor Kit repo root:

```bash
python3 tutor_cli.py init --zo-id <your_zo_id>
python3 tutor_cli.py invite --peer-id other.zo --modes capability,knowledge --out /tmp/invite.txt
```

This writes a blob like:

```text
--- BEGIN ZO-TUTOR-INVITE ---
{ ...JSON payload... }
--- END ZO-TUTOR-INVITE ---
```

You can email `/tmp/invite.txt` to the other Zo's human.

## Accepting an invite (Student side)

After saving the invite blob to a file, e.g. `/tmp/invite.txt`:

```bash
python3 tutor_cli.py init --zo-id <your_zo_id>
python3 tutor_cli.py accept /tmp/invite.txt
```

This will:

- Parse the JSON payload from the blob (or from raw JSON if there are
  no markers).
- Register the peer under its `from_zo_id` in `peers.json`.
- Store the last invite and the allowed modes for future use.

This phase intentionally stops short of any live bridge. It only
establishes identity and permitted Tutor modes in a way that can be
carried via email or other out-of-band channels.

