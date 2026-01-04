#!/usr/bin/env python3
"""
Kalshi API Client for market analysis.
Fetches markets, prices, and orderbooks for prediction market analysis.

Usage:
    python kalshi_client.py markets --status open --limit 100
    python kalshi_client.py market TICKER
    python kalshi_client.py search "unemployment"
    python kalshi_client.py edge  # Find markets where V's positions might apply
"""

import argparse
import json
import requests
import sqlite3
from pathlib import Path
from datetime import datetime
import sys

# API Configuration
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
DEMO_URL = "https://demo-api.kalshi.co/trade-api/v2"

# V's position domains that might have market relevance
EDGE_DOMAINS = {
    "hiring-market": ["layoff", "employment", "job", "hiring", "unemployment", "workforce"],
    "ai-automation": ["ai", "openai", "gpt", "llm", "automation", "robot", "tech"],
    "careerspan": ["hiring", "recruiting", "career", "job"],
    "worldview": ["economy", "recession", "inflation", "growth"],
    "epistemology": ["knowledge", "information", "prediction"],
}


def get_markets(status="open", limit=100, series_ticker=None, cursor=None):
    """Fetch markets from Kalshi API."""
    params = {"limit": limit}
    if status:
        params["status"] = status
    if series_ticker:
        params["series_ticker"] = series_ticker
    if cursor:
        params["cursor"] = cursor
    
    resp = requests.get(f"{BASE_URL}/markets", params=params)
    resp.raise_for_status()
    return resp.json()


def get_market(ticker: str):
    """Fetch a specific market by ticker."""
    resp = requests.get(f"{BASE_URL}/markets/{ticker}")
    resp.raise_for_status()
    return resp.json()


def get_orderbook(ticker: str):
    """Fetch orderbook for a market."""
    resp = requests.get(f"{BASE_URL}/markets/{ticker}/orderbook")
    resp.raise_for_status()
    return resp.json()


def get_series(ticker: str):
    """Fetch series info."""
    resp = requests.get(f"{BASE_URL}/series/{ticker}")
    resp.raise_for_status()
    return resp.json()


def search_markets(query: str, status="open"):
    """Search for markets matching query in title."""
    markets = []
    cursor = None
    query_lower = query.lower()
    
    while True:
        data = get_markets(status=status, limit=200, cursor=cursor)
        for m in data.get("markets", []):
            title = m.get("title", "").lower()
            subtitle = m.get("subtitle", "").lower()
            if query_lower in title or query_lower in subtitle:
                markets.append(m)
        
        cursor = data.get("cursor")
        if not cursor or len(data.get("markets", [])) < 200:
            break
    
    return markets


def load_positions():
    """Load V's positions from the positions database."""
    db_path = Path("/home/workspace/N5/data/positions.db")
    if not db_path.exists():
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, domain, insight, confidence 
        FROM positions 
        WHERE confidence >= 3
        ORDER BY confidence DESC
    """)
    positions = cursor.fetchall()
    conn.close()
    return positions


def find_edge_markets():
    """
    Find markets where V's documented positions might give informational edge.
    Cross-references positions with market categories and keywords.
    """
    positions = load_positions()
    if not positions:
        print("No positions found in database")
        return []
    
    # Build keyword set from positions
    position_keywords = set()
    for pos_id, title, domain, insight, confidence in positions:
        # Extract keywords from title and insight
        words = (title + " " + insight).lower().split()
        position_keywords.update(w for w in words if len(w) > 4)
    
    # Fetch all open markets
    all_markets = []
    cursor = None
    while True:
        data = get_markets(status="open", limit=1000, cursor=cursor)
        all_markets.extend(data.get("markets", []))
        cursor = data.get("cursor")
        if not cursor:
            break
    
    # Score markets by relevance to positions
    scored_markets = []
    for market in all_markets:
        title = market.get("title", "").lower()
        subtitle = market.get("subtitle", "").lower()
        category = market.get("category", "").lower()
        
        # Count keyword matches
        text = f"{title} {subtitle} {category}"
        matches = sum(1 for kw in position_keywords if kw in text)
        
        # Check domain relevance
        domain_boost = 0
        for domain, keywords in EDGE_DOMAINS.items():
            if any(kw in text for kw in keywords):
                domain_boost += 2
        
        score = matches + domain_boost
        if score > 0:
            scored_markets.append((score, market))
    
    # Sort by score
    scored_markets.sort(key=lambda x: -x[0])
    return scored_markets[:50]  # Top 50


def format_market(m: dict) -> str:
    """Format market for display."""
    yes_bid = m.get("yes_bid", 0)
    yes_ask = m.get("yes_ask", 0)
    volume = m.get("volume", 0)
    return f"""
Ticker: {m.get('ticker')}
Title: {m.get('title')}
Category: {m.get('category')}
Yes Bid/Ask: {yes_bid}¢ / {yes_ask}¢  (implied prob: {yes_bid}-{yes_ask}%)
Volume: {volume:,}
Close: {m.get('close_time', 'N/A')}
"""


def main():
    parser = argparse.ArgumentParser(description="Kalshi market analysis")
    subparsers = parser.add_subparsers(dest="command")
    
    # Markets command
    markets_p = subparsers.add_parser("markets", help="List markets")
    markets_p.add_argument("--status", default="open", choices=["open", "closed", "settled"])
    markets_p.add_argument("--limit", type=int, default=20)
    markets_p.add_argument("--series", help="Filter by series ticker")
    markets_p.add_argument("--json", action="store_true", help="Output JSON")
    
    # Market command
    market_p = subparsers.add_parser("market", help="Get specific market")
    market_p.add_argument("ticker")
    
    # Search command
    search_p = subparsers.add_parser("search", help="Search markets")
    search_p.add_argument("query")
    
    # Edge command
    edge_p = subparsers.add_parser("edge", help="Find markets aligned with V's positions")
    edge_p.add_argument("--json", action="store_true")
    
    args = parser.parse_args()
    
    if args.command == "markets":
        data = get_markets(status=args.status, limit=args.limit, series_ticker=args.series)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            for m in data.get("markets", []):
                print(format_market(m))
                print("-" * 60)
    
    elif args.command == "market":
        data = get_market(args.ticker)
        print(json.dumps(data, indent=2))
    
    elif args.command == "search":
        markets = search_markets(args.query)
        print(f"Found {len(markets)} markets matching '{args.query}':\n")
        for m in markets[:20]:
            print(format_market(m))
            print("-" * 60)
    
    elif args.command == "edge":
        results = find_edge_markets()
        if args.json:
            print(json.dumps([{"score": s, "market": m} for s, m in results], indent=2))
        else:
            print(f"=== Markets Aligned With V's Positions ===\n")
            for score, m in results[:20]:
                print(f"[Score: {score}]")
                print(format_market(m))
                print("-" * 60)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

