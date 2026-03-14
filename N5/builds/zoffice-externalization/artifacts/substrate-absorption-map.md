---
created: 2026-03-13
last_edited: 2026-03-13
version: 1.0
provenance: con_hs2l0mnC3kX6g5tx
type: absorption_map
status: draft
---

# Substrate Absorption Map

## Decision rule

Every meaningful substrate element must land in one of three buckets:

1. **Absorb into exported Zoffice now**
2. **Retain as local factory/reference support**
3. **Deprecate from the deployment story**

## Bucket 1 — Absorb into exported Zoffice now

### `shared/sanitizer/sanitizer.py`
**Disposition:** Absorb conceptually and operationally into `Zoffice/capabilities/zo2zo/`

**Why:** It provides deterministic prompt-injection protection for inter-Zo transfer. That is part of the exported office’s transfer capability, not merely a local factory concern.

**Action:** Add a sanitizer module under the Zoffice `zo2zo` capability and document it as the canonical transfer-safety layer.

### `Skills/zo2zo-relay/`
**Disposition:** Absorb the relay model into `Zoffice/capabilities/zo2zo/`

**Why:** Manual/path-based transfer and skill relay are part of substrate transfer capability. The exported office should know how this works without requiring a separate substrate-first mental model.

**Action:** Add relay documentation and code surface under `Zoffice/capabilities/zo2zo/` or document the in-package equivalent clearly.

## Bucket 2 — Retain as local factory/reference support

### `zoputer-substrate/shared/docs/ZOPUTER_SYSTEM_BRIEF.md`
**Disposition:** Local/reference

**Why:** This is target-instance-specific orientation material for zoputer, not generic Zoffice package logic.

### `zoputer-substrate/shared/docs/localization-protocol.md`
**Disposition:** Local/reference

**Why:** Useful precedent for later target customization, but not necessary for base package review.

### `zoputer-substrate/shared/git-sync/`
**Disposition:** Local/reference

**Why:** This is a factory/distribution mechanism, not a required part of the office package itself.

### `zoputer-substrate/RelayDrops/`
**Disposition:** Local/runtime support only

**Why:** Runtime transfer state should not define the package shape.

### `zoputer-substrate/BuildSystem/`
**Disposition:** Local/reference

**Why:** This belongs to build/factory process and should not be mistaken for the external product.

## Bucket 3 — Deprecate from the deployment story

### `zoputer-substrate/Zoffice/releases/`
**Disposition:** Deprecated duplicate release surface

**Why:** Release authority should live under the canonical `Zoffice/releases/` tree, not in a parallel substrate mirror.

### `zoputer-substrate/Zoffice/BOOTLOADER.md`
**Disposition:** Deprecated duplicate

**Why:** The canonical bootloader belongs in the product tree.

### `consulting-zoffice-stack` deployment framing
**Disposition:** Deprecated architecture narrative

**Why:** It was a precursor. It no longer explains the current package accurately.

## Resulting rule of thumb

If a future contributor asks, “Should this live in substrate or Zoffice?” the default answer should be:

- **If it is part of how an external office operates or transfers safely, it belongs in `Zoffice/capabilities/zo2zo/`.**
- **If it is only part of how this machine manufactures or stages packages, it can remain local/reference support.**
