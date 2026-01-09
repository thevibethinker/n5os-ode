---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
---

# Careerspan Sales Prospecting Engine

System that surfaces recruiters discussing problems Careerspan solves, enabling V to engage constructively and warm them into sales conversations.

## Objective

5 qualified NYC/SF recruiter prospects per day, surfaced with context and suggested engagement angles

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| w1_project_scaffold | project_structure | pending | - | ?h |
| w2_database_schema | database | pending | w1_project_scaffold | ?h |
| w3_search_queries | configuration | pending | w1_project_scaffold | ?h |
| w4_topic_monitor | core_engine | pending | w2_database_schema, w3_search_queries | ?h |
| w5_icp_scorer | qualification | pending | w2_database_schema | ?h |
| w6_pain_classifier | qualification | pending | w2_database_schema | ?h |
| w7_qualification_pipeline | orchestration | pending | w5_icp_scorer, w6_pain_classifier | ?h |
| w8_engagement_generator | engagement | pending | w7_qualification_pipeline | ?h |
| w9_cli | interface | pending | w4_topic_monitor, w7_qualification_pipeline, w8_engagement_generator | ?h |
| w10_daily_digest | delivery | pending | w9_cli | ?h |

## Key Decisions

- Separate project from TLE, shares x_api.py via symlink
- SQLite database for prospects and tweets
- Topic-based discovery (pain points) over bio-based search
- NYC/SF geo focus via bio keywords and location signals
- Basic tier X API: 10K tweets/mo budget → ~300/day → be selective with queries
- Qualification scoring: recruiter signals + pain alignment + engagement potential
- Human-in-the-loop: V reviews and sends all engagements manually

## Relevant Files

- `Projects/x-thought-leader/src/x_api.py`
- `Projects/x-thought-leader/db/tweets.db`
- `N5/builds/careerspan-sales-prospecting/PLAN.md`
