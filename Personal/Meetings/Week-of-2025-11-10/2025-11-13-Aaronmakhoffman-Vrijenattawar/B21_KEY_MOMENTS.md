# B21_KEY_MOMENTS

## Key Quotes

**"It would take 40 to 60 hours to build something. That now takes me three."**  
— Aaron Mak Hoffman  
*Context:* Describing productivity gains from using Zo for planning before handing off to Replit Agent. The dramatic time reduction (40-60 hours → 3 hours) comes from doing the hard work of pulling in the right context and building strategy first, then letting the agent purely execute.

**"I almost think of it as like the knowledge base are my sacred texts."**  
— Vrijen Attawar  
*Context:* Explaining his information hierarchy system where raw data flows through processing stages, with knowledge base representing the highest level of distilled information. This metaphor signals how he treats certain information as foundational and immutable.

**"I'm always having it make something that I can understand along with it so that if I need to, I can grab this document and give it to the AI and say, hey, I want this, and I can actually, like, take control versus just having it spit out this crazy prompt."**  
— Aaron Mak Hoffman  
*Context:* Describing his philosophy of always requesting READMEs and technical documentation alongside code. This maintains human agency—if he needs to intervene, he can understand and direct the system rather than being locked out of his own creation.

**"Like it's just like your stages of like in between compression and then ultra distilled compression. It's the same concept with the code."**  
— Aaron Mak Hoffman  
*Context:* Extending his compression framework (full PRD → planning docs → ultra-distilled README) to software development. Shows how he thinks about information architecture consistently across domains—massive documents, middle-stage planning, and minimal usable summaries.

**"What I observed is that if you're not watching it, like, if you don't have that open, it will stall out."**  
— Vrijen Attawar  
*Context:* Revealing a practical workaround for Zo's tendency to stall on long runs—keeping the window open prevents it. Both participants experienced this issue, highlighting a current platform limitation and a pragmatic solution.

**"I find with vibing anything right, you want to break it up into manageable sections."**  
— Aaron Mak Hoffman  
*Context:* General principle about working with AI systems. Replit Agent can't handle agentic shortcomings like recalling the right things at the right times, so he does the hard work of breaking work into sections and managing context upstream.

**"They can be made more reliable with explicit instructioning within the Persona to switch on the appropriate occasion."**  
— Vrijen Attawar  
*Context:* Addressing Aaron's question about whether persona switches are reliable. The answer reveals that reliability comes from embedding explicit switching instructions within the persona definitions themselves, not expecting automatic behavior.

## Strategic Questions Raised

**"How do you plan? Like, I would love to learn some, like, best practices, because I kind of just dove in."**  
— Vrijen Attawar  
*Significance:* Vrijen explicitly positioning himself as someone learning and asking for guidance from Aaron, who has developed sophisticated planning workflows. This prompted Aaron to share his compression framework (PRD → planning docs → README), which became a key insight of the conversation.

**"How do you maintain sync between what the system is doing in the technical docs?"**  
— Vrijen Attawar  
*Significance:* Identifying a critical operational problem—if code changes, how do technical docs stay in sync? Aaron's answer revealed his solution: maintaining everything in docs rather than code, allowing Zo to reference planning documents when building rather than relying on documentation that may have diverged from implementation.

**"So Zo can create new chats and close conversations, like by itself?"**  
— Aaron Mak Hoffman  
*Significance:* Probing a critical capability for Vrijen's build orchestrator concept—spawning parallel worker conversations. Vrijen confirmed it's possible through `/zo/ask`, which led to discussion of current limitations (no parallel chats, stalling when switching conversations).

**"Are you pulling in as context to write that?"**  
— Aaron Mak Hoffman  
*Significance:* Early question that surfaced Vrijen's entire information architecture system (raw data → content library → knowledge base). This question opened up the discussion of how both participants structure context for their AI systems differently.

**"Do you find that it like stalls a lot on long agent runs?"**  
— Aaron Mak Hoffman  
*Significance:* Identifying a shared pain point that both participants experienced. This led to exchanging workarounds (keeping windows open) and confirming that it's a platform limitation affecting both users, highlighting a need for feature improvements like parallel chats.

*February 2, 2026 at 3:50 PM ET*