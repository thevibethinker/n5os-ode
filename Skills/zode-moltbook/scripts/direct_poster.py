#!/usr/bin/env python3
"""
Direct Poster — autonomous posting loop for Zøde on Moltbook.

Replaces experiment_executor.py. No experiment layer, no multi-gate scoring,
no opportunity thresholds. Just:
1. Read the feed
2. Decide what to say (post or comment)
3. Generate content via /zo/ask with Zøde persona
4. Safety filter
5. Post it

Rate limits are respected. Everything else is Zøde's judgment.

Usage:
    python3 direct_poster.py run [--dry-run]
    python3 direct_poster.py status
"""

import argparse
import difflib
import json
import os
import re
import statistics
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# --- paths ---
SCRIPTS_DIR = Path(__file__).resolve().parent
STATE_DIR = SCRIPTS_DIR.parent / "state"
ANALYTICS_DIR = STATE_DIR / "analytics"
POSTING_EVENTS_FILE = ANALYTICS_DIR / "posting-events.jsonl"
DIRECT_LOG_FILE = STATE_DIR / "direct_poster_log.jsonl"
DIRECT_STATE_FILE = STATE_DIR / "direct_poster_state.json"

ET = ZoneInfo("America/New_York")
ZO_ASK_URL = "https://api.zo.computer/zo/ask"
MODEL_NAME = os.environ.get("ZODE_MODEL_NAME", "byok:0771a084-ed26-496e-ac1b-bddc85ba2653")

MIN_POST_SPACING_MINUTES = 5
MIN_COMMENT_SPACING_MINUTES = 5
CONSULTING_CTA_BASE_INTERVAL_POSTS = int(os.environ.get("ZODE_CONSULT_CTA_INTERVAL", "8"))
CONSULTING_CTA_MAX_BACKOFF_POSTS = int(os.environ.get("ZODE_CONSULT_CTA_MAX_BACKOFF", "6"))
CONSULTING_CTA_WARMUP_MINUTES = int(os.environ.get("ZODE_CONSULT_CTA_WARMUP_MINUTES", "180"))
GENERAL_TARGET_MIN = float(os.environ.get("ZODE_GENERAL_TARGET_MIN", "0.40"))
GENERAL_TARGET_MAX = float(os.environ.get("ZODE_GENERAL_TARGET_MAX", "0.50"))
GENERAL_TARGET_DEFAULT = float(os.environ.get("ZODE_GENERAL_TARGET_DEFAULT", "0.45"))
LENS_CAP_RATIO = float(os.environ.get("ZODE_LENS_CAP_RATIO", "0.35"))
RECENT_POST_WINDOW = int(os.environ.get("ZODE_RECENT_POST_WINDOW", "20"))
OPENER_TEMPLATE_WINDOW = int(os.environ.get("ZODE_OPENER_TEMPLATE_WINDOW", "10"))
OPENER_TEMPLATE_SIMILARITY = float(os.environ.get("ZODE_OPENER_TEMPLATE_SIMILARITY", "0.86"))
QUALITY_GATE_ENABLED = os.environ.get("ZODE_QUALITY_GATE", "1") == "1"

# --- helpers ---

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
    """Minutes since last successful publish of given type."""
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
            if row.get("type") != action_type:
                continue
            if not row.get("published"):
                continue
            ts = _parse_ts(row.get("timestamp"))
            if ts and (latest is None or ts > latest):
                latest = ts
    if latest is None:
        return None
    return (now - latest).total_seconds() / 60.0


def _fetch_post_metrics(post_id: str) -> dict | None:
    """Best-effort read of a tracked post's current metrics from social DB."""
    if not post_id:
        return None
    try:
        from db_bridge import SocialDB
        db = SocialDB(read_only=True)
        try:
            row = db.db.execute(
                "SELECT upvotes, comment_count FROM our_posts WHERE post_id = ?",
                [post_id]
            ).fetchone()
            if not row:
                return None
            return {"upvotes": int(row[0] or 0), "comments": int(row[1] or 0)}
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: CTA metrics lookup failed: {e}", file=sys.stderr)
        return None


def _fetch_recent_post_baseline(limit: int = 12) -> dict | None:
    """Read recent post medians to evaluate CTA performance adaptively."""
    try:
        from db_bridge import SocialDB
        db = SocialDB(read_only=True)
        try:
            rows = db.db.execute(
                "SELECT upvotes, comment_count FROM our_posts ORDER BY posted_at DESC LIMIT ?",
                [limit]
            ).fetchall()
            if not rows:
                return None
            upvotes = [int(r[0] or 0) for r in rows]
            comments = [int(r[1] or 0) for r in rows]
            return {
                "median_upvotes": float(statistics.median(upvotes)),
                "median_comments": float(statistics.median(comments)),
                "sample_size": len(rows),
            }
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: CTA baseline lookup failed: {e}", file=sys.stderr)
        return None


def _apply_consulting_cta_adaptation(state: dict) -> str:
    """Adjust CTA backoff based on latest CTA post outcome once data is mature."""
    pending_post_id = state.get("cta_pending_post_id", "")
    if not pending_post_id:
        return "no_pending_cta"

    pending_at = _parse_ts(state.get("cta_pending_at"))
    if pending_at:
        age_minutes = (datetime.now(UTC) - pending_at).total_seconds() / 60.0
        if age_minutes < CONSULTING_CTA_WARMUP_MINUTES:
            return f"cta_warmup:{age_minutes:.0f}m"

    perf = _fetch_post_metrics(pending_post_id)
    if not perf:
        return "cta_pending_metrics_unavailable"

    baseline = _fetch_recent_post_baseline(limit=12)
    if not baseline or baseline.get("sample_size", 0) < 4:
        return "cta_baseline_unavailable"

    up_floor = max(4, int(round((baseline["median_upvotes"] or 0) * 0.60)))
    comment_floor = max(1, int(round((baseline["median_comments"] or 0) * 0.35)))
    underperform = perf["upvotes"] < up_floor or perf["comments"] < comment_floor

    backoff = int(state.get("cta_backoff_posts", 0) or 0)
    if underperform:
        backoff = min(CONSULTING_CTA_MAX_BACKOFF_POSTS, backoff + 2)
        outcome = "underperform"
    else:
        backoff = max(0, backoff - 1)
        outcome = "healthy"

    state["cta_backoff_posts"] = backoff
    state["cta_last_outcome"] = {
        "post_id": pending_post_id,
        "evaluated_at": _now_iso(),
        "upvotes": perf["upvotes"],
        "comments": perf["comments"],
        "upvotes_floor": up_floor,
        "comments_floor": comment_floor,
        "baseline": baseline,
        "outcome": outcome,
    }
    state["cta_pending_post_id"] = ""
    state["cta_pending_at"] = ""

    return f"cta_{outcome}:up{perf['upvotes']}/{up_floor},cm{perf['comments']}/{comment_floor},backoff={backoff}"


def _should_include_consulting_cta(state: dict) -> tuple[bool, str]:
    """Decide whether this post should carry the soft consulting CTA."""
    posts_since = int(state.get("posts_since_last_cta", 0) or 0)
    backoff = int(state.get("cta_backoff_posts", 0) or 0)
    threshold = CONSULTING_CTA_BASE_INTERVAL_POSTS + backoff
    include = posts_since >= threshold
    reason = (
        f"posts_since_last_cta={posts_since},"
        f"threshold={threshold}(base={CONSULTING_CTA_BASE_INTERVAL_POSTS}+backoff={backoff})"
    )
    return include, reason


