# Structure Analysis — What Went Wrong

**Problem**: Package has confusing, redundant structure that doesn't match V's N5 conventions

---

## Issues Found

### 1. Two `docs/` folders
```
./docs/                          ← Root level (wrong)
./Documents/                     ← Should be here (correct per N5 convention)
```

### 2. Two copies of Zero Touch Manifesto
```
./docs/zero_touch_manifesto.md
./Documents/zero_touch_manifesto.md
```

### 3. Two `scripts/` folders
```
./scripts/                       ← Root level (wrong)
./core/scripts/                  ← Where I put them (also wrong)
```
**Should be**: `N5/scripts/` per V's convention

### 4. No Knowledge hierarchy
**Missing**: `Knowledge/architectural/`, `Knowledge/stable/` distinction

### 5. No N5/ container
**Current**: Everything dumped at root
**Should be**: Most things under `N5/` to match V's structure

---

## V's Actual Structure (Reference)

```
/home/workspace/
├── Knowledge/           # Stable reference (SSOT)
│   ├── architectural/   # Design principles
│   └── stable/          # Long-term reference
├── Documents/           # Working documents
│   └── System/          # System docs
├── Lists/               # JSONL action items
├── Records/             # Staging area
└── N5/                  # The OS itself
    ├── commands/        # Command docs
    ├── config/          # System config
    ├── prefs/           # Preferences
    ├── schemas/         # Validation
    └── scripts/         # Executable scripts
```

---

## What I Did Wrong

1. **Didn't reference V's existing structure** before building
2. **Created redundant directories** (docs/ when Documents/ exists)
3. **No N5/ container** - dumped everything at root
4. **Ignored Knowledge hierarchy** - no stable/semi-stable distinction
5. **Rushed without checking** - violated my own P18 (Verify State)

---

## Correct Structure Should Be

```
n5os-core/
├── README.md                    # Entry point
├── LICENSE                      # MIT
├── bootstrap.sh                 # Installer
├── .gitignore                   # Privacy protection
│
├── Documents/                   # Working docs (NOT "docs/")
│   ├── N5.md                   # System overview
│   └── System/                 # System documentation
│       ├── zero_touch_manifesto.md
│       ├── SETUP_REQUIREMENTS.md
│       ├── FIRST_RUN_CHECKLIST.md
│       ├── ONBOARDING_DESIGN.md
│       ├── SESSION_STATE_GUIDE.md
│       ├── CONVERSATION_DATABASE_GUIDE.md
│       ├── CONSULTANT_GUIDE.md
│       ├── TELEMETRY_SERVICE_DESIGN.md
│       └── ROADMAP.md
│
├── Knowledge/                   # Stable reference (SSOT)
│   └── architectural/
│       └── architectural_principles.md
│
├── Lists/                       # JSONL system
│   ├── POLICY.md
│   ├── README.md
│   └── templates/
│       ├── ideas.jsonl.template
│       └── must-contact.jsonl.template
│
└── N5/                          # The OS core
    ├── commands/                # Command documentation
    ├── config/                  # System configuration
    ├── prefs/                   # Preferences (25 files)
    ├── schemas/                 # Validation (16 files)
    ├── scripts/                 # Executable scripts (4 core)
    └── personas/                # AI personas
        └── vibe_builder_persona.md
```

---

## Fix Strategy

1. **Delete redundant directories** (`docs/`, root `scripts/`)
2. **Move files to correct locations** per V's conventions
3. **Create N5/ container** and move core OS files
4. **Preserve Knowledge hierarchy** (architectural/)
5. **Update bootstrap.sh** to install to correct paths
6. **Test on fresh install** before pushing

---

**Status**: Analysis complete, ready to fix  
**Time to fix**: ~30 minutes  
**Lesson**: Always reference existing structure before building
