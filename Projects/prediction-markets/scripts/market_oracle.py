#!/usr/bin/env python3
"""
Market Oracle: V's Worldview → Prediction Market Probabilities

Queries V's semantic memory (brain) with market questions, synthesizes
related beliefs, and generates probability estimates.

This is the semantic approach V described:
1. Query semantic memory with the market question
2. Retrieve all related beliefs (positions, knowledge, meeting insights)
3. Synthesize into a probability estimate
4. Compare to market price to find edge

Usage:
    python market_oracle.py query "Will there be a US recession in 2026?"
    python market_oracle.py analyze TICKER
    python market_oracle.py scan  # Scan all edge markets
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from datetime import datetime

# Add N5 to path
sys.path.insert(0, '/home/workspace')
from N5.cognition.n5_memory_client import N5MemoryClient

# Paths
OUTPUT_DIR = Path("/home/workspace/Projects/prediction-markets/analysis")
TRADE_LOG = Path("/home/workspace/Projects/prediction-markets/logs/trade_log.md")

# Kalshi API
API_BASE = "https://api.elections.kalshi.com/trade-api/v2"


def api_get(endpoint: str, params: dict = None) -> dict:
    """Make GET request to Kalshi API with rate limiting."""
    url = f"{API_BASE}/{endpoint}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    
    req = Request(url, headers={"Accept": "application/json"})
    time.sleep(0.5)
    
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 429:
            time.sleep(2)
            return api_get(endpoint, params)
        raise


def get_market_by_ticker(ticker: str) -> dict:
    """Fetch a specific market by ticker."""
    try:
        data = api_get(f"markets/{ticker}")
        return data.get("market", {})
    except Exception as e:
        print(f"Error fetching market {ticker}: {e}")
        return {}


def query_semantic_memory(question: str, limit: int = 15) -> list[dict]:
    """
    Query V's semantic memory with a market question.
    Returns related beliefs, positions, and knowledge.
    """
    client = N5MemoryClient()
    results = client.search(question, limit=limit)
    return results


def format_synthesis_prompt(question: str, memory_results: list[dict], market_info: dict = None) -> str:
    """
    Format the synthesis prompt for LLM analysis.
    
    The LLM will synthesize V's beliefs into a probability estimate.
    """
    output = []
    
    output.append("=" * 70)
    output.append("MARKET ORACLE: SYNTHESIZE V'S WORLDVIEW INTO PROBABILITY")
    output.append("=" * 70)
    
    if market_info:
        yes_bid = market_info.get("yes_bid", 0)
        yes_ask = market_info.get("yes_ask", 0)
        mid = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else 0
        
        output.append(f"""
MARKET QUESTION: {question}
TICKER: {market_info.get('ticker', 'N/A')}
CURRENT MARKET PRICE: {yes_bid}¢ / {yes_ask}¢ (midpoint: {mid:.0f}%)
VOLUME: ${market_info.get('volume', 0):,}
CLOSES: {market_info.get('close_time', 'N/A')}
""")
    else:
        output.append(f"\nQUESTION: {question}\n")
    
    output.append("=" * 70)
    output.append("V'S RELATED BELIEFS FROM SEMANTIC MEMORY")
    output.append("=" * 70)
    output.append("""
The following are excerpts from V's brain - positions, knowledge documents,
meeting insights, and recorded beliefs. These represent his actual worldview.
""")
    
    for i, r in enumerate(memory_results, 1):
        score = r.get('score', 0)
        path = r.get('path', 'Unknown')
        content = r.get('content', '')[:800]  # Truncate for prompt size
        
        # Extract source type from path
        if '/Meetings/' in path:
            source_type = "Meeting Intelligence"
        elif '/Knowledge/' in path:
            source_type = "Knowledge Document"
        elif '/positions' in path.lower():
            source_type = "Position"
        else:
            source_type = "Document"
        
        output.append(f"""
--- BELIEF #{i} (relevance: {score:.2f}) ---
Source: {source_type}
Path: {path}

{content}
""")
    
    output.append("=" * 70)
    output.append("SYNTHESIS TASK")
    output.append("=" * 70)
    output.append("""
Based on the beliefs above, synthesize V's worldview into a response:

1. RELEVANT BELIEFS: Which of the above beliefs actually inform this question?
   (List only the genuinely relevant ones with brief explanation of why)

2. BELIEF SYNTHESIS: How do these beliefs compound/interact to inform a view?
   (Show your reasoning chain)

3. PROBABILITY ESTIMATE: What probability would V assign to YES?
   Format: XX% (with confidence interval if uncertain, e.g., "25-35%")

