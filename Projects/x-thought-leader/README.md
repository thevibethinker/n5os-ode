---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_S4D4PEMvW09h9VCl
---

# X Thought Leadership Engine

Reactive Twitter engagement system that monitors industry leaders, correlates their tweets with V's positions, and generates multi-variant draft responses for HITL approval.

## Quick Start

```bash
# Test API credentials
python src/x_api.py test-auth

# Check system status
python src/orchestrator.py status

# Manual poll (bypass schedule)
python src/orchestrator.py poll-now
```

## Architecture

```
@asanwal tweets about hiring
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  POLLING AGENT (every 15min, 8am-10pm ET)                  │
│  └─► Fetch new tweets from monitored accounts               │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  POSITION MATCHER                                           │
│  └─► Score against 105 positions in positions.db            │
│  └─► High correlation? Continue. Low? Skip.                 │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  DRAFT GENERATOR                                            │
│  └─► Generate 4 variants:                                   │
│      • SUPPORTIVE - builds on their point                   │
│      • CHALLENGING - questions assumptions                   │
│      • SPICY - bold, contrarian                             │
│      • COMEDIC - witty, playful                             │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  SMS APPROVAL (V's phone)                                   │
│  └─► "Reply 1-4 to post, 'skip' to pass"                   │
│  └─► Supports refinement: "3 but shorter"                   │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  POSTER                                                     │
│  └─► Post as reply (appears in target's mentions)           │
│  └─► Log for voice learning                                 │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables (in Zo Secrets)
- `X_API_KEY` - X/Twitter API key
- `X_API_SECRET` - X/Twitter API secret  
- `X_BEARER_KEY` - X/Twitter bearer token
- `X_ACCESS_TOKEN` - User access token (for posting)
- `X_ACCESS_SECRET` - User access secret (for posting)

### Monitored Accounts
Edit via prompt: `@X Thought Leader add @username`

Current: `@asanwal` (Anand Sanwal, CB Insights)

### Voice Variants
See `config/voice_variants.yaml`

## Rate Limits (Basic Tier - $200/mo)
- **Read**: 10,000 tweets/month (~333/day)
- **Write**: 17 tweets/24 hours
- **Polling**: Every 15 min = ~64 polls/day

## Files

```
x-thought-leader/
├── README.md
├── build_plan.json
├── config/
│   ├── voice_variants.yaml     # 4 variant definitions
│   ├── voice_examples.md       # Few-shot examples
│   └── learned_voice.yaml      # Evolving from learner
├── db/
│   ├── tweets.db               # Main database
│   └── schema.sql              # Schema reference
├── src/
│   ├── x_api.py                # X API wrapper
│   ├── position_matcher.py     # Correlation engine
│   ├── draft_generator.py      # 4-variant generator
│   ├── sms_interface.py        # Approval flow
│   ├── poster.py               # Tweet posting
│   ├── polling_agent.py        # Scheduled poller
│   ├── orchestrator.py         # Main coordinator
│   ├── archive_ingester.py     # Historical tweet import
│   └── voice_learner.py        # Style analysis
└── agents/
    └── (Zo scheduled agents)
```

## Approval Flow

SMS format:
```
🐦 @asanwal just tweeted:
"AI is changing how we assess candidates"

Your drafts:

1️⃣ SUPPORTIVE:
Been saying this for years...

2️⃣ CHALLENGING:
True, but AI isn't changing assessment...

3️⃣ SPICY:
Hot take: AI won't fix hiring...

4️⃣ COMEDIC:
Resumes watching AI enter the chat: 👀💀

Reply 1-4 to post, or "skip"
Expires: 11:59 PM ET
```

Responses:
- `2` → Post variant 2
- `skip` or `0` → Skip this tweet
- `3 but shorter` → Regenerate variant 3 with feedback

## Voice Learning

The system tracks:
1. Which variants V approves (preference weights)
2. Refinement requests (learned rules)
3. Historical tweets (baseline style)

Weekly analysis updates `learned_voice.yaml`.

## Build Status

See `N5/builds/x-thought-leader/` for worker status.

---

*Built for V by Zo | con_S4D4PEMvW09h9VCl*

