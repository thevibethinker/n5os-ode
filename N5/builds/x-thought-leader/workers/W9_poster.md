---
created: 2026-01-09
worker_id: W9
component: Tweet Poster
status: pending
depends_on: [W2, W8]
---

# W9: Tweet Poster

## Objective
Post approved tweets as replies to original tweets.

## Output Files
- `Projects/x-thought-leader/src/poster.py`

## Dependencies
- W2 (X API) — uses post_reply method
- W8 (Approval Handler) — receives approved drafts

## Core Functions

```python
def post_approved_tweet(
    db_path: str,
    draft_id: str
) -> dict:
    """
    Post an approved draft as a reply.
    
    1. Get draft from DB
    2. Get original tweet ID
    3. Post reply via X API
    4. Store posted tweet ID
    5. Update draft status to 'posted'
    6. Log to our_tweets table
    
    Returns: {"success": bool, "posted_tweet_id": str, "error": str}
    """

def log_posted_tweet(
    db_path: str,
    draft: dict,
    posted_tweet_id: str
) -> None:
    """
    Record what we posted for:
    - Voice learning
    - Pattern tracking
    - Analytics
    """
```

## Rate Limit Awareness

Basic tier: **17 tweets/24h**

This is tight! System should:
```python
def check_daily_post_limit(db_path: str) -> dict:
    """
    Returns:
        {
            "posts_today": int,
            "limit": 17,
            "remaining": int,
            "can_post": bool
        }
    """
    
def warn_if_near_limit(posts_today: int) -> str | None:
    """Return warning message if close to limit."""
    if posts_today >= 15:
        return f"⚠️ {17 - posts_today} posts remaining today"
```

## Posting Flow

1. Receive approved draft from approval handler
2. Check daily limit
3. If limit reached, queue for tomorrow + notify V
4. Otherwise, post reply
5. Verify post succeeded (get tweet ID back)
6. Log everything

## Error Handling

- Rate limit hit → Queue for later, notify V
- API error → Retry once, then mark failed + notify
- Duplicate detection → Skip if same text posted recently

## Confirmation to V

After successful post:
```
✅ Posted! Your reply to @asanwal:
"[tweet text]"
https://x.com/thevibethinker/status/XXXXX
(14 posts remaining today)
```

## Acceptance Criteria
- [ ] Posts replies correctly to original tweets
- [ ] Respects daily posting limit
- [ ] Logs all posted tweets
- [ ] Sends confirmation SMS
- [ ] Handles errors gracefully
