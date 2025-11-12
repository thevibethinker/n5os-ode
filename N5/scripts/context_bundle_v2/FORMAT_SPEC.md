---
created: 2025-11-11
last_edited: 2025-11-11
version: 1.0
---

# Context Bundle Format v2.0 - Specification

## Overview

The context bundle format v2.0 enables structured, YAML-based context serialization with both backward compatibility and enhanced security features.

## Format Structure

### Old Format (Compatibility - v1.x)

```yaml
# Simple key-value pairs for backward compatibility
context: |
  Multi-line text content
  Goes here

metadata:
  source: /path/to/source
  created: 2025-11-11T16:04:40Z

files:
  - path/to/file1.txt
  - path/to/file2.yaml
```

**Location**: Maintained in `/home/.z/workspaces/con_XXX/context.md`

**Use case**: Legacy systems, simple context sharing

### New Format (Structured - v2.0)

```yaml
# Structured context bundle with sections
bundle_format: 2.0
bundle_id: bundle_H3UuSUiwVB2pzGp2
conversation_id: con_H3UuSUiwVB2pzGp2

metadata:
  title: "Session State Implementation"
  description: "Implementation of session state management system"
  created: 2025-11-11T16:04:40Z
  updated: 2025-11-11T16:04:40Z
  generator: "spawn_worker.py v2.0"
  version: "2.0"
  parent_conversation: con_cJgeywufVZ8ICrPB

context:
  objective: "Create context bundle format v2.0"
  status: "in_progress"
  priority: "high"
  
  sections:
    - name: "core_implementation"
      type: "file"
      path: "context_bundle_v2/builder.py"
      description: "Core builder class"
      
    - name: "credential_scanner"
      type: "file"
      path: "context_bundle_v2/credential_scanner.py"
      description: "Credential scanning utilities"
      
    - name: "test_suite"
      type: "file_pattern"
      pattern: "context_bundle_v2/tests/test_*.py"
      description: "Test suite for v2.0"

files:
  - path: "/home/workspace/N5/scripts/context_bundle_v2/builder.py"
    type: "application/x-python"
    last_modified: 2025-11-11T16:04:40Z
    size: 12345
    
  - path: "/home/workspace/N5/scripts/context_bundle_v2/credential_scanner.py"
    type: "application/x-python"
    last_modified: 2025-11-11T16:04:40Z
    size: 6789

credentials:
  # Placeholder for detected credentials (scanned)
  findings: []
  # If credentials are needed, use references:
  # api_key: "${CONFIG_API_KEY}"
  # token: "${SESSION_TOKEN}"

security:
  credential_scanning: true
  sensitive_fields:
    - "api_key"
    - "token"
    - "secret"
    - "password"
  
legacy_compatibility:
  maintains_old_format: true
  old_format_path: "/home/.z/workspaces/con_XXX/context.md"
```

**Location**: `/home/.z/workspaces/con_XXX/bundle.yaml`

**Use case**: Enhanced context, security scanning, structured metadata

## Key Differences

| Feature | Old Format (v1.x) | New Format (v2.0) |
|---------|------------------|-------------------|
| Format | Text block in markdown | YAML structure |
| Metadata | Minimal | Rich (title, description, timestamps) |
| Files | Simple list | File metadata + patterns |
| Credentials | Not scanned | Automatic scanning |
| Structure | Flat | Hierarchical sections |
| Generator | `spawn_worker.py v1.x` | `spawn_worker.py v2.0` |

## Migration Path

### Phase 1: Dual Format (Current)
- Old format: `context.md` (default for compatibility)
- New format: `bundle.yaml` (alternative, opt-in)
- Both formats maintained simultaneously

### Phase 2: New Default
- New format becomes default
- Old format generated for backward compatibility
- Deprecation warning for old format

### Phase 3: Remove Old (Future)
- Only new format maintained
- Migration tool provided

## Schema Validation

The v2.0 format uses strict schema validation:

**Required fields**:
- `bundle_format` (must be "2.0")
- `bundle_id` (unique identifier)
- `conversation_id` (parent conversation)
- `metadata.created`
- `metadata.generator`

**Optional fields**:
- `metadata.updated`
- `metadata.title`
- `metadata.description`
- `metadata.parent_conversation`
- `context`
- `files` (array)
- `credentials`
- `security`
- `legacy_compatibility`

## Security Features

### Credential Scanning
Automatic detection of sensitive data:

1. **Keys**: API keys, access tokens
2. **Secrets**: Passwords, client secrets
3. **Identifiers**: Email addresses, conversation IDs
4. **Custom patterns**: Project-specific secrets

### Protection Methods
- Masking: Value truncation (`sk-...key`)
- Redaction: Complete removal of sensitive data
- References: Use environment variables (`${VAR_NAME}`)

### Configuration
```yaml
# In bundle.yaml
security:
  credential_scanning: true
  mask_sensitive: true  # Default: true
  sensitive_fields:
    - ".*key$"
    - ".*token$"
    - ".*secret$"
    - ".*password$"
```

## Implementation Components

### 1. Builder Class (`builder.py`)
- `ContextBundleBuilder`: Main builder class
- `create_bundle()`: Create new bundle
- `load_bundle()`: Load existing bundle
- `add_file()`: Add files with metadata
- `add_section()`: Add context sections
- `scan_credentials()`: Run credential scanner
- `save()`: Save both old and new formats

### 2. Credential Scanner (`credential_scanner.py`)
- `CredentialScanner`: Main scanner class
- `scan_text()`: Scan text content
- `scan_file()`: Scan file content
- `scan_yaml()`: Scan YAML structure
- Pattern matching for common credentials

### 3. Updated spawn_worker.py
- Detect v2.0 support
- Generate new format bundles
- Maintain backward compatibility
- CLI flags for format selection

## Usage Examples

### Creating a Bundle
```python
from context_bundle_v2.builder import ContextBundleBuilder

builder = ContextBundleBuilder(
    conversation_id="con_H3UuSUiwVB2pzGp2",
    title="My Project"
)

builder.add_section("overview", "High-level description")
builder.add_file("/path/to/file.py")
builder.scan_credentials()

# Save both formats
builder.save()
```

### Loading a Bundle
```python
from context_bundle_v2.builder import ContextBundleBuilder

builder = ContextBundleBuilder.load("/path/to/bundle.yaml")
print(builder.bundle_data['metadata']['title'])
```

### CLI Usage
```bash
# Generate v2.0 bundle (new format)
spawn_worker.py --format v2.0 --title "My Mission"

# Generate dual format (default)
spawn_worker.py  # Both context.md and bundle.yaml
```

## Testing Requirements

Minimum 12 tests covering:

1. **Builder Tests** (5 tests)
   - Create new bundle
   - Add sections and files
   - Save in both formats
   - Load existing bundle
   - Credential scanning integration

2. **Credential Scanner Tests** (5 tests)
   - Scan text content
   - Scan file content
   - Masking functionality
   - YAML structure scanning
   - Pattern matching accuracy

3. **Format Tests** (2 tests)
   - Old format compatibility
   - Schema validation

Total: **12+ tests**

## Future Enhancements

- **Bundle signing**: Cryptographic signatures for integrity
- **Schema versioning**: Bundle format migrations
- **Compression**: Optional GZIP compression for large bundles
- **Encryption**: Optional encryption for sensitive bundles
- **Bundle registry**: Centralized bundle management
- **Diff/merge**: Compare and merge bundles

## References

- `builder.py`: Implementation
- `credential_scanner.py`: Security utilities
- `tests/test_bundle_v2.py`: Test suite
- `spawn_worker.py v2.0`: Updated worker launcher

