# B04: Open Questions & Unresolved Items

## Question 1: Ben Eras's Location in Brooklyn

**QUESTION:** Where exactly is Ben Eras located in Brooklyn?

**CONTEXT:** David wants to schedule a meetup between Ben Eras, Vrijen, and himself. Knowing Ben's location will help determine the most convenient meeting spot and logistics.

**WHO NEEDS TO ANSWER:** David Speigel (he mentioned he will find out)

**BLOCKING:** Planning the meetup location; scheduling the introduction meeting

**NEXT STEP:** David to contact Ben Eras and determine his Brooklyn location

---

## Question 2: Technical Architecture for David's AI Coaching System

**QUESTION:** What is the technical architecture for building David's AI-based coaching bot that can provide personalized messaging advice?

**CONTEXT:** David envisions an AI system that can:
- Store David's background materials (slides, transcripts, principles)
- Store individual candidate information (Careerspan answers, interview responses, LinkedIn profiles)
- Triangulate across candidate background, target's LinkedIn profile, and candidate's goal
- Generate outreach messages in David's voice based on these inputs

Multiple technical uncertainties exist:
- How to structure databases for individual users with proper separation (11:22)
- Whether to use graph databases or vector databases for semantic search
- How to handle multi-threaded conversations and user data isolation
- Frontend design (web interface, email-based, or other)
- Integration points (LinkedIn API access, etc.)

**WHO NEEDS TO ANSWER:** Technical implementation team (to be determined; potentially Zo or external developer)

**BLOCKING:** David cannot build the full vision product; stuck using ChatGPT projects with limited functionality

**NEXT STEP:** Vrijen suggested starting with a simpler Zo-based meeting processing system first to build familiarity before tackling the full system

---

## Question 3: Zo's Value Proposition & Positioning Strategy

**QUESTION:** How should Zo articulate its unique value proposition and differentiation from other AI tools (Claude Code, ChatGPT Projects, etc.)?

**CONTEXT:** Both David and Vrijen identified that Zo has a messaging/positioning problem:
- Technical users don't see value ("I don't need Zo for this")
- Non-technical users don't appreciate the value of having their own personal server
- Current messaging focuses on technical features that don't resonate with either audience

The target audience appears to be users who are "just smart enough to use projects and custom GPTs in ChatGPT" but are getting limited by those tools (e.g., Noah King's situation).

**WHO NEEDS TO ANSWER:** Zo team (product/marketing)

**BLOCKING:** Adoption and understanding of Zo's value; effective communication to prospective users

**NEXT STEP:** Help Zo articulate differentiation; potentially position around the specific pain point of users who have outgrown ChatGPT Projects but need more than standard AI chat interfaces

---

## Question 4: Integration of GitHub-based Materials into David's Zo Workspace

**QUESTION:** Once the N5OS system is successfully installed and running in David's Zo workspace, what specific materials from David's teaching repository should be ingested and in what format?

**CONTEXT:** The team worked on updating David's Zo workspace with the latest version of the N5OS repository from GitHub. David has teaching materials (slides, transcripts, principles) that could be loaded into Zo for better context and capabilities.

**WHO NEEDS TO ANSWER:** David Speigel (to identify materials) + Vrijen (to advise on optimal format/location)

**BLOCKING:** Full utilization of Zo's capabilities for David's coaching work

**NEXT STEP:** Once N5OS is fully operational, determine which teaching materials to load and structure them appropriately

---

## Question 5: Careerspan Demo & Outreach Timeline

**QUESTION:** When will the Careerspan demo showing human data collection capabilities be completed, and what is the timeline for sending the initial outreach emails?

**CONTEXT:** Vrijen mentioned they are "trying to get a demo out the door today" that shows how Careerspan's human data collection works, with plans to send approximately 10 outreach emails to prospective users.

**WHO NEEDS TO ANSWER:** Vrijen / Careerspan team

**BLOCKING:** Potential user acquisition and pipeline building for Careerspan

**NEXT STEP:** Completion of demo development; execution of outreach email campaign

---

## Question 6: Smart Glasses Integration with Zo

**QUESTION:** What is the technical approach for integrating Vrijen's new smart glasses with Zo to provide heads-up display capabilities?

**CONTEXT:** Vrijen is expecting smart glasses that can provide a heads-up display for adding items, recording to-do lists, and potentially integrating with Zo to provide information overlays (Sherlock-style "omniscience"). The glasses have no camera and are designed to be discreet.

**WHO NEEDS TO ANSWER:** Vrijen (spec development) + Zo integration team

**BLOCKING:** None explicitly stated (notional/future capability)

**NEXT STEP:** Vrijen to explore integration possibilities once glasses arrive; potential API/app development for Zo-glasses connection