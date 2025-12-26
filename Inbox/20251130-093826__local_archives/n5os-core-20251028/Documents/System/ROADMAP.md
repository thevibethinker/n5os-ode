# N5 OS Core — Roadmap

**Current**: v1.0-core (Generous Base Layer)  
**Status**: Production Ready

---

## v1.0-core (SHIPPED ✅)

**Released**: 2025-10-26

- ✅ Core foundation (prefs, schemas, commands, scripts)
- ✅ Zero-Touch philosophy + architectural principles
- ✅ Vibe Builder persona
- ✅ 5 essential scheduled tasks + 2 optional
- ✅ Zo settings guide (5 critical rules)
- ✅ First-run checklist (45-min guided setup)
- ✅ How-to-build guide
- ✅ MIT license
- ✅ 65 files, <700 KB

---

## v1.1 (Interactive Onboarding) — 2 weeks

**Focus**: Personalization + Config Separation

### Features
- [ ] Interactive onboarding script (`onboard.py`)
  - 12 questions, 10-15 minutes
  - Generates personalized configs
  - Sets up initial lists/goals
  
- [ ] Config separation architecture
  - `user_config/` directory (never tracked)
  - `.gitignore` updated
  - Base configs vs. user overrides
  
- [ ] Telemetry foundation (opt-in, local-only)
  - `telemetry_settings.json`
  - Local logging to `N5/logs/telemetry.jsonl`
  - Privacy-first design

### Files Added
- `N5/scripts/onboard.py` — Interactive setup
- `user_config/` directory structure
- `defaults/` — Base configs to copy
- Updated `.gitignore`

**ETA**: 2 weeks after v1.0 validation

---

## v1.2 (Safe Updates) — 3-4 weeks

**Focus**: Pull upstream changes without losing personalization

### Features
- [ ] Update mechanism (`n5_update.py`)
  - Check for updates
  - Preview changelog
  - Apply with snapshot
  - Rollback support
  
- [ ] Snapshot system
  - Pre-update backups to `.n5_snapshots/`
  - Quick rollback if issues
  - Preserve user configs
  
- [ ] Merge strategy
  - Update system files
  - Preserve `user_config/`, `Lists/`, `Records/`
  - Smart merge for `N5/config/`

### Files Added
- `N5/scripts/n5_update.py` — Update manager
- `.n5_snapshots/` directory
- `CHANGELOG.md` — Version history

**ETA**: 4 weeks after v1.0

---

## v1.3 (Analytics & Polish) — 6 weeks

**Focus**: Usage insights + quality of life

### Features
- [ ] Telemetry dashboard
  - View local usage stats
  - Command frequency
  - Workflow patterns
  - Export for debugging
  
- [ ] Enhanced onboarding
  - Workflow recommendations based on focus
  - Auto-configure integrations
  - Sample data/templates
  
- [ ] Health checks
  - System validation
  - Config drift detection
  - Automated fixes

### Files Added
- `N5/scripts/n5_telemetry.py` — Analytics viewer
- `N5/scripts/n5_health.py` — System health checker
- Enhanced `onboard.py`

**ETA**: 6-8 weeks after v1.0

---

## Expansion Packs (Parallel Development)

**After core validation with Eric**

### Pack 1: Meeting System
- Meeting detection & ingestion
- Transcript processing
- Intelligence extraction
- 10-15 files, ~400 KB

### Pack 2: Communication Hub
- Email templates
- LinkedIn content
- Follow-up management
- 12-18 files, ~300 KB

### Pack 3: Document Generation
- Deliverable templates
- Structured output
- Multi-format export
- 15-20 files, ~400 KB

**See**: `file 'N5OS_EXPANSION_ARCHITECTURE.md'` for full plan

---

## Long-Term Vision

### Phase 1: Foundation (Q4 2025)
- ✅ v1.0: Generous core
- ⏳ v1.1: Personalization
- ⏳ v1.2: Safe updates
- ⏳ v1.3: Analytics

### Phase 2: Expansion (Q1 2026)
- Expansion Pack 1-3
- Community contributions
- Integration marketplace
- Shared workflow library

### Phase 3: Platform (Q2 2026)
- Multi-user support
- Team workflows
- Commercial licensing for packs
- Zo ecosystem integration

---

## Principles (Unchanging)

1. **User Privacy First** — Configs never leave their machine
2. **Generous Core** — Free forever, genuinely useful
3. **Safe Updates** — Never break user customizations
4. **Modular Design** — Choose what you need
5. **Zero-Touch Philosophy** — Organization as artifact, not activity

---

## Feedback Loop

**How we decide what's next**:
1. Eric validates v1.0 (1-2 weeks)
2. Gather feedback on pain points
3. Prioritize based on:
   - User need (high impact)
   - Effort (quick wins first)
   - Foundation work (enables future features)

**Current priority**: Get v1.0 working perfectly before adding more.

---

**Version**: 1.0-core  
**Last Updated**: 2025-10-26  
**Status**: Roadmap published  
**Next**: Eric validation → v1.1 planning
