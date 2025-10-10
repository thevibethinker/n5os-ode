# Deprecated Meeting Orchestrator Scripts

These scripts were replaced by `meeting_intelligence_orchestrator.py` on 2025-10-10.

## Why Deprecated

### 1. meeting_orchestrator.py (V2 Phased Workflow)
- **Replaced:** 2025-10-10
- **Reason:** Used removed `llm_utils` module with hardcoded block generation
- **Replacement:** `meeting_intelligence_orchestrator.py` with registry-based system

**Key differences:**
- Old: Direct LLM calls via `llm_utils.query_llm_internal()`
- New: Extraction request pattern with batch processing

### 2. meeting_info_extractor.py
- **Replaced:** 2025-10-10
- **Reason:** Moved into modular blocks/ system
- **Replacement:** `blocks/meeting_info_extractor.py`

## Do Not Use

These files are kept only as historical reference. The active script is:

**`/home/workspace/N5/scripts/meeting_intelligence_orchestrator.py`**

## Architecture Evolution

**V1 → V2 → V3 (Current)**

- **V1** (archived): Monolithic orchestrator with CRM integration
- **V2** (this folder): Phased workflow with `llm_utils` dependencies
- **V3** (active): Registry-driven extraction system

## Migration Notes

If you need to understand the old system for historical context, these files show:
- How the phased workflow concept originated
- Parameter inference and validation logic
- Simple extraction fallbacks used before LLM integration

---

**Do not import or execute these scripts.** They have broken dependencies and will fail.

**For current documentation, see:** `file 'N5/commands/meeting-process.md'`
