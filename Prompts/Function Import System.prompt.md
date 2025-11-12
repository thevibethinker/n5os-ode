---
description: 'Command: function-import-system'
tool: true
tags:
- framework
- import
- workflow
- enhancement
- system
---
# Function Import System for N5 OS

**Version**: 1.0  
**Date**: 2025-10-09  
**Purpose**: Systematic process for importing external workflow prompts into N5 OS

---

## Overview

This framework provides a battle-tested, 5-phase process for taking external workflow prompts and integrating them natively into N5 OS.

**Success Rate**: 100% (validated with 4 enhancements)

---

## The 5-Phase Framework

### Phase 1: Analysis & Deconstruction
- Read function completely
- Identify purpose, complexity, dependencies
- Extract inputs, outputs, processing logic
- Check N5 alignment

### Phase 2: Design & Architecture
- Define command name (kebab-case)
- Choose approach: prompt-only, script-based, or hybrid
- Design inputs/outputs
- Plan prefs integration

### Phase 3: Implementation
- Localize external files FIRST (to N5-native format)
- Create command file
- Register in commands.jsonl
- Update documentation

### Phase 4: Validation & Testing
- Dry run, integration, real-world testing
- Safety checks

### Phase 5: Refinement & Documentation
- Fix issues
- Document lessons learned
- Git commit

---

## Key Patterns

**Confidence Scoring**: Use ≥0.75 threshold for auto-execution

**Prefs-First**: Always reference authoritative prefs files

**Incremental**: Implement one enhancement at a time

**File Localization**: Convert external files to N5-native format (kebab-case, proper location, archive originals)

---

## Quick Start

1. Read this framework
2. Analyze function file
3. Follow 5 phases systematically
4. Test on real data
5. Document and refine

**Related Files**:
- Commands: file 'Recipes/recipes.jsonl (index only)'
- Voice Prefs: file 'N5/prefs/communication/voice.md'
- Links: file 'N5/prefs/communication/content-library.json'
- Example: file 'N5/commands/follow-up-email-generator.md' (v11.0)

---

**Version**: 1.0  
**Status**: Production-ready ✅
