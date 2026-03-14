---
created: 2026-03-13
last_edited: 2026-03-13
version: 1.0
provenance: con_hs2l0mnC3kX6g5tx
type: architecture_reconciliation
status: draft
---

# Zoffice Architecture Reconciliation

## Purpose

This document answers one question unambiguously:

**What is the deployable Zoffice product now?**

## Canonical Answer

The deployable product is the `Zoffice/` tree.

This build treats `Zoffice/` as the canonical external package source and treats prior work as follows:

- `N5/builds/n5os-rice/` — architectural origin and rationale
- `N5/builds/rice-core/` — foundational implementation provenance
- `N5/builds/rice-capabilities/` — capability implementation provenance
- `N5/builds/rice-staff/` — starter staff implementation provenance
- `N5/builds/rice-integration/` — wiring/integration provenance
- `N5/builds/consulting-zoffice-stack/` — deprecated deployment story; reference-only
- `zoputer-substrate/` — local transfer/factory support and legacy substrate context, not the product shell

## How the pieces now relate

### 1. Rice
Rice was the multi-build architecture and implementation program that produced the Zoffice product surface.

Its role now is historical and explanatory:
- it explains **why** the structure exists
- it documents **how** the structure was built
- it no longer defines the day-1 operator experience for a new external deployment

### 2. Zoffice
Zoffice is the product surface that survived the Rice process.

It contains the pieces needed to reason about the deployable office directly:
- configs
- capabilities
- staff definitions
- scripts
- release artifacts
- bootloader/personalization flow

### 3. Substrate
Substrate was originally part of the consultancy / inter-Zo transfer story.

Its surviving value is real, but narrower:
- transfer mechanics
- relay patterns
- sanitizer patterns
- export/factory support for moving assets between Zo environments

Substrate should not be treated as the shell that explains Zoffice. Instead, the useful transfer concepts either belong inside Zoffice’s `zo2zo` capability or remain local-only factory support for preparing external releases.

## Product boundary

### Included in the canonical external package
- `Zoffice/config/`
- `Zoffice/capabilities/`
- `Zoffice/staff/`
- `Zoffice/scripts/`
- `Zoffice/BOOTLOADER.md`
- `Zoffice/PERSONALIZE.md`
- `Zoffice/MANIFEST.json`

### Excluded from the canonical external package story
- the core live operating machinery of this device (`N5/`, workspace-level control systems, existing live environment state)
- legacy consultancy framing as the primary explanation of the system
- substrate as a separate product shell

## Deployment story after reconciliation

A future operator should be able to follow this chain without reading old build plans:

1. Review `Zoffice/`
2. Review the current release folder under `Zoffice/releases/`
3. Read `Zoffice/BOOTLOADER.md`
4. Personalize with `Zoffice/PERSONALIZE.md`
5. Validate locally on the target environment
6. Cut over only after validation

## Implication for future work

Future improvements should default to one of these destinations:

- **Product behavior or docs** → `Zoffice/`
- **Transfer mechanics used by exported offices** → `Zoffice/capabilities/zo2zo/`
- **Factory-only support for this machine** → local support paths / reference tooling
- **Historical rationale** → existing build artifacts under `N5/builds/`

## Decision summary

`Zoffice/` supersedes the older partially or previously complete deployment stories.

It does **not** supersede the core functionality of this device. This machine remains the factory and origin environment, not the thing being replaced.
