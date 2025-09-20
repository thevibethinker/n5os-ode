# TMP Execution Naming Conventions

## Purpose
Establish human-readable, greppable naming for executions to improve organization and searchability.

## Rules
1. **Human-Readable Names**: Execution folders should include a descriptive name derived from the plan's title or content, followed by the timestamp (e.g., `exec_hello_world_test_20250920_073731`).
2. **Greppable**: Names should use underscores for spaces, lowercase, and include keywords for easy grep searches (e.g., search for "hello_world" or "test").
3. **Fallback**: If no title is found, use a generic prefix like "execution_" + timestamp.
4. **Consistency**: All files within an execution folder retain original names for traceability.
5. **Future Extensions**: Add metadata tags in file content for better indexing (e.g., YAML frontmatter).

## Implementation
- Extract title from plan Markdown (e.g., first # header or "Intended Outcome").
- Sanitize: Lowercase, replace spaces with underscores, remove special chars.
- Append timestamp for uniqueness.

This ensures the system is greppable on-site and user-friendly.