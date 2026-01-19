---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_HlPJMzaB3VXQtuD0
---

# After-Action Report: Mind Map Layout Fix

**Date:** 2026-01-19  
**Duration:** ~2.5 hours  
**Conversation:** con_HlPJMzaB3VXQtuD0  
**Tier:** 3 (Full Build/Debug)

## Mission

Fix the Mind Map page layout on vrijenattawar.com where the ForceGraph2D visualization was not filling the available viewport space between the left sidebar and right detail panel, leaving large areas of empty black space.

## Outcome: Partial Success (80%)

The graph now renders properly and fills significantly more of the available space. However, achieving true edge-to-edge filling would require either distorting the graph's natural proportions or implementing complex force configuration changes.

## What Happened

### Initial State
- Screenshot showed graph clustered in upper-left of viewport
- Massive black empty space between graph content and right panel
- Graph appeared to be sized for a much smaller container

### Root Cause Analysis
1. **Width calculation issue** - Some edits introduced double-subtraction of sidebar widths
2. **zoomToFit behavior** - The library's `zoomToFit()` function preserves the graph's aspect ratio, fitting nodes within the viewport but not stretching to fill rectangular spaces
3. **Force-directed layout geometry** - D3 force simulations naturally produce roughly circular node distributions, not wide rectangles

### Attempted Fixes
1. ✅ Fixed `right-[384px]` → `right-96` for consistency
2. ✅ Reduced zoomToFit padding from 60px → 10px
3. ✅ Added `onEngineStop` callback to trigger fit after simulation stabilizes
4. ❌ Attempted complex force reconfiguration (introduced breaking changes)
5. ❌ Attempted viewport normalization stretch (broke rendering)

### Recovery
Multiple aggressive edits introduced breaking changes (wrong API endpoints, missing variables, concept-specific filtering on non-concept data). Had to `git checkout` to restore working state and apply only minimal changes.

## Key Learnings

### Technical
- **ForceGraph2D zoomToFit preserves aspect ratio** - This is by design. The library fits the bounding box of all nodes into the viewport with specified padding, but will not stretch or skew to fill non-matching aspect ratios.
- **Force-directed layouts are inherently circular** - Without explicit constraints, D3 force simulations converge to roughly circular/oval distributions. Making a force layout fill a wide rectangle requires either custom forces or accepting distortion.

### Process
- **Minimal targeted edits > wholesale refactoring** - When working with complex React components, making small precise changes is safer than attempting to refactor multiple systems at once.
- **edit_file_llm scope creep** - The LLM edit tool sometimes introduces unrelated changes across distant parts of files. Verify the full diff after each edit.
- **Git as safety net** - Committing working states before experiments allows quick recovery.

## What Worked
- Restoring from git when things broke
- Reducing padding to 10px for tighter fit
- Using `onEngineStop` for proper timing of zoomToFit

## What Didn't Work
- Attempting to add complex force configuration (forceRadial, forceCenter)
- Attempting non-uniform viewport stretching
- Making multiple simultaneous changes to the component

## Recommendations

For future layout improvements:
1. **Accept aspect ratio constraint** - The graph will always have some margin in wide viewports unless distorted
2. **If edge-to-edge is critical** - Consider a different visualization library or custom canvas rendering with non-uniform scaling
3. **Alternative approach** - Adjust sidebar widths or use collapsible panels to give graph more viewport area

## Files Modified

- `Sites/vrijenattawar/src/pages/MindMap.tsx` - zoomToFit padding reduction

## Git Status

32 uncommitted changes - review before committing.
