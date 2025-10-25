# Intended vs Actual Storage Pattern Analysis

Generated: 2025-10-24T15:20:00Z

## Pattern: Where Things SHOULD Go vs Where They ACTUALLY Land

### Resumes (10 misplaced at root)
**Intended**: `Documents/Resumes/`  
**Actual**: Root directory  
**Why**: Zo defaults to root when no explicit path given; upload workflows don't enforce destination  
**Anti-pattern**: AP-001 Root file sprawl (documents)

### Logs (2 misplaced at root)
**Intended**: `N5/logs/`  
**Actual**: Root directory  
**Why**: Bootstrap/diagnostic scripts write to CWD instead of canonical log path  
**Anti-pattern**: AP-002 System artifacts at root

### Projects (case duplicate)
**Intended**: Single canonical `Projects/` (or `projects/`)  
**Actual**: Both `Projects/` AND `projects/` exist  
**Why**: Inconsistent casing in mkdir commands; no case-normalization guard  
**Anti-pattern**: AP-003 Case-variant siblings

### SESSION_STATE.md artifacts
**Intended**: Conversation workspace only (`/home/.z/workspaces/con_*/`)  
**Actual**: Found in user workspace under Documents/Archive/, N5/logs/threads/  
**Why**: Thread archival copies conversation workspace to user space  
**Anti-pattern**: AP-004 Conversation artifacts leaking to user workspace

### Temporary staging (2 locations)
**Intended**: Unclear - both exist for different purposes?  
**Actual**: `Document Inbox/Temporary` AND `Records/Temporary`  
**Why**: Semantic confusion between "inbox triage" vs "working scratch"  
**Decision needed**: Clarify distinct purposes or consolidate

### Meeting notes (scattered)
**Intended**: Context-specific (Careerspan/, Personal/, etc)  
**Actual**: Loose `Notes/` at root  
**Why**: No command guidance on meeting note destination  
**Anti-pattern**: AP-005 Generic catch-all folders at root

### Unexpected top-level directories (20 extras)
**Intended**: 14 canonical top-level dirs (N5, Documents, Records, Knowledge, Lists, Projects, Careerspan, Personal, Images, Articles, Audio, Video, Recipes, Sites)  
**Actual**: 30 top-level dirs including: ATS, Backups, Commands, Document Inbox, Downloads, Exports, N5_mirror, Notes, Sync, Trash, Under Construction, Zo Consultancy, ZoATS, projects, plus dot-dirs  
**Why**: Ad-hoc folder creation without anchor enforcement  
**Anti-pattern**: AP-006 Uncontrolled top-level sprawl

## Root Causes

1. **No path guard on folder creation** → arbitrary mkdir succeeds
2. **Commands don't enforce destinations** → defaults to root or CWD
3. **Upload/download workflows lack routing** → lands at root
4. **Case-insensitive FS not enforced** → Projects vs projects both created
5. **Conversation artifact archival** → copies internal state to user workspace
6. **Unclear semantic boundaries** → "where does this go?" defaults to root or generic folder

## Enforcement Mechanisms Needed

1. **Pre-flight path guard**: Check new paths against anchors.json; reject or prompt for non-canonical
2. **Command-level routing**: Every file-creating command specifies destination via anchors
3. **Upload interceptor**: Route by file type/context (resume → Documents/Resumes, log → N5/logs)
4. **Case normalization**: Prevent case-variant siblings; warn on ambiguous casing
5. **Conversation boundary**: Never copy SESSION_STATE or internal artifacts to user workspace during archival
6. **Periodic hygiene audit**: Weekly digest of violations; quarterly consolidation prompts
