# ZoATS Evidence Pipeline

**Version**: 1.0.0  
**Purpose**: System for collecting, validating, and weighting evidence in candidate evaluation  
**Last Updated**: 2025-10-22

---

## Overview

The Evidence Pipeline is the backbone of ZoATS scoring. It ensures that every score is **traceable to specific evidence**, validated where possible, and appropriately weighted based on source reliability.

### Core Principles

1. **No Score Without Evidence**: Every criterion score must cite specific evidence
2. **Validation Over Volume**: One validated piece of evidence > five self-reported claims
3. **Triangulation**: Cross-reference claims across multiple sources
4. **Transparency**: Show founders exactly why a candidate scored as they did
5. **Continuous Validation**: Evidence strength increases as more sources corroborate

---

## Evidence Collection Stages

### Stage 1: Application Intake (Automatic)

**Trigger**: New candidate email arrives  
**Duration**: <5 seconds  
**Automated**: 100%

#### Actions:
1. **Parse Email & Attachments**
   - Extract email body, subject, sender info
   - Download and categorize attachments:
     - Resume (PDF, DOCX, TXT)
     - Cover letter (if separate)
     - Portfolio links (extract URLs)
     - Additional materials

2. **Initial Data Extraction**
   - Resume parsing:
     - Contact info (name, email, phone, location, LinkedIn, GitHub, portfolio)
     - Work history (company, title, dates, description)
     - Education (school, degree, dates, GPA if present)
     - Skills (technical, soft, languages, tools)
     - Projects (name, description, links)
     - Certifications
   - Cover letter analysis:
     - "Why this company" section
     - "Why this role" section
     - Key themes and motivations

3. **Create Candidate Record**
   - Generate candidate ID: `{job-slug}-{timestamp}-{hash}`
   - Initialize `candidate.json` with parsed data
   - Create `candidate.md` for human-readable summary

**Evidence Collected**:
- `application_materials.resume_path`
- `application_materials.cover_letter_path`
- `parsed_data.*` (all structured resume data)
- `contact_info.*`

**Evidence Weight**: Self-reported (0.6)

---

### Stage 2: Quick Test Filter (Automatic)

**Trigger**: Application intake complete  
**Duration**: 10-30 seconds  
**Automated**: 100%

#### Actions:
1. **Dealbreaker Checks** (per rubric)
   - Check each `is_dealbreaker: true` criterion
   - Example: "Minimum 3 years Python experience"
     - Scan work history for Python mentions
     - Calculate total months of Python work
     - Pass/Fail determination
   - Document result in `quick_test_results.dealbreaker_checks[]`

2. **Initial AI-Generation Scan**
   - Run AI detection on:
     - Resume text (full)
     - Cover letter (full)
   - Generate likelihood scores (0.0-1.0)
   - Flag if any component >0.70
   - Store in `authenticity_analysis.resume_ai_likelihood`, etc.

3. **Basic Red Flag Detection**
   - Keyword stuffing (density analysis)
   - Suspicious patterns (e.g., "expert in 20+ languages")
   - Obvious inconsistencies (dates, locations)
   - Store in `quick_test_results.initial_flags[]`

4. **Routing Decision**
   - **Pass**: All dealbreakers passed, no critical red flags → Deep Screening
   - **Fail**: Any dealbreaker failed → Reject
   - **Review**: Borderline or flags need human assessment → Manual Review

**Evidence Collected**:
- `quick_test_results.dealbreaker_checks[]`
- `authenticity_analysis.resume_ai_likelihood`
- `authenticity_analysis.cover_letter_ai_likelihood`
- `quick_test_results.initial_flags[]`

**Evidence Weight**: Inferred (0.5) for dealbreakers, AI detection model-dependent

---

### Stage 3: External Validation (Automatic)

**Trigger**: Quick test passed  
**Duration**: 30-90 seconds  
**Automated**: 100%

#### Actions:
1. **LinkedIn Cross-Reference**
   - Search for candidate by name + email
   - If found:
     - Compare work history (companies, titles, dates)
     - Compare education
     - Extract endorsements (top skills)
     - Count recommendations
     - Calculate match scores (0.0-1.0):
       - `work_history_match`: % of resume jobs found on LinkedIn
       - `education_match`: degree and school matches
     - Flag discrepancies
   - Store in `cross_reference_results.linkedin_validation`

2. **GitHub Analysis** (if GitHub link provided)
   - Fetch public profile data:
     - Username, bio
     - Public repos count
     - Contribution activity (last year)
     - Primary languages used
     - Stars received on projects
   - Identify notable projects (>50 stars or mentioned in resume)
   - Assess activity level: commits/month
   - Store in `cross_reference_results.github_analysis`

