---
created: 2026-01-03
last_edited: 2026-01-03
version: 1
provenance: con_J2vxTbWJaUzc0NVQ
---
# Boris Cherny's Claude Code Masterclass: Beginner Takeaways

Derived from Boris Cherny's (Creator of Claude Code) workflow thread on X (Jan 2026).

## 1. Philosophy: Orchestration > Writing
- **The Shift:** Stop thinking of yourself as a "writer of code" and start thinking as an "orchestrator of agents."
- **Practical Application:** Don't just ask Claude to "fix a bug." Ask it to "Investigate three different ways to solve this bug, show me the trade-offs, and then I'll pick one to execute."

## 2. Parallelism: The Multi-Tab Mindset
- **The Strategy:** Use multiple terminal tabs for different "worker" threads.
- **For Beginners:** You don't need 15 tabs yet, but try using **two**:
    - **Tab 1:** Active implementation (writing the code).
    - **Tab 2:** Background research/documentation (asking Claude to explain a library or find an example).
- **Tool Tip:** Use `claude --continue` in a new tab to pick up where you left off or `claude --resume` to branch a conversation.

## 3. The Verification Loop (Critical)
- **The Concept:** Claude is 3x better when it can check its own work.
- **Actionable Steps:**
    - Never accept a code change without asking Claude to verify it.
    - If you don't have a test suite, ask Claude: "Write a quick bash script to verify that this change actually works."
    - **V's Advantage:** Since you are non-technical, make Claude prove it works by showing you the output of a command or a screenshot (if using web tools).

## 4. Automation via Slash Commands
- **The Concept:** Don't repeat yourself (DRY) in prompts.
- **How to Start:** If you find yourself typing "Commit these changes with a good message and push" every hour, create a custom slash command.
- **Location:** Store them in `file '.claude/commands/'`.

## 5. Model Quality Matters
- **The Tip:** Use the best model available (currently Opus 4.5) for complex logic.
- **Beginner Logic:** It might feel slower, but it saves time on "steering" and correcting mistakes.

---
*Source: https://x.com/bcherny/status/2007179832300581177*
