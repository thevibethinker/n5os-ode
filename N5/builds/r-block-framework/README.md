---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
---

# r-block-framework

R-Block Framework: Central Theory & Deep Analysis Prompts for Reflection Engine

## Objective

Transform skeleton R-block prompts into deep analytical frameworks with consistent substructure, plus integration layer for cross-reflection connections

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| w01_foundation | base_template | completed | - | 2h |
| w02_edge_infra | edge_infrastructure | completed | - | 1h |
| w03_r04_pilot | R04_Market | completed | w01_foundation | 3h |
| w04_r01 | R01_Personal | completed | w01_foundation, w03_r04_pilot | 2h |
| w05_r02 | R02_Learning | completed | w01_foundation, w03_r04_pilot | 2h |
| w06_r03 | R03_Strategic | completed | w01_foundation, w03_r04_pilot | 2h |
| w07_r05 | R05_Product | completed | w01_foundation, w03_r04_pilot | 2h |
| w08_r06 | R06_Synthesis | completed | w01_foundation, w03_r04_pilot | 2h |
| w09_r07 | R07_Prediction | completed | w01_foundation, w03_r04_pilot | 2h |
| w10_r08 | R08_Venture | completed | w01_foundation, w03_r04_pilot | 2h |
| w11_r09 | R09_Content | completed | w01_foundation, w03_r04_pilot | 2h |
| w12_r00 | R00_Emergent | completed | w01_foundation, w03_r04_pilot | 2h |
| w13_rix | RIX_Integration | completed | w01_foundation, w02_edge_infra, w03_r04_pilot | 4h |
| w14_orchestrator | process_reflection | completed | w13_rix, w04_r01, w05_r02, w06_r03, w07_r05, w08_r06, w09_r07, w10_r08, w11_r09, w12_r00 | 3h |

## Key Decisions

- 7-section common substructure for all R-blocks (Domain, Extraction, Analysis, Memory, Output, Connection Hooks, Worked Example)
- RIX as architecturally distinct special block (always runs)
- Both JSONL edges AND inline markdown for connections
- <100 words = lightweight capture only
- Query existing memory profiles; emergent integration-patterns store after 3+ occurrences
- R04 (Market) as pilot block

## Relevant Files

- `N5/builds/r-block-framework/PLAN.md`
- `N5/prefs/reflection_blocks_v2.md`
- `Prompts/Blocks/Reflection/R04_Market.prompt.md`
- `Prompts/Blocks/Generate_B08.prompt.md`
