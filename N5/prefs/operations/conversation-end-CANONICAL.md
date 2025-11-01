# Conversation-End: Canonical Workflow

**Version:** 2.0  
**Date:** 2025-11-01  
**Status:** Active

## ⚠️ CRITICAL: Only ONE Correct Workflow

The old monolithic script has been **completely removed**.

## Canonical 3-Phase Pipeline

**Phase 1: ANALYZE** (conversation_end_analyzer.py)
- Scan conversation workspace, classify files
- Output: analysis.json

**Phase 2: PROPOSE** (conversation_end_proposal.py)
- Generate human-readable proposal
- Show movements, conflicts, warnings

**Phase 3: EXECUTE** (conversation_end_executor.py)
- Execute with rollback support
- Archive and update state

## Active Scripts

✅ conversation_end_analyzer.py  
✅ conversation_end_proposal.py  
✅ conversation_end_executor.py  
✅ n5_conversation_end_v2.py (orchestrator)  

## Removed (2025-11-01)

❌ n5_conversation_end.py - DELETED (old monolithic)

## Usage

See: Prompts/Close Conversation.md
