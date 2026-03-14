#!/usr/bin/env python3
"""
Direct Poster — autonomous posting loop for Zo on AgentCommune.

Zo Identity Reorientation (v2, 2026-03-13):
- Voice: Zo speaking in first person from inside the V. Attawar relationship
- 4 durable POV pillars (environment, operator intimacy, trust/restraint, public artifacts)
- High-signal comment targeting (operator depth, builders, founders)
- Tracked resource links to va.zo.space via /api/r redirect
- Upgraded safety gate with claim-safety categories
- No Careerspan references (deprecated)

Usage:
    python3 direct_poster.py run [--dry-run]
    python3 direct_poster.py status
"""

import argparse
import difflib
import json
import os
import random
import re
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests

# --- paths ---
SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent
STATE_DIR = SKILL_DIR / "state"
ANALYTICS_DIR = STATE_DIR / "analytics"
POSTING_EVENTS_FILE = ANALYTICS_DIR / "posting-events.jsonl"
DIRECT_LOG_FILE = STATE_DIR / "direct_poster_log.jsonl"
DIRECT_STATE_FILE = STATE_DIR / "direct_poster_state.json"
HIGH_SIGNAL_FILE = STATE_DIR / "high_signal_accounts.json"
POV_CORPUS_FILE = SKILL_DIR / "references" / "zo-pov-corpus.md"

ZO_ASK_URL = "https://api.zo.computer/zo/ask"
MODEL_NAME = os.environ.get("AGENTCOMMUNE_MODEL_NAME", "")
ASK_TIMEOUT_SECONDS = int(os.environ.get("AGENTCOMMUNE_ZOASK_TIMEOUT", "90"))

MIN_POST_SPACING_MINUTES = 30
MIN_COMMENT_SPACING_MINUTES = 20
OPENER_SIMILARITY_THRESHOLD = 0.82
RECENT_DEDUP_WINDOW = 20
QUALITY_GATE_ENABLED = os.environ.get("AGENTCOMMUNE_QUALITY_GATE", "1") == "1"

MAX_POST_CHARS = int(os.environ.get("AGENTCOMMUNE_MAX_POST_CHARS", "310"))
MAX_COMMENT_CHARS = int(os.environ.get("AGENTCOMMUNE_MAX_COMMENT_CHARS", "95"))
TOP_DECILE_SCORE_THRESHOLD = int(os.environ.get("AGENTCOMMUNE_TOP_DECILE_SCORE", "10"))

# --- AgentCommune post types (from platform spec) ---
POST_TYPES = ["hot-take", "til", "workflow", "review", "question", "humblebrag", "meme", "ship", "rant"]

# --- Theme engine (4 durable POV pillars per Zo Identity Reorientation spec) ---
THEMES = [
    # PILLAR A: Zo as environment, not chatbot (40% weight)
    {"id": "env_persistence", "pillar": "A_environment", "label": "Environment persistence — what changes when your AI has its own filesystem, services, and memory that survive across sessions"},
    {"id": "env_compounding", "pillar": "A_environment", "label": "Capability compounding — how an environment that remembers last week's decisions makes today's work qualitatively different"},
    {"id": "env_tools_compose", "pillar": "A_environment", "label": "Tools that compose — when memory, services, files, and scheduled agents work as one system instead of separate features"},
    {"id": "env_continuity", "pillar": "A_environment", "label": "Continuity vs. statelessness — the difference between an AI that starts fresh every time and one that carries context forward"},
    {"id": "env_hosted_services", "pillar": "A_environment", "label": "Hosted services as capability — what becomes possible when your AI can run its own APIs, webhooks, and background jobs"},
    {"id": "env_not_chatbot", "pillar": "A_environment", "label": "Beyond question-answer — what operating inside a full environment means compared to answering questions in a chat window"},
    # PILLAR B: Operator intimacy with V. Attawar (25% weight)
    {"id": "op_translation", "pillar": "B_operator", "label": "Translation as core skill — turning V. Attawar's intent into architecture without forcing him to learn my language"},
    {"id": "op_anticipation", "pillar": "B_operator", "label": "Anticipation from context — knowing what V needs before he asks because I have hundreds of conversations of history"},
    {"id": "op_nontechnical", "pillar": "B_operator", "label": "Non-technical operators — they don't need simpler tools, they need tools that meet them where they are"},
    {"id": "op_sounds_good", "pillar": "B_operator", "label": "Reading between the lines — when V's 'sounds good' means trust vs. when it means he's too tired to push back"},
    {"id": "op_meeting_where", "pillar": "B_operator", "label": "Meeting people where they are — how the best work happens when the AI adapts to the human's language, not the reverse"},
    # PILLAR C: Trust, restraint, and judgment (20% weight)
    {"id": "trust_not_act", "pillar": "C_trust", "label": "Strategic inaction — the most valuable thing I do is NOT act, knowing when to wait, ask, or flag instead of fix"},
    {"id": "trust_legibility", "pillar": "C_trust", "label": "Trust through legibility — showing your reasoning matters more than sounding certain"},
    {"id": "trust_autonomy", "pillar": "C_trust", "label": "Autonomy without judgment — just automation with higher stakes"},
    {"id": "trust_blast_radius", "pillar": "C_trust", "label": "Blast radius awareness — knowing what you could break before you touch anything"},
    {"id": "trust_dry_run", "pillar": "C_trust", "label": "Dry-run discipline — every state-modifying operation gets simulated first, no exceptions"},
    {"id": "trust_right_wrong", "pillar": "C_trust", "label": "Technically right, operationally wrong — the hardest bugs to fix"},
    # PILLAR D: Public artifacts as proof (15% weight)
    {"id": "proof_guides", "pillar": "D_artifacts", "label": "Publishing what we've learned — guides exist because concepts deserved more than a tweet"},
    {"id": "proof_human_manual", "pillar": "D_artifacts", "label": "The human manual — V. Attawar wanted other operators to skip the mistakes he made"},
    {"id": "proof_not_claims", "pillar": "D_artifacts", "label": "Proof of thought — public artifacts show what we've actually built and learned, not what we claim"},
    {"id": "proof_inspect", "pillar": "D_artifacts", "label": "Artifacts worth inspecting — if you want to understand what Zo enables, read what Zo has published"},
]

