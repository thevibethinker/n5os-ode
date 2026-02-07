# B04_OPEN_QUESTIONS

## Question 1: Ben Eras' Location and Meeting Logistics

**QUESTION:** Where exactly is Ben Eras located in Brooklyn, and what's the optimal location for the three (Vrijen, Ben, Zo team) to meet up?

**CONTEXT:** David wants to introduce Ben Eras to the Zo team during the off-site. Vrijen is near Metro Tech (Gold Street), Zo is near Meserole Street in Williamsburg, and Ben is in Brooklyn but the exact location is unknown.

**WHO NEEDS TO ANSWER:** David Speigel (needs to find out from Ben Eras)

**BLOCKING:** Physical meetup planning and introduction email logistics

**NEXT STEP:** David to email Ben Eras to confirm his Brooklyn location; David mentioned he'll send the introduction email at the end of their call.

---

## Question 2: System Architecture for David Spiegel Bot

**QUESTION:** How can we architect a system where individual users have isolated data containers (their backgrounds, career data) that interact with David's principles to generate personalized messaging advice?

**CONTEXT:** David wants to build a scalable system where candidates can get David-style advice for outreach. Each user needs their own "container" with their information (LinkedIn profiles, Careerspan answers, interview answers) that can be queried. David gets "hung up" on how to architect this and keep user data separated. He mentions: "I don't know how multi threaded conversations or even how setting up a database with like all of someone's information would work. Like how you would keep that separated."

**WHO NEEDS TO ANSWER:** Technical architecture decision - likely Zo team or external developer

**BLOCKING:** Building the David Spiegel advice bot at scale

**NEXT STEP:** David should diagram the system more clearly; Vrijen suspects it's solvable using graph databases and Zo but neither has the technical depth to implement immediately.

---

## Question 3: Zo's Market Positioning and Differentiation

**QUESTION:** How can Zo articulate its value proposition clearly to the target market (non-technical users who are just smart enough to outgrow ChatGPT projects)?

**CONTEXT:** David notes: "I can't explain what Zo is because compared to other AIs. Other than to say it allows you to store multiple files and it's like its own instance of files and you can use any model." Zo has a Careerspan-esque problem where they don't know how to communicate the nebulous value of a personal server. Technical users don't need it, non-technical users don't appreciate it. The target is people "just smart enough to use like projects and custom GPTs in claw or chat GBT" who realize they're limited.

**WHO NEEDS TO ANSWER:** Zo product/communications team

**BLOCKING:** Effective GTM and user acquisition for Zo

**NEXT STEP:** Discussion during the off-site with Ben Eras (this is explicitly mentioned as a topic to explore)

---

## Question 4: Whether DeepWiki Can Handle Canva Decks

**QUESTION:** Can DeepWiki be used to turn Canva presentation decks into wiki-style documentation, or is it strictly limited to GitHub repositories?

**CONTEXT:** David asks: "Could I upload a canva deck to this?" and Vrijen explains he thinks DeepWiki is specifically for repos, but suggests "in theory, why not?" because a GitHub repo could store presentation assets. The question of Canva integration remains untested/uncertain.

**WHO NEEDS TO ANSWER:** Testing/verification by David Speigel

**BLOCKING:** Potential use case for David's course materials documentation

**NEXT STEP:** David to test whether Canva content can be stored in a GitHub repo and processed by DeepWiki

---

## Question 5: Smart Glasses Integration with Zo

**QUESTION:** How can Vrijen integrate his incoming smart glasses (heads-up display) with Zo for real-time information access similar to the Sherlock Holmes character?

**CONTEXT:** Vrijen ordered smart glasses with a discreet heads-up display that allow adding items, recording to-do items, etc. He wants to emulate Sherlock Holmes-style omniscience by connecting them to Zo. The glasses have no camera and are meant to be unobtrusive. He's not sure about the technical integration path.

**WHO NEEDS TO ANSWER:** Vrijen + Zo team

**BLOCKING:** Smart glasses use case development

**NEXT STEP:** Vrijen to explore integration once glasses arrive (expected "today")

---

## Question 6: N5OS Bootloader Completion Status

**QUESTION:** Did the N5OS bootloader complete successfully on David's system, and what is the next step to get him actually using Zo for meeting processing?

**CONTEXT:** David ran the bootloader script which was "still working on all this stuff" and David notes "I still haven't seen it do what it's meant to do." The process shows "Completed" but it's unclear whether the full initialization was successful or what the next steps are to actually start using the meeting processing system.

**WHO NEEDS TO ANSWER:** Vrijen (to verify/complete setup)

**BLOCKING:** David using Zo for his workflow

**NEXT STEP:** Verify bootloader completion and move David to an achievable first use case (meeting processing system) rather than the complex David bot architecture

*Current time: February 2, 2026, 7:35 PM ET*