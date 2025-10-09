# Knowledge: Evolving Layer

This directory contains **contemporary knowledge** that changes frequently.

---

## Purpose

Evolving knowledge represents current state and recent learnings:
- SPO (Subject-Predicate-Object) triples in knowledge graph
- Recently read articles and extracted insights
- Current metrics and status
- Temporary facts with time-bound validity

---

## Files

- **`facts.jsonl`**: Knowledge graph as SPO triples
  - Subject: Entity (person, company, concept)
  - Predicate: Relationship or property
  - Object: Value or related entity
  - Confidence: 0.0-1.0 (typically 0.95-1.0)
  - Source: Attribution (URL, document, conversation)
  - Timestamp: When fact was added

- **`article_reads.jsonl`**: Reading history and extracted insights
  - URL, title, date read
  - Key takeaways
  - Relevance to Careerspan

---

## Structure

### facts.jsonl
```jsonl
{
  "subject": "Careerspan",
  "predicate": "has_employee_count",
  "object": "1",
  "confidence": 1.0,
  "source": "direct_knowledge",
  "timestamp": "2025-10-08T12:00:00Z"
}
```

### article_reads.jsonl
```jsonl
{
  "url": "https://example.com/article",
  "title": "AI in Career Coaching",
  "date_read": "2025-10-08",
  "takeaways": ["Key insight 1", "Key insight 2"],
  "relevance": "Product development"
}
```

---

## Characteristics

- **Changes Frequently**: Updated regularly as new information arrives
- **Time-Bound**: Facts may have expiration dates
- **Confidence Scored**: Each fact has reliability measure
- **Source Attributed**: Origin tracking for verification
- **Portable**: Schema-validated, exportable

---

## Usage

### Adding Facts
```bash
python3 /home/workspace/N5/scripts/n5_knowledge_add.py \
  --subject "Careerspan" \
  --predicate "launched_feature" \
  --object "AI resume builder" \
  --confidence 1.0 \
  --source "internal"
```

### Querying Knowledge
```bash
python3 /home/workspace/N5/scripts/n5_knowledge_query.py \
  --subject "Careerspan" \
  --predicate "has_*"
```

### Direct Processing
Use Zo directly to analyze documents and extract facts (no API calls).

---

## Maintenance

- **Deduplication**: Periodic scan for duplicate facts
- **Confidence Decay**: Some facts lose validity over time
- **Source Verification**: Check attribution integrity
- **Schema Validation**: Ensure compliance

---

## Related

- **Stable Knowledge**: `../stable/` (historical facts)
- **Schemas**: `../schemas/` (validation rules)
- **Scripts**: `/home/workspace/N5/scripts/n5_knowledge_*.py`
- **Direct Processing**: `../DIRECT_PROCESSING_README.md`

---

*Part of Knowledge Layer - Contemporary facts and insights*
