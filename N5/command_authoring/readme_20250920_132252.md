# N5 OS Command Authoring System

A modular Python system for generating and authoring commands from natural language inputs, incorporating comprehensive telemetry and logging throughout the process.

## Overview

The Command Authoring System transforms natural language descriptions into structured, executable commands with built-in error handling, validation, conflict resolution, and telemetry. It follows the CLI executor pattern with retries and comprehensive logging.

## Architecture

The system is composed of 7 modular components that work together in a pipeline:

1. **Conversation Parser** (`conversation_parser.py`) - Parses user input into structured segments
2. **LLM Scoping Agent** (`llm_scoping_agent.py`) - Uses LLM to scope steps and clarify requirements
3. **Command Structure Generator** (`command_structure_generator.py`) - Generates structured command representation
4. **Validation & Enhancement** (`validation_enhancement.py`) - Validates and enhances commands with defaults
5. **Conflict Resolution Engine** (`conflict_resolution_engine.py`) - Detects conflicts and suggests adaptations
6. **Safe Export Handler** (`safe_export_handler.py`) - Safely exports to append-only commands.jsonl
7. **Main Orchestration** (`__main__.py`) - Coordinates all modules with CLI interface

## Features

- **Natural Language Processing**: Convert conversations into structured commands
- **LLM Integration**: Intelligent scoping and clarification of requirements
- **Comprehensive Validation**: Multi-layer validation with dry-run simulation
- **Conflict Detection**: Automatic detection of duplicate names and similar functionality
- **Auto-Resolution**: Automatic conflict resolution with naming adaptations
- **Safe Export**: Atomic append operations with backup and rollback capability
- **Redistillation**: Automatic optimization and deduplication of command storage
- **Rich Telemetry**: Comprehensive logging and metrics throughout the pipeline
- **CLI Interface**: Full command-line interface with multiple options

## Installation

The system is self-contained within the N5 directory structure. No additional installation required.

## Usage

### Basic Usage

```bash
# Generate command from text input
python -m command_authoring --input "Create a log analysis command that processes error patterns"

# Generate from file input
python -m command_authoring --input-file conversation.txt

# Dry run (don't export to file)
python -m command_authoring --input "Your command description" --dry-run

# Validate only (don't export)
python -m command_authoring --input "Your command description" --validate-only
```

### Advanced Usage

```bash
# Custom output file
python -m command_authoring --input "Command description" --output-file custom_commands.jsonl

# Skip conflict resolution
python -m command_authoring --input "Command description" --skip-conflicts

# Force export even if validation fails
python -m command_authoring --input "Command description" --force-export

# Enable debug logging
python -m command_authoring --input "Command description" --log-level DEBUG

# Log to file
python -m command_authoring --input "Command description" --log-file authoring.log

# Verbose output
python -m command_authoring --input "Command description" --verbose
```

### Input Examples

The system accepts various types of natural language input:

**Simple Task Description:**
```
Task: Create a file backup command
This should copy important files to a backup directory with timestamp.
```

**Detailed Requirements:**
```
Task: Implement log analysis workflow

Requirements:
1. Read log files from /var/logs/
2. Parse for ERROR and WARN patterns
3. Generate summary statistics
4. Export results to CSV format
5. Include proper error handling
6. Add progress indicators

Context: This will run daily via cron job
```

**Conversation Format:**
```
User: I need a command to process customer data
System: What type of processing do you need?
User: Extract email addresses and validate them
User: Also need to handle CSV and JSON input formats
User: Output should be clean contact list
```

## Output Format

Commands are exported to `commands.jsonl` in structured format with:

- **Metadata**: ID, name, version, timestamps, categories, tags
- **Execution Steps**: Detailed step-by-step execution plan
- **Configuration**: Retry logic, timeouts, error handling
- **Validation**: Input/output specifications and validation rules
- **Integration**: CLI compatibility, async capabilities, dependencies
- **Telemetry**: Comprehensive logging and monitoring configuration
- **Processing History**: Complete audit trail of generation process

## Pipeline Stages