3. **News/Publication Search** (if candidate claims notable achievements)
   - Extract newsworthy claims:
     - "Featured in [Publication]"
     - "Spoke at [Conference]"
     - "Won [Award]"
   - Search for candidate name + claim keywords
   - Validate and store mentions in `cross_reference_results.news_mentions[]`

4. **Portfolio Validation** (if portfolio link provided)
   - Fetch portfolio URL
   - Assess:
     - Does it exist and load?
     - Quality level (basic/good/excellent/exceptional)
     - Work sample count
     - Authenticity signals (process documentation, variety)
   - Store in `cross_reference_results.portfolio_validation`

**Evidence Collected**:
- `cross_reference_results.linkedin_validation.*`
- `cross_reference_results.github_analysis.*`
- `cross_reference_results.news_mentions[]`
- `cross_reference_results.portfolio_validation.*`

**Evidence Weight**: Validated External (1.2) - highest confidence

---

### Stage 4: Screening Questions (Interactive)

**Trigger**: External validation complete, candidate still in consideration  
**Duration**: 2-48 hours (candidate response time)  
**Automated**: Question generation + response analysis

#### Actions:
1. **Generate Personalized Questions**
   - Load job rubric `screening_questions[]` (core questions for all)
   - Add personalized follow-ups based on:
     - Gaps or ambiguities in application
     - Impressive claims to explore deeper
     - Red flags to probe
     - Unique background to understand better
   - Limit: 3-5 questions total (respect candidate time)
   - Store questions in `screening_interaction.questions[]`

2. **Send Email to Candidate**
   - Personalized email with questions
   - 48-hour response window
   - Include company context and expectations
   - Log `questions_sent_at` timestamp

3. **Await Response** (no action)

4. **Process Response** (when received)
   - Parse response email
   - Match answers to questions (by order or explicit matching)
   - For each response:
     - Calculate word count
     - Run AI-generation detection
     - Calculate specificity score:
       - Concrete examples vs. generic statements
       - Quantified details vs. vague descriptions
       - Unique insights vs. common wisdom
     - Calculate uniqueness score:
       - Compare to other candidates' responses to same/similar questions
       - Semantic similarity analysis
       - Highlight most unique phrasing/ideas
   - Log `response_received_at` and calculate `response_time_hours`
   - Update `authenticity_analysis.screening_responses_ai_likelihood`
   - Store all in `screening_interaction`

**Evidence Collected**:
- `screening_interaction.questions[]`
- `screening_interaction.questions[].response`
- `screening_interaction.questions[].ai_likelihood`
- `screening_interaction.questions[].specificity_score`
- `screening_interaction.questions[].uniqueness_score`
- `authenticity_analysis.uniqueness_analysis.*`

**Evidence Weight**: Direct Evidence (1.0), but weighted by authenticity scores

---

### Stage 5: Deep Evaluation (Automatic)

**Trigger**: Screening responses received and analyzed  
**Duration**: 60-120 seconds  
**Automated**: 100%

#### Actions:
1. **Evidence Aggregation**
   - For each rubric criterion:
     - Identify all relevant evidence from:
       - Resume (`parsed_data`)
       - Cover letter
       - Screening responses
       - LinkedIn validation
       - GitHub activity
       - Portfolio
       - News mentions
     - Tag evidence by type (see Evidence Types below)
     - Extract relevant excerpts
     - Assess evidence strength (weak/moderate/strong)

2. **Criterion Scoring**
   - For each criterion:
     - Apply scoring method (binary, scale_1_5, scale_1_10, etc.)
     - Weight evidence by source reliability
     - Generate rationale (2-3 sentences citing specific evidence)
     - Store in `rubric_scores.criteria_groups[].criteria_scores[]`

3. **Multi-Perspective Evaluation** (if enabled)
   - For each persona in rubric:
     - Simulate evaluation from that perspective
     - Focus on persona's `focus_areas`
     - Generate persona-specific score
     - Document key observations, concerns, strengths
   - Calculate consensus score (weighted average)
   - Assess disagreement level
   - Store in `multi_perspective_scores`

4. **Ultra-Signal Detection**
   - Scan for green flags (from rubric + general)
   - Scan for red flags (from rubric + general)
   - For each detected:
     - Extract evidence
     - Assess significance/severity
     - Store in `ultra_signals`

5. **Final Score Calculation**
   - Calculate group scores (weighted sum of criteria)
   - Calculate total score (weighted sum of groups)
   - Calculate percentile (if enough candidates for normalization)
   - Store in `rubric_scores`

6. **Interview Recommendations**
   - Determine `should_interview` based on threshold
   - Assess `priority_level`
   - Generate suggested interview questions:
     - Areas to probe deeper (ambiguities, red flags)
     - Strengths to validate (impressive claims)
     - Ultra-signals to explore (unique background)
   - Store in `interview_recommendations`

