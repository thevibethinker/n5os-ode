#!/usr/bin/env python3
"""
Ingest script for X/Twitter archive (pre-Jan-8 2026).
Run from dataset root: python ingest/ingest.py
"""
import duckdb
import json
import re
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data.duckdb"
SOURCE_DIR = Path(__file__).parent.parent / "source" / "extracted" / "data"


def load_twitter_js(filepath: Path) -> list:
    """Load Twitter's JS format: window.YTD.xxx.part0 = [...]"""
    content = filepath.read_text(encoding='utf-8')
    # Remove the window.YTD.xxx.part0 = prefix
    match = re.search(r'=\s*(\[.*\])\s*$', content, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return []


def main():
    # Clean rebuild
    DB_PATH.unlink(missing_ok=True)
    con = duckdb.connect(str(DB_PATH))
    
    # =========================================================================
    # TWEETS - Your posts
    # =========================================================================
    tweets_file = SOURCE_DIR / "tweets.js"
    if tweets_file.exists():
        tweets_data = load_twitter_js(tweets_file)
        
        rows = []
        for item in tweets_data:
            t = item.get('tweet', {})
            
            # Parse mentions
            mentions = [m.get('screen_name') for m in t.get('entities', {}).get('user_mentions', [])]
            
            # Parse hashtags
            hashtags = [h.get('text') for h in t.get('entities', {}).get('hashtags', [])]
            
            # Parse URLs
            urls = [u.get('expanded_url') for u in t.get('entities', {}).get('urls', [])]
            
            rows.append({
                'id': t.get('id_str'),
                'created_at': t.get('created_at'),
                'full_text': t.get('full_text'),
                'favorite_count': int(t.get('favorite_count', 0)),
                'retweet_count': int(t.get('retweet_count', 0)),
                'in_reply_to_user_id': t.get('in_reply_to_user_id_str'),
                'in_reply_to_status_id': t.get('in_reply_to_status_id_str'),
                'is_retweet': t.get('full_text', '').startswith('RT @'),
                'mentions': json.dumps(mentions) if mentions else None,
                'hashtags': json.dumps(hashtags) if hashtags else None,
                'urls': json.dumps(urls) if urls else None,
                'source': re.sub(r'<[^>]+>', '', t.get('source', '')),  # Strip HTML
            })
        
        con.execute("""
            CREATE TABLE tweets (
                id VARCHAR,
                created_at VARCHAR,
                full_text VARCHAR,
                favorite_count INTEGER,
                retweet_count INTEGER,
                in_reply_to_user_id VARCHAR,
                in_reply_to_status_id VARCHAR,
                is_retweet BOOLEAN,
                mentions VARCHAR,
                hashtags VARCHAR,
                urls VARCHAR,
                source VARCHAR
            )
        """)
        con.executemany("INSERT INTO tweets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                       [(r['id'], r['created_at'], r['full_text'], r['favorite_count'], 
                         r['retweet_count'], r['in_reply_to_user_id'], r['in_reply_to_status_id'],
                         r['is_retweet'], r['mentions'], r['hashtags'], r['urls'], r['source']) 
                        for r in rows])
        
        # Parse timestamps
        con.execute("""
            ALTER TABLE tweets 
            ALTER COLUMN created_at TYPE TIMESTAMP 
            USING strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
        """)
        
        print(f"  tweets: {len(rows)} rows")
    
    # =========================================================================
    # LIKES - Tweets you liked
    # =========================================================================
    likes_file = SOURCE_DIR / "like.js"
    if likes_file.exists():
        likes_data = load_twitter_js(likes_file)
        
        rows = []
        for item in likes_data:
            l = item.get('like', {})
            rows.append((
                l.get('tweetId'),
                l.get('fullText'),
                l.get('expandedUrl'),
            ))
        
        con.execute("""
            CREATE TABLE likes (
                tweet_id VARCHAR,
                full_text VARCHAR,
                expanded_url VARCHAR
            )
        """)
        con.executemany("INSERT INTO likes VALUES (?, ?, ?)", rows)
        print(f"  likes: {len(rows)} rows")
    
    # =========================================================================
    # FOLLOWING - Accounts you follow
    # =========================================================================
    following_file = SOURCE_DIR / "following.js"
    if following_file.exists():
        following_data = load_twitter_js(following_file)
        
        rows = []
        for item in following_data:
            f = item.get('following', {})
            rows.append((
                f.get('accountId'),
                f.get('userLink'),
            ))
        
        con.execute("""
            CREATE TABLE following (
                account_id VARCHAR,
                user_link VARCHAR
            )
        """)
        con.executemany("INSERT INTO following VALUES (?, ?)", rows)
        print(f"  following: {len(rows)} rows")
    
    # =========================================================================
    # FOLLOWERS - Accounts following you
    # =========================================================================
    followers_file = SOURCE_DIR / "follower.js"
    if followers_file.exists():
        followers_data = load_twitter_js(followers_file)
        
        rows = []
        for item in followers_data:
            f = item.get('follower', {})
            rows.append((
                f.get('accountId'),
                f.get('userLink'),
            ))
        
        con.execute("""
            CREATE TABLE followers (
                account_id VARCHAR,
                user_link VARCHAR
            )
        """)
        con.executemany("INSERT INTO followers VALUES (?, ?)", rows)
        print(f"  followers: {len(rows)} rows")
    
    # =========================================================================
    # DIRECT MESSAGES - DM conversations
    # =========================================================================
    dms_file = SOURCE_DIR / "direct-messages.js"
    if dms_file.exists():
        dms_data = load_twitter_js(dms_file)
        
        rows = []
        for item in dms_data:
            conv = item.get('dmConversation', {})
            conv_id = conv.get('conversationId')
            
            for msg in conv.get('messages', []):
                mc = msg.get('messageCreate', {})
                if mc:
                    rows.append((
                        conv_id,
                        mc.get('id'),
                        mc.get('senderId'),
                        mc.get('recipientId'),
                        mc.get('text'),
                        mc.get('createdAt'),
                    ))
        
        con.execute("""
            CREATE TABLE direct_messages (
                conversation_id VARCHAR,
                message_id VARCHAR,
                sender_id VARCHAR,
                recipient_id VARCHAR,
                text VARCHAR,
                created_at VARCHAR
            )
        """)
        con.executemany("INSERT INTO direct_messages VALUES (?, ?, ?, ?, ?, ?)", rows)
        
        # Parse timestamps
        con.execute("""
            ALTER TABLE direct_messages 
            ALTER COLUMN created_at TYPE TIMESTAMP 
            USING strptime(created_at, '%Y-%m-%dT%H:%M:%S.%gZ')
        """)
        
        print(f"  direct_messages: {len(rows)} rows")
    
    # =========================================================================
    # NOTE TWEETS - Long-form tweets
    # =========================================================================
    notes_file = SOURCE_DIR / "note-tweet.js"
    if notes_file.exists():
        notes_data = load_twitter_js(notes_file)
        
        rows = []
        for item in notes_data:
            n = item.get('noteTweet', {})
            core = n.get('core', {})
            rows.append((
                n.get('noteTweetId'),
                core.get('text'),
                n.get('createdAt'),
                n.get('updatedAt'),
            ))
        
        con.execute("""
            CREATE TABLE note_tweets (
                id VARCHAR,
                text VARCHAR,
                created_at VARCHAR,
                updated_at VARCHAR
            )
        """)
        con.executemany("INSERT INTO note_tweets VALUES (?, ?, ?, ?)", rows)
        
        # Parse timestamps
        con.execute("""
            ALTER TABLE note_tweets 
            ALTER COLUMN created_at TYPE TIMESTAMP 
            USING strptime(created_at, '%Y-%m-%dT%H:%M:%S.%gZ')
        """)
        con.execute("""
            ALTER TABLE note_tweets 
            ALTER COLUMN updated_at TYPE TIMESTAMP 
            USING strptime(updated_at, '%Y-%m-%dT%H:%M:%S.%gZ')
        """)
        
        print(f"  note_tweets: {len(rows)} rows")
    
    # =========================================================================
    # BLOCKS - Accounts you blocked
    # =========================================================================
    blocks_file = SOURCE_DIR / "block.js"
    if blocks_file.exists():
        blocks_data = load_twitter_js(blocks_file)
        
        rows = []
        for item in blocks_data:
            b = item.get('blocking', {})
            rows.append((
                b.get('accountId'),
                b.get('userLink'),
            ))
        
        con.execute("""
            CREATE TABLE blocks (
                account_id VARCHAR,
                user_link VARCHAR
            )
        """)
        con.executemany("INSERT INTO blocks VALUES (?, ?)", rows)
        print(f"  blocks: {len(rows)} rows")
    
    # =========================================================================
    # MUTES - Accounts you muted
    # =========================================================================
    mutes_file = SOURCE_DIR / "mute.js"
    if mutes_file.exists():
        mutes_data = load_twitter_js(mutes_file)
        
        rows = []
        for item in mutes_data:
            m = item.get('muting', {})
            rows.append((
                m.get('accountId'),
                m.get('userLink'),
            ))
        
        con.execute("""
            CREATE TABLE mutes (
                account_id VARCHAR,
                user_link VARCHAR
            )
        """)
        con.executemany("INSERT INTO mutes VALUES (?, ?)", rows)
        print(f"  mutes: {len(rows)} rows")
    
    # =========================================================================
    # DELETED TWEETS - Tweets you deleted
    # =========================================================================
    deleted_file = SOURCE_DIR / "deleted-tweets.js"
    if deleted_file.exists():
        deleted_data = load_twitter_js(deleted_file)
        
        rows = []
        for item in deleted_data:
            t = item.get('tweet', {})
            if t:
                rows.append((
                    t.get('id_str'),
                    t.get('created_at'),
                    t.get('full_text'),
                ))
        
        if rows:
            con.execute("""
                CREATE TABLE deleted_tweets (
                    id VARCHAR,
                    created_at VARCHAR,
                    full_text VARCHAR
                )
            """)
            con.executemany("INSERT INTO deleted_tweets VALUES (?, ?, ?)", rows)
            
            # Parse timestamps
            con.execute("""
                ALTER TABLE deleted_tweets 
                ALTER COLUMN created_at TYPE TIMESTAMP 
                USING strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
            """)
            
            print(f"  deleted_tweets: {len(rows)} rows")
    
    # =========================================================================
    # ACCOUNT INFO
    # =========================================================================
    account_file = SOURCE_DIR / "account.js"
    if account_file.exists():
        account_data = load_twitter_js(account_file)
        
        rows = []
        for item in account_data:
            a = item.get('account', {})
            rows.append((
                a.get('accountId'),
                a.get('username'),
                a.get('accountDisplayName'),
                a.get('email'),
                a.get('createdAt'),
            ))
        
        con.execute("""
            CREATE TABLE account (
                account_id VARCHAR,
                username VARCHAR,
                display_name VARCHAR,
                email VARCHAR,
                created_at VARCHAR
            )
        """)
        con.executemany("INSERT INTO account VALUES (?, ?, ?, ?, ?)", rows)
        print(f"  account: {len(rows)} rows")
    
    # =========================================================================
    # ADD COMMENTS FOR SCHEMA DOCUMENTATION
    # =========================================================================
    
    # Table comments
    con.execute("COMMENT ON TABLE tweets IS 'Your tweets/posts on X'")
    con.execute("COMMENT ON TABLE likes IS 'Tweets you liked'")
    con.execute("COMMENT ON TABLE following IS 'Accounts you follow'")
    con.execute("COMMENT ON TABLE followers IS 'Accounts following you'")
    con.execute("COMMENT ON TABLE direct_messages IS 'Direct message conversations'")
    con.execute("COMMENT ON TABLE note_tweets IS 'Long-form tweets (notes)'")
    con.execute("COMMENT ON TABLE blocks IS 'Accounts you blocked'")
    con.execute("COMMENT ON TABLE mutes IS 'Accounts you muted'")
    con.execute("COMMENT ON TABLE account IS 'Your account information'")
    
    # Column comments - tweets
    con.execute("COMMENT ON COLUMN tweets.id IS 'Tweet ID'")
    con.execute("COMMENT ON COLUMN tweets.created_at IS 'When the tweet was posted'")
    con.execute("COMMENT ON COLUMN tweets.full_text IS 'Tweet content'")
    con.execute("COMMENT ON COLUMN tweets.favorite_count IS 'Number of likes'")
    con.execute("COMMENT ON COLUMN tweets.retweet_count IS 'Number of retweets'")
    con.execute("COMMENT ON COLUMN tweets.in_reply_to_user_id IS 'User ID this is replying to (if reply)'")
    con.execute("COMMENT ON COLUMN tweets.in_reply_to_status_id IS 'Tweet ID this is replying to (if reply)'")
    con.execute("COMMENT ON COLUMN tweets.is_retweet IS 'Whether this is a retweet'")
    con.execute("COMMENT ON COLUMN tweets.mentions IS 'JSON array of @mentioned usernames'")
    con.execute("COMMENT ON COLUMN tweets.hashtags IS 'JSON array of #hashtags used'")
    con.execute("COMMENT ON COLUMN tweets.urls IS 'JSON array of URLs in tweet'")
    con.execute("COMMENT ON COLUMN tweets.source IS 'Client used to post (Android, Web, etc.)'")
    
    # Column comments - likes
    con.execute("COMMENT ON COLUMN likes.tweet_id IS 'ID of the liked tweet'")
    con.execute("COMMENT ON COLUMN likes.full_text IS 'Content of the liked tweet'")
    con.execute("COMMENT ON COLUMN likes.expanded_url IS 'Link to the tweet'")
    
    # Column comments - following/followers
    con.execute("COMMENT ON COLUMN following.account_id IS 'X user ID'")
    con.execute("COMMENT ON COLUMN following.user_link IS 'Link to user profile'")
    con.execute("COMMENT ON COLUMN followers.account_id IS 'X user ID'")
    con.execute("COMMENT ON COLUMN followers.user_link IS 'Link to user profile'")
    
    # Column comments - DMs
    con.execute("COMMENT ON COLUMN direct_messages.conversation_id IS 'Conversation thread ID'")
    con.execute("COMMENT ON COLUMN direct_messages.message_id IS 'Individual message ID'")
    con.execute("COMMENT ON COLUMN direct_messages.sender_id IS 'User ID who sent the message'")
    con.execute("COMMENT ON COLUMN direct_messages.recipient_id IS 'User ID who received the message'")
    con.execute("COMMENT ON COLUMN direct_messages.text IS 'Message content'")
    con.execute("COMMENT ON COLUMN direct_messages.created_at IS 'When the message was sent'")
    
    # Column comments - deleted tweets
    try:
        con.execute("COMMENT ON COLUMN deleted_tweets.id IS 'Tweet ID'")
        con.execute("COMMENT ON COLUMN deleted_tweets.created_at IS 'When the tweet was posted'")
        con.execute("COMMENT ON COLUMN deleted_tweets.full_text IS 'Tweet content'")
    except:
        pass  # Table may not exist if no deleted tweets
    
    con.close()
    print(f"\nCreated {DB_PATH}")


if __name__ == "__main__":
    main()


