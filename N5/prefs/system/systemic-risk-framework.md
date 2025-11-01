# Systemic Risk Scoring Framework

**Purpose:** Assess downstream impact of file operations to prevent cascading failures  
**Version:** 1.0 | **Created:** 2025-10-31  
**Used by:** Vibe Operator, Vibe Builder

---

## Overview

Calculate systemic risk score (0-20) across 5 dimensions before destructive operations.

**Dimensions:**
1. Dependency Depth (0-4) - How many files reference this?
2. Schema Impact (0-4) - Does this violate expected structure?
3. Cross-Persona Impact (0-4) - Which personas rely on this?
4. Recovery Cost (0-4) - How expensive to fix if breaks?
5. Blast Radius (0-4) - Direct + indirect systems touched

**Thresholds:**
- 0-5: LOW (proceed)
- 6-11: MEDIUM (dry-run + confirm)
- 12-16: HIGH (backup + mitigation plan)
- 17-20: CRITICAL (multi-step process required)

---

## Scoring Criteria

### Dimension 1: Dependency Depth
- 0 references: 0 pts
- 1-2 references: 1 pt
- 3-5 references: 2 pts
- 6-10 references: 3 pts
- 11+ references: 4 pts

### Dimension 2: Schema Impact
- Not in any schema: 0 pts
- In folder-policy.md: 1 pt
- In naming-conventions.md: 2 pts
- In index.schema.json: 3 pts
- Multiple schema references: 4 pts

### Dimension 3: Cross-Persona Impact
- 0 personas: 0 pts
- 1 persona: 1 pt
- 2-3 personas: 2 pts
- 4-5 personas: 3 pts
- All/most personas: 4 pts

### Dimension 4: Recovery Cost
- No downstream updates: 0 pts
- Update 1-2 config files: 1 pt
- Update 3-5 files OR 1 workflow: 2 pts
- Update 6+ files OR multiple workflows: 3 pts
- Update personas + workflows + schemas: 4 pts

### Dimension 5: Blast Radius
- 0-2 total touches: 0 pts
- 3-5 touches: 1 pt
- 6-10 touches: 2 pts
- 11-20 touches: 3 pts
- 21+ touches: 4 pts

---

## Usage

python3 /home/workspace/N5/scripts/systemic_risk.py <operation> <target_path>

Output example:
  Operation: move example.py -> Archive/
  TOTAL RISK: 13/20 (HIGH)
  Safeguards: backup + update dependencies first

---

## Special Cases

Protected paths: +4 to score if n5_protect.py blocks
Bulk operations: score highest + 1 per additional 5 files
Cross-system: +2 if touches both N5/ and workspace/

---

## Integration

Operator should:
1. Call systemic_risk.py before destructive ops
2. Report score + breakdown
3. Apply safeguards per threshold
4. Log to audit trail

---

*Location: /home/workspace/N5/prefs/system/systemic-risk-framework.md*  
*Script: /home/workspace/N5/scripts/systemic_risk.py*
