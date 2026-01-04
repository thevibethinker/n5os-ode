---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.0
provenance: con_mgEc47MbgTrIuvq8
---

# PLAN: Block Prompt Consolidation

## Open Questions

1. ✅ RESOLVED: Should we consolidate to one location?
   - **Answer: YES** — Two locations creates drift. The worker should load prompts from `Prompts/Blocks/`
   - Rationale: `Prompts/Blocks/` is already user-invokable AND has the latest semantic memory features

2. What to do with `N5/prompts/blocks/`?
   - **Proposal:** Archive it, have worker point to `Prompts/Blocks/`

---

## Checklist

### Phase 1: Consolidation Architecture
- [ ] Update `worker_generate_blocks.py` to load from `Prompts/Blocks/`
- [ ] Create filename mapping (Generate_B08.prompt.md → B08)
- [ ] Archive `N5/prompts/blocks/` to `N5/.archive_block_prompts_YYYYMMDD/`
- [ ] Add redirect note in archived location

### Phase 2: Worker Block Selection Update
- [ ] Add B09 (Collaboration Terms) trigger keywords: partnership, deal, terms, pricing, agreement
- [ ] Add B10 (Relationship Trajectory) trigger: recurring contacts (via CRM/memory lookup)
- [ ] Add B12 (Technical Infrastructure) trigger: API, integration, platform
- [ ] Add B31 (Stakeholder Research) trigger: research, due diligence, intel
- [ ] Add B32 (Thought Provoking) trigger: all substantial meetings

### Phase 3: Memory Integration Test
- [ ] Verify N5MemoryClient can be imported in worker context
- [ ] Test semantic memory lookup for B07 CRM dedup
- [ ] Test B08 prior meeting lookup
- [ ] Document memory integration pattern for future blocks

---

## Phase 1: Consolidation Architecture

**Affected Files:**
- `N5/workers/worker_generate_blocks.py` — Change BLOCKS_DIR constant
- `N5/prompts/blocks/` — Archive entire directory
- `Prompts/Blocks/` — No changes (this becomes the SSOT)

**Changes:**

1. **worker_generate_blocks.py**
```python
# OLD
BLOCKS_DIR = Path("/home/workspace/N5/prompts/blocks")

# NEW
BLOCKS_DIR = Path("/home/workspace/Prompts/Blocks")
```

2. **Filename mapping function** (add to worker):
```python
def get_prompt_path(block_code: str, block_name: str) -> Path:
    """Map block code to prompt file in Prompts/Blocks/"""
    # New format: Generate_B08.prompt.md
    prompt_file = BLOCKS_DIR / f"Generate_{block_code}.prompt.md"
    if prompt_file.exists():
        return prompt_file
    
    # Fallback: old format B08_STAKEHOLDER_INTELLIGENCE.md
    old_file = BLOCKS_DIR / f"{block_code}_{block_name}.md"
    if old_file.exists():
        return old_file
    
    raise FileNotFoundError(f"No prompt found for {block_code}")
```

3. **Archive old prompts:**
```bash
mv N5/prompts/blocks N5/.archive_block_prompts_20260103
echo "Archived: Block prompts consolidated to Prompts/Blocks/" > N5/.archive_block_prompts_20260103/README.md
```

**Unit Tests:**
- Worker can load Generate_B08.prompt.md
- Worker correctly parses YAML frontmatter
- Block selection still works

---

## Phase 2: Worker Block Selection Update

**Affected Files:**
- `N5/workers/worker_generate_blocks.py` — `select_blocks()` method

**Changes:**

Add to `select_blocks()`:

```python
# B09: Collaboration Terms (partnership/deal tracking)
if any(word in transcript_lower for word in ["partnership", "deal", "terms", "pricing", "agreement", "contract", "negotiation"]):
    selected.append({"block_code": "B09", "block_name": "COLLABORATION_TERMS", "priority": 62, "category": "contextual"})

# B10: Relationship Trajectory (recurring relationships)
# Note: This requires CRM lookup - flag for memory-enabled meetings
if len(transcript_lower.split()) > 800:  # Substantial relationship-focused meeting
    selected.append({"block_code": "B10", "block_name": "RELATIONSHIP_TRAJECTORY", "priority": 58, "category": "contextual"})

# B12: Technical Infrastructure
if any(word in transcript_lower for word in ["api", "integration", "platform", "infrastructure", "architecture", "webhook"]):
    selected.append({"block_code": "B12", "block_name": "TECHNICAL_INFRASTRUCTURE", "priority": 63, "category": "contextual"})

# B31: Stakeholder Research
if any(word in transcript_lower for word in ["research", "due diligence", "background", "intel", "investigate"]):
    selected.append({"block_code": "B31", "block_name": "STAKEHOLDER_RESEARCH", "priority": 52, "category": "contextual"})

# B32: Thought Provoking Ideas (substantial meetings only)
if len(transcript_lower.split()) > 1000:  # Meaningful conversation
    selected.append({"block_code": "B32", "block_name": "THOUGHT_PROVOKING", "priority": 30, "category": "contextual"})
```

**Unit Tests:**
- Transcript with "API integration" triggers B12
- Transcript with "partnership terms" triggers B09
- Long transcripts (>1000 words) get B32

---

## Phase 3: Memory Integration Test

**Affected Files:**
- `N5/workers/worker_generate_blocks.py` — Add optional memory enrichment

**Changes:**

Add memory context loading (optional, graceful degradation):

```python
def load_memory_context(self, block_code: str, stakeholder_names: List[str]) -> Optional[Dict]:
    """Load semantic memory context for memory-enabled blocks"""
    try:
        from N5.cognition.n5_memory_client import N5MemoryClient
        client = N5MemoryClient()
        
        context = {"crm_profiles": [], "prior_meetings": []}
        
        for name in stakeholder_names:
            # Check CRM
            crm = client.search_profile(profile="crm", query=name, limit=2)
            if crm:
                context["crm_profiles"].extend(crm)
            
            # Check meeting history
            meetings = client.search_profile(profile="meetings", query=name, limit=3)
            if meetings:
                context["prior_meetings"].extend(meetings)
        
        return context if (context["crm_profiles"] or context["prior_meetings"]) else None
        
    except ImportError:
        logger.warning("N5MemoryClient not available - generating without semantic context")
        return None
    except Exception as e:
        logger.warning(f"Memory lookup failed: {e}")
        return None
```

**Unit Tests:**
- Memory client import works
- CRM search returns results for known contact
- Graceful fallback when memory unavailable

---

## Success Criteria

1. **Single source of truth:** Only `Prompts/Blocks/` contains block prompts
2. **Worker functional:** `worker_generate_blocks.py` loads prompts from new location
3. **New blocks active:** B09, B10, B12, B31, B32 generate when content triggers
4. **Memory integration:** Blocks can optionally load CRM/meeting context

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Worker breaks during migration | Keep archive, test before committing |
| Missing prompt files | Add fallback filename patterns |
| Memory client unavailable | Graceful degradation - generate without context |
| Performance regression | Memory lookups are optional, not blocking |

---

## Nemawashi (Alternatives Considered)

### Alternative A: Sync Both Locations
- **Pros:** No code changes to worker
- **Cons:** Creates ongoing maintenance burden, drift will happen again
- **Verdict:** ❌ Rejected — violates SSOT principle

### Alternative B: Consolidate to N5/prompts/blocks/
- **Pros:** Keeps prompts in N5 system directory
- **Cons:** Loses `tool: true` invokability, less discoverable
- **Verdict:** ❌ Rejected — user-facing prompts belong in Prompts/

### Alternative C: Consolidate to Prompts/Blocks/ ✅ SELECTED
- **Pros:** Single location, user-invokable, latest features
- **Cons:** Small code change to worker
- **Verdict:** ✅ Selected — cleanest architecture

---

## Handoff

Ready for Builder to execute Phases 1-3.

