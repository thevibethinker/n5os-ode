# N5 OS Core - Onboarding System Design

**Date**: 2025-10-28 03:58 ET  
**Status**: Worker Assigned  
**Priority**: High (foundational for v1.0)

---

## Why Onboarding Matters

**Problem**: Users clone N5 OS Core and get generic templates  
**Need**: Personalized configuration that matches their work style  
**Solution**: Interactive onboarding that customizes everything

---

## Phase 0.5: Initial Setup

**New phase added to roadmap**

**Position**: Between Phase 0 (Foundation) and Phase 1 (Infrastructure)  
**Rationale**: Must personalize config before using the system

---

## Onboarding System Components

### 1. Intake Interview Script

**Purpose**: Discover user preferences, goals, work style

**Questions Cover**:
- Work context (role, industry, goals)
- Preferences (communication style, organization preferences)
- Technical comfort level
- Primary use cases
- Tool integrations
- Customization desires

**Format**: Conversational, friendly, 15-20 minutes max

---

### 2. Config Personalization

**Purpose**: Generate customized N5/config/ from templates

**Personalizes**:
- `rules.md` - adjust safety level, verbosity, style
- `prefs.md` - set preferences based on interview
- `commands.jsonl` - include relevant example commands
- Initial folder structure
- Default workflows

**Method**: Template variables + smart defaults

---

### 3. Guided Setup Wizard

**Purpose**: Walk through key decisions step-by-step

**Steps**:
1. Welcome & overview
2. Interview (discover preferences)
3. Review proposed config
4. Customize (optional deep-dive)
5. Generate configs
6. Validate setup
7. Tutorial (core concepts)

**UX**: Simple, educational, validatable

---

### 4. Validation System

**Purpose**: Ensure setup works correctly

**Tests**:
- Config files generated
- Syntax valid
- Preferences loadable
- Commands parseable
- System operational

**Output**: "✅ Setup complete!" or specific errors to fix

---

### 5. Welcome Experience

**Purpose**: Teach core concepts & features

**Includes**:
- Quick tour of N5 OS
- Key features demo
- First command execution
- Where to get help
- Next steps

---

## Design Principles

### 1. Simple (15-20 min max)
- Don't overwhelm with options
- Smart defaults for everything
- Can customize later

### 2. Educational
- Teach N5 concepts during setup
- Explain "why" behind questions
- Show examples

### 3. Personalizable
- Real customization, not just name swaps
- Meaningful configuration
- Reflects work style

### 4. Validatable
- Test everything works
- Clear success/failure
- Easy to retry

---

## Implementation Plan

### Files to Create

**Scripts**:
- `/install/onboard.py` - Main onboarding script
- `/install/interview.py` - Question flow
- `/install/personalize.py` - Config generation
- `/install/validate.py` - Setup validation

**Templates**:
- `/install/interview_questions.json` - Question bank
- `/install/personalization_rules.json` - Mapping logic
- `/templates/*.template.md` - Parameterized templates

**Docs**:
- `/docs/ONBOARDING.md` - User guide
- `/docs/CUSTOMIZATION.md` - Advanced config

---

## Example Interview Questions

**Work Context**:
1. "What's your primary role?" (creator, analyst, manager, etc.)
2. "What industry are you in?" (tech, creative, finance, etc.)
3. "What are your main goals with N5 OS?" (productivity, learning, automation, etc.)

**Preferences**:
4. "Communication style?" (concise, detailed, casual, formal)
5. "Organization preference?" (structured, flexible, minimal)
6. "Technical comfort?" (beginner, intermediate, advanced)

**Use Cases**:
7. "Primary use case?" (task management, knowledge base, automation, creative work)
8. "Which apps do you use daily?" (Gmail, Calendar, Notion, etc.)
9. "What workflows do you want to automate?"

**Customization**:
10. "Preferred command style?" (natural language, shortcuts, hybrid)
11. "Safety level?" (cautious, balanced, confident)
12. "Verbosity?" (minimal, moderate, detailed)

---

## Personalization Logic Examples

**If role = "Manager"**:
- Enable team coordination commands
- Add meeting management workflows
- Set communication style = professional

**If technical = "Beginner"**:
- Verbose error messages
- More examples in docs
- Safety = cautious
- Include tutorials

**If use case = "Knowledge Base"**:
- Enable knowledge management workflows
- Add search commands
- Set SSOT enforcement = strict

---

## Success Metrics

**Technical**:
- 10+ personalized config settings
- <20 min average completion time
- >95% successful validation
- Zero manual config editing required

**User**:
- Users complete onboarding (not skip)
- Positive feedback on personalization
- Setup works on first try
- Users understand core concepts

---

## Worker Assignment

**Worker**: file 'Records/Temporary/WORKER_ASSIGNMENT_20251028_085810_980082_dfVR.md'

**Deliverables**:
1. Full specification document
2. Interview question bank
3. Personalization logic
4. Setup scripts (Python)
5. Validation tests
6. Welcome guide
7. Documentation

**Timeline**: 3-5 hours design + implementation

---

## Integration with Roadmap

**Updated Roadmap**:
```
Phase 0 (Foundation) ✅
  ↓
Phase 0.5 (Onboarding) 📋 ← NEW
  ↓
Phase 1 (Infrastructure) ✅
  ↓
...continues to Phase 6
```

**Impact on v1.0**:
- Adds 3-5h to timeline
- Critical for user adoption
- Dramatically improves first-time experience
- Reduces support burden

---

## Why This Matters

**Without Onboarding**:
- Users get generic config
- Must manually customize everything
- Don't understand N5 concepts
- High abandonment rate

**With Onboarding**:
- Personalized from day one
- Educated on core concepts
- Working system immediately
- Higher adoption & satisfaction

**ROI**: 3-5h investment → 10x better user experience

---

## Next Steps

1. ✅ Worker spawned (designing system)
2. ⏳ Review worker output
3. ⏳ Refine based on feedback
4. ⏳ Implement on Demonstrator
5. ⏳ Test with real users
6. ⏳ Iterate based on results

---

*Created: 2025-10-28 03:58 ET*  
*By: Vibe Builder (Main Account)*  
*Worker: Designing onboarding system now*
