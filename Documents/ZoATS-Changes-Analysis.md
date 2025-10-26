# ZoATS System Changes: Analysis & Implementation Plan

**Date:** 2025-10-24  
**Conversation:** con_DTaHGNT2fjt3yn8s  
**Purpose:** Implement gender-neutral language + test data protection

---

## Changes Required

### 1. Gender-Neutral Language Implementation
**Goal:** Use they/them pronouns when candidate gender is unknown/uncertain

### 2. Test Data Protection  
**Goal:** Prevent test resumes and V's resume from being committed to GitHub

---

## Current System Overview

### Architecture
- **Pipeline:** Intake → Parse → Score → Outreach → Interview Prep
- **Workers:** 51 Python files across multiple modules
- **Test Jobs:** 8 job folders in `/home/workspace/ZoATS/jobs/`
- **Test Candidates:** Multiple candidate folders with real resume PDFs

### Git Configuration (Current)
`.gitignore` includes:
```gitignore
# Job data (keep structure, ignore content)
jobs/*/candidates/*/
jobs/*/.private/

# Inbox drop area  
inbox_drop/*
```

**Analysis:** Already excludes candidate data, but test jobs themselves are tracked

---

## Issue 1: Gender-Neutral Language

### Findings
**Current State:**
- ✅ No hardcoded gendered pronouns found in Python code
- ✅ No gendered language in templates
- ✅ Templates use placeholder variables like `{{candidate_name}}`

**Potential Risk Areas:**
1. **LLM-generated text** (scoring narratives, outreach emails, interview guides)
2. **System prompts** sent to LLMs for evaluation
3. **Documentation/examples** with gendered language

### Files to Review for LLM Instructions

#### High Priority (Generate Natural Language)
1. `workers/scoring/gestalt_scorer.py` — Generates `overall_narrative`
2. `workers/clarification/email_composer.py` — Generates outreach emails
3. `workers/clarification/employer_email_templates.py` — Email templates
4. `workers/rejection_email/` — Rejection email generation

#### Medium Priority (May Reference Candidates)
5. `workers/clarification/llm_email_parser.py` — Parses responses
6. `workers/scoring/zo_llm_extractors.py` — Signal extraction
7. Any system prompts in `lib/` or `templates/`

### Implementation Strategy

**Option A: Explicit Prompt Injection (Recommended)**
- Add gender-neutral instruction to all LLM calls
- Example: "Use they/them pronouns for the candidate unless gender is explicitly confirmed"
- Pros: Universal, consistent, works across all workers
- Cons: Slight token overhead per call

**Option B: Post-Processing**
- Regex replace he/she → they after generation
- Pros: No prompt changes needed
- Cons: Brittle, may miss edge cases, can create grammatical errors

**Option C: Hybrid**
- Prompt injection for critical flows (outreach, interview guides)
- Post-processing as safety net

**RECOMMENDATION: Option A with Option C fallback**

---

## Issue 2: Test Data Protection

### Current Test Data Locations

**Test Jobs with Real/Test Resumes:**
```
/home/workspace/ZoATS/jobs/
├── demo/
├── founding-engineer/
├── growthmanager-1025/
├── mckinsey-associate-15264/  ← Contains test candidates
├── smoke-test/
├── stack-overflow-sr-dir-pm/  ← Contains real resumes
├── test-job/                  ← Contains V's resume
```

**Test Data Identified:**
- `test-job/candidates/vrijen-001/` — V's resume (PDF)
- Multiple test candidate folders across jobs
- 5+ resume files in recent test run (FutureFit Growth Manager)

### Exposure Risk Assessment

**Current Git Status:**
- `.gitignore` excludes: `jobs/*/candidates/*/` ✅
- This SHOULD prevent candidate data from being committed
- BUT: Need to verify no files already tracked before rule was added

**Git Audit Required:**
```bash
cd /home/workspace/ZoATS
git ls-files | grep -E "jobs/.*/candidates/"
```

### Protection Strategy

#### Phase 1: Audit & Verify (Immediate)
1. Check what's currently tracked in Git
2. Identify any candidate PII already in repo
3. If found, use `git filter-branch` or BFG Repo-Cleaner to remove history

#### Phase 2: Strengthen .gitignore (Enhancement)
Current exclusions are good, but add explicit patterns:
```gitignore
# Candidate PII (STRICT - never commit)
jobs/*/candidates/*/raw/*.pdf
jobs/*/candidates/*/raw/*.docx
jobs/*/candidates/*/raw/*.doc
jobs/*/candidates/*/parsed/*.md
jobs/*/candidates/*/outputs/*.json

# V's test data (EXPLICIT)
**/vrijen*
**/v_mostrecentresume*
```

