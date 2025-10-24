# ZoATS Criteria Library

**Version**: 1.0.0  
**Purpose**: Reusable evaluation criteria for building job-specific rubrics  
**Last Updated**: 2025-10-22

---

## How to Use This Library

1. **Select criteria** relevant to your role from the groups below
2. **Customize weights** based on role requirements
3. **Add role-specific criteria** not covered here
4. **Define dealbreakers** for must-have requirements
5. **Configure evidence types** needed to validate each criterion

---

## Criteria Groups

### 1. Technical Skills

#### 1.1 Core Technical Competency
**ID**: `tech_core_competency`  
**Description**: Demonstrated mastery of role-essential technical skills  
**Typical Weight**: 0.30-0.50 (for technical roles)

**Evidence Types**: 
- Work history with specific technologies
- Portfolio/GitHub projects
- Technical certifications
- Code samples or technical writing

**Green Flags**:
- Deep expertise in multiple related technologies
- Self-taught in emerging/cutting-edge domains
- Open source contributions
- Technical blog posts or teaching

**Red Flags**:
- Keyword stuffing without context
- Exaggerated claims (e.g., "expert in 20 languages")
- No demonstrable projects or work samples
- Technologies listed don't match job history

**Scoring Method**: `scale_1_10` or `evidence_count`

---

#### 1.2 System Design & Architecture
**ID**: `system_design`  
**Description**: Ability to design scalable, maintainable systems  
**Typical Weight**: 0.20-0.30 (senior technical roles)

**Evidence Types**:
- Architecture decisions in past roles
- Portfolio case studies showing system design
- Published technical writing on architecture
- Open source project structure

**Evaluation Prompts**:
- "Does the candidate demonstrate understanding of trade-offs?"
- "Evidence of building vs. over-engineering?"
- "Can they explain complex systems simply?"

**Green Flags**:
- Experience scaling systems from 0→100k+ users
- Clear articulation of architectural decisions
- Balance between pragmatism and quality

**Red Flags**:
- Buzzword-heavy without substance
- No experience with production systems
- Over-engineering small projects

---

#### 1.3 Problem Solving & Debugging
**ID**: `problem_solving`  
**Description**: Ability to diagnose and solve complex technical problems  
**Typical Weight**: 0.15-0.25

**Evidence Types**:
- Specific examples of problems solved
- Stack Overflow contributions
- Bug fixes in open source
- Technical incident post-mortems

**Evaluation Prompts**:
- "Do they describe their debugging process?"
- "Evidence of root cause analysis vs. band-aid fixes?"
- "Can they work through ambiguous problems?"

---

#### 1.4 Code Quality & Craftsmanship
**ID**: `code_quality`  
**Description**: Writing clean, maintainable, well-tested code  
**Typical Weight**: 0.15-0.25

**Evidence Types**:
- GitHub code samples
- Code review comments
- Testing practices mentioned
- Documentation quality

**Green Flags**:
- Tests written alongside features
- Clear, self-documenting code
- Thoughtful comments where needed
- Refactoring experience

---

### 2. Soft Skills & Collaboration

#### 2.1 Communication Clarity
**ID**: `communication_clarity`  
**Description**: Ability to explain complex ideas clearly to varied audiences  
**Typical Weight**: 0.15-0.25

**Evidence Types**:
- Cover letter quality
- Screening responses
- Technical writing samples
- Presentation experience

**Evaluation Prompts**:
- "Is the writing clear and concise?"
- "Do they adapt explanations for audience?"
- "Evidence of teaching or documentation?"

**Green Flags**:
- Technical concepts explained simply
- Active listening in written responses
- Experience teaching or mentoring
- High-quality documentation

**Red Flags**:
- Jargon-heavy with poor clarity
- One-size-fits-all communication
- Dismissive of non-technical stakeholders
- Poor grammar/structure in application

---

#### 2.2 Collaboration & Teamwork
**ID**: `collaboration`  
**Description**: Works effectively with cross-functional teams  
**Typical Weight**: 0.15-0.25

**Evidence Types**:
- Team project descriptions
- Cross-functional work examples
- References to collaboration tools
- Open source collaboration

**Evaluation Prompts**:
- "Do they emphasize 'we' over 'I'?"
- "Evidence of working across disciplines?"
- "How do they handle disagreements?"

