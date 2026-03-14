---
created: 2026-01-09
worker_id: W2
component: X API Wrapper
status: pending
depends_on: []
---

# W2: X API Wrapper

## Objective
Create a Python module wrapping X API v2 with auth, rate limiting, and core operations.

## Output Files
- `Projects/x-thought-leader/src/x_api.py`

## Environment Variables
```
X_API_KEY       - Consumer/API key
X_API_SECRET    - Consumer/API secret
X_BEARER_KEY    - Bearer token for app-only auth
```

## API Tier: Basic ($200/mo)
- **Read**: 10,000 tweets/month
- **Write**: 17 tweets/24h per user, 50K/month app-level
- **Rate limits**: 15 requests/15min for most endpoints

## Core Interface

```python
import os
import time
from dataclasses import dataclass
from typing import Optional
import requests
from requests_oauthlib import OAuth1

@dataclass
class Tweet:
    id: str
    text: str
    author_id: str
    author_username: str
    created_at: str
    retweet_count: int
    like_count: int
    reply_count: int

@dataclass
class User:
    id: str
    username: str
    name: str
    description: str
    followers_count: int

class XAPIClient:
    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self):
        self.api_key = os.environ["X_API_KEY"]
        self.api_secret = os.environ["X_API_SECRET"]
        self.bearer_token = os.environ["X_BEARER_KEY"]
        self._rate_limits = {}  # endpoint -> {remaining, reset_time}
    
    # === Authentication ===
    
    def _bearer_headers(self) -> dict:
        """Headers for app-only auth (reading)."""
        return {"Authorization": f"Bearer {self.bearer_token}"}
    
    def _oauth1(self) -> OAuth1:
        """OAuth1 for user-context auth (posting)."""
        # For posting, we need user access token/secret too
        # These should be obtained via OAuth flow
        return OAuth1(
            self.api_key,
            self.api_secret,
            os.environ.get("X_ACCESS_TOKEN"),
            os.environ.get("X_ACCESS_SECRET")
        )
    
    # === Rate Limiting ===
    
    def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if we can make request to endpoint."""
        if endpoint not in self._rate_limits:
            return True
        limit = self._rate_limits[endpoint]
        if limit["remaining"] <= 0 and time.time() < limit["reset_time"]:
            return False
        return True
    
    def _update_rate_limit(self, endpoint: str, headers: dict):
        """Update rate limit tracking from response headers."""
        self._rate_limits[endpoint] = {
            "remaining": int(headers.get("x-rate-limit-remaining", 100)),
            "reset_time": int(headers.get("x-rate-limit-reset", 0))
        }
    
    # === Core Methods ===
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Look up user by @handle."""
        url = f"{self.BASE_URL}/users/by/username/{username}"
        params = {"user.fields": "description,public_metrics"}
        resp = requests.get(url, headers=self._bearer_headers(), params=params)
        self._update_rate_limit("users", resp.headers)
        if resp.status_code != 200:
            return None
        data = resp.json().get("data", {})
        return User(
            id=data.get("id"),
            username=data.get("username"),
            name=data.get("name"),
            description=data.get("description"),
            followers_count=data.get("public_metrics", {}).get("followers_count", 0)
        )
    
    def get_user_tweets(
        self, 
        user_id: str, 
        since_id: Optional[str] = None,
        max_results: int = 10
    ) -> list[Tweet]:
        """Get recent tweets from a user."""
        url = f"{self.BASE_URL}/users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,author_id",
            "expansions": "author_id",
            "user.fields": "username"
        }
        if since_id:
            params["since_id"] = since_id
        
        resp = requests.get(url, headers=self._bearer_headers(), params=params)
        self._update_rate_limit("user_tweets", resp.headers)
        
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} - {resp.text}")
            return []
        
        data = resp.json()
        tweets = []
        users = {u["id"]: u["username"] for u in data.get("includes", {}).get("users", [])}
        
        for t in data.get("data", []):
            metrics = t.get("public_metrics", {})
            tweets.append(Tweet(
                id=t["id"],
                text=t["text"],
                author_id=t["author_id"],
                author_username=users.get(t["author_id"], ""),
                created_at=t.get("created_at", ""),
                retweet_count=metrics.get("retweet_count", 0),
                like_count=metrics.get("like_count", 0),
                reply_count=metrics.get("reply_count", 0)
            ))
        return tweets
    
    def post_reply(self, text: str, reply_to_tweet_id: str) -> Optional[str]:
        """
        Post a reply to a tweet.
        Returns posted tweet ID or None on failure.
        """
        url = f"{self.BASE_URL}/tweets"
        payload = {
            "text": text,
            "reply": {"in_reply_to_tweet_id": reply_to_tweet_id}
        }
        resp = requests.post(url, auth=self._oauth1(), json=payload)
        self._update_rate_limit("post_tweet", resp.headers)
        
        if resp.status_code != 201:
            print(f"Post error: {resp.status_code} - {resp.text}")
            return None
        return resp.json().get("data", {}).get("id")
```

## CLI for Testing

```python
if __name__ == "__main__":
    import sys
    client = XAPIClient()
    
    if len(sys.argv) < 2:
        print("Usage: python x_api.py <command> [args]")
        print("Commands: test-auth, lookup <username>, tweets <user_id>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "test-auth":
        # Test bearer token
        user = client.get_user_by_username("asanwal")
        if user:
            print(f"Auth works! Found: {user.name} (@{user.username})")
        else:
            print("Auth failed")
    
    elif cmd == "lookup" and len(sys.argv) > 2:
        user = client.get_user_by_username(sys.argv[2].lstrip("@"))
        print(user)
    
    elif cmd == "tweets" and len(sys.argv) > 2:
        tweets = client.get_user_tweets(sys.argv[2], max_results=5)
        for t in tweets:
            print(f"[{t.id}] {t.text[:80]}...")
```

## OAuth Flow Note

For posting (user-context actions), we need:
- `X_ACCESS_TOKEN`
- `X_ACCESS_SECRET`

These are obtained via OAuth 1.0a flow. Worker should include setup instructions or a one-time auth script.

## Acceptance Criteria
- [ ] Bearer auth works for reading
- [ ] get_user_by_username returns user data
- [ ] get_user_tweets returns recent tweets
- [ ] Rate limiting tracked and enforced
- [ ] post_reply works (once OAuth flow complete)
- [ ] CLI test commands work
