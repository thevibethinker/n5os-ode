---
tool: true
description: Ingest information into knowledge base with structured analysis
tags: [knowledge, workflow, ingest, analysis]
version: 1.0
created: 2025-11-03
---

# Knowledge Ingest

Ingest biographical, historical, or strategic information into knowledge base with LLM analysis and structured storage.

## Instructions

**You are ingesting knowledge. Process systematically and store in appropriate locations.**

### 1. Receive Input

**Input Format:**
- Raw text (transcripts, notes, articles)
- Structured data (meeting notes, research)
- Unstructured content (conversations, documents)

### 2. Analyze Content

**Analysis Steps:**

1. **Identify Type**
   - Biographical (people/relationships)
   - Historical (events/timeline)
   - Strategic (decisions/plans)
   - Technical (systems/processes)
   - Domain (specific field knowledge)

2. **Extract Structure**
   - Key entities (people, companies, concepts)
   - Relationships and connections
   - Timeline and causality
   - Actionable insights

3. **Assess Quality**
   - Confidence level (high/medium/low)
   - Source reliability
   - Completeness
   - Verification needed?

### 3. Store Appropriately

**Storage Locations:**

**Knowledge/domain/** - Domain-specific deep dives
- Technical specifications
- Industry knowledge
- Research findings

**Knowledge/people/** - Biographical information
- Stakeholder profiles
- Relationship maps
- Communication patterns

**Knowledge/strategic/** - Strategic decisions
- Business plans
- Market analysis
- Competitive intelligence

**Lists/** - Structured, queryable data
- Tools, resources, contacts
- Action items, ideas
- JSONL format for easy querying

### 4. Cross-Reference

**Link to Existing Knowledge:**
- Check if entity already exists
- Merge with existing information
- Create bidirectional links
- Update indices

### 5. Tag and Metadata

**Required Metadata:**
```yaml
source: [where it came from]
date_ingested: YYYY-MM-DD
confidence: [high|medium|low]
tags: [relevant, topics]
related_to: [linked entities]
```

## Output Format

**Knowledge File Structure:**
```markdown
# [Entity/Topic Name]

**Type:** [Biographical/Strategic/Technical/etc]  
**Source:** [Original source]  
**Date Ingested:** YYYY-MM-DD  
**Confidence:** [High/Medium/Low]

## Summary

[2-3 sentence overview]

## Key Points

- Point 1
- Point 2
- Point 3

## Detailed Analysis

[Full content with structure]

## Related Entities

- [[Entity 1]]
- [[Entity 2]]

## Tags

`tag1` `tag2` `tag3`

---
*Last Updated: YYYY-MM-DD*
```

## Quality Checks

Before finalizing:
- [ ] Content is structured and readable
- [ ] Metadata is complete
- [ ] Storage location is appropriate
- [ ] Cross-references are valid
- [ ] Confidence level is honest
- [ ] Sources are documented

## Examples

**Example 1: Biographical**
```
Input: "John leads product at TechCorp. MIT grad, 10 years PM experience."
Output Location: Knowledge/people/john-techcorp.md
Structure: Role, background, expertise, connections
```

**Example 2: Strategic**
```
Input: "Q4 plan focuses on enterprise pivot, hiring 3 engineers."
Output Location: Knowledge/strategic/q4-2025-plan.md  
Structure: Goals, actions, timeline, dependencies
```

**Example 3: Technical**
```
Input: "API uses OAuth2, rate limit 1000/hour, JSON responses."
Output Location: Knowledge/technical/techcorp-api.md
Structure: Specs, limitations, usage patterns
```

## Related

- Principles: P1 (Human-Readable First)
- Principles: P2 (Single Source of Truth)
- Principles: P16 (Accuracy Over Sophistication)
- System: `filesystem_standard.md` (storage locations)
- Prompt: `add-to-list.md` (for structured data)

---

**Knowledge compounds. Ingest systematically.**
