---
created: 2026-03-02
last_edited: 2026-03-02
version: 1.0
provenance: con_pLLTlqfVu4hKeKhT
---

# Phase 0 Discovery Brief (va -> zoputer)

## Mission
Initiate Zo2Zo phased transfer for standalone capability uplift.

## Scope for This Packet
- Handshake and compatibility discovery only.
- No destructive apply operations.
- No secrets transferred.

## Required Response From zoputer
Return a structured Phase 0 response with:
1. Capability matrix (current state per domain)
2. Localization profile (all required keys)
3. Dependency blockers and risk notes
4. Proposed remaps for mismatched paths/ports/services
5. Content Library + pathways + Wisdom System topology map

## Domains
- Architecting/building/debugging/filesystem maintenance
- Memory
- Communication + ingestion
- Critical APIs + webhooks
- Content Library
- Pathways feeding Content Library
- Wisdom System relation and promotion logic

## Convergence Rules
- Max 3 reconcile loops for Phase 0
- Escalate if unresolved critical blockers remain

## Acceptance Criteria for Phase 0
- Required localization keys complete
- Critical blockers identified and triaged
- Phase 1 transfer manifest draft accepted by both sides
