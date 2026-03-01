---
name: zo2zo-relay
description: Manual Zo2Zo relay wrapper for skill sync and allowlisted arbitrary transfers over the substrate repository.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0.0"
created: 2026-03-01
last_edited: 2026-03-01
version: 1.0
provenance: con_1TdLAm1kG1JY0cs0
---

# zo2zo-relay

Manual command surface for Zo2Zo operations:
- skill sync (`send-skill`, `recv-skill`)
- skill bundle lane (`bundle-skill`)
- arbitrary allowlisted path transfer (`send-paths`, `pull-paths`, `list-drops`)

## Quick Start

```bash
python3 Skills/zo2zo-relay/scripts/zo2zo_relay.py check

python3 Skills/zo2zo-relay/scripts/zo2zo_relay.py send-skill --skills zo2zo-relay

python3 Skills/zo2zo-relay/scripts/zo2zo_relay.py send-paths \
  --paths "Documents/example.md,Knowledge" \
  --note "hotline context packet"

python3 Skills/zo2zo-relay/scripts/zo2zo_relay.py list-drops

python3 Skills/zo2zo-relay/scripts/zo2zo_relay.py pull-paths \
  --sender va \
  --transfer-id <id> \
  --dest /home/workspace/N5/data/zo2zo-relay/inbox
```

## Allowlist

Roots are configured in `Skills/zo2zo-relay/config/allowlist.yaml`.
Only paths under these roots can be transferred with `send-paths`.
