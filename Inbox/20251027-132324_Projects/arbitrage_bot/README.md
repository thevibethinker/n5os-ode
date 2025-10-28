# Prediction Market Arbitrage Bot

Automated system for detecting and exploiting arbitrage opportunities between Kalshi and Polymarket prediction markets.

## What This Does

Finds "free money" opportunities when the same event trades at different prices across platforms:
- **Kalshi:** Yes @ 6.3¢ + **Polymarket:** No @ 92¢ = 98.3¢ total
- **Guaranteed payout:** $1.00 (one outcome must occur)
- **Risk-free profit:** 1.7¢ per dollar

## Quick Start

### 1. Test the Scanner (No credentials needed)

```bash
cd /home/workspace/Projects/arbitrage_bot
python3 arbitrage_poc.py
```

This will:
- Fetch live markets from both platforms
- Find matching markets
- Calculate arbitrage opportunities
- Show profit potential

### 2. Read the Documentation

- **`EXECUTIVE_SUMMARY.md`** - Start here! Quick overview and recommendation
- **`arbitrage_analysis.md`** - Full feasibility study with technical details
- **`SETUP_GUIDE.md`** - Implementation guide for production bot
- **`arbitrage_poc.py`** - Working Python scanner (450 lines)

## Files Included

| File | Purpose | Size |
|------|---------|------|
| `EXECUTIVE_SUMMARY.md` | Quick overview, recommendation | 8.7 KB |
| `arbitrage_analysis.md` | Complete feasibility analysis | 16 KB |
| `SETUP_GUIDE.md` | Implementation guide | 11 KB |
| `arbitrage_poc.py` | Working scanner (runnable now) | 15 KB |

## Verdict

**✅ FEASIBLE & POTENTIALLY PROFITABLE**

- Both APIs are accessible and bot-friendly
- Opportunities do exist (proven by Twitter example)
- Low technical barriers
- Expected return: 10-30% annually

## Recommended Next Steps

### Week 1: Validate
Run the scanner daily for 7 days to measure opportunity frequency.

```bash
# Run once per day
python3 arbitrage_poc.py >> scan_log.txt
```

### Week 2: Setup (If opportunities exist)
1. Create accounts on both platforms
2. Get API credentials
3. Test with small amounts

### Week 3-4: Automate
1. Add real-time monitoring (WebSockets)
2. Build alert system
3. Semi-automated trading

## Requirements

```bash
pip install aiohttp python-dotenv kalshi-python pandas
```

## Safety Note

Start small. This is arbitrage (low risk) but still requires:
- Capital (locked until markets settle)
- API reliability
- Correct execution
- Fee management

## Questions?

Review the executive summary first, then the full analysis for details.

---

**Built:** 2025-10-22  
**Status:** Proof of concept (scanner works, trading not yet implemented)  
**Platform APIs:** Kalshi (REST/WebSocket) + Polymarket (CLOB/Gamma)
