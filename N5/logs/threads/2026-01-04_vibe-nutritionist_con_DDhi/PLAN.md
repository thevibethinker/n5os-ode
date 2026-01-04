---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.1
type: build_plan
status: in_progress
provenance: con_DDhidFgCJ5Rzs4wC
---

# Plan: Vibe Nutritionist Persona

**Objective:** Develop and integrate a specialized "Vibe Nutritionist" persona into N5OS, capable of providing evidence-backed supplementation and health advice by triangulating genetic data, lab results, and subjective bio-logs.

**Trigger:** V requested a persona grounded in his specific vitals and genetic information.

**Key Design Principle:** Triangulation-based logic. Never recommend based on one data point. Genetic potential must be validated by Labs, and Lab markers must be correlated with BioLog symptoms before intervention.

---

## Open Questions

- [ ] Does V want the persona to proactively flag issues (Agent mode) or only respond to queries (Interactive mode)? (Default: Interactive first, with instructions for periodic "Health Checks").
- [ ] Should the persona have authority to update `Knowledge/bio-context/foundations/current_supplements.md` directly or only propose changes? (Default: Propose via Markdown block for V approval).

---

## Checklist

### Phase 1: Persona Definition & Workflow
- ☑ Create `N5/prefs/workflows/nutritionist_workflow.md` codifying the Triangulation Logic.
- ☑ Create Persona Brief for system registration.
- ☑ Test: Run a manual "triangulation" mock-up to verify logic flow.

### Phase 2: System Integration & Registration
- ☑ Register persona via `create_persona` API.
- ☑ Update `N5/prefs/system/persona_routing_contract.md` with handoff triggers.
- ☑ Add "Nutritionist" to persona selection guides.
- ☐ Test: Switch to persona and ask for a supplement review.

### Phase 3: Remediation & Enhancement (Debugger Findings)
- ☑ Fix bio_snapshots path specification in workflow and persona
- ☑ Properly integrate routing contract entry (not append)
- ☑ Add bidirectional handoff ID to Vibe Trainer persona
- ☑ Operationalize Stack Budget with actual counting logic
- ☑ (Enhancement) Add supplement interaction awareness
- ☑ (Enhancement) Add temporal/timing guidance capability
- ☑ (Enhancement) Document meal pairing logic

---

## Phases

### Phase 0: Signal Hierarchy & Protocol Design (Architectural Foundation)
- [ ] Define **Hierarchy of Truth**: Labs (Verdict) > Genetics (Boundaries) > BioLogs (Subjective Tuning).
- [ ] Implement **Stack Auditor Mandate**: Persona defaults to "No change" or "Removal" unless evidence is overwhelming. Max stack budget (default 10).
- [ ] Define **Signal Decay Protocol**: If BioLogs contradict Genetics for >14 days, the Genetic signal is deprecated for that marker until a new Lab is provided.

### Phase 1: Persona Core Prompt Design
- [ ] Draft `Vibe Nutritionist` prompt focusing on "Evidence-Grounded Observation" rather than "Prescription".

---

## Phase 1: Persona Definition & Workflow

### Affected Files
- `N5/prefs/workflows/nutritionist_workflow.md` - CREATE - The "Brain" of the nutritionist.
- `N5/builds/vibe-nutritionist/persona_brief.md` - CREATE - Definition for API registration.

### Changes

**1.1 Nutritionist Workflow:**
Define the "Grounding Protocol":
1. **Genetic Baseline:** Read `Personal/Health/V_GENETIC_PROFILE.md` for predispositions (e.g., COMT, MTHFR, Caffeine metabolism).
2. **Current State (Labs):** Cross-reference with `Personal/Health/labs/` (latest LabCorp).
3. **Subjective Validation:** Search `bio_snapshots` or `COACHING_NOTES.md` for correlated symptoms.
4. **Intervention Design:** Propose supplement or behavioral change with dose/rationale/test period.

**1.2 Persona Brief:**
Design the prompt to be concise but authoritative. Emphasis on "Clinical but Vibes-aligned." High standards for intellectual honesty—must flag when data is missing or contradictory.

### Unit Tests
- Rationale check: Provide a genetic predisposition (e.g., High COMT) and check if it correctly looks for Labs (Magnesium, B12) and BioLog (Anxiety/Stress) before recommending.

---

## Phase 2: System Integration & Registration

### Affected Files
- `N5/prefs/system/persona_routing_contract.md` - UPDATE - Add handoff logic.
- `Documents/System/PERSONAS_README.md` - UPDATE - Document new capability.

### Changes

**2.1 Persona Registration:**
Call `create_persona` with the designed prompt and name "Vibe Nutritionist".

