---
created: 2026-03-13
last_edited: 2026-03-13
version: 1.0
provenance: con_hs2l0mnC3kX6g5tx
type: readiness_checklist
status: draft
---

# Package Readiness Checklist

## Product boundary
- [ ] `Zoffice/` is clearly documented as canonical product source
- [ ] legacy Rice / consultancy / substrate paths are not required to understand the package
- [ ] no step assumes installation into this live Zo

## Transfer capability
- [ ] `zo2zo` capability documents parent link, trust, transfer, and safety behavior
- [ ] transfer-safety story is explicit
- [ ] substrate-derived relay behavior is either integrated or clearly superseded

## Packaging integrity
- [ ] release creation uses a new versioned folder
- [ ] old release folders are not recursively bundled into new artifacts
- [ ] manifest/checksum artifacts are produced
- [ ] dry-run works before live packaging

## Validation
- [ ] `python3 Zoffice/scripts/healthcheck.py` passes
- [ ] `python3 Zoffice/scripts/layer2_smoke_test.py` passes or any failure is explicitly documented
- [ ] release review artifact summarizes results honestly

## Human review gate
- [ ] release contents can be understood from the release folder + Zoffice docs
- [ ] next step after approval is clear
- [ ] transfer to Zoputer has not yet happened