**Green Flags**:
- Specific examples of team successes
- Cross-functional project leadership
- Mentoring junior team members
- Active in communities (online/offline)

**Red Flags**:
- Solo work only, no team context
- "Lone wolf" mentality
- Dismissive of others' contributions
- Conflict avoidance or aggression

---

#### 2.3 Ownership & Initiative
**ID**: `ownership`  
**Description**: Takes responsibility and drives projects to completion  
**Typical Weight**: 0.20-0.30

**Evidence Types**:
- Projects led or initiated
- Side projects or open source
- Process improvements made
- Taking responsibility in screening responses

**Evaluation Prompts**:
- "Do they describe taking initiative?"
- "Evidence of seeing projects through?"
- "Do they own mistakes or blame others?"

**Green Flags**:
- Started projects from scratch
- Process improvements implemented
- Takes responsibility for failures
- Self-directed learning

**Red Flags**:
- Passive role descriptions only
- Blaming others for failures
- No evidence of independent work
- Waiting to be told what to do

---

#### 2.4 Adaptability & Learning
**ID**: `adaptability`  
**Description**: Thrives in changing environments, learns quickly  
**Typical Weight**: 0.15-0.25

**Evidence Types**:
- Career transitions
- New skills acquired recently
- Diverse project types
- Handling of ambiguity in responses

**Evaluation Prompts**:
- "Evidence of learning new domains quickly?"
- "Comfortable with ambiguity?"
- "Growth trajectory across roles?"

**Green Flags**:
- Successfully pivoted between domains
- Recent upskilling in new technologies
- Thrives in early-stage/ambiguous environments
- Specific examples of learning from failure

---

### 3. Experience & Track Record

#### 3.1 Relevant Experience Depth
**ID**: `experience_depth`  
**Description**: Years and depth of experience in relevant domain  
**Typical Weight**: 0.20-0.30  
**Often a Dealbreaker**: Yes (e.g., "minimum 3 years")

**Evidence Types**:
- Work history duration
- Progression of responsibilities
- Domain expertise demonstrated
- Validated via LinkedIn

**Scoring Method**: `scale_1_5` or `binary` (if dealbreaker)

**Thresholds** (example):
- 1: <1 year relevant experience
- 2: 1-2 years
- 3: 2-4 years
- 4: 4-7 years
- 5: 7+ years with deep expertise

---

#### 3.2 Impact & Results
**ID**: `impact`  
**Description**: Demonstrated measurable impact in previous roles  
**Typical Weight**: 0.25-0.40

**Evidence Types**:
- Quantified achievements
- Product launches or features shipped
- Revenue/growth impact
- Awards or recognition

**Evaluation Prompts**:
- "Are achievements quantified with metrics?"
- "Evidence of moving key business metrics?"
- "Do they articulate their specific contribution?"

**Green Flags**:
- Specific metrics (e.g., "increased conversion by 40%")
- Product launches with adoption metrics
- Revenue or growth directly attributed
- Company-wide recognition

**Red Flags**:
- Vague achievements ("helped improve...")
- Team success without individual contribution
- No measurable outcomes
- Inflated or unverifiable claims

---

#### 3.3 Career Trajectory
**ID**: `career_trajectory`  
**Description**: Growth pattern and progression over time  
**Typical Weight**: 0.10-0.20

**Evidence Types**:
- Job title progression
- Responsibility growth
- Compensation growth (if mentioned)
- Promotions and role changes

**Evaluation Prompts**:
- "Steady upward trajectory?"
- "Expanding scope of responsibility?"
- "Logical career transitions?"

**Green Flags**:
- Consistent promotions or expanding roles
- Increased responsibility over time
- Strategic career moves with clear reasoning
- Fast progression in high-quality companies

**Red Flags**:
- Frequent job hopping (<1 year stints)
- Lateral moves without growth
- Downward trajectory without explanation
- Inconsistent career narrative

---

### 4. Culture Fit & Values

#### 4.1 Mission Alignment
**ID**: `mission_alignment`  
**Description**: Genuine connection to company mission/problem space  
**Typical Weight**: 0.10-0.20

**Evidence Types**:
- "Why this company" specificity
- Personal connection to problem
- Research depth into company
- Alignment in values

**Evaluation Prompts**:
- "How specific is their 'why this company'?"
- "Personal connection or just career move?"
- "Evidence of researching company deeply?"

