"""
N5 OS Command Authoring System

A modular Python system for generating and authoring commands from natural language inputs.
Incorporates telemetry for logging and monitoring throughout the process.

Modules:
- conversation_parser: Parse user input into structured segments
- llm_scoping_agent: Use LLM to scope steps and clarify ambiguities  
- command_structure_generator: Generate structured command representation
- validation_enhancement: Validate and enhance command structure
- conflict_resolution_engine: Scan for conflicts and suggest adaptations
- safe_export_handler: Safely export to append-only commands.jsonl
"""

__version__ = "1.0.0"
__author__ = "N5 OS Command Authoring System"

# Import main functions for easier access
from .conversation_parser import parse_conversation, validate_segments
from .llm_scoping_agent import scope_and_clarify_segments, query_llm
from .command_structure_generator import generate_command_structure
from .validation_enhancement import validate_and_enhance_command
from .conflict_resolution_engine import resolve_conflicts_and_suggest
from .safe_export_handler import safe_export_command, validate_export_integrity

__all__ = [
    'parse_conversation',
    'validate_segments',
    'scope_and_clarify_segments',
    'query_llm',
    'generate_command_structure',
    'validate_and_enhance_command',
    'resolve_conflicts_and_suggest',
    'safe_export_command',
    'validate_export_integrity'
]