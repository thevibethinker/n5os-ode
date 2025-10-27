---
description: '[DEPRECATED] Command: meeting-intelligence-orchestrator'
tags: [deprecated, archived]
---
# Meeting Intelligence Orchestrator

## ⚠️ DEPRECATED - DO NOT USE

**Deprecated:** 2025-10-27  
**Superseded by:** Registry-based Meeting Processing (v4.0.0+)

This template-based orchestration approach has been fully replaced by:
- file 'N5/prefs/block_type_registry.json' (v1.3+)
- file 'Recipes/Meetings/Meeting Process.md' (current)
- Registry-driven block generation with Zo's native LLM

## Migration Path

### Old Approach (Deprecated):
```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py
```

### New Approach (Current):
```bash
# Use the registry-based meeting process recipe
# Zo analyzes transcript directly using block_type_registry.json
```

See file 'Recipes/Meetings/Meeting Process.md' for current workflow.

## Why This Was Deprecated

1. **External LLM dependency** - Required API calls instead of using Zo's built-in capabilities
2. **Template rigidity** - Hard-coded templates instead of dynamic registry
3. **Token limitations** - API chunking vs. full context
4. **Maintenance overhead** - Python script maintenance vs. registry updates
5. **Cost** - Per-token API costs vs. included Zo capabilities

## Historical Reference

Preserved in: file 'N5/scripts/_DEPRECATED_2025-10-10/meeting_intelligence_orchestrator.py'

**Do not use for new implementations.**