**Green Flags**:
- Specific references to company's unique approach
- Personal story connecting to mission
- Deep understanding of company's market position
- Excitement about specific aspects of the work

**Red Flags**:
- Generic reasons ("great opportunity," "exciting team")
- Keyword matching from job description
- No evidence of research
- Focus only on compensation/title

**Uniqueness Scoring**: Compare across all applicants - most specific/unique should rank highest

---

#### 4.2 Startup Mindset (for early-stage)
**ID**: `startup_mindset`  
**Description**: Thrives in ambiguity, wears multiple hats, resourceful  
**Typical Weight**: 0.20-0.35 (for employees 1-3)

**Evidence Types**:
- Early-stage company experience
- Side projects or entrepreneurial ventures
- Scrappy problem-solving examples
- Comfort with ambiguity

**Evaluation Prompts**:
- "Experience building from scratch (0→1)?"
- "Evidence of wearing multiple hats?"
- "Comfort with rapid change?"

**Green Flags**:
- Previous startup experience (seed/Series A)
- Founded or co-founded projects
- Generalist skillset + specialist depth
- Examples of scrappy resourcefulness

**Red Flags**:
- Only big company/corporate experience
- Narrow specialist without flexibility
- Need for structure and process
- Risk-averse decision making

---

#### 4.3 Work Style Match
**ID**: `work_style`  
**Description**: Alignment with team's working style and pace  
**Typical Weight**: 0.10-0.20

**Evidence Types**:
- Remote/onsite preference match
- Work hours/pace preferences
- Collaboration style
- Response to screening questions

**Evaluation Prompts**:
- "Do their preferences match our setup?"
- "Communication style aligned?"
- "Pace and intensity match?"

---

### 5. Motivation & Intent

#### 5.1 Intrinsic Motivation
**ID**: `intrinsic_motivation`  
**Description**: Genuinely passionate about the work itself  
**Typical Weight**: 0.15-0.25

**Evidence Types**:
- Side projects related to domain
- Self-directed learning
- Community involvement
- Long-term engagement in field

**Evaluation Prompts**:
- "Do they work on related projects outside work?"
- "Evidence of deep curiosity?"
- "Learning for its own sake?"

**Green Flags**:
- Side projects aligned with role
- Active in technical/industry communities
- Self-taught skills acquired for fun
- Long-term engagement (not just job-seeking)

**Red Flags**:
- Only motivated by external rewards
- No evidence of work outside job requirements
- Transactional language throughout
- Lack of curiosity or exploration

---

#### 5.2 Long-Term Commitment Potential
**ID**: `commitment_potential`  
**Description**: Likelihood of staying and growing with company  
**Typical Weight**: 0.10-0.20

**Evidence Types**:
- Job tenure patterns
- Reasons for leaving past roles
- Long-term goals alignment
- Relocation or remote stability

**Evaluation Prompts**:
- "Pattern of job longevity?"
- "Reasons for leaving make sense?"
- "Long-term goals align with company trajectory?"

---

### 6. Authenticity & Integrity

#### 6.1 Authenticity of Application
**ID**: `authenticity`  
**Description**: Application materials reflect real person, not AI/template  
**Typical Weight**: 0.15-0.25  
**Critical for ZoATS**

**Evidence Types**:
- AI-generation likelihood score
- Uniqueness across applicants
- Specificity of examples
- Voice consistency

**Evaluation Prompts**:
- "Does this sound like a real person?"
- "Specific details vs. generic statements?"
- "Voice consistent across materials?"

**Green Flags**:
- Highly specific personal examples
- Unique perspective or framing
- Imperfect but authentic voice
- Details that can't be AI-generated

**Red Flags**:
- High AI-generation likelihood (>70%)
- Generic phrasing matching templates
- Perfect polish with no personality
- Inconsistent voice across materials

**Scoring Method**: `ai_likelihood` inverse + `uniqueness_score` + `specificity_score`

---

#### 6.2 Honesty & Transparency
**ID**: `honesty`  
**Description**: Truthful about experience, doesn't exaggerate  
**Typical Weight**: 0.10-0.15  
**Dealbreaker if Failed**

**Evidence Types**:
- Cross-reference with LinkedIn
- Verification of claims via news/GitHub
- Consistency across materials
- Acknowledgment of gaps/weaknesses

**Evaluation Prompts**:
- "Claims match external validation?"
- "Honest about limitations?"
- "Consistent story across sources?"

