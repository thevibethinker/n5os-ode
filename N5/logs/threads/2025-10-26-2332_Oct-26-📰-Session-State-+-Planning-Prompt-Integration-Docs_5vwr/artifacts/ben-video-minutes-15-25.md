# Velocity Coding: Minutes 15-25 Deep Dive
**The Planning Phase & Maintaining Craft**  
**Rich Supplementation Guide for V**

---

## Context: Where We Are

Ben has just finished explaining the foundational concepts (think, plan, execute). Now he's drilling into the **Planning phase** — the part where you write specifications that guide AI code generation. This is the core of velocity coding. The execution (actual code generation) becomes almost automatic if you plan well. This section teaches you HOW to plan intentionally and stay connected to your code's quality.

---

## The Shift in Thinking (15:22-16:30)

### What Ben Says
Ben moves to the Planning phase and immediately emphasizes that the most critical thing about planning is **not losing the "feel" for your code**. He talks about keeping craft high through what he calls "feel" — a visceral, human sense of whether code is good or weird.

### Why This Matters & What He Means

Here's where Ben is making a subtle but critical distinction that's worth unpacking:

**The Problem He's Trying to Solve:**

When you use AI for code generation, there's a real danger that emerges. You can end up like a factory supervisor who never looks at the shop floor. You issue commands ("build me authentication"), AI produces 500 lines of code, you review it quickly, and ship it. The code works. So you think you're winning.

But here's what's actually happening: over time, you become *disconnected* from the codebase. You don't *feel* the shape of it anymore. You don't notice when certain patterns start to smell off. You don't catch the subtle brittleness that emerges gradually. Code quality degrades not in dramatic ways, but in small, accumulating ways that you miss because you're not *reading* the code.

**What "Feel" Really Means:**

Ben uses the word "feel" somewhat poetically, but he's describing something very concrete: the aesthetic and ergonomic quality of code. Think about it like this:

- **Feel of reading code:** Does the code flow naturally as you scan it? Or do your eyes keep stopping at weird stuff?
- **Feel of modifying code:** When you need to change something, does the code make it easy or hard to find what you need to change?
- **Feel of naming:** Do variable and function names make sense and map to real concepts? Or do they feel like abbreviations that hide intent?
- **Feel of structure:** Do related things live together, or are they scattered?
- **Feel of density:** Does the code say a lot in a small space (good) or take up a lot of room to say a little (bad)?

This is what craftspeople call **taste** — an internalized sense of what good looks like in your domain.

**Why This Applies to You Specifically:**

As a career coach who's learning to build, you probably already know this intuition in your own domain. You can probably *feel* when a career conversation is going well versus when it's stuck. You can sense when someone's narrative is authentic versus performative. That's taste in action. 

Code taste works the same way: it's a pattern-recognition ability that develops only through *repeated exposure* and *active judgment*. You can't develop it by delegating. You develop it by reading code, building opinions about what's good and bad, then seeing the consequences of those choices over time.

**The Risk of AI Coding:**

The danger is that AI is so productive that you can build an enormous system without ever developing taste. It's like being a director who hires brilliant cinematographers and never learns to actually *see*. You ship beautiful work, but you can't defend it or evolve it because you don't actually understand it at the level of craft.

### Christopher Alexander Quote (16:24-16:35)

Ben references Christopher Alexander, an architect and design theorist. The idea is:

> There's a quality to good design that's hard to articulate but immediately recognizable when you see it.

Alexander spent decades trying to understand what makes spaces feel *right* — why some rooms are pleasant to be in and others aren't. He concluded that certain proportions, relationships, and details have a subtle rightness to them that goes beyond function.

The same is true in code. There are ways of organizing logic that feel right, even if they work the same functionally. A system where concepts are well-separated and named appropriately *feels* good to work in. A system where concerns are tangled and naming is inconsistent *feels* wrong even if the behavior is correct.

**How This Translates To You:**

In Careerspan, if you're using AI to generate features, you need to make sure you're still *reading* them and checking that they feel right. Does a user flow through the interface naturally? Does the structure of your data (how clients are organized, how sessions are tracked) make sense conceptually? These aren't purely functional questions — they're craft questions.

---

## Owning the Planning Process (16:35-18:30)

### What Ben Says

Ben is now directly addressing the temptation to outsource planning. He notices that various AI coding tools (Cursor, Kilobuild, CloudCode) are building "plan mode" UX — features where the AI *suggests* the plan and you approve it.

Ben's position is clear: **Don't do this.** Own the planning process yourself.

### Why This Is Critical

This is a pivotal insight, so let me expand it substantially:

**The Planning Process Generates Everything**

When you write a plan, you're not writing a document for AI. You're writing a document that *generates your entire codebase*. The plan is:
- The seed of all architectural decisions
- The source of truth for what the system should do
- The place where your intent lives
- The artifact you'll refer to when debugging something six months later

