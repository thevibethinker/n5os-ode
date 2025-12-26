# CHANGELOG

## [2.2.0] - 2025-10-27

### Added
- **Content Library System**: Link and snippet management for startup operators
  - Auto-classification by purpose, audience, and tone (30+ signals)
  - Multi-dimensional tagging and fast retrieval
  - Lifecycle management (versioning, deprecation, expiration)
  - JSON schemas for validation
  - 3 new commands: `content-add`, `content-search`, `content-stats`
  - Complete documentation in `Documents/CONTENT_LIBRARY.md`
  - Example config in `N5/prefs/system/examples/content-library.example.json`
- Generic system for founders managing bios, pitches, resources, references

### Documentation
- Added `Documents/CONTENT_LIBRARY.md` with complete usage guide
- Added command docs for content library operations

## [2.1.0] - 2025-10-26

### Added
- **Build Orchestrator System** - Parallel AI worker coordination

## [2.0.0] - 2025-10-26

### Added
- **Architectural Principles:** P24-P34 (11 new principles)
  - P24: Simulation Over Doing
  - P25: Code Is Free, Thinking Is Expensive
  - P26: Fast Feedback Loops
  - P27: Nemawashi Mode
  - P28: Plans as Code DNA
  - P29: Focus Plus Parallel
  - P30: Maintain Feel for Code
  - P31: Own the Planning Process
  - P32: Simple Over Easy
  - P33: Old Tricks Still Work
  - P34: Secrets Management (full framework)

- **Planning Framework:** `starter_planning_prompt.md` (simplified version)

- **Recipes:** 2 example workflows
  - `conversation-end.md` - Formal conversation closure
  - `git-check.md` - Pre-commit safety audit

- **Documentation:**
  - Comprehensive `Documents/N5.md` (6 → 311 lines)
  - Complete rewrite of `README.md` with Quick Start

### Changed
- **Architectural Principles Index:** Updated to include P1-P34
- **Documentation:** All docs reflect current system state

### Archived
- Old README.md → `_archive/README.md`
- QUICK_START.md → `_archive/QUICK_START.md`
- DEVELOPER_QUICKSTART.md → `_archive/DEVELOPER_QUICKSTART.md`
- bootstrap.sh → `_archive/bootstrap.sh`

### Security
- No credentials or secrets included
- P34 framework provided with sanitized examples
- All personal/business data excluded

## [1.0.0] - 2025-10-21

### Added
- Initial core foundation
- 26 essential scripts:
  - Session management (session_state_manager.py, conversation_registry.py)
  - Workspace utilities (n5_workspace_maintenance.py)
  - Safety checks (n5_git_check.py, n5_safety.py)
  - Knowledge & lists (n5_knowledge_add.py, n5_lists_add.py)
  - Conversation tools (n5_conversation_end.py, n5_thread_export.py)
  - Index management (n5_index_rebuild.py, n5_index_update.py)

- Initial architectural principles framework
- Basic directory structure
- Core schemas and configuration templates

---

## Version Naming

- **Major (X.0.0):** Breaking changes, major architectural shifts
- **Minor (x.Y.0):** New features, new principles, new scripts
- **Patch (x.y.Z):** Bug fixes, documentation updates, minor improvements

---

## Keeping Up to Date

This repo represents the **core foundation** of N5. For the latest:
- Check releases: https://github.com/vrijenattawar/n5os-core/releases
- Review changelog before updating
- Test in separate branch before merging to your fork

---

**Maintained by:** V (@vrijenattawar)  
**Built for:** Zo Computer (https://zo.computer)
