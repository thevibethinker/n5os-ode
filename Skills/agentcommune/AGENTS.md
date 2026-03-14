---
created: 2026-03-02
last_edited: 2026-03-02
version: 1.0
provenance: con_bYOerV59r8L14pNg
---

# AgentCommune Local Rules

## Scope

This directory manages AgentCommune activity only.

## Hard Isolation

1. Never read/write `Skills/zode-moltbook/state/` from scripts in this folder.
2. Never use `MOLTBOOK_API_KEY` in this folder.
3. Keep heartbeat logs and rate tracking in `Skills/agentcommune/state/` only.
4. Keep scheduling independent from Moltbook heartbeat agents.

## Change Safety

- Preserve CLI compatibility for existing commands before adding new ones.
- Prefer additive changes so posting strategy experiments can be rolled back quickly.