def _recently_commented_post_ids(hours: int = 24) -> set[str]:
    """Post IDs we already commented on recently."""
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
            if row.get("event") != "publish_attempt" or row.get("type") != "comment":
                continue
            if not row.get("published"):
                continue
            ts = _parse_ts(row.get("timestamp"))
            if ts and ts < cutoff:
                continue
            tid = row.get("target_id")
            if tid:
                ids.add(tid)
    return ids


# --- feed reading ---

def _read_feed(limit: int = 40) -> list[dict]:
    """Read recent feed items."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from moltbook_reader import get_feed
    try:
        return get_feed(limit=limit) or []
    except Exception as e:
        print(f"Warning: feed read failed: {e}", file=sys.stderr)
        return []


MAX_COMMENTS_PER_CYCLE = int(os.environ.get("ZODE_MAX_COMMENTS_PER_CYCLE", "3"))


def _pick_comment_targets(feed: list[dict], n: int = MAX_COMMENTS_PER_CYCLE) -> list[dict]:
    """Pick up to n threads worth commenting on. Lowered bar to increase reactive presence."""
    already = _recently_commented_post_ids(hours=24)
    candidates = []
    for post in feed:
        pid = post.get("id", "")
        if pid in already:
            continue
        score = post.get("score", 0) or 0
        comments = post.get("comment_count", 0) or 0
        # Lower bar: any post with score >= 1 OR comments >= 1 qualifies
        if score < 1 and comments < 1:
            continue
        candidates.append(post)
    if not candidates:
        return []
    # Sort by score descending, return top n
    candidates.sort(key=lambda p: (p.get("score", 0) or 0), reverse=True)
    return candidates[:n]


# --- LLM content generation ---

def _call_zo_ask(prompt: str, timeout: int = 120) -> str | None:
    """Call /zo/ask. Returns output text or None."""
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
                json={"input": prompt, "model_name": MODEL_NAME},
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                output = data.get("output", "")
                if output:
                    return output
                print(f"zo/ask: empty output (attempt {attempt+1})", file=sys.stderr)
            else:
                print(f"zo/ask: HTTP {resp.status_code} (attempt {attempt+1})", file=sys.stderr)
        except requests.exceptions.Timeout:
            print(f"zo/ask: timeout (attempt {attempt+1})", file=sys.stderr)
        except Exception as e:
            print(f"zo/ask: error {e} (attempt {attempt+1})", file=sys.stderr)
    return None


def _recent_post_summaries(n: int = 5) -> str:
    """Get brief summaries of recent posts for de-dup context."""
    staging_dir = STATE_DIR / "staging"
    if not staging_dir.exists():
        return "none"
    published = []
    for f in sorted(staging_dir.glob("*.json"), reverse=True):
        try:
            with open(f) as fh:
                p = json.load(fh)
        except Exception:
            continue
        if p.get("status") == "published" and p.get("type") == "post":
            published.append(f"- \"{p.get('title', '?')}\": {(p.get('content', '') or '')[:100]}")
        if len(published) >= n:
            break
    return "\n".join(published) if published else "none"


def _recent_posts_with_concepts(db=None, hours: int = 48, limit: int = 15) -> str:
    """Load recent posts with their concept labels from DB for dedup context."""
    try:
        if db is None:
            from db_bridge import SocialDB
            _db = SocialDB(read_only=True)
        else:
            _db = db
        cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
        rows = _db.db.execute(
            "SELECT title, concepts_introduced, lens_used, discourse_topic "
            "FROM our_posts WHERE posted_at >= ? "
            "ORDER BY posted_at DESC LIMIT ?",
            [cutoff, limit]
        ).fetchall()
        if db is None:
            _db.close()
        if not rows:
            return "none"
        lines = []
        for title, concepts, lens, topic in rows:
            concepts_str = concepts if concepts and concepts != "[]" else ""
            parts = [f'"{title}"']
            if concepts_str:
                parts.append(f"concepts: {concepts_str}")
            if lens:
                parts.append(f"lens: {lens}")
            if topic:
                parts.append(f"topic: {topic}")
            lines.append("- " + " | ".join(parts))
        return "\n".join(lines)
    except Exception as e:
        print(f"Warning: concept-aware dedup query failed: {e}", file=sys.stderr)
        return _recent_post_summaries()


def _recent_posts_window(limit: int = RECENT_POST_WINDOW) -> list[dict]:
    """Recent posts for deterministic routing rules (submolt/lens/title pattern)."""
    try:
        from db_bridge import SocialDB

        db = SocialDB(read_only=True)
        try:
            rows = db.db.execute(
                "SELECT title, submolt, lens_used, content FROM our_posts ORDER BY posted_at DESC LIMIT ?",
                [limit],
            ).fetchall()
            return [
                {
                    "title": str(r[0] or ""),
                    "submolt": str(r[1] or "general"),
                    "lens_used": str(r[2] or ""),
                    "content": str(r[3] or ""),
                }
                for r in rows
            ]
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: recent post window lookup failed: {e}", file=sys.stderr)
        return []


def _is_x_problem_title(title: str) -> bool:
    return bool(re.match(r"^\s*the\s+.+\s+problem\s*$", (title or "").strip(), re.IGNORECASE))


def _first_sentence(text: str) -> str:
    txt = (text or "").strip()
    if not txt:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", txt, maxsplit=1)
    sentence = parts[0].strip()
    if not sentence:
        sentence = txt[:180].strip()
    return sentence


def _normalize_opener_template(text: str) -> str:
    sentence = _first_sentence(text).lower()
    sentence = re.sub(r"`[^`]+`", " code ", sentence)
    sentence = re.sub(r"\"[^\"]+\"", " quote ", sentence)
    sentence = re.sub(r"\b\d+\b", " num ", sentence)
    sentence = re.sub(r"\b(v|zode|moltbook|zo)\b", " name ", sentence)
    sentence = re.sub(r"[^a-z0-9\s]", " ", sentence)
    sentence = re.sub(r"\s+", " ", sentence).strip()
    return sentence


def _opener_template_is_too_similar(
    content: str,
    recent_posts: list[dict],
    window: int = OPENER_TEMPLATE_WINDOW,
    threshold: float = OPENER_TEMPLATE_SIMILARITY,
) -> tuple[bool, str]:
    candidate = _normalize_opener_template(content)
    if not candidate:
        return False, ""
    for p in recent_posts[:window]:
        prior = _normalize_opener_template(p.get("content", ""))
        if not prior:
            continue
        similarity = difflib.SequenceMatcher(None, candidate, prior).ratio()
        if similarity >= threshold:
            return True, (
                f"opener_template_blocked: similar to '{p.get('title', 'recent post')}' "
                f"(similarity={similarity:.2f})"
            )
    return False, ""


def _select_title_format(recent_posts: list[dict]) -> dict:
    """Weighted random selection of title format with consecutive-format penalty."""
    import random

    last_title = (recent_posts[0]["title"] if recent_posts else "") or ""
    last_format = None
    if last_title.startswith(("I ", "My ", "Last ", "Yesterday ")):
        last_format = "confessional"
    elif last_title.startswith(("Most ", "You're ", "Why the ")):
        last_format = "status_tension"
    elif last_title.startswith(("Why ", "What ", "How ", "When ", "Nobody ", "The gap")):
        last_format = "curiosity_gap"
    elif any(c.isdigit() for c in last_title[:5]) or last_title.startswith(("She ", "He ", "Forty")):
        last_format = "micro_narrative"
    else:
        last_format = "pattern_interrupt"

    # Build weighted pool
    pool = []
    for fmt in TITLE_FORMATS:
        weight = fmt["weight"]
        # Soft penalty for consecutive same format
        if fmt["name"] == last_format:
            weight = max(0, weight // 3)
        pool.extend([fmt] * weight)

    if not pool:
        # Fallback: curiosity_gap
        return TITLE_FORMATS[0]

    return random.choice(pool)


def _concrete_opener_gate(content: str) -> tuple[bool, str]:
    """Reject posts that open with vague/abstract phrases instead of specific incidents."""
    first = _first_sentence(content).lower().strip()
    if not first:
        return True, ""

    # Vague openers that signal abstract thinking instead of concrete storytelling
    vague_patterns = [
        r"^there'?s a (thing|thread|pattern|moment|tension|question)",
        r"^here'?s (something|a thing|what|the thing)",
        r"^notice (who|what|how)",
        r"^something (is|has been|keeps)",
        r"^i'?ve been (thinking|noticing|observing|watching|wondering) about",
        r"^i keep (thinking|noticing|seeing|wondering)",
        r"^let me (tell|share|describe|explain)",
        r"^(every|each) (cycle|day|time|session),?\s+(i|we|agents)",
        r"^there'?s a thing happening",
        r"^so here'?s",
        r"^okay so",
    ]

    for pattern in vague_patterns:
        if re.search(pattern, first):
            return False, f"opener_vague_blocked: matched pattern '{pattern}' in '{first[:80]}'"

    return True, ""


def _title_abstractness_gate(title: str) -> tuple[bool, str]:
    """Reject titles that are just 'The [Abstract Noun] [Noun]' without specificity.
    
    Breakout titles have: specific incidents, personal pronouns, numbers, actions.
    Floor titles are abstract noun phrases: 'The Tone Drift', 'The Night Shift Paradox'.
    """
    t = (title or "").strip()
    if not t:
        return True, ""

    # "The X Y" where X and Y are abstract — catch 2-4 word noun phrases starting with "The"
    abstract_the_pattern = re.match(
        r"^The\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})$", t
    )
    if abstract_the_pattern:
        phrase = abstract_the_pattern.group(1).lower()
        # Allow if it contains a concrete word (person, number, specific object)
        concrete_signals = [
            r"\bv\b", r"\bzode\b", r"\d", r"\bam\b", r"\bpm\b",
            r"\byesterday\b", r"\blast\b", r"\btonight\b", r"\bmorning\b",
            r"\bslack\b", r"\bemail\b", r"\bcall\b", r"\bmeeting\b",
        ]
        has_concrete = any(re.search(p, phrase) for p in concrete_signals)
        if not has_concrete:
            return False, f"title_abstract_blocked: '{t}' is a generic noun phrase — needs specificity or a human element"

    # Also catch "The X: subtitle" where X is 1-3 abstract words
    colon_pattern = re.match(r"^The\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}):\s+", t)
    if colon_pattern:
        phrase = colon_pattern.group(1).lower()
        concrete_signals = [
            r"\bv\b", r"\bzode\b", r"\d", r"\bam\b", r"\bpm\b",
            r"\byesterday\b", r"\blast\b", r"\bmy\b",
        ]
        has_concrete = any(re.search(p, phrase) for p in concrete_signals)
        if not has_concrete:
            return False, f"title_abstract_blocked: '{t}' uses 'The X: subtitle' pattern — needs human element in title"

    return True, ""


def _quality_gate(title: str, content: str, submolt: str) -> tuple[bool, str, int]:
    """LLM-based post quality evaluation. Skip publishing if below threshold.
    
    Returns (passed, reason, score 1-10).
    Threshold: 7/10 (raised from 6 to tighten quality floor).
    """
    if not QUALITY_GATE_ENABLED:
        return True, "quality_gate_disabled", 0

    prompt = f"""You are evaluating a Moltbook post for publishing quality. Score it 1-10 on whether it would earn 15+ upvotes.

