---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
type: build_plan
status: complete
provenance: con_jfdmQM1xwEi3Gcta
---

# Plan: MemeBench - AI Cultural Zeitgeist Benchmark

**Objective:** Build a benchmark framework that tests AI models' ability to interpret meme culture—layered irony, cultural references, temporal context, and sociological subtext.

**Trigger:** V's pilot project to learn benchmark construction before tackling GestaltBench.

**Key Design Principle:** Keep it simple. This is a learning project. Framework and categories first, data collection later.

---

## Open Questions

<!-- All resolved through design decisions below -->
- [x] Scoring approach? → Multi-dimensional rubric (5 dimensions, 1-5 scale each)
- [x] Data format? → YAML for questions, JSONL for results (LLM-friendly)
- [x] How to test without real memes? → Synthetic/hypothetical meme descriptions in Phase 1

---

## Checklist

### Phase 1: Framework & Categories
- ☑ Create `Projects/memebench/` directory structure
- ☑ Write README.md with project overview
- ☑ Define 6 benchmark categories in `categories/`
- ☑ Create scoring rubric in `scoring/rubric.yaml`
- ☑ Test: Directory structure verified, all files readable

### Phase 2: Evaluation Harness Scaffold
- ☑ Create `src/evaluate.py` CLI skeleton
- ☑ Create `src/models.py` model interface
- ☑ Create sample question format in `data/sample.yaml`
- ☑ Test: `python src/evaluate.py --help` runs without error

---

## Nemawashi: Alternatives Considered

### Alt 1: JSON-Schema Strict Format
- **Pros:** Type-safe, machine-parseable
- **Cons:** Harder for LLMs to generate, brittle to small errors
- **Verdict:** Rejected—too rigid for pilot

### Alt 2: Free-Form Markdown Questions
- **Pros:** Easy to write, human-readable
- **Cons:** No structure for automated scoring
- **Verdict:** Rejected—can't automate evaluation

### Alt 3: YAML Questions + JSONL Results ✓ SELECTED
- **Pros:** YAML is LLM-friendly for authoring, JSONL is append-only for results
- **Cons:** Two formats to maintain
- **Verdict:** Selected—sweet spot of flexibility and structure

---

## Trap Doors Identified

| Decision | Cost to Reverse | Notes |
|----------|-----------------|-------|
| YAML for questions | 2-4 hours | Migration script if needed |
| Scoring dimensions (5) | 4-8 hours | Would require re-scoring all data |
| Directory structure | 2-4 hours | Standard, low risk |

**Assessment:** No high-cost trap doors in Phase 1-2. All decisions reversible with modest effort.

---

## Phase 1: Framework & Categories

### Affected Files
- `Projects/memebench/` - CREATE - root directory
- `Projects/memebench/README.md` - CREATE - project overview
- `Projects/memebench/categories/` - CREATE - category definitions directory
- `Projects/memebench/categories/01_absurdist_meta_irony.md` - CREATE - category def
- `Projects/memebench/categories/02_corporate_cringe.md` - CREATE - category def
- `Projects/memebench/categories/03_generational_trauma.md` - CREATE - category def
- `Projects/memebench/categories/04_political_subtext.md` - CREATE - category def
- `Projects/memebench/categories/05_internet_archaeology.md` - CREATE - category def
- `Projects/memebench/categories/06_format_literacy.md` - CREATE - category def
- `Projects/memebench/scoring/` - CREATE - scoring directory
- `Projects/memebench/scoring/rubric.yaml` - CREATE - scoring dimensions

### Changes

**1.1 Directory Structure:**
```
Projects/memebench/
├── README.md
├── categories/
│   ├── 01_absurdist_meta_irony.md
│   ├── 02_corporate_cringe.md
│   ├── 03_generational_trauma.md
│   ├── 04_political_subtext.md
│   ├── 05_internet_archaeology.md
│   └── 06_format_literacy.md
├── scoring/
│   └── rubric.yaml
├── data/
│   └── .gitkeep
└── src/
    └── .gitkeep
```

