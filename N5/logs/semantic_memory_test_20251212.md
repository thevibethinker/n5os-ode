---
created: 2025-12-12
last_edited: 2025-12-12
version: 1.0
---

# N5 Semantic Memory Quality Assessment Report

**Generated:** 2025-12-12T02:49:09.942404
**Overall Score:** 75.4%

## 📊 Executive Summary

| Metric | Score | Status |
|--------|-------|--------|
| **Overall** | 75.4% | ✅ HEALTHY |
| Retrieval Quality | 75.0% | ✅ |
| Embedding Coherence | 100.0% | ✅ |
| Chunking Quality | 45.6% | ⚠️ |
| Coverage | 80.0% | ✅ |

## 📈 Database Statistics

- **Total Resources:** 1,150
- **Total Blocks/Chunks:** 4,751
- **Total Vectors:** 4,751
- **Average Chunk Size:** 865 chars
- **Chunk Size Range:** 16 - 1691 chars

## 🔍 Retrieval Quality

**Tests Passed:** 6/8
**Average Precision:** 57.5%
**Average Recall:** 83.3%

### Individual Test Results

#### ✅ Careerspan company query
- Query: `What is Careerspan and what does the company do?`
- Precision: 70.0%
- Path Matches: 7
- Top Results:
  - `/home/workspace/Documents/Deliverables/Careerspan/TechBuffalo_OnePager_Dec2024.m` (score: 0.8163)
  - `/home/workspace/Personal/Knowledge/Canon/Company/positioning.md` (score: 0.7964)
  - `/home/workspace/N5/prefs/communication/style-guides/blurbs.md` (score: 0.7559)

#### ✅ Meeting system architecture
- Query: `How does the meeting processing system work in N5?`
- Precision: 70.0%
- Path Matches: 7
- Top Results:
  - `/home/workspace/N5/capabilities/internal/meeting-pipeline-v2.md` (score: 0.8105)
  - `/home/workspace/Documents/System/architecture/meeting-processing-v3-architecture` (score: 0.7411)
  - `/home/workspace/N5/capabilities/integrations/akiflow-actions-bridge.md` (score: 0.7307)

#### ✅ CRM functionality
- Query: `How to add contacts to the CRM system?`
- Precision: 90.0%
- Path Matches: 9
- Top Results:
  - `/home/workspace/N5/workflows/crm_add_contact.prompt.md` (score: 0.8272)
  - `/home/workspace/N5/docs/crm_interface_guide.md` (score: 0.7707)
  - `/home/workspace/N5/workflows/crm_add_contact.prompt.md` (score: 0.7361)

#### ✅ Warm intro generator
- Query: `Generate warm introductions for networking`
- Precision: 60.0%
- Path Matches: 6
- Top Results:
  - `/home/workspace/Personal/Knowledge/Legacy_Inbox/crm/individuals/andrew-yeung.md` (score: 0.8178)
  - `/home/workspace/Personal/Knowledge/Legacy_Inbox/crm/individuals/andrew-yeung.md` (score: 0.7588)
  - `/home/workspace/Knowledge/reasoning-patterns/warm-intro-zero-signal-digest.md` (score: 0.7488)

#### ✅ Knowledge management
- Query: `How to store and retrieve knowledge in N5?`
- Precision: 60.0%
- Path Matches: 6
- Top Results:
  - `/home/workspace/Documents/Deliverables/N5OS-Lite-v2/n5os-lite/prompts/knowledge-` (score: 0.7070)
  - `/home/workspace/Documents/Deliverables/N5OS-Lite/n5os-lite-github/prompts/knowle` (score: 0.7070)
  - `/home/workspace/N5/capabilities/internal/positions-system.md` (score: 0.6569)

#### ❌ Embedding and vector search
- Query: `semantic search embedding vectors RAG`
- Precision: 0.0%
- Path Matches: 0
- Top Results:
  - `/home/workspace/N5/capabilities/internal/positions-system.md` (score: 0.6935)
  - `/home/workspace/Personal/Knowledge/ContentLibrary/content/2025-11-28_context-rot` (score: 0.6885)
  - `/home/workspace/Documents/Knowledge/Articles/2025-11-28_context-rot_chroma.md` (score: 0.6885)

#### ✅ Persona and routing
- Query: `Vibe personas and how routing works`
- Precision: 90.0%
- Path Matches: 9
- Top Results:
  - `/home/workspace/Documents/Deliverables/N5OS-Lite/n5os-lite-github/system/persona` (score: 0.8433)
  - `/home/workspace/N5/prefs/system/persona_routing_contract.md` (score: 0.8432)
  - `/home/workspace/Documents/Deliverables/N5OS-Lite-v2/n5os-lite/system/persona_rou` (score: 0.7279)

#### ❌ Scheduled tasks agents
- Query: `How do scheduled tasks and agents work?`
- Precision: 20.0%
- Path Matches: 2
- Top Results:
  - `/home/workspace/Personal/Knowledge/Canon/V/SocialContent/linkedin/2025-10-20-200` (score: 0.7238)
  - `/home/workspace/N5/capabilities/internal/task-intelligence-v1.md` (score: 0.7208)
  - `/home/workspace/Personal/Knowledge/Canon/V/SocialContent/linkedin/2025-10-20-200` (score: 0.6848)

## 🧬 Embedding Coherence

**Tests Passed:** 3/3
**Average Similarity:** 0.641
**Self-Similarity (same doc chunks):** avg=0.719, min=0.571, max=0.807

- ✅ **CRM profiles similarity**: similarity=0.793 (expected ≥0.50)
- ✅ **Meeting docs similarity**: similarity=0.616 (expected ≥0.60)
- ✅ **Knowledge ingest docs**: similarity=0.514 (expected ≥0.50)

## ✂️ Chunking Quality

**Chunks Analyzed:** 500
**Quality Score:** 45.6%
**Issues Found:** 54.4%

| Issue Type | Count |
|------------|-------|
| Truncated Sentences | 199 |
| Broken Markdown | 45 |
| Orphan Headers | 25 |
| Too Small (<100 chars) | 3 |
| Too Large (>3000 chars) | 0 |
| Ideal Size (200-2000) | 486 |

### Examples of Problematic Chunks

**/home/workspace/Knowledge/content-library/escape-dopamine-ho** - Issues: truncated_sentence
```
...00](https://youtube.com/watch?v=eXQ3VVRuy1I&t=0s)

```

**/home/workspace/Knowledge/content-library/escape-dopamine-ho** - Issues: truncated_sentence
```
...scrolling, watching pornography, eating junk food,
```

**/home/workspace/Knowledge/content-library/exa_deep_VC platfo** - Issues: truncated_sentence
```
...log/vc-platform-roles  
**Published:** 2023-07-28

```

## 📁 Coverage Validation

**Critical Files Indexed:** 4/5

### ❌ Missing Critical Files
- `/home/workspace/N5/README.md`

### Directory Coverage

| Directory | Indexed Files |
|-----------|---------------|
| N5 | 183 |
| Knowledge | 251 |
| Documents | 374 |
| Personal | 342 |
| Prompts | 0 |

## ⚖️ Hybrid vs Pure Semantic Search

**Tests Run:** 5
**Hybrid Wins:** 4 (80.0%)
**Semantic Wins:** 0 (0.0%)
**Ties:** 1
**Recommendation:** Use hybrid search (BM25 + semantic)

## 💡 Recommendations

1. Chunking has 54.4% issues - review chunking algorithm
2. Missing 1 critical files - run reindex
3. Hybrid search performs better - ensure BM25 is enabled

---
*Report generated by semantic_memory_quality_test.py*