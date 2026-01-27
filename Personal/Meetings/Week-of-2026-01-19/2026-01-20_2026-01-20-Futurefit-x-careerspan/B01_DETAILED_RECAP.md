---
created: 2026-01-27
last_edited: 2026-01-27
version: 1.0
provenance: con_Jc97WwrqOmaN77IU
---

# B01: Detailed Recap

## Meeting Overview
An introductory partnership discussion between Careerspan (Vrijen, Logan, Ilse) and FutureFit (Hamoon, Katya). The conversation explored potential acquisition/merger scenarios, with FutureFit indicating strong interest in bringing the Careerspan team aboard. The discussion covered Careerspan's product philosophy, technical approach, and team backgrounds, followed by FutureFit's transparent positioning about integration and deal-breaker exploration.

## Chronological Discussion

### Introductions and Careerspan Overview (0:00-15:00)
The meeting opened with team introductions. Hamoon from FutureFit set expectations for a 34-45 minute exploratory call. Vrijen provided Careerspan's background: he and Logan met 10.5 years ago working in college admissions and standardized test prep, focusing on narrative design. After Vrijen's MBA at McKinsey and Logan's edtech experience in Asia (Thailand, China, Singapore), they reunited to build Careerspan around the concept of using AI as a "smart mirror" to help people advocate for themselves.

**Key Points:**
- Careerspan has ~4,000 users with $0 in marketing spend
- 35% of users complete at least one story
- Median user spends 40-45 minutes in deep reflection with the AI
- Team: Vrijen (co-founder, MBA McKinsey), Logan (co-founder, edtech in Asia), Ilse (head of AI, joined 2.5 years ago)

**Interesting Details:**
- Vrijen emphasized job seekers are difficult to monetize ("reasons of the heart and reasons of the purse")
- The real value: Careerspan's data capture through coaching conversations creates "way better ATS data" than traditional approaches
- Ilse's joke about her role: "Poke the AI with a stick when it misbehaves"

### Ilse's Technical Background (15:00-25:00)
Hamoon asked about Ilse's career journey from project management to software engineering to data/AI. Ilse described falling into software engineering at her first job after college (math major hired by a company that "had really good luck hiring math majors"), learning Ruby on Rails when short-staffed during a $30M lawsuit with Morningstar. She worked on various industries including "wastewater heat mapping for fracking" (calling it "the most evil thing I've ever done"), then pursued her master's in data science before co-founding a company building automated software testing platforms using graph theory.

**Key Points:**
- Ilse values being "the dumbest person in the room" for learning
- Built financial software using behavioral techniques to increase 401k contributions
- Her last company raised $17M before she left during COVID
- Core philosophy: "using AI to do something that isn't evil is really good"

### Technical Deep-Dive on Job Description Analysis (25:00-35:00)
Hamoon asked about the best AI feature Ilse has built for Careerspan. Ilse described the job description breakdown system: parsing JDs into 10-12 soft skills, hard skills, and responsibilities (~30 items total), each with importance level and mastery requirements. She tracks which skills map to which responsibilities at what mastery levels.

**Decisions:**
- Using closed-source models (OpenAI) for this component
- No fine-tuned models needed for low-volume job descriptions
- Multi-shot LLM prompts exploded into parallel atomic LLM tasks

Vrijen added context: Ilse's standout engineering capability is atomizing tasks effectively to use cheaper models ("dumb models") rather than reflexively throwing the most powerful models at problems.

### Logan's Background and Interests (35:00-45:00)
Logan described his through line: "helping an individual find more agency and dealing with big systems" over 16+ years. He emphasized translating research-backed approaches into visceral, practical applications. Recent focus has been on where the job market is going, including learning in public and the dying resume signal.

**Key Points:**
- Spent majority of career in edtech in Asia (New Pathway Education, employee #3, scaled to 400+ employees)
- Studying Mandarin, postgraduate certificate in education, Master's in education and learning design
- Passionate about marketing across channels (LinkedIn, newsletter, TikTok) and translating frameworks into products

### FutureFit's Positioning and Deal Breakers Discussion (45:00-End)
Hamoon provided FutureFit context: team of 30+ people, end-to-end career services (exploration, training, wraparound supports, job connection), partners with state governments and industry groups across North America and Europe. **Critical positioning:** FutureFit does not do direct-to-consumer.

**Major Disclosure:**
Hamoon stated that in this scenario, the "likely path" would be welcoming the Careerspan team over to their side—essentially an acquisition. He was transparent that this "doesn't necessarily mean carrying on of the tech exactly as it exists today" but emphasized mission alignment.

He then explored deal breakers and frustration points:

**Vrijen's requirements:**
- Wants to stay in touch with tech, ideally through product-oriented role with AI exposure or external non-competitive pursuit
- **Non-negotiable:** Must sell the power of the UX they built—not just looking at it as technology. Believes Careerspan is "the best team in the market, bar none" at understanding candidate user experience and generating tangibly better data than resume parsing.

**Logan's preferences:**
- Wants to wear "mini hats" and contribute broadly
- **Deal breaker:** Being boxed into "you're doing this and only this"
- Enjoys being thrown in the deep end and adapting

The transcript cuts off mid-sentence during Logan's response.

## Key Takeaways

- **Acquisition signal:** FutureFit explicitly positioned this as a potential team acquisition scenario, stating "welcome you and the team over to our side" while noting the tech may not continue as-is
- **Product differentiation:** Careerspan's core value proposition is user experience design that generates superior candidate data through conversational reflection, not NLP/ML algorithms
- **Strong technical discipline:** Ilse's engineering philosophy prioritizes task atomization and cost efficiency over model power, enabling high-quality analysis at low compute cost
- **Cultural alignment:** Both teams emphasize mission-driven work helping people navigate career transitions and "better jobs faster and cheaper"
- **Business model alignment required:** FutureFit is B2B/B2G only (no DTC), which Vrijen acknowledged earlier as the monetization challenge for job seekers
- **Team integration risk:** Hamoon proactively surfaced the identity challenge of joining an existing organization with different brand/product, seeking to understand deal breakers upfront
- **NDA likely needed:** Technical discussions would require NDA before deeper dives (implied by Ilse's deferral on details)