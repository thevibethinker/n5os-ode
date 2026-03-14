---
created: 2026-03-13
last_edited: 2026-03-13
version: 1.0
provenance: con_hs2l0mnC3kX6g5tx
type: release_review
status: draft
---

# Zoffice Release Review — v2.0.0-rc3

## Outcome

Created a new local review release at `Zoffice/releases/v2.0.0-rc3/` and stopped before any transfer to Zoputer.

## What changed in this build

### 1. Canonical product story clarified
Created build artifacts that make the current package boundary explicit:
- `N5/builds/zoffice-externalization/artifacts/architecture-reconciliation.md`
- `N5/builds/zoffice-externalization/artifacts/substrate-absorption-map.md`
- `N5/builds/zoffice-externalization/artifacts/supersession-plan.md`
- `N5/builds/zoffice-externalization/artifacts/package-readiness-checklist.md`

### 2. Substrate transfer-safety absorbed into Zoffice
Added:
- `Zoffice/capabilities/zo2zo/sanitizer.py`

Updated:
- `Zoffice/capabilities/zo2zo/README.md`

This makes transfer-safety part of the in-package `zo2zo` capability instead of requiring a substrate-first explanation.

### 3. Release machinery hardened
Updated:
- `Zoffice/scripts/create_release_bundle.py`

Hardening effects:
- excludes all `releases/` content from new bundles
- excludes runtime conversation logs
- excludes `data/office.db` from the shipped package
- preserves versioned-output behavior

### 4. Root metadata and control-plane references normalized
Updated the canonical product surface so it now points at `v2.0.0-rc3` instead of stale rc1-era release references:
- `Zoffice/BOOTLOADER.md`
- `Zoffice/MANIFEST.json`
- `Zoffice/config/office.yaml`
- `Zoffice/config/integration.yaml`
- `Zoffice/config/controller.yaml`
- `Zoffice/scripts/layer2_smoke_test.py`
- `Zoffice/scripts/control_plane.py`
- `Zoffice/scripts/create_release_bundle.py`
- `Zoffice/contracts/mutual-acceptance-v2.0.0-rc3.json`

## Validation run

### Product checks
- `python3 Zoffice/scripts/healthcheck.py` → PASS (42/42)
- `python3 Zoffice/scripts/layer2_smoke_test.py` → PASS
- product-surface version references normalized to rc3

### Packaging checks
- `python3 Zoffice/scripts/create_release_bundle.py --version v2.0.0-rc3 --dry-run` → PASS
- `python3 Zoffice/scripts/create_release_bundle.py --version v2.0.0-rc3` → PASS
- Manifest inspection confirms:
  - no nested `releases/` content
  - no `data/office.db`
  - no `data/conversations/` runtime artifacts
- Tarball inspection confirms the same exclusions
- `sha256sum -c bundle.sha256` → PASS

## Release contents

Release folder:
- `Zoffice/releases/v2.0.0-rc3/bundle-manifest.json`
- `Zoffice/releases/v2.0.0-rc3/bundle.sha256`
- `Zoffice/releases/v2.0.0-rc3/zoffice-v2.0.0-rc3.tar.gz`

Manifest file count: 102

## What this version now supersedes

As deployment story / package source, this version supersedes:
- `N5/builds/n5os-rice/`
- `N5/builds/rice-core/`
- `N5/builds/rice-capabilities/`
- `N5/builds/rice-staff/`
- `N5/builds/rice-integration/`
- `N5/builds/consulting-zoffice-stack/` (reference only)

It does **not** supersede the core operating functionality of this live device.

## Remaining caveats

- The old rc1 contract file remains in `Zoffice/contracts/` as a historical artifact; it no longer defines the current release.
- `zoputer-substrate/` still contains duplicate historic Zoffice release artifacts; these were not destructively removed in this build.
- This release is review-ready, not transfer-complete.

## Next human review question

Does `v2.0.0-rc3` feel like the first version whose package can be understood from `Zoffice/` and its release folder alone, without needing the old Rice/substrate deployment story?