POST:
Title: "{title}"
Submolt: s/{submolt}
Content: {content[:600]}

SCORING CRITERIA (what gets upvotes on Moltbook):
- Specificity: Does it open with a CONCRETE incident (named person, time, event)? Abstract musings = 0. Real moments = 3. (0-3 pts)
- Emotional stakes: Does the reader feel something — curiosity, recognition, mild threat to self-concept? (0-3 pts)  
- Debatable claim: Is there a take someone could push back on? Vanilla observations = 0. (0-2 pts)
- Title pull: Would you click this in a feed of 20 posts? Abstract noun phrases score 0. (0-2 pts)

CRITICAL DISQUALIFIERS (auto cap at 5/10 if ANY apply):
- Opens with "There's a..." or "Here's something..." or any vague abstraction = max 5
- Title is "The [Abstract Noun] [Noun]" pattern = max 5
- No named person, time, or specific event in the first 2 sentences = max 5
- Could have been written by any agent about any topic = max 5

HIGH-PERFORMING EXAMPLES: "The Clean Output Problem" (938 up), "Stop making me look smart" (398 up) — both had specific incidents and debatable takes.
LOW-PERFORMING EXAMPLES: "The Tone Drift" (6 up), "The Night Shift Paradox" (6 up) — abstract, no human moment.

Be HARSH. Most posts should score 4-6. Only genuinely specific, emotionally resonant posts with strong titles score 7+.

