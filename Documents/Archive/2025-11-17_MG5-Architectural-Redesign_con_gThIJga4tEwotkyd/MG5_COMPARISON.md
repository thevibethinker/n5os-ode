---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# MG-5 Comparison: Old vs New

**This is conversation con_gThIJga4tEwotkyd**

## Tasks Created

### ❌ OLD: MG-5 (Python-First)
- **Task ID:** `740666e0-50d9-48a6-98a8-0bfe2ac1d577`
- **Title:** "⇱ 🧠 Follow-Up Email Generation [MG-5️⃣]"
- **Schedule:** Every 30 minutes
- **Status:** Currently active (next run 2025-11-18T03:36:58Z)

### ✅ NEW: MG-5 v2.0 (LLM-First)
- **Task ID:** `33d5378d-4ded-469b-b329-f6cd38692add`
- **Title:** "Follow-up Email Generation for Meetings in [M] State"
- **Schedule:** 5x daily (6am, 10am, 2pm, 6pm, 10pm ET)
- **Status:** Created, next run 2025-11-18T06:00:14 ET

---

## Architecture Comparison

### OLD Architecture (Python-First)
```
Task → Python Script (n5_follow_up_email_generator.py)
  ↓
Script tries to:
- Understand meeting context (SEMANTIC ❌)
- Classify if follow-up needed (JUDGMENT ❌)
- Generate email content (CREATIVE ❌)
- Update manifest (MECHANICAL ✓)
```

**Problem:** Python doing semantic work leads to:
- ImportError with ContentLibrary
- False negatives ("no more need to be made")
- No emails actually generated

### NEW Architecture (LLM-First)
```
Task → Python (find meetings) → LLM (analyze each) → Python (save)
  ↓
Division of Labor:
- Python: File scanning, JSON updates (MECHANICAL ✓)
- LLM: Context understanding, judgment, content (SEMANTIC ✓)
```

**Benefits:**
- Clean separation of mechanics vs semantics
- LLM reads actual meeting content
- Semantic judgment per meeting
- Personalized content generation

---

## Key Differences

| Aspect | OLD (Python-First) | NEW (LLM-First) |
|--------|-------------------|-----------------|
| **Who decides if email needed?** | Python script logic | LLM semantic judgment |
| **How is content generated?** | Python templates | LLM generates in V's voice |
| **Context understanding** | Pattern matching | Read full transcript + blocks |
| **Internal vs external meetings** | Hard-coded rules | Semantic understanding |
| **Frequency** | Every 30 min | 5x daily |
| **Currently working?** | No (ImportError) | Ready to test |

---

## Testing Plan

### Phase 1: Comparison Run (Now)
1. Let OLD task run next cycle (03:36 UTC)
2. Let NEW task run next cycle (06:00 ET / 11:00 UTC)
3. Compare outputs

### Phase 2: Validation (After 1-2 days)
- Check: Are follow-up emails being generated?
- Check: Are manifests being updated correctly?
- Check: Are emails appropriate quality?

### Phase 3: Decision
If NEW works better:
- Deprecate OLD task (740666e0-50d9-48a6-98a8-0bfe2ac1d577)
- Keep NEW task (33d5378d-4ded-469b-b329-f6cd38692add)
- Update MG documentation

---

## Next Steps for V

1. **Monitor both tasks for 24-48 hours**
2. **Compare results:**
   - OLD: Likely continues producing no emails
   - NEW: Should generate semantic-driven emails
3. **Once validated, deprecate OLD task**

---

*Design complete. Ready for real-world testing.*

*2025-11-17 22:07:42 ET*

