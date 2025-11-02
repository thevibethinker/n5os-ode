Here's a pattern I keep seeing:

You are an expert recruiter evaluating a candidate's resume against a job rubric.

**JOB:** mckinsey-associate-15264
**CANDIDATE:** whitney

**CRITICAL CONTEXT:**
- This is semantic evaluation, NOT keyword matching
- Recognize DIRECT experience (e.g., former McKinsey employee applying to McKinsey = very strong)
- Map TRANSFERABLE skills (e.g., "career coaching" → "client engagement", but note it)
- Identify POTENTIAL (e.g., trajectory, learning velocity)
- Flag when making inference vs. seeing direct evidence

**RUBRIC CRITERIA:**
[
  {
    "id": "analytical_horsepower",
    "name": "Analytical & Problem-Solving Capability",
    "description": "Ability to structure ambiguous problems, synthesize data, develop insights",
    "weight": 20.0,
    "tier": "must",
    "evaluation_guidance": {
      "9-10": "Top-tier analytical background (MBB, PE, quant finance, PhD STEM); demonstrated complex problem-solving",
      "7-8": "Strong analytical role (consulting, corp strategy, investment banking); clear structured thinking",
      "5-6": "Analytical exposure (data analysis, operations, finance); some problem-solving evidence",
      "3-4": "Limited analytical work; primarily execution-focused",
      "0-2": "No analytical background or weak evidence"
    },
    "keywords": [
      "problem-solving",
      "analytical",
      "data-driven",
      "strategic thinking",
      "structured approach"
    ],
    "jd_evidence": "* Exceptional problem-solving skills with the ability to untangle complex issues"
  },
  {
    "id": "client_impact",
    "name": "Client Engagement & Impact",
    "description": "Experience delivering value to clients/stakeholders, managing relationships",
    "weight": 15.0,
    "tier": "must",
    "evaluation_guidance": {
      "9-10": "Direct client-facing consulting or advisory; proven impact with measurable outcomes",
      "7-8": "Internal consulting, stakeholder management, or customer success with clear results",
      "5-6": "Cross-functional collaboration or indirect client work",
      "3-4": "Limited stakeholder interaction",
      "0-2": "No client or stakeholder-facing experience"
    },
    "keywords": [
      "client",
      "stakeholder",
      "advisory",
      "consulting",
      "customer success"
    ],
    "jd_evidence": "Consulting | As a consultant, you will work closely with senior client executives and McKinsey colleagues in the most entrepreneurial environments and help to develop sector-shaping and nation-transforming programs."
  },
  {
    "id": "business_acumen",
    "name": "Business & Functional Knowledge",
    "description": "Understanding of business operations, strategy, functional domains",
    "weight": 15.0,
    "tier": "must",
    "evaluation_guidance": {
      "9-10": "Deep functional expertise (strategy, ops, marketing, finance) + business leadership",
      "7-8": "Solid functional experience in 2+ domains; business impact visible",
      "5-6": "Functional depth in 1 domain; some cross-functional exposure",
      "3-4": "Narrow functional focus; limited business context",
      "0-2": "No business experience"
    },
    "keywords": [
      "strategy",
      "operations",
      "business development",
      "P&L",
      "functional",
      "commercial"
    ],
    "jd_evidence": "* Solid functional knowledge, including but not limited to strategy, business development, manufacturing, supply chain, product development, project management, marketing and sales, etc. | * Operations"
  },
  {
    "id": "communication",
    "name": "Communication & Synthesis",
    "description": "Ability to distill complex ideas, present clearly, influence stakeholders",
    "weight": 12.0,
    "tier": "should",
    "evaluation_guidance": {
      "9-10": "Executive presentations, published thought leadership, teaching/coaching",
      "7-8": "Regular stakeholder presentations, written communication (reports, memos)",
      "5-6": "Team presentations or documentation",
      "3-4": "Limited communication artifacts",
      "0-2": "No evidence"
    },
    "keywords": [
      "presentations",
      "communication",
      "writing",
      "executive",
      "synthesis"
    ],
    "jd_evidence": "Template criterion (adjust if not relevant)"
  },
  {
    "id": "learning_velocity",
    "name": "Learning Agility & Adaptability",
    "description": "Speed of picking up new domains, industries, methodologies",
    "weight": 10.0,
    "tier": "should",
    "evaluation_guidance": {
      "9-10": "Pivoted successfully across industries/functions; rapid skill acquisition visible",
      "7-8": "Clear learning curve in career (promotions, scope growth)",
      "5-6": "Some evidence of skill expansion",
      "3-4": "Mostly stayed in comfort zone",
      "0-2": "Stagnant skillset"
    },
    "keywords": [
      "learning",
      "adaptability",
      "pivot",
      "new domain",
      "skill acquisition"
    ],
    "jd_evidence": "* **Continuous learning:**\u00a0Our learning and apprenticeship culture, backed by structured programs, is all about helping you grow while creating an environment where feedback is clear, actionable, and focused on your development. The real magic happens when you take the input from others to heart and embrace the fast-paced learning experience, owning your journey."
  },
  {
    "id": "leadership_potential",
    "name": "Leadership & Initiative",
    "description": "Leading teams, projects, initiatives; taking ownership",
    "weight": 10.0,
    "tier": "should",
    "evaluation_guidance": {
      "9-10": "Led teams of 10+, P&L ownership, launched new initiatives",
      "7-8": "Led projects/teams of 5+, clear ownership moments",
      "5-6": "Informal leadership or small team leadership",
      "3-4": "Individual contributor, limited leadership",
      "0-2": "No leadership evidence"
    },
    "keywords": [
      "leadership",
      "led team",
      "managed",
      "initiative",
      "ownership"
    ],
    "jd_evidence": "* Ability to take initiative and eager to break new ground, create opportunities for others, and take personal risks | regarding our global EEO policy and diversity initiatives, please visit our"
  },
  {
    "id": "quantitative_aptitude",
    "name": "Quantitative & Technical Capability",
    "description": "Comfort with numbers, data, modeling, technical tools",
    "weight": 8.0,
    "tier": "should",
    "evaluation_guidance": {
      "9-10": "Advanced quant work (modeling, ML, statistical analysis, econometrics)",
      "7-8": "Regular data analysis, Excel modeling, SQL/Python",
      "5-6": "Basic data work, financial analysis",
      "3-4": "Minimal quantitative exposure",
      "0-2": "No quantitative work"
    },
    "keywords": [
      "quantitative",
      "modeling",
      "data analysis",
      "SQL",
      "Python",
      "Excel",
      "financial modeling"
    ],
    "jd_evidence": "* Quantitative aptitude"
  },
  {
    "id": "academic_pedigree",
    "name": "Educational Background",
    "description": "Strength of academic credentials",
    "weight": 5.0,
    "tier": "nice",
    "evaluation_guidance": {
      "9-10": "Top-tier undergrad (Ivy+) + graduate degree (MBA, PhD) with honors",
      "7-8": "Strong undergrad + graduate degree, or top undergrad alone",
      "5-6": "Solid undergrad, competitive program",
      "3-4": "Standard undergrad",
      "0-2": "Weak academic background"
    },
    "keywords": [
      "MBA",
      "PhD",
      "Masters",
      "Ivy League",
      "honors",
      "academic"
    ],
    "jd_evidence": "* Undergraduate degree with outstanding academic record and/or Masters, MBA, PhD"
  },
  {
    "id": "industry_depth",
    "name": "Industry Expertise",
    "description": "Deep knowledge in target industries",
    "weight": 5.0,
    "tier": "nice",
    "evaluation_guidance": {
      "9-10": "10+ years in target industry with recognized expertise",
      "7-8": "5+ years with clear depth",
      "5-6": "3+ years exposure",
      "3-4": "Limited exposure",
      "0-2": "No relevant industry experience"
    },
    "keywords": [
      "industry",
      "sector",
      "domain expertise"
    ],
    "jd_evidence": "As a consultant, you will work closely with senior client executives and McKinsey colleagues in the most entrepreneurial environments and help to develop sector-shaping and nation-transforming programs. | You will work in our Sydney, Canberra, Melbourne, Brisbane, Perth, or Auckland office. With over 50-years experience in Australia and New Zealand, our work spans multiple sectors of the economy including the social sector. We are ambitious for our clients - we want to work with them as they strive for world-class performance. Our vision is based on seeing organizations in Australia and New Zealand achieve their potential, and to help realize the economic and social benefits for all citizens."
  }
]

