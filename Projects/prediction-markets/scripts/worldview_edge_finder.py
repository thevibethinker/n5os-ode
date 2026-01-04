#!/usr/bin/env python3
"""
Worldview Edge Finder v2 - Semantic Matching

Uses LLM-based semantic matching to connect V's positions to prediction markets.
No regex fallbacks - if there's no genuine semantic connection, we don't surface it.

Usage:
    python worldview_edge_finder.py fetch         # Fetch markets and positions for LLM analysis
    python worldview_edge_finder.py markets       # List relevant open markets
    python worldview_edge_finder.py positions     # List V's high-confidence positions
"""

import argparse
import json
import sqlite3
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

# Paths
POSITIONS_DB = Path("/home/workspace/N5/data/positions.db")
OUTPUT_DIR = Path("/home/workspace/Projects/prediction-markets/analysis")

# Kalshi API
API_BASE = "https://api.elections.kalshi.com/trade-api/v2"

# Series tickers in V's potential edge domains
EDGE_SERIES = [
    # Labor/Employment
    "UNRATE", "KXINITCLAIMS", "KXJOBSM", "KXFEDEMPLOYEES", "LAYOFFSYINFO",
    # Economic indicators  
    "KXGDP", "KXRECESSION", "KXCPI", "KXINFLATION", "FED",
    # Tech/AI companies
    "OAIAGI", "KXOPENAIIPO", "KXGOOGLECEOCHANGE", "KXMETACEOCHANGE",
    # Corporate behavior
    "KXSP500", "KXTECHLAYOFFS",
]


def api_get(endpoint: str, params: dict = None) -> dict:
    """Make GET request to Kalshi API with rate limiting."""
    url = f"{API_BASE}/{endpoint}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    
    req = Request(url, headers={"Accept": "application/json"})
    time.sleep(0.5)  # Rate limiting
    
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 429:
            time.sleep(2)
            return api_get(endpoint, params)
        raise


def get_positions(min_confidence: int = 3) -> list[dict]:
    """Load V's positions from the database."""
    if not POSITIONS_DB.exists():
        return []
    
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("""
        SELECT id, title, domain, insight, confidence, stability
        FROM positions 
        WHERE confidence >= ?
        ORDER BY confidence DESC, stability DESC
    """, (min_confidence,)).fetchall()
    
    conn.close()
    return [dict(r) for r in rows]


def get_edge_markets() -> list[dict]:
    """Fetch open markets in edge-relevant categories."""
    markets = []
    
    # Get Economics, Companies, and Financials categories
    for category in ["Economics", "Companies", "Financials"]:
        try:
            data = api_get("markets", {"status": "open", "limit": 50})
            for m in data.get("markets", []):
                # Only include if has meaningful volume and price
                if m.get("volume", 0) > 1000:
                    markets.append({
                        "ticker": m.get("ticker"),
                        "title": m.get("title"),
                        "subtitle": m.get("subtitle", ""),
                        "yes_bid": m.get("yes_bid"),
                        "yes_ask": m.get("yes_ask"),
                        "volume": m.get("volume"),
                        "close_time": m.get("close_time"),
                        "category": m.get("category", ""),
                    })
        except Exception as e:
            print(f"Error fetching {category}: {e}")
    
    # Also fetch specific series we care about
    for series in EDGE_SERIES:
        try:
            data = api_get("markets", {"series_ticker": series, "status": "open"})
            for m in data.get("markets", []):
                if m.get("volume", 0) > 100:  # Lower threshold for specific series
                    markets.append({
                        "ticker": m.get("ticker"),
                        "title": m.get("title"),
                        "subtitle": m.get("subtitle", ""),
                        "yes_bid": m.get("yes_bid"),
                        "yes_ask": m.get("yes_ask"),
                        "volume": m.get("volume"),
                        "close_time": m.get("close_time"),
                        "series": series,
                    })
        except Exception:
            pass  # Series may not exist
    
    # Dedupe by ticker
    seen = set()
    unique = []
    for m in markets:
        if m["ticker"] not in seen:
            seen.add(m["ticker"])
            unique.append(m)
    
    return unique


