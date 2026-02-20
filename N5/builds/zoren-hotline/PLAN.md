---
created: 2026-02-20
last_edited: 2026-02-20
version: 2.3
provenance: con_gFL5uhApy1RZtlSJ
---

# Zøren Hotline — Build Plan

**Build slug:** `zoren-hotline`
**One-liner:** Dedicated voice/text communication system for The Vibe Pill, deployed on Zoputer.

## Objective

Build and deploy a fully operational AI voice hotline (Zøren) for The Vibe Pill community. The system must:
1. Accept inbound calls on (415) 340-8017 and route them through VAPI to the Zøren AI concierge
2. Resolve caller identity via phone → Stripe → Airtable lookup
3. Handle four pathways: intake/screening, member support, FAQ, and co-building
4. Track all member data in Airtable and call analytics in DuckDB
5. Process Stripe payments with phone collection for identity joining
6. Deploy entirely on Zoputer — V's Zo stays clean

## Brand Change Log

| Field | Old | New |
|-------|-----|-----|
| Brand | FounderMaxxing | **The Vibe Pill** |
| Domain | foundermaxx.ing | **thevibepill.com** |
| Concept doc | FounderMaxxing-Concept-V1.md | **VibePill-Concept.md** (v2.0) |
| Landing page routes | /foundermaxxing, /api/foundermaxxing-* | **/vibe-pill, /api/vibe-pill-*** |
| Knowledge base | (new) | **Knowledge/vibe-pill-hotline/** |
| Concierge identity | TBD | **Zøren** |
| World-first line | "...is...is..." | **"The course you're learning = the product you're building = the community you're fostering."** |

## Decisions (ALL FINAL)

| Decision | Status | Detail |
|----------|--------|--------|
| AI name | ✅ FINAL | **Zøren** (ø like Ødegaard) |
| Brand | ✅ FINAL | **The Vibe Pill** |
| Domain | ✅ FINAL | **thevibepill.com** |
| Deploy target | ✅ FINAL | Zoputer (ZOPUTER_API_KEY confirmed working) |
| Phone | ✅ FINAL | (415) 340-8017 (SF Twilio number) |
| AgentMail | ✅ FINAL | zoren@agentmail.to |
| Identity joining | ✅ FINAL | Stripe phone collection → phone is primary key |
| Knowledge base | ✅ FINAL | `Knowledge/vibe-pill-hotline/` (fork from zo-hotline, layer on top) |
| URL routing | ✅ FINAL | Rename everything: /vibe-pill, /api/vibe-pill-* |
| ElevenLabs voice | ✅ INTERIM | Using Zoseph default `DwwuoY7Uz8AP8zrY5TAo` (V will swap later) |
| Airtable base | ✅ CONFIRMED | `app4RseEJNYVUnH28` "The Vibe Pill Community" — table `tblP4vacxxgnTX26A` "Community Members" (needs field expansion for phone, email, Stripe ID, membership status, call history) |

## Success Criteria

1. **End-to-end call flow:** A test call to (415) 340-8017 reaches Zøren, who responds in character with correct voice and persona
2. **Identity resolution:** Known members are greeted by name; unknown callers enter the screening pathway
3. **Airtable integration:** Member records created/updated on Stripe checkout; call logs linked to member records
4. **Stripe phone collection:** Payment links collect phone numbers; webhook activates member status
5. **Analytics:** Call data ingested into DuckDB with queryable schema
6. **Isolation:** All services run on Zoputer; no artifacts or services on V's primary Zo
7. **Knowledge base:** ≥8 Vibe Pill-specific knowledge entries layered on Zo platform base

## Infrastructure Confirmed

- **Zoputer API:** Tested ✅ — `ZOPUTER_API_KEY` env var → `api.zo.computer/zo/ask` → responds as `zoputer`
- **Twilio:** (415) 340-8017
- **AgentMail:** zoren@agentmail.to
- **Stripe phone collection:** Native `phone_number_collection` parameter on Payment Links — no custom code needed

## Architecture

### Security Model
- All hotline services run on **Zoputer** — V's Zo stays clean
- Callers/texters interact with Zoputer, never V's Zo directly
- Member data in Airtable (shared access with business partner)
- Call logs in DuckDB on Zoputer (analytics only)

### Identity Flow
```
Stripe Checkout (phone collected) → webhook → Airtable record created
   ↓
Caller dials (415) 340-8017 → VAPI → phone lookup in Airtable
   ↓
If match: "Welcome back, [name]" + member context
If no match: Application/screening pathway
```

### Pedagogical Framing (V's words, captured for system prompt)
The course is structured around building your own productivity setup because:
1. You learn best by building
2. Your own productivity is the highest-ROI build target — intrinsically engaging AND compounds
3. Focused structure prevents aimless intellectual meandering
4. Zøren + community shortcut solutions design and compound optimization

## Drops (7 total)

### Phase 1 (Parallel — no dependencies)
| Drop | Title | Description |
|------|-------|-------------|
| D1 | Knowledge Base Fork | Fork zo-hotline → `Knowledge/vibe-pill-hotline/`, add Vibe Pill entries |
| D4 | Airtable Schema + Stripe | Member tracking, Stripe webhook for phone→identity |
| D6 | Call Analytics Pipeline | DuckDB schema + analysis scripts on Zoputer |

### Phase 2 (Sequential — needs Phase 1)
| Drop | Title | Description |
|------|-------|-------------|
| D2 | Zøren System Prompt | Voice conversation prompt for Vibe Pill (based on Zoseph) |
| D3 | Webhook Server | Fork hotline-webhook.ts for Zoputer, Vibe Pill routing |

### Phase 3 (Needs Phase 2)
| Drop | Title | Description |
|------|-------|-------------|
| D5 | VAPI Assistant | Configure VAPI with Zøren prompt, new number, voice |

### Phase 4 (Landing page — parallel with others)
| Drop | Title | Description |
|------|-------|-------------|
| D7 | Landing Page Rebrand | Rename zo.space routes to /vibe-pill, update all copy, work in world-first = line, pedagogical framing |

## Open Questions (Reduced)

| # | Question | Blocker? |
|---|----------|----------|
| 1 | V's landing page edits — need to read current state before D7 | Not a blocker |

---

*v2.2 — All strategic decisions finalized. Ready for Phase 1 execution on V's go.*
