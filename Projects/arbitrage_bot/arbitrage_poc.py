#!/usr/bin/env python3
"""
Prediction Market Arbitrage Bot - Proof of Concept
Scans Kalshi and Polymarket for arbitrage opportunities
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Market:
    """Represents a market on a prediction platform"""
    platform: str
    id: str
    question: str
    yes_price: float  # Price in cents (0-100)
    no_price: float
    volume: float
    url: str


@dataclass
class ArbitrageOpportunity:
    """Represents a detected arbitrage opportunity"""
    market_a: Market
    market_b: Market
    strategy: str  # "yes_a_no_b" or "no_a_yes_b"
    total_cost: float  # cents
    guaranteed_payout: float  # cents
    profit: float  # cents
    profit_pct: float
    
    def __str__(self):
        return (
            f"\n{'='*70}\n"
            f"🎯 ARBITRAGE OPPORTUNITY DETECTED\n"
            f"{'='*70}\n"
            f"Market Question:\n  {self.market_a.question}\n\n"
            f"Strategy: {self.strategy.upper()}\n"
            f"  → {self.market_a.platform}: Buy at {self.get_price_a():.1f}¢\n"
            f"  → {self.market_b.platform}: Buy at {self.get_price_b():.1f}¢\n\n"
            f"💰 Profit Analysis:\n"
            f"  Total Cost:         {self.total_cost:.2f}¢\n"
            f"  Guaranteed Payout:  {self.guaranteed_payout:.2f}¢\n"
            f"  Profit:             {self.profit:.2f}¢\n"
            f"  Return:             {self.profit_pct:.2f}%\n\n"
            f"🔗 Links:\n"
            f"  {self.market_a.platform}: {self.market_a.url}\n"
            f"  {self.market_b.platform}: {self.market_b.url}\n"
            f"{'='*70}\n"
        )
    
    def get_price_a(self) -> float:
        """Get the price we're buying on platform A"""
        return self.market_a.yes_price if "yes_a" in self.strategy else self.market_a.no_price
    
    def get_price_b(self) -> float:
        """Get the price we're buying on platform B"""
        return self.market_b.yes_price if "yes_b" in self.strategy else self.market_b.no_price


