---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
---

# Zorg Due Diligence

Research best practices for crafting puzzle-based adventures, CTFs, and ARGs.

## Objective

Produce a detailed reference guide for Zorg's puzzle design, ensuring a high-quality, immersive experience inspired by DEF CON and best-in-class puzzle games.

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| worker_research_best_practices | best_practices_research | pending | - | 3h |
| worker_puzzle_taxonomies | puzzle_mechanics | pending | worker_research_best_practices | 2h |
| worker_player_psychology | ux_immersion | pending | worker_research_best_practices | 2h |
| worker_synthesis_critique | final_synthesis | pending | worker_puzzle_taxonomies, worker_player_psychology | 2h |

## Key Decisions

- Use Exa-powered research for deep dives
- Categorize by: Riddle Mechanics, Narrative Integration, Technical Puzzles, and Player Psychology
- Final synthesis must include a 'What's Missing?' self-critique

## Relevant Files

- `N5/builds/vibe-arg/CORE_ELEMENTS_LOCKDOWN.md`
- `N5/builds/vibe-arg/PLAN.md`