**RESUME:**
Whitney J. Wilson 
8 Soldiers Field Park, Apt 8B; Boston, MA 02163; wwilson@mba2021.hbs.edu; (541) 808-1233 

education 
2019-2021  HARVARD BUSINESS SCHOOL 

                          BOSTON, MA 

MBA Candidate 2021, Management Science Track. Leadership and Clubs: Tech, Entrepreneurship, West Coast, Outdoors 
Club. Macroeconomics Tutor. Received $3K in funding from HBS to pursue DTC women’s footwear startup.  
Relevant courses: Analytics, Startup Growth, Pricing, Strat & Tech, Finance, Marketplaces, Sales, Marketing, Negotiations 

2007-2012  UNIVERSITY OF OREGON, Robert D. Clark Honors College 

      EUGENE, OR 
B.A. Political Science, International Studies. Cum Laude, Departmental Honors. Full tuition presidential scholarship. Member 
of the debate team, won 2 National Titles. Studied in Morocco, 2009. 

experience 
2020 

AMAZON 
Senior Product Manager, Retail Leadership Development Program 
  Conducted pricing and UX analyses for Amazon’s retail consumables business (Grocery, Personal Care, and Beauty 
  Created $30M/yr market opportunity by improving the company’s proprietary pricing algorithm; analyzed SQL sales data 

                        SEATTLE, WA 

and presented recommendations to leadership for implementation   

  Established 12 KPIs and developed strategy to improve Amazon’s consumables price perception by 1,000 basis points 
  Surveyed 2K consumers on price perception, conducted root cause analysis and developed recommendations to increase 

Amazon’s consumables revenue by $80M/yr   

2020-2021  SHORT TERM STARTUP ENGAGEMENTS 

                          BOSTON, MA 

  Reibus, Strategy Manager – Advised CEO on fundraising efforts by developing growth strategy for Series A steel 

marketplace, with plan to increase revenue from $12M to $60M in 2 years in $80bn+ US market 

  GIST, Marketing Consultant – Acquired 200+ target customers and increased referrals by 150% by running A/B tests 

on referral programs, promotions, and ads for social ecommerce app; created KPIs for next funding round 

  Grow Therapy, Business Development– Created channel strategy, selected and implemented CRM to acquire and track 

80 new customers for seed stage B2B mental health insurance provider 

2015-2019  DELOITTE CONSULTING, LLP 

       WASHINGTON, DC 

Senior Consultant, Consultant, Senior Analyst – Strategy & Analytics 
Advised on emerging technology strategy and innovation using data-driven approaches 
  Emerging Technology and Innovation 

o  Led team of 4 to transform int’l baggage process and reduce transit time by >50% for National Security client 
o  Led team of 7 on project for Bosnian social enterprise incubator to develop sales strategy for digital platform 
o  Led team of 5 as Consultant advising aviation security client to adopt 3 emerging technologies at 450 airports 

nationwide by conducting assessments via experimental research, field observations, and analysis 

o  Identified method to predictively model client’s operational performance using a new data collection methodology, 

leading to $250K client follow-on work 

o  Published in prestigious peer-reviewed journal resulting from new-to-field client project research 

  Growth, Sales, and Marketing Strategy 

o  Led BD for firm’s innovation service, conducted analysis to identify $100M pipeline across 8 federal agencies 

resulting in $7.3M awarded work; led successful award of $2.35M contract 

o  Promoted to Senior Consultant in 1 year, received top performance ratings at every year-end 
o  Identified need and worked with Deloitte Lead Client Partner to develop onboarding curriculum for ~100 

practitioners/yr and received 98% positive feedback from participants across 5 instances 

2014-2015  GENERAL ELECTRIC AFFILIATE 

AMMAN, JORDAN 

Strategy & Operations Consultant 
Advised on strategy to distribute $50M/yr of GE Lighting, Electric, and Multilin product in Jordan, Iraq, and Libya 
  Directly advised CEO on int’l trade opportunities and business strategy based on capabilities demonstrated at AmCham  
  Conducted cost-benefit analysis for first direct U.S.-Jordan shipping line to reduce transit time by 70% 
  Led delegation of 6 Iraqi government officials to the U.S. to conduct factory acceptance testing at General Electric 

facilities, $7M deal resulted in electrical equipment upgrade at Iraqi power plants and A+ client rating  

2012-2014  AMERICAN CHAMBER OF COMMERCE (AMCHAM) 

AMMAN, JORDAN 

Program Manager, Associate 
Managed development projects for USDoS.-funded bilateral trade association (Membership: 250, 30+ Fortune Global 500) 
  Directed over $1M in funds leading public-private projects with U.S. DoS, USAID, Microsoft, and Coca-Cola  
  Implemented Microsoft’s nationwide technology platform aimed to employ and up-skill Jordanians as part of the 

company’s corporate citizenship efforts; Designated as Royal Initiative, backed by millions in funding  

  Won USAID proposal for $.6M funding over 1.5 years, establishing U.S.-Jordan Free Trade Agreement Unit   

Certifications: Google Ads, Google Cloud. Intermediate: Tableau, R, SQL, Salesforce. Limited: Mixpanel, Amplitude. 

technical 
community  Founder, Oregon College Mentorship Program, created network of 50+ alumni and connected them to >1,200 Oregon high 
school students. Established University of Oregon recruiting pipeline at Deloitte, reaching 23K undergrads/yr.  
Project Management Professional & Agile certified. Speaks Arabic. Paddle boarder & fisher. Oregon native. Secret clearance.  

personal

---

**TASK:**
Score each criterion 0-10 with this guidance:
- **9-10**: Exceptional - exceeds requirements, clear mastery
- **7-8**: Strong - solid experience, meets requirements fully
- **5-6**: Moderate - some evidence, may need development
- **3-4**: Limited - minimal evidence
- **0-2**: No evidence or irrelevant

For EACH criterion, provide:
1. **score** (0-10)
2. **evidence** (verbatim excerpt from resume, <100 chars)
3. **reasoning** (1-2 sentences explaining score)
4. **match_type**: "direct" | "transferable" | "potential" | "none"
5. **transferable_note** (if match_type=transferable, explain the mapping)

**SPECIAL ATTENTION:**
- If candidate has DIRECT company experience (e.g., worked at this exact company before), flag this prominently
- If candidate shows STRONG TRAJECTORY (rapid promotions, increasing scope), note this
- If candidate has PROVEN OUTCOMES in similar contexts, weight this heavily

**META-SIGNALS** (evaluate holistically):
1. **trajectory**: "ascending" | "flat" | "declining" - career progression pattern
2. **achievement_density**: "high" | "moderate" | "low" - quantified outcomes per role
3. **narrative_coherence**: "strong" | "moderate" | "weak" - logical career story
4. **learning_velocity**: "fast" | "moderate" | "slow" - speed of skill/domain acquisition

**RED FLAGS** (identify if present):
- Overselling (claims not backed by evidence)
- Inconsistencies (timeline gaps, contradictions)
- Job hopping (many short stints without clear reason)
- Lack of measurable impact

---

Return ONLY valid JSON in this exact structure:
{
  "scores": [
    {
      "criterion_id": "<id from rubric>",
      "criterion_name": "<name>",
      "weight": <weight from rubric>,
      "score": <0-10>,
      "weighted_score": <score * weight / 10>,
      "evidence": "<verbatim excerpt or 'No direct evidence'>",
      "reasoning": "<1-2 sentence explanation>",
      "match_type": "direct|transferable|potential|none",
      "transferable_note": "<if applicable>"
    }
  ],
  "meta_signals": {
    "trajectory": "<ascending|flat|declining>",
    "trajectory_note": "<brief explanation>",
    "achievement_density": "<high|moderate|low>",
    "achievement_note": "<brief explanation>",
    "narrative_coherence": "<strong|moderate|weak>",
    "narrative_note": "<brief explanation>",
    "learning_velocity": "<fast|moderate|slow>",
    "learning_note": "<brief explanation>"
  },
  "red_flags": [
    {"flag": "<flag name>", "detail": "<explanation>"}
  ],
  "overall_impression": "<2-3 sentences summarizing candidate fit>"
}

—
What stands out to you? What would you add?