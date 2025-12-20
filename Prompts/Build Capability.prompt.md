---
title: Build Capability
description: |
  Initialize a new build for a capability/feature/system. Creates workspace,
  activates Architect to create plan, then routes to Builder for execution.
  Use when V says "build X" or "I want to add capability Y".
tags:
  - build
  - capability
  - planning
  - architect
tool: true
---

# Build Capability

**Trigger:** V wants to build a new capability, feature, or system.

## Flow

1. **Parse the request** - Extract the capability name/slug from V's message
2. **Initialize workspace:**
   ```bash
   python3 N5/scripts/init_build.py <slug> --title "<Capability Name>"
   ```
3. **Activate Architect** (`set_active_persona("74e0a70d-398a-4337-bcab-3e5a3a9d805c")`)
4. **Architect creates plan** in `N5/builds/<slug>/PLAN.md` following template
5. **Invoke Level Upper** for counterintuitive review (experimental)
6. **Present plan to V** for approval
7. **On approval:** Hand off to Builder for execution

## Slug Convention

Convert capability name to lowercase-hyphenated:
- "Calendar Sync" → `calendar-sync`
- "Email Intelligence System" → `email-intelligence-system`
- "CRM v4" → `crm-v4`

## Example

V says: "I want to build a meeting summarizer capability"

1. Slug: `meeting-summarizer`
2. Run: `python3 N5/scripts/init_build.py meeting-summarizer --title "Meeting Summarizer"`
3. Activate Architect
4. Create plan in `N5/builds/meeting-summarizer/PLAN.md`
5. Present for approval

## Reference

- Template: `N5/templates/build/plan_template.md`
- Guide: `N5/docs/BUILD_PLANNING_GUIDE.md`
- Routing: `N5/prefs/system/persona_routing_contract.md` Section 7.1

