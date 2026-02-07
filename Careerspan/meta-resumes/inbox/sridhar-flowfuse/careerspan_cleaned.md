---
created: 2026-01-30
last_edited: 2026-01-30
version: 1.0
provenance: pulse-sridhar-extract
---

# Shridhar Agarwal - Careerspan Intelligence Brief

## Overview
- **Recommendation:** Strong AI-focused fullstack candidate with standout backend/LLM integration and reliability patterns; recommend
- **Careerspan Score:** Not explicitly stated in source
- **Verdict:** Proceed ✓

## Elevator Pitch
You get a builder who reliably turns ambiguous AI ideas into production features under real constraints—bridging legacy sync backends with modern async protocols, inventing entity-based context to cut tokens by 60%, and adding a human-in-the-loop layer that made sensitive actions 100% correct. You also get someone who listens to users, translates fresh research into pragmatic pipelines, and ships measurable gains (+18% correctness, +27% recall) across domains—bringing the mix of product empathy, systems thinking, and delivery speed you need to bootstrap your AI foundation.

## Key Strengths
- Nine years of applied AI/ML delivery with a strong record of turning ideas into production features under real constraints
- Repeatedly integrated LLMs, RAG, embeddings, and vector search into user-facing systems and built robust backends around them
- Emphasizes reliability and safety with concrete mechanisms—FaithfulRAG to reduce hallucinations, human-in-the-loop approvals, guardrails/feedback loops, entity-based context to cut token use by ~60%
- Measures outcomes quantifiably (e.g., +18% correctness, 84% relevance, +27% recall, 97% schema adherence)
- End-to-end ownership (sole ML engineer; founder delivering 15+ client solutions; first data scientist in a finance org)
- Pragmatic problem solving and cross-functional alignment on success metrics

## Concerns / Weaknesses
- Limited explicit evidence of modern frontend implementation (e.g., React/Vue/TypeScript, UI state management, design-system integration) or direct ownership of complex UI/UX flows
- Formal privacy/security compliance experience (SOC 2/GDPR, audit artifacts, access controls, incident response) and concrete observability tooling (e.g., OpenTelemetry/Prometheus, SLOs/alerts, drift monitoring) are not stated
- Lighter on explicit async-first communication artifacts (RFCs, design docs) and formalized knowledge-sharing programs
- Profile is weighted toward backend/AI systems and architectural integration rather than classic fullstack UI depth and formal compliance/observability practice

## Work Experience

### Principal ML Engineer
**EclecticIQ**  
Jul 2024 - Present

Led all AI initiatives at EclecticIQ, overseeing projects from research adaptation through to production deployment. Spearheaded the design and implementation of a multi-stage pipeline to automate structured security report generation from large-scale unstructured data, despite significant infrastructure constraints like smaller LLMs, limited async support, and legacy systems. Led the six-month integration of a sophisticated AI assistant into the flagship product, architecting a modular, scalable solution that decoupled synchronous Flask backends from async AI protocols (MCP) and introduced innovative patterns like entity-based context and a custom Human-in-the-Loop approval system—reducing token usage by 60% and enabling robust enterprise workflows. Emphasized factual accuracy and transparency, partnering closely with product and sales to align solutions with analyst needs, which led to impactful, measurable results: 18% higher correctness, 84% prompt relevance, 27% better recall, and 97% schema adherence. Work on LangGraph, MCP server deployments, FaithfulRAG for cybersecurity, advanced summarization, Text-to-Lucene, scalable contextual search (100M+ entities), and SecureBERT 2.0 fine-tuning showcased strength in architectural innovation, constraint-driven problem solving, and high-stakes delivery across multidisciplinary teams.

### AI/ML Specialist
**Cambridge University Press And Assessment**  
Apr 2023 - Jun 2024

