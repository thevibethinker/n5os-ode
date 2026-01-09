#!/usr/bin/env python3
"""
X API Wrapper for Thought Leadership Engine

Handles authentication, rate limiting, and provides clean interfaces
for fetching tweets and posting replies.

Environment variables required:
- X_API_KEY: API Key (Consumer Key)
- X_API_KEY_SECRET: API Secret (Consumer Secret)
- X_BEARER_TOKEN: Bearer Token
- X_ACCESS_TOKEN: User Access Token (for posting)
- X_ACCESS_TOKEN_SECRET: User Access Token Secret (for posting)
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from functools import wraps
import requests
from requests_oauthlib import OAuth1Session

# YAML Frontmatter
# ---
# created: 2026-01-08
# last_edited: 2026-01-08
# version: 1.0
# provenance: con_eszoRWFeDprxC93n
# ---

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("x_api")

class XAPIError(Exception):
    """Custom exception for X API errors"""
    pass

def handle_rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = func(*args, **kwargs)
                if response.status_code == 429:
                    reset_time = int(response.headers.get('x-rate-limit-reset', time.time() + 60))
                    sleep_time = max(reset_time - time.time(), 1)
                    logger.warning(f"Rate limited. Sleeping {sleep_time}s (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(min(sleep_time, 900))  # Cap at 15 min
                    continue
                
                if response.status_code == 401:
                    logger.error(f"Authentication failure (401): {response.text}")
                    raise XAPIError(f"Authentication failure: {response.text}")
                
                if response.status_code == 403:
                    logger.error(f"Forbidden (403): {response.text}")
                    raise XAPIError(f"Forbidden: {response.text}")
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt) # Exponential backoff for connection issues
        raise XAPIError("Rate limit exceeded after retries or persistent failure")
    return wrapper

def get_bearer_headers():
    bearer_token = os.environ.get("X_BEARER_TOKEN")
    if not bearer_token:
        raise XAPIError("X_BEARER_TOKEN environment variable is missing")
    return {"Authorization": f"Bearer {bearer_token}"}

def get_oauth_session():
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_KEY_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret]):
        raise XAPIError("X_API_KEY and/or X_API_SECRET environment variables are missing")
    
    if not all([access_token, access_secret]):
        logger.warning("X_ACCESS_TOKEN and/or X_ACCESS_TOKEN_SECRET missing. Write operations will fail.")
        return OAuth1Session(api_key, client_secret=api_secret)
        
    return OAuth1Session(
        api_key,
        client_secret=api_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_secret,
    )

@handle_rate_limit
def _get_request(url, params=None):
    return requests.get(url, headers=get_bearer_headers(), params=params)

def get_user_id(username: str) -> Optional[str]:
    """
    Get X user ID from username (without @).
    """
    username = username.lstrip('@')
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    response = _get_request(url)
    if response and response.status_code == 200:
        data = response.json()
        if 'data' in data:
            return data['data']['id']
    return None

def get_user_tweets(user_id: str, since_id: Optional[str] = None, max_results: int = 10) -> List[Dict]:
    # X API Basic tier requires min 10, max 100
    max_results = max(10, min(max_results, 100))
    """
    Get recent tweets from a user.
    """
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,referenced_tweets",
        "expansions": "referenced_tweets.id"
    }
    if since_id:
        params["since_id"] = since_id
        
    response = _get_request(url, params=params)
    if response and response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    return []

def get_tweet(tweet_id: str) -> Optional[Dict]:
    """
    Get a single tweet by ID.
    """
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    params = {
        "tweet.fields": "created_at,public_metrics,referenced_tweets"
    }
    response = _get_request(url, params=params)
    if response and response.status_code == 200:
        data = response.json()
        return data.get('data')
    return None

def post_reply(reply_to_id: str, text: str) -> Optional[Dict]:
    """
    Post a reply to a tweet using OAuth 1.0a User Context.
    """
    oauth = get_oauth_session()
    if not oauth.resource_owner_key:
        raise XAPIError("X_ACCESS_TOKEN and X_ACCESS_TOKEN_SECRET are required for posting replies. Run 'oauth' command first.")
        
    url = "https://api.twitter.com/2/tweets"
    payload = {
        "text": text,
        "reply": {"in_reply_to_tweet_id": reply_to_id}
    }
    
    try:
        response = oauth.post(url, json=payload)
        if response.status_code == 429:
             # Manual rate limit handling for OAuth session post
             reset_time = int(response.headers.get('x-rate-limit-reset', time.time() + 60))
             sleep_time = max(reset_time - time.time(), 1)
             logger.warning(f"Rate limited on post. Sleeping {sleep_time}s")
             time.sleep(min(sleep_time, 900))
             response = oauth.post(url, json=payload)
             
        if response.status_code in [200, 201]:
            return response.json().get('data')
        else:
            logger.error(f"Failed to post reply: {response.status_code} {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error posting reply: {e}")
        return None

def initiate_oauth_flow() -> str:
    """Returns authorization URL for user to complete OAuth"""
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_KEY_SECRET")
    
    if not all([api_key, api_secret]):
        raise XAPIError("X_API_KEY and X_API_SECRET are required to initiate OAuth flow")
        
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob"
    oauth = OAuth1Session(api_key, client_secret=api_secret)
    
    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except Exception as e:
        raise XAPIError(f"Failed to fetch request token: {e}")
        
    resource_owner_key = fetch_response.get("oauth_token")
    # Store this temporarily in memory or a file if needed, but for 'oob' we just return the URL
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    
    logger.info("Request token received. Directing user to authorization URL.")
    return authorization_url

def complete_oauth_flow(oauth_verifier: str) -> Dict[str, str]:
    """Exchanges verifier for access tokens"""
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_KEY_SECRET")
    
    # Note: In a real oob flow, we'd need the request token (oauth_token) from the previous step.
    # requests-oauthlib handles this if we use the same session, but here we might need to prompt for it
    # or assume it's passed in. For simplicity in CLI, we'll try to get it.
    
    # Actually, for 'oob' flow, we often need to re-initiate or have kept the state.
    # Let's assume the user provides the verifier.
    
    logger.warning("comple_oauth_flow usually requires the request token from initiate_oauth_flow session.")
    # For a CLI, it's better to keep the session alive or store the token.
    # Let's use a simpler approach for the CLI.
    return {"note": "Use initiate_oauth_flow to get the URL, then provide verifier."}

# ============================================================
# LIST ENDPOINTS (added Phase 1 - con_nRtJ8573Bwl836An)
# ============================================================

def get_list_info(list_id: str) -> Optional[Dict]:
    """
    Get list metadata (name, description, member_count).
    
    Args:
        list_id: The X list ID
        
    Returns:
        Dict with list info or None if not found/error
    """
    url = f"https://api.twitter.com/2/lists/{list_id}"
    params = {
        "list.fields": "created_at,description,member_count,name,owner_id,private"
    }
    response = _get_request(url, params=params)
    if response and response.status_code == 200:
        data = response.json()
        return data.get('data')
    return None


def get_list_members(list_id: str, max_results: int = 100) -> List[Dict]:
    """
    Get all members of a list with pagination.
    
    Args:
        list_id: The X list ID
        max_results: Max results per page (1-100)
        
    Returns:
        List of user dicts with id, username, name, description, public_metrics
    """
    url = f"https://api.twitter.com/2/lists/{list_id}/members"
    max_results = max(1, min(max_results, 100))
    params = {
        "max_results": max_results,
        "user.fields": "id,username,name,description,public_metrics,created_at"
    }
    
    all_members = []
    next_token = None
    
    while True:
        if next_token:
            params["pagination_token"] = next_token
        
        response = _get_request(url, params=params)
        if not response or response.status_code != 200:
            break
            
        data = response.json()
        members = data.get('data', [])
        all_members.extend(members)
        
        # Check for pagination
        meta = data.get('meta', {})
        next_token = meta.get('next_token')
        if not next_token:
            break
            
        logger.info(f"Fetched {len(all_members)} members so far, paginating...")
    
    logger.info(f"Total members fetched from list {list_id}: {len(all_members)}")
    return all_members


def get_list_tweets(list_id: str, max_results: int = 100, since_id: Optional[str] = None) -> List[Dict]:
    """
    Get recent tweets from a list timeline.
    
    Args:
        list_id: The X list ID
        max_results: Max results (1-100)
        since_id: Only return tweets newer than this ID
        
    Returns:
        List of tweet dicts
    """
    url = f"https://api.twitter.com/2/lists/{list_id}/tweets"
    max_results = max(1, min(max_results, 100))
    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,author_id,referenced_tweets",
        "expansions": "author_id",
        "user.fields": "username,name"
    }
    if since_id:
        params["since_id"] = since_id
    
    response = _get_request(url, params=params)
    if response and response.status_code == 200:
        data = response.json()
        tweets = data.get('data', [])
        
        # Attach author info from includes
        includes = data.get('includes', {})
        users = {u['id']: u for u in includes.get('users', [])}
        for tweet in tweets:
            author_id = tweet.get('author_id')
            if author_id and author_id in users:
                tweet['author'] = users[author_id]
        
        return tweets
    return []


def add_list_member(list_id: str, user_id: str) -> bool:
    """
    Add a user to a list. Requires OAuth1 user context.
    
    Args:
        list_id: The X list ID
        user_id: The user ID to add
        
    Returns:
        True if successful, False otherwise
    """
    api_key = os.environ.get('X_API_KEY')
    api_secret = os.environ.get('X_API_KEY_SECRET')
    access_token = os.environ.get('X_ACCESS_TOKEN')
    access_secret = os.environ.get('X_ACCESS_TOKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_secret]):
        logger.error("Missing OAuth1 credentials for list member management")
        return False
    
    oauth = OAuth1Session(
        api_key,
        client_secret=api_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_secret
    )
    
    url = f"https://api.x.com/2/lists/{list_id}/members"
    response = oauth.post(url, json={"user_id": user_id})
    
    if response.status_code == 200:
        logger.info(f"Added user {user_id} to list {list_id}")
        return True
    else:
        logger.error(f"Failed to add user to list: {response.status_code} {response.text}")
        return False


def remove_list_member(list_id: str, user_id: str) -> bool:
    """
    Remove a user from a list. Requires OAuth1 user context.
    """
    api_key = os.environ.get('X_API_KEY')
    api_secret = os.environ.get('X_API_KEY_SECRET')
    access_token = os.environ.get('X_ACCESS_TOKEN')
    access_secret = os.environ.get('X_ACCESS_TOKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_secret]):
        logger.error("Missing OAuth1 credentials for list member management")
        return False
    
    oauth = OAuth1Session(
        api_key,
        client_secret=api_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_secret
    )
    
    url = f"https://api.x.com/2/lists/{list_id}/members/{user_id}"
    response = oauth.delete(url)
    
    if response.status_code == 200:
        logger.info(f"Removed user {user_id} from list {list_id}")
        return True
    else:
        logger.error(f"Failed to remove user from list: {response.status_code} {response.text}")
        return False


def lookup_user_by_username(username: str) -> Optional[Dict]:
    """
    Look up a user by username to get their ID.
    """
    username = username.lstrip('@')
    url = f"https://api.x.com/2/users/by/username/{username}"
    params = {"user.fields": "id,username,name,description,public_metrics"}
    response = _get_request(url, params=params)
    if response and response.status_code == 200:
        return response.json().get('data')
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="X API Wrapper CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # user-id command
    user_parser = subparsers.add_parser("user-id", help="Get user ID from username")
    user_parser.add_argument("username", help="Username without @")
    
    # tweets command  
    tweets_parser = subparsers.add_parser("tweets", help="Get user tweets")
    tweets_parser.add_argument("user_id", help="User ID")
    tweets_parser.add_argument("--since", help="Since tweet ID")
    tweets_parser.add_argument("--max", type=int, default=10, help="Max results")
    
    # reply command
    reply_parser = subparsers.add_parser("reply", help="Post a reply")
    reply_parser.add_argument("tweet_id", help="Tweet ID to reply to")
    reply_parser.add_argument("text", help="Reply text")
    
    # oauth command
    oauth_parser = subparsers.add_parser("oauth", help="Initiate OAuth flow")
    
    # complete-oauth command
    comp_oauth_parser = subparsers.add_parser("complete-oauth", help="Complete OAuth flow with verifier")
    comp_oauth_parser.add_argument("verifier", help="The PIN/verifier provided by X")
    comp_oauth_parser.add_argument("resource_owner_key", help="The oauth_token from initiate_oauth_flow")

    args = parser.parse_args()
    
    if args.command == "user-id":
        uid = get_user_id(args.username)
        if uid:
            print(uid)
        else:
            print(f"User {args.username} not found.")
            
    elif args.command == "tweets":
        tweets = get_user_tweets(args.user_id, since_id=args.since, max_results=args.max)
        import json
        print(json.dumps(tweets, indent=2))
        
    elif args.command == "reply":
        result = post_reply(args.tweet_id, args.text)
        if result:
            print("Reply posted successfully:")
            print(result)
        else:
            print("Failed to post reply.")
            
    elif args.command == "oauth":
        try:
            url = initiate_oauth_flow()
            print(f"Please visit this URL to authorize the app: {url}")
            print("After authorizing, you will receive a PIN (verifier).")
            # For CLI we'll just extract the oauth_token from the URL to help the user
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            oauth_token = parse_qs(parsed_url.query).get('oauth_token', [None])[0]
            print(f"Your request oauth_token is: {oauth_token}")
            print(f"Then run: python3 {__file__} complete-oauth <PIN> {oauth_token}")
        except Exception as e:
            print(f"Error: {e}")
            
    elif args.command == "complete-oauth":
        api_key = os.environ.get("X_API_KEY")
        api_secret = os.environ.get("X_API_KEY_SECRET")
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            api_key,
            client_secret=api_secret,
            resource_owner_key=args.resource_owner_key
        )
        try:
            oauth_tokens = oauth.fetch_access_token(access_token_url, verifier=args.verifier)
            print("Access tokens received successfully!")
            print(f"X_ACCESS_TOKEN: {oauth_tokens.get('oauth_token')}")
            print(f"X_ACCESS_TOKEN_SECRET: {oauth_tokens.get('oauth_token_secret')}")
            print("\nSave these in your environment variables/Zo Secrets.")
        except Exception as e:
            print(f"Error completing OAuth flow: {e}")
    else:
        parser.print_help()








