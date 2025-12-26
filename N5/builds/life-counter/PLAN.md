---
created: 2025-12-23
last_edited: 2025-12-23
version: 1.0
type: build_plan
status: draft
provenance: con_TwWTxz0rcZU4UqIx
---

# Plan: Life Counter & Habit System (GitHub for Life)

**Objective:** Build a robust, SQLite-backed counter system that tracks daily increments for various items/categories, supporting both manual CLI triggers (e.g., "+1 weed") and automated external integrations (e.g., Fitbit workouts).

**Trigger:** V's request for a "GitHub for life" tracking system to encourage good habits and destroy bad ones.

---

## Open Questions
- [ ] **Fitbit Auth:** Does V already have Fitbit credentials stored in `file 'N5/config/secrets'`?
- [ ] **Visualization:** Does V want a terminal-based "contribution graph" (ASCII) or just the data structure ready for a Site/App later? (Assumption: ASCII first for "GitHub feel").
- [ ] **Categories:** Should categories be strictly enforced via a schema, or dynamic? (Recommendation: Dynamic but with a `categories` table for metadata like "good/bad" habit tagging).

---

## Checklist

### Phase 1: Core Engine & CLI
- ☐ Initialize `file 'N5/data/wellness.db'` with counters and logs tables.
- ☐ Create `file 'N5/scripts/wellness_counter.py'` for manual increments.
- ☐ Create `file 'N5/scripts/wellness_viz.py'` for the GitHub-style contribution graph.
- ☐ Test: Manual increment and visualization of data.

### Phase 2: Automation & Integration
- ☐ Create `file 'N5/scripts/fitbit_sync.py'` (Stub or full depending on API access).
- ☐ Register scheduled task for daily auto-population.
- ☐ Create `file 'Prompts/Wellness Counter.prompt.md'` for natural language interaction.
- ☐ Test: "+1 [item]" via chat increments the correct category.

---

## Phase 1: Core Engine & CLI

### Affected Files
- `N5/data/wellness.db` - CREATE - SQLite database for habit data.
- `N5/scripts/wellness_counter.py` - CREATE - CLI tool for increments and management.
- `N5/scripts/wellness_viz.py` - CREATE - ASCII contribution graph generator.

### Changes

**1.1 Schema Design:**
- Table `categories`: `id`, `name`, `type` (habit/stat), `sentiment` (good/bad/neutral).
- Table `logs`: `id`, `category_id`, `timestamp`, `value`, `source` (manual/fitbit).
- Table `daily_summaries`: (Cached) `date`, `category_id`, `total_value`.

**1.2 CLI Implementation (`wellness_counter.py`):**
- Command: `python3 wellness_counter.py increment <slug> [value] [--source <name>]`
- Command: `python3 wellness_counter.py list` (show categories and sentiment).

**1.3 Visualization Implementation (`wellness_viz.py`):**
- Generate a 52-week grid (columns) by 7 days (rows) ASCII representation for a specific category.

### Unit Tests
- `sqlite3 N5/data/wellness.db ".tables"`: Should show categories and logs.
- `python3 wellness_counter.py increment weed 1`: Should record entry in logs.

---

## Phase 2: Automation & Integration

### Affected Files
- `N5/scripts/fitbit_sync.py` - CREATE - Fetch workout data from Fitbit API.
- `Prompts/Wellness Counter.prompt.md` - CREATE - User-facing interface for increments.

### Changes

**2.1 Fitbit Sync:**
- Use `use_app_fitbit` (if available) or raw requests to fetch daily step/workout counts.
- Map Fitbit "workouts" to a `category` in `wellness.db`.

**2.2 Chat Interface:**
- Natural language parsing in the prompt to handle "+1 X" or "I just worked out".

---

## Success Criteria
1. `+1 weed` increments the daily counter for "weed".
2. `python3 wellness_viz.py graph weed` shows a GitHub-style grid.
3. Automated sources (Fitbit) populate without manual intervention.
4. "Sentiment" tracking allows reporting on "Good Habit Streak" vs "Bad Habit Relapses".

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API Authentication failure (Fitbit) | Start with a robust manual entry system; add auto-sync as a secondary layer. |
| Data corruption | Use SQLite transactions and periodic backups to `file 'N5/backups/wellness'`. |

---

## Level Upper Review (Internal Architect Simulation)

### Counterintuitive Suggestions Received:
1. "Don't just track counts; track 'Time Spent' for bad habits to measure the real cost."
2. "Use a 'Debt' metaphor for bad habits that requires 'Repayment' through good habits."

### Incorporated:
- Added `sentiment` to categories to allow for differential reporting (Good vs Bad).

### Rejected (with rationale):
- "Debt metaphor": Complects the simple counter system. Keep it simple first.