Built a Student Companion System leveraging retrieval-augmented generation (RAG) to enhance multimodal course Q&A, implement semantic search using vector databases, ensure agentic response verification, and support both quiz generation and pedagogical-style adaptation. Additionally, developed an Automatic Marking System that utilizes few-shot prompting to accurately score short answers—achieving around 85% accuracy—and to generate reasoning using chain-of-thought techniques.

### AI Consultant
**Ponderbot Analytics**  
Aug 2022 - Apr 2023

Founded and owned an AI-focused firm where I delivered end-to-end intelligent solutions for clients in travel, retail, marketing, and agriculture. Designed and built a travel recommendation chatbot that uses a personality-based quiz to suggest personalized destinations and activities. Created over 15 AI solutions for a marketing client, such as recommendation engines, customer retention tools, campaign targeting, and customer segmentation. Developed a grocery retail chatbot capable of providing real-time product information and answering customer queries accurately. Built a feed composition optimization system for cattle that used linear programming to balance nutritional requirements and reduce CO2 emissions.

### Senior Data Scientist
**Cyware Labs**  
Jul 2021 - Aug 2022

Served as the sole machine learning engineer, designing and building end-to-end ML products from the ground up. Developed a cybersecurity entity extraction model using spaCy, achieving approximately a 0.78 F1 score by integrating named entity recognition and sentence classification, and also explored BERT and Stanza alternatives. Created a multi-label classification system for identifying Tactics & Techniques using a custom ML pipeline with various logistic regression models. Built a Python/Django application to serve these ML models with multi-threaded inference to minimize latency, incorporating a feedback loop for ongoing model improvement. Engineered a Text-to-NoSQL system leveraging the pretrained PICARD model for Elasticsearch queries.

### Data Scientist
**Dell Technologies**  
Mar 2019 - Jun 2021

Was the first data scientist in the Finance Department, where I pioneered several impactful initiatives. Built a capacity planning system that used time-series forecasting to predict global resource needs for the next two quarters. Developed a table parsing system, leveraging deep learning models like Faster R-CNN and LSTM, to accurately extract structured data from purchase orders. Designed a highly accurate product matching system utilizing BERT and data augmentation techniques to match line items on purchase orders with quotes.

### Data Scientist
**SquareOne Insights Pvt Ltd**  
May 2017 - Feb 2019

Built a transactional anomaly detection system in Scala that leveraged rule-based statistical models to return risk scores in under 300ms. Developed a credit risk model using Random Forest on Spark, achieving an F1 score of approximately 0.81.

### Software Engineer
**Loylty Rewards Pvt Ltd**  
Jun 2016 - May 2017

Responsible for upgrading SQL stored procedures from single-entry to double-entry (credit and debit) accounting. This migration project impacted the databases of 18 banking clients, supporting over 100 million users.

## Skill Assessments

### Hard Skills

**Prototype and productionize AI** - Rating: Advanced | Required: Advanced | Importance: 10/10  
> Our Take: The resume provides multiple clear, end-to-end examples of taking AI features from concept/prototype into production with attention to evaluation and operational hardening. Direct evidence: at EclecticIQ the candidate led full AI initiatives, architected and shipped an AI assistant into a flagship product (six-month integration), built modular backends (decoupled Flask sync from async MCP), deployed an MCP server, and added Human-in-the-Loop approval, guardrails, and feedback loops — explicitly reducing token usage (cost/latency control) and improving correctness/recall/schema adherence (measured success metrics).

**Develop AI features** - Rating: Advanced | Required: Advanced | Importance: 10/10  
> Our Take: The resume provides multiple clear, production-focused examples that match the responsibility. Direct evidence: at EclecticIQ the candidate led end-to-end AI initiatives, architected and deployed an AI assistant into a flagship product (multi-stage pipeline, Flask backends decoupled from async AI protocols, public MCP server), implemented Human-in-the-Loop approval, reduced token usage by 60%, and reported measurable improvements (accuracy, recall, prompt relevance, schema adherence).

