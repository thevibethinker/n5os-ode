---
created: 2025-12-08
last_edited: 2025-12-08
version: 1.0
---

# N5OS Lite v2.0.0 Release Notes

## 📦 Distribution Files

| File | Size | Format |
|------|------|--------|
| `n5os-lite-v2.0.0.tar.gz` | 179 KB | Linux/Mac |
| `n5os-lite-v2.0.0.zip` | 247 KB | Windows/Universal |

## ✅ What's Fixed

### Privacy (Critical)
- **Complete PII sanitization** - No personal names, company names, or identifying information
- Removed all references to specific individuals
- Removed all company-specific content
- Sanitized example data and templates

### Previously Leaked (Now Fixed)
- `n5_knowledge_ingest.py` - Was containing full biographical details → Now a clean template
- `n5_thread_export.py` - Was referencing specific names → Now generic
- `n5_export_core.py` - Was referencing specific identifiers → Now generic

## 🆕 What's New (Since v1.2.3)

### New Scripts
| Script | Purpose |
|--------|---------|
| `session_state_manager.py` | Track conversation state across complex workflows |
| `n5_load_context.py` | Dynamic context loading by task type |
| `debug_logger.py` | Debug logging for troubleshooting loops |

### New System Components
- **Persona routing contract** - Defines when to switch between AI personas
- **Context manifest** - Configuration for dynamic context loading
- **Essential rules template** - Starting point for user customization

### Updated Content
- **Principles**: Full set of 37 principles (was 20)
- **Rules**: New `essential_rules.yaml` template
- **Documentation**: Refreshed README, STATUS, and guides

## 📊 Package Contents

```
Total files:     137
├── Scripts:      22
├── Personas:      8  (Operator, Builder, Strategist, Researcher, Writer, Teacher, Architect, Debugger)
├── Principles:   39  (P01-P37 + index + decision matrix)
├── Prompts:      15
├── System docs:  10
├── Config files:  4
└── Examples:      4
```

## 🚀 Installation

```bash
# Extract
tar -xzf n5os-lite-v2.0.0.tar.gz -C /home/workspace/

# Setup
cd /home/workspace/n5os-lite
./setup.sh

# Optional: Run onboarding
python3 scripts/onboarding_wizard.py
```

## 📋 Post-Installation

1. **Set up personas** in your AI platform (Zo Settings → Your AI → Personas)
2. **Customize rules** in `rules/essential_rules.yaml`
3. **Review principles** in `principles/` and disable any that don't fit your workflow

## ⚠️ Known Limitations

- Personas require manual setup in Zo (copy YAML content into persona prompts)
- Some script paths assume `/home/workspace/N5/` structure
- Advanced integrations (Gmail, Calendar) not included

## 🔮 Future Roadmap

- [ ] Automated persona installation script
- [ ] Integration templates
- [ ] GitHub Actions for CI/CD
- [ ] More workflow prompts

---

**Built from:** V's N5 system, December 2025
**Privacy status:** ✅ Clean - No PII

