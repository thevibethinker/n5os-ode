# DEPRECATION NOTICE

**Date**: 2025-10-12  
**Status**: DEPRECATED - Do Not Use

## What Happened

This template system has been **replaced by the Block Type Registry** system as of version 4.0.0 of the `meeting-process` command.

## Why Deprecated

The template system caused inconsistent output because:

1. **Two competing systems existed:**
   - Template System (simple files with `{{VARIABLES}}`)
   - Registry System (sophisticated JSON with priorities, conditions, feedback)

2. **Command referenced Registry but Templates existed on disk:**
   - Different Zo instances made different choices
   - Resulted in three different output formats across meetings

3. **Templates were too simple:**
   - No priority levels
   - No conditional logic
   - No stakeholder combinations
   - No feedback mechanisms

## What Replaced It

**Block Type Registry**: `N5/prefs/block_type_registry.json`

This registry provides:
- 30+ block definitions (B01-B30)
- Priority levels (REQUIRED, HIGH, MEDIUM, CONDITIONAL)
- Exact format specifications
- Conditional generation rules
- Stakeholder-specific combinations
- Feedback markers for user feedback
- Comprehensive variable definitions

## Migration

All meeting processing now uses:
- **Source of Truth**: `N5/prefs/block_type_registry.json` (v1.3+)
- **Command**: `N5/commands/meeting-process.md` (v4.0.0+)
- **Output Format**: `B##_BLOCKNAME.md` (separate files per block)

## Archive Contents

This archive contains the old template system for historical reference:
- `internal/` - Templates for internal meetings
- `external/` - Templates for external meetings
- Various `.template.md` files with `{{VARIABLE}}` syntax

**DO NOT USE THESE TEMPLATES.** They are preserved only for Git history and reference.

## Related Changes

See handoff document: `N5/records/meetings/2025-09-23_carly-careerspan-2/BLOCK_SYSTEM_REALIGNMENT.md` (if exists)

Or conversation thread: con_HKvMSWJKndWJAsfg