**Stay Current with AI Trends** - Rating: Intermediate | Required: Intermediate | Importance: 5/10  
> Our Take: The resume contains multiple direct examples of tracking, evaluating, and adopting emerging AI/LLM tools and practices, and shows measurable outcomes from those choices. Examples: at EclecticIQ the candidate led AI initiatives "from research adaptation to production," adopted LangGraph and MCP frameworks, enabled dual LLM support (OpenAI + open-source via Ollama), extended FaithfulRAG to reduce hallucinations, and deployed a public MCP server — all indicate active evaluation and productionization of recent AI tooling.

**Integrate LLM APIs** - Rating: Advanced | Required: Advanced | Importance: 10/10  
> Our Take: The resume provides multiple, concrete examples of integrating LLMs and external AI services into production products—not just experiments. At EclecticIQ the candidate: built an AI assistant using LangGraph and MCP frameworks, deployed a public MCP server for third-party AI clients, enabled dual LLM support (OpenAI and hosted open-source models via Ollama), and implemented FaithfulRAG and guardrails to reduce hallucinations.

**Design for operational constraints** - Rating: Advanced | Required: Advanced | Importance: 9/10  
> Our Take: The resume provides multiple direct, production-first examples showing the candidate designed AI systems while explicitly addressing AI-specific failure modes, latency, cost, and operational concerns. Key evidence: (1) EclecticIQ (Principal ML Engineer) — led end-to-end AI integration under infrastructure constraints, implemented FaithfulRAG and guardrails to reduce hallucinations, built a Human-in-the-Loop approval system (operational/fallback), decoupled synchronous Flask backends from async AI protocols (architectural decision to manage latency/availability), and reduced token usage by 60% (direct cost optimization).

**AI Technical Debt Management** - Rating: Advanced | Required: Advanced | Importance: 7/10  
> Our Take: The story demonstrates that the candidate proactively identified maintainability and scalability challenges in a real-world, AI-powered production system. The candidate led a shift from a monolithic, prototype-like implementation to a modular three-service architecture, which decoupled dependencies and addressed long-term maintainability and scalability concerns.

**Collaborate cross-functionally** - Rating: Advanced | Required: Advanced | Importance: 9/10  
> Our Take: The resume contains multiple clear, concrete examples of scoping and delivering AI-driven, product-facing solutions in collaboration with non-research stakeholders. At EclecticIQ the candidate explicitly led all AI initiatives, oversaw feature scoping, success metrics, and deliverables, partnered closely with Product and Sales to align solutions, and drove the six-month integration of an AI assistant into the flagship product — delivering measurable business metrics (18% higher correctness, 84% prompt relevance, 27% better recall, 97% schema adherence).

**Build AI capability patterns** - Rating: Advanced | Required: Advanced | Importance: 8/10  
> Our Take: The resume provides direct, concrete evidence that the candidate has created patterns, guardrails, and reusable components to enable other engineers and scale AI features. The Principal ML Engineer role at EclecticIQ explicitly describes architecting a modular, decoupled AI assistant (separating synchronous Flask backends from async AI protocols), introducing entity-based context and a Human-in-the-Loop approval system, and building guardrails/feedback loops (Text-to-Lucene with guardrails).

**User Feedback Integration** - Rating: Intermediate | Required: Intermediate | Importance: 7/10  
> Our Take: The resume contains multiple direct indicators that the candidate has run feedback-driven, iterative improvement cycles for AI features used by real users. Explicit evidence: at EclecticIQ they built a custom Human-in-the-Loop approval system, described "feedback looping," and state they partnered closely with Product and Sales to align solutions with analyst needs—producing measurable improvements (e.g., 18% higher correctness, 84% prompt relevance, 27% better recall, 97% schema adherence).

**Contribute to fullstack work** - Rating: Intermediate | Required: Intermediate | Importance: 6/10  
> Our Take: Resume contains multiple concrete examples of stepping beyond pure ML research into full-stack and general engineering work: Built Python/Django application to serve ML models with multi-threaded inference and feedback loops (explicit web/backend application development and production serving). Upgraded SQL stored procedures and migrated databases for 18 banking clients (classic backend/data engineering at scale, 100M+ users).

