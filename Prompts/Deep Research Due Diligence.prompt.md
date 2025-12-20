---
created: 2025-10-15
last_edited: 2025-12-17
version: 2.0
provenance: con_8fSBkRPMwtmGxawq
title: Deep Research Due Diligence
description: |
  DEPRECATED - Use the new DD system instead.
  For individuals: @DD Individual
  For organizations: @DD Organization
tags:
  - due-diligence
  - research
  - deprecated
tool: true
---

# Deep Research Due Diligence

> ⚠️ **This prompt is deprecated.** Use the new DD system:
>
> - **For individuals:** `@DD Individual`
> - **For organizations:** `@DD Organization`

## New DD System

The DD system has been formalized with:

1. **Purpose-driven research** - Every DD has a thesis/question to answer
2. **Structured output** - JSON schemas at `N5/schemas/dd_individual.schema.json` and `dd_organization.schema.json`
3. **CRM integration** - DD reports link to CRM profiles
4. **WIIFM analysis** - Explicit "What's In It For Me/Careerspan" section
5. **Script orchestration** - `python3 N5/scripts/n5_dd.py`

## Quick Start

```bash
# Individual DD
python3 N5/scripts/n5_dd.py individual --name "Adam Alpert" --org "Pangea" --type acquisition

# Organization DD  
python3 N5/scripts/n5_dd.py organization --name "Pangea" --domain "pangea.com" --type acquisition_inbound

# List all DDs
python3 N5/scripts/n5_dd.py list
```

## Prompts

- `file 'Prompts/DD Individual.prompt.md'` - Full protocol for individual DD
- `file 'Prompts/DD Organization.prompt.md'` - Full protocol for organization DD

