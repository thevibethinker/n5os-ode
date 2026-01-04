---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.2
type: build_plan
status: ready_for_builder
provenance: con_fu1GgsowkllHgO3i
---

# Plan: Health Intelligence Protocol (HIP)

**Objective:** Create a generalized, machine-readable health SSOT that powers:
1. Multi-checkpoint SMS reminders throughout the day (wake, post-workout, evening)
2. Auto-tick Life Counter when V completes each checkpoint
3. Persona-queryable regimen data for intelligent health advice
4. BioLog integration for tracking and correlation

**Trigger:** V asked about iron/VitC timing → discovered personas lack queryable access to current regimen → designed generalized supplement timing system.

**Key Design Principle:** Plans are FOR AI execution, not human review. Build a generalized system that handles ANY supplement timing protocol, not just iron.

---

## V's Decisions (Confirmed)

| Decision | Choice |
|----------|--------|
| Life Counter Integration | **Auto-tick** when V replies "done" or logs via BioLog |
| Notification Style | **Multiple SMS** at each checkpoint throughout the day |
| Scope | **Generalized** — all checkpoints (wake, post-workout, evening), not just morning |

---

## Full Daily Protocol

### Checkpoint 1: Wake (7:30 AM)
| Item | Brand | Dose | Notes |
|------|-------|------|-------|
| Iron Bisglycinate | Thorne | 25mg | Empty stomach, with VitC |
| Vitamin C | ENDUR-C | 500mg | Enhances iron absorption |
| Vyvanse | — | 60mg | Rx |
| Bupropion XL | — | 300mg | Rx |

**SMS:** "☀️ Wake Stack: Iron (25mg) + ENDUR-C + Vyvanse + Bupropion. Empty stomach. Reply 'done' when taken."
**Life Counter:** `supplement_wake` auto-tick on "done" reply

### Checkpoint 2: Post-Workout (9:30 AM)
| Item | Brand | Dose | Notes |
|------|-------|------|-------|
| O.N.E. Multivitamin | Pure Encapsulations | 1 cap | With food/protein |
| Omega-3 | TBD | TBD | With food |
| Probiotic 10 | Nature's Bounty | 1 cap | Can be empty stomach |
| Creatine | TBD | 5g | With protein shake |
| Protein Powder | TBD | 1 scoop | Post-workout |

**SMS:** "✅ 2hr iron window complete. Take: Multi + Omega-3 + Probiotic + Creatine + Protein. Coffee OK now. Reply 'done' when taken."
**Life Counter:** `supplement_main` auto-tick on "done" reply

### Checkpoint 3: Evening (9:00 PM or configurable)
| Item | Brand | Dose | Notes |
|------|-------|------|-------|
| Aripiprazole | — | 5mg | Rx, mood stabilization |
| Magnesium Glycinate | TBD | 200-400mg | Promotes sleep, GABA support |

**SMS:** "🌙 Evening Stack: Aripiprazole (5mg) + Magnesium. Reply 'done' when taken."
**Life Counter:** `supplement_evening` auto-tick on "done" reply

---

## Drug Interaction Assessment ✅

| Combination | Status | Notes |
|-------------|--------|-------|
| Iron + VitC | ✅ SYNERGY | VitC enhances absorption 2-3x |
| Iron + Vyvanse | ✅ SAFE | No interaction; both fine empty stomach |
| Iron + Bupropion | ✅ SAFE | No interaction |
| Vyvanse + Bupropion | ✅ SAFE | Different mechanisms; V's established combo |
| Iron + Coffee/Caffeine | ⚠️ AVOID | Wait until 2hr window (Checkpoint 2) |
| Magnesium + Evening | ✅ OPTIMAL | Promotes GABA, supports sleep |
| Aripiprazole + Evening | ✅ OPTIMAL | Standard timing per prescriber |

**Verdict:** All proposed timings are pharmacologically sound.

---

## Generalized Architecture

### Core Principle: Data-Driven Checkpoints

The system should NOT hardcode "7:30 AM" or "Iron" — instead:

```
regimen.json (SSOT) → health_checkpoint.py (logic) → Agents (delivery) → Life Counter (tracking)
```

Any change to `regimen.json` automatically propagates to:
- SMS content
- Timing of reminders
- Life Counter categories
- Persona context queries

### Schema Design for Generalization

