---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_Eu1OoHRtx1VWaR6g
worker_id: 1
title: CRM Semantic Search
status: ready
---
# Worker 1: CRM Semantic Search

## Objective
Find CRM profiles for all 10 brokers using semantic/fuzzy matching.

## Brokers to Search

1. Jennifer Ives
2. Ajit Singh
3. Kamina Singh  
4. Katherine Von Jan
5. Vir Kashyap
6. Colin Emerson
7. Michael Fanous
8. Reliance (org or contact?)
9. Ray Batra
10. Jeffrey Botteron (listed as "Jeffery Bot" in Notion)

## Search Strategy

1. **Exact match:** `Knowledge/crm/individuals/{firstname}-{lastname}.md`
2. **Fuzzy match:** Search CRM DB by name
3. **Email search:** If CRM has email field, cross-reference
4. **Organization match:** For "Reliance", check `Knowledge/crm/organizations/`

## Commands

```bash
# CRM individuals
ls /home/workspace/Knowledge/crm/individuals/ | grep -i <name>

# CRM DB search
sqlite3 /home/workspace/Knowledge/crm/crm.db "SELECT * FROM individuals WHERE name LIKE '%<name>%'"

# Full-text search
grep -ril "<name>" /home/workspace/Knowledge/crm/
```

## Output
Save matches to: `N5/builds/broker-enrichment/data/crm_matches.json`
