---
created: 2026-04-19
last_edited: 2026-04-19
version: 2.0
provenance: con_zo4RJ6QXliPNhcnn
---

# Pulse

Pulse is the exported build orchestrator that ships with N5OS Ode. It coordinates build work using **Waves** (parallel barriers), **Streams** (ordered sequences inside a wave), **Drops** (individual tasks), and **Deposits** (completion reports).

## Shipped Command Surface

Use the exported CLI under `Skills/pulse/scripts/pulse.py`.

```bash
# Required pre-start checks
python3 N5/scripts/build_contract_check.py <slug>
python3 Skills/pulse/scripts/pulse.py validate <slug>

# Lifecycle
python3 Skills/pulse/scripts/pulse.py start <slug>
python3 Skills/pulse/scripts/pulse.py status <slug>
python3 Skills/pulse/scripts/pulse.py stop <slug>
python3 Skills/pulse/scripts/pulse.py resume <slug>
python3 Skills/pulse/scripts/pulse.py tick <slug>
python3 Skills/pulse/scripts/pulse.py ring <slug> <drop-id>
python3 Skills/pulse/scripts/pulse.py launch <slug> <drop-id>
python3 Skills/pulse/scripts/pulse.py retry <slug> <drop-id> --reason "why"
python3 Skills/pulse/scripts/pulse.py finalize <slug>
```

## Recommended Workflow

```bash
# 1. Initialize the build folder
python3 N5/scripts/init_build.py my-build

# 2. Fill in PLAN.md, meta.json, and drops/
python3 N5/scripts/build_contract_check.py my-build
python3 Skills/pulse/scripts/pulse.py validate my-build

# 3. Start orchestration
python3 Skills/pulse/scripts/pulse.py start my-build

# 4. Monitor
python3 Skills/pulse/scripts/pulse.py status my-build
```

## Build Contract

Every shipped Pulse build must include:

- `N5/builds/<slug>/PLAN.md`
- `N5/builds/<slug>/meta.json`
- `N5/builds/<slug>/drops/`
- `N5/builds/<slug>/deposits/`
- `N5/builds/<slug>/artifacts/`

The contract gate is enforced by:

```bash
python3 N5/scripts/build_contract_check.py <slug>
```

## Manual Drops

When a Drop uses `spawn_mode: manual`, Pulse creates a launcher file:

```bash
python3 Skills/pulse/scripts/pulse.py launch <slug> <drop-id>
```

That launcher tells you exactly which Drop brief to load and where to write the deposit. After the deposit exists, ring the bell:

```bash
python3 Skills/pulse/scripts/pulse.py ring <slug> <drop-id>
```

## What This Export Does Not Promise

This export documents only the command surface that currently ships. If you need a broader internal Pulse environment or custom orchestration layers, treat that as follow-up work rather than assuming undocumented commands exist here.

## Canonical Reference

For the most up-to-date exported operating guidance, see:

- `Skills/pulse/SKILL.md`