**Evidence Collected**:
- `rubric_scores.*` (complete rubric evaluation)
- `multi_perspective_scores.*` (panel simulation)
- `ultra_signals.*` (exceptional indicators)
- `interview_recommendations.*` (what to ask next)

**Evidence Weight**: Composite (varies by source)

---

## Evidence Types

### Primary Sources (Direct Evidence, Weight: 1.0)

1. **Resume Section** (`resume_section`)
   - Structured data from specific resume section
   - Work history, education, skills, projects
   - High volume, but self-reported

2. **Work History** (`work_history`)
   - Specific job with company, title, dates, achievements
   - Quantified impact statements
   - Can be cross-referenced

3. **Education** (`education`)
   - Degree, institution, dates
   - Easily verifiable
   - Less subject to inflation

4. **Screening Response** (`screening_response`)
   - Candidate's answers to custom questions
   - Shows communication, thinking, authenticity
   - Can be AI-generated (must detect)

5. **Portfolio Link** (`portfolio_link`)
   - URL to candidate's portfolio or work samples
   - Direct evidence of capability
   - Authenticity must be validated

6. **Code Sample** (`code_sample`)
   - Actual code written by candidate
   - GitHub repos, CodePen, attachments
   - Strong signal if authentic

7. **Writing Sample** (`writing_sample`)
   - Blog posts, documentation, technical writing
   - Shows communication and expertise
   - Can validate via publication date

### Validated External (Weight: 1.2)

8. **LinkedIn Endorsement** (`linkedin_endorsement`)
   - Skills endorsed by connections
   - Weak signal individually, strong in aggregate
   - Harder to fake than self-report

9. **GitHub Profile** (`github_profile`)
   - Public contribution history
   - Activity level, languages, notable projects
   - Difficult to fake sustained activity

10. **News Mention** (`news_mention`)
    - Media coverage of candidate's work
    - Third-party validation
    - Rare but highly valuable

11. **Published Work** (`published_work`)
    - Papers, articles, open source projects
    - Verifiable through publication metadata
    - Strong credibility signal

### Secondary Sources (Indirect Evidence, Weight: 0.7)

12. **Case Study** (`case_study`)
    - Portfolio case studies or project write-ups
    - Self-reported but shows thinking process
    - Can be detailed and impressive

13. **Reference** (`reference`)
    - Third-party testimonial (future feature)
    - Strong if from reputable source
    - Can be gamed (friends/family)

---

## Evidence Weighting System

Each piece of evidence is weighted based on:

1. **Source Reliability** (see weights above)
2. **Validation Status**
   - Cross-referenced: +20%
   - Contradicted: -50%
   - Single source only: -20%
3. **Recency** (if time decay enabled)
   - Half-life: 24 months (default)
   - Formula: `weight * (0.5 ^ (age_months / 24))`
4. **Strength Assessment**
   - **Strong**: Specific, quantified, unique → 1.0x
   - **Moderate**: Adequate but not exceptional → 0.8x
   - **Weak**: Vague, generic, or insufficient → 0.5x

### Example Evidence Scoring

**Criterion**: Core Technical Competency (Python)

**Evidence Pieces**:
1. Resume: "3 years Python experience at Company X"
   - Type: `work_history`
   - Base Weight: 1.0 (direct)
   - Validation: LinkedIn confirms Company X employment ✓ → 1.2x
   - Strength: Moderate (duration stated but no projects detailed) → 0.8x
   - **Final Weight**: 1.0 × 1.2 × 0.8 = **0.96**

2. GitHub: 15 public Python repos, 500+ commits last year
   - Type: `github_profile`
   - Base Weight: 1.2 (validated external)
   - Validation: Live data, can't fake ✓ → 1.2x
   - Strength: Strong (sustained activity) → 1.0x
   - **Final Weight**: 1.2 × 1.2 × 1.0 = **1.44**

3. Screening Response: "I built a Django backend that scaled to 100k users..."
   - Type: `screening_response`
   - Base Weight: 1.0 (direct)
   - Validation: AI likelihood 15% (human) ✓, specificity 8/10 ✓ → 1.1x
   - Strength: Strong (specific, quantified) → 1.0x
   - **Final Weight**: 1.0 × 1.1 × 1.0 = **1.1**

4. Portfolio: Live web app built with Python/Flask
   - Type: `portfolio_link`
   - Base Weight: 1.0 (direct)
   - Validation: Working URL, code visible, authentic ✓ → 1.2x
   - Strength: Strong (actual product) → 1.0x
   - **Final Weight**: 1.0 × 1.2 × 1.0 = **1.2**

**Aggregate Evidence Score**: (0.96 + 1.44 + 1.1 + 1.2) / 4 = **1.175**  
**Criterion Raw Score**: 8/10 (strong evidence)  
**Weighted Score**: 8 × 1.175 = **9.4/10** (exceptional confidence)

---

## Evidence Traceability