def format_for_llm_analysis(positions: list[dict], markets: list[dict]) -> str:
    """
    Format positions and markets for LLM semantic analysis.
    
    The LLM will determine genuine connections - no keyword matching here.
    """
    output = []
    
    output.append("=" * 70)
    output.append("SEMANTIC MATCHING REQUEST")
    output.append("=" * 70)
    output.append("""
Task: Identify which of V's POSITIONS genuinely inform predictions on which MARKETS.

Rules:
1. Only match if the position provides REAL inferential value for the market outcome
2. A position about "AI impact on work" does NOT match "Will OpenAI announce AGI"
3. A position about "hiring signal collapse" DOES match "unemployment rate" markets
4. Be conservative - false negatives are better than false positives
5. For each match, explain the causal/inferential chain

Output format for each genuine match:
- Position ID → Market Ticker
- Inference chain: [How position informs market prediction]
- Direction: [Does position suggest YES or NO is underpriced?]
- Confidence in match: [High/Medium/Low]
""")
    
    output.append("\n" + "=" * 70)
    output.append("V'S POSITIONS")
    output.append("=" * 70)
    
    for p in positions:
        output.append(f"""
ID: {p['id']}
Domain: {p['domain']}
Title: {p['title']}
Confidence: {p['confidence']}/5
Insight: {p['insight'][:500]}{'...' if len(p.get('insight', '')) > 500 else ''}
""")
    
    output.append("\n" + "=" * 70)
    output.append("OPEN MARKETS")
    output.append("=" * 70)
    
    for m in markets:
        yes_bid = m.get('yes_bid', 0)
        yes_ask = m.get('yes_ask', 0)
        mid = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else 0
        
        output.append(f"""
Ticker: {m['ticker']}
Title: {m['title']}
{f"Subtitle: {m['subtitle']}" if m.get('subtitle') else ""}
Market Price: {yes_bid}¢ / {yes_ask}¢ (midpoint: {mid:.0f}%)
Volume: ${m.get('volume', 0):,}
Closes: {m.get('close_time', 'N/A')}
""")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Worldview Edge Finder v2")
    parser.add_argument("command", choices=["fetch", "markets", "positions"],
                       help="Command to run")
    parser.add_argument("--min-confidence", type=int, default=3,
                       help="Minimum position confidence (default: 3)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == "positions":
        positions = get_positions(args.min_confidence)
        print(f"Found {len(positions)} positions with confidence >= {args.min_confidence}\n")
        for p in positions:
            print(f"[{p['domain']}] {p['id']} (conf: {p['confidence']}/5)")
            print(f"  {p['title']}")
            print(f"  {p['insight'][:200]}...")
            print()
    
    elif args.command == "markets":
        print("Fetching markets in edge domains...")
        markets = get_edge_markets()
        print(f"Found {len(markets)} markets with volume\n")
        for m in markets:
            yes_bid = m.get('yes_bid', 0)
            yes_ask = m.get('yes_ask', 0)
            print(f"{m['ticker']}: {m['title']}")
            print(f"  Price: {yes_bid}¢ / {yes_ask}¢ | Vol: ${m.get('volume', 0):,}")
            print()
    
    elif args.command == "fetch":
        print("Loading positions...")
        positions = get_positions(args.min_confidence)
        print(f"Found {len(positions)} positions\n")
        
        print("Fetching markets...")
        markets = get_edge_markets()
        print(f"Found {len(markets)} markets\n")
        
        # Generate LLM analysis prompt
        analysis = format_for_llm_analysis(positions, markets)
        
        # Save to file for LLM to process
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = args.output or OUTPUT_DIR / "semantic_match_request.md"
        Path(output_path).write_text(analysis)
        
        print(f"Saved analysis request to: {output_path}")
        print("\nNext step: Feed this to the LLM for semantic matching.")
        print("The LLM will identify genuine position→market connections.")


if __name__ == "__main__":
    main()

