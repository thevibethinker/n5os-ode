---
created: 2026-03-13
last_edited: 2026-03-13
version: 1.0
provenance: con_hs2l0mnC3kX6g5tx
type: supersession_plan
status: draft
---

# Zoffice Externalization — Supersession Plan

## Decision

This externalized Zoffice version is the **canonical deployment package** going forward.

After this build, the default answer to "what should be deployed externally?" is:

> Deploy the versioned release produced from `Zoffice/`.

Older build folders and supporting substrate assets remain useful, but they no longer define the primary product or deployment story.

---

## Supersession Framework

Each legacy surface gets one of four dispositions:

1. **Absorbed** — functionality or structure now lives inside canonical `Zoffice/`
2. **Superseded** — no longer a standalone deployment path
3. **Reference** — kept for provenance, rationale, or factory support
4. **Excluded** — belongs to this live device and is not part of the exportable Zoffice product

---

## Disposition by Surface

### 1. `Zoffice/`
**Disposition:** Canonical

- Becomes the sole product source for external packaging
- Owns staff, capabilities, routing, bootloader, manifest, and release folders
- Must contain or explicitly supersede the transfer behaviors previously scattered across substrate work

### 2. `N5/builds/n5os-rice/`
**Disposition:** Reference

- Keeps the architectural rationale: Troika model, Layer 0/1/2 framing, fractal office pattern
- No longer acts as a deployment entrypoint
- Serves as provenance explaining why the product is shaped the way it is

### 3. `N5/builds/rice-core/`
**Disposition:** Superseded as standalone build; absorbed into canonical product

- Its outputs are already embodied in `Zoffice/`
- The build folder remains useful as provenance and implementation history
- Future deployment should not begin from this build folder directly

### 4. `N5/builds/rice-capabilities/`
**Disposition:** Superseded as standalone build; absorbed into canonical product

- Capability outputs belong in `Zoffice/capabilities/`
- This build remains a record of how those capabilities were defined and implemented
- Future deployers should consume the integrated product, not the stream folder

### 5. `N5/builds/rice-staff/`
**Disposition:** Superseded as standalone build; absorbed into canonical product

- Starter staff definitions now live under `Zoffice/staff/`
- The build remains useful as design/provenance material
- It is no longer a separate product surface

### 6. `N5/builds/rice-integration/`
**Disposition:** Superseded as standalone build; absorbed into canonical product

- Routing and Layer 1 integration outputs belong in the canonical package
- This build remains reference material for how integration was achieved

### 7. `N5/builds/consulting-zoffice-stack/`
**Disposition:** Deprecated / Reference only

- Important as an early exploration of external Zo-to-Zo consulting architecture
- No longer defines the product or installation story
- Any still-useful ideas should be either absorbed into `Zoffice/` or explicitly mapped to modern equivalents

### 8. `zoputer-substrate/`
**Disposition:** Split

#### 8a. Transfer-capability elements
**Disposition:** Absorb or supersede explicitly

- Relay, trust, sanitization, or transfer patterns that matter to external office-to-office movement should either:
  - be integrated into `Zoffice/capabilities/zo2zo/`, or
  - be documented as already superseded by the in-package `zo2zo` capability

#### 8b. Local factory/export support
**Disposition:** Reference / local support

- If some substrate assets are only useful on this machine to help prepare or transfer packages, they can remain local support tooling
- They should not be presented as the product itself

### 9. Live device core (`N5/`, local agents, local automations, local operating internals)
**Disposition:** Excluded

- This build does **not** supersede the core operating machinery of this device
- The external Zoffice product may have analogous mechanisms, but it should not claim to replace the local operating substrate of va’s live system

---

## Operational Rule

When deciding whether a file/folder belongs in the external product, ask:

### Ship it if:
- It is part of the office product itself
- It is needed by a clean external Zoffice install
- It helps the exported office communicate, route, store knowledge, evaluate, or transfer across instances

### Do not ship it if:
- It is specific to this live device’s operation
- It is personal/local orchestration infrastructure unrelated to the exported office package
- It exists only to help this machine manufacture, inspect, or manage releases

---

## End-State Statement

After `zoffice-externalization` is complete:

- **One canonical product source:** `Zoffice/`
- **One canonical review surface:** the new versioned release folder under `Zoffice/releases/`
- **One legacy policy:** older Rice/substrate/consultancy artifacts are provenance, reference, or local support — not competing deployment paths
- **One explicit exclusion:** this does not replace the core operating functionality of this live device

---

## Implications

- Future builders should start from the integrated Zoffice package, not from individual Rice stream plans
- Future documentation should point to the release folder and canonical `Zoffice/` tree first
- Any remaining ambiguity about substrate should be resolved by either absorbing the needed pieces into `zo2zo` or marking them as local-only support
