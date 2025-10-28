# Action Items for Main System

**Thread**: con_HuaTrPlhVJRg9c9m  
**Date**: 2025-10-28 00:13 ET

---

## 1. Remove "Rule of Two" from Main System

**Status**: ⏳ Pending

**What**: Remove the P0/Rule-of-Two principle that limits context loading to 2 files

**Where to patch**:
- file 'Knowledge/architectural/principles/P0-rule-of-two.md' (if exists)
- file 'Knowledge/architectural/architectural_principles.md' (index - remove P0 reference)
- file 'Documents/Vibe-Builder-Persona.md' (remove Rule-of-Two mentions)
- Any other references in prefs or principles

**Reason**: Arbitrary limit causes more harm than good; monitor for actual issues instead

**Test**: After removal, verify Vibe Builder persona still loads correctly and operates without references to Rule of Two

---

## 2. Future: Apply Config Template System to Main

**Status**: 🔮 Future (after Demonstrator stable)

**What**: Backport the templates/ vs config/ pattern to Main system

**Why**: Would solve update issues on Main as well

**When**: After Phase 0 complete on Demonstrator and pattern proven

---

*Created: 2025-10-28 00:13 ET*
