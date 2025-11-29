---
created: 2025-11-25
last_edited: 2025-11-25
version: 1.0
---

# Business Context – Rice x Careerspan

## Careerspan

**Core problem**
- Hiring has shifted toward a paradigm where success often depends less on *capability* and more on how well candidates can *sell themselves*.
- Many strong candidates (especially first‑gen, lower‑income, non‑traditional backgrounds) lack the networks, language, and confidence to signal their value.
- AI is simultaneously disrupting jobs and reshaping hiring, raising the bar on articulation, not just competence.

**Solution**
- Careerspan is a story‑driven, AI‑assisted platform that:
  - Captures rich stories from candidates via audio‑first conversations.
  - Transcribes and structures those stories into resume‑ready bullets and a skills map.
  - Decomposes job descriptions into skills and compares them to a candidate’s story graph, surfacing gaps and opportunities.
  - Helps candidates prioritize where to invest effort ("fill in the gaps"), then reuse that work across many applications.

**Architecture & differentiation**
- Uses "off‑the‑shelf" frontier models (GPT‑class) plus Whisper for transcription.
- Differentiated by the "middle layer"—the Logan + V playbook for:
  - Asking the right questions.
  - Encouraging metacognition and self‑efficacy.
  - Structuring skills, gaps, and hiring signals.
- Intentionally keeps a human in the loop (no automatic final resume documents) to avoid over‑generic outputs and to force reflective choice.

**Hiring‑side value**
- Employers see candidates who have invested effort (2–3+ stories) and are filtered for BS/AI fakery.
- They get structured evidence of skills mapped directly to their job requirements.
- Careerspan can support a curated "one‑click apply" experience for high‑intent candidate pools (e.g., Rice engineering alums).

---

## Rice Engineering Alumni, SEE/CSE, and the Dean

**Rice Engineering Alumni (REA) & SEE/CSE**
- REA is a working board, not just an advisory group; SEE/CSE is a flagship program connecting students with internships.
- Felix and Jim want SEE/CSE to move from manual internship matchmaking toward teaching students to:
  - Find opportunities themselves.
  - Tell strong stories about their work.
  - Build durable self‑advocacy muscles.
- They also seek ways to maintain long‑term engagement with alums beyond graduation.

**Equity & access context**
- Many SEE/CSE students are first‑gen or from lower‑income backgrounds; their families often lack white‑collar professionals.
- They compete with peers who have stacked internships from high school onward.
- The board wants tools that close this gap without overwhelming volunteers or Career Services.

**Dean of Engineering & Computing**
- Frequently hears from parents: "What are my child’s job prospects?"
- Values SEE/CSE as a concrete answer but is looking for broader, durable strategies.
- Will likely be receptive to tools that:
  - Improve employment outcomes and resilience in an AI‑shaped market.
  - Reflect responsible, human‑centered use of AI.

---

## Fit Between Careerspan and Rice

**Where Careerspan aligns strongly**
- **Storytelling & reflection:** Gives students structured practice talking about their work, which SEE/CSE leaders already see as the main gap.
- **Skill signalling:** Makes implicit skills visible and linkable to jobs, addressing the "skill signalling" meta‑skill Logan highlighted.
- **Equity:** Lowers the writing barrier (audio‑first, multi‑language) and gives under‑networked students a way to compete on substance.
- **Alumni engagement:** Long‑term, story‑logging behavior supports ongoing touchpoints with alumni.

**Strategic opportunities**
1. **Pilots with SEE/CSE cohorts** – Integrated before/during/after internships.
2. **Rice‑specific alumni offer** – Promo code / link enabling low‑friction adoption.
3. **Rice companies ↔ Rice talent loop** – Employers post roles into Careerspan; Rice candidates with stories can be surfaced quickly.

**Risks / sensitivities**
- University bureaucracy and vendor processes are slow; attempting a top‑down rollout too early would likely stall.
- REA has not historically endorsed specific vendors; any move here must be carefully framed as experimental and value‑driven.
- AI skepticism (formatting, hallucinations, ethics) must be addressed head‑on; hence the emphasis on transparency and human‑in‑the‑loop design.

