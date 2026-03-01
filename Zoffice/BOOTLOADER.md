---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: con_6F6fVNruJQtAc6zW
---

# @bootloader — Zoffice Local Setup

Use this file as the canonical bootloader for setting up Zoffice on a local Zo instance.

## Objective

Install a fully runnable local Zoffice, then stage it in `shadow` mode as the control plane before cutover.

## Inputs

- Release bundle path (default): `Zoffice/releases/v2.0.0-rc1/zoffice-v2.0.0-rc1.tar.gz`
- Bundle checksum path: `Zoffice/releases/v2.0.0-rc1/bundle.sha256`
- Acceptance contract: `Zoffice/contracts/mutual-acceptance-v2.0.0-rc1.json`

## Step 1: Verify Release Artifact

```bash
cd /home/workspace
sha256sum -c Zoffice/releases/v2.0.0-rc1/bundle.sha256
```

Expected: `OK`.

## Step 2: Expand or Sync Zoffice Tree

```bash
cd /home/workspace
tar -xzf Zoffice/releases/v2.0.0-rc1/zoffice-v2.0.0-rc1.tar.gz
```

## Step 3: Run Health Checks

```bash
cd /home/workspace
python3 Zoffice/scripts/healthcheck.py
python3 Zoffice/scripts/layer2_smoke_test.py
```

Expected: all checks pass.

## Step 4: Activate Controller Shadow Mode

```bash
cd /home/workspace
python3 Zoffice/scripts/control_plane.py status
```

Mode should be `shadow` until parity samples are complete.

## Step 5: Personalize This Instance

Run `@personalize` using `file 'Zoffice/PERSONALIZE.md'`.

## Step 6: Route External Channels to Zoffice

- VAPI webhook URL: `https://<handle>.zo.space/api/zoffice/webhooks/vapi`
- GitHub webhook URL: `https://<handle>.zo.space/api/zoffice/webhooks/github`
- Stripe webhook URL: `https://<handle>.zo.space/api/zoffice/webhooks/stripe`

Required secrets in Zo Advanced settings:
- `VAPI_WEBHOOK_SECRET`
- `GITHUB_WEBHOOK_SECRET`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

## Step 7: Shadow Validation

During shadow testing, append parity samples:

```bash
python3 Zoffice/scripts/control_plane.py shadow-sample --passed
```

Once `parity_samples_passed >= parity_samples_required`, status moves to `ready_for_cutover`.

## Step 8: Cutover (Only After Rebuild Proof)

When target reports `100% integrity rebuild`:

```bash
python3 Zoffice/scripts/control_plane.py cutover --integrity-rebuild-percent 100
```

This marks:
- controller mode `cutover`
- legacy schedulers disabled in control state
- contract mutually accepted and effective