class KalshiClient:
    """Client for Kalshi API"""
    
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
    
    async def fetch_markets(self, session: aiohttp.ClientSession) -> List[Market]:
        """Fetch all active markets from Kalshi"""
        try:
            url = f"{self.BASE_URL}/markets"
            params = {
                "limit": 200,
                "status": "open"
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Kalshi API error: {response.status}")
                    return []
                
                data = await response.json()
                markets = []
                
                for market_data in data.get("markets", []):
                    try:
                        # Kalshi prices are in cents
                        yes_price = float(market_data.get("yes_bid", 0))
                        no_price = float(market_data.get("no_bid", 0))
                        
                        # If bid prices not available, use ask or last
                        if yes_price == 0:
                            yes_price = float(market_data.get("yes_ask", market_data.get("last_price", 0)))
                        if no_price == 0:
                            no_price = 100 - yes_price
                        
                        market = Market(
                            platform="Kalshi",
                            id=market_data.get("ticker", ""),
                            question=market_data.get("title", ""),
                            yes_price=yes_price,
                            no_price=no_price,
                            volume=float(market_data.get("volume", 0)),
                            url=f"https://kalshi.com/markets/{market_data.get('ticker', '')}"
                        )
                        markets.append(market)
                    except (KeyError, ValueError, TypeError) as e:
                        logger.debug(f"Skipping malformed Kalshi market: {e}")
                        continue
                
                logger.info(f"Fetched {len(markets)} markets from Kalshi")
                return markets
                
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return []


class PolymarketClient:
    """Client for Polymarket API"""
    
    GAMMA_URL = "https://gamma-api.polymarket.com"
    CLOB_URL = "https://clob.polymarket.com"
    
    async def fetch_markets(self, session: aiohttp.ClientSession) -> List[Market]:
        """Fetch all active markets from Polymarket"""
        try:
            url = f"{self.GAMMA_URL}/markets"
            params = {
                "closed": "false",  # String instead of boolean
                "limit": 200
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Polymarket API error: {response.status}")
                    return []
                
                data = await response.json()
                markets: List[Market] = []
                
                for market_data in data:
                    try:
                        yes_price = no_price = None
                        # Preferred: parse outcomePrices from Gamma
                        outcome_prices = market_data.get("outcomePrices")
                        if isinstance(outcome_prices, str) and outcome_prices:
                            import json as _json
                            try:
                                parsed = _json.loads(outcome_prices)
                                if isinstance(parsed, list) and len(parsed) >= 2:
                                    # expect ["0.02", "0.98"] for [Yes, No]
                                    yes_price = float(parsed[0]) * 100.0
                                    no_price = float(parsed[1]) * 100.0
                            except Exception:
                                pass
                        
                        # Fallback: tokens list with per-token price (rare on Gamma)
                        if yes_price is None or no_price is None:
                            tokens = market_data.get("tokens", []) or []
                            if len(tokens) >= 2:
                                yes_token = next((t for t in tokens if str(t.get("outcome", "")).upper() == "YES"), tokens[0])
                                no_token = next((t for t in tokens if str(t.get("outcome", "")).upper() == "NO"), tokens[1])
                                try:
                                    yes_price = float(yes_token.get("price", 0)) * 100.0
                                    no_price = float(no_token.get("price", 0)) * 100.0
                                except Exception:
                                    yes_price = yes_price or 0.0
                                    no_price = no_price or 0.0
                        
                        # If still missing, skip
                        if yes_price is None or no_price is None:
                            continue
                        
                        q = market_data.get("question") or market_data.get("title") or market_data.get("slug") or ""
                        vol_raw = market_data.get("volume") or market_data.get("volumeNum") or 0
                        try:
                            volume = float(vol_raw)
                        except Exception:
                            volume = 0.0
                        slug = market_data.get("slug", "")
                        market = Market(
                            platform="Polymarket",
                            id=str(market_data.get("conditionId") or market_data.get("condition_id") or market_data.get("id") or ""),
                            question=q,
                            yes_price=yes_price,
                            no_price=no_price,
                            volume=volume,
                            url=f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com/"
                        )
                        markets.append(market)
                    except Exception as e:
                        logger.debug(f"Skipping malformed Polymarket market: {e}")
                        continue
                
                logger.info(f"Fetched {len(markets)} markets from Polymarket")
                return markets
                
        except Exception as e:
            logger.error(f"Error fetching Polymarket markets: {e}")
            return []


class MarketMatcher:
    """Matches equivalent markets across platforms"""
    
    @staticmethod
    def normalize_question(question: str) -> str:
        """Normalize market question for comparison"""
        import re
        # Convert to lowercase, remove punctuation, extra whitespace
        normalized = question.lower()
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()
    
    @staticmethod
    def similarity_score(q1: str, q2: str) -> float:
        """Calculate similarity between two questions (0-1)"""
        # Simple word overlap similarity
        words1 = set(MarketMatcher.normalize_question(q1).split())
        words2 = set(MarketMatcher.normalize_question(q2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def find_matches(
        markets_a: List[Market],
        markets_b: List[Market],
        threshold: float = 0.6
    ) -> List[Tuple[Market, Market]]:
        """Find matching markets between two platforms"""
        matches = []
        
        for market_a in markets_a:
            best_match = None
            best_score = 0.0
            
            for market_b in markets_b:
                score = MarketMatcher.similarity_score(
                    market_a.question,
                    market_b.question
                )
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = market_b
            
            if best_match:
                matches.append((market_a, best_match))
                logger.debug(
                    f"Match (score={best_score:.2f}): "
                    f"{market_a.question[:50]}... <-> {best_match.question[:50]}..."
                )
        
        logger.info(f"Found {len(matches)} matching market pairs")
        return matches


class ArbitrageDetector:
    """Detects arbitrage opportunities"""
    
    # Fee structure (estimates)
    KALSHI_FEE_PCT = 3.0  # 3% on profits
    POLYMARKET_GAS_FEE = 0.05  # ~5 cents per trade in gas
    MIN_PROFIT_THRESHOLD = 2.0  # Minimum 2% profit after fees
    
    @staticmethod
    def detect_opportunity(
        market_a: Market,
        market_b: Market
    ) -> Optional[ArbitrageOpportunity]:
        """
        Detect if there's an arbitrage opportunity between two markets
        
        Arbitrage exists when:
        - Kalshi_Yes + Polymarket_No < 100 cents (buy both, win either way)
        - OR Polymarket_Yes + Kalshi_No < 100 cents
        """
        opportunities = []
        
        # Strategy 1: Buy Yes on market_a, No on market_b
        cost_1 = market_a.yes_price + market_b.no_price
        if cost_1 < 100:
            profit = 100 - cost_1
            # Account for fees (simplified)
            profit_after_fees = profit - (profit * ArbitrageDetector.KALSHI_FEE_PCT / 100) - ArbitrageDetector.POLYMARKET_GAS_FEE
            profit_pct = (profit_after_fees / cost_1) * 100
            
            if profit_pct >= ArbitrageDetector.MIN_PROFIT_THRESHOLD:
                opportunities.append(ArbitrageOpportunity(
                    market_a=market_a,
                    market_b=market_b,
                    strategy="yes_a_no_b",
                    total_cost=cost_1,
                    guaranteed_payout=100.0,
                    profit=profit_after_fees,
                    profit_pct=profit_pct
                ))
        
        # Strategy 2: Buy No on market_a, Yes on market_b
        cost_2 = market_a.no_price + market_b.yes_price
        if cost_2 < 100:
            profit = 100 - cost_2
            profit_after_fees = profit - (profit * ArbitrageDetector.KALSHI_FEE_PCT / 100) - ArbitrageDetector.POLYMARKET_GAS_FEE
            profit_pct = (profit_after_fees / cost_2) * 100
            
            if profit_pct >= ArbitrageDetector.MIN_PROFIT_THRESHOLD:
                opportunities.append(ArbitrageOpportunity(
                    market_a=market_a,
                    market_b=market_b,
                    strategy="no_a_yes_b",
                    total_cost=cost_2,
                    guaranteed_payout=100.0,
                    profit=profit_after_fees,
                    profit_pct=profit_pct
                ))
        
        # Return best opportunity (highest profit %)
        if opportunities:
            return max(opportunities, key=lambda x: x.profit_pct)
        
        return None


async def main():
    """Main entry point"""
    logger.info("🤖 Starting Prediction Market Arbitrage Scanner...")
    logger.info(f"⏰ Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("-" * 70)
    
    kalshi = KalshiClient()
    polymarket = PolymarketClient()
    matcher = MarketMatcher()
    detector = ArbitrageDetector()
    
    async with aiohttp.ClientSession() as session:
        # Fetch markets from both platforms
        logger.info("📊 Fetching markets from both platforms...")
        kalshi_markets, polymarket_markets = await asyncio.gather(
            kalshi.fetch_markets(session),
            polymarket.fetch_markets(session)
        )
        
        if not kalshi_markets or not polymarket_markets:
            logger.error("❌ Failed to fetch markets from one or both platforms")
            return
        
        # Match markets across platforms
        logger.info("🔍 Matching markets across platforms...")
        matches = matcher.find_matches(kalshi_markets, polymarket_markets)
        
        if not matches:
            logger.warning("⚠️  No matching markets found")
            return
        
        # Detect arbitrage opportunities
        logger.info("💰 Scanning for arbitrage opportunities...")
        opportunities = []
        
        for kalshi_market, polymarket_market in matches:
            opp = detector.detect_opportunity(kalshi_market, polymarket_market)
            if opp:
                opportunities.append(opp)
        
        # Report results
        logger.info("\n" + "=" * 70)
        logger.info(f"📈 SCAN COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Markets scanned: {len(kalshi_markets)} (Kalshi) + {len(polymarket_markets)} (Polymarket)")
        logger.info(f"Matching pairs found: {len(matches)}")
        logger.info(f"Arbitrage opportunities: {len(opportunities)}")
        
        if opportunities:
            # Sort by profit percentage
            opportunities.sort(key=lambda x: x.profit_pct, reverse=True)
            
            logger.info("\n🎯 TOP OPPORTUNITIES:")
            for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
                print(f"\n{'='*70}")
                print(f"OPPORTUNITY #{i}")
                print(str(opp))
        else:
            logger.info("\n😔 No arbitrage opportunities found at this time.")
            logger.info("💡 Tip: Markets are often efficient. Try running during volatile periods.")
    
    logger.info("\n✅ Scan complete")


if __name__ == "__main__":
    asyncio.run(main())
