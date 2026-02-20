---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_gFL5uhApy1RZtlSJ
drop_id: D6
title: DuckDB Call Analytics Dataset
status: pending
dependencies: []
---

# D6: DuckDB Call Analytics Dataset

## Objective
Set up `Datasets/foundermaxxing-calls/` mirroring Zoseph call analytics pattern.

## Inputs
- `Datasets/zo-hotline-calls/` (template)

## Outputs
- `Datasets/foundermaxxing-calls/datapackage.json`
- `Datasets/foundermaxxing-calls/data.duckdb`
- `Datasets/foundermaxxing-calls/schema.yaml`
- `Datasets/foundermaxxing-calls/README.md`
- `Datasets/foundermaxxing-calls/ingest/ingest.py`

## Acceptance Criteria
- [ ] Dataset created with valid datapackage.json
- [ ] Schema includes: calls, caller_profiles, call_analysis tables
- [ ] Ingest script handles VAPI webhook payloads
- [ ] README documents schema and example queries