Every score must be traceable to specific evidence. In `candidate.json`:

```json
{
  "rubric_scores": {
    "criteria_groups": [
      {
        "group_id": "technical_skills",
        "criteria_scores": [
          {
            "criterion_id": "tech_core_competency",
            "raw_score": 8,
            "weighted_score": 9.4,
            "evidence": [
              {
                "source": "work_history",
                "excerpt": "Senior Python Developer at Company X (2020-2023): Built microservices handling 1M+ requests/day",
                "strength": "moderate",
                "weight": 0.96
              },
              {
                "source": "github_profile",
                "excerpt": "15 public Python repos, 500+ commits in last year, primarily Django and FastAPI",
                "strength": "strong",
                "weight": 1.44
              },
              {
                "source": "screening_response",
                "excerpt": "I built a Django backend that scaled to 100k users by implementing Redis caching and database connection pooling...",
                "strength": "strong",
                "weight": 1.1
              },
              {
                "source": "portfolio_link",
                "excerpt": "Live web app: taskmanager.com - Full-stack app built with Python/Flask, PostgreSQL, React. [URL validated]",
                "strength": "strong",
                "weight": 1.2
              }
            ],
            "rationale": "Candidate demonstrates strong Python expertise through sustained work experience (3 years), active GitHub contributions (500+ commits/year), specific technical examples in screening responses, and a live production-quality portfolio project. Evidence is cross-validated via LinkedIn and GitHub. Depth and breadth exceed role requirements."
          }
        ]
      }
    ]
  }
}
```

---

## Evidence Pipeline Automation

### Implementation Stages

**MVP (Week 1)**:
- ✅ Resume parsing (basic)
- ✅ Quick-test dealbreakers
- ✅ AI-generation detection (cover letter + resume)
- ✅ Evidence extraction (manual rubric scoring)
- ✅ Basic evidence citations

**Week 2**:
- ✅ LinkedIn cross-reference (web scraping or API)
- ✅ GitHub analysis (GitHub API)
- ✅ Screening question generation + analysis
- ✅ Uniqueness scoring across candidates
- ✅ Specificity scoring

**Post-MVP**:
- 🔮 Portfolio quality assessment (vision model)
- 🔮 News mention validation (web search API)
- 🔮 Multi-perspective scoring
- 🔮 Time decay weighting
- 🔮 Evidence strength ML model (learn from hiring outcomes)

---

## Evidence Quality Checks

Before finalizing a candidate score, run quality checks:

1. **Sufficient Evidence**: Each criterion has ≥2 evidence pieces
2. **Diverse Sources**: Not all evidence is self-reported
3. **Cross-Validation**: Key claims are validated externally where possible
4. **No Contradictions**: Evidence pieces don't contradict each other (flag if they do)
5. **Recency**: Evidence isn't all outdated (>5 years old)

If any check fails → Flag for manual review

---

## Human-in-the-Loop

While the pipeline is automated, humans can:

1. **Add Manual Evidence** (via `notes[]`)
   - Founder/team can add observations
   - Tagged and timestamped
   - Factored into manual review

2. **Override Scores** (with justification)
   - Stored in `notes[]` with reasoning
   - Logged in `timeline[]`
   - Does not affect other candidates (prevents bias drift)

3. **Validate AI-Flagged Content**
   - Review borderline AI likelihood scores
   - Confirm or reject system determination
   - Improves model over time

---

## Privacy & Ethics

- **Data Minimization**: Collect only what's needed for evaluation
- **Transparency**: Show candidates what data was collected (upon request)
- **Deletion**: Support candidate data deletion requests
- **Bias Auditing**: Regular review of evidence weighting for unintended discrimination
- **No Black Box**: Every score must have human-readable rationale

---

## Integration with ZoATS

The Evidence Pipeline integrates with:

- **`rubric.json`**: Defines what evidence is needed per criterion
- **`candidate.json`**: Stores all collected evidence
- **`scoring_engine.py`**: Calculates weighted scores from evidence
- **`founder_digest.md`**: Surfaces key evidence for finalist decisions

---

## Monitoring & Improvement

Track evidence quality metrics:

1. **Coverage**: % of criteria with ≥2 evidence pieces
2. **Validation Rate**: % of claims cross-referenced
3. **Conflict Rate**: % of evidence showing contradictions
4. **Evidence-to-Outcome**: Correlation of evidence types with successful hires
5. **Source Reliability**: Update weights based on prediction accuracy

Review quarterly, adjust weights based on hiring outcomes.

---

**Version History**:
- v1.0.0 (2025-10-22): Initial evidence pipeline design

**Related Files**:
- `file 'schemas/rubric.schema.json'` - Evidence types defined
- `file 'schemas/candidate.schema.json'` - Evidence storage structure
- `file 'scoring_weights.json'` - Evidence weighting configuration
