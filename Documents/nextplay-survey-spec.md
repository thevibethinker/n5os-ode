---
created: 2026-01-21
last_edited: 2026-01-21
version: 3
provenance: con_CDQZwhK7WBueZgnV
---
# Fundamentals of AI Productivity — Pre-Session Survey

**Purpose:** Gather data to present at session opening + meta-demo of Fillout → Zo dashboard

**Target:** 2-3 minute completion time | **Fully anonymous** | **Attendees only**

**Create in Fillout:** https://build.fillout.com

---

## Survey Questions

### SECTION: Who's In The Room (Open-Ended Demographics)

*Note: These are intentionally open-ended. We'll use LLM semantic clustering to group responses — no need for rigid dropdowns with <100 respondents.*

---

### Q1: What's your current role or title?

**Type:** Short text  
**Placeholder:** "e.g., Product Manager, Founder, Software Engineer, Marketing Director..."

**Analysis:** LLM clusters into role families (Product, Engineering, Design, Ops, Leadership, etc.)

---

### Q2: What function or department do you work in?

**Type:** Short text  
**Placeholder:** "e.g., Product, Sales, Engineering, Marketing, Operations, Consulting..."

**Analysis:** LLM clusters into functional areas

---

### Q3: How would you describe your seniority or career stage?

**Type:** Short text  
**Placeholder:** "e.g., Early career, Mid-level IC, Senior IC, Manager, Director, VP, Founder, Career changer..."

**Analysis:** LLM clusters into seniority bands (Early/Mid/Senior IC, Management, Executive, Founder)

---

### SECTION: Your AI Journey

---

### Q4: What's your biggest challenge with AI tools right now?

**Type:** Multiple choice (single select)  
**Options:**

- I don't know where to start
- I start but can't stick with it
- I get results but they're inconsistent
- I know the basics but can't level up
- I'm overwhelmed by all the options
- Other (free text)

**Visual:** Pie chart — "Here's what you're struggling with"

---

### Q5: How would you describe your current AI usage?

**Type:** Multiple choice (single select)  
**Options:**

- I rarely use AI tools
- I use ChatGPT occasionally for basic tasks
- I use AI regularly but feel like I'm just scratching the surface
- I use AI daily and have built some workflows
- I'm an advanced user looking to level up further

**Visual:** Horizontal bar chart or distribution — shows where the room sits

---

### Q6: How do you FEEL about AI right now?

**Type:** Slider or emoji scale (1-5)  
**Scale:**

- 1 = 😰 Anxious / Overwhelmed
- 2 = 🤔 Skeptical / Cautious
- 3 = 😐 Neutral / Curious
- 4 = 😊 Optimistic / Interested
- 5 = 🚀 Excited / All-in

**Visual:** Sentiment gauge / temperature meter — big visual impact, shows room's emotional state

---

### Q7: What would make this session valuable for you? (pick up to 2)

**Type:** Multiple choice (multi-select, max 2)  
**Options:**

- Simple tactics I can use immediately
- Understanding how to think about AI differently
- Seeing what's possible at an advanced level
- Getting templates/prompts I can copy
- Learning how to build my own system over time

**Visual:** Horizontal bar chart — shows what the room wants

---

### SECTION: Your Pain Points

---

### Q8: What are the most annoying repetitive tasks in your professional life?

**Type:** Short text  
**Placeholder:** "e.g., summarizing meeting notes, formatting reports, scheduling follow-ups, organizing files..."

**Visual:** Word cloud or grouped themes — we can read highlights aloud

**Analysis:** LLM extracts themes and clusters similar pain points

---

### Q9: How much time per week do you estimate you spend on repetitive computer tasks?

**Type:** Multiple choice (single select)  
**Options:**

- Less than 1 hour
- 1-3 hours
- 3-5 hours
- 5-10 hours
- 10+ hours
- No idea

**Visual:** Pie chart — "Look at how much time you're losing to repetitive work"

---

### Q10: What AI tools or features are you currently using? (select all that apply)

**Type:** Multiple choice (multi-select)  
**Options:**

- I do not regularly use AI tools or features
- I use AI features within traditional products e.g. Word, Adobe, etc.
- Consumer (Chatbot) AI: ChatGPT, Claude, Gemini, etc.
- Consumer (non-Chatbot) AI: Canva, Jasper, etc.
- AI Search: Perplexity, ChatGPT, Gemini, etc.
- Image/Video Gen: Midjourney, DALL-E, Sora, etc.
- B2B AI: Copilot, Harvey AI, Figma AI, etc.
- Agentic AI: Claude Code, Manus, Zo.computer, etc.
- IDE/ADEs: Cursor, Windsurf, Replit, etc.