### 1. Conversation Parsing
- Segments input into structured components (tasks, commands, context)
- Validates segment completeness
- Logs parse time and segment counts

### 2. LLM Scoping & Clarification
- Scopes requirements into actionable steps
- Performs clarification loops when needed
- Follows CLI executor patterns (retries, logging)
- Logs LLM queries/responses and confidence levels

### 3. Command Structure Generation
- Generates comprehensive command structure
- Incorporates wrapper patterns (retries, logging, validation)
- Determines complexity and resource requirements
- Logs generation time and structure metrics

### 4. Validation & Enhancement
- Validates required fields and structure
- Enhances with default configurations
- Performs dry-run simulation
- Logs validation results and risk assessment

### 5. Conflict Resolution
- Preemptive scanning for conflicts (duplicates, similar functionality)
- Automatic resolution strategies (renaming, adaptations)
- Generation of manual intervention suggestions
- Logs scan results and resolution actions

### 6. Safe Export
- Atomic append operations with backup creation
- File integrity verification
- Redistillation triggering for optimization
- Logs export status and file changes

## Telemetry & Monitoring

The system provides comprehensive telemetry:

**Timing Metrics:**
- Per-stage execution times
- Total pipeline duration
- LLM query latencies
- File operation timings

**Quality Metrics:**
- Validation success rates
- Conflict detection accuracy
- Dry-run risk assessments
- Confidence scores

**Operational Metrics:**
- Segments processed
- Steps generated
- Conflicts resolved
- Files exported

**Error Tracking:**
- Parse failures
- Validation errors
- Export failures
- Conflict resolution issues

## Configuration

The system uses intelligent defaults but can be configured through:

- Command-line arguments for runtime behavior
- Environment variables for system settings
- Configuration files for advanced settings (future)

## Error Handling

Multi-layer error handling throughout:

- **Graceful Degradation**: Fallback structures for failed generations
- **Rollback Capability**: Automatic rollback on export failures
- **Retry Logic**: Configurable retry strategies with backoff
- **Comprehensive Logging**: All errors logged with context

## Testing

Run the comprehensive test suite:

```bash
python -m command_authoring.test_command_authoring
```

Tests cover:
- Unit tests for each module
- Integration tests for complete pipeline
- Error handling scenarios
- Telemetry validation

## Examples

### Example 1: Simple File Processing Command

**Input:**
```
Create a command to process CSV files and extract email addresses
```

**Output:** Structured command with 6 steps including file reading, parsing, email validation, and export functionality.

### Example 2: Complex Workflow Command

**Input:**
```
Task: Build a log monitoring system

Features needed:
- Real-time log tailing
- Pattern matching for errors
- Alert generation
- Dashboard updates
- Performance metrics collection
```

**Output:** Multi-step command with async capabilities, monitoring configuration, and integration specifications.

## Troubleshooting

**Common Issues:**

1. **Empty Input**: Ensure input text is not empty or whitespace-only
2. **Validation Failures**: Use `--force-export` to bypass validation if needed
3. **Conflict Issues**: Use `--skip-conflicts` to disable conflict resolution
4. **Permission Issues**: Ensure write permissions for output directory

**Debug Mode:**
```bash
python -m command_authoring --input "Your text" --log-level DEBUG --verbose
```

**Dry Run Testing:**
```bash
python -m command_authoring --input "Your text" --dry-run --validate-only
```

## Development

The system is designed for extensibility:

- **Modular Architecture**: Each stage is independently replaceable
- **Plugin System**: Easy to add new processing stages
- **LLM Agnostic**: Simple interface for different LLM providers
- **Telemetry Integration**: Built-in metrics collection

## Version History

- **v1.0.0**: Initial implementation with full pipeline
  - Natural language processing
  - LLM integration
  - Conflict resolution
  - Safe export with redistillation
  - Comprehensive telemetry

## Contributing

The system follows defensive security practices:
- Input sanitization at all stages
- No execution of generated commands (export only)
- Comprehensive audit logging
- Safe file operations with atomic writes

## License

Part of the N5 OS ecosystem.