**Green Flags**:
- Perfect or near-perfect cross-reference match
- Acknowledges skills they're still learning
- Transparent about career gaps
- Undersells rather than oversells

**Red Flags**:
- Discrepancies between resume and LinkedIn
- Unverifiable or inflated claims
- Omission of significant gaps
- Exaggerated titles or responsibilities

**Scoring Method**: `binary` - pass/fail based on cross-reference

---

### 7. Role-Specific Ultra-Signals

#### 7.1 For Founding Engineers

**Non-Traditional Excellence**
- Self-taught developer with shipped products
- Transitioned from non-tech background successfully
- Open source maintainer of meaningful projects

**Technical Taste**
- Strong opinions, loosely held
- Pragmatic technology choices
- Understanding of technical debt trade-offs

**Builder Mentality**
- Examples of 0→1 products
- Shipped side projects users actually use
- Prototype-to-production experience

---

#### 7.2 For Founding Designers

**Product Thinking**
- Design decisions tied to business outcomes
- User research driving design choices
- Comfort with data-informed iteration

**Craft & Versatility**
- High-quality portfolio across mediums
- Brand + product + UI/UX breadth
- Understands technical constraints

**Early-Stage Fit**
- Comfort with lo-fi to hi-fi range
- Can design and implement (code/no-code)
- Experience defining design systems from scratch

---

#### 7.3 For Founding PMs

**Strategic Product Sense**
- Clear product narratives in past work
- Understanding of market positioning
- Data-driven prioritization examples

**Scrappiness**
- Built MVPs with minimal resources
- Learned to code/design enough to be dangerous
- User research without formal research team

**Commercial Awareness**
- Revenue/growth impact demonstrated
- Understanding of unit economics
- Pricing and go-to-market experience

---

## Usage Examples

### Example 1: Founding Engineer Rubric (Startup Employee #1)

**Criteria Groups**:
1. Technical Skills (40%)
   - Core Technical Competency (50%) - dealbreaker if <6/10
   - System Design (30%)
   - Code Quality (20%)

2. Startup Fit (30%)
   - Startup Mindset (50%)
   - Ownership & Initiative (30%)
   - Adaptability (20%)

3. Authenticity & Culture (20%)
   - Authenticity (40%)
   - Mission Alignment (30%)
   - Intrinsic Motivation (30%)

4. Experience (10%)
   - Impact & Results (60%)
   - Relevant Experience Depth (40%) - must have 2+ years

**Thresholds**:
- Reject: <50
- Review: 50-70
- Interview: 70-85
- Finalist: >85

---

### Example 2: Senior Product Designer (Startup Employee #2)

**Criteria Groups**:
1. Design Craft (35%)
   - Portfolio Quality (40%)
   - Product Thinking (35%)
   - Versatility (25%)

2. Collaboration & Communication (25%)
   - Communication Clarity (40%)
   - Collaboration (35%)
   - Stakeholder Management (25%)

3. Startup Fit (20%)
   - Startup Mindset (50%)
   - Adaptability (30%)
   - Ownership (20%)

4. Authenticity & Motivation (20%)
   - Authenticity (35%)
   - Mission Alignment (35%)
   - Intrinsic Motivation (30%)

**Thresholds**:
- Reject: <55
- Review: 55-72
- Interview: 72-88
- Finalist: >88

---

## Notes

- **Weights must sum to 1.0** at each level (group weights, criterion weights within groups)
- **Start with library defaults**, customize per role
- **3-5 criteria groups** optimal (more = complexity without precision)
- **Dealbreakers should be rare** - only for true must-haves
- **Multi-perspective scoring** catches blind spots single evaluators miss
- **Authenticity is critical** - bad signal if AI-generated applications pass

---

## Maintenance

This library should be updated based on:
1. **Hiring outcomes** - which criteria predicted success?
2. **New signal types** - what patterns emerge across candidates?
3. **Role evolution** - what matters for new/emerging roles?
4. **Bias detection** - what criteria inadvertently discriminate?

Review quarterly, update semi-annually.

---

**Version History**:
- v1.0.0 (2025-10-22): Initial criteria library

**Related Files**:
- `file 'schemas/rubric.schema.json'` - Rubric structure
- `file 'schemas/candidate.schema.json'` - Candidate evaluation record
- `file 'scoring_weights.json'` - Default weight configurations
- `file 'examples/'` - Complete rubric examples
