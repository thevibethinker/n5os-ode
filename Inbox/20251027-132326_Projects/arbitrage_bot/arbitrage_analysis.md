# Prediction Market Arbitrage Bot - Feasibility Analysis

**Date:** 2025-10-22  
**Platforms:** Kalshi & Polymarket  
**Opportunity:** Cross-platform arbitrage on binary prediction markets

---

## Executive Summary

**VERDICT: HIGHLY FEASIBLE** ✅

Both Kalshi and Polymarket provide public APIs suitable for building an arbitrage bot. The opportunity described in the Twitter post is real and exploitable programmatically.

### The Arbitrage Opportunity

**Example from post (Andrew Cuomo NYC Mayor):**
- Kalshi: Buy "Yes" @ 6.3¢
- Polymarket: Buy "No" @ 92¢  
- **Total cost:** 98.3¢
- **Guaranteed payout:** $1.00 (one position will win)
- **Guaranteed profit:** 1.7¢ per dollar (1.7% return)

**How it works:**
1. Same binary event traded on both platforms
2. Price inefficiencies exist between platforms
3. When `Kalshi_Yes + Polymarket_No < 100¢` → guaranteed profit
4. Or when `Polymarket_Yes + Kalshi_No < 100¢` → guaranteed profit

---

## API Capabilities Assessment

### Kalshi API [^1]

**Status:** ✅ Full REST + WebSocket API available  
**Access:** Free (tiered rate limits based on activity)  
**Documentation:** https://docs.kalshi.com/

**Key Features:**
- **Market Data Access:** Real-time orderbook, market prices, historical data
- **WebSocket Support:** Live price streaming for fast arbitrage detection
- **Trading:** Full order management (create, cancel, batch operations)
- **Rate Limits:** Tiered system (Basic → Advanced → Premier → Prime)
- **Demo Environment:** Test environment available for development
- **Python SDK:** Official `kalshi-python` package available [^2]

**Critical Endpoints:**
- `GET /markets` - List all markets with current prices
- `GET /markets/{market_ticker}/orderbook` - Real-time bid/ask data
- `POST /orders` - Place orders programmatically
- WebSocket - Subscribe to price updates

**Rate Limit Tiers:**
- Basic: Default tier (sufficient for testing)
- Advanced: Request via form (higher limits)
- Premier/Prime: High-frequency trading support

### Polymarket API [^3]

**Status:** ✅ Multiple APIs available (CLOB, Gamma, Data-API)  
**Access:** Free for market data, authentication required for trading  
**Documentation:** https://docs.polymarket.com/

**Key Features:**
- **Market Data:** Via Gamma API (read-only, no auth required)
- **Order Book:** CLOB API provides real-time pricing
- **Trading:** CLOB API for order placement (requires API keys)
- **WebSocket:** Real-time market data streaming
- **Python SDK:** Community `py-clob-client` available [^4]

**Critical Endpoints:**
- Gamma API: `GET https://gamma-api.polymarket.com/markets` - All markets
- CLOB API: `GET https://clob.polymarket.com/price` - Current prices
- CLOB API: `GET https://clob.polymarket.com/book` - Order book
- Data API: `GET https://data-api.polymarket.com/trades` - Trade history

**Important Notes:**
- Gamma API: Public, no authentication needed for market discovery
- CLOB API: Requires API credentials for trading operations
- Hybrid-decentralized architecture (on-chain settlement, off-chain matching)
- Built on Polygon (Ethereum layer-2) - gas fees apply

---

## Technical Architecture

### Bot Components