If you outsource this to AI, you're outsourcing *your entire strategy*.

**Why Outsourcing Planning Is Different from Outsourcing Code**

Here's the crucial distinction:

- **Outsourcing code generation** = "AI, given this plan, write the implementation" → This is fine. The plan is still *yours*.
- **Outsourcing planning** = "AI, tell me what to build" → This means an AI is deciding your architecture. Even if it's smart, it's *not aligned with your values and intent*.

When you look at a plan and think "yes, this is right," you're not thinking "this is correct." You're thinking "this matches how I want to organize this system." Those are different things.

**The Hidden Cost of Plan Outsourcing**

If you let AI plan and you approve the first thing that comes back, you're likely to end up with:
- Systems that are architecturally sound but not *yours*
- Features that work but don't reflect your judgment
- A codebase that feels foreign to you even though you wrote it
- Future developers (or you in 6 months) confused about *why* choices were made

This is particularly dangerous because it's *invisible*. The code works. The feature ships. You just gradually feel more and more disconnected from your own system.

**Applying This To Careerspan:**

When Ben talks about owning planning, he's saying: don't let Claude or ChatGPT tell you how to structure your career coaching platform. Don't let Cursor's plan mode generate your architecture. *You* need to think through:
- How should career data be modeled?
- What's the core workflow for a coaching session?
- How do assessments flow into development plans?
- What's your philosophy on data ownership and privacy?

These are *your* questions to answer. AI can help you execute them, but not decide them.

---

## How to Plan Intentionally (18:26-20:28)

### What Ben Says

Ben shifts to the tactical: *how* do you actually write good plans? His approach:

