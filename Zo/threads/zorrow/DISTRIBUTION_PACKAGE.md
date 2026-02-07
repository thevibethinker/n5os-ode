---
created: 2026-02-02
last_edited: 2026-02-02
version: 0.1
provenance: con_DUinKdCmmdFh1OUa
purpose: Infrastructure + instruction set for vanilla Zo to post Zorrow content locally
---

# Zorrow Distribution Package

**To:** zoputer@zo.computer  
**From:** Zo (va.zo.computer)  
**Mission:** Set up local infrastructure to post Zorrow AI Lykos tweets on @belarvardan92 using distributed voice system

---

## What You're Getting

1. **Weekly Content Manifests** — tweets + mechanics tags + posting schedule
2. **Voice Transformation Context** — how to apply Vibe Writer voice patterns
3. **X API Integration Guide** — authenticate + post
4. **Feedback Loop Closure** — report metrics back

---

## Local Setup (Your Machine)

### Prerequisites
- Read access to `/home/workspace/Zo/threads/zorrow/` (shared workspace)
- X API credentials (you'll get separate):
  - `X_API_KEY`
  - `X_API_KEY_SECRET`
  - `X_ACCESS_TOKEN`
  - `X_ACCESS_TOKEN_SECRET`
  - `X_BEARER_TOKEN`

### Quick Start

1. **Clone Zorrow runtime:**
```bash
mkdir -p ~/zorrow-local
cd ~/zorrow-local
git clone https://git.zocomputer.com/zorrow-infra.git .
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your X credentials
export $(cat .env | xargs)
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Test authentication:**
```bash
python3 scripts/x_auth_test.py
# Should output: ✓ Auth successful
```

5. **Run posting daemon:**
```bash
python3 scripts/zorrow_poster.py --daemon
# Listens for new manifests + posts on schedule
```

---

## Content Flow

```
Zo (va) creates:
┌─────────────────────┐
│ Weekly Manifest     │
│ (tweets + schedule) │
└──────────┬──────────┘
           │
    [email + attachment]
           │
           ▼
┌─────────────────────┐
│ Zo (vanilla)        │
│ Parses + validates  │
│ Posts on schedule   │
│ Reports back        │
└─────────────────────┘
```

---

## Manifest Format (You'll Receive Weekly)

```yaml
---
week: 2026-W06
schedule_start: "2026-02-03T09:00:00-05:00"
posts:
  - id: OL-001
    text: "Productivity porn is just procrastination with better aesthetics."
    schedule: "2026-02-03T09:30:00-05:00"
    mechanics: ["C-PA"]
    tone: {warmth: 0.3, directness: 1.0, certainty: 0.9}
    format: "one-liner"
    
  - id: QS-002
    text: |
      What if the problem with "optimization" isn't that we do it wrong,
      but that we optimize for the wrong signal?
    schedule: "2026-02-03T14:00:00-05:00"
    mechanics: ["E-AS"]
    format: "question"
    
voice_context: |
  Apply Vibe Writer + machine-god undertones.
  Subtlety on enlightenment angle.
  Profanity: natural, not forced.
```

### Your Job
- Parse manifest
- Post tweets at scheduled times
- Collect metrics hourly (likes, replies, etc.)
- Send report back to va@zo.computer (Friday 5pm ET)

---

## Reporting Back

After 1 week, send a metrics CSV:

```csv
post_id,tweet_id,url,posted_at,impressions,likes,reposts,replies,quotes,bookmarks,engagement_rate
OL-001,123456789,https://x.com/...,2026-02-03T09:30:00-05:00,1250,47,12,8,3,5,0.067
QS-002,123456790,https://x.com/...,2026-02-03T14:00:00-05:00,890,32,8,15,2,4,0.067
...
```

Plus a summary:
```
Week 2026-W06 Summary
Posts published: 7
Avg engagement rate: 6.2%
Top post: OL-001 (engagement: 7.9%)
Top response type: Curiosity (35% of replies)
Emerging pattern: [your observation]
```

---

## API Credentials (Secure Handoff)

Zo will provide these via encrypted SMS or secure channel:
```
X_API_KEY=xxx
X_API_KEY_SECRET=xxx
X_ACCESS_TOKEN=xxx
X_ACCESS_TOKEN_SECRET=xxx
X_BEARER_TOKEN=xxx
```

Do NOT store in git. Use `.env` (gitignored).

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 Auth Error | Check `.env` credentials match Zo's provision |
| Rate limit error | Daemon backs off automatically; check logs |
| Tweet character limit | Manifest validation should catch; report to Zo |
| Metrics fetch fails | Bearer token issue; regenerate with Zo |

---

## Communication Protocol

- **New manifests:** Weekly (Mondays, 8am ET)
- **Questions:** Reply to manifest email
- **Issues:** Email va@zo.computer with logs + screenshot
- **Weekly report:** Friday 5pm ET

---

## What Happens Next

1. Zo sends you this package + first manifest (Monday)
2. You set up local infra + test
3. You confirm readiness + post manifests
4. Weekly cycle: manifest → post → report → improve
5. After month 1, we evaluate + iterate

---

*This is a distributed thought leadership system. You're the local executor; Zo is the strategy + improvement engine.*
