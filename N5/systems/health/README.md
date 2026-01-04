---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.0
provenance: con_fu1GgsowkllHgO3i
---

# Health Intelligence Protocol (HIP)

Machine-readable health SSOT for V's supplement and medication regimen.

## Files

| File | Purpose |
|------|---------|
| `regimen.json` | **SSOT** — All checkpoints, items, interactions, and timing rules |
| `history/` | Change history (timestamped copies when regimen changes) |
| `README.md` | This documentation |

## Schema Overview

### Checkpoints

Each checkpoint represents a time-based reminder:

```json
{
  "id": "wake",
  "time": "07:30",
  "label": "Wake Stack",
  "emoji": "☀️",
  "items": ["iron-bisglycinate", "vitamin-c", ...],
  "conditions": { "empty_stomach": true },
  "life_counter_slug": "supplement_wake",
  "sms_template": "{emoji} {label}: {item_list}. ..."
}
```

### Items

Each item (supplement or medication) has:

```json
{
  "name": "Iron Bisglycinate",
  "brand": "Thorne",
  "dose": "25mg",
  "category": "mineral",
  "active": true,
  "take_with": ["vitamin-c"],
  "avoid_with": ["calcium", "coffee", ...],
  "wait_before_other": 120,
  "notes": "..."
}
```

### Interactions

Interaction rules for absorption:

```json
{
  "iron-bisglycinate": {
    "synergy": ["vitamin-c"],
    "blockers": ["calcium", "magnesium", ...],
    "wait_minutes": 120
  }
}
```

## Usage

### Query Current Regimen

```bash
# All checkpoints
jq '.checkpoints[] | {id, time, items}' regimen.json

# Specific item
jq '.items["iron-bisglycinate"]' regimen.json

# Items for wake checkpoint
jq '.checkpoints[] | select(.id=="wake") | .items' regimen.json
```

### Generate SMS Content

```bash
python3 N5/scripts/health_checkpoint.py --checkpoint wake
```

### Log Checkpoint Completion

```bash
python3 N5/scripts/health_log.py --checkpoint wake
```

## Integration Points

| System | How It Uses regimen.json |
|--------|-------------------------|
| **Agents** | Query checkpoints, generate SMS content |
| **Life Counter** | Use `life_counter_slug` to auto-tick |
| **BioLog** | Parse "done" replies via `done_aliases` |
| **Context Loader** | Inject into health persona context |
| **Nutritionist** | Query items for interaction advice |

## Modifying the Regimen

1. Edit `regimen.json` directly
2. Changes automatically propagate to all SMS and agent content
3. No need to update agent instructions (data-driven)

### Adding a New Item

```json
"new-item-id": {
  "name": "New Supplement",
  "brand": "Brand",
  "dose": "XXmg",
  "category": "vitamin|mineral|rx|...",
  "active": true
}
```

Then add `"new-item-id"` to the relevant checkpoint's `items` array.

### Adding a New Checkpoint

```json
{
  "id": "midday",
  "time": "13:00",
  "label": "Midday Stack",
  "emoji": "🌞",
  "items": ["item-id-1", "item-id-2"],
  "conditions": {},
  "life_counter_slug": "supplement_midday",
  "sms_template": "{emoji} {label}: {item_list}. Reply 'done'."
}
```

## Categories

- `rx` — Prescription medications
- `mineral` — Iron, Magnesium, Zinc, etc.
- `vitamin` — Vitamins A, B, C, D, E, K
- `multivitamin` — Multi-nutrient formulas
- `essential_fatty_acid` — Omega-3, Omega-6
- `gut_health` — Probiotics, prebiotics
- `performance` — Creatine, pre-workout
- `nutrition` — Protein, collagen

## Validation

```bash
# Validate JSON syntax
jq '.' regimen.json > /dev/null && echo "Valid JSON"

# Check all checkpoint items exist
python3 -c "
import json
with open('N5/systems/health/regimen.json') as f:
    data = json.load(f)
items = set(data['items'].keys())
for cp in data['checkpoints']:
    for item in cp['items']:
        if item not in items:
            print(f'ERROR: {item} not found in items')
print('Validation complete')
"
```

