---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: con_6F6fVNruJQtAc6zW
---

# @personalize — Zoffice Instance Personalization

Use this file to personalize a local Zoffice install on a Zo instance.

## Goal

Bind Zoffice to the target instance identity, channel endpoints, and preferred operating behavior before cutover.

## Personalization Fields

Update these files in order:

1. `Zoffice/config/office.yaml`
- `office.handle` (target Zo handle)
- `office.owner` (owner label)
- `office.domain` (`<handle>.zo.space`)
- `office.parent` (if this instance has a parent office)

2. `Zoffice/config/security.yaml`
- `security.trust.trusted_instances`
- `security.trust.trusted_domains`
- environment key names under `security.api_keys`

3. `Zoffice/config/integration.yaml`
- webhook URLs and provider states
- scheduler agent IDs
- persona IDs
- acceptance status

4. `Zoffice/staff/registry.yaml`
- ensure each staff role has the correct `zo_persona_id`

## Recommended Persona Mapping

- Receptionist: front-door routing for voice/sms/zo2zo
- Chief of Staff: operations and inbox/webhooks
- Librarian: knowledge intake, classification, and publishing pipeline
- Controller: top-level control plane (`Zoffice Controller`)

## Quick Validation After Personalization

```bash
cd /home/workspace
python3 Zoffice/scripts/layer2_smoke_test.py
python3 Zoffice/scripts/control_plane.py status
```

Expected:
- smoke test pass
- controller still in `shadow` until cutover gate

## Cutover Preconditions

All must be true:

- `@bootloader` completed successfully
- shadow parity complete (`ready_for_cutover`)
- target instance reports `100% integrity rebuild`
- mutual acceptance contract exists and producer signature is present

## Finalize Cutover

```bash
cd /home/workspace
python3 Zoffice/scripts/control_plane.py cutover --integrity-rebuild-percent 100
```