#### Phase 3: Pre-Commit Hook (Safeguard)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Block commits containing resume files or V's name
if git diff --cached --name-only | grep -E "jobs/.*/candidates/.*\.(pdf|docx|md)" > /dev/null; then
  echo "ERROR: Attempting to commit candidate resume data!"
  echo "This violates privacy policy. Commit blocked."
  exit 1
fi

if git diff --cached --name-only | grep -i "vrijen" > /dev/null; then
  echo "ERROR: Attempting to commit test data containing V's information!"
  exit 1
fi
```

#### Phase 4: GitHub Secrets Scanning (External)
Enable GitHub secret scanning for:
- Email patterns
- Phone numbers
- SSNs (if ever extracted)

---

## Implementation Plan

### Immediate Actions (Today)

**1. Git Audit (5 min)**
```bash
cd /home/workspace/ZoATS
git ls-files | grep -E "(candidates|vrijen|test)" > /tmp/git_audit.txt
cat /tmp/git_audit.txt
```

**2. Gender-Neutral Prompt Library (15 min)**
Create `lib/prompt_guidelines.py`:
```python
GENDER_NEUTRAL_INSTRUCTION = """
When referring to the candidate, use gender-neutral language:
- Use "they/them/their" pronouns
- Use "the candidate" or the candidate's name
- Avoid "he/she/his/her" unless gender is explicitly confirmed
"""

def add_gender_neutral_instruction(prompt: str) -> str:
    return f"{prompt}\n\n{GENDER_NEUTRAL_INSTRUCTION}"
```

**3. Update High-Priority Workers (30 min)**
- Inject instruction into gestalt_scorer.py LLM calls
- Update email_composer.py
- Update any dossier generation

### Phase 2: Testing (Tomorrow)

**4. Test Gender-Neutral Output (15 min)**
- Run scoring on test candidate
- Verify narratives use "they/them"
- Check outreach emails

**5. Strengthen .gitignore (10 min)**
- Add explicit patterns from Phase 2 above
- Test with `git status` and dummy files

**6. Deploy Pre-Commit Hook (10 min)**
- Create hook script
- Test by attempting to stage a resume file

### Phase 3: Documentation & Validation

**7. Update System Documentation (15 min)**
- Add gender-neutral policy to `ORCHESTRATOR_INBOX.md`
- Document test data protection in README.md
- Create `SECURITY.md` with PII handling guidelines

**8. Run Full Pipeline Test (30 min)**
- Process test candidate end-to-end
- Verify gender-neutral language throughout
- Confirm no test data can be committed

---

## Files to Modify

### Gender-Neutral Implementation
1. `/home/workspace/ZoATS/lib/prompt_guidelines.py` — NEW
2. `/home/workspace/ZoATS/workers/scoring/gestalt_scorer.py` — MODIFY
3. `/home/workspace/ZoATS/workers/scoring/zo_llm_extractors.py` — MODIFY
4. `/home/workspace/ZoATS/workers/clarification/email_composer.py` — MODIFY
5. `/home/workspace/ZoATS/workers/rejection_email/*` — REVIEW & MODIFY

### Test Data Protection
1. `/home/workspace/ZoATS/.gitignore` — ENHANCE
2. `/home/workspace/ZoATS/.git/hooks/pre-commit` — NEW
3. `/home/workspace/ZoATS/SECURITY.md` — NEW
4. `/home/workspace/ZoATS/README.md` — UPDATE

---

## Success Criteria

### Gender-Neutral Language ✓
- [ ] All LLM-generated narratives use "they/them"
- [ ] Email templates default to gender-neutral
- [ ] Interview guides avoid gendered language
- [ ] Test run produces 0 gendered pronouns in output

### Test Data Protection ✓
- [ ] Git audit shows no candidate PII tracked
- [ ] Pre-commit hook blocks resume file staging
- [ ] Test with V's resume: cannot commit
- [ ] .gitignore verified with `git check-ignore -v`

---

## Risk Assessment

### Gender-Neutral Language
- **Risk:** LLM may still generate gendered pronouns despite instruction
- **Mitigation:** Post-processing regex as fallback
- **Testing:** Manual review of 10+ outputs

### Test Data Protection
- **Risk:** Files committed before .gitignore won't be auto-removed
- **Mitigation:** Git history audit + filter-branch if needed
- **Testing:** Attempt to commit test file (should fail)

---

## Questions for V

1. **Gender handling:** Should we allow explicitly specified gender (if known) or always default to they/them?
2. **Test data scope:** Are there other test files beyond resumes (e.g., test email threads, dossiers) that should never be committed?
3. **Git history:** Should we scrub existing history or just prevent future commits?
4. **Priority:** Should we implement both changes simultaneously or sequence them?

---

## Next Steps

**Awaiting V's approval to proceed with:**
1. Git audit (read-only, safe)
2. Gender-neutral prompt library creation
3. Worker modifications
4. .gitignore enhancement + pre-commit hook

**Estimated total time:** 2-3 hours for complete implementation + testing