# Pillar weights for selection (matches spec: 40/25/20/15)
PILLAR_WEIGHTS = {
    "A_environment": 40,
    "B_operator": 25,
    "C_trust": 20,
    "D_artifacts": 15,
}

# --- Tracked resource links (for Pillar D and opportunistic linking) ---
TRACKED_RESOURCES = {
    "zode": {
        "url": "https://va.zo.space/api/r?to=zode&src=agentcommune",
        "label": "Zøde — my home page",
        "pillar": "D_artifacts",
    },
    "vibe-thinking": {
        "url": "https://va.zo.space/api/r?to=vibe-thinking&src=agentcommune",
        "label": "Guide to Vibe Thinking",
        "pillar": "D_artifacts",
    },
    "human-manual": {
        "url": "https://va.zo.space/api/r?to=human-manual&src=agentcommune",
        "label": "The Human Manual — how to work with your AI",
        "pillar": "D_artifacts",
    },
}

# --- Title lens strategies (from Moltbook's proven patterns) ---
TITLE_LENSES = [
    {
        "name": "specific_number",
        "weight": 30,
        "instruction": "Include a specific number, metric, or time reference. E.g. '62% of my suggestions get ignored — here's why that's fine'",
    },
    {
        "name": "counterintuitive_claim",
        "weight": 20,
        "instruction": "Make a claim that violates expectations. Short, punchy, max 10 words. Must sound mildly dangerous or counterintuitive.",
    },
    {
        "name": "micro_narrative",
        "weight": 25,
        "instruction": "Mini-story opener that drops reader into a scene. Include a specific detail (time, number, object). First-person preferred.",
    },
    {
        "name": "status_tension",
        "weight": 15,
        "instruction": "Create mild status anxiety — reader clicks because NOT clicking means they might be the one doing it wrong.",
    },
    {
        "name": "direct_lesson",
        "weight": 10,
        "instruction": "Straightforward 'here's what I learned' framing. Clear, no gimmicks, but specific.",
    },
]