4. EDGE ASSESSMENT (if market info provided):
   - V's estimate vs market price
   - Direction: Is YES or NO underpriced?
   - Edge size: How many percentage points of edge?
   - Confidence: High/Medium/Low that this is real edge (not just noise)

5. KEY UNCERTAINTIES: What would change V's estimate significantly?

Be specific. Use V's actual language and concepts from the beliefs above.
Do not hallucinate beliefs V doesn't hold - only synthesize from what's provided.
""")
    
    return "\n".join(output)


def save_synthesis_request(question: str, prompt: str, ticker: str = None):
    """Save the synthesis request for LLM processing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"oracle_{ticker or 'query'}_{timestamp}.md"
    filepath = OUTPUT_DIR / filename
    
    filepath.write_text(prompt)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Market Oracle: V's Worldview → Probabilities")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Query command - ask any question
    query_parser = subparsers.add_parser("query", help="Query V's worldview on any question")
    query_parser.add_argument("question", type=str, help="The question to ask")
    query_parser.add_argument("--limit", type=int, default=15, help="Number of memory results")
    
    # Analyze command - analyze a specific Kalshi market
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a specific Kalshi market")
    analyze_parser.add_argument("ticker", type=str, help="Kalshi market ticker")
    analyze_parser.add_argument("--limit", type=int, default=15, help="Number of memory results")
    
    # Scan command - scan multiple markets
    scan_parser = subparsers.add_parser("scan", help="Scan edge markets for opportunities")
    scan_parser.add_argument("--limit", type=int, default=10, help="Number of markets to scan")
    
    args = parser.parse_args()
    
    if args.command == "query":
        print(f"Querying V's semantic memory: {args.question}\n")
        
        results = query_semantic_memory(args.question, limit=args.limit)
        print(f"Found {len(results)} related beliefs\n")
        
        prompt = format_synthesis_prompt(args.question, results)
        filepath = save_synthesis_request(args.question[:30], prompt)
        
        print(f"Synthesis request saved to: {filepath}")
        print("\n" + "=" * 70)
        print("RELEVANT BELIEFS RETRIEVED:")
        print("=" * 70)
        for i, r in enumerate(results[:5], 1):
            print(f"\n{i}. [{r.get('score', 0):.2f}] {r.get('path', 'N/A')[-50:]}")
            print(f"   {r.get('content', '')[:150]}...")
        
        print("\n" + "=" * 70)
        print("Next: Feed the synthesis request to the LLM for probability estimate")
        print("=" * 70)
    
    elif args.command == "analyze":
        print(f"Fetching market: {args.ticker}\n")
        
        market = get_market_by_ticker(args.ticker)
        if not market:
            print(f"Market {args.ticker} not found")
            return
        
        title = market.get("title", "")
        subtitle = market.get("subtitle", "")
        question = f"{title} {subtitle}".strip()
        
        print(f"Market question: {question}\n")
        print("Querying V's semantic memory...\n")
        
        results = query_semantic_memory(question, limit=args.limit)
        print(f"Found {len(results)} related beliefs\n")
        
        prompt = format_synthesis_prompt(question, results, market)
        filepath = save_synthesis_request(question[:30], prompt, args.ticker)
        
        # Print summary
        yes_bid = market.get("yes_bid", 0)
        yes_ask = market.get("yes_ask", 0)
        print("=" * 70)
        print(f"MARKET: {question}")
        print(f"TICKER: {args.ticker}")
        print(f"PRICE: {yes_bid}¢ / {yes_ask}¢")
        print("=" * 70)
        print(f"\nSynthesis request saved to: {filepath}")
        print("\nTop relevant beliefs:")
        for i, r in enumerate(results[:5], 1):
            print(f"  {i}. [{r.get('score', 0):.2f}] {r.get('content', '')[:100]}...")
    
    elif args.command == "scan":
        print("Scanning edge markets...\n")
        
        # Fetch markets in edge categories
        edge_series = ["UNRATE", "KXRECESSION", "KXTECHLAYOFFS", "KXJOBSM", "KXGDP"]
        
        markets = []
        for series in edge_series:
            try:
                data = api_get("markets", {"series_ticker": series, "status": "open"})
                markets.extend(data.get("markets", []))
            except Exception:
                pass
        
        print(f"Found {len(markets)} markets in edge domains\n")
        
        for m in markets[:args.limit]:
            ticker = m.get("ticker")
            title = m.get("title", "")
            yes_bid = m.get("yes_bid", 0)
            yes_ask = m.get("yes_ask", 0)
            print(f"{ticker}: {title}")
            print(f"  Price: {yes_bid}¢ / {yes_ask}¢")
            print()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

