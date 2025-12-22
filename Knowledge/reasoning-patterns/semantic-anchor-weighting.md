---
created: 2025-12-23
last_edited: 2025-12-23
version: 1.0
provenance: con_C0bA0iV26t5PdNUt
---

# Reasoning Pattern: Semantic Anchor Weighting

**Context:** Multi-source deduplication where unique identifiers (IDs) are missing (e.g., manual uploads).

**Problem:** Over-reliance on single-word overlaps in titles creates "False Positive Collisions" (e.g., "Project Alpha" colliding with "Project Beta" due to "Project").

**Pattern:** 
1. **Common Term Filtering:** Aggressively strip generic "meeting noise" words (Sync, Meeting, Call, Project, Review).
2. **Anchor Threshold:** Require at least **two** shared unique keywords for a match.
3. **Proportional Overlap:** If unique keyword sets are small (1-2 words), require >50% overlap of the total unique word set.

**Application:** Use this in file organization, duplicate detection, and semantic search filtering to balance recall and precision.

