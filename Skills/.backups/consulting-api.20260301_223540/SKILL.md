---
name: consulting-api
description: API communication layer for the Zoffice Consultancy Stack. Handles skill bundle creation, validation, and transmission between va and zoputer instances.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
  created: "2026-02-06"
  build: consulting-zoffice-stack
  drop: D1.3
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_GwlFHPrBi5KsNm1X
---

# Consulting API

## Purpose

Manages the creation, validation, and transmission of skill bundles between va.zo.computer and zoputer.zo.computer in the Zoffice Consultancy Stack.

## Usage

```bash
# Create a skill bundle
python3 Skills/consulting-api/scripts/bundle_manager.py create --skill security-gate --output /tmp/bundle.json

# Validate a bundle before transmission
python3 Skills/consulting-api/scripts/bundle_manager.py validate --bundle /tmp/bundle.json

# List all exportable skills
python3 Skills/consulting-api/scripts/bundle_manager.py list-exportable

# Transmit a bundle to zoputer
python3 Skills/consulting-api/scripts/bundle_manager.py transmit --bundle /tmp/bundle.json --target zoputer

# Generate daily export manifest
python3 Skills/consulting-api/scripts/bundle_manager.py manifest --output /tmp/manifest.json
```

## Integration

This skill is used by:
- **librarian-export** (D3.1): Daily export pipeline
- **security-gate** (D1.1): Pre-transmission validation
- **audit-system** (D1.2): Logs all transmissions

## Exportable Skills Registry

The following skills are registered for export:
- security-gate
- audit-system
- consulting-api
- content-classifier
- librarian-export

To add a new skill to the registry, edit `EXPORTABLE_SKILLS` in `bundle_manager.py`.
