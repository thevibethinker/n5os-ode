

# B02_B05_COMMITMENTS_AND_ACTIONS

---
created: 2026-02-15
last_edited: 2026-02-15
version: 1.0
provenance: con_UBTGBfKrHLNJDdBp
meeting_date: 2026-01-26
participants: [Vrijen Attawar, David Speigel]
meeting_type: external
---

## Commitments by David

| # | Commitment | Context | Urgency |
|---|-----------|---------|---------|
| D1 | Send intro email connecting Ben Erez with V and the Zo team | "I'm gonna send that email. I'll send that at the end of our call." | Immediate — end of call |
| D2 | Find out where Ben Erez is located in Brooklyn | "I don't know. That's what I gotta find out." | Near-term, needed for meetup planning |
| D3 | Send separate email(s) to Ben Erez beyond the intro | "I owe an email to Ben Erez. I want to get a couple emails to him, but the first one I want is to introduce him to the three of you." | After intro email |
| D4 | Diagram the messaging-assistant product concept more clearly | "That's where I start getting hung up... maybe I should try to diagram it a little bit more." | Self-assigned, no deadline |

## Commitments by V

| # | Commitment | Context | Urgency |
|---|-----------|---------|---------|
| V1 | Meet with Ben Erez in Brooklyn (1:1 if needed) | "Even if I can meet him separately, I'm happy to make the trek to find some time with him." | After David's intro email |
| V2 | Get Careerspan demo recorded and send ~10 outreach emails | "We are trying to get a demo out the door today... send out maybe like 10 hey, come get us sort of emails." | Same day (2026-01-26) |
| V3 | Fix N5OS bootloader to include N5 instructions on crash/resume | "I don't know why N5 instructions aren't included in that. Okay, I'll have to..." — noted as something to patch | Self-assigned, no deadline |

## Action Items

### Immediate (during/right after call)

1. **David** — Send intro email: Ben Erez → V + Zo team (Brooklyn meetup context)
2. **David** — Update N5OS to upstream on his Zo instance (completed during call)
3. **David** — Run bootloader on fresh conversation (initiated during call)
4. **V** — Record Careerspan demo and send outreach emails (same day)

### Near-Term

5. **David** — Authenticate GitHub on Zo (skipped during call, remains outstanding)
6. **V + David** — Arrange in-person Brooklyn meetup with Ben Erez once intro is made
7. **V** — Help David get Zo into daily use starting with meeting processing (simpler than the messaging-assistant vision)
8. **V** — Investigate patching N5OS resume/crash behavior to include full N5 instructions

### Longer-Term (Discussed, Not Yet Committed)

9. **V + David** — Build "Spiegel-as-a-bot" messaging assistant using Zo
   - David's knowledge base (slides, transcripts, principles) as one repository
   - Candidate's background as second repository
   - Triangulate against a target's LinkedIn profile + candidate's goal
   - Generate outreach messaging sequences (warm + cold) per David's rules
   - *V's assessment:* "I think that's actually entirely achievable. I don't have the technical [ability] to do it now."
10. **V** — Explore building a front-end for querying David's methodology ("put in a $5 token and you get 20 questions from David Spiegel") or an email-based interface (e.g., ai@davidspiegel.com)

## Key Dependency Chain

```
David sends intro email to Ben Erez
  → V meets Ben Erez in Brooklyn
  → Potential Zo offsite participation / collaboration

David authenticates GitHub on Zo
  → Full N5OS sync capability
  → Foundation for meeting processing system
  → Eventually: messaging-assistant product build
```

## Open Questions

- **David's cohort content:** 4 paid students, 2-week program ending this week — could cohort materials feed into the "Spiegel bot" knowledge base?
- **Zo skills feature:** Currently behind a feature flag (V has access, David doesn't yet) — timeline for general availability affects product roadmap
- **Product scope:** V explicitly steered away from the big messaging-assistant build toward simpler Zo adoption first: "I'm almost saying like something that's far more within the realm of reach. So like just a meeting processing system."

---

*2026-02-15 12:40 PM ET*