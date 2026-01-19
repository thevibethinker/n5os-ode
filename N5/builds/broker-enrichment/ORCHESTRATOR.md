---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_Eu1OoHRtx1VWaR6g
---
# Deal Broker Enrichment & Notion Sync

## Objective

Populate the Notion "Deal Brokers" database with enriched profiles from:
1. CRM profiles (semantic search)
2. Meeting records (context for angle/blurb customization)
3. Email history (for brokers without CRM profiles)
4. Granola records (for Ray Batra specifically)

## Brokers to Enrich (10 total)

| # | Broker | Notion Page ID | Status |
|---|--------|----------------|--------|
| 1 | Jennifer Ives | `2ec5c3d6-a5db-8001-915a-c7eb74d380fa` | 🔴 Pending |
| 2 | Ajit Singh | `2ec5c3d6-a5db-802b-a9ee-e5367995c5d9` | 🔴 Pending |
| 3 | Kamina Singh | `2ec5c3d6-a5db-804f-95f9-d95a150b84be` | 🔴 Pending |
| 4 | Katherine Von Jan | `2ec5c3d6-a5db-8056-9d06-de12d7d4debb` | 🔴 Pending |
| 5 | Vir Kashyap | `2ec5c3d6-a5db-8057-922b-c64323927ff7` | 🔴 Pending |
| 6 | Colin Emerson | `2ec5c3d6-a5db-805b-9ed7-f26d2d5eafb6` | 🔴 Pending |
| 7 | Michael Fanous | `2ec5c3d6-a5db-8099-bd13-db047bc8407e` | 🔴 Pending |
| 8 | Reliance (contact TBD) | `2ec5c3d6-a5db-80e6-a408-c4b14f0abbd1` | 🔴 Pending |
| 9 | Ray Batra | `2ec5c3d6-a5db-80f4-98b4-eab69ff37d59` | 🔴 Pending |
| 10 | Jeffery Bot (= Jeffrey Botteron) | `2ec5c3d6-a5db-80fd-aff4-c3ac5fd88ab7` | 🔴 Pending |

## Notion Fields to Populate

| Field | Type | Source |
|-------|------|--------|
| Contact | Title | Already filled |
| Email | Email | CRM / Email search |
| LinkedIn | Rich text | CRM / Web search |
| Current Org | Rich text | CRM / Meeting context |
| Angle / Strategy | Rich text | Meeting context + intro target |
| Shareable Blurb for Them | Rich text | Careerspan pitch customized per broker |

## Workers

| # | Worker | Purpose | Parallel? |
|---|--------|---------|-----------|
| 1 | CRM Search | Semantic search CRM for all 10 brokers | No |
| 2 | Meeting Search | Find meetings with each broker | Yes (with W1) |
| 3 | Granola Search | Find Ray Batra's Granola record | Yes (with W1,W2) |
| 4 | Email Reconstruction | For brokers without CRM, search email + create profiles | After W1 |
| 5 | Blurb Generation | Generate customized Careerspan blurbs per broker | After W1-4 |
| 6 | Notion Push | Push enriched data to Notion | After W5 |

## Standard Careerspan Pitch (Base)

```
Careerspan helps professionals articulate their authentic career story. 
With 4,000+ users averaging 45+ minutes of deep self-reflection, we've built 
a platform that captures who people really are—beyond what AI can fabricate 
on a resume. [CUSTOMIZE: specific relevance to broker's network/intro target]
```

## Data Sources

- **CRM:** `file 'Knowledge/crm/individuals/'` 
- **Meetings:** `file 'Personal/Meetings/'`
- **Granola:** `file 'Records/granola/'` or similar
- **Email:** Gmail via `use_app_gmail`

## Output Artifacts

- `file 'N5/builds/broker-enrichment/data/broker_profiles.json'` — Collected data per broker
- `file 'N5/builds/broker-enrichment/data/notion_payloads.json'` — Ready-to-push Notion updates