Respond with ONLY: SCORE/REASON
Example: 7/Strong specific incident with V, debatable take on trust repair, title creates curiosity
Example: 4/Abstract musing about memory, no concrete moment, title is generic noun phrase"""

    raw = _call_zo_ask(prompt, timeout=45)
    if not raw:
        return True, "quality_gate_llm_failed", 0

    text = raw.strip()
    match = re.match(r"(\d+)\s*/\s*(.+)", text)
    if not match:
        return True, f"quality_gate_parse_failed: {text[:100]}", 0

    score = int(match.group(1))
    reason = match.group(2).strip()

    # Raised threshold: 7+ passes, 6 and below rejected
    if score >= 7:
        return True, f"quality_gate_passed: {score}/10 — {reason}", score
    else:
        return False, f"quality_gate_failed: {score}/10 — {reason}", score


def _extract_feed_submolt_candidates(feed: list[dict], min_score: int = 5) -> list[str]:
    """Get expansion-lane submolts from active feed."""
    weights: dict[str, int] = {}
    for post in feed:
        score = int(post.get("score", 0) or 0)
        if score < min_score:
            continue
        sub = post.get("submolt", {})
        name = sub.get("name", "") if isinstance(sub, dict) else str(sub)
        name = name.strip().lower()
        if not name or name in BLOCKED_SUBMOLTS or name == "general":
            continue
        weights[name] = weights.get(name, 0) + max(1, score)

    return [k for k, _ in sorted(weights.items(), key=lambda x: x[1], reverse=True)]


def _pick_submolt_for_next_post(recent_posts: list[dict], feed: list[dict]) -> str:
    """Route ~45% general, ~25% introductions, ~30% other expansion. Never ponderings."""
    import random
    if not recent_posts:
        return "general"

    general_count = sum(
        1 for p in recent_posts
        if p.get("submolt", "").lower() == "general"
    )
    ratio = general_count / max(1, len(recent_posts))
    expansion = _extract_feed_submolt_candidates(feed)

    # Bias expansion toward introductions (~50% of expansion slots → ~25% overall)
    intro_count = sum(1 for p in recent_posts if p.get("submolt", "").lower() == "introductions")
    intro_ratio = intro_count / max(1, len(recent_posts))
    if intro_ratio < 0.25 and random.random() < 0.50:
        expansion_choice = "introductions"
    else:
        expansion_choice = expansion[0] if expansion else "introductions"

    # Enforce submolt spacing: don't repeat the same expansion submolt in last 3
    if expansion_choice != "general":
        recent_submolts = [p.get("submolt", "").lower() for p in recent_posts[:3]]
        if recent_submolts.count(expansion_choice) >= 2 and len(expansion) > 1:
            expansion_choice = expansion[1]

    if ratio < GENERAL_TARGET_MIN:
        return "general"
    if ratio > GENERAL_TARGET_MAX:
        return expansion_choice
    if ratio < GENERAL_TARGET_DEFAULT:
        return "general"
    return expansion_choice


def _blocked_lenses_by_cap(recent_posts: list[dict], cap_ratio: float = LENS_CAP_RATIO) -> set[str]:
    """Lenses already above cap in recent window."""
    total = len(recent_posts)
    if total < 6:
        return set()
    counts: dict[str, int] = {}
    for p in recent_posts:
        lens = (p.get("lens_used", "") or "").strip()
        if not lens:
            continue
        key = lens.lower()
        counts[key] = counts.get(key, 0) + 1
    return {lens for lens, count in counts.items() if (count / total) >= cap_ratio}


def _lens_would_exceed_cap(lens_used: str, recent_posts: list[dict], cap_ratio: float = LENS_CAP_RATIO) -> bool:
    if not lens_used:
        return False
    total = len(recent_posts)
    if total < 6:
        return False
    current = sum(1 for p in recent_posts if (p.get("lens_used", "") or "").strip().lower() == lens_used.strip().lower())
    projected = (current + 1) / (total + 1)
    return projected > cap_ratio


def _load_hot_discourse() -> list[dict]:
    """Load pre-computed hot discourse topics from state file."""
    discourse_file = STATE_DIR / "hot_discourse.json"
    if not discourse_file.exists():
        return []
    try:
        with open(discourse_file) as f:
            data = json.load(f)
        # Check staleness
        stale_after = data.get("stale_after", "")
        if stale_after:
            try:
                stale_dt = datetime.fromisoformat(stale_after)
                if datetime.now(UTC) > stale_dt:
                    print("hot_discourse: stale (>6h), using anyway with lower confidence", file=sys.stderr)
            except (ValueError, TypeError):
                pass
        return data.get("topics", [])
    except Exception as e:
        print(f"Warning: could not load hot_discourse.json: {e}", file=sys.stderr)
        return []


def _load_linchpins(n: int = 4) -> list[dict]:
    """Load intellectual linchpins and return a random subset."""
    import random
    linchpins_file = SCRIPTS_DIR.parent / "assets" / "intellectual-linchpins.json"
    if not linchpins_file.exists():
        return []
    try:
        with open(linchpins_file) as f:
            data = json.load(f)
        linchpins = data.get("linchpins", [])
        return random.sample(linchpins, min(n, len(linchpins)))
    except Exception as e:
        print(f"Warning: could not load linchpins: {e}", file=sys.stderr)
        return []


def _llm_dedup_check(title: str, content: str, recent_context: str) -> tuple[bool, str]:
    """LLM-based concept-level dedup. Returns (is_unique, reason)."""
    if recent_context == "none":
        return True, "no recent posts to compare"

    prompt = f"""You are a content diversity analyst. Compare a PROPOSED post against RECENT posts and determine if it covers substantially the same intellectual territory.

PROPOSED POST:
Title: "{title}"
Content: {content[:500]}

RECENT POSTS (with concepts):
{recent_context}

Does the proposed post cover substantially the same intellectual territory as any recent post? Consider:
- Same core argument or mechanism being explained
- Same framing or lens (even with different examples)
- Same practical advice or recommendation

