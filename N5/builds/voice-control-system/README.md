---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
---

# Voice Control System (Modes, Moves, Retrieval, Rubric)

Evolve LinkedIn reference blocks into a best-in-class voice control system: modes, moves library, anti-trope constitution, debranding, and evaluation rubric, wired into existing voice-library-v2 infrastructure.

## Objective

Enable low-review, high-fidelity generation that moves like V across LinkedIn posts, emails, and memos, with professionalism as the primary adjustable variable.

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| worker_modes | voice_modes | pending | - | 2h |
| worker_moves | moves_library | pending | - | 3h |
| worker_constitution | voice_constitution | pending | worker_moves | 2h |
| worker_debranding | debranding_playbook | pending | - | 3h |
| worker_rubric | evaluation_rubric | pending | worker_moves, worker_constitution | 2h |
| worker_retrieval_spec | retrieval_strategy | pending | worker_moves | 3h |
| worker_wiring_plan | integration_plan | pending | worker_modes, worker_moves, worker_constitution, worker_rubric, worker_retrieval_spec, worker_debranding | 3h |

## Key Decisions

- Voice stored at 3 resolutions: Atoms (phrases), Moves (thinking maneuvers), Monologues (reference blocks)
- Do/Don't constitution includes explicit anti-tropes; exclude Not-X-But-Y as a reusable template but allow individual instances
- Retrieval must be by rhetorical job + topic, not just semantic similarity
- Debrand by role/entity abstraction while preserving motion and cadence
- Evaluation via lightweight voice-fit rubric; aim for minimum ongoing review

## Relevant Files

- `N5/builds/voice-library-v2/PLAN.md`
- `N5/builds/voice-library-v2/linkedin_corpus.jsonl`
- `N5/review/voice/2026-01-12_linkedin-primitives_review.md`
- `N5/data/voice_library.db`
- `N5/data/voice_library_schema_v2.sql`
- `N5/scripts/linkedin_voice_extractor.py`
- `Documents/System/Sites-System.md`