**Deliver end-to-end solutions** - Rating: Advanced | Required: Advanced | Importance: 10/10  
> Our Take: Summary judgment: The resume provides solid evidence that the candidate has repeatedly owned end-to-end AI product deliveries (design > implementation > deployment) across backend and AI components and has integrated those into user-facing products. Concrete examples: Cyware: built an end-to-end ML product and a Python/Django application to serve models with multi-threaded inference and a feedback loop (production-serving, backend + model integration).

**Ensure feature reliability** - Rating: Advanced | Required: Advanced | Importance: 10/10  
> Our Take: The resume contains multiple, concrete examples of building and operating AI systems with production-facing reliability, latency, and fallback considerations. Relevant evidence: (1) Transactional anomaly detection returned risk scores under 300ms (SquareOne) — direct work on low-latency, predictable inference. (2) Built a Python/Django service with multi-threaded inference to reduce latency and included a feedback loop for retraining (Cyware) — shows operationalization and iterative observability.

**Onboarding and Mentoring** - Rating: Advanced | Required: Advanced | Importance: 6/10  
> Our Take: Resume shows repeated leadership and knowledge-transfer responsibilities but lacks an explicit statement of formal onboarding or training activities. Evidence: led all AI initiatives and technical efforts for a team of 8+ PhD researchers at EclecticIQ (overseeing feature scoping, success metrics, deliverables, and guiding domain & technical execution), introduced new architectural patterns (entity-based context, Human-in-the-Loop, decoupled async patterns) and deployed shared infra (public MCP server) — all activities that typically require teaching peers, documenting patterns, and enabling others to adopt them.

**Build backend/frontend workflows** - Rating: Advanced | Required: Advanced | Importance: 10/10  
> Our Take: The resume provides strong, concrete evidence of building and operating production backend services that power AI workflows: e.g., a Scala transactional scoring system with <300ms latency, a Python/Django multi-threaded model-serving app with a feedback loop, Flask backends decoupled from async AI protocols (MCP), a public MCP server, Text-to-Lucene and ES-based contextual search (100M+ entities), and multiple RAG/LLM integrations (FaithfulRAG, vector DBs, few-shot prompting).

**Share applied AI practices** - Rating: Advanced | Required: Advanced | Importance: 6/10  
> Our Take: Evidence for knowledge-sharing and codifying AI best practices is present but indirect. Strong signals: as Principal ML Engineer at EclecticIQ Shridhar led all AI initiatives, 'oversaw feature scoping, success metrics, deliverables, and guide[d] both domain and technical execution' for an 8+ PhD researcher team, architected reusable patterns (entity-based context, Human-in-the-Loop, modular decoupling), deployed a public MCP server (supporting third-party clients), and introduced guardrails/feedback loops and Text-to-Lucene/multi-index RAG patterns.

**Ensure privacy and security** - Rating: Advanced | Required: Advanced | Importance: 8/10  
> Our Take: Evidence supporting capability (transferable): The candidate has multiple roles working in security-sensitive domains and delivered technical controls that map to privacy/security responsibilities. At EclecticIQ and Cyware they led/owned AI for cybersecurity products (SecureBERT fine-tuning, FaithfulRAG, entity-based context, human-in-the-loop approval, guardrails, feedback loops, reduced hallucinations, schema adherence, enterprise workflows, contextual search for 100M+ entities) — these show design-for-trust, mitigation of model hallucinations, and operational controls typical in secure AI deployments.

### Soft Skills

