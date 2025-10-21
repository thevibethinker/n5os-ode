---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 3e4b7e43018441818963a5d2d960765c
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/knowledge/ingestion_standards.md
---
# N5 Knowledge Ingestion Standards

## Purpose
Establish what information is ingested into the N5 knowledge reservoirs. The goal is to build a complete understanding of V (the user) and [COMPANY], focusing on biographical, historical, and strategic aspects that inform ongoing work and decision-making.

## Inclusion Criteria

### Ingest (Yes)
- Biographical information about V: background, education, career milestones, personal values, preferences
- Recurring characters in V's life: family, key colleagues, mentors, collaborators
- [COMPANY] company details: history, strategy, principles, culture, products/services
- Strategic information: long-term goals, market positioning, competitive advantages
- Historical context: key events, decisions, pivots that shaped V or [COMPANY]
- Operational patterns: recurring workflows, communication styles, decision-making frameworks

### Exclude (No)
- Transient operational details (e.g., daily tasks, short-term projects unless strategically significant)
- Sensitive personal information (financial details, health records, legal issues unless directly relevant to strategic understanding)
- Unverified rumors or speculation
- Competitive intelligence that violates ethical standards
- Information that could become outdated quickly (e.g., current market prices, unless part of strategic analysis)

## MECE Principle
All ingested information must be:
- **Mutually Exclusive**: No overlap between reservoirs or facts
- **Collectively Exhaustive**: Cover all aspects of V and [COMPANY] without gaps
- **Single Source of Truth**: Each piece of information has one canonical location for updates

## Pointers and Cross-References
- Use markdown links to reference related information across reservoirs
- Facts should tag related entities (e.g., `person:V`, `company:[COMPANY]`)
- Timeline entries should link to glossary terms and sources

## Adaptive Suggestions
When analyzing input, suggest new reservoirs or subcategories if the current structure doesn't fit emerging patterns (e.g., if recurring themes appear that don't fit bio/company/strategy).

## Future Expansion
As the system matures, expand to track:
- Opportunities and leads
- Customer relationships
- Partnership networks
- Market intelligence
- Personal development goals