```json
{
  "version": "1.0",
  "updated": "2026-01-04",
  "checkpoints": [
    {
      "id": "wake",
      "time": "07:30",
      "label": "Wake Stack",
      "emoji": "☀️",
      "items": ["iron-bisglycinate", "vitamin-c", "vyvanse", "bupropion"],
      "conditions": {
        "empty_stomach": true,
        "with_water": true
      },
      "life_counter_slug": "supplement_wake",
      "sms_suffix": "Empty stomach. Reply 'done' when taken."
    },
    {
      "id": "post_workout",
      "time": "09:30",
      "label": "Main Stack",
      "emoji": "✅",
      "items": ["methylated-multi", "omega-3", "probiotic", "creatine", "protein"],
      "conditions": {
        "after_checkpoint": "wake",
        "min_minutes_after": 120,
        "with_food": true
      },
      "life_counter_slug": "supplement_main",
      "sms_suffix": "Coffee OK now. Reply 'done' when taken."
    },
    {
      "id": "evening",
      "time": "21:00",
      "label": "Evening Stack",
      "emoji": "🌙",
      "items": ["aripiprazole", "magnesium"],
      "conditions": {
        "before_bed": true
      },
      "life_counter_slug": "supplement_evening",
      "sms_suffix": "Reply 'done' when taken."
    }
  ],
  "items": {
    "iron-bisglycinate": {
      "name": "Iron Bisglycinate",
      "brand": "Thorne",
      "dose": "25mg",
      "category": "mineral",
      "active": true,
      "take_with": ["vitamin-c"],
      "avoid_with": ["calcium", "coffee", "tea", "dairy", "magnesium", "zinc"],
      "wait_before_other": 120
    },
    "vitamin-c": {
      "name": "Vitamin C",
      "brand": "ENDUR-C",
      "dose": "500mg",
      "category": "vitamin",
      "active": true
    },
    "vyvanse": {
      "name": "Vyvanse",
      "dose": "60mg",
      "category": "rx",
      "active": true
    },
    "bupropion": {
      "name": "Bupropion XL",
      "dose": "300mg",
      "category": "rx",
      "active": true
    },
    "methylated-multi": {
      "name": "O.N.E. Multivitamin",
      "brand": "Pure Encapsulations",
      "dose": "1 capsule",
      "category": "multivitamin",
      "active": true
    },
    "omega-3": {
      "name": "Omega-3 Fish Oil",
      "brand": "TBD",
      "dose": "TBD",
      "category": "essential_fatty_acid",
      "active": true
    },
    "probiotic": {
      "name": "Probiotic 10",
      "brand": "Nature's Bounty",
      "dose": "1 capsule",
      "category": "gut_health",
      "active": true
    },
    "creatine": {
      "name": "Creatine Monohydrate",
      "brand": "TBD",
      "dose": "5g",
      "category": "performance",
      "active": true
    },
    "protein": {
      "name": "Protein Powder",
      "brand": "TBD",
      "dose": "1 scoop",
      "category": "nutrition",
      "active": true
    },
    "aripiprazole": {
      "name": "Aripiprazole",
      "dose": "5mg",
      "category": "rx",
      "active": true
    },
    "magnesium": {
      "name": "Magnesium Glycinate",
      "brand": "TBD",
      "dose": "200-400mg",
      "category": "mineral",
      "active": true
    }
  },
  "interactions": {
    "iron-bisglycinate": {
      "synergy": ["vitamin-c"],
      "blockers": ["calcium", "magnesium", "zinc", "coffee", "tea", "dairy", "antacids"],
      "wait_minutes": 120,
      "notes": "Iron absorption reduced 40-70% by blockers; VitC enhances 2-3x"
    }
  }
}
```

---

## Recent System Updates (Already Live)

1. **Vibe Nutritionist v1.3:**
   - Direct update authority on `Personal/Health/stack/` files
   - Routing contract with Vibe Trainer

2. **Morning Digest:**
   - `💊 Stack: X/10 🟢` — Stack budget indicator
   - `7-day mood: [emojis]` — BioLog correlation

These are **already deployed** — no build work needed.

---

## Checklist

### Phase 1: Data Consolidation
- ☑ Create `N5/systems/health/` directory with `.n5protected`
- ☑ Create `regimen.json` with full checkpoint schema (wake, post_workout, evening)
- ☑ Create `interactions.json` (or embed in regimen.json)
- ☑ Create `README.md` documenting schema
- ☑ Update `Personal/Health/stack/current_supplements.yaml` — add Iron, VitC, fix multi brand
- ☑ Test: `jq '.checkpoints[] | .id' regimen.json` returns 3 checkpoints

### Phase 2: Life Counter Integration
- ☑ Verify Life Counter categories exist: `supplement_wake`, `supplement_main`, `supplement_evening`
- ☑ If missing, create categories in wellness.db or life_categories table
- ☑ Create `N5/scripts/health_log.py` — helper to log checkpoint completion
- ☑ Test: `python3 N5/scripts/health_log.py --checkpoint wake` ticks counter

