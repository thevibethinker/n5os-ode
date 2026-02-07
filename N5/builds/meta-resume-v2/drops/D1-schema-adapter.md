---
created: 2026-02-03
last_edited: 2026-02-03
version: 1.0
provenance: con_NJlvnFnzUY6KsX9t
build_slug: meta-resume-v2
drop_id: D1
drop_title: Schema Adapter
spawn_mode: auto
---

# Drop 1: Schema Adapter

## Context

The `meta-resume-generator` skill currently takes hand-crafted JSON files as input. We need it to consume the structured outputs from `careerspan-decomposer` directly.

The decomposer outputs live at:
```
Careerspan/meta-resumes/inbox/<candidate>-<company>/
├── scores_complete.json   # Main assessment data
├── overview.yaml          # Overall score, verdict, recommendation
├── jd.yaml               # Job description details
├── profile.yaml          # Candidate profile info
└── manifest.yaml         # Processing metadata
```

## Scope

### Files to CREATE:
- `Skills/meta-resume-generator/scripts/adapter.ts`

### Files to MODIFY:
- `Skills/meta-resume-generator/scripts/generate-decoded.ts` (CLI interface + imports)
- `Skills/meta-resume-generator/SKILL.md` (update usage docs)

### Files to READ (for reference):
- `Skills/careerspan-decomposer/assets/canonical_schema.json` (decomposer schema)
- `Careerspan/meta-resumes/inbox/hardik-flowfuse/` (sample data)
- `Skills/meta-resume-generator/scripts/hardik-decoded.json` (current input format)

### Must NOT touch:
- `template-decoded.html` (that's Drop 2)
- Any CSS or visual styling
- Section ordering

## MUST DO

1. **Create `adapter.ts`** with these exports:
   ```typescript
   export interface DecomposerInput {
     scoresComplete: ScoresComplete;
     overview: Overview;
     jd: JobDescription;
     profile: CandidateProfile;
   }
   
   export async function loadDecomposerOutput(dirPath: string): Promise<DecomposerInput>
   export function mapToCandidateDecoded(input: DecomposerInput): CandidateDecodedData
   export function extractSpikes(skills: Skill[]): { upSpikes: Spike[], downSpikes: Spike[] }
   ```

2. **Field mappings** (implement these exactly):
   | Decomposer Field | Generator Field |
   |-----------------|-----------------|
   | `overview.yaml → careerspan_score.overall` | `confidenceScore` |
   | `overview.yaml → recommendation.verdict` | `verdictText` |
   | `overview.yaml → recommendation.summary` | `verdictSummary` |
   | `scores_complete.json → overall_score` | Fallback for confidenceScore |
   | `scores_complete.json → signal_strength` | `signalStrength` |
   | `jd.yaml → title` or `position` | `candidateRole` |
   | `profile.yaml → candidate.name` or `overview.yaml → candidate.name` | `candidateName` |

3. **Spike extraction logic**:
   ```typescript
   function extractSpikes(skills: Skill[]): { upSpikes: Spike[], downSpikes: Spike[] } {
     // Upward spikes: rating = "Excellent", sorted by importance DESC, take top 5
     const upSpikes = skills
       .filter(s => s.rating === "Excellent")
       .sort((a, b) => (b.importance || 0) - (a.importance || 0))
       .slice(0, 5)
       .map(s => ({
         label: truncateToWords(s.skill_name, 5),
         evidenceType: s.evidence_type,
         importance: s.importance
       }));
     
     // Downward spikes: rating in ["Gap", "Fair"], sorted by importance DESC, take top 3
     const downSpikes = skills
       .filter(s => s.rating === "Gap" || s.rating === "Fair")
       .sort((a, b) => (b.importance || 0) - (a.importance || 0))
       .slice(0, 3)
       .map(s => ({
         label: truncateToWords(s.skill_name, 5),
         evidenceType: s.evidence_type,
         importance: s.importance
       }));
     
     return { upSpikes, downSpikes };
   }
   ```

4. **Update `generate-decoded.ts` CLI**:
   - Accept directory path OR JSON file as first argument
   - If directory: use adapter to load and map
   - If JSON file: use existing logic (backward compatible)
   - Detection: check if path ends with `.json` or is a directory

5. **Update `SKILL.md`** with new usage:
   ```bash
   # NEW: Generate from decomposer output directory
   bun run generate-decoded.ts /path/to/candidate-company/
   
   # LEGACY: Generate from JSON file (still works)
   bun run generate-decoded.ts input.json
   ```

6. **Add YAML parsing** - install `yaml` package if not present:
   ```bash
   cd Skills/meta-resume-generator/scripts && bun add yaml
   ```

## MUST NOT DO

- Do NOT modify `template-decoded.html`
- Do NOT change any CSS or visual styling
- Do NOT reorder sections in the template
- Do NOT change the PDF generation logic
- Do NOT modify the Handlebars template rendering

## Expected Output

After this drop:
```bash
cd Skills/meta-resume-generator/scripts
bun run generate-decoded.ts /home/workspace/Careerspan/meta-resumes/inbox/hardik-flowfuse/
# Should produce: ../output/hardik-decoded.pdf
```

The output should be visually identical to the current output (same sections, same order) but populated from decomposer data.

## Validation

1. Run against hardik-flowfuse directory
2. PDF generates without errors
3. All fields populated (no undefined/null in visible content)
4. `upSpikes` and `downSpikes` arrays populated in data object
5. Backward compatibility: JSON file input still works

## Deposit Location

Write your deposit to: `N5/builds/meta-resume-v2/deposits/D1-deposit.md`

Include:
- Files created/modified
- Any deviations from spec (with rationale)
- Test results
- Blockers encountered (if any)
