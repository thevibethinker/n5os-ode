# X Thought Leader: Orchestration & Architecture

## System Overview

The X Thought Leader system is a **Twitter Radar** designed to help V engage with high-value conversations.

**Philosophy:**
- **V writes the tweets.** The AI does not auto-post or auto-draft by default.
- **AI acts as a scout.** It scans the horizon, identifies opportunities that match V's worldview, and alerts V.
- **AI acts as a sparring partner.** It suggests *angles* (premises), not just copy.

## Core Loop (Hourly)

1. **Poll**: `polling_agent.py` fetches new tweets from monitored accounts.
2. **Correlate**: `correlator.py` scores tweets against V's 105 positions in `positions.db`.
3. **Radar**: `opportunity_radar.py` scans for high-correlation tweets (score >= 0.5) that haven't been alerted.
4. **Alert**: The system sends an SMS to V with the opportunity and 3 brainstorming angles.

## Components

### 1. Polling (`src/polling_agent.py`)
- **Input:** `config/monitored_accounts.yaml`
- **Action:** Fetches user timelines via Apify/Twitter API.
- **Output:** Saves raw tweets to `db/tweets.db` with status `new`.

### 2. Correlation (`src/correlator.py`)
- **Input:** New tweets from DB.
- **Action:**
  - Embeds tweet content.
  - Compares against `positions.db` embeddings.
  - Calculates `correlation_score` (0.0 - 1.0).
- **Output:** Updates tweet status to `correlated`. Records `position_correlations`.

### 3. Opportunity Radar (`src/opportunity_radar.py`)
- **Input:** Correlated tweets with score >= 0.5.
- **Action:**
  - Checks `alerts` table to ensure we haven't bugged V about this yet.
  - Generates "Premises" (brainstorming angles) using V's persona.
  - Creates an alert record.
- **Output:** Prints formatted alert text (consumed by the hourly agent) or sends SMS directly.

### 4. Voice Learner (`src/voice_learner.py`)
- **Input:** V's tweet archive (`tweets.duckdb` / `voice_examples.md`).
- **Action:** Analyzes V's style to update `voice_variants.yaml`.
- **Purpose:** Ensures that when V *does* ask for a draft, it sounds like him.

## Data Schema

### `tweets`
- `id`: Tweet ID
- `content`: Text
- `author`: Handle
- `correlation_score`: Float
- `status`: new -> correlated -> alerted -> responded

### `alerts`
- `id`: UUID
- `tweet_id`: FK
- `status`: pending -> sent

### `positions` (External: N5/db/positions.db)
- Source of truth for V's worldview.

## Configuration

- `config/monitored_accounts.yaml`: Who we watch.
- `config/voice_variants.yaml`: How we sound (for drafts).
- `config/account_candidates.yaml`: Potential new accounts to watch.

## Operations

**Manual Scan:**
```bash
python3 src/opportunity_radar.py --scan
```

**Generate Draft (On Demand):**
```bash
python3 src/opportunity_radar.py --draft <TWEET_ID> --instruction "Disagree with the second point"
```

**Add Account:**
```bash
python3 src/add_account.py @handle
```