### Phase 3: Agent System (Multi-Checkpoint)
- ☑ Create `N5/scripts/health_checkpoint.py` — generates SMS content from regimen.json
- ☑ Create/update agents for each checkpoint:
  - ☑ Agent 1: 7:30 AM → Wake Stack SMS
  - ☑ Agent 2: 9:30 AM → Post-Workout Stack SMS
  - ☑ Agent 3: 9:00 PM → Evening Stack SMS
- ☑ Each agent instruction includes:
  - Run `health_checkpoint.py --checkpoint <id>` to get SMS content
  - Send SMS
  - Listen for "done" reply → call `health_log.py --checkpoint <id>`
- ☑ Test: Dry-run each agent; verify SMS format and Life Counter tick

### Phase 4: BioLog Integration
- ☑ Update BioLog reply processing to recognize supplement confirmations (done_aliases in regimen.json)
- ☐ When V replies "done" to health SMS, auto-route to `health_log.py` (requires SMS reply handler)
- ☑ Test: Send test SMS, reply "done", verify Life Counter incremented

### Phase 5: Persona Context Integration
- ☑ Update `n5_load_context.py` health mode to inject `regimen.json`
- ☑ All health personas (Nutritionist, Trainer) can now query V's current stack
- ☑ Test: `python3 N5/scripts/n5_load_context.py health | grep "iron-bisglycinate"`

---

## Affected Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `N5/systems/health/` | CREATE | New directory for health SSOT |
| `N5/systems/health/regimen.json` | CREATE | Machine-readable checkpoint + item data |
| `N5/systems/health/README.md` | CREATE | Schema documentation |
| `N5/systems/health/.n5protected` | CREATE | Prevent accidental deletion |
| `N5/scripts/health_checkpoint.py` | CREATE | Generate SMS content from regimen.json |
| `N5/scripts/health_log.py` | CREATE | Log checkpoint completion to Life Counter |
| `Personal/Health/stack/current_supplements.yaml` | UPDATE | Add Iron, VitC, fix brands |
| Agent (7:30 AM) | CREATE/UPDATE | Wake stack reminder |
| Agent (9:30 AM) | CREATE | Post-workout stack reminder |
| Agent (9:00 PM) | CREATE | Evening stack reminder |
| `N5/scripts/n5_load_context.py` | UPDATE | Add regimen.json to health context |

---

## Success Criteria

1. **regimen.json** exists with all 3 checkpoints and all items with correct brands/doses
2. **3 agents** send SMS at wake (7:30), post-workout (9:30), evening (21:00)
3. **Life Counter** auto-ticks when V replies "done" to any checkpoint SMS
4. **Any persona** can query `regimen.json` via context loader
5. **Adding/removing** a supplement in `regimen.json` automatically updates all SMS content
6. **No hardcoded times/items** in agent instructions — all driven by data

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| SMS spam (3x/day) | V explicitly requested this; can disable any checkpoint in regimen.json |
| "done" reply parsing fails | Fuzzy match: "done", "took it", "✓", etc. |
| Life Counter categories don't exist | Phase 2 creates them if missing |
| Schema changes break agents | Agents query regimen.json dynamically; no hardcoding |
| Evening time varies | Make `time` field in checkpoint configurable; default 21:00 |

---

## Handoff Notes for Builder

**Starting Phase:** 1 (Data Consolidation)

**Context:**
- V confirmed all brands/doses (see Full Daily Protocol section)
- V wants auto-tick Life Counter on "done" reply
- V wants SMS at ALL checkpoints (wake, post-workout, evening)
- Generalize: data-driven architecture, not hardcoded

**Key Files to Reference:**
- `Personal/Health/stack/current_supplements.yaml` — existing data to migrate
- `Personal/Health/stack/current_medications.yaml` — existing Rx data
- `N5/data/wellness.db` — Life Counter database (if using SQLite)
- `N5/scripts/log_bio_reply.py` — existing BioLog logging (pattern to follow)

**Open Design Decisions (Builder can decide):**
- Embed interactions in `regimen.json` vs separate `interactions.json`
- Life Counter: new SQLite table vs existing life_logs table
- Evening checkpoint time: fixed 21:00 or relative to V's typical bedtime

**Anti-Patterns to Avoid:**
- Do NOT hardcode "Iron" or "7:30 AM" in agent instructions
- Do NOT create separate scripts for each checkpoint — one parameterized script
- Do NOT skip Life Counter integration — it's core to the value prop