```
┌─────────────────────────────────────────────────────┐
│              ARBITRAGE BOT SYSTEM                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐        ┌──────────────┐         │
│  │   Kalshi     │        │  Polymarket  │         │
│  │   API Client │        │  API Client  │         │
│  └──────┬───────┘        └──────┬───────┘         │
│         │                       │                  │
│         └───────────┬───────────┘                  │
│                     │                              │
│            ┌────────▼─────────┐                    │
│            │  Market Matcher  │                    │
│            │  - Normalize IDs │                    │
│            │  - Pair markets  │                    │
│            └────────┬─────────┘                    │
│                     │                              │
│            ┌────────▼─────────┐                    │
│            │ Arbitrage Engine │                    │
│            │  - Price monitor │                    │
│            │  - Calculate arb │                    │
│            │  - Risk checks   │                    │
│            └────────┬─────────┘                    │
│                     │                              │
│            ┌────────▼─────────┐                    │
│            │ Execution Engine │                    │
│            │  - Order sizing  │                    │
│            │  - Simultaneous  │                    │
│            │    execution     │                    │
│            └────────┬─────────┘                    │
│                     │                              │
│            ┌────────▼─────────┐                    │
│            │  Logging/Alerts  │                    │
│            │  - Opportunities │                    │
│            │  - Executions    │                    │
│            │  - P&L tracking  │                    │
│            └──────────────────┘                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Core Logic Flow

1. **Market Discovery:**
   - Fetch all active markets from both platforms
   - Normalize market descriptions/questions
   - Create mapping of equivalent markets

2. **Price Monitoring:**
   - Poll or stream prices from both platforms
   - Calculate arbitrage opportunities: `if (price_A + price_B < 0.98): alert`
   - Account for fees (Kalshi: ~3%, Polymarket: gas + exchange fees)

3. **Opportunity Validation:**
   - Check liquidity depth (ensure sufficient volume)
   - Verify market expiry dates match
   - Calculate net profit after all fees
   - Apply minimum profit threshold (e.g., 2% to be safe)

4. **Execution:**
   - Place orders on both platforms simultaneously
   - Monitor fill status
   - Handle partial fills or rejections
   - Log all trades for reconciliation

5. **Position Management:**
   - Track open positions across platforms
   - Calculate realized/unrealized P&L
   - Monitor for settlement/payout

---

## Key Challenges & Mitigations

### Challenge 1: Market Matching
**Problem:** Same event may have different titles/IDs on each platform  
**Solution:** 
- Semantic matching using string similarity algorithms
- Manual curation of high-volume market pairs
- Maintain mapping database of verified pairs

### Challenge 2: Timing/Latency
**Problem:** Prices move fast, opportunity may vanish before execution  
**Solution:**
- Use WebSocket connections for real-time updates
- Place orders simultaneously (asyncio concurrent execution)
- Set conservative profit thresholds to account for slippage

### Challenge 3: Fee Structures
**Problem:** Different fee models on each platform  
**Solution:**
- Kalshi: ~3% fee on profits
- Polymarket: Gas fees (Polygon) + exchange fees
- Build fee calculator into profit calculation
- Minimum profit threshold: 2-3% after all fees

### Challenge 4: Liquidity Risk
**Problem:** Order may not fill completely or at desired price  
**Solution:**
- Check order book depth before placing orders
- Start with small position sizes
- Implement partial fill handling
- Set maximum position limits

### Challenge 5: Settlement Timing
**Problem:** Platforms may settle at different times  
**Solution:**
- Capital must be locked until both positions settle
- Calculate capital efficiency (return per day locked)
- Prefer markets with near-term expiry

### Challenge 6: Regulatory/TOS Compliance
**Problem:** Arbitrage bots might violate terms of service  
**Solution:**
- Review TOS for both platforms (neither explicitly prohibits arbitrage)
- Stay within rate limits
- Operate transparently (no spoofing/manipulation)
- Kalshi is CFTC-regulated (US only); Polymarket is offshore

---

## Cost-Benefit Analysis

### Development Costs
- **Initial Build:** 20-40 hours (depending on sophistication)
- **Testing/Refinement:** 10-20 hours
- **Ongoing Maintenance:** 2-4 hours/week

### Operating Costs
- **Infrastructure:** $10-50/month (hosting, monitoring)
- **Gas Fees (Polymarket):** ~$0.01-0.10 per trade on Polygon
- **Trading Fees:** 3% of profits (Kalshi)
- **Capital Requirements:** $500-5,000+ (more capital = more opportunities)

### Expected Returns
- **Per Opportunity:** 1-5% guaranteed profit (after fees)
- **Frequency:** Depends on market inefficiency
- **Risk:** Low (arbitrage is theoretically risk-free if executed correctly)
- **Scalability:** Limited by capital and market liquidity

### ROI Estimate
- **Conservative:** 10-20% annual return on deployed capital
- **Optimistic:** 30-50% if opportunities are frequent
- **Reality Check:** Arbitrage opportunities tend to disappear as more bots enter

---

## Proof of Concept Implementation

### Phase 1: Data Collection (Week 1)
- [ ] Set up API clients for both platforms
- [ ] Fetch all active markets
- [ ] Build market matching algorithm
- [ ] Calculate historical arbitrage opportunities
- [ ] Generate report of opportunity frequency/size

### Phase 2: Monitoring Bot (Week 2)
- [ ] Real-time price monitoring
- [ ] Arbitrage detection engine
- [ ] Alert system (email/SMS when opportunities arise)
- [ ] Dashboard for visualization

### Phase 3: Paper Trading (Week 3-4)
- [ ] Simulate order execution (no real trades)
- [ ] Track hypothetical P&L
- [ ] Refine fee calculations
- [ ] Optimize profit thresholds

### Phase 4: Live Trading (Week 5+)
- [ ] Start with small position sizes ($10-50)
- [ ] Gradual scale-up based on success rate
- [ ] Monitor for issues (failed orders, timing problems)
- [ ] Optimize execution speed

---

## Code Architecture

### Technology Stack
- **Language:** Python 3.11+ (async/await support)
- **Key Libraries:**
  - `aiohttp` - Async HTTP requests
  - `websockets` - Real-time price feeds
  - `kalshi-python` - Official Kalshi SDK
  - `py-clob-client` - Polymarket client
  - `pandas` - Data analysis
  - `sqlite3` - Local database for market mappings
  - `python-dotenv` - Credentials management

### Module Structure
```
arbitrage_bot/
├── clients/
│   ├── kalshi_client.py      # Kalshi API wrapper
│   ├── polymarket_client.py  # Polymarket API wrapper
│   └── base_client.py        # Shared interface
├── matching/
│   ├── market_matcher.py     # Match markets across platforms
│   └── similarity.py         # String similarity algorithms
├── arbitrage/
│   ├── detector.py           # Find arbitrage opportunities
│   ├── calculator.py         # Profit calculations with fees
│   └── validator.py          # Risk checks, liquidity checks
├── execution/
│   ├── executor.py           # Order placement logic
│   └── position_tracker.py   # Track open positions
├── monitoring/
│   ├── price_monitor.py      # Real-time price tracking
│   └── alerts.py             # Notification system
├── database/
│   ├── models.py             # Data models
│   └── db.py                 # Database operations
├── config/
│   ├── settings.py           # Configuration
│   └── credentials.env       # API keys (gitignored)
├── main.py                   # Entry point
└── tests/                    # Unit tests
```

---

## Next Steps

### Immediate Actions (Can Do Now)
1. ✅ **API Access Verification:**
   - Create accounts on both platforms
   - Generate API credentials
   - Test basic API calls (market data fetching)

2. ✅ **Market Survey:**
   - Pull list of all active markets from both platforms
   - Manually identify 10-20 matching market pairs
   - Document any naming/ID differences

3. ✅ **Opportunity Scanner:**
   - Build simple script to check current prices for matched pairs
   - Calculate potential arbitrage profits
   - Generate daily report of opportunities

### Short-term Development (1-2 Weeks)
4. **Build Core Bot:**
   - Implement real-time monitoring
   - Add fee calculations
   - Create alert system

5. **Backtesting:**
   - Collect historical price data
   - Simulate past opportunities
   - Validate profit assumptions

### Long-term (1+ Month)
6. **Live Trading:**
   - Start with manual execution based on bot alerts
   - Graduate to semi-automated execution
   - Eventually full automation (with safeguards)

7. **Optimization:**
   - Improve market matching accuracy
   - Reduce latency
   - Add more sophisticated risk management

---

## Risk Disclaimer

### Technical Risks
- **Execution Risk:** Orders may not fill at expected prices
- **Timing Risk:** Opportunity may disappear before both orders execute
- **API Risk:** APIs may go down or change without notice
- **Bug Risk:** Code errors could lead to unintended trades

### Financial Risks
- **Capital Lock:** Money tied up until market resolves
- **Fee Erosion:** Fees may exceed expected profit on small trades
- **Platform Risk:** Platform could freeze funds or change rules

### Regulatory Risks
- **Kalshi:** US-only, CFTC regulated (geographic restrictions)
- **Polymarket:** Offshore, may have legal gray areas
- **Tax Implications:** Gains may be taxable as ordinary income or gambling winnings

---

## Conclusion

Building an arbitrage bot for Kalshi/Polymarket is **technically feasible** and **potentially profitable**. Both platforms provide robust APIs suitable for algorithmic trading.

**Key Success Factors:**
1. Fast execution (WebSockets + async programming)
2. Accurate market matching (semantic algorithms + manual curation)
3. Conservative profit thresholds (account for all fees + slippage)
4. Proper risk management (position limits, error handling)

**Recommendation:**
- **Phase 1 (Now):** Build monitoring/alert system (10-15 hours)
- **Phase 2 (2-4 weeks):** Paper trade to validate approach
- **Phase 3 (1-2 months):** Start live trading with small amounts

**Expected ROI:** 15-30% annual return on deployed capital (conservative estimate)

The opportunity exists, but may diminish as more traders (and bots) exploit these inefficiencies. First-mover advantage is real in arbitrage markets.

---

[^1]: https://docs.kalshi.com/
[^2]: https://pypi.org/project/kalshi-python/
[^3]: https://docs.polymarket.com/
[^4]: https://github.com/Polymarket/py-clob-client
