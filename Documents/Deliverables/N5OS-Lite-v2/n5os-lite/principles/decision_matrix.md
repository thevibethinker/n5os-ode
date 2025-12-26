# P36/P37 Decision Matrix
Quick Decision Tree

Version: 1.0 | Created: 2025-11-02

## Decision Flow

START: What am I trying to do?

├─ Improving existing system?
│  ├─ Core logic sound? → P37 (Refactor)
│  ├─ Core logic wrong? → REBUILD
│  └─ Unsure? → See below
│
└─ New work spanning multiple domains?
   ├─ Single domain? → Use specialist directly
   ├─ Multiple domains? → P36 (Orchestration)
   └─ Unsure? → See below

## P36 (Orchestration) - When?

Use when:
- Work spans multiple domains
- Different cognitive modes needed
- Single thread hitting context limits
- Multiple artifacts with different skillsets

Dont use when:
- Single domain work
- Quick tactical execution
- No clear phase boundaries

## P37 (Refactor) - When?

Use when:
- Core logic sound, implementation messy
- Behavior correct, organization poor
- 70%+ code preservable
- Low regression risk

Dont use when:
- Core logic wrong → REBUILD
- <50% survives → REBUILD
- Changing behavior → Enhancement, not refactor

## Refactor vs Rebuild

REFACTOR when:
- Core logic: Sound
- Preservation: 70%+
- Risk: Low
- Structure: Mostly good

REBUILD when:
- Core logic: Wrong abstractions
- Preservation: <50%
- Risk: High if incremental
- Structure: Fighting constantly

## Quick Reference

| Scenario | Use | Why |
|----------|-----|-----|
| Multi-domain project | P36 | Specialization |
| Single domain new | Specialist | No orchestration needed |
| Improving structure | P37 | Preserve working parts |
| Wrong architecture | REBUILD | Fresh start better |
| Quick fix | Direct | Low overhead |

v1.0 | 2025-11-02