**Attention to detail** - Rating: Advanced | Required: Advanced | Importance: 8/10  
> Our Take: The story provides strong, direct evidence of attention to detail. The candidate describes handling mission-critical, high-risk requirements (zero tolerance for hallucinations, reports critical to security analysts) and takes numerous, deliberate, technical actions explicitly aimed at ensuring factual accuracy, correctness, and trust in the output. Key actions that indicate advanced attention to detail include: 1) implementing multi-stage context reduction to retain only high-signal information, 2) using hybrid selection methods (vector and centroid similarity) to maximize thematic coherence, 3) aligning model outputs with verified, retrievable knowledge to avoid drift or hallucination, 4) engineering rigorous traceability systems so every claim is backed by a source reference, and 5) achieving high scores in correctness, relevance, and schema adherence (all measured).

**Problem-solving** - Rating: Advanced | Required: Advanced | Importance: 8/10  
> Our Take: Alignment to skill: Problem-solving for FlowFuse requires identifying ambiguous, cross-stack technical challenges in applied AI, scoping them, choosing tradeoffs, and delivering reliable production solutions. Shridhar's resume contains multiple STAR-like examples showing exactly this pattern.

**Pragmatism** - Rating: Advanced | Required: Advanced | Importance: 7/10  
> Our Take: The resume repeatedly shows pragmatic, delivery-focused decision making across backend, frontend, and AI components. Concrete examples: choosing rule-based statistical models in Scala to return transaction risk scores under 300ms (performance-driven tradeoff); using Random Forest on Spark for a credit-risk model (practical, scalable model choice); building multi-threaded inference and low-latency services as the sole ML engineer; upgrading SQL procedures for a large banking migration (practical correctness and impact); and founding a consultancy delivering 15+ client solutions (client-driven, outcome-focused work).

**Adaptability** - Rating: Advanced | Required: Advanced | Importance: 6/10  
> Our Take: This story convincingly demonstrates direct, advanced-level adaptability in a highly relevant technical environment. The candidate describes not just responding to changing requirements and technology constraints, but proactively driving iterative architectural changes in response to customer needs (e.g., transitioning from a monolithic assistant to a distributed, three-service architecture as new demands for interoperability appeared).

**System-level thinking** - Rating: Intermediate | Required: Intermediate | Importance: 8/10  
> Our Take: Alignment to skill: System-level thinking requires understanding interdependent components, making architecture tradeoffs (reliability, cost, security, UX), and designing solutions that consider downstream effects. The resume includes multiple examples where the candidate designed multi-stage pipelines, architectural patterns, and operational controls rather than isolated features.

## Education

**B-Tech, Mechanical Engineering**  
Indian Institute of Technology - Kanpur  
Jun 2012 - May 2016

**Class 12th**  
John Milton Senior Secondary School - Agra  
Mar 2011 - Mar 2012

**Class 10th**  
The Scindia School - Gwalior  
Mar 2009 - Mar 2010

---

**Note:** Candidate attained minor in MBA with coursework in Accounting & Finance during undergraduate studies.

## Awards & Achievements

### Academic Excellence
- Secured AIR 884 in JEE among 20 lakh+ candidates (99.5+ percentile)
- CBSE topper in Mathematics (Class 12th)
- Scored overall 92.1% in Class 12th
- Scored overall grade point of 9.8/10 in Class 10th
- Awarded merit scholarship for 4 years (Class 10th)

### Leadership & Campus Involvement
- Elected student senator
- Worked as student guide to freshers
- Managed events in cultural/tech fests
- Raised funds as marketing coordinator

### Professional Impact
- Led 6-month integration of AI assistant into flagship product
- Reduced token usage by 60% in enterprise workflow
- Delivered 18% higher correctness, 84% prompt relevance, 27% better recall, 97% schema adherence
- Built Student Companion System for multimodal course Q&A, quiz generation, and adaptation
- Developed Automatic Marking System (85% scoring accuracy)
- First data scientist in Dell Finance Dept.
- Built a capacity planning system for global resource prediction
- Developed high-accuracy table parsing and product matching systems
- Pioneered ML solutions for various industries as AI consultant

---

*Document generated from OCR source on 2026-01-29*