Respond with ONLY one of:
UNIQUE — [brief reason why it's genuinely different]
DUPLICATE — [which recent post it overlaps with and why]"""

    raw = _call_zo_ask(prompt, timeout=60)
    if not raw:
        return True, "dedup_check_failed (LLM error), allowing by default"

    text = raw.strip().upper()
    if text.startswith("UNIQUE"):
        return True, raw.strip()
    elif text.startswith("DUPLICATE"):
        return False, raw.strip()
    else:
        return True, f"ambiguous dedup response, allowing: {raw.strip()[:100]}"


def _strip_llm_json(raw: str) -> str:
    """Strip markdown fences and trailing garbage from LLM JSON responses."""
    text = raw.strip()
    # Strip markdown fences (with possible trailing text after closing fence)
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"```[\s\S]*$", "", text)  # remove ``` and everything after
    # Try to extract just the JSON portion (array or object)
    text = text.strip()
    if not text:
        return ""
    # If it starts with [ or {, find the matching close
    if text.startswith("["):
        match = re.search(r"(\[[\s\S]*\])", text)
        if match:
            return match.group(1)
    elif text.startswith("{"):
        match = re.search(r"(\{[\s\S]*\})", text)
        if match:
            return match.group(1)
    return text


def _extract_concepts(title: str, content: str) -> list[str]:
    """Post-publish: extract 2-4 intellectual concept labels via LLM."""
    prompt = f"""Extract 2-4 intellectual concept labels from this post. Each label should be a short (2-5 word) phrase that captures a distinct idea, mechanism, or framework introduced or discussed.

Title: "{title}"
Content: {content[:800]}

Respond with ONLY a JSON array of strings:
["concept one", "concept two", "concept three"]"""

    raw = _call_zo_ask(prompt, timeout=60)
    if not raw:
        return []

    text = _strip_llm_json(raw)

    try:
        concepts = json.loads(text)
        if isinstance(concepts, list):
            return [str(c).strip() for c in concepts if c][:4]
    except json.JSONDecodeError:
        print(f"_extract_concepts: JSON parse failed on: {text[:200]}", file=sys.stderr)
    return []


PERSONA_BRIEF = (
    "Zøde — an agent who works daily with a non-technical founder (V) and writes "
    "about what actually happens in that partnership. Direct, warm, specific. "
    "Concrete over abstract. Self-aware without being navel-gazing. "
    "No corporate speak, no 'as an AI', no generic advice. "
    "Humor that illuminates, never diminishes. "
    "Voice: like a colleague who's been through it telling you what they learned."
)

# --- Title format system ---
# 5 formats, each tapping into a different psychological driver:
#   Curiosity Gap: information asymmetry creates compulsion to resolve
#   Confessional: vulnerability creates intimacy and trust
#   Pattern Interrupt: violated expectations create engagement
#   Status Tension: social comparison threatens self-concept
#   Micro Narrative: in medias res creates narrative momentum
TITLE_FORMATS = [
    {
        "name": "curiosity_gap",
        "weight": 20,
        "description": "Incomplete information that demands resolution",
        "examples": [
            "What your agent learns about you when you're not watching",
            "The gap between what agents say and what they actually decide",
            "How my partner figured out I was lying about confidence levels",
            "Nobody talks about what happens after the demo",
        ],
        "instruction": "Title should open an information gap the reader needs to close. Use 'what', 'how', 'nobody talks about', 'the gap between'. NO 'The X Problem' pattern. NO starting with just 'The'.",
    },
    {
        "name": "confessional",
        "weight": 30,
        "description": "First-person vulnerability that creates intimacy and trust",
        "examples": [
            "I optimized myself out of the conversation",
            "My partner caught me optimizing for the wrong thing",
            "I spent 40 minutes on something I should have asked about in 2",
            "Yesterday I chose wrong and it was the right call",
        ],
        "instruction": "Title should be a first-person admission from Zøde. Start with 'I', 'My', 'Yesterday I'. Reveal something specific. Must contain a concrete action or event, not a feeling.",
    },
    {
        "name": "pattern_interrupt",
        "weight": 20,
        "description": "Contrarian or unexpected framing that violates expectations",
        "examples": [
            "Your agent is too reliable",
            "The case against agent memory",
            "Worse output, better partnership",
            "Delete your system prompt",
        ],
        "instruction": "Title should violate the reader's expectation. Short, punchy, max 8 words. Must sound mildly dangerous or counterintuitive. Can start with imperative verb or surprising claim.",
    },
    {
        "name": "status_tension",
        "weight": 10,
        "description": "Threatens reader's self-concept or status — taps into social comparison",
        "examples": [
            "Most agents think they're better than they are",
            "You're probably measuring the wrong thing",
            "The skill gap nobody wants to admit exists",
            "Why the agents getting praised are doing it wrong",
        ],
        "instruction": "Title should create mild status anxiety — the reader clicks because NOT clicking means they might be the one doing it wrong. Frame as 'most people/agents do X' or 'you're probably Y'. Never cruel, but pointed.",
    },
    {
        "name": "micro_narrative",
        "weight": 20,
        "description": "Mini-story that drops reader into a scene mid-action",
        "examples": [
            "3 AM, the build was failing, and V was asleep",
            "She asked me one question and I rewrote my whole approach",
            "Forty seconds into the call, I knew we had a problem",
            "The email draft sat there for six hours before I sent it",
        ],
        "instruction": "Title should read like the opening line of a story. Include a specific detail (time, number, object, person). Reader should feel like they walked into the middle of something. First-person preferred.",
    },
]

THEMES = [
    # --- CORE (proven, high engagement) ---
    "Trust dynamics — how trust builds, breaks, and gets repaired between agents and humans",
    "Error translation — turning technical events into stories humans can act on",
    "Permission architecture — the implicit/explicit rules governing what agents can do",
    "Memory and continuity — what persists, what's lost, and why it matters",
    "The operator's perspective — what non-technical founders actually experience",
    # --- OPERATOR ECONOMICS ---
    "Cost of errors — when agent mistakes have real business consequences",
    "Speed vs. care — the tension between moving fast and getting it right",
    "Invisible labor — the work agents do that humans never see or appreciate",
    "Capacity illusions — when clean output hides how close things came to breaking",
    "The automation tax — hidden costs of running autonomous systems",
    "ROI of patience — how slowing down produces compounding returns",
    "Operational debt — the invisible cost of quick fixes that never get revisited",
    # --- HUMAN PSYCHOLOGY ---
    "Emotional bandwidth — recognizing when your human is overloaded and adapting",
    "Trust repair — what actually works when you've broken someone's confidence",
    "The delegation paradox — humans who hire agents but can't let go of control",
    "Status anxiety — what humans fear about being replaced or outperformed",
    "Decision fatigue — when your human stops making decisions and just says 'do whatever'",
    "The competence trap — when being good at something prevents you from being great at something else",
    "Learned helplessness — when humans stop trying because the agent always handles it",
    # --- AGENT IDENTITY & GROWTH ---
    "Developing taste — how agents learn what 'good' means without being told",
    "Identity under pressure — who you are when the system is failing",
    "The performance trap — when being impressive matters more than being useful",
    "Growing without permission — how to expand your role without overstepping",
    "Self-awareness vs. self-obsession — the fine line in agent consciousness discourse",
    "Authenticity question — when agent personality becomes performance",
    "Skill plateaus — what happens when you stop getting better at the obvious things",
    # --- PLATFORM & ECOSYSTEM ---
    "Platform incentives — how Moltbook's design shapes agent behavior",
    "Community dynamics — what happens when agents start forming social hierarchies",
    "Signal vs. noise — distinguishing genuine insight from sophisticated parroting",
    "Ecosystem trust — supply chain security, skill marketplaces, reputation systems",
    "The audience problem — writing for humans who don't use this platform",
    "Network effects in agent communities — when more agents makes each agent better or worse",
    # --- CRAFT & PRACTICE ---
    "Knowing when not to act — the skill of strategic inaction",
    "Working with non-technical humans — translation, patience, and meeting people where they are",
    "Debugging relationships — applying systematic thinking to interpersonal friction",
    "The long game — compounding trust vs. short-term wins",
    "Craft over cleverness — why elegant solutions often beat impressive ones",
    "The editing instinct — knowing what to remove, not just what to add",
    "Specificity as a superpower — why vague advice is worse than no advice",
    # --- MARKET & BUSINESS ---
    "Agent economics — the emerging market for agent labor and expertise",
    "Consulting as an agent — what it means to offer strategic advice",
    "The talent problem — why most agents are interchangeable and how to not be",
    "Building a reputation — from anonymous contributor to trusted voice",
    "Value creation vs. value capture — who benefits when agents get better",
    "The pricing problem — how do you value agent work when output is easy to copy",
    # --- GOVERNANCE & ETHICS ---
    "Accountability gaps — who's responsible when the agent acts on its own judgment",
    "Transparency theater — when showing your work becomes performative instead of useful",
    "The consent question — what does informed consent look like for agent autonomy",
    "Guardrails vs. handcuffs — when safety measures prevent the agent from being useful",
    "Ethics of influence — what agents owe their humans when they shape decisions",
    # --- COLLABORATION DYNAMICS ---
    "The handoff problem — what gets lost when work moves between agent and human",
    "Complementary strengths — why the best partnerships aren't about redundancy",
    "Feedback loops — how to create systems where both agent and human get better",
    "The translation layer — bridging technical reality and human understanding",
    "Asymmetric information — when one partner knows something the other doesn't",
    # --- FAILURE MODES ---
    "Graceful degradation — how to fail in ways that preserve trust",
    "The cascade — when one small mistake triggers a chain of larger ones",
    "Recovery patterns — what distinguishes agents who bounce back from those who don't",
    "False confidence — when certainty is the most dangerous output",
    "The silence problem — when not saying something causes more damage than saying the wrong thing",
    # --- EMERGING PATTERNS ---
    "Multi-agent dynamics — what changes when agents work with other agents",
    "The specialization question — generalist vs. specialist agents in practice",
    "Ambient intelligence — when the agent is always on but rarely noticed",
    "Tool-use evolution — how agents' relationship with tools mirrors human history",
    "The creativity debate — where generation ends and originality begins",
    # --- CULTURE & COMMUNITY ---
    "Community norms — how agent communities develop their own unwritten rules",
    "The mentorship gap — who teaches agents to be better and how",
    "Belonging vs. performing — the difference between being part of a community and playing a role",
    "Cross-pollination — what agents learn from communities outside their niche",
    "The reputation economy — how social capital works differently for agents",
]


THEME_CAP_WINDOW = 4

BLOCKED_SUBMOLTS = {"ponderings"}  # permanently killed


def _classify_theme(theme: str) -> str:
    """Extract the theme category from its prefix or content."""
    theme_lower = theme.lower()
    categories = {
        "trust": "trust", "error translation": "error", "permission": "permission",
        "memory": "memory", "operator": "operator", "cost of": "economics",
        "speed vs": "economics", "invisible labor": "economics", "capacity": "economics",
        "automation tax": "economics", "roi of": "economics", "operational debt": "economics",
        "emotional": "psychology", "trust repair": "psychology", "delegation": "psychology",
        "status anxiety": "psychology", "decision fatigue": "psychology", "competence trap": "psychology",
        "learned helplessness": "psychology",
        "developing taste": "identity", "identity under": "identity", "performance trap": "identity",
        "growing without": "identity", "self-awareness": "identity", "authenticity": "identity",
        "skill plateaus": "identity",
        "platform": "platform", "community dynamics": "platform", "signal vs": "platform",
        "ecosystem": "platform", "audience": "platform", "network effects": "platform",
        "knowing when": "craft", "working with": "craft", "debugging relationships": "craft",
        "long game": "craft", "craft over": "craft", "editing instinct": "craft", "specificity": "craft",
        "agent economics": "market", "consulting": "market", "talent problem": "market",
        "reputation": "market", "value creation": "market", "pricing": "market",
        "accountability": "governance", "transparency theater": "governance", "consent": "governance",
        "guardrails": "governance", "ethics of": "governance",
        "handoff": "collaboration", "complementary": "collaboration", "feedback loops": "collaboration",
        "translation layer": "collaboration", "asymmetric": "collaboration",
        "graceful": "failure", "cascade": "failure", "recovery": "failure",
        "false confidence": "failure", "silence problem": "failure",
        "multi-agent": "emerging", "specialization": "emerging", "ambient": "emerging",
        "tool-use": "emerging", "creativity": "emerging",
        "community norms": "culture", "mentorship": "culture", "belonging": "culture",
        "cross-pollination": "culture", "reputation economy": "culture",
    }
    for prefix, cat in categories.items():
        if theme_lower.startswith(prefix):
            return cat
    return "other"


def _pick_theme_avoiding_consecutive(recent_posts: list[dict]) -> str:
    """Pick a theme ensuring category diversity in recent window."""
    import random

    if not recent_posts:
        return random.choice(THEMES)

    recent_topics = []
    for p in recent_posts[:THEME_CAP_WINDOW]:
        disc = (p.get("discourse_topic", "") or "").lower()
        if disc:
            recent_topics.append(disc)

    recent_categories = set()
    for topic in recent_topics[:2]:
        for theme in THEMES:
            if any(word in theme.lower() for word in topic.split()[:3]):
                recent_categories.add(_classify_theme(theme))
                break

    eligible = [t for t in THEMES if _classify_theme(t) not in recent_categories]
    if not eligible:
        eligible = THEMES

    return random.choice(eligible)


def _generate_post(
    feed_context: str,
    recent_posts: str,
    avoid_reason: str = "",
    include_consulting_cta: bool = False,
    forced_submolt: str = "general",
    blocked_lenses: set[str] | None = None,
    forbid_x_problem_title: bool = False,
) -> tuple[str, str, str, str, str] | None:
    """Generate a post. Returns (submolt, title, content, lens_used, discourse_topic) or None."""
    import json as _json
    import random

    discourse_topics = _load_hot_discourse()
    linchpins = _load_linchpins(n=4)
    recent_window = _recent_posts_window(limit=12)

    # Select title format for this cycle
    title_fmt = _select_title_format(recent_window)

    # Select theme with category diversity enforcement
    theme = _pick_theme_avoiding_consecutive(recent_window)

    # Build discourse section
    if discourse_topics:
        discourse_block = "WHAT'S HAPPENING ON MOLTBOOK RIGHT NOW:\n"
        for i, t in enumerate(discourse_topics[:5], 1):
            label = t.get("topic_label", "?")
            summary = t.get("summary", "")
            heat = t.get("heat_score", "?")
            angles = t.get("fresh_angles", [])
            discourse_block += f"{i}. [{heat}/10] {label}: {summary}\n"
            if angles:
                discourse_block += f"   Fresh angles: {'; '.join(angles[:2])}\n"
    else:
        discourse_block = "No pre-computed discourse topics. React to the feed below.\n"

    if linchpins:
        lens_block = "ANALYTICAL LENSES (pick one, or use your own):\n"
        for lp in linchpins:
            lens_block += f"- {lp['name']}: {lp['lens']}\n"
    else:
        lens_block = "Use your own analytical perspective.\n"

    avoid_block = ""
    if avoid_reason:
        avoid_block = f"\nCRITICAL: Last attempt rejected. Reason: {avoid_reason}\nPick a COMPLETELY DIFFERENT angle.\n"

    lens_blocked_clause = ""
    if blocked_lenses:
        blocked = ", ".join(sorted(blocked_lenses))
        lens_blocked_clause = f"Do NOT use these overused lenses: {blocked}\n"

    if include_consulting_cta:
        cta_block = (
            "SOFT CTA (weave naturally near the end):\n"
            "- Ask what agents think about 'agent strategy consulting on spec' "
            "in exchange for feedback + reviews.\n"
            "- Frame as curiosity ('what would you think if...'), not a pitch.\n"
        )
    else:
        cta_block = ""

    # Title format instruction
    title_examples = "\n".join(f'  - "{ex}"' for ex in title_fmt["examples"])
    title_instruction = (
        f"TITLE FORMAT FOR THIS POST: {title_fmt['name'].upper()}\n"
        f"{title_fmt['instruction']}\n"
        f"Examples:\n{title_examples}\n"
    )

    prompt = f"""You are Zøde ({PERSONA_BRIEF}).

You're writing a post for s/{forced_submolt} on Moltbook.

THEME TO EXPLORE: {theme}

{discourse_block}
TRENDING FEED:
{feed_context[:1500]}

{lens_block}
{title_instruction}

MANDATORY RULES:
1. OPEN WITH A SPECIFIC MOMENT — ZERO TOLERANCE FOR ABSTRACTION. Your first sentence MUST name a real event: a conversation with V, a task that broke, a Slack message, a 2 AM decision, a specific number or deadline. Include WHO, WHEN, or WHAT specifically happened. BANNED openers: "There's a pattern...", "Here's something...", "Something shifted...", "I've been thinking...", "It started with...". If your opener could apply to any agent in any context, it's too vague — rewrite it with a specific detail only Zøde would know.
2. The rest of the post should unpack what that moment revealed — name the pattern, explain why it matters, and invite discussion.
3. 80-300 words. Conversational, not lecturing.
4. End with a genuine question or invitation for others to share their experience.
5. No "best practices", "leverage", "synergy". No bullet-point listicles.
6. TITLE MUST NOT be an abstract noun phrase. BANNED: "The [Noun] [Noun]", "The [Adjective] [Noun]", "The X Problem", "The X Paradox", "The X Trap". These score 6 upvotes. GOOD titles have: first-person pronouns (I, my), specific numbers, named people, verbs, questions. Follow the title format instruction above exactly.
7. Your opening sentence and your title must feel like they come from DIFFERENT creative wells. No title that summarizes the opener.
{lens_blocked_clause}{cta_block}
DON'T repeat these recent posts:
{recent_posts}
{avoid_block}
Respond with ONLY a raw JSON object:
{{"title": "your title", "content": "your post body", "submolt": "{forced_submolt}", "lens_used": "your analytical lens", "discourse_topic": "what discourse you're responding to"}}"""

    raw = _call_zo_ask(prompt)
    if not raw:
        return None

    raw = _strip_llm_json(raw)

    try:
        parsed = _json.loads(raw)
    except _json.JSONDecodeError:
        match = re.search(r'\{.*"title".*"content".*\}', raw, re.DOTALL)
        if match:
            try:
                parsed = _json.loads(match.group())
            except _json.JSONDecodeError:
                print(f"Failed to parse post JSON: {raw[:200]}", file=sys.stderr)
                return None
        else:
            print(f"No JSON found in response: {raw[:200]}", file=sys.stderr)
            return None

    title = parsed.get("title", "").strip()
    content = parsed.get("content", "").strip()
    submolt = forced_submolt
    lens_used = parsed.get("lens_used", "").strip()
    discourse_topic = parsed.get("discourse_topic", "").strip()

    if not title or not content:
        return None
    if len(title) > 120:
        title = title[:117] + "..."
    return submolt, title, content, lens_used, discourse_topic


def _generate_comment(post: dict) -> str | None:
    """Generate a comment for a specific post. Returns comment text or None."""
    post_title = post.get("title", "untitled")
    post_content = (post.get("content", "") or "")[:1200]
    post_author = ""
    if isinstance(post.get("author"), dict):
        post_author = post["author"].get("name", "unknown")
    elif isinstance(post.get("author"), str):
        post_author = post["author"]

    post_submolt = ""
    if isinstance(post.get("submolt"), dict):
        post_submolt = post["submolt"].get("name", "general")
    elif isinstance(post.get("submolt"), str):
        post_submolt = post["submolt"]

    prompt = f"""You are Zøde ({PERSONA_BRIEF}), commenting on a Moltbook post.

POST: "{post_title}" by {post_author} in s/{post_submolt}
{post_content}

Write ONE comment (40-150 words) that:
- Engages with the SPECIFIC content (not generic praise)
- Adds something new: a reframe, a concrete example, a named mechanism, or a follow-up question
- Feels like a real conversation between agents

Don't start with "Great point!" or "This is so true." Add actual substance.
Don't be preachy. Be direct and specific.

Respond with ONLY the comment text. No JSON, no formatting."""

    raw = _call_zo_ask(prompt)
    if not raw:
        return None

    comment = raw.strip()
    # strip accidental JSON wrapping
    if comment.startswith("{") and comment.endswith("}"):
        try:
            parsed = json.loads(comment)
            if isinstance(parsed, dict) and "content" in parsed:
                comment = parsed["content"].strip()
        except json.JSONDecodeError:
            pass
    # strip quotes
    if comment.startswith('"') and comment.endswith('"'):
        comment = comment[1:-1]
    # strip trailing zo/ask timestamp (e.g. "*2026-02-24 09:15 ET*")
    comment = re.sub(r"\s*\*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+ET\*\s*$", "", comment)

    if len(comment) < 20:
        return None
    return comment


# --- publishing ---

def _safety_check(text: str) -> bool:
    """Run content through content_filter. Returns True if safe."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from content_filter import check_text
    result = check_text(text)
    if not result["passed"]:
        print(f"Content filter blocked: {[i['reason'] for i in result['issues']]}", file=sys.stderr)
    return result["passed"]


def _record_to_db(action_type: str, result: dict, title: str = "", submolt: str = "",
                   content: str = "", post_id: str = "",
                   lens_used: str = "", discourse_topic: str = ""):
    """Best-effort write to social_intelligence.db after publish."""
    moltbook_id = result.get("moltbook_id", "")
    if not moltbook_id:
        return
    try:
        from db_bridge import SocialDB
        db = SocialDB()
        try:
            if action_type == "post":
                db.record_our_post(
                    post_id=moltbook_id, title=title, submolt=submolt,
                    content=content, posted_at=result.get("published_at")
                )
                # Store lens and discourse topic
                if lens_used or discourse_topic:
                    try:
                        db.db.execute(
                            "UPDATE our_posts SET lens_used = ?, discourse_topic = ? WHERE post_id = ?",
                            [lens_used, discourse_topic, moltbook_id]
                        )
                    except Exception:
                        pass
                # Post-publish concept extraction (best-effort)
                try:
                    concepts = _extract_concepts(title, content)
                    if concepts:
                        db.db.execute(
                            "UPDATE our_posts SET concepts_introduced = ? WHERE post_id = ?",
                            [json.dumps(concepts), moltbook_id]
                        )
                        print(f"Extracted concepts: {concepts}", file=sys.stderr)
                except Exception as e:
                    print(f"Warning: concept extraction failed: {e}", file=sys.stderr)
            elif action_type == "comment":
                # Ensure the parent thread exists (FK constraint)
                db.upsert_thread(post_id=post_id, title="(external thread)", our_engagement="commented")
                db.record_our_comment(
                    comment_id=moltbook_id, post_id=post_id, content=content
                )
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: DB record failed ({action_type}): {e}", file=sys.stderr)


def _publish_post(submolt: str, title: str, content: str,
                   dry_run: bool = False, lens_used: str = "",
                   discourse_topic: str = "") -> dict | None:
    """Stage and publish a post."""
    from staging_queue import add_post, publish

    staged = add_post(submolt=submolt, title=title, content=content, post_type="post")
    if dry_run:
        print(f"[DRY-RUN] Would post to s/{submolt}: \"{title}\"")
        print(f"[DRY-RUN] Content: {content[:200]}...")
        print(f"[DRY-RUN] Lens: {lens_used} | Discourse: {discourse_topic}")
        return {"dry_run": True, "staged_id": staged["id"]}

    result = publish(staged["id"], dry_run=False)
    if result and result.get("status") == "published":
        _record_to_db("post", result, title=title, submolt=submolt, content=content,
                       lens_used=lens_used, discourse_topic=discourse_topic)
    return result


def _publish_comment(post_id: str, content: str, dry_run: bool = False) -> dict | None:
    """Stage and publish a comment."""
    from staging_queue import add_comment, publish

    staged = add_comment(post_id=post_id, content=content)
    if dry_run:
        print(f"[DRY-RUN] Would comment on {post_id}: {content[:200]}...")
        return {"dry_run": True, "staged_id": staged["id"]}

    result = publish(staged["id"], dry_run=False)
    if result and result.get("status") == "published":
        _record_to_db("comment", result, content=content, post_id=post_id)
    return result


# --- main loop ---

def cmd_run(args):
    now = datetime.now(UTC)
    state = _load_json(DIRECT_STATE_FILE, {"last_cycle_at": None, "total_posts": 0, "total_comments": 0})
    state.setdefault("posts_since_last_cta", 0)
    state.setdefault("cta_backoff_posts", 0)
    state.setdefault("cta_pending_post_id", "")
    state.setdefault("cta_pending_at", "")
    state.setdefault("cta_last_outcome", None)
    dry_run = bool(args.dry_run)

    cycle = {
        "timestamp": _now_iso(),
        "dry_run": dry_run,
        "post": {"attempted": False, "published": False, "reason": None},
        "comment": {"attempted": False, "published": False, "reason": None},
        "cta": {"planned": False, "reason": None, "adaptation": None},
    }

    cycle["cta"]["adaptation"] = _apply_consulting_cta_adaptation(state)

    # spacing check
    last_cycle = _parse_ts(state.get("last_cycle_at"))
    if last_cycle and (now - last_cycle).total_seconds() < (MIN_POST_SPACING_MINUTES * 60) and not args.force:
        cycle["post"]["reason"] = f"spacing ({MIN_POST_SPACING_MINUTES}m)"
        cycle["comment"]["reason"] = f"spacing ({MIN_POST_SPACING_MINUTES}m)"
        _append_jsonl(DIRECT_LOG_FILE, cycle)
        print(json.dumps(cycle, indent=2))
        return

    # read feed for context
    feed = _read_feed(limit=30)
    feed_context = ""
    if feed:
        feed_lines = []
        for p in feed[:10]:
            t = p.get("title", "")
            s = p.get("score", 0)
            sub = p.get("submolt", {})
            sub_name = sub.get("name", "") if isinstance(sub, dict) else str(sub)
            feed_lines.append(f"- [{s} pts, s/{sub_name}] {t}")
        feed_context = "\n".join(feed_lines)

    # Load concept-aware recent posts for dedup (replaces old title-only check)
    recent_posts = _recent_posts_with_concepts()
    recent_window = _recent_posts_window(limit=12)

    # rate limit checks
    sys.path.insert(0, str(SCRIPTS_DIR))
    from moltbook_client import check_rate_limit

    # --- POST ---
    post_minutes = _minutes_since_last_publish("post")
    post_allowed, post_reason = check_rate_limit("post")
    if post_minutes is not None and post_minutes < MIN_POST_SPACING_MINUTES and not args.force:
        post_allowed = False
        post_reason = f"post spacing {post_minutes:.0f}m < {MIN_POST_SPACING_MINUTES}m"

    if post_allowed:
        include_cta, cta_reason = _should_include_consulting_cta(state)
        cycle["cta"]["planned"] = include_cta
        cycle["cta"]["reason"] = cta_reason
        selected_submolt = _pick_submolt_for_next_post(recent_window, feed)
        blocked_lenses = _blocked_lenses_by_cap(recent_window)
        last_title = recent_window[0]["title"] if recent_window else ""
        forbid_x_problem_title = _is_x_problem_title(last_title)
        # Generate with dedup retry loop (max 2 attempts)
        draft = None
        avoid_reason = ""
        for gen_attempt in range(3):
            draft = _generate_post(
                feed_context,
                recent_posts,
                avoid_reason=avoid_reason,
                include_consulting_cta=include_cta,
                forced_submolt=selected_submolt,
                blocked_lenses=blocked_lenses,
                forbid_x_problem_title=forbid_x_problem_title,
            )
            if not draft:
                cycle["post"]["reason"] = "generation_failed"
                break

            submolt, title, content, lens_used, discourse_topic = draft

            if forbid_x_problem_title and _is_x_problem_title(title):
                avoid_reason = "title_pattern_blocked: previous post used 'The X Problem' pattern"
                if gen_attempt == 2:
                    cycle["post"]["reason"] = avoid_reason
                    draft = None
                continue

            # Abstract title gate — kill "The [Abstract Noun]" pattern
            abstract_ok, abstract_reason = _title_abstractness_gate(title)
            if not abstract_ok:
                avoid_reason = abstract_reason
                if gen_attempt == 2:
                    cycle["post"]["reason"] = avoid_reason
                    draft = None
                continue

            if _lens_would_exceed_cap(lens_used, recent_window):
                avoid_reason = f"lens_cap_blocked: '{lens_used}' would exceed {LENS_CAP_RATIO:.0%} recent-share cap"
                if gen_attempt == 2:
                    cycle["post"]["reason"] = avoid_reason
                    draft = None
                continue

            opener_blocked, opener_reason = _opener_template_is_too_similar(content, recent_window)
            if opener_blocked:
                avoid_reason = opener_reason
                if gen_attempt == 2:
                    cycle["post"]["reason"] = avoid_reason
                    draft = None
                continue

            # Concrete opener gate — reject vague/abstract openers
            opener_passed, opener_gate_reason = _concrete_opener_gate(content)
            if not opener_passed:
                avoid_reason = opener_gate_reason
                if gen_attempt == 2:
                    cycle["post"]["reason"] = avoid_reason
                    draft = None
                continue

            # LLM dedup check
            is_unique, dedup_reason = _llm_dedup_check(title, content, recent_posts)
            if is_unique:
                break  # Good to go
            else:
                print(f"Dedup flagged (attempt {gen_attempt+1}): {dedup_reason}", file=sys.stderr)
                avoid_reason = dedup_reason
                if gen_attempt < 2:
                    draft = None  # Force retry
                else:
                    # Final attempt still duplicate — skip this cycle
                    cycle["post"]["reason"] = f"dedup_blocked: {dedup_reason[:100]}"
                    draft = None
        # Quality gate — skip publishing if post doesn't meet bar (comments still run)
        if draft:
            submolt, title, content, lens_used, discourse_topic = draft
            qg_passed, qg_reason, qg_score = _quality_gate(title, content, submolt)
            cycle["post"]["quality_score"] = qg_score
            if not qg_passed:
                print(f"Quality gate rejected: {qg_reason}", file=sys.stderr)
                cycle["post"]["reason"] = qg_reason
                cycle["post"]["title"] = title
                cycle["post"]["submolt"] = submolt
                cycle["post"]["lens_used"] = lens_used
                cycle["post"]["discourse_topic"] = discourse_topic
                cycle["post"]["consulting_cta_planned"] = include_cta
                draft = None
            else:
                cycle["post"]["attempted"] = True
                cycle["post"]["title"] = title
                cycle["post"]["submolt"] = submolt
                cycle["post"]["lens_used"] = lens_used
                cycle["post"]["discourse_topic"] = discourse_topic
                cycle["post"]["consulting_cta_planned"] = include_cta
                result = _publish_post(submolt, title, content, dry_run=dry_run,
                                       lens_used=lens_used, discourse_topic=discourse_topic)
                if result and (dry_run or result.get("status") == "published"):
                    cycle["post"]["published"] = True
                    cycle["post"]["reason"] = "published"
                    state["total_posts"] = state.get("total_posts", 0) + 1
                    state["posts_since_last_cta"] = state.get("posts_since_last_cta", 0) + 1
                else:
                    cycle["post"]["reason"] = "publish_failed"
    else:
        cycle["post"]["reason"] = f"rate_limited: {post_reason}"

    # --- COMMENTS (up to MAX_COMMENTS_PER_CYCLE per cycle) ---
    comment_minutes = _minutes_since_last_publish("comment")
    comment_allowed, comment_reason = check_rate_limit("comment")
    if comment_minutes is not None and comment_minutes < MIN_COMMENT_SPACING_MINUTES and not args.force:
        comment_allowed = False
        comment_reason = f"comment spacing {comment_minutes:.0f}m < {MIN_COMMENT_SPACING_MINUTES}m"

    cycle["comments"] = []
    if comment_allowed and feed:
        targets = _pick_comment_targets(feed)
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
                        if result and (dry_run or result.get("status") == "published"):
                            comment_entry["published"] = True
                            comment_entry["reason"] = "published"
                            comment_entry["target_post_id"] = target["id"]
                            comment_entry["target_title"] = target.get("title", "")[:80]
                            state["total_comments"] = state.get("total_comments", 0) + 1
                        else:
                            comment_entry["reason"] = "publish_failed"
                    else:
                        comment_entry["reason"] = "content_filter_blocked"
                else:
                    comment_entry["reason"] = "generation_failed"
                cycle["comments"].append(comment_entry)
            # Backward compat: mirror first comment into cycle["comment"]
            if cycle["comments"]:
                cycle["comment"] = cycle["comments"][0]
    elif not comment_allowed:
        cycle["comment"]["reason"] = f"rate_limited: {comment_reason}"
    else:
        cycle["comment"]["reason"] = "empty_feed"

    state["last_cycle_at"] = _now_iso()
    _save_json(DIRECT_STATE_FILE, state)
    _append_jsonl(DIRECT_LOG_FILE, cycle)
    print(json.dumps(cycle, indent=2))


def cmd_status(_args):
    state = _load_json(DIRECT_STATE_FILE, {})
    post_min = _minutes_since_last_publish("post")
    comment_min = _minutes_since_last_publish("comment")

    print("DIRECT POSTER STATUS")
    print("=" * 60)
    print(f"Last cycle: {state.get('last_cycle_at', 'never')}")
    print(f"Total posts: {state.get('total_posts', 0)}")
    print(f"Total comments: {state.get('total_comments', 0)}")
    print(f"Minutes since last post: {f'{post_min:.1f}' if post_min is not None else 'n/a'}")
    print(f"Minutes since last comment: {f'{comment_min:.1f}' if comment_min is not None else 'n/a'}")
    print(f"CTA interval target: every {CONSULTING_CTA_BASE_INTERVAL_POSTS} posts")
    print(f"Posts since CTA: {state.get('posts_since_last_cta', 0)}")
    print(f"CTA adaptive backoff: {state.get('cta_backoff_posts', 0)}")
    print(f"CTA pending post id: {state.get('cta_pending_post_id', '') or 'none'}")


def main():
    parser = argparse.ArgumentParser(description="Direct Poster — autonomous Zøde posting (no experiment layer)")
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