1. You create a plan
2. You iterate on it (don't take the first version AI produces)
3. You read it, think about it, sit on it
4. You spend real time obsessing over the plan — sometimes 30 minutes to an hour for a good one

Then he talks about the planning prompt — the instructions you give to AI to generate plans. He emphasizes this is a craft: you need to experiment with prompts until you get the style and depth you want.

### The Iterative Planning Cycle (18:26-19:00)

**First Pass ≠ Final Plan**

This deserves emphasis. When you ask AI to generate a plan, what comes back is a *draft*, not a specification. Ben's practice is:

1. **AI generates a plan** based on your request
2. **You read it carefully** — not skimming, but actually reading
3. **You think about it** — Does this make sense? Are there hidden issues? Would this be hard to maintain?
4. **You sit on it** — Sometimes Ben sleeps on big decisions. This gives your subconscious time to find problems.
5. **You propose alternatives** — "What if we did it this way instead?"
6. **You iterate** — Back to AI with your feedback: "I like part of this, but I think the authentication should work this way instead"

**Why This Takes Time**

A good plan might take 30 minutes to an hour. This seems slow. But remember: once the plan is solid, the code generation becomes mechanical. You're *not* iterating on code; you're iterating on design.

This is the big win of velocity coding: you move the cognitive effort to where it matters (planning) and reduce effort on the mechanical stuff (coding).

**Why It's Worth It:**

If you spend 45 minutes perfecting a plan and then code generation takes 10 minutes and works perfectly, that's a 10x win over the old way where you'd spend hours debugging generated code.

### The Planning Prompt (19:26-20:28)

**What's a Planning Prompt?**

A planning prompt is a meta-instruction you give to AI. It says: "When I ask you to generate a plan, here's how I want you to think about it, what format I want, what values you should optimize for."

**Ben's Approach**

Ben's planning prompt includes:
- **Format instructions:** "Describe code changes, be concise, highlight what's going on at the top, then go into more details"
- **Philosophical content:** Quotes from Rich Hickey and Christopher Alexander ("the Bible of our codebase," Ben calls it)
- **Style rules:** Things like "prefer simplicity," "avoid coupling," "make naming explicit"
- **Context:** Information about the codebase structure, conventions, patterns that have worked

**Why This Matters**

The planning prompt is the *origin* of your codebase. It's like the DNA. Everything that follows is generated from it. So Ben obsesses over it. He:
- Keeps it as a shared secret/reference document
- Iterates on it based on what works
- Treats it as sacred — the core specification of how *his* codebase should be

**For You:**

This is where your N5 design principles would live. Your planning prompt would say something like:
- "Prefer shell scripts over Python for glue; Python for complex logic"
- "Keep configs as human-readable JSONL"
- "Modular over monolithic; flexibility over convenience"
- "Explicit over implicit; say what you mean"

These aren't just preferences — they're the *shape* of your entire system.

**The Meta-Insight:**

What Ben is really saying is: **All your code is generated from your planning prompt and your plans.** So if you care about code quality, you don't care about code quality at the code level — you care about it at the prompt and plan level.

This is why he doesn't worry much about the actual code generation step. If the planning is right, the code is almost guaranteed to be right.

---

## The Role of "Feel" in Execution (15:22-16:30 Revisited More Deeply)

### The Craft Principle

Ben brings up "feel" at the start of the Planning section, and it's worth revisiting because it's fundamental to maintaining quality.

**Feel is Not Subjective**

When someone says "this code feels wrong," they're not being poetic. They're detecting patterns that their brain has learned but can't yet articulate. That's actually more reliable than explicit rules.

For example:
- You can *feel* when a function is too long (even if you don't know the "max 20 lines" rule)
- You can *feel* when naming is inconsistent
- You can *feel* when a module has too many responsibilities
- You can *feel* when you're about to change something and it'll ripple through the codebase

**This Only Develops Through Exposure**

The problem with AI is that it can skip the apprenticeship phase. You can ship production code on day one. That's powerful, but it means you can miss the development of taste.

In traditional programming, you spent years reading code, learning why certain patterns are stable and others are fragile. By the time you wrote production systems, you had internalized a lot of this.

With AI, you need to *deliberately* maintain that phase. This means:
- **Read your generated code.** Don't just review it for bugs; read it for structure.
- **Question it.** Why did AI organize it this way? Is there a better way?
- **Feel when something's off.** If a module feels janky, it probably is.
- **Invest time in refactoring.** Don't just let entropy accumulate.

---

## Model Selection & The Planning Prompt (20:28-21:30)

### What Ben Says

Ben mentions that the model you choose for planning affects the output. Different models have different "styles." He settles on:
- **GPT-5 Codeex** for planning (slow but high quality)
- **GPT-5 Fast** for code generation (quick execution)

### The Model-as-Flavor Concept

This is interesting: Ben is treating the model itself as part of the planning prompt. Different models produce different *feels*.

**Why Model Choice Matters**

Some models are:
- More verbose vs. concise
- More pragmatic vs. theoretical
- More exploratory vs. direct
- More likely to suggest trade-offs vs. just decide

For planning, Ben wants a slow, thoughtful model that explores options. For execution, he wants a fast, direct model that just does what the plan says.

This is another dimension of craftsmanship: knowing which tool (model) is right for which job.

**For You:**

When you build your planning and execution workflows, you'll probably want to experiment with:
- Claude for planning (known for thoughtfulness)
- GPT-4 for complex decisions (good at trade-off analysis)
- GPT-4o for quick execution (fast and reliable)

But the principle is: **choose the model that matches what you're trying to do.**

---

## Execution Phase (21:30-27:36)

### What Ben Says

Once the plan is solid, execution is "robotic" — just moving fast and not breaking things. The key insight: *if you've made a mistake in thinking or planning, it doesn't matter how you execute. It's already over.*

### Execution Is Not Where Quality Comes From

This is counterintuitive. Most people think of coding as execution — sitting down and writing clean code, testing it, etc.

Ben's position: **Execution is mechanical.** The quality comes from planning.

Here's why:

**The Plan Contains the Truth**

If you have a good plan that specifies:
- What should happen
- How the pieces relate
- What the data flow is
- What the edge cases are

Then any competent implementation of that plan will be good. It doesn't matter if the AI takes 5 minutes or 50 minutes to generate it. The quality is already determined.

**Conversely, a Bad Plan Can't Be Rescued in Execution**

If your plan is vague or wrong:
- "Build an API" ← This is too vague; no code quality will fix this
- "Store user tokens in session, refresh when expired" ← This is specific; execution just fills in details

You can write beautiful code that implements a bad plan, and you've just wasted effort.

**This Flips the Traditional Coding World**

Historically, quality came from:
- Writing code carefully
- Reviewing it thoroughly
- Refactoring often
- Testing extensively

With AI, the emphasis shifts:
- Quality comes from clear thinking
- Comes from specific plans
- Comes from knowing *why* you're doing something

The execution (code generation) is still important, but it's not where you invest most cognitive energy.

### Being Ruthless With Your Codebase (23:32-24:32)

**The Accumulation Problem**

As your codebase grows, complexity tends to accumulate. Code that was fine in month 1 starts to feel brittle in month 6. Bad decisions cascade.

Ben's practice: **Be ruthless about eliminating anything that slows you down.**

**What Slows You Down:**

1. **Janky or buggy code** — If you know a section is fragile, fix it now, not later
2. **Slow feedback loops** — Anything that delays your cycle (slow tests, unclear error messages, hard-to-debug code)
3. **Complexity that isn't necessary** — Extra abstraction layers, over-engineered solutions
4. **Coupling and tangles** — Code that shouldn't be related but is

**What Speeds You Up:**

1. **Tests** — They give you confidence to refactor
2. **Types** — They prevent whole classes of bugs
3. **Linting** — They enforce consistency (which makes code faster to read and modify)
4. **Refactoring** — Keeping the system clean as it grows
5. **Simplicity** — The golden rule

### Rich Hickey on Simplicity (24:32-25:00)

Ben references Rich Hickey's famous talk on simplicity. The core idea:

**Simplicity ≠ Easy**

- **Easy** = you can do it quickly or understand it at first glance
- **Simple** = it has few parts, clear relationships, low coupling

Something can be simple but hard to learn (because it's new). Something can be easy but complicated (because it has lots of interacting parts).

**Why Simplicity Matters for AI Coding**

When you have a simple codebase:
- AI can understand context quickly
- Generated code tends to stay consistent with existing code
- You can reason about the whole system
- Changes don't cause unexpected side effects

When you have a complicated codebase:
- AI gets confused by tangled dependencies
- Generated code starts to contradict itself
- You can't predict downstream effects
- The system becomes rigid and hard to change

**The Living vs. Dead Codebase Feel**

Ben mentions something important: you can *feel* when a codebase is alive vs. dead.

- **Living:** New code flows in naturally, patterns are clear, changes compound nicely
- **Dead:** New code feels like you're fighting the system, patterns are unclear, changes create problems

This is the output of simplicity. A simple system feels alive because it responds well to change. A complex system feels dead because it resists change.

### The Cognitive Load Problem (25:34-26:35)

**If You're Not Tired, Something's Wrong**

This is a crucial insight: Ben says if you're generating a lot of code with AI and you're not mentally exhausted, you're probably not *understanding* what you're generating.

Why?

Because you're generating code that's too complex for your brain to track, and you don't realize it. You're operating on autopilot, and that's where bad decisions happen.

**The Spidey Sense for Problem Areas**

When you're *locked in* and understand your system, you develop intuition about where problems lurk:
- Parts that feel weird
- "Dark forests" (code you don't really understand)
- Brittle spots that break for mysterious reasons
- Pesky issues that crop up unpredictably

These signals are important. They're telling you *where you should go deep*.

**AI Can't Fix These Through Iteration**

When you ask AI to "fix this buggy part," it'll often just add band-aids. It doesn't understand the *why* of the problem. Only your deep thinking can identify the root cause.

---

## Bringing It All Together: The Plan-Driven Architecture (Minutes 15-25 Overview)

### The Architecture of Velocity Coding

Here's the full picture Ben is painting:

```
YOUR THINKING
    ↓
YOUR PLANNING PROMPT (The DNA)
    ↓
YOUR PLAN (The Design)
    ↓
AI CODE GENERATION (Mechanical)
    ↓
YOUR REVIEW & FEEL (Quality Assurance)
    ↓
PRODUCTION CODE
```

The effort distribution:
- **70% thinking + planning** — This is where you invest cognitive energy
- **20% review + craft** — You stay connected and maintain quality
- **10% mechanical execution** — AI handles the repetitive part

This is backwards from traditional coding, where the split is more like:
- 10% thinking
- 80% coding and debugging
- 10% review

### How This Applies to Your N5 & Careerspan

**For N5:**

Your modular scripts should come from a clear planning prompt that says:
- What problem does each script solve?
- How do they compose?
- What data flows between them?
- What's the philosophy (explicit, modular, local-first)?

Then each script is generated from a specific plan, and you review it for feel.

**For Careerspan:**

When building features:
- **Think:** "How should career progression be modeled?"
- **Plan:** "The system will track milestones, track competencies, surface them in the coaching interface..."
- **Execute:** Generate the code
- **Review:** Does it feel right? Does the data model make sense? Are the workflows natural?

The difference between velocity coding and vibe coding: you're *owning* the thinking and planning, not just the code.

---

## Key Takeaways from Minutes 15-25

1. **Feel matters.** You need to maintain a visceral sense of your code's quality. This only comes from reading and thinking deeply.

2. **Own the planning process.** Don't outsource planning to AI. This is where all your architectural decisions originate. This is where your intent lives.

3. **The planning prompt is sacred.** It's the DNA of your codebase. Invest in it. Experiment with it. Keep it clear and consistent.

4. **Quality is upstream.** Quality comes from thinking and planning, not from careful code writing. This is a huge shift from traditional programming.

5. **Simplicity is the golden rule.** Complexity accumulates. Be ruthless about it. Simple systems respond well to change (and AI generation).

6. **Model selection matters.** Choose the right AI model for the right job. Slow + thoughtful for planning. Fast + direct for execution.

7. **You should feel tired.** If you're generating lots of code and not mentally exhausted, you're probably not understanding what you're generating.

8. **Code review needs context.** The plan helps AI review better, because it knows what you're trying to do, not just what the code does.

---

Ready to continue from 25:22 onward? This is where Ben gets into the practical specifics of Cursor workflow and execution.

---

**2025-10-26 14:26 ET**
