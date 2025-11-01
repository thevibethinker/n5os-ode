# P29: Mock Data Discipline

**Category:** Development Hygiene  
**Priority:** P0 (System Integrity)  
**Added:** 2025-10-30

## Principle
Mock data, placeholder data, stub data, and test fixtures MUST be explicitly tracked and isolated from production code paths.

## The Problem
- Silent failures (dedup → 0, duplicates created)
- Missing data (mock API instead of real)
- Cascading bugs

## Requirements
**Dev:** Mark all mock data, track in SESSION_STATE Development section, run n5_safety.py  
**Prod:** No mock in production dirs, demo scripts need .DEMO suffix

## Detection Patterns
Filenames: mock|demo|stub|test|fake|dummy|example

## Real Example (2025-10-30)
Bug: meeting_transcript_scan.py had mock_google_drive_list_files() in main path  
Impact: 14 duplicates created when dedup state reset to 0  
Fix: Real API with pagination + persistent registry

## Related: P11, P15, P23
