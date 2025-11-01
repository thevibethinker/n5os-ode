# BUILD WORKER 2: Tool-Based Block Generator (REVISED)

Build Orchestrator: con_gEITMa8CweOAFip5
Task: BW2-GENERATOR-TOOLS
Time: 45-60 minutes
Dependencies: BUILD_WORKER_1 complete

## Mission (REVISED)
Create pure tool-based block generation system using prompts as executable tools.

## Architecture Decision
TOOL-BASED (not API-based):
- Each block type = prompt in Prompts/Blocks/
- Stage 2 script loads prompt + injects transcript + captures Zo output
- No API calls needed - Zo interprets prompt instructions directly

## Deliverables
1. 15 block generation prompts in /home/workspace/Prompts/Blocks/
2. Register in executables.db
3. Stage 2 script: stage_2_generator.py
4. Test with Lisa Noble meeting

## Block Prompts to Create
B01, B02, B05, B07, B08, B13, B14, B15, B16, B17, B20, B22, B23, B24, B25, B26

## Implementation Steps

Step 1: Create block generation prompts (15 files)
- Each prompt has frontmatter: tool: true
- Includes generation instructions + output format
- Designed to accept transcript as context

Step 2: Register prompts
- Use executable_manager.py to register all

Step 3: Create stage_2_generator.py
- Load block prompts from Prompts/Blocks/
- Inject transcript data
- Execute (Zo interprets and generates)
- Capture output and save

Step 4: Test
- Run on Lisa Noble meeting
- Verify quality vs manual generation

Report when complete.

Created: 2025-10-31 20:26 ET
