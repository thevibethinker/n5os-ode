# B04: Open Questions & Unresolved Items

## Question 1: Location of Ben Eras in Brooklyn

**QUESTION:** Where exactly is Ben Eras located in Brooklyn?

**CONTEXT:** David is planning an in-person meetup between Ben Eras, Vrijen, and the Zo team. Knowing Ben's location will help determine logistics for the meeting. Vrijen speculated he might be in Williamsburg but this is unconfirmed.

**WHO NEEDS TO ANSWER:** David needs to follow up with Ben Eras directly.

**BLOCKING:** Planning the in-person meetup logistics.

**NEXT STEP:** David will email Ben Eras after this call to ask about his Brooklyn location.

## Question 2: System Architecture for Multi-User Bot

**QUESTION:** How should the database/graph structure be designed to keep user information separated while enabling multi-user access to David's advice system?

**CONTEXT:** David wants to build a system where users can interact with an AI that provides advice based on David's methodology. The system needs to: (1) store David's background/methodology, (2) store each individual user's background/careerspan answers, (3) store target LinkedIn profile information, and (4) facilitate back-and-forth messaging. David is uncertain whether this requires different tables for each user or another architectural approach.

**WHO NEEDS TO ANSWER:** Technical architect/engineer (potentially Zo team if building with Zo).

**BLOCKING:** Development of the messaging/advice bot system.

**NEXT STEP:** Need to diagram the system architecture and determine data model (graph database vs. tables, user isolation approach).

## Question 3: Can Canva Decks Be Uploaded to DeepWiki?

**QUESTION:** Can non-repository content (like Canva decks) be uploaded to DeepWiki to create a Wikipedia-style documentation?

**CONTEXT:** David saw the DeepWiki.com capability to turn GitHub repos into wikis and asked if he could upload his Canva presentation decks. Vrijen was uncertain, suggesting it's repo-specific but theoretically possible if stored in a GitHub repo.

**WHO NEEDS TO ANSWER:** Someone to test DeepWiki capabilities or review documentation.

**BLOCKING:** Potentially using DeepWiki for David's presentation materials.

**NEXT STEP:** Test by creating a GitHub repo with Canva deck files or review DeepWiki documentation.

## Question 4: Zo's Positioning vs. Other AI Tools

**QUESTION:** How should Zo articulate its unique value proposition compared to other AI tools like Claude Code, especially for the target audience?

**CONTEXT:** Both Vrijen and David acknowledged that Zo has a communication problem similar to Careerspan's—struggling to convey the value of a "personal server" concept to a non-technical audience. Technical folks don't need it, and non-technical folks don't appreciate the value of having their own server. They need to find the "just smart enough" users who have hit limitations with ChatGPT projects/custom GPTs.

**WHO NEEDS TO ANSWER:** Zo team/marketing.

**BLOCKING:** Effective go-to-market messaging for Zo.

**NEXT STEP:** Help Zo articulate their positioning, possibly by identifying the "frustrated power user" segment who has outgrown ChatGPT's file/project limitations.

## Question 5: Skills Feature Availability in Web Version

**QUESTION:** Should the Zo web version show the Skills feature, or is it currently limited to certain users via feature flags?

**CONTEXT:** Vrijen noticed he has access to Skills in his Zo instance while David's was prompting to upgrade. Vrijen speculated it might be a pre-release feature flag enabled specifically for him, but wasn't certain whether the web version should display it.

**WHO NEEDS TO ANSWER:** Zo team.

**BLOCKING:** David's ability to use the Skills feature.

**NEXT STEP:** Reload the web version after upgrade to see if Skills appear.

## Question 6: N5 Resume Instructions Not Included

**QUESTION:** Why are N5 instructions not included in the resume functionality after a crash/reload?

**CONTEXT:** When Zo crashed and the bootloader resumed with the `n5:resume` command, Vrijen noticed that the N5 instructions weren't being picked up properly for recovery context.

**WHO NEEDS TO ANSWER:** Vrijen (to investigate/fix in N5OS).

**BLOCKING:** Proper crash recovery in N5OS.

**NEXT STEP:** Vrijen mentioned he'll have to investigate why N5 instructions aren't included in the resume context.