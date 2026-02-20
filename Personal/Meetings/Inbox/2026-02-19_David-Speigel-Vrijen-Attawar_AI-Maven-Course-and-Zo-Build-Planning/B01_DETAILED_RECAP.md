Interesting — file content seems garbled. Let me just proceed with generating the block based on the prompt spec and transcript.

# B01_DETAILED_RECAP

---
created: 2026-02-19
last_edited: 2026-02-19
version: 1.0
provenance: con_aIWyjBcSE7OJvyMp
---

# B01: Detailed Recap

## Meeting Overview

V and David Speigel met for a working session to consolidate multiple threads they've been developing together: an AI Maven course, collaborative building on Zo, a career coaching hotline, and a CRM-style agentic networking tool. The conversation evolved from agenda-setting into a deeper strategic discussion about monetizing AI productivity education for funded founders — and landed on a concrete first build: a Zo-to-Zo protocol enabling David to share his networking knowledge through a controlled, queryable system.

## Chronological Discussion

### Agenda Framing (~0:00–3:00)

David opened by bucketing their ongoing work into two categories. **Category one:** an AI Maven course — one course, one syllabus, one cohort, with lightning lessons as lead-up. He recommended against multiple courses at launch. **Category two:** building with Zo — specifically, David wants V's help building things hands-on rather than just receiving built tools, though he's been tempted to try Copilot instead of Zo because of peer pressure.

David also surfaced the two ideas V had previously sent: (1) a career coaching hotline ("Ask a Career Coach"), and (2) a CRM-style agentic networking tool. He flagged significant overlap between the CRM concept and things IDO and Logan have been building, plus growing activity around this space on X.

### Zo Mental Model Correction (~3:00–5:00)

V addressed David's Copilot-vs-Zo confusion head-on: Zo is just a computer. You could use Copilot, Cursor, or the Zo chat interface — they're all equivalent paths to the same machine. This was a mental model correction V acknowledged having needed himself. The distinction matters because it repositions Zo as infrastructure, not a competing IDE.

V then proposed a structured co-building arrangement: **$25 for the first three hours**, where V instructs his Zo to architect solutions, David's Zo receives the instructions, and they loop together on implementation. V would grant David temporary access to query V's Zo for architectural guidance. The first round would be a design cycle — no pressure to monetize — just proving the collaborative workflow.

### The "Founder Maxing" Concept (~5:00–15:00)

V pivoted to a bigger idea brewing from multiple signals. The catalyst: founders are terrified of being left behind on AI. V cited a conversation with the Calendly founder, who admitted he no longer feels in touch with productivity. V's read: that's not false humility — it's an accurate self-assessment, and it represents a monetizable existential fear.

**The pitch: "Founder Maxing" — weekly tactical AI productivity sessions for funded founders.** Structure:

- **Format:** Virtual sessions. 10 minutes of show-and-tell on a new piece of functionality, 5–10 minutes for participants to implement it, remainder for tactical discussion on adaptation and AI landscape rundowns.
- **Positioning:** Agentic productivity now, evolving toward "cognitive amplification." V's one-liner: *"I want to give everyone 30 more IQ points."*
- **Target audience:** Founders already executing well who want a convenient excuse to learn AI while improving personal productivity.
- **Pricing path:** $1/month for a seeded group of 10 reliable friends → $50–100 for warm referrals → full pricing once proven.
- **Sponsorship angle:** Shivam has contacts at Manifest, Brex, and similar companies looking to sponsor founder-facing content.
- **Competitive moat:** V believes he's in a very small group of founders who are (a) deeply skilled at AI, (b) not using that skill solely for their own company, and (c) motivated to teach. That group isn't monetizing at the apex yet.

David connected this to Marc Andreessen's recent appearance on Lenny's podcast about AI augmenting IQ, and to his own frustration about wanting to write like Ben Thompson (his Kellogg classmate at Stratechery) about the forces AI is accelerating in software.

### Software Forces & The Vibe Coding Fallacy (~15:00–20:00)

David articulated a thesis V agreed with: AI has accelerated pre-existing software forces, not created new ones. Three things that "just because you can vibe code" doesn't solve: (1) maintenance at the cutting edge, (2) deep customer empathy, and (3) ongoing support and iteration. Companies that don't use AI to keep cycling at the new speed will be displaced — but vibe coding alone isn't the answer.

V reframed: there are two layers — knowing the landscape, and translating it to "how does this apply to my business." Productivity is the ideal bridge because it's visceral, personal, and nuanced. The engineering required to navigate personal productivity is rich enough to develop genuine AI fluency as a byproduct.

### Complementary Brands: David's Maven Course vs. V's Founder Maxing (~20:00–22:00)

They identified the split clearly. **David's lane:** Use AI to build a specific thing (camp one — the Maven course). **V's lane:** Ongoing AI fluency applied to your business with a peer group (camp two — Founder Maxing). The two are complementary with cross-halo potential.

V referenced Tiago Forte's "Building a Second Brain" as an analog: why can't they be the equivalent for agentic networking (David) and agentic productivity (V)?

### Go-to-Market: Credibility & Seeding (~22:00–25:00)

V laid out a three-tier GTM plan:

1. **Proof points:** Collect quotes from people already impressed (Ben and Rob top of pile).
2. **Seed group:** 10 friends at $1/month for the first session — a reliable experiential floor.
3. **Warm referrals:** Tap David and other trusted connectors. One-off commission for getting someone in the door, plus a smaller ongoing amount for retention. For high-profile names (Benarez-level), flexible — might comp entirely for the marquee effect.

V emphasized that linchpin members matter more than early revenue at this stage.

### First Build: Ambient CRM → Zo-to-Zo Protocol (~25:00–end)

David pushed for specificity: what would they actually build first? He scoped the agentic networking use case — who to contact, how often, how to follow up, what to say.

V initially proposed a simple ambient CRM — something that tracks contacts via email/calendar and auto-builds profiles. But the conversation evolved when David described what he really wants: a system where (1) he dials in his networking parameters, (2) others can see those parameters and apply them to their own context, and (3) the whole thing is shareable.

V realized the Zo-to-Zo protocol he built the previous week handles this cleanly:

- **Architecture:** David gets a Zo. His Zo has a deconstructed database of his networking knowledge, independently updatable. A Zo-to-Zo protocol limits clients to querying a commercial slice of David's knowledge — they can't exfiltrate the full dataset.
- **Security model:** V recommended David set up a "Zo Pewter" (secondary Zo) as a concierge layer, mirroring V's own approach. Double firewall: break into Zo Pewter, then wrangle it into breaking into the personal Zo.
- **Extensibility:** V and David can design tools within the Zo system that incrementally increase functionality available through the Zo-to-Zo handshake. Clients can use whatever infrastructure they want on their side — they just need to know how to handshake David's Zo.

David agreed: **"Let's just start with that."**

### Security Sidebar: Jason Rosen (~brief)

David asked if V had spoken with Jason Rosen. V confirmed — about a week ago. David noted Jason is focusing on AI security. V committed to getting Jason to review the repo, recognizing the security implications of the Zo-to-Zo protocol.

## Key Takeaways

- **Two complementary brands crystallized:** David's Maven course (build a specific thing with AI) and V's Founder Maxing (ongoing AI fluency for funded founders). They cross-pollinate, not compete.
- **First build decided:** A Zo-to-Zo protocol that lets David share his networking knowledge through a controlled, queryable system — not a standalone CRM, but a knowledge-sharing architecture.
- **V's competitive positioning sharpened:** The intersection of AI skill + founder experience + motivation to teach + available bandwidth is a near-empty market. Founder Maxing occupies that gap.
- **"Cognitive amplification" is V's long-term brand direction** — giving everyone 30 more IQ points via agentic productivity.
- **GTM is relationship-first:** Seed with friends at $1, collect proof points, tap warm referrals via trusted connectors with commission structure, pursue sponsor relationships (Brex, Manifest) through Shivam.
- **Security review needed:** Jason Rosen flagged as the right person to audit the Zo-to-Zo protocol repo.
- **Co-building arrangement agreed:** $25 for first 3 hours, V's Zo architects, David's Zo receives — treat the first round as a design cycle.

---

*2026-02-19 1:35 PM ET*