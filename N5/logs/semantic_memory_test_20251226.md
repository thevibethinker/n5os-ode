---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
---

# N5 Semantic Memory Quality Assessment Report

**Generated:** 2025-12-26T16:47:11.229363
**Overall Score:** 75.0%

## 📊 Executive Summary

| Metric | Score | Status |
|--------|-------|--------|
| **Overall** | 75.0% | ✅ HEALTHY |
| Retrieval Quality | 75.0% | ✅ |
| Embedding Coherence | 100.0% | ✅ |
| Chunking Quality | 54.0% | ⚠️ |
| Coverage | 80.0% | ✅ |

## 📈 Database Statistics

- **Total Resources:** 4,320
- **Total Blocks/Chunks:** 17,550
- **Total Vectors:** 17,550
- **Average Chunk Size:** 791 chars
- **Chunk Size Range:** 16 - 5061 chars

## 🔍 Retrieval Quality

**Tests Passed:** 6/8
**Average Precision:** 50.0%
**Average Recall:** 83.3%

### Individual Test Results

#### ✅ Careerspan company query
- Query: `What is Careerspan and what does the company do?`
- Precision: 30.0%
- Path Matches: 3
- Top Results:
  - `/home/workspace/Personal/Meetings/Week-of-2025-12-08/2025-12-08_Loganhellomegang` (score: 0.7946)
  - `/home/workspace/Personal/Meetings/Week-of-2025-12-08/2025-12-08_Loganhellomegang` (score: 0.7945)
  - `/home/workspace/Personal/Meetings/Week-of-2025-12-01/2025-12-03_Alexcavenylogan-` (score: 0.7926)

#### ✅ Meeting system architecture
- Query: `How does the meeting processing system work in N5?`
- Precision: 70.0%
- Path Matches: 7
- Top Results:
  - `/home/workspace/N5/capabilities/internal/meeting-pipeline-v2.md` (score: 0.8015)
  - `/home/workspace/Documents/System/architecture/meeting-processing-v3-architecture` (score: 0.7411)
  - `/home/workspace/Personal/Meetings/_quarantine/2025-11-03_Plaud-VrijenaAI-Workflo` (score: 0.7379)

#### ✅ CRM functionality
- Query: `How to add contacts to the CRM system?`
- Precision: 80.0%
- Path Matches: 8
- Top Results:
  - `/home/workspace/N5/workflows/crm_add_contact.prompt.md` (score: 0.8205)
  - `/home/workspace/N5/docs/crm_interface_guide.md` (score: 0.7595)
  - `/home/workspace/Prompts/LinkedIn Review Queue.prompt.md` (score: 0.7292)

#### ✅ Warm intro generator
- Query: `Generate warm introductions for networking`
- Precision: 70.0%
- Path Matches: 7
- Top Results:
  - `/home/workspace/Prompts/Warm Intro Generator.prompt.md` (score: 0.7959)
  - `/home/workspace/Personal/Meetings/Week-of-2025-10-20/2025-10-24_Careerspan-sam-P` (score: 0.7391)
  - `/home/workspace/Prompts/warm-intro-generator.prompt.md` (score: 0.7345)

#### ✅ Knowledge management
- Query: `How to store and retrieve knowledge in N5?`
- Precision: 40.0%
- Path Matches: 4
- Top Results:
  - `/home/workspace/Personal/Knowledge/Architecture/ingestion_standards/INGESTION_ST` (score: 0.7419)
  - `/home/workspace/Documents/System/knowledge-pipeline-and-semantic-memory.md` (score: 0.7044)
  - `/home/workspace/Documents/Deliverables/N5_Bootstrap_v1.0.0/N5_Bootstrap_Package_` (score: 0.7021)

#### ❌ Embedding and vector search
- Query: `semantic search embedding vectors RAG`
- Precision: 0.0%
- Path Matches: 0
- Top Results:
  - `/home/workspace/N5/capabilities/internal/hybrid-rag-layer-v1.md` (score: 0.8585)
  - `/home/workspace/N5/capabilities/internal/hybrid-rag-layer-v1.md` (score: 0.7796)
  - `/home/workspace/Personal/Knowledge/Specs/wisdom_roots_system_outline.md` (score: 0.6858)

#### ✅ Persona and routing
- Query: `Vibe personas and how routing works`
- Precision: 90.0%
- Path Matches: 9
- Top Results:
  - `/home/workspace/Documents/System/personas/INDEX.md` (score: 0.8808)
  - `/home/workspace/Documents/System/personas/vibe_operator_persona.md` (score: 0.8488)
  - `/home/workspace/N5/prefs/system/persona_routing_contract.md` (score: 0.8351)

#### ❌ Scheduled tasks agents
- Query: `How do scheduled tasks and agents work?`
- Precision: 20.0%
- Path Matches: 2
- Top Results:
  - `/home/workspace/Personal/Knowledge/Legacy_Inbox/personal-brand/social-content/li` (score: 0.7976)
  - `/home/workspace/Personal/Meetings/Week-of-2025-12-15/2025-12-15_David-X-Careersp` (score: 0.7679)
  - `/home/workspace/Personal/Meetings/Week-of-2025-12-15/2025-12-15_Logandspeigellog` (score: 0.7626)

## 🧬 Embedding Coherence

**Tests Passed:** 3/3
**Average Similarity:** 0.641
**Self-Similarity (same doc chunks):** avg=0.729, min=0.571, max=0.807

- ✅ **CRM profiles similarity**: similarity=0.793 (expected ≥0.50)
- ✅ **Meeting docs similarity**: similarity=0.616 (expected ≥0.60)
- ✅ **Knowledge ingest docs**: similarity=0.514 (expected ≥0.50)

## ✂️ Chunking Quality

**Chunks Analyzed:** 500
**Quality Score:** 54.0%
**Issues Found:** 46.0%

| Issue Type | Count |
|------------|-------|
| Truncated Sentences | 153 |
| Broken Markdown | 46 |
| Orphan Headers | 28 |
| Too Small (<100 chars) | 3 |
| Too Large (>3000 chars) | 0 |
| Ideal Size (200-2000) | 485 |

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
| N5 | 252 |
| Knowledge | 309 |
| Documents | 484 |
| Personal | 3036 |
| Prompts | 198 |

## ⚖️ Hybrid vs Pure Semantic Search

**Tests Run:** 5
**Hybrid Wins:** 3 (60.0%)
**Semantic Wins:** 0 (0.0%)
**Ties:** 2
**Recommendation:** Use hybrid search (BM25 + semantic)

## 💡 Recommendations

1. Chunking has 46.0% issues - review chunking algorithm
2. Missing 1 critical files - run reindex

---
*Report generated by semantic_memory_quality_test.py*