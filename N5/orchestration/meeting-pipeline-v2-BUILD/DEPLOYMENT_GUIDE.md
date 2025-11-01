# Meeting Pipeline V2 - Deployment Guide

Version: 2.0
Build Complete: 2025-11-01
Architecture: Approach B (Script as Zo Agent)

## System Overview

Automated meeting intelligence pipeline with 30-60 minute SLA.

ARCHITECTURE:
Every 30 min → Zo agent → transcript_processor.py
  Phase 1 (Python): Detect transcripts
  Phase 2 (Zo): Intelligent block selection
  Phase 3 (Python): Queue blocks
  Phase 4 (Zo): Generate blocks
  Phase 5 (Python): Save + finalize

COMPONENTS:
- meeting_pipeline.db: Meeting tracking
- block_registry.db: Block queue + knowledge
- transcript_processor.py: Main script
- 15 block generation tools (Prompts/Blocks/)

MANUAL RUN:
python3 /home/workspace/N5/scripts/meeting_pipeline/transcript_processor.py --dry-run

AUTOMATED:
Scheduled task runs every 30 minutes

BUILD_ORCHESTRATOR: con_gEITMa8CweOAFip5
Completed: 2025-11-01 22:15 ET
