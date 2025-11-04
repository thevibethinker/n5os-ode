# LLM-Based Extraction Design

## Current Problem
- 4 different regex parsers for 4 format variants
- Routing logic has bugs (substring matching)
- Can't handle format variations
- Silent failures when format doesn't match

## Solution: LLM Interpreter
Replace regex parsing with LLM that reads B31 content and extracts insights.

## Flow
1. Read B31 file content
2. Send to LLM with extraction prompt
3. LLM returns structured JSON with all insights
4. Insert into database

## Advantages
- Handles all format variations (H2, H3, bold, numbered, narrative)
- Extracts semantic meaning, not just pattern matching
- Can infer missing fields (category, signal strength)
- Single code path instead of 4 parsers

## Implementation
Use existing gtm_backfill_llm.py script - check if it's already set up for this.
