# N5 OS Expansion Pack Architecture

**Design**: Modular system for shipping N5 functionality to other Zo instances  
**Date**: 2025-10-26  
**Status**: Architecture Proposal

---

## Core Question

**Should we pre-assemble expansion packs OR assemble on-the-fly?**

**Answer**: **Pre-Assemble** (with version control)

**Why**:
- ✅ Testable (validate pack works before shipping)
- ✅ Versionable (track what's in each pack)
- ✅ Documentable (each pack has README)
- ✅ Dependency-aware (declare requirements)
- ✅ Reproducible (same pack = same result)
- ✅ Quality control (curated, not dump-everything)

**vs. On-the-Fly**:
- ❌ Untested (might break)
- ❌ No version control
- ❌ Dependency hell
- ❌ Quality unpredictable

---

## Proposed Architecture

### 1. Core + Expansion Packs Model

```
N5 OS = CORE (required) + EXPANSION PACKS (optional, modular)

CORE (already built):
  └── Foundation for everything else

EXPANSION PACKS:
  ├── Meeting System
  ├── Communication Tools
  ├── Productivity Suite
  ├── Intelligence & Stakeholder
  ├── Deliverable Generation
  ├── Social Media Management
  ├── Job Sourcing (Careerspan)
  └── [Custom Packs]
```

---

## Natural Module Boundaries

Based on your current N5 system, here are the natural expansion packs:

### Pack 1: Meeting System
**What**: Complete meeting ingestion & processing  
**Size**: ~20 files, ~500 KB  
**Includes**:
- Meeting workflows (11 protocol docs)
- Meeting processing scripts (4-6 scripts)
- Meeting prep digest generation
- Transcript processing
- Intelligence extraction from meetings
- Integration with Lists (action items)

**Dependencies**: Core (lists, schemas)

**Use Case**: Anyone who has regular meetings and wants AI to process them

**Status**: Ready to package (already exists in your system)

---

### Pack 2: Communication Tools
**What**: Templates & generators for external communication  
**Size**: ~30 files, ~400 KB  
**Includes**:
- Email templates (follow-ups, intros, etc.)
- LinkedIn post generators
- Social post generators (multi-angle)
- Introduction generators
- Email post-processing
- Style guides for communication

**Dependencies**: Core (prefs, templates)

**Use Case**: Founders, professionals who need AI-assisted communication

**Status**: Ready to package

---

### Pack 3: Productivity Suite
**What**: Daily workflow automation & productivity tools  
**Size**: ~15 files, ~300 KB  
**Includes**:
- Daily prep digest generation
- Reflection ingestion
- Weekly summary generation
- Task prioritization
- Time blocking helpers
- Focus mode protocols

**Dependencies**: Core + Meeting System (optional)

**Use Case**: Knowledge workers optimizing daily workflow

**Status**: Ready to package

---

### Pack 4: Intelligence & Stakeholder Management
**What**: Relationship & intelligence tracking  
**Size**: ~25 files, ~600 KB  
**Includes**:
- Stakeholder profiling
- Relationship tracking
- Intelligence extraction
- Contact enrichment
- Stakeholder rules engine
- Opportunity tracking

**Dependencies**: Core (lists, schemas)

**Use Case**: Founders, BizDev, anyone managing relationships

**Status**: Ready to package

---

### Pack 5: Deliverable Generation
**What**: Structured document & deliverable creation  
**Size**: ~20 files, ~400 KB  
**Includes**:
- Deliverable templates
- Block-based generation
- Structured document assembly
- Output review system
- Quality checks
- Version control for deliverables

**Dependencies**: Core (templates, schemas)

**Use Case**: Consultants, service providers, anyone creating client deliverables

**Status**: Ready to package

---

### Pack 6: Social Media Management
**What**: Social content creation & scheduling  
**Size**: ~15 files, ~300 KB  
**Includes**:
- Social idea generation
- Post scheduling
- Multi-platform posting
- Content calendar
- Performance tracking
- Repurposing tools

**Dependencies**: Core

**Use Case**: Personal brands, entrepreneurs building social presence

**Status**: Ready to package

---

### Pack 7: Job Sourcing (Careerspan-Specific)
**What**: Specialized for job board management  
**Size**: ~20 files, ~500 KB  
**Includes**:
- Job scraping scripts
- Job source management
- Posting extraction
- Job board integration
- Careerspan-specific workflows
- Opportunity tracking for jobs

**Dependencies**: Core (lists)

**Use Case**: Careerspan users, job board operators

**Status**: Ready to package (but highly specialized)

---

### Pack 8: Advanced Automation (Future)
**What**: Complex workflow orchestration  
**Size**: TBD  
**Includes**:
- Workflow builder
- Multi-step automation
- Conditional logic
- Integration framework
- Scheduled task templates
- Agent composition patterns

**Dependencies**: Core + other packs

**Use Case**: Power users building custom workflows

**Status**: Future development

---

## Expansion Pack Structure

### Standard Pack Directory Layout

```
n5os-pack-[NAME]/
├── README.md              # What this pack does
├── DEPENDENCIES.md        # Requires: Core v1.0+
├── CHANGELOG.md           # Version history
├── install.sh             # Installation script
├── manifest.json          # Pack metadata
├── scripts/               # Python scripts
├── commands/              # Command docs
├── prefs/                 # Preferences (if any)
├── templates/             # Templates (if any)
├── schemas/               # Schemas (if any)
├── workflows/             # Workflow protocols
└── examples/              # Usage examples
```

---

## Pack Manifest Format

### `manifest.json` (Standard Metadata)

```json
{
  "name": "meeting-system",
  "version": "1.0.0",
  "description": "Complete meeting ingestion & processing system",
  "author": "Vrijen Attawar",
  "license": "Private",
  "n5_core_required": "1.0+",
  "dependencies": [
    {
      "pack": "core",
      "version": "1.0+"
    }
  ],
  "optional_dependencies": [
    {
      "pack": "intelligence",
      "version": "1.0+",
      "reason": "For stakeholder extraction from meetings"
    }
  ],
  "files": {
    "scripts": 6,
    "commands": 11,
    "workflows": 5,
    "prefs": 3
  },
  "size_kb": 500,
  "tested_with": ["Zo Computer v1.0"],
  "installation_time_minutes": 2,
  "tags": ["meetings", "productivity", "workflows"]
}
```

---

## Installation Mechanism

### Option A: Simple Script (Recommended for v1)

**Each pack has `install.sh`**:

```bash
#!/bin/bash
# N5 OS Expansion Pack Installer
# Pack: Meeting System v1.0

# Check dependencies
check_n5_core() {
  if [ ! -f "N5/prefs/prefs.md" ]; then
    echo "ERROR: N5 Core not found. Install core first."
    exit 1
  fi
}

# Install
install_pack() {
  echo "Installing Meeting System v1.0..."
  
  cp -r scripts/* N5/scripts/
  cp -r commands/* N5/commands/
  cp -r workflows/* N5/workflows/
  
  # Update command registry
  python3 update_commands.py
  
  echo "✓ Meeting System installed"
}

check_n5_core
install_pack
```

**Usage**:
```bash
cd n5os-pack-meeting-system
bash install.sh
```

---

### Option B: Central Installer (Future)

**Single installer manages all packs**:

```bash
n5os install meeting-system
n5os install communication-tools
n5os list-packs
n5os upgrade meeting-system
```

**Benefits**:
- Centralized dependency resolution
- Version management
- Upgrade path
- Uninstall capability

**Complexity**: Higher, implement later

---

## Dependency Management

### Levels of Dependencies

**1. Hard Dependencies** (required):
```json
"dependencies": [
  {"pack": "core", "version": "1.0+"}
]
```
→ Installation fails if missing

**2. Soft Dependencies** (optional):
```json
"optional_dependencies": [
  {"pack": "intelligence", "reason": "Enhanced stakeholder tracking"}
]
```
→ Warning if missing, installation continues

**3. Feature Flags** (conditional):
```json
"features": {
  "stakeholder_extraction": {
    "requires": ["intelligence-pack"],
    "enabled": false
  }
}
```
→ Features auto-enable when dependencies present

---

## Versioning Strategy

### Semantic Versioning for Packs

**Format**: `MAJOR.MINOR.PATCH`

**Examples**:
- `meeting-system v1.0.0` — Initial release
- `meeting-system v1.1.0` — Add new feature (backward compatible)
- `meeting-system v1.1.1` — Bug fix
- `meeting-system v2.0.0` — Breaking change (requires core v2.0+)

**Compatibility Matrix**:
```
Core v1.0 → Packs v1.x
Core v2.0 → Packs v2.x
```

---

## GitHub Repository Structure

### Option A: Monorepo (Recommended)

**Single repo, multiple packs**:

```
github.com/[USER]/n5os-system/
├── core/                    # Core package
├── packs/
│   ├── meeting-system/
│   ├── communication-tools/
│   ├── productivity-suite/
│   ├── intelligence/
│   ├── deliverable-generation/
│   ├── social-media/
│   └── job-sourcing/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PACK_DEVELOPMENT.md
│   └── INSTALLATION.md
└── README.md
```

**Pros**: Single version, easier coordination, shared docs
**Cons**: Larger repo size

---

### Option B: Multi-Repo

**Separate repo per pack**:

```
github.com/[USER]/n5os-core
github.com/[USER]/n5os-pack-meeting-system
github.com/[USER]/n5os-pack-communication-tools
...
```

**Pros**: Independent versioning, smaller clones
**Cons**: Harder to coordinate, duplicated docs

---

## Installation Flow for End Users

### Eric's Journey (Example)

**Step 1: Install Core**
```bash
git clone https://github.com/[USER]/n5os-system.git
cd n5os-system/core
bash bootstrap.sh
```

**Step 2: Browse Available Packs**
```bash
cd ../packs
ls -la
cat meeting-system/README.md
```

**Step 3: Install Pack(s)**
```bash
cd meeting-system
bash install.sh
```

**Step 4: Verify**
```bash
python3 ~/N5/scripts/meeting-process.py --help
```

**Step 5: (Later) Install More**
```bash
cd ../../packs/communication-tools
bash install.sh
```

---

## Pack Development Workflow

### Creating a New Pack

**1. Identify Module Boundaries**
- What problem does it solve?
- What files are needed?
- What are dependencies?
- Who is the target user?

**2. Create Pack Structure**
```bash
mkdir n5os-pack-[NAME]
cd n5os-pack-[NAME]
touch README.md DEPENDENCIES.md manifest.json install.sh
mkdir scripts commands workflows
```

**3. Populate Files**
- Copy relevant scripts from your N5 system
- Write command documentation
- Create workflow protocols
- Write examples

**4. Write manifest.json**
- Declare dependencies
- List files
- Set version

**5. Test Installation**
- Fresh Zo instance
- Install core
- Install pack
- Verify scripts work
- Check dependencies

**6. Document**
- README with clear use cases
- Installation instructions
- Examples
- Troubleshooting

**7. Version & Release**
- Tag in git: `v1.0.0`
- Update CHANGELOG
- Announce

---

## Quality Standards for Packs

### Before Releasing a Pack

**Checklist**:
- [ ] Works on fresh Zo instance with only core installed
- [ ] All scripts have `--dry-run` mode
- [ ] All dependencies declared in manifest.json
- [ ] README has clear use case explanation
- [ ] At least 2 examples included
- [ ] Installation script tested
- [ ] No hardcoded paths (use relative paths)
- [ ] No credentials or sensitive data
- [ ] Proper .gitignore
- [ ] Follows N5 architectural principles (P0-P30)
- [ ] Version number assigned
- [ ] CHANGELOG started

---

## Recommendations

### For Your Use Case

**1. Pre-Assemble Packs** ✅
- Create 6-7 standard packs (listed above)
- Test each independently
- Version control each
- Document thoroughly

**2. Monorepo Structure** ✅ (easier for now)
```
n5os-system/
├── core/
└── packs/
    ├── meeting-system/
    ├── communication-tools/
    └── ...
```

**3. Simple Install Scripts** ✅ (v1)
- Each pack has `install.sh`
- Manual dependency checking
- Clear error messages

**4. Future: Central Installer** (v2+)
- `n5os` CLI tool
- Auto-dependency resolution
- Pack marketplace concept

---

## Next Steps (Concrete Actions)

### Immediate (With Eric)

**1. Ship Core v2** ✅
- Already built, ready to deploy

**2. Create Pack 1: Meeting System**
- Extract from your N5 system
- Package according to structure above
- Test with Eric as first user

**3. Validate Approach**
- Does install.sh work?
- Are dependencies clear?
- Is documentation sufficient?

### Near-Term (After Eric Validates)

**4. Build 3-4 More Packs**
- Communication Tools (high value)
- Productivity Suite (high value)
- Intelligence (mid value)
- Pick based on Eric's needs

**5. Refine Process**
- Learn from Eric's experience
- Update pack structure
- Improve documentation

### Long-Term

**6. Pack Marketplace Concept**
- Central registry
- Community packs?
- Version management
- CLI installer

---

## Decision: Pre-Assemble or On-the-Fly?

**RECOMMENDATION: Pre-Assemble**

**Architecture**:
```
Pre-built, versioned, tested expansion packs
    ↓
Installed via simple scripts
    ↓
Future: CLI tool for management
```

**Why This Works**:
1. **Quality**: Test before shipping
2. **Versions**: Track what works
3. **Docs**: Each pack self-documenting
4. **Dependencies**: Declared explicitly
5. **Reproducible**: Same pack = same result
6. **Maintainable**: Update packs independently

---

## Summary

**Answer**: **Pre-assemble expansion packs**, using structure above.

**Natural Modules** (7 packs identified):
1. Meeting System
2. Communication Tools
3. Productivity Suite
4. Intelligence & Stakeholder
5. Deliverable Generation
6. Social Media Management
7. Job Sourcing (Careerspan)

**Mechanism**: Simple `install.sh` per pack (v1), CLI tool later (v2+)

**Repository**: Monorepo with `core/` and `packs/` directories

**Next**: Build Pack 1 (Meeting System) and validate with Eric

---

**Date**: 2025-10-26  
**Status**: Architecture Proposal  
**Ready for**: Implementation
