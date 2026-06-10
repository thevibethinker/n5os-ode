---
name: recommend-skill-chain
description: >
  Recommend an ordered chain of atomic visual skills for a design spec by
  loading the catalog from chain_metadata frontmatter and ranking candidate
  skills.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0.0"
created: 2026-06-10
last_edited: 2026-06-10
version: 1.0
provenance: con_sQ03t9FFBWIVZTXO
---

# Recommend Skill Chain

Recommend an ordered chain of visual skills for a spec.

## When to Use

Use when a visual specification needs a chain of atomic skills.

## Pipeline

1. Load spec
2. Load catalog from `Skills/*/SKILL.md`
3. Build heuristic signals
4. Prefer a clarifying question if the spec is too short or conflicting
5. Output chain or director delegation

## Outputs

- `chain.json`
- optional clarification prompt
- optional director delegation
