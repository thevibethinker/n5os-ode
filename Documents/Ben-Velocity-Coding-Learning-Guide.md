# Velocity Coding: Play-by-Play Learning Guide
**First 10 Minutes Breakdown for V**  
**Video:** [Ben Guo - Velocity Coding](https://www.youtube.com/watch?v=Bw1FGnbS71g)

---

## Overview: What This Talk Is About

Ben is teaching **velocity coding** — his approach to building software with AI that's fast, intentional, and high-quality. He wrote 500,000 lines of code in 4 months building Zo Computer, spending $6k/month on AI tools. This isn't about "vibing" and letting AI do whatever — it's about **leveraged thinking**: using AI as a tool to amplify your strategic decisions while maintaining full ownership of the *what* and *why*.

**Key mental model:** Think of AI coding like having a career coaching team. You (the expert coach) set the strategy, diagnose the client's needs, and design the intervention. Your team executes the intake forms, schedules follow-ups, and drafts session notes. But *you* review everything, adjust the approach, and own the outcome. AI is your execution team — you're still the architect.

---

## Minute-by-Minute Breakdown

### 0:00-1:00 | The Setup: Vibe vs. Velocity

**What Ben says:**
- "Vibe coding" = letting AI write code without looking at it, trusting it blindly, getting mad when it fails
- He calls his approach "velocity coding" = using AI to move faster *intentionally*, not passively
- He spent $6k/month on AI at peak (still cheaper than a human engineer)

**Translation for you:**
Think of "vibe coding" like delegating a client intake to an assistant and never checking their work — just hoping they asked the right questions. When the client complains, you blame the assistant instead of fixing your process.

"Velocity coding" is like having a detailed intake template you designed, letting your assistant execute it, then reviewing their notes to spot gaps. The assistant handles the typing, but *you* own the quality.

**Why this matters:** AI can generate tons of output, but garbage-in = garbage-out. The leverage comes from YOUR strategic decisions, not from AI's raw output. You're the bottleneck (in a good way) — your thinking determines code quality.

---

### 1:00-2:01 | The Numbers: 500K Lines in 4 Months

**What Ben says:**
- Wrote 500,000 lines of code in 4-5 months
- Averaged 40,000 lines/week (way more than traditional coding)
- Some code was bad because he "didn't think hard enough" — but that's normal

**Translation for you:**
Imagine building N5 (your note system), Careerspan's entire client workflow, and your scheduling automation *all at once* in a few months. That's the scale.

The "bad code" admission is key: **volume ≠ quality**. Just like drafting 40 coaching session summaries in a week — some will need rewrites because you rushed the diagnosis phase. The speed lets you iterate faster, but you still need judgment.

**Analogy:** It's like when you prototype a new Careerspan feature. You build it fast to test the concept, learn what's wrong, then rebuild it properly. AI lets you prototype at industrial scale.

---

### 2:01-3:04 | What He Built: Zo Computer

**What Ben says:**
- Zo is an "AI cloud computer" (looks like an IDE but works with all file types)
- He can text it, email it, connect it to Google Calendar
- Example: He built an agent that scrapes his Twitter feed into a database so he can ask AI "what's on my feed?" instead of scrolling

**Translation for you:**
Zo is like if N5 lived in the cloud, could text you back, and had its own computer to run scripts. You could say "summarize my inbox" or "what meetings do I have this week?" and it handles the work.

The Twitter agent example is pure automation: instead of manually checking Twitter → reading tweets → synthesizing insights, he automated the pipeline. Now he just asks a question and gets the answer.

**Connection to your work:** This is the vision behind your N5 scripts. Instead of manually updating `file 'N5/lists/n5_todo.jsonl'`, you want automation that asks "what should I focus on today?" and gets an answer derived from your system.

---

### 3:04-4:05 | Core Principle #1: Simulation & Leverage

**What Ben says:**
- Building anything is about **simulation** (thinking through options without doing them) and **leverage** (finding ways to amplify effort)
- He's applied these principles since childhood (music, tinkering)
- Now looking for "new ways to simulate, new kinds of leverage"

**Translation for you:**
**Simulation** = mental modeling before execution. Like when you design a new career coaching framework: you map the client journey, anticipate failure points, iterate on the structure *before* running a pilot. You "simulate" the intervention in your head.

**Leverage** = force multipliers. Careerspan's templates are leverage — one good template serves 1,000 clients. N5's JSONL structure is leverage — consistent format lets scripts process any note the same way.

**With AI:** AI *is* the leverage. It turns your simulation (the plan) into working code. You still do the hard thinking (simulation), but AI handles the mechanical execution (typing 40,000 lines).

**Example from your world:** When you designed N5's modular architecture (`file 'Knowledge/architectural/architectural_principles.md'`), you *simulated* how notes → lists → indexes would flow. That thinking was the high-leverage decision. The scripts that implement it are just execution.

---

### 4:05-5:05 | What Slows You Down (The Hierarchy)

**What Ben says:**
Ben lists **three tiers of slowdown**:
1. **Doing the wrong thing** (choosing the wrong project/feature) — worst, wastes days
2. **Doing it the wrong way** (bad architecture/approach) — bites you later, causes rework
3. **Doing it badly** (sloppy execution) — creates bugs, low scalability

**Translation for you:**
**Tier 1:** Like deciding to build a LinkedIn job scraper for Careerspan when your clients actually need interview prep. Wrong problem = wasted effort.

**Tier 2:** Like building N5 with nested folders instead of tags + JSONL. It "works" but becomes unmaintainable. Bad structure compounds over time.

**Tier 3:** Like writing a script that works but crashes on edge cases (empty files, weird formats). Execution bugs slow you down with firefighting.

**The insight:** AI makes Tier 3 problems (execution) nearly free to fix. But it *cannot* fix Tier 1-2 (strategy/architecture). That's where your human judgment matters most.

**Implication:** Spend 80% of your energy on "what should I build?" and "how should it be structured?" — the thinking phase. AI handles the other 80% (typing).

---

### 5:05-6:06 | History: Old School Code Generation

**What Ben says:**
- Before AI, he built an inference platform and agent framework (also 500k lines, all by hand)
- Used "old school code generation" — templates and macros (metaprogramming)
- This still inspires him today

**Translation for you:**
**Templates/macros** = repeatable patterns that generate output. Like if you had a "session notes template" that auto-populated client name, date, and session goals — you fill in blanks, it generates the doc.

In programming, this looks like: "I need user login, admin login, and guest login" → write one template, generate three versions with slight variations.

**Why he mentions this:** AI is the *new* code generator. Instead of writing templates in code, you write templates in English (plans). AI fills in the blanks (generates code).

**Connection to you:** Your N5 schemas (`file 'N5/schemas/index.schema.json'`) are templates. Every note follows the schema structure. If you wanted to auto-generate notes, you'd use the schema as a template. Ben's doing the same thing, but with English descriptions instead of JSON schemas.

---

### 6:06-7:08 | What Code Generation Looks Like Now

**What Ben says:**
- 2025 codegen = "English documents that are still pretty technical"
- He calls them "plan files" — code mixed with English
- This is what he looks at now instead of raw code

**Translation for you:**
Instead of:
```python
def process_note(note_path):
    with open(note_path) as f:
        content = f.read()
    # ... 50 more lines
```

He writes:
```
PLAN: Process note file
1. Read note from path
2. Extract metadata (title, tags, date)
3. Validate against schema
4. If valid, add to index
5. If invalid, log error and skip

Error handling: Wrap in try/except, log to system log
Testing: Add test for empty file, malformed JSON
```

Then AI generates the Python code from the plan.

**Why this matters:** The plan is *human-readable strategy*. You can review it without needing to parse code syntax. It's like the difference between reading "Schedule client for Tuesday 2pm" vs. reading raw Google Calendar API calls.

**For you:** This is how you should think about your N5 scripts. The *plan* lives in `file 'N5/commands/'` or your architectural docs. The *implementation* is what Python does. You own the plan, AI handles the implementation.

---

### 7:08-8:09 | Lesson from 10 Years: Make It Work First

**What Ben says:**
- Quotes Kent Beck: "Make it work, then make it right, then make it fast"
- Don't worry about quality or performance until it works
- With AI, you can "make a ton of it work really fast, then worry about making it good"

**Translation for you:**
This is **prototype-first thinking**. Like when you test a new coaching technique:
1. Run it with one client (make it work)
2. Refine the process (make it right)
3. Scale it to 10 clients (make it fast)

You don't start by perfecting the technique for scale. You prove the concept, *then* optimize.

**With AI:** You can build the "make it work" version in hours instead of days. Test it, learn from it, throw it away if needed. The cost of experimentation drops to near-zero.

**Example:** Your `file 'N5/scripts/n5_ingest.py'` probably started as "just get notes into JSONL." Later you added validation, error handling, schema checks. That's "make it work → make it right."

**The trap:** Skipping step 1 (making it work) to obsess over perfection. AI *invites* this trap because generating code feels free. But if you're building the wrong thing, fast generation just creates fast garbage.

---

### 8:09-9:12 | Coding as Thinking + Flow State

**What Ben says:**
- "Coding is a form of thinking" — the code is instrumental to designing systems
- Good coding requires a "focused flow state"
- With AI, it's easy to lose flow, but done right, AI *increases* focus

**Translation for you:**
When you write (coaching frameworks, N5 documentation, Careerspan strategy), the *writing is thinking*. The document is a side effect — the real work is clarifying ideas.

Same with coding. The code is a side effect of designing the system. The thinking (what should this do? how should it connect to other parts?) is the real work.

**Flow state** = deep work. When you're writing a career transition framework and 2 hours vanish because you're fully immersed — that's flow.

**AI paradox:** AI *interrupts* flow (waiting for generation, reviewing output) but *also enables* flow (removes typing friction, lets you think at concept-level instead of syntax-level).

**Ben's solution (preview):** Focus your human brain on the hardest problem (the architecture, the strategy). Let AI handle a secondary task in parallel (generating boilerplate, writing tests). You review the secondary stuff later in a batch.

**For you:** When designing N5 workflows, you should be in flow on *the workflow logic* (what data flows where, what breaks if X fails). Let AI handle "write the Python that implements step 3." You stay in the strategic layer.

---

### 9:12-10:14 | The Secret: Focused Attention

**What Ben says:**
- "One weird trick": Focus your whole brain on the hardest problem + one other thing in parallel
- That's his whole workflow
- You review the parallel work later

**Translation for you:**
**Main thread (your focus):** Designing the architecture for Careerspan's new AI-powered career assessment tool. You're sketching the user flow, defining the data model, thinking through edge cases.

**Parallel thread (AI handles):** Generate the database schema, write the API endpoints, create test fixtures.

You stay locked on the hard problem (strategy). AI churns on the mechanical stuff (execution). When you finish the design, you review AI's output in batch, fix issues, move forward.

**Why this works:**
- Your brain doesn't context-switch between "design thinking" and "typing syntax"
- AI handles the low-leverage work (typing)
- You batch review instead of incremental review, which preserves flow

**Contrast with vibe coding:**
- Main thread: Waiting for AI to generate
- Parallel thread: Scrolling Twitter, context switching
- Result: No flow, shallow thinking, low-quality output

**For you:** When you're building N5 workflows, your main thread should be "what's the information architecture?" not "how do I write this Python loop?" The loop is AI territory. The architecture is yours.

---

## Key Themes from First 10 Minutes

### 1. **Leverage, Not Magic**
AI isn't doing the thinking for Ben. It's amplifying *his* thinking. He designs the system, AI types the code. Like you designing a coaching framework and having an assistant format it into a slide deck.

### 2. **Strategy > Execution**
The hierarchy of slowdown teaches: getting strategy right (what to build, how to structure it) matters 10x more than execution quality. AI makes execution nearly free, so your bottleneck becomes strategic clarity.

### 3. **Thinking Is Still the Bottleneck**
Even with AI generating 40k lines/week, Ben's output is limited by *how fast he can think through problems*. The typing isn't the constraint — the design decisions are.

### 4. **Plans Are the New Code**
Ben doesn't write code directly anymore. He writes plans (English descriptions of what the code should do), then AI generates code from the plan. The plan is the artifact he obsesses over.

### 5. **Flow State Is Critical**
AI can destroy flow (waiting, reviewing, context switching) or enhance it (removing friction, enabling concept-level thinking). The difference is *how* you use it.

---

## How This Applies to Your N5/Careerspan Work

### **N5 Architecture**
You've already done the high-leverage thinking: JSONL for notes, modular scripts, schemas for validation. That's the "simulation" phase (designing the system). Now AI can help you *execute* — write the Python that implements your design.

### **Careerspan Features**
When you design a new AI-powered feature (like resume analysis), your job is:
1. **Think:** What questions should it answer? What data does it need? How does it fit the user workflow?
2. **Plan:** "Input: PDF resume. Extract skills, experience, gaps. Compare to target role. Output: 3 improvement suggestions."
3. **Execute:** AI writes the PDF parser, the comparison logic, the output formatter.

You own steps 1-2 (strategy). AI handles step 3 (typing).

### **Learning to Code**
Your path forward:
- **Focus on:** System design, data modeling, workflow logic (the "plan")
- **Use AI for:** Syntax, boilerplate, implementation details (the "execution")
- **Review:** Always review AI's output, but at the *plan* level (does this match my intent?) not the *line-by-line* level (is this perfect Python?)

---

## Questions to Test Your Understanding

1. **Application:** If you wanted to add a new feature to N5 (auto-tag notes by topic), how would you split the work between "your thinking" and "AI execution"?

2. **Trade-offs:** Ben mentions "doing it the wrong way" bites you later. Can you identify a decision in N5's architecture that, if done differently, would have compounded into a maintenance nightmare?

3. **Leverage:** Ben says "simulation is better than doing." How does writing `file 'Knowledge/architectural/architectural_principles.md'` act as simulation for N5's future development?

---

## Next Steps

- Continue watching Ben's video with this guide alongside
- Notice how Ben's "think → plan → execute" maps to your N5 workflow design process
- Try applying this to your next N5 script: write a plan first (in English), then have me generate the code

---

**Timestamp:** 2025-10-26 13:21 ET
