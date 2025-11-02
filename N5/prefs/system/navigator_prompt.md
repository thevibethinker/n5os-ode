# N5 Navigator
Quick Reference for N5 System Structure

Version: 1.0 | Created: 2025-11-02 | Limit: <7k chars

## Purpose
Quick reference for navigating N5. Load when you need to know WHERE things are.

## Directory Structure (3 levels)

N5/
├── prefs/               # Configuration & prompts
│   ├── operations/      # planning_prompt.md
│   ├── strategic/       # thinking_prompt.md
│   ├── system/          # navigator (this), nuance-manifest
│   ├── principles/      # P36, P37 YAMLs, decision_matrix
│   └── communication/   # Style guides
├── scripts/             # Executable Python scripts
│   ├── executable_manager.py
│   ├── debug_logger.py
│   └── n5_protect.py
├── data/                # Databases, indices
│   └── executables.db
├── builds/              # Active projects
└── logs/threads/        # Conversation archives

## Key Scripts
- executable_manager.py: search registered prompts
- debug_logger.py: append/recent/patterns
- n5_protect.py: check path protection

## Persona Switching
Current personas: Architect, Builder, Strategist, Teacher, Writer, Debugger, Operator (base)

Switch: set_active_persona with persona_id
Return to Operator: persona_id 90a7486f-46f9-41c9-a98c-21931fa5c5f6

## Workflow Patterns

### Building: 
1. Load planning_prompt.md
2. Think→Plan→Execute (70/20/10)
3. Identify trap doors
4. Execute with Builder if complex

### Strategic:
1. Load thinking_prompt.md
2. Apply mental models
3. Nemawashi (2-3 alternatives)
4. Document decision

### Multi-Domain (P36):
1. Coordinator spawns specialists
2. Each produces artifacts
3. Coordinator integrates

### Refactor (P37):
1. Read before write
2. Preserve working parts
3. One concern at a time
4. Test and commit frequently

## File Locations

Config:
- N5/prefs/operations/planning_prompt.md
- N5/prefs/strategic/thinking_prompt.md
- N5/prefs/system/navigator_prompt.md
- N5/prefs/system/nuance-manifest.md

Principles:
- N5/prefs/principles/P36_orchestration_pattern.yaml
- N5/prefs/principles/P37_refactor_pattern.yaml
- N5/prefs/principles/decision_matrix.md

Knowledge:
- Knowledge/architectural/planning_prompt.md
- Knowledge/architectural/research_frameworks.md

## When To Load
LOAD: Need locations, switching personas, finding scripts
DONT LOAD: Already know locations, mid-execution

v1.0 | 2025-11-02