**Visual:** Horizontal bar chart — shows tool landscape

---

## Dashboard Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 FUNDAMENTALS OF AI PRODUCTIVITY                             │
│  Pre-Session Survey Results • N responses                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👥 WHO'S IN THE ROOM (from Q1-Q3 semantic clusters)            │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ ROLES          FUNCTIONS        SENIORITY            │      │
│  │ Product  35%   Engineering 28%  Senior IC    32%     │      │
│  │ Eng      25%   Product     24%  Mid-level    28%     │      │
│  │ Founder  20%   Marketing   18%  Founder      20%     │      │
│  │ Ops      12%   Ops         15%  Manager      15%     │      │
│  │ Other     8%   Other       15%  Early         5%     │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
│  🎯 BIGGEST CHALLENGES           😊 ROOM SENTIMENT              │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │ [PIE CHART]         │         │ [GAUGE: 3.4/5]      │       │
│  │ "Can't level up" 34%│         │ "Curious but        │       │
│  │ "Inconsistent"   28%│         │  cautious"          │       │
│  └─────────────────────┘         └─────────────────────┘       │
│                                                                 │
│  ⏰ TIME LOST TO REPETITIVE TASKS                               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ <1hr ██ 12%                                          │      │
│  │ 1-3  ████████ 35%                                    │      │
│  │ 3-5  ██████ 28%                                      │      │
│  │ 5-10 ████ 18%                                        │      │
│  │ 10+  █ 7%                                            │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
│  🛠️ TOOLS YOU'RE USING           📋 WHAT YOU WANT              │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │ ChatGPT      ████ 78%│        │ Simple tactics ████ │       │
│  │ Claude       ██ 34%  │        │ Templates     ███   │       │
│  │ Perplexity   █ 23%   │        │ Advanced demo ██    │       │
│  └─────────────────────┘         └─────────────────────┘       │
│                                                                 │
│  💬 YOUR PAIN POINTS (themes from Q8)                          │
│  "meeting notes" • "email follow-ups" • "scheduling" •         │
│  "formatting reports" • "data entry"                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## LLM Semantic Clustering (for Q1, Q2, Q3, Q8)

For open-ended responses, the dashboard script will:

1. **Collect all responses** for the question
2. **Send to LLM** with prompt like:
   ```
   Cluster these job titles into 5-7 categories. Return JSON:
   {"clusters": [{"name": "Product", "count": 12, "examples": ["PM", "Product Manager", "Head of Product"]}]}
   ```
3. **Cache results** to avoid repeated API calls
4. **Display** as horizontal bar chart with category names

This gives us clean visuals from messy open-ended data without forcing respondents into predefined boxes.

---

## Survey Settings

- **Title:** "Fundamentals of AI Productivity — Quick Survey"
- **Description:** "Help us tailor Thursday's session to you. Takes ~2-3 minutes. Fully anonymous."
- **Completion message:** "Thanks! See you Thursday, Jan 29th at 12pm ET / 9am PT."
- **No email collection** — fully anonymous

---

## After Creation

1. Copy the form ID (looks like `foAdHjd1Duus`)
2. Share the public link with me
3. I'll configure:
   - Webhook to capture responses in real-time
   - Dashboard generator script with LLM clustering
   - HTML dashboard for screen sharing during session

---

## Webhook Setup (V does this in Fillout)

1. Go to form → Integrations → Webhooks
2. Add webhook URL: `https://fillout-webhook-va.zocomputer.io/webhooks/fillout`
3. Enable "Send on new submission"

---

## Question → Visual Mapping

| Question | Type | Visual | Dashboard Impact |
| --- | --- | --- | --- |
| Q1: Role/title | Open text → LLM cluster | Horizontal bars | High — "who's here" |
| Q2: Function | Open text → LLM cluster | Horizontal bars | High — "who's here" |
| Q3: Seniority | Open text → LLM cluster | Horizontal bars | High — "who's here" |
| Q4: Biggest challenge | Single select | Pie chart | High — "you're not alone" |
| Q5: Current usage | Single select | Distribution bar | Medium — calibrates room |
| Q6: Sentiment | Slider 1-5 | Gauge/thermometer | High — emotional hook |
| Q7: What you want | Multi-select (max 2) | Horizontal bars | Medium — sets expectations |
| Q8: Repetitive tasks | Open text → LLM themes | Word cloud / themes | High — specific pain points |
| Q9: Time lost | Single select | Pie chart | High — quantifies problem |
| Q10: Tools using | Multi-select | Horizontal bars | Medium — tool landscape |
