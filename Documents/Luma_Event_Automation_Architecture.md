---
created: 2025-12-06
last_edited: 2025-12-06
version: 1.0
---

# Luma + Zo Event Automation Architecture

## Purpose
Scope a disciplined automation stack so Zo can find, qualify, and register you for invite-only or public Luma events via a Playwright-powered browser runner, enriched by your Content Library answers and the same approval workflow you described.

## Core components
1. **Browser Runner** (Playwright + Python)
   - Runs inside Zo via `python3 N5/scripts/browser_runner.py` with a simple JSON contract (task name + params) and returns structured JSON (events, registration status, unanswered fields, confirmation text).
   - Tasks we will support first:
     - `luma_list_city_events` (discover events on a city page, scroll/pagination, harvest metadata + event URLs).
     - `luma_inspect_event` (open an event URL, capture title/date/host/faq/registration state).
     - `luma_register_for_event` (autofill and submit forms, report missing questions back to Zo so it can pull answers).
   - Playwright handles the headless browser mechanics; Zo remains responsible for reasoning about which events to choose and what to answer.
2. **Build Orchestrator** (new worker supervisor)
   - Drives the high-level workflow via discrete threads (see below) and ensures tasks stay deterministic:
     - Each worker thread consumes data from a shared queue (e.g., a YAML job record), runs specific scripts, and stores outputs for Zo to inspect.
3. **Content Library Bridge**
   - A lightweight mapping file (e.g., `Personal/Knowledge/ContentLibrary/Luma/form_answers.md`) links question patterns to stored snippets.
   - During registration, Zo compares form labels with that map. If there is no match, it surfaces the question, collects your response, writes a new snippet file, and updates the mapping so future runs reuse it.
   - This keeps LLM-level interpretation inside Zo while Python handles storage/matching.
4. **Approval Loop + Refinement System**
   - Daily, Zo presents recommendations (topic/speaker scoring plus eligibility and travel buffers). Each approval/refusal updates a refinement registry so the scoring weights evolve.
   - If Zo sees new topics in you emails/links, it persists them to the registry so the next scan uses a more precise seed.

## Build Orchestrator + Worker Threads
| Thread | Responsibility | Inputs | Outputs | Failure Mode & Safeguards |
|---|---|---|---|---|
| **Discovery Worker** | Scrapes Luma discover pages + inbound newsletter links (via Playwright) | Jobs tagged `discover:<city>` or `discover:link` | `events/` JSON feed with metadata + event URLs | retries on network/cart; logs when layout changes; fails gracefully when login required; instrumentation to detect 404s vs. blockers |
| **Recommendation Worker** | Scores events vs. V’s topic/speaker profile, enforces 30m travel buffer, filters by calendar conflicts, writes digest to `state/daily_recommendations.md` | `events/` feed, `calendar/availability.json`, `refinement/topics.yaml` | approved list + rationale | Validate that calendar API responses include timezone; escalate to V if travel buffer would require partial attendance |
| **Registration Worker** | When V approves, runs `browser_runner` to register, uses Content Library to answer questions | Approved event + mapping file | Registration confirmation + new question list | If form questions emerge, mark job as `needs_human`; do not auto-submit without answers |
| **Content Learning Worker** | Watches for unanswered questions, asks V, writes new snippet and mapping entry | `missing_questions/` queue | New snippet file + map update | Append-only file writes with YAML front matter to keep history; log ambiguous matches for manual review |
| **Monitoring Worker** | Validates that Playwright jobs finish within expected time, resets browser session on memory/network hiccups | Runner logs | Health metrics + alerts | Detects if Playwright version fails (trigger install step) |

### Work queue / orchestration pattern
- Each worker reads the same `build_jobs.yaml` structure, e.g.: 
```yaml
- id: job-20251206-001
  type: discover
  params:
    city: san-francisco
  status: pending
```
- Workers acquire jobs via a simple locking mechanism (file rename or SQLite flag) and write results to `artifacts/<job-id>.json`.
- The orchestrator (main script) acts as a coordinator: it schedules jobs, watches completion, and routes outputs into the next worker.
- This approach avoids scattering `playwright` logic across numerous scripts and lets us add new task types (e.g., email inbox scraping) without tearing down existing flows.

## Content Library integration principles
1. **Snippet schema**: Each answer lives in `Personal/Knowledge/ContentLibrary/Luma/` in a markdown file with YAML front matter describing the question pattern, confidence, tags (e.g., `#Luma #form #bio`).
2. **Mapping file**: `form_answers.md` keeps question → snippet references plus fallback cues (e.g., `similarity_threshold`).
3. **Auto learning**: When V supplies an answer, Zo: (a) writes the snippet file, (b) updates the mapping, (c) marks the original registration job complete, and (d) logs “new knowledge added” to the knowledge registry so future automation uses it.

## Next steps (Builder handoff)
1. Create `N5/scripts/browser_runner.py` with the JSON contract described above, wired to Playwright.
2. Implement the build orchestrator script (maybe `N5/scripts/build_orchestrator.py`) that coordinates worker queue creation and job assignments.
3. Create templates for snippet files and mapping file updates, plus a lightweight CLI (e.g., `n5_luma_answer.py`) that the Content Learning Worker uses to persist answers.
4. Add tests/dry runs for each worker thread using saved HTML snapshots so we can detect layout rot before hitting production.

That’s the scoped-out architecture—modular worker threads supervised by a build orchestrator, a Playwright browser runner for event interactions, and a self-updating Content Library for every new answer.

