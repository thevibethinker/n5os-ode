---
created: 2026-02-13
last_edited: 2026-02-13
version: 1.0
provenance: con_lUAmO8hsfnmiy3xh
---

# Persona Optimization — Agency Bootloader

Portable package that installs a coordinated persona agency with automatic switching on any Zo. Lighter than N5OS Ode — focused specifically on the persona layer.

## What It Sets Up
- **7 personas**: Operator, Builder, Debugger, Strategist, Writer, Researcher, Teacher
- **Hybrid switching model**: Hard switches for stances (Builder, Debugger, Strategist, Writer) + methodology injection for techniques (Researcher, Teacher)
- **Routing contract**: Rules that trigger the right persona automatically based on what you say

## Hard Switch vs Methodology Injection
- Hard switch = full persona change. Builder loads engineering discipline. Writer loads voice fidelity. Different cognitive stance.
- Methodology injection = load a process framework without switching. Researcher adds multi-source search discipline. Teacher adds scaffolded explanation. Lighter, faster.

## Install
```
git clone https://github.com/vrijenattawar/n5-os-zo-persona-optimization.git
python3 scripts/bootloader.py --scan   # Review proposal
python3 scripts/bootloader.py --apply  # Install
```

## When to Use This vs N5OS Ode
- **This**: You just want persona switching. Quick install, minimal footprint.
- **N5OS Ode**: You want the full system — memory, blocks, principles, safety, plus personas.

Repo: github.com/vrijenattawar/n5-os-zo-persona-optimization
