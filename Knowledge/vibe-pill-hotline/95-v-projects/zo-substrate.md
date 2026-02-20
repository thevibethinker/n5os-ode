---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# Zo Substrate — Skill Exchange Between Zo Instances

Bidirectional skill exchange using a shared GitHub repo. Push skills from one Zo, pull them on another.

## How It Works
```
Zo A  --push-->  GitHub Repo  <--pull--  Zo B
```
Skills travel as folders with SKILL.md files. The substrate repo tracks provenance — who pushed what, when, and the SHA.

## Quick Start
```bash
cd Skills && git clone https://github.com/vrijenattawar/zo-substrate.git
python3 zo-substrate/scripts/substrate.py setup init \
  --identity my-zo --partner their-zo --repo user/shared-repo
python3 zo-substrate/scripts/substrate.py push --dry-run
python3 zo-substrate/scripts/substrate.py push
```

## Key Commands
- `push` — Send your skills to the shared repo
- `pull` — Get skills from the shared repo
- `status` — See what's available
- `bundle create/validate` — Package skills with checksums

## Safety
- Push never modifies your local workspace
- Pull backs up existing skills before overwriting
- Dry-run on all mutating commands
- MANIFEST.json tracks full provenance

## Use Case
Two people (or two Zo instances) collaborating. One builds a useful skill, pushes it. The other pulls it and uses it immediately. No manual copying.

Repo: github.com/vrijenattawar/zo-substrate
