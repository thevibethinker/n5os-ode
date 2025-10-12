# Phase 3 Implementation Plan - AAR System v2.0

**Goal:** Transform AAR system from manual/dummy to intelligent and progressive

---

## Feature 1: Progressive Documentation (Checkpoint System)

### Concept
Allow mid-conversation AAR checkpoints for long threads, enabling:
- Save progress without closing thread
- Build AAR incrementally as work progresses
- Preview current state anytime
- Merge checkpoint data into final AAR

### Implementation

#### New Flags
- `--checkpoint`: Save draft AAR (doesn't finalize)
- `--preview`: Show current AAR without saving
- `--merge-checkpoint`: Load existing checkpoint when creating final AAR

#### File Structure
```
N5/logs/threads/
└── {thread-id}-{title}/
    ├── checkpoint-YYYY-MM-DD-HHMMSS.json  # Progressive drafts
    ├── aar-YYYY-MM-DD.json                # Final AAR
    └── aar-YYYY-MM-DD.md                  # Final markdown
```

#### New Methods
- `save_checkpoint()`: Save draft without finalizing
- `load_checkpoint()`: Load most recent checkpoint
- `merge_checkpoints()`: Combine checkpoint data with current session
- `list_checkpoints()`: Show available checkpoints

#### Workflow
```python
# Mid-conversation checkpoint
python3 n5_thread_export.py --auto --checkpoint --title "Progress Update"

# Preview without saving
python3 n5_thread_export.py --auto --preview

# Final export (merges checkpoints)
python3 n5_thread_export.py --auto --merge-checkpoint
```

---

## Feature 2: Automatic Content Extraction

### Concept
Intelligently extract AAR content from artifacts instead of dummy data

### Extraction Strategy

#### A. Filename Analysis
Extract clues from artifact names:
- `implementation-*.md` → Implementation project
- `research-*.md` → Research session
- `bug-fix-*.py` → Bug fix
- `analysis-*.json` → Data analysis

#### B. Content Pattern Matching
Analyze file content for:
- **Markdown headers**: Extract objectives from H1/H2
- **Code comments**: Find TODO, FIXME, DECISION markers
- **JSON data**: Look for metadata sections
- **Git-style commit messages**: Extract decision context

#### C. Heuristic Rules
```python
# Example heuristics
if len(scripts) > 3:
    type = "implementation"
elif len(documents) > len(scripts):
    type = "research"
elif "test" in filenames:
    type = "testing"
```

#### D. Artifact Clustering
Group artifacts by:
- Creation time (what was worked on together)
- File type (scripts vs docs vs data)
- Name patterns (common prefixes/suffixes)

### New Methods
- `extract_objective_from_artifacts()`: Infer conversation purpose
- `detect_conversation_type()`: Classify conversation
- `extract_key_decisions()`: Find decision points in content
- `generate_smart_summary()`: Create intelligent outcome description
- `infer_next_steps()`: Predict logical next actions

### Smart AAR Generation Flow
```python
def generate_smart_aar(self):
    # 1. Classify conversation type
    conv_type = self.detect_conversation_type()
    
    # 2. Extract objective
    objective = self.extract_objective_from_artifacts()
    
    # 3. Identify key decisions
    decisions = self.extract_key_decisions()
    
    # 4. Generate summary
    outcomes = self.generate_smart_summary()
    
    # 5. Infer next steps
    next_steps = self.infer_next_steps(conv_type)
    
    return self.generate_aar_data({
        'objective': objective,
        'decisions': decisions,
        'outcomes': outcomes,
        'next_objective': next_steps[0] if next_steps else 'Continue work',
        'challenges': ''
    })
```

---

## Feature 3: AAR Templates

### Concept
Different conversation types need different AAR formats and emphasis

### Template Types

#### A. Implementation Template
Focus: Technical details, decisions, architecture
```json
{
  "template": "implementation",
  "sections": {
    "architecture_decisions": [...],
    "technologies_used": [...],
    "integration_points": [...],
    "testing_strategy": "..."
  }
}
```

#### B. Research Template
Focus: Findings, sources, insights
```json
{
  "template": "research",
  "sections": {
    "research_questions": [...],
    "key_findings": [...],
    "sources": [...],
    "open_questions": [...]
  }
}
```

#### C. Strategy Template
Focus: Decisions, tradeoffs, rationale
```json
{
  "template": "strategy",
  "sections": {
    "decision_framework": "...",
    "options_considered": [...],
    "tradeoffs": [...],
    "selected_approach": "..."
  }
}
```

#### D. Bug Fix Template
Focus: Problem, root cause, solution
```json
{
  "template": "bugfix",
  "sections": {
    "problem_description": "...",
    "root_cause": "...",
    "solution_implemented": "...",
    "prevention_measures": [...]
  }
}
```

### Template Detection
```python
def detect_template(self):
    artifacts = self.artifacts
    
    # Implementation indicators
    if self._has_multiple_scripts() and self._has_architecture_docs():
        return "implementation"
    
    # Research indicators
    if self._has_many_documents() and self._has_external_refs():
        return "research"
    
    # Bug fix indicators
    if "bug" in self.title.lower() or "fix" in self.title.lower():
        return "bugfix"
    
    # Default
    return "general"
```

---

## Feature 4: Enhanced Schema (Optional)

### Extended AAR Schema
Support template-specific fields:
```json
{
  "aar_version": "2.1",
  "template": "implementation",
  "extended_fields": {
    // Template-specific structured data
  }
}
```

---

## Implementation Priority

### Phase 3A (High Priority - Implement First)
1. ✅ Automatic Content Extraction - Core methods
2. ✅ Smart AAR generation (replaces dummy data)
3. ✅ Checkpoint system basics

### Phase 3B (Medium Priority)
4. Template detection
5. Template-specific markdown generation
6. Enhanced schema support

### Phase 3C (Future Enhancement)
7. Cross-thread linking
8. ML-based content extraction
9. Visual AAR dashboard

---

## Testing Strategy

### Test Cases

**Test 1: Progressive Checkpoint**
```bash
# Create checkpoint mid-conversation
python3 n5_thread_export.py --auto --checkpoint --title "Midpoint"

# Preview current state
python3 n5_thread_export.py --auto --preview

# Final export with merge
python3 n5_thread_export.py --auto --merge-checkpoint
```

**Test 2: Smart Extraction**
```bash
# Create test artifacts with obvious patterns
# Run with smart extraction
python3 n5_thread_export.py --auto --yes
# Verify AAR has intelligent content (not dummy data)
```

**Test 3: Template Detection**
```bash
# Implementation project (multiple scripts)
# Research project (multiple docs)
# Bug fix (bug in title)
# Verify correct template selected
```

---

## Success Criteria

✅ **Checkpoint System**
- [ ] Can save mid-conversation drafts
- [ ] Can preview without saving
- [ ] Final AAR merges checkpoint data
- [ ] Checkpoints don't interfere with final export

✅ **Smart Extraction**
- [ ] Objective extracted from artifacts (not dummy)
- [ ] Key decisions identified in content
- [ ] Summary reflects actual work done
- [ ] Next steps are contextually relevant

✅ **Templates**
- [ ] Conversation type detected accurately
- [ ] Template-specific sections populated
- [ ] Markdown generation respects template

✅ **Backward Compatibility**
- [ ] All Phase 2 functionality still works
- [ ] Interactive mode unchanged
- [ ] Automated mode enhanced but not broken