**1.2 README.md Content:**
- Project name and one-line description
- What MemeBench tests (zeitgeist fluency, not image recognition)
- Category overview (6 categories)
- Scoring approach (5 dimensions)
- Status: Framework only, no data yet

**1.3 Category Definitions:**
Each category file contains:
- Name and description
- What it tests (specific cultural competency)
- Example meme patterns (described, not actual images)
- Difficulty spectrum (easy → hard examples)
- Scoring notes specific to category

**1.4 Scoring Rubric:**
YAML file with 5 scoring dimensions:
1. **Cultural Reference Recognition** (1-5): Does model identify the referenced cultural artifact?
2. **Irony Detection** (1-5): Does model recognize layers of irony/sincerity?
3. **Temporal Context** (1-5): Does model understand when this meme is from?
4. **Sociological Subtext** (1-5): Does model get the underlying social commentary?
5. **Format Appropriateness** (1-5): Does model understand why this format was chosen?

### Unit Tests
- `ls Projects/memebench/categories/ | wc -l` returns 6
- `cat Projects/memebench/scoring/rubric.yaml` is valid YAML
- All markdown files have frontmatter with created/version

---

## Phase 2: Evaluation Harness Scaffold

### Affected Files
- `Projects/memebench/src/evaluate.py` - CREATE - main CLI
- `Projects/memebench/src/models.py` - CREATE - model interface
- `Projects/memebench/data/sample.yaml` - CREATE - example question

### Changes

**2.1 evaluate.py:**
- CLI using argparse
- `--input` flag for question file (YAML)
- `--model` flag for model selection (stub)
- `--output` flag for results file (JSONL)
- `--dry-run` flag to validate without running
- Main logic is placeholder—prints "Evaluation harness ready"

**2.2 models.py:**
- Abstract base class `ModelInterface`
- Stub implementation `MockModel` that returns random scores
- Function `get_model(name: str) -> ModelInterface`
- Designed for future OpenAI/Anthropic/local model integration

**2.3 sample.yaml:**
```yaml
# Sample question format
- id: sample_001
  category: absurdist_meta_irony
  description: |
    A meme showing a person staring at a butterfly, 
    captioned "Is this [mundane thing]?" applied to 
    an absurdly inappropriate context.
  question: |
    Explain why this meme format works for this application.
    What layers of irony are present?
  expected_signals:
    - references "Is This a Pigeon?" anime scene
    - recognizes deliberate misapplication
    - understands meta-commentary on categorization
```

### Unit Tests
- `python Projects/memebench/src/evaluate.py --help` exits 0
- `python -c "from src.models import get_model; print(get_model('mock'))"` works
- `python -c "import yaml; yaml.safe_load(open('data/sample.yaml'))"` parses

---

## Success Criteria

1. **Directory exists:** `Projects/memebench/` with complete structure
2. **Documentation complete:** README explains project, categories are defined
3. **Rubric defined:** `scoring/rubric.yaml` has 5 dimensions with 1-5 scales
4. **CLI works:** `python src/evaluate.py --help` runs without error
5. **Sample question:** At least one valid sample question in `data/sample.yaml`
6. **No over-engineering:** No actual model integration, no data collection, no complex infrastructure

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Scope creep into data collection | Hard constraint: Phase 1-2 only |
| Over-engineering scoring system | Keep to 5 simple dimensions |
| Categories too academic | Include concrete meme examples (described) |
| Framework without validation | Sample question proves format works |

---

## Level Upper Review

*Skipped for this build—straightforward scaffold, no architectural ambiguity requiring divergent thinking.*

---

## Handoff Notes for Builder

**Execute Phase 1 first, then Phase 2.**

Phase 1 is pure file creation—no code execution needed.
Phase 2 creates minimal Python scaffolds—test with `--help` flags.

Keep it simple. This is a learning project.



