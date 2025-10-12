# Thread Export Implementation Plan

## Current State
- Script: `n5_thread_export.py` (757 lines)
- Current output: Simple AAR format with basic sections
- Schema: `aar.schema.json` (v2.0)

## Changes Needed

### Phase 1: Update generate_markdown() method
**Current**: Generates simple AAR with basic sections:
- Executive Summary
- Key Events & Decisions
- Final State
- Primary Objective
- Actionable Next Steps
- Metadata (collapsed)

**Target**: Generate comprehensive v2.0 format with:
- Header section with Thread ID, Export Date, Topic, Status
- Summary (2-3 sentences)
- Quick Start (First 10 minutes guide)
- What Was Completed (deliverables with status indicators)
- Critical Constraints (DO NOT CHANGE / MUST PRESERVE)
- Key Technical Decisions
- Known Issues / Gotchas
- Anti-Patterns / Rejected Approaches
- Integration Points & Next Steps
- Code Patterns / Quick Reference
- State Snapshot (file system, dependencies, commands status)
- Testing Status
- Open Questions
- If Stuck, Check These
- System Architecture Context
- Assumptions & Validations
- User Preferences (V's Style)
- Files Created/Modified
- Thread Lineage & Related Work
- Success Criteria
- Context for Resume
- Related Documentation
- Export Metadata

### Phase 2: Update Schema (if needed)
- Review new format requirements
- Add any missing fields to schema
- Ensure validation handles new structure

### Phase 3: Update data collection
- Add methods to gather additional context
- Enhance artifact analysis
- Add state snapshot collection
- Collect dependency information

### Phase 4: Testing
- Test with dry-run
- Validate schema compliance
- Verify markdown output quality

## Implementation Strategy

### Step 1: Backup current script
Create backup of working version

### Step 2: Update generate_markdown() - Header sections
- Add new header with Status field
- Add Summary section
- Add Quick Start section

### Step 3: Update generate_markdown() - Core sections  
- Transform "What Was Completed"
- Add Critical Constraints
- Add Key Technical Decisions
- Transform Known Issues/Gotchas

### Step 4: Update generate_markdown() - Technical sections
- Add Anti-Patterns
- Transform Integration Points & Next Steps
- Add Code Patterns
- Add State Snapshot

### Step 5: Update generate_markdown() - Support sections
- Add Testing Status
- Add Open Questions
- Add If Stuck guide
- Add System Architecture Context

### Step 6: Update generate_markdown() - Context sections
- Add Assumptions & Validations
- Add User Preferences
- Update Files Created/Modified
- Add Thread Lineage

### Step 7: Update generate_markdown() - Final sections
- Add Success Criteria
- Add Context for Resume
- Update Related Documentation
- Update Export Metadata

### Step 8: Test and validate
- Run with --dry-run
- Check schema validation
- Verify output quality
