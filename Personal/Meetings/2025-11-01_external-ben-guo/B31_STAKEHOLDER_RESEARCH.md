# STAKEHOLDER_RESEARCH

---
**Feedback**: - [ ] Useful
---

**Perspective:** Speaking as Zo Computer core team member / AI product builder

## Landscape Insights

### 1. LLMs Don't Naturally Recognize When They ARE the LLM
**Evidence:** "Yeah. So I guess some of the stuff they're trying to get Zo to do, it will kind of act like it has to call like the OpenAI API or something... I think like right now the best approach really is just like very specific prompting about it."

**Why it matters:** Training data bias causes LLMs to default to external API calls because most products in training data aren't themselves LLMs - this creates architectural confusion for AI-native products that must teach users when to leverage internal intelligence vs. external tools.

**Signal strength:** ● ● ● ● ○  
**Category:** Product Strategy  
**Domain credibility:** ● ● ● ● ● (Ben is core Zo team, deals with this daily)

**Source Credibility:**
- Stakeholder: Ben Guo → Link to B08
- Relevant experience: Core Zo Computer engineer, directly implements LLM tool calling and prompt engineering
- Source type: PRIMARY - Firsthand operational experience building AI-native OS
- Firsthand? Yes - Ben experiences this behavior daily in Zo development
- Weight justification: Very high weight - this is direct product development insight from someone solving the problem in production

### 2. The Spectrum from Squishy LLM Mode to Deterministic Scripts Is A Core Design Pattern
**Evidence:** "I think like essentially like you're kind of trying to like create like an organizational system using like files and folders where there might be like kind of other ways to represent the same information that might be like kind of easier to manage... I think like over time or like maybe it's kind of depending on what I'm doing, like I will like gravitate towards like kind of maximum determinism because it just like is more stable and easy to manage."

**Why it matters:** Power users should consciously move systems from exploration mode (markdown files, natural language) toward production mode (scripts, databases) as they mature - treating this as a spectrum rather than binary choice enables smoother evolution and helps users understand when each approach fits.

**Signal strength:** ● ● ● ● ○  
**Category:** Product Strategy  
**Domain credibility:** ● ● ● ● ● (Ben has extensive experience with both modes)

**Source Credibility:**
- Stakeholder: Ben Guo → Link to B08
- Relevant experience: Power Zo user, observes patterns across user base, builds workflows himself
- Source type: PRIMARY - Direct experience with trade-offs between approaches
- Firsthand? Yes - Ben personally navigates this spectrum in his own work
- Weight justification: Very high - this is synthesized pattern from real usage, not theoretical

### 3. YAML Beats JSON for LLM Generation Due to Syntax Simplicity
**Evidence:** "I find that YAML is like a little bit easier for LLMs to write a proper YAML... There's not so many like curly braces that it has to close and like quotes that it has to like reason about. There's like not as much syntax around it."

**Why it matters:** File format choice significantly impacts reliability of LLM-generated configs - fewer syntax requirements mean fewer generation errors, making YAML preferable for human-editable structured data despite JSON being more common in APIs.

**Signal strength:** ● ● ● ○ ○  
**Category:** Product Strategy  
**Domain credibility:** ● ● ● ● ○ (Ben has practical experience, possibly echoes community wisdom)

**Source Credibility:**
- Stakeholder: Ben Guo → Link to B08
- Relevant experience: Has observed LLM generation failures with JSON vs. YAML in practice
- Source type: PRIMARY - Direct observation of generation quality differences
- Firsthand? Yes - Ben has debugged malformed JSON vs. YAML from LLMs
- Weight justification: High - practical wisdom from production experience, though may also reflect community consensus

### 4. EdTech Has Money for Classes But Not Extraneous Tools - Embed in Curriculum to Win
**Evidence:** "One of the things I was trying to convey to her [Tiff] and part of the problem with selling to higher ed is they don't have any money... And the people that care about what you have to offer have no power generally... But the good thing about higher ed is one thing they always have money for is classes."

**Why it matters:** Higher ed GTM strategy should target professors willing to use tool in classes rather than selling to admin/career services - universities have dedicated budget for curriculum but not for peripheral tools, making class adoption the viable wedge despite lower individual transaction value.

**Signal strength:** ● ● ● ● ○  
**Category:** GTM & Distribution  
**Domain credibility:** ● ● ● ○ ○ (Vrijen speaking, not Ben, but Ben agreed)

**Source Credibility:**
- Stakeholder: Vrijen Attawar (insight generator, not Ben)
- Relevant experience: Vrijen spent a year doing GTM for Careerspan in higher ed, learned this lesson through painful experience
- Source type: PRIMARY - Direct go-to-market experience and budget discovery
- Firsthand? Yes - Vrijen personally tried selling to career services vs. embedding in classes
- Weight justification: High - hard-won GTM wisdom from actual sales cycles, though specific to career tech which may not perfectly translate to developer tools

### 5. Working With AI Is About "Surfing the Wave" Not Rule Application
**Evidence:** "Yeah, no, everything you're saying is very right. Like I think what you're saying really applies to working with any kind of like AI agentic system. And yeah, it's about like kind of surfing on the wave of its like..."

**Why it matters:** User education for AI products should emphasize building intuition and feel rather than memorizing rules - this represents fundamental shift in how humans interact with software, requiring different onboarding and documentation approaches that embrace emergence rather than determinism.

**Signal strength:** ● ● ● ● ○  
**Category:** Product Strategy  
**Domain credibility:** ● ● ● ● ● (Ben builds AI products, deeply understands this)

**Source Credibility:**
- Stakeholder: Ben Guo → Link to B08
- Relevant experience: Core team at AI-native company, observes user behavior, thinks about product philosophy
- Source type: PRIMARY - Direct experience onboarding users and building AI systems
- Firsthand? Yes - Ben sees how users succeed or fail with AI systems daily
- Weight justification: Very high - this is philosophical insight grounded in product development reality
