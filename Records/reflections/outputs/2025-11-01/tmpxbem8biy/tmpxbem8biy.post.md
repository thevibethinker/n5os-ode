Here's a pattern I keep seeing:

You are an expert recruiter evaluating a candidate's resume against a job rubric.

**JOB:** mckinsey-associate-15264
**CANDIDATE:** marla

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
María José Guerrero 
Cambridge, Massachusetts, 02138 
Contact: 
(857) 242-9324 
majoguerrerod@gmail.com 
majo_guerrero@harvard.edu 
LinkedIn: https://www.linkedin.com/in/majoguerrerodg/ 
Portfolio: https://sites.google.com/view/majoguerrero-portfolio/home 

Dedicated and knowledgeable Children's Librarian with experience in developing engaging 
library programs, promoting literacy, and fostering community engagement. Skilled in creating 
interactive learning experiences through storytelling, book discussions, and outreach programs 
tailored to diverse populations. Strong background in children's literature, reader’s advisory 
services, and digital resource instruction. Passionate about cultivating a love of reading and 
lifelong learning in young patrons while fostering inclusive and welcoming library spaces. 

●  Children’s Literacy & Programming: Expertise in planning and conducting story hours, 

book talks, craft programs, puppetry, and summer reading programs. 

●  Reader’s Advisory & Reference Services: Strong ability to assist children and 

caregivers in selecting appropriate books and learning resources. 

●  Library Collection Development: Experience managing children's book collections, 

selecting age-appropriate materials, and overseeing materials budgets. 

●  Community Engagement & Outreach: Proven success in building relationships with 

● 

schools, local agencies, and community partners to increase library access. 
Instruction & Digital Literacy: Skilled in teaching children and caregivers how to 
navigate online databases and research tools. 

●  Program Development & Budget Management: Ability to manage program funds and 

execute library initiatives within allocated resources. 

●  Collaboration & Staff Training: Experience mentoring and training staff to enhance 

library services. 

●  Diversity, Equity, and Inclusion (DEI): Commitment to creating inclusive library 

environments that serve diverse community needs. 

Harvard University – Harvard Graduate School of Education 
Master’s Degree: Learning Design, Innovation, and Technology (06/2022–05/2023) 
Certificate: Teaching Language and Culture, The Derek Bok Center for Teaching and Learning 
(04/2024) 

Universidad San Francisco de Quito, Ecuador 
Bachelor of Arts in Education, Minor in Psychology (08/2016–05/2020) 
Dissertation: Service-Learning Methodology Implementation in High School Curricula (adopted 
by the Ministry of Education during the COVID-19 pandemic). 

Children’s Literacy & Learning Program Manager 
Center on the Developing Child at Harvard University, Cambridge, MA (03/2024–Present) 

●  Develop and implement children’s literacy programs and storytelling initiatives. 
●  Facilitate book discussion groups and interactive reading programs for diverse 

audiences. 

●  Collaborate with schools and community organizations to expand library outreach 

services. 

●  Design age-appropriate learning resources and activities to enhance engagement. 

Children’s Library Program Coordinator & Spanish Language Instructor 
Harvard Faculty of Arts and Sciences, Harvard University, Cambridge, MA (08/2023–Present) 

●  Plan and conduct story hours, book talks, and early literacy workshops. 
●  Provide reader’s advisory services, guiding children and caregivers in book selection. 
●  Assist in developing the children’s book collection, ensuring diverse and inclusive 

representation. 

Project Assistant (Children’s Literacy & Outreach Focus) 
Project Zero, Harvard Graduate School of Education, Cambridge, MA (06/2023–05/2024) 

●  Supported early literacy initiatives, developing instructional materials for children’s 

programs. 

●  Assisted in program planning and outreach to schools and community groups. 
●  Provided research support for children’s literature programming and reader engagement. 

Content Developer (Internship – Storytelling & Children's Literature Focus) 
The Good Project at Project Zero, Harvard Graduate School of Education, Cambridge, MA 
(10/2022–05/2023) 

●  Designed interactive storytelling sessions to engage children in literary experiences. 
●  Created educational content focused on ethical literacy and reading comprehension. 
●  Assisted in curating reading lists and book recommendations for young readers. 

Research Assistant (Community Engagement & Early Literacy Initiatives) 
Learning Innovations Lab (LILA) at Project Zero, Harvard Graduate School of Education, 
Cambridge, MA (09/2022–06/2023) 

●  Conducted research on effective community-based literacy programs. 
●  Assisted in planning literacy events and developing outreach strategies for children’s 

services. 

Elementary Spanish & Literacy Teacher 
Colegio Americano de Quito, Ecuador (02/2021–07/2022) 

● 

Integrated literacy-rich instruction into language learning to support bilingual children’s 
literacy development. 

●  Designed and implemented library-based literacy initiatives, encouraging reading habits 

in young students. 

●  Developed inclusive and engaging literacy programming to support diverse learning 

needs. 

English & Science Teacher (Literacy & STEM Focus) 
Liceo Campoverde, Quito, Ecuador (08/2020–02/2021) 

●  Conducted literacy-driven science instruction, integrating reading and storytelling into 

science lessons. 

●  Designed interactive and hands-on reading activities to improve literacy comprehension. 

●  Teaching Language and Culture – The Derek Bok Center for Teaching and Learning 

(2024) 

●  Children’s Literature & Storytelling Workshop – Harvard Extension School (2023) 
●  Data-Driven Literacy Instruction – HarvardX (2023) 

●  Library Management Systems (Koha, Evergreen) 
●  Digital Literacy Instruction (Google Scholar, EBSCOhost) 
●  Literacy Program Development & Outreach 
●  Content Development Tools (Canva, Adobe InDesign) 
●  Assessment & Evaluation (Rubric Development, Data Analysis) 

●  English (Fluent) 
●  Spanish (Native)

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