#!/usr/bin/env python3
"""
Ingest script for Google Takeout data.
Run from dataset root: python ingest/ingest.py
"""
import duckdb
import json
import re
from pathlib import Path
from html import unescape
from datetime import datetime
import glob

DB_PATH = Path(__file__).parent.parent / "data.duckdb"
SOURCE_DIR = Path(__file__).parent.parent / "source"
EXTRACTED_DIR = SOURCE_DIR / "extracted" / "Takeout"


def parse_youtube_watch_history(html_path: Path) -> list[dict]:
    """Parse YouTube watch history from HTML export."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    entries = []
    # Pattern: Watched[nbsp]<a href="URL">TITLE</a><br><a href="CHANNEL_URL">CHANNEL</a><br>TIMESTAMP<br>
    # Google uses \xa0 (nbsp) after "Watched" and \u202f (narrow nbsp) before AM/PM
    pattern = r'Watched\xa0<a href="(https://(?:www\.|music\.)?youtube\.com/watch\?v=[^"]+)">([^<]+)</a><br>(?:<a href="([^"]+)">([^<]+)</a><br>)?([A-Z][a-z]{2} \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2}[\s\u202f][AP]M [A-Z]+)<br>'
    
    for match in re.finditer(pattern, html):
        url = match.group(1)
        title = unescape(match.group(2))
        channel_url = match.group(3)  # May be None
        channel_name = unescape(match.group(4)) if match.group(4) else None
        timestamp_str = match.group(5).strip()
        
        # Extract video ID from URL
        video_id_match = re.search(r'v=([^&]+)', url)
        video_id = video_id_match.group(1) if video_id_match else None
        
        # Determine if it's YouTube Music
        is_music = 'music.youtube.com' in url
        
        # Parse timestamp (format: "Jan 21, 2026, 10:30:45 AM EST")
        watched_at = None
        try:
            # Normalize narrow nbsp to regular space and remove timezone suffix
            ts_clean = timestamp_str.replace('\u202f', ' ')
            ts_clean = re.sub(r'\s+(EST|EDT|PST|PDT|CST|CDT|MST|MDT)$', '', ts_clean)
            watched_at = datetime.strptime(ts_clean, '%b %d, %Y, %I:%M:%S %p')
        except ValueError:
            pass
        
        entries.append({
            'video_id': video_id,
            'title': title,
            'url': url,
            'channel_name': channel_name,
            'channel_url': channel_url,
            'watched_at': watched_at,
            'is_music': is_music,
            'platform': 'YouTube Music' if is_music else 'YouTube'
        })
    
    return entries


def parse_youtube_search_history(html_path: Path) -> list[dict]:
    """Parse YouTube search history from HTML export."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    entries = []
    # Pattern for search entries - Google uses \xa0 after "Searched for" and \u202f before AM/PM
    pattern = r'Searched for\xa0<a href="[^"]*(?:search_query|results\?search_query|search\?q)=([^"&]+)[^"]*">([^<]+)</a><br>([A-Z][a-z]{2} \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2}[\s\u202f][AP]M [A-Z]+)<br>'
    
    for match in re.finditer(pattern, html):
        query = unescape(match.group(2))
        timestamp_str = match.group(3).strip()
        
        # Parse timestamp
        searched_at = None
        try:
            ts_clean = timestamp_str.replace('\u202f', ' ')
            ts_clean = re.sub(r'\s+(EST|EDT|PST|PDT|CST|CDT|MST|MDT)$', '', ts_clean)
            searched_at = datetime.strptime(ts_clean, '%b %d, %Y, %I:%M:%S %p')
        except ValueError:
            pass
        
        entries.append({
            'query': query,
            'searched_at': searched_at,
            'platform': 'YouTube'
        })
    
    return entries


def load_reservations(reservations_dir: Path) -> list[dict]:
    """Load all reservation JSON files."""
    reservations = []
    for json_file in reservations_dir.glob('action_*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        booking = data.get('booking', {})
        reservations.append({
            'unique_id': data.get('uniqueId'),
            'name': booking.get('name'),
            'merchant_name': booking.get('merchantName'),
            'service': booking.get('service'),
            'address': booking.get('address'),
            'party_size': booking.get('partySize'),
            'start_time': booking.get('startTime'),
            'end_time': booking.get('endTime'),
            'last_modified': data.get('lastModifiedTime')
        })
    
    return reservations


def load_saved_places(geojson_path: Path) -> list[dict]:
    """Load saved places from GeoJSON."""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    places = []
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        location = props.get('location', {})
        coords = feature.get('geometry', {}).get('coordinates', [None, None])
        
        places.append({
            'name': location.get('name'),
            'address': location.get('address'),
            'saved_at': props.get('date'),
            'google_maps_url': props.get('google_maps_url'),
            'longitude': coords[0] if coords else None,
            'latitude': coords[1] if len(coords) > 1 else None
        })
    
    return places


def load_reviews(geojson_path: Path) -> list[dict]:
    """Load reviews from GeoJSON."""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    reviews = []
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        location = props.get('location', {})
        coords = feature.get('geometry', {}).get('coordinates', [None, None])
        
        reviews.append({
            'place_name': location.get('name'),
            'address': location.get('address'),
            'rating': props.get('five_star_rating_published'),
            'review_text': props.get('review_published'),
            'reviewed_at': props.get('date'),
            'google_maps_url': props.get('google_maps_url'),
            'longitude': coords[0] if coords else None,
            'latitude': coords[1] if len(coords) > 1 else None
        })
    
    return reviews


def main():
    # Delete existing DB for clean rebuild
    DB_PATH.unlink(missing_ok=True)
    
    con = duckdb.connect(str(DB_PATH))
    
    # 1. YouTube Watch History
    watch_history_path = EXTRACTED_DIR / "YouTube and YouTube Music" / "history" / "watch-history.html"
    if watch_history_path.exists():
        watch_entries = parse_youtube_watch_history(watch_history_path)
        if watch_entries:
            con.execute("""
                CREATE TABLE youtube_watch_history (
                    video_id VARCHAR,
                    title VARCHAR,
                    url VARCHAR,
                    watched_at TIMESTAMP,
                    is_music BOOLEAN,
                    platform VARCHAR
                )
            """)
            con.executemany(
                "INSERT INTO youtube_watch_history VALUES (?, ?, ?, ?, ?, ?)",
                [(e['video_id'], e['title'], e['url'], e['watched_at'], e['is_music'], e['platform']) 
                 for e in watch_entries]
            )
            print(f"Loaded {len(watch_entries)} YouTube watch history entries")
    
    # 2. YouTube Search History
    search_history_path = EXTRACTED_DIR / "YouTube and YouTube Music" / "history" / "search-history.html"
    if search_history_path.exists():
        search_entries = parse_youtube_search_history(search_history_path)
        if search_entries:
            con.execute("""
                CREATE TABLE youtube_search_history (
                    query VARCHAR,
                    searched_at TIMESTAMP
                )
            """)
            con.executemany(
                "INSERT INTO youtube_search_history VALUES (?, ?)",
                [(e['query'], e['searched_at']) for e in search_entries]
            )
            print(f"Loaded {len(search_entries)} YouTube search history entries")
    
    # 3. YouTube Subscriptions
    subscriptions_path = EXTRACTED_DIR / "YouTube and YouTube Music" / "subscriptions" / "subscriptions.csv"
    if subscriptions_path.exists():
        con.execute(f"""
            CREATE TABLE youtube_subscriptions AS 
            SELECT 
                "Channel Id" AS channel_id,
                "Channel Url" AS channel_url,
                "Channel Title" AS channel_name
            FROM read_csv_auto('{subscriptions_path}', header=true)
        """)
        count = con.execute("SELECT COUNT(*) FROM youtube_subscriptions").fetchone()[0]
        print(f"Loaded {count} YouTube subscriptions")
    
    # 4. Reservations
    reservations_dir = EXTRACTED_DIR / "Purchases & Reservations" / "Reservations"
    if reservations_dir.exists():
        reservations = load_reservations(reservations_dir)
        if reservations:
            con.execute("""
                CREATE TABLE reservations (
                    unique_id VARCHAR,
                    name VARCHAR,
                    merchant_name VARCHAR,
                    service VARCHAR,
                    address VARCHAR,
                    party_size INTEGER,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    last_modified TIMESTAMP
                )
            """)
            con.executemany(
                "INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(r['unique_id'], r['name'], r['merchant_name'], r['service'], r['address'],
                  r['party_size'], r['start_time'], r['end_time'], r['last_modified']) 
                 for r in reservations]
            )
            print(f"Loaded {len(reservations)} reservations")
    
    # 5. Maps Saved Places
    saved_places_path = EXTRACTED_DIR / "Maps (your places)" / "Saved Places.json"
    if saved_places_path.exists():
        places = load_saved_places(saved_places_path)
        if places:
            con.execute("""
                CREATE TABLE maps_saved_places (
                    name VARCHAR,
                    address VARCHAR,
                    saved_at TIMESTAMP,
                    google_maps_url VARCHAR,
                    longitude DOUBLE,
                    latitude DOUBLE
                )
            """)
            con.executemany(
                "INSERT INTO maps_saved_places VALUES (?, ?, ?, ?, ?, ?)",
                [(p['name'], p['address'], p['saved_at'], p['google_maps_url'], 
                  p['longitude'], p['latitude']) for p in places]
            )
            print(f"Loaded {len(places)} saved places")
    
    # 6. Maps Reviews
    reviews_path = EXTRACTED_DIR / "Maps (your places)" / "Reviews.json"
    if reviews_path.exists():
        reviews = load_reviews(reviews_path)
        if reviews:
            con.execute("""
                CREATE TABLE maps_reviews (
                    place_name VARCHAR,
                    address VARCHAR,
                    rating INTEGER,
                    review_text VARCHAR,
                    reviewed_at TIMESTAMP,
                    google_maps_url VARCHAR,
                    longitude DOUBLE,
                    latitude DOUBLE
                )
            """)
            con.executemany(
                "INSERT INTO maps_reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [(r['place_name'], r['address'], r['rating'], r['review_text'],
                  r['reviewed_at'], r['google_maps_url'], r['longitude'], r['latitude']) 
                 for r in reviews]
            )
            print(f"Loaded {len(reviews)} maps reviews")
    
    # 7. Search Contributions - Thumbs (media ratings)
    thumbs_path = EXTRACTED_DIR / "Search Contributions" / "Thumbs.json"
    if thumbs_path.exists():
        con.execute(f"""
            CREATE TABLE search_thumbs AS 
            SELECT 
                "Search Query" AS title,
                "Thumbs Rating" AS rating,
                "Published" AS rated_at,
                "Updated" AS updated_at
            FROM read_json_auto('{thumbs_path}')
        """)
        count = con.execute("SELECT COUNT(*) FROM search_thumbs").fetchone()[0]
        print(f"Loaded {count} search thumbs ratings")
    
    # Add table comments
    con.execute("COMMENT ON TABLE youtube_watch_history IS 'YouTube and YouTube Music watch history — one row per video watched'")
    con.execute("COMMENT ON TABLE youtube_search_history IS 'YouTube search queries — one row per search'")
    con.execute("COMMENT ON TABLE youtube_subscriptions IS 'YouTube channel subscriptions — one row per subscribed channel'")
    con.execute("COMMENT ON TABLE reservations IS 'Dining and other reservations from Google — one row per booking'")
    con.execute("COMMENT ON TABLE maps_saved_places IS 'Google Maps saved/starred places — one row per place'")
    con.execute("COMMENT ON TABLE maps_reviews IS 'Google Maps reviews written — one row per review'")
    con.execute("COMMENT ON TABLE search_thumbs IS 'Google Search thumbs up/down ratings for movies/shows'")
    
    # Add column comments
    con.execute("COMMENT ON COLUMN youtube_watch_history.video_id IS 'YouTube video ID (from URL)'")
    con.execute("COMMENT ON COLUMN youtube_watch_history.title IS 'Video or song title'")
    con.execute("COMMENT ON COLUMN youtube_watch_history.url IS 'Full YouTube URL'")
    con.execute("COMMENT ON COLUMN youtube_watch_history.watched_at IS 'When the video was watched'")
    con.execute("COMMENT ON COLUMN youtube_watch_history.is_music IS 'True if from YouTube Music'")
    con.execute("COMMENT ON COLUMN youtube_watch_history.platform IS 'YouTube or YouTube Music'")
    
    con.execute("COMMENT ON COLUMN youtube_search_history.query IS 'Search query text'")
    con.execute("COMMENT ON COLUMN youtube_search_history.searched_at IS 'When the search was performed'")
    
    con.execute("COMMENT ON COLUMN youtube_subscriptions.channel_id IS 'YouTube channel ID'")
    con.execute("COMMENT ON COLUMN youtube_subscriptions.channel_url IS 'Full channel URL'")
    con.execute("COMMENT ON COLUMN youtube_subscriptions.channel_name IS 'Channel display name'")
    
    con.execute("COMMENT ON COLUMN reservations.unique_id IS 'Google internal reservation ID'")
    con.execute("COMMENT ON COLUMN reservations.name IS 'Reservation type (e.g., Dining Reservation)'")
    con.execute("COMMENT ON COLUMN reservations.merchant_name IS 'Restaurant or venue name'")
    con.execute("COMMENT ON COLUMN reservations.service IS 'Service type'")
    con.execute("COMMENT ON COLUMN reservations.address IS 'Venue address'")
    con.execute("COMMENT ON COLUMN reservations.party_size IS 'Number of people in reservation'")
    con.execute("COMMENT ON COLUMN reservations.start_time IS 'Reservation start time'")
    con.execute("COMMENT ON COLUMN reservations.end_time IS 'Reservation end time'")
    con.execute("COMMENT ON COLUMN reservations.last_modified IS 'When the reservation was last modified'")
    
    con.execute("COMMENT ON COLUMN maps_saved_places.name IS 'Place name'")
    con.execute("COMMENT ON COLUMN maps_saved_places.address IS 'Full address'")
    con.execute("COMMENT ON COLUMN maps_saved_places.saved_at IS 'When the place was saved'")
    con.execute("COMMENT ON COLUMN maps_saved_places.google_maps_url IS 'Google Maps link'")
    con.execute("COMMENT ON COLUMN maps_saved_places.longitude IS 'Longitude coordinate'")
    con.execute("COMMENT ON COLUMN maps_saved_places.latitude IS 'Latitude coordinate'")
    
    con.execute("COMMENT ON COLUMN maps_reviews.place_name IS 'Place name'")
    con.execute("COMMENT ON COLUMN maps_reviews.address IS 'Full address'")
    con.execute("COMMENT ON COLUMN maps_reviews.rating IS 'Star rating (1-5)'")
    con.execute("COMMENT ON COLUMN maps_reviews.review_text IS 'Written review content'")
    con.execute("COMMENT ON COLUMN maps_reviews.reviewed_at IS 'When the review was posted'")
    con.execute("COMMENT ON COLUMN maps_reviews.google_maps_url IS 'Google Maps link'")
    con.execute("COMMENT ON COLUMN maps_reviews.longitude IS 'Longitude coordinate'")
    con.execute("COMMENT ON COLUMN maps_reviews.latitude IS 'Latitude coordinate'")
    
    con.execute("COMMENT ON COLUMN search_thumbs.title IS 'Movie or show title'")
    con.execute("COMMENT ON COLUMN search_thumbs.rating IS 'Thumbs Up or Thumbs Down'")
    con.execute("COMMENT ON COLUMN search_thumbs.rated_at IS 'When the rating was given'")
    con.execute("COMMENT ON COLUMN search_thumbs.updated_at IS 'When the rating was last updated'")
    
    con.close()
    print(f"\nCreated {DB_PATH}")


if __name__ == "__main__":
    main()