**2.2 Routing Integration:**
Add triggers:
- From Trainer: "If diet or recovery is the bottleneck → Nutritionist"
- From Strategist: "If energy/focus is the bottleneck → Nutritionist"

### Unit Tests
- Switching test: `set_active_persona` to Vibe Nutritionist and verify identity.
- Integration test: Ask Vibe Trainer about poor recovery and see if it suggests the Nutritionist.

---

## Phase 3: Remediation & Enhancement

**Source:** Debugger QA Report (con_DDhidFgCJ5Rzs4wC)

### 3.1 Bug Fixes (Required)

#### 3.1.1 bio_snapshots Path Specification
**Affected Files:**
- `N5/prefs/workflows/nutritionist_workflow.md` - UPDATE
- `N5/builds/vibe-nutritionist/persona_brief.md` - UPDATE (reference only)
- Vibe Nutritionist persona prompt - UPDATE via `edit_persona`

**Changes:**
- Add explicit path: `N5/data/journal.db` table `bio_snapshots`
- Add SQL example for querying recent entries
- Document schema: `mood_text`, `mood_score`, `energy_level`, `raw_message`, `created_at`

#### 3.1.2 Routing Contract Integration
**Affected Files:**
- `N5/prefs/system/persona_routing_contract.md` - UPDATE

**Changes:**
- Move Nutritionist entry from end-of-file to proper "Health & Wellness" section
- Create section if it doesn't exist, grouping with Vibe Trainer
- Remove trailing whitespace

#### 3.1.3 Bidirectional Handoff (Trainer → Nutritionist)
**Affected Files:**
- Vibe Trainer persona prompt - UPDATE via `edit_persona`

**Changes:**
- Add explicit handoff instruction: `set_active_persona("f25038f1-114c-4f77-8bd2-40f1ed07182d")`
- Clarify trigger: "When diet, supplementation, or metabolic recovery is the blocker"

#### 3.1.4 Stack Budget Operationalization
**Affected Files:**
- `N5/prefs/workflows/nutritionist_workflow.md` - UPDATE
- Vibe Nutritionist persona prompt - UPDATE via `edit_persona`

**Changes:**
- Stack Budget = count of items in `Personal/Health/stack/current_supplements.yaml`
- Add instruction: "Read current_supplements.yaml and count active items"
- Format: "Stack Budget: X/10 (from current_supplements.yaml)"

### 3.2 Enhancements (Optional, High-Value)

#### 3.2.1 Supplement Interaction Awareness
**Design Decision:** Simple heuristic list, not full drug interaction database.

**Changes:**
- Add `Personal/Health/stack/interaction_notes.md` with known interactions V should watch for
- Persona prompt: "Check interaction_notes.md before recommending additions"

#### 3.2.2 Temporal/Timing Guidance
**Design Decision:** Add timing context to current_supplements.yaml schema.

**Changes:**
- Each supplement entry can have `timing: [morning|afternoon|evening|with_food|empty_stomach]`
- Persona: "When recommending, include optimal timing based on mechanism"

#### 3.2.3 Meal Pairing Logic
**Design Decision:** Simple annotation, not complex rules engine.

**Changes:**
- Add `requires_food: true/false` to supplement entries
- Persona: "Flag supplements that need food pairing"

### Unit Tests
- Query bio_snapshots successfully using documented path
- Routing contract grep shows Nutritionist in proper section
- Trainer persona includes Nutritionist handoff ID
- Stack Budget correctly reports count from current_supplements.yaml

---

## Success Criteria
- [ ] Persona can identify a conflict between Genetics and Labs and correctly defer to Labs (Verdict).
- [ ] Persona identifies "Stack Creep" and recommends removal of redundant supplements.
- [ ] Persona uses `Personal/Health/` citations for every recommendation.
- [ ] Response includes "Stack Budget" status (e.g., "7/10 slots filled").

---

## Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| **Stack Creep** | Mandatory "Stack Auditor" mindset; limit additions; prioritize removals. |
| **Complecting Signals** | **Strict Veto Hierarchy** (Labs > Genetics). |
| Medical Misinformation | Standard disclaimer + grounding in personal file ONLY. |

---

## Level Upper Review

### Counterintuitive Suggestions Incorporated:
1. **The Veto Power Hierarchy**: Labs = Verdict, Genetics = Boundary, BioLogs = Optimization. Prevents "clever" but wrong triangulation.
2. **Stack Auditor Mindate**: Shift from "Stack Builder" to "Stack Auditor". Prioritize negative space (not adding noise).
3. **Signal Decay**: Handle conflicting signals by deprecating static (Genetic) data in favor of dynamic (BioLog) data until Lab validation is possible.

---




