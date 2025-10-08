# Personal Prompts Library

**Purpose**: Your reusable prompt infrastructure - custom prompts callable via Incantum or direct invocation.

---

## Overview

This is your **personal prompt library** - sophisticated prompts you've developed for various tasks. They're essentially like N5 commands but more focused on specific workflows.

**Key Difference from N5 Commands**:
- **N5 Commands**: System operations (lists-add, knowledge-ingest, etc.)
- **Personal Prompts**: Task-specific workflows (research, marketing, interviews, etc.)

**Both are callable via Incantum** - just say what you need!

---

## Current Prompts

### Research & Intelligence
1. **Deep Research Due Diligence v0.3**
   - Two-part research dossier on target entities
   - For partnership/GTM/fundraising strategy
   - Trigger: "Run deep research on [company/person]"

2. **PR - Intel - Extractor v1.1**
   - Extract intelligence from PR materials
   - Trigger: "Extract PR intel from [document]"

3. **Stakeholder Pain Point Extractor v1.0**
   - Identify and analyze stakeholder pain points
   - Trigger: "Extract pain points from [interview/document]"

4. **Stakeholder Q&A Extractor And Analyzer v1.0**
   - Process stakeholder interviews
   - Trigger: "Analyze stakeholder Q&A from [transcript]"

### Product & Marketing
5. **B2C Marketing And Sales Collateral Generator v1.0**
   - Generate marketing materials for job seekers
   - Trigger: "Generate B2C marketing collateral"

6. **Follow - Up Email Generator v10.6**
   - Context-aware follow-up emails
   - Trigger: "Generate follow-up email for [person/context]"

### Job Analysis
7. **JTBD Plus Interview Extractor v1.0**
   - Jobs-to-be-Done analysis from interviews
   - Trigger: "Extract JTBD from [interview]"

---

## Companion Files (Context)

These provide context/voice for prompts:

1. **Intellectual Priority Ontology v1.0**
   - Framework for prioritizing intellectual work
   
2. **Essential Links v1.6**
   - Key resources and references

3. **Master Voice Vrijen v1.3**
   - Your communication voice/style

4. **Universal Nuance Manifest v1.0**
   - Nuanced guidelines for AI behavior

---

## Usage Patterns

### Direct Invocation
```
V: "Run deep research on Sequoia Capital"
Zo: [Loads Function [01], executes research workflow]
```

### Natural Language (Incantum)
```
V: "I need to analyze this stakeholder interview"
Zo: [Maps to Stakeholder Q&A Extractor, processes]
```

### Explicit Call
```
V: "Use the Follow-Up Email Generator for this contact"
Zo: [Loads Function [02], generates email]
```

---

## Integration with N5

### Option 1: Incantum Triggers (Recommended)
- Add these prompts to `N5/config/incantum_triggers.json`
- Map natural language to prompt files
- Example: "deep research" → Function [01]

### Option 2: N5 Commands Wrapper
- Create N5 commands that load these prompts
- Example: `N5/commands/research-deep.md` → loads Function [01]
- Benefit: Consistent with N5 architecture

### Option 3: Hybrid
- Keep prompts in Personal/Prompts/ (portable)
- Reference from N5 commands when needed
- Best of both worlds

---

## Proposed Structure

### Current (Flat)
```
Personal/Prompts/
├── Function [01] - Deep Research...
├── Function [01] - B2C Marketing...
├── Function [02] - Follow-Up Email...
├── Companion [01] - Intellectual Priority...
└── README.md
```

### Proposed (Organized)
```
Personal/Prompts/
├── Research/
│   ├── deep-research-due-diligence.txt
│   ├── pr-intel-extractor.txt
│   └── stakeholder-pain-point-extractor.txt
├── Marketing/
│   ├── b2c-collateral-generator.pdf
│   └── follow-up-email-generator.txt
├── Analysis/
│   ├── jtbd-interview-extractor.pdf
│   └── stakeholder-qa-analyzer.pdf
├── Context/
│   ├── intellectual-priority-ontology.txt
│   ├── essential-links.txt
│   ├── master-voice-vrijen.txt
│   └── universal-nuance-manifest.txt
└── README.md
```

---

## Next Steps (Your Decision)

1. **Keep flat** - Works fine, easy to find
2. **Reorganize by category** - Better organization, scales better
3. **Integrate with N5 commands** - Create command wrappers
4. **Register with Incantum** - Add natural language triggers

**My Recommendation**: 
- Keep flat for now (only 11 files)
- Register top 3-5 most-used prompts with Incantum
- Create N5 command wrappers as needed

---

## Maintenance

### Adding New Prompts
1. Create prompt file in Personal/Prompts/
2. Add to this README
3. (Optional) Register with Incantum
4. (Optional) Create N5 command wrapper

### Versioning
- Prompts are versioned (v0.3, v1.0, etc.)
- Keep old versions in Archive/ when updating
- Document changes in prompt file itself

---

*Your personal prompt library - part of your cognitive infrastructure*