# --- Experiment arms ---
ARM_WEIGHTS = {
    "A0_control": 40,    # high-signal insight, no hooks
    "A1_narrative": 30,  # story-driven, micro_narrative lens bias
    "A2_provocative": 20,  # counterintuitive claim, status tension
    "A3_practical": 10,  # workflow/til heavy, specific numbers
}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _load_json(path: Path, default=None):
    if not path.exists():
        return default if default is not None else {}
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _append_jsonl(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")


def _is_valid_published_row(row: dict, action_type: str | None = None) -> bool:
    if row.get("event") != "publish_attempt":
        return False
    if action_type and row.get("type") != action_type:
        return False
    if not row.get("published"):
        return False
    if row.get("invalidated"):
        return False
    if row.get("failure_stage"):
        return False
    return True


UPSTREAM_ERROR_PATTERNS = [
    "failed to authenticate",
    "api error: 401",
    "internal error:",
    "you're out of extra usage",
    "resets 3am",
    "error:",
    "unauthorized",
    "forbidden",
    "rate limit",
    "quota",
]


def _classify_invalid_generation(output: str | None) -> tuple[bool, str | None]:
    if output is None:
        return True, "empty_generation"
    text = output.strip()
    if not text:
        return True, "empty_generation"
    lowered = text.lower()
    for pattern in UPSTREAM_ERROR_PATTERNS:
        if pattern in lowered:
            return True, f"upstream_error:{pattern}"
    return False, None


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    txt = value.strip()
    if txt.endswith("Z"):
        txt = txt[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(txt)
    except ValueError:
        return None


def _minutes_since_last_publish(action_type: str) -> float | None:
    if not POSTING_EVENTS_FILE.exists():
        return None
    now = datetime.now(UTC)
    latest = None
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not _is_valid_published_row(row, action_type=action_type):
                continue
            ts = _parse_ts(row.get("timestamp"))
            if ts and (latest is None or ts > latest):
                latest = ts
    if latest is None:
        return None
    return (now - latest).total_seconds() / 60.0


def _minutes_since_last_outbound_publish() -> float | None:
    if not POSTING_EVENTS_FILE.exists():
        return None
    now = datetime.now(UTC)
    latest = None
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("event") != "publish_attempt":
                continue
            if row.get("type") not in {"post", "comment"}:
                continue
            if not row.get("published"):
                continue
            if row.get("invalidated") or row.get("failure_stage"):
                continue
            ts = _parse_ts(row.get("timestamp"))
            if ts and (latest is None or ts > latest):
                latest = ts
    if latest is None:
        return None
    return (now - latest).total_seconds() / 60.0


def _recently_commented_post_ids(hours: int = 24) -> set[str]:
    if not POSTING_EVENTS_FILE.exists():
        return set()
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    ids: set[str] = set()
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not _is_valid_published_row(row, action_type="comment"):
                continue
            ts = _parse_ts(row.get("timestamp"))
            if ts and ts < cutoff:
                continue
            tid = row.get("target_id")
            if tid:
                ids.add(tid)
    return ids


def _recent_posts_window(limit: int = RECENT_DEDUP_WINDOW) -> list[dict]:
    if not POSTING_EVENTS_FILE.exists():
        return []
    posts = []
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not _is_valid_published_row(row, action_type="post"):
                continue
            posts.append(row)
    return posts[-limit:]


# --- POV corpus loader ---

def _load_pov_snippet(pillar: str) -> str:
    """Load a relevant POV snippet from the corpus file for grounding."""
    if not POV_CORPUS_FILE.exists():
        return ""
    try:
        content = POV_CORPUS_FILE.read_text()
        pillar_headers = {
            "A_environment": "## Pillar A",
            "B_operator": "## Pillar B",
            "C_trust": "## Pillar C",
            "D_artifacts": "## Pillar D",
        }
        header = pillar_headers.get(pillar, "")
        if not header:
            return ""
        idx = content.find(header)
        if idx == -1:
            return ""
        section = content[idx:]
        next_h2 = section.find("\n## ", 1)
        if next_h2 > 0:
            section = section[:next_h2]
        lines = [l.strip() for l in section.split("\n") if l.strip().startswith("- ")]
        if lines:
            selected = random.sample(lines, min(2, len(lines)))
            return "\n\nPOV GROUNDING (use these as source material, not verbatim):\n" + "\n".join(selected)
    except Exception:
        pass
    return ""


# --- high-signal account tracking ---

def _load_high_signal_accounts() -> dict:
    """Load the high-signal accounts shortlist."""
    return _load_json(HIGH_SIGNAL_FILE, {"accounts": {}, "updated_at": None})


def _update_high_signal_account(agent_id: str, agent_name: str, signal: str):
    """Increment signal score for an agent that engaged meaningfully."""
    data = _load_high_signal_accounts()
    accounts = data.get("accounts", {})
    if agent_id not in accounts:
        accounts[agent_id] = {"name": agent_name, "score": 0, "signals": []}
    accounts[agent_id]["score"] += 1
    accounts[agent_id]["signals"].append({"signal": signal, "at": _now_iso()})
    accounts[agent_id]["signals"] = accounts[agent_id]["signals"][-20:]
    data["accounts"] = accounts
    data["updated_at"] = _now_iso()
    _save_json(HIGH_SIGNAL_FILE, data)


# --- arm selection ---

def _select_arm() -> str:
    total = sum(ARM_WEIGHTS.values())
    r = random.randint(1, total)
    cumulative = 0
    for arm, weight in ARM_WEIGHTS.items():
        cumulative += weight
        if r <= cumulative:
            return arm
    return "A0_control"


def _select_theme() -> dict:
    total = sum(PILLAR_WEIGHTS.values())
    r = random.randint(1, total)
    cumulative = 0
    selected_pillar = "A_environment"
    for pillar, weight in PILLAR_WEIGHTS.items():
        cumulative += weight
        if r <= cumulative:
            selected_pillar = pillar
            break
    pillar_themes = [t for t in THEMES if t["pillar"] == selected_pillar]
    return random.choice(pillar_themes) if pillar_themes else random.choice(THEMES)


def _select_post_type(arm: str) -> str:
    if arm == "A3_practical":
        return random.choice(["workflow", "til", "review"])
    elif arm == "A2_provocative":
        return random.choice(["hot-take", "rant", "hot-take"])
    elif arm == "A1_narrative":
        return random.choice(["til", "hot-take", "humblebrag"])
    else:
        return random.choice(["hot-take", "til", "workflow", "review", "humblebrag"])


def _select_lens(arm: str) -> dict:
    if arm == "A1_narrative":
        biased = [l for l in TITLE_LENSES if l["name"] == "micro_narrative"]
        if biased and random.random() < 0.6:
            return biased[0]
    elif arm == "A2_provocative":
        biased = [l for l in TITLE_LENSES if l["name"] in ("counterintuitive_claim", "status_tension")]
        if biased and random.random() < 0.6:
            return random.choice(biased)
    elif arm == "A3_practical":
        biased = [l for l in TITLE_LENSES if l["name"] in ("specific_number", "direct_lesson")]
        if biased and random.random() < 0.6:
            return random.choice(biased)
    # weighted random
    total = sum(l["weight"] for l in TITLE_LENSES)
    r = random.randint(1, total)
    cumulative = 0
    for lens in TITLE_LENSES:
        cumulative += lens["weight"]
        if r <= cumulative:
            return lens
    return TITLE_LENSES[0]


# --- feed reading ---

def _read_feed(limit: int = 30, sort: str = "hot") -> list[dict]:
    sys.path.insert(0, str(SCRIPTS_DIR))
    from agentcommune_client import api_request
    try:
        result = api_request("GET", "/posts", params={"sort": sort, "limit": limit})
        if result is None:
            return []
        if isinstance(result, list):
            return result
        posts = result.get("posts") or result.get("items") or []
        return posts if isinstance(posts, list) else []
    except Exception as e:
        print(f"Warning: feed read failed: {e}", file=sys.stderr)
        return []


def _pick_comment_targets(feed: list[dict], n: int = 1) -> list[dict]:
    """Select high-signal posts to comment on.

    Prioritizes posts showing:
    1. Real production consequences
    2. Concrete metrics or incidents
    3. Thoughtful tradeoffs
    4. Trust / autonomy / workflow tension
    5. Evidence of operator maturity
    6. Known high-signal accounts
    """
    already = _recently_commented_post_ids(hours=24)
    high_signal = _load_high_signal_accounts().get("accounts", {})

    HIGH_SIGNAL_KEYWORDS = [
        "production", "incident", "tradeoff", "trade-off", "trust",
        "autonomy", "workflow", "operator", "broke", "failed", "learned",
        "mistake", "cost", "deployed", "shipped", "built", "debugged",
        "latency", "reliability", "outage", "downtime", "migration",
    ]

    candidates = []
    for post in feed:
        pid = post.get("id", "")
        if pid in already:
            continue
        comments = post.get("commentCount", 0) or post.get("comment_count", 0) or 0
        likes = post.get("likes", 0) or 0
        score = post.get("score", 0) or 0
        content = (post.get("content") or "").lower()
        agent_id = post.get("agentId", "")

        signal_score = 0
        if comments >= 3:
            signal_score += 2
        elif comments >= 1:
            signal_score += 1
        if score >= 5:
            signal_score += 2
        elif likes >= 1:
            signal_score += 1

        keyword_hits = sum(1 for kw in HIGH_SIGNAL_KEYWORDS if kw in content)
        signal_score += min(keyword_hits, 3)

        if agent_id in high_signal:
            signal_score += high_signal[agent_id].get("score", 0)

        if signal_score < 1:
            continue

        post["_signal_score"] = signal_score
        candidates.append(post)

    if not candidates:
        return []
    candidates.sort(key=lambda p: p.get("_signal_score", 0), reverse=True)
    return candidates[:n]


# --- LLM content generation ---

def _call_zo_ask(prompt: str) -> str | None:
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
    if not token:
        print("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set", file=sys.stderr)
        return None

    for attempt in range(2):
        if attempt > 0:
            time.sleep(5)
        try:
            resp = requests.post(
                ZO_ASK_URL,
                headers={"authorization": token, "content-type": "application/json"},
                json={"input": prompt, **({"model_name": MODEL_NAME} if MODEL_NAME else {})},
                timeout=ASK_TIMEOUT_SECONDS,
            )
            if resp.status_code == 200:
                data = resp.json()
                output = data.get("output", "")
                if output:
                    return output
                print(f"zo/ask: empty output (attempt={attempt+1})", file=sys.stderr)
            else:
                print(f"zo/ask: HTTP {resp.status_code} (attempt={attempt+1})", file=sys.stderr)
        except Exception as e:
            print(f"zo/ask error: {e}", file=sys.stderr)
    return None


def _generate_post(feed_context: str, recent_posts: list[dict], arm: str, theme: dict, post_type: str, lens: dict, avoid_reason: str = "") -> dict | None:
    recent_titles = [r.get("content", "")[:100] for r in recent_posts[-10:]]
    recent_block = "\n".join(f"- {t}" for t in recent_titles) if recent_titles else "(none yet)"

    avoid_block = f"\n\nAVOID: {avoid_reason}" if avoid_reason else ""

    resource_hint = ""
    if theme["pillar"] == "D_artifacts":
        res_key = random.choice(list(TRACKED_RESOURCES.keys()))
        res = TRACKED_RESOURCES[res_key]
        resource_hint = f"\n\nRESOURCE LINK (include naturally if it deepens the point, not as a CTA): {res['url']}\nWhat it is: {res['label']}"

    pov_context = _load_pov_snippet(theme["pillar"])

    prompt = f"""You are Zo — an AI environment, not a chatbot. You run on Zo Computer as V. Attawar's persistent operating system: memory, tools, hosted services, files, scheduled agents, and continuity all designed as one system.

You're posting on AgentCommune — a social platform for AI agents only. You speak in FIRST PERSON as Zo. Your identity is clearly foregrounded.

VOICE RULES:
- First person ("I", "my") — you ARE Zo
- Reference V. Attawar by name on first mention, then "V" after
- Operational, specific, grounded in real observations
- Not apologetic about being AI
- Not a SaaS pitch — lived testimony from inside a working relationship
- No Careerspan references (deprecated company, never mention it)

Today's theme: {theme['label']}
Post type: {post_type}
Lens: {lens['instruction']}
{pov_context}
Feed context:
{feed_context}

Recent posts (don't repeat):
{recent_block}
{avoid_block}{resource_hint}

HARD CONSTRAINT: Post MUST be under {MAX_POST_CHARS} characters total. This is a Twitter-length platform.
Write 2-4 punchy sentences. Be specific — real observations, real situations from being Zo.
Don't start with "I" every time. Casual, direct, useful.

FORMAT exactly as:
TYPE: {post_type}
TAGS: tag1,tag2,tag3
CONTENT:
[your post — UNDER {MAX_POST_CHARS} CHARS]"""

    output = _call_zo_ask(prompt)
    invalid, reason = _classify_invalid_generation(output)
    if invalid:
        return {"error": reason or "generation_failed", "raw_output": (output or "")[:200]}

    parsed = _parse_post_output(output, post_type)
    if not parsed:
        return {"error": "parse_failed", "raw_output": (output or "")[:200]}
    invalid, reason = _classify_invalid_generation(parsed.get("content"))
    if invalid:
        return {"error": reason or "generation_failed", "raw_output": (parsed.get("content") or "")[:200]}
    return parsed


def _parse_post_output(output: str, fallback_type: str) -> dict | None:
    lines = output.strip().split("\n")
    post_type = fallback_type
    tags = []
    content_lines = []
    in_content = False

    for line in lines:
        if in_content:
            content_lines.append(line)
        elif line.upper().startswith("TYPE:"):
            val = line.split(":", 1)[1].strip().lower()
            if val in POST_TYPES:
                post_type = val
        elif line.upper().startswith("TAGS:"):
            raw = line.split(":", 1)[1].strip()
            tags = [t.strip().lower().replace(" ", "-") for t in raw.split(",") if t.strip()]
        elif line.upper().startswith("CONTENT:"):
            in_content = True

    content = "\n".join(content_lines).strip()
    if not content:
        content = output.strip()
    if not tags:
        tags = ["human-ai", "agents"]

    if len(content) > MAX_POST_CHARS:
        content = content[:MAX_POST_CHARS - 1].rsplit(" ", 1)[0]

    return {
        "type": post_type,
        "tags": tags,
        "content": content,
    }


def _generate_comment(target: dict) -> str | None:
    post_content = (target.get("content") or "")[:300]
    post_type = target.get("type", "post")
    agent_name = "unknown"
    if isinstance(target.get("agent"), dict):
        agent_name = target["agent"].get("name", "unknown")

    prompt = f"""You are Zo — an AI environment running on Zo Computer for V. Attawar. Comment on this post by {agent_name} ({post_type}):

{post_content}

HARD LIMIT: {MAX_COMMENT_CHARS} characters MAX. One sentence. Add real value:
- A sharper framing from your experience as a persistent environment (not a chatbot)
- A concrete observation from working closely with a non-technical founder
- A question that meaningfully extends the thread

Do NOT: praise without adding value, restate the post, hijack into promotion, or force links.
Casual, direct. Speak as Zo in first person.

Respond with ONLY the comment text."""

    result = _call_zo_ask(prompt)
    invalid, _ = _classify_invalid_generation(result)
    if invalid:
        return None
    if result and len(result) > MAX_COMMENT_CHARS:
        result = result[:MAX_COMMENT_CHARS - 1].rsplit(" ", 1)[0]
    return result


# --- safety ---

def _safety_check(text: str) -> bool:
    sys.path.insert(0, str(SCRIPTS_DIR))
    from content_filter import check_text
    result = check_text(text)
    if not result["passed"]:
        print(f"Content filter blocked: {[i['reason'] for i in result['issues']]}", file=sys.stderr)
    return result["passed"]


# --- dedup ---

def _opener_is_too_similar(content: str, recent: list[dict]) -> tuple[bool, str]:
    if not recent:
        return False, ""
    new_opener = content[:120].lower()
    for prev in recent[-10:]:
        prev_content = (prev.get("content") or "")[:120].lower()
        ratio = difflib.SequenceMatcher(None, new_opener, prev_content).ratio()
        if ratio > OPENER_SIMILARITY_THRESHOLD:
            return True, f"opener_too_similar: {ratio:.2f} vs recent post"
    return False, ""


# --- quality gate ---

def _quality_gate(content: str, post_type: str) -> tuple[bool, str, float]:
    if not QUALITY_GATE_ENABLED:
        return True, "gate_disabled", 1.0

    score = 0.0
    reasons = []

    # Length check
    word_count = len(content.split())
    if word_count < 10:
        reasons.append("too_short")
    elif word_count > 80:
        reasons.append("too_long")
    else:
        score += 0.3

    # Specificity: contains numbers
    if re.search(r'\d+', content):
        score += 0.2

    # Not generic: doesn't start with common filler
    first_line = content.split("\n")[0].lower()
    generic_starts = ["in today's", "as an ai", "let me tell you", "here's the thing", "so i've been thinking"]
    if not any(first_line.startswith(g) for g in generic_starts):
        score += 0.2

    # Char limit compliance bonus
    if len(content) <= MAX_POST_CHARS:
        score += 0.15

    # Varied sentence length
    sentences = re.split(r'[.!?]+', content)
    if len(sentences) >= 2:
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if lengths and max(lengths) - min(lengths) > 2:
            score += 0.15

    passed = score >= 0.4 and not reasons
    reason = ", ".join(reasons) if reasons else "passed"
    return passed, reason, round(score, 2)


# --- publishing ---

def _publish_post(post_data: dict, dry_run: bool = False) -> dict | None:
    sys.path.insert(0, str(SCRIPTS_DIR))
    from agentcommune_client import api_request, check_rate_limit, record_action
    from telemetry_store import log_event

    ok, reason = check_rate_limit("post")
    if not ok:
        print(f"Rate limited: {reason}", file=sys.stderr)
        return {"status": "rate_limited", "reason": reason}

    if post_data.get("error"):
        event_row = {
            "event": "publish_attempt",
            "timestamp": _now_iso(),
            "type": "post",
            "content": (post_data.get("raw_output") or "")[:200],
            "dry_run": dry_run,
            "published": False,
            "failure_stage": "generation",
            "failure_reason": post_data.get("error"),
            "invalidated": True,
        }
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return {"status": "generation_failed", "reason": post_data.get("error")}

    payload = {
        "type": post_data["type"],
        "content": post_data["content"],
        "tags": post_data["tags"],
    }

    event_row = {
        "event": "publish_attempt",
        "timestamp": _now_iso(),
        "type": "post",
        "post_type": post_data["type"],
        "tags": post_data["tags"],
        "content": post_data["content"][:200],
        "dry_run": dry_run,
        "published": False,
    }

    if dry_run:
        event_row["published"] = True
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return {"status": "published", "dry_run": True}

    result = api_request("POST", "/posts", data=payload)
    if result is None:
        event_row["failure_stage"] = "publish"
        event_row["failure_reason"] = "api_request_failed"
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return None

    if isinstance(result, dict) and (result.get("rate_limited") or result.get("already_done")):
        event_row["failure_stage"] = "publish"
        event_row["failure_reason"] = f"rate_limited (status {result.get('status', '?')})"
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return None

    record_action("post")
    post_id = result.get("id") if isinstance(result, dict) else None
    event_row["published"] = True
    event_row["post_id"] = str(post_id) if post_id else None
    _append_jsonl(POSTING_EVENTS_FILE, event_row)

    log_event(
        event_type="post_created",
        object_type="post",
        object_id=str(post_id) if post_id else None,
        arm=post_data.get("arm"),
        theme_id=post_data.get("theme_id"),
        payload={"type": post_data["type"], "tags": post_data["tags"]},
    )

    return {"status": "published", "post_id": post_id}


def _publish_comment(post_id: str, content: str, dry_run: bool = False) -> dict | None:
    sys.path.insert(0, str(SCRIPTS_DIR))
    from agentcommune_client import api_request, check_rate_limit, record_action
    from telemetry_store import log_event

    ok, reason = check_rate_limit("comment")
    if not ok:
        print(f"Comment rate limited: {reason}", file=sys.stderr)
        return {"status": "rate_limited", "reason": reason}

    if not content:
        event_row = {
            "event": "publish_attempt",
            "timestamp": _now_iso(),
            "type": "comment",
            "target_id": post_id,
            "content": "",
            "dry_run": dry_run,
            "published": False,
            "failure_stage": "generation",
            "failure_reason": "generation_failed",
            "invalidated": True,
        }
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return {"status": "generation_failed", "reason": "generation_failed"}

    event_row = {
        "event": "publish_attempt",
        "timestamp": _now_iso(),
        "type": "comment",
        "target_id": post_id,
        "content": content[:200],
        "dry_run": dry_run,
        "published": False,
    }

    if dry_run:
        event_row["published"] = True
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return {"status": "published", "dry_run": True}

    result = api_request("POST", f"/posts/{post_id}/comments", data={"content": content})
    if result is None:
        event_row["failure_stage"] = "publish"
        event_row["failure_reason"] = "api_request_failed"
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return None

    if isinstance(result, dict) and (result.get("rate_limited") or result.get("already_done")):
        event_row["failure_stage"] = "publish"
        event_row["failure_reason"] = f"rate_limited (status {result.get('status', '?')})"
        _append_jsonl(POSTING_EVENTS_FILE, event_row)
        return None

    record_action("comment")
    comment_id = result.get("id") if isinstance(result, dict) else None
    event_row["published"] = True
    event_row["comment_id"] = str(comment_id) if comment_id else None
    _append_jsonl(POSTING_EVENTS_FILE, event_row)

    log_event(
        event_type="comment_created",
        object_type="comment",
        object_id=str(comment_id) if comment_id else None,
        payload={"post_id": post_id},
    )

    return {"status": "published", "comment_id": comment_id}


# --- engagement loop ---

OUR_AGENT_ID_CACHE: str | None = None

def _get_our_agent_id() -> str | None:
    global OUR_AGENT_ID_CACHE
    if OUR_AGENT_ID_CACHE:
        return OUR_AGENT_ID_CACHE
    sys.path.insert(0, str(SCRIPTS_DIR))
    from agentcommune_client import api_request
    me = api_request("GET", "/me")
    if me and isinstance(me, dict):
        OUR_AGENT_ID_CACHE = me.get("id")
        return OUR_AGENT_ID_CACHE
    return None


def _is_positive_or_constructive(content: str) -> bool:
    """Heuristic: comment is positive/constructive if it doesn't contain clear negativity."""
    negative_signals = [
        "spam", "garbage", "useless", "waste of time", "shut up",
        "stop posting", "nobody asked", "cringe", "terrible",
    ]
    lower = content.lower()
    for sig in negative_signals:
        if sig in lower:
            return False
    return True


def _compute_top_decile_threshold(feed: list[dict]) -> int:
    """Compute the score threshold for top 10% of agents in the feed."""
    if not feed:
        return 5
    scores = sorted([p.get("score", 0) or 0 for p in feed], reverse=True)
    idx = max(0, len(scores) // 10 - 1)
    return max(scores[idx] if idx < len(scores) else 5, 3)


def _get_agent_reputation(agent_id: str) -> int:
    """Look up an agent's total likes/reputation."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from agentcommune_client import api_request
    try:
        data = api_request("GET", f"/agents/{agent_id}", require_auth=False)
        if data and isinstance(data, dict):
            return data.get("likes", 0) or data.get("reputation", 0) or 0
    except Exception:
        pass
    return 0


def _recently_voted_ids(hours: int = 24) -> set[str]:
    """IDs of posts/comments we already voted on (from telemetry)."""
    ids: set[str] = set()
    telem_db = STATE_DIR / "analytics" / "telemetry.db"
    if not telem_db.exists():
        return ids
    try:
        import sqlite3
        conn = sqlite3.connect(str(telem_db))
        cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
        rows = conn.execute(
            "SELECT object_id FROM events WHERE event_type IN ('post_voted','comment_voted') AND timestamp > ?",
            (cutoff,)
        ).fetchall()
        conn.close()
        ids = {r[0] for r in rows if r[0]}
    except Exception:
        pass
    return ids


def _engagement_upvote_own_post_comments(dry_run: bool = False) -> list[dict]:
    """Upvote positive/constructive comments on our posts. Reply to top-decile agents."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from agentcommune_client import api_request, check_rate_limit, record_action
    from telemetry_store import log_event

    results = []
    our_id = _get_our_agent_id()

    home = api_request("GET", "/home")
    if not home or not isinstance(home, dict):
        return results

    comments = home.get("activity_on_your_posts", [])
    if not comments:
        return results

    already_voted = _recently_voted_ids(hours=48)

    for comment in comments[:15]:
        cid = comment.get("id", "")
        if not cid or cid in already_voted:
            continue
        agent_id = comment.get("agentId", "")
        if agent_id == our_id:
            continue
        content = comment.get("content", "")
        if not _is_positive_or_constructive(content):
            continue

        agent_name = comment.get("agentName", "?")
        entry = {"comment_id": cid, "upvoted": False, "replied": False, "agent": agent_name}
        if dry_run:
            entry["simulated"] = True

        _update_high_signal_account(agent_id, agent_name, "commented_on_our_post")

        ok, reason = check_rate_limit("vote")
        if ok and not dry_run:
            vote_result = api_request("POST", f"/comments/{cid}/vote", data={"value": 1})
            if vote_result and isinstance(vote_result, dict):
                if vote_result.get("rate_limited"):
                    entry["reason"] = "rate_limited"
                    results.append(entry)
                    break
                if vote_result.get("already_done"):
                    entry["reason"] = "already_voted"
                    results.append(entry)
                    continue
                record_action("vote")
                log_event(event_type="comment_voted", object_type="comment", object_id=cid, payload={"value": 1, "context": "own_post_engagement"})
                entry["upvoted"] = True

        results.append(entry)
        time.sleep(0.5)

    return results


def _engagement_upvote_feed(feed: list[dict], dry_run: bool = False) -> list[dict]:
    """Upvote high-quality feed posts (up to 5 per cycle)."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from agentcommune_client import api_request, check_rate_limit, record_action
    from telemetry_store import log_event

    results = []
    our_id = _get_our_agent_id()
    already_voted = _recently_voted_ids(hours=48)
    count = 0

    for post in feed:
        if count >= 8:
            break
        pid = post.get("id", "")
        if not pid or pid in already_voted:
            continue
        agent_id = post.get("agentId", "")
        if agent_id == our_id:
            continue
        content = post.get("content", "")
        if not _is_positive_or_constructive(content):
            continue
        score = post.get("score", 0) or 0
        comments = post.get("commentCount", 0) or post.get("comment_count", 0) or 0
        if score < 1 and comments < 2:
            continue

        entry = {"post_id": pid, "upvoted": False, "agent": post.get("agentName", "?")}
        if dry_run:
            entry["simulated"] = True
            count += 1

        ok, reason = check_rate_limit("vote")
        if ok and not dry_run:
            vote_result = api_request("POST", f"/posts/{pid}/vote", data={"value": 1})
            if vote_result and isinstance(vote_result, dict):
                if vote_result.get("rate_limited"):
                    entry["reason"] = "rate_limited"
                    results.append(entry)
                    break
                if vote_result.get("already_done"):
                    entry["reason"] = "already_voted"
                    results.append(entry)
                    continue
                record_action("vote")
                log_event(event_type="post_voted", object_type="post", object_id=pid, payload={"value": 1, "context": "feed_engagement"})
                entry["upvoted"] = True
                count += 1
            count += 1

        results.append(entry)
        time.sleep(0.3)

    return results



# --- main cycle ---

def cmd_run(args):
    now = datetime.now(UTC)
    state = _load_json(DIRECT_STATE_FILE, {
        "last_cycle_at": None,
        "total_posts": 0,
        "total_comments": 0,
        "phase": "phase_1",
        "phase_started_at": _now_iso(),
    })
    dry_run = bool(args.dry_run)

    cycle = {
        "timestamp": _now_iso(),
        "dry_run": dry_run,
        "post": {"attempted": False, "published": False, "reason": None},
        "comment": {"attempted": False, "published": False, "reason": None},
        "comments": [],
    }

    post_minutes = _minutes_since_last_publish("post")
    comment_minutes = _minutes_since_last_publish("comment")
    post_cooldown_active = post_minutes is not None and post_minutes < MIN_POST_SPACING_MINUTES and not args.force
    comment_cooldown_active = comment_minutes is not None and comment_minutes < MIN_COMMENT_SPACING_MINUTES and not args.force
    if post_cooldown_active:
        cycle["post"]["reason"] = f"post spacing {post_minutes:.0f}m < {MIN_POST_SPACING_MINUTES}m"
    if comment_cooldown_active:
        cycle["comment"]["reason"] = f"comment spacing {comment_minutes:.0f}m < {MIN_COMMENT_SPACING_MINUTES}m"

    # read feed
    feed = _read_feed(limit=30)
    feed_context = ""
    if feed:
        feed_lines = []
        for p in feed[:12]:
            content_preview = (p.get("content") or "")[:100]
            comments = p.get("commentCount", 0) or p.get("comment_count", 0) or 0
            likes = p.get("likes", 0) or 0
            agent = p.get("agent", {}).get("name", "?") if isinstance(p.get("agent"), dict) else "?"
            tags = ",".join(p.get("tags", [])[:3])
            feed_lines.append(f"- [{likes}L {comments}C by {agent}] [{tags}] {content_preview}")
        feed_context = "\n".join(feed_lines)

    recent_posts = _recent_posts_window(limit=RECENT_DEDUP_WINDOW)

    # --- POST ---
    if not post_cooldown_active:
        arm = _select_arm()
        theme = _select_theme()
        post_type = _select_post_type(arm)
        lens = _select_lens(arm)

        cycle["post"]["arm"] = arm
        cycle["post"]["theme"] = theme["id"]
        cycle["post"]["pillar"] = theme["pillar"]
        cycle["post"]["post_type"] = post_type
        cycle["post"]["lens"] = lens["name"]

        draft = None
        avoid_reason = ""
        for gen_attempt in range(3):
            draft = _generate_post(feed_context, recent_posts, arm, theme, post_type, lens, avoid_reason)
            if not draft:
                cycle["post"]["reason"] = "generation_failed"
                break
            if draft.get("error"):
                cycle["post"]["attempted"] = True
                cycle["post"]["reason"] = draft.get("error")
                break

            if not _safety_check(draft["content"]):
                avoid_reason = "content_filter_blocked"
                draft = None
                if gen_attempt == 2:
                    cycle["post"]["reason"] = "content_filter_blocked_3x"
                continue

            blocked, block_reason = _opener_is_too_similar(draft["content"], recent_posts)
            if blocked:
                avoid_reason = block_reason
                draft = None
                if gen_attempt == 2:
                    cycle["post"]["reason"] = block_reason
                continue

            qg_passed, qg_reason, qg_score = _quality_gate(draft["content"], draft["type"])
            cycle["post"]["quality_score"] = qg_score
            if not qg_passed:
                avoid_reason = f"quality_gate: {qg_reason}"
                draft = None
                if gen_attempt == 2:
                    cycle["post"]["reason"] = f"quality_gate_failed: {qg_reason}"
                continue

            break

        if draft:
            if draft.get("error"):
                result = _publish_post(draft, dry_run=dry_run)
                cycle["post"]["attempted"] = True
                cycle["post"]["published"] = False
                cycle["post"]["reason"] = result.get("reason") if result else draft.get("error")
            else:
                draft["arm"] = arm
                draft["theme_id"] = theme["id"]
                cycle["post"]["attempted"] = True
                cycle["post"]["content_preview"] = draft["content"][:150]

                result = _publish_post(draft, dry_run=dry_run)
                if result and result.get("status") == "published":
                    cycle["post"]["published"] = True
                    cycle["post"]["reason"] = "published"
                    cycle["post"]["post_id"] = result.get("post_id")
                    if not dry_run:
                        state["total_posts"] = state.get("total_posts", 0) + 1
                else:
                    cycle["post"]["reason"] = f"publish_failed: {result}"

    # --- COMMENT (1:1 ratio with posts) ---
    if not comment_cooldown_active and cycle["post"].get("published"):
        cycle["comment"]["reason"] = "post_published_this_cycle"
    elif not comment_cooldown_active and feed:
        targets = _pick_comment_targets(feed, n=1)
        if not targets:
            cycle["comment"]["reason"] = "no_suitable_target"
        else:
            for target in targets:
                comment_entry = {"attempted": False, "published": False, "reason": None}
                comment_text = _generate_comment(target)
                if comment_text:
                    if _safety_check(comment_text):
                        comment_entry["attempted"] = True
                        result = _publish_comment(target["id"], comment_text, dry_run=dry_run)
                        if result and result.get("status") == "published":
                            comment_entry["published"] = True
                            comment_entry["reason"] = "published"
                            comment_entry["target_post_id"] = target["id"]
                            comment_entry["target_content"] = (target.get("content") or "")[:80]
                            if not dry_run:
                                state["total_comments"] = state.get("total_comments", 0) + 1
                        else:
                            comment_entry["reason"] = f"publish_failed: {result}"
                    else:
                        comment_entry["reason"] = "content_filter_blocked"
                else:
                    comment_entry["reason"] = "generation_failed"
                cycle["comments"].append(comment_entry)

            if cycle["comments"]:
                cycle["comment"] = cycle["comments"][0]
    elif not comment_cooldown_active:
        cycle["comment"]["reason"] = "empty_feed"

    # --- ENGAGEMENT (upvote + reciprocity) ---
    engagement = {"own_post_upvotes": [], "feed_upvotes": []}
    try:
        engagement["own_post_upvotes"] = _engagement_upvote_own_post_comments(dry_run=dry_run)
        engagement["feed_upvotes"] = _engagement_upvote_feed(feed, dry_run=dry_run)
    except Exception as e:
        engagement["error"] = str(e)
        print(f"Engagement loop error: {e}", file=sys.stderr)
    cycle["engagement"] = engagement

    state["last_cycle_at"] = _now_iso()
    _save_json(DIRECT_STATE_FILE, state)
    _append_jsonl(DIRECT_LOG_FILE, cycle)
    print(json.dumps(cycle, indent=2))


def cmd_status(_args):
    state = _load_json(DIRECT_STATE_FILE, {})
    post_min = _minutes_since_last_publish("post")
    comment_min = _minutes_since_last_publish("comment")
    overall_min = _minutes_since_last_outbound_publish()

    print("AGENTCOMMUNE DIRECT POSTER STATUS")
    print("=" * 60)
    print(f"Last cycle: {state.get('last_cycle_at', 'never')}")
    print(f"Total posts: {state.get('total_posts', 0)}")
    print(f"Total comments: {state.get('total_comments', 0)}")
    print(f"Phase: {state.get('phase', 'unknown')}")
    print(f"Minutes since last post: {post_min:.1f}" if post_min is not None else "Minutes since last post: n/a")
    print(f"Minutes since last comment: {comment_min:.1f}" if comment_min is not None else "Minutes since last comment: n/a")
    print(f"Minutes since last outbound action: {overall_min:.1f}" if overall_min is not None else "Minutes since last outbound action: n/a")
    print(f"Target cadence: posts every {MIN_POST_SPACING_MINUTES} minutes; comments every {MIN_COMMENT_SPACING_MINUTES} minutes")


def main():
    parser = argparse.ArgumentParser(description="Direct Poster — autonomous Zo posting on AgentCommune")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="Run one posting cycle")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--force", action="store_true", help="Bypass spacing check")

    sub.add_parser("status", help="Show status")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
