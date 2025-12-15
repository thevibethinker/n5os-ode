---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# B03 – Decisions

1. **Use join decks (or similar) only as a thin access layer to Zo**
   - **Decision:** Treat join decks as a context bridge ("assistant on your desktop") that can call into Zo, not as the primary system of record.
   - **Rationale:** Keeps Zo as the durable home for state while still giving users in‑browser convenience.

2. **Lean on email + Condo + tagging for v1 data flows**
   - **Decision:** Anchor the first implementation around email traffic and Condo, using tags/signatures to classify networking interactions.
   - **Rationale:** These channels are already where real conversations happen and are controllable without fighting LinkedIn’s API constraints.

3. **Aggregate past networking attempts as explicit training data**
   - **Decision:** Design a behavior where Zo proposes a candidate set of "networking emails" from history and asks the user to confirm or reject them.
   - **Rationale:** Yields a high‑quality corpus for tone/style learning without guessing blindly.

4. **Stage complexity via starter kit + advanced modules**
   - **Decision:** Ship a minimal, self-contained starter kit first (simple cohorts, queues, and agents), then layer on optional modules (Condo, scrapers, more sophisticated flows).
   - **Rationale:** Reduces onboarding friction and lets serious users opt into more power over time instead of being forced into it.

5. **Target "option maximizers" as the primary design persona**
   - **Decision:** Optimize the system and programming for professionals who are not urgently job seeking, but want a calm, reliable networking rhythm.
   - **Rationale:** This group aligns with Next Play’s membership and is more tolerant of a slow-burn habit-building approach.

6. **Frame historical gaps as non-blocking**
   - **Decision:** Do not attempt to fully reconstruct the past; focus on setting up a forward-looking system that starts producing value immediately.
   - **Rationale:** Trying to backfill every historical interaction would be overwhelming and unnecessary for success.


