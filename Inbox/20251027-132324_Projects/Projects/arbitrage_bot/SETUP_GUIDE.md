# Arbitrage Bot Setup Guide

## Quick Start

### Prerequisites
```bash
# Install required packages
pip install aiohttp python-dotenv kalshi-python pandas
```

### Run the POC Scanner
```bash
# Make executable
chmod +x arbitrage_poc.py

# Run a single scan
python3 arbitrage_poc.py
```

This will:
1. Fetch all active markets from Kalshi and Polymarket
2. Match equivalent markets across platforms
3. Calculate arbitrage opportunities
4. Display results with profit estimates

---

## Next Steps for Production Bot

### 1. Get API Credentials

#### Kalshi
1. Sign up at https://kalshi.com/
2. Navigate to Settings → API Keys
3. Generate new API key (will get key ID + private key file)
4. Save credentials securely

#### Polymarket
1. Sign up at https://polymarket.com/
2. Follow their API docs: https://docs.polymarket.com/developers/CLOB/authentication
3. Generate API credentials (requires wallet setup)
4. Note: Trading requires crypto (USDC on Polygon)

### 2. Create Credentials File

Create `.env` file:
```bash
# Kalshi credentials
KALSHI_API_KEY_ID=your_key_id_here
KALSHI_PRIVATE_KEY_PATH=/path/to/private_key.pem

# Polymarket credentials
POLYMARKET_API_KEY=your_api_key_here
POLYMARKET_API_SECRET=your_api_secret_here
POLYMARKET_API_PASSPHRASE=your_passphrase_here
POLYMARKET_PRIVATE_KEY=your_wallet_private_key_here
```

### 3. Enhanced Bot Features to Add

#### A. Real-time Monitoring
- WebSocket connections for live price updates
- Immediate alerts when opportunities arise
- Discord/Telegram/Email notifications

#### B. Automated Execution
- Order placement on both platforms simultaneously
- Partial fill handling
- Position tracking and reconciliation

#### C. Risk Management
- Maximum position size limits
- Stop-loss mechanisms
- Circuit breakers for API errors

#### D. Analytics Dashboard
- Historical opportunity tracking
- P&L visualization
- Performance metrics

### 4. Development Roadmap

**Week 1: Foundation**
- [ ] Set up accounts on both platforms
- [ ] Get API credentials
- [ ] Test API access with simple calls
- [ ] Run POC scanner to verify functionality

**Week 2: Real-time Monitoring**
- [ ] Implement WebSocket connections
- [ ] Build alert system
- [ ] Create monitoring dashboard
- [ ] Track opportunity frequency and size

**Week 3: Paper Trading**
- [ ] Simulate order execution
- [ ] Track hypothetical P&L
- [ ] Refine fee calculations
- [ ] Test edge cases

**Week 4: Live Trading (Small Scale)**
- [ ] Start with $50-100 positions
- [ ] Manual order placement initially
- [ ] Monitor execution quality
- [ ] Optimize for speed and reliability

**Month 2+: Scale & Optimize**
- [ ] Automate execution
- [ ] Increase position sizes
- [ ] Add more sophisticated matching
- [ ] Implement machine learning for prediction

---

## Testing the POC

### Manual Test Run

```bash
# Run the scanner
python3 arbitrage_poc.py

# Expected output:
# - Number of markets fetched from each platform
# - Number of matched market pairs
# - List of arbitrage opportunities (if any)
# - Profit calculations
```

### Example Output
```
🤖 Starting Prediction Market Arbitrage Scanner...
⏰ Scan time: 2025-10-22 15:30:00
----------------------------------------------------------------------
📊 Fetching markets from both platforms...
Fetched 150 markets from Kalshi
Fetched 200 markets from Polymarket
🔍 Matching markets across platforms...
Found 45 matching market pairs
💰 Scanning for arbitrage opportunities...

======================================================================
📈 SCAN COMPLETE
======================================================================
Markets scanned: 150 (Kalshi) + 200 (Polymarket)
Matching pairs found: 45
Arbitrage opportunities: 3

🎯 TOP OPPORTUNITIES:

======================================================================
OPPORTUNITY #1
======================================================================
🎯 ARBITRAGE OPPORTUNITY DETECTED
======================================================================
Market Question:
  Will Andrew Cuomo be elected NYC Mayor in 2025?

Strategy: YES_A_NO_B
  → Kalshi: Buy at 6.3¢
  → Polymarket: Buy at 92.0¢

💰 Profit Analysis:
  Total Cost:         98.30¢
  Guaranteed Payout:  100.00¢
  Profit:             1.17¢
  Return:             1.19%

🔗 Links:
  Kalshi: https://kalshi.com/markets/CUOMO-NYC-2025
  Polymarket: https://polymarket.com/event/andrew-cuomo-nyc-mayor
======================================================================

✅ Scan complete
```

---

## Architecture for Production

### File Structure
```
arbitrage_bot/
├── .env                          # Credentials (DO NOT COMMIT)
├── .gitignore                    # Ignore .env, logs, etc.
├── requirements.txt              # Python dependencies
├── config.py                     # Configuration settings
├── main.py                       # Main bot loop
├── clients/
│   ├── kalshi_client.py         # Kalshi API wrapper
│   ├── polymarket_client.py     # Polymarket API wrapper
│   └── base_client.py           # Shared interface
├── matching/
│   ├── matcher.py               # Market matching logic
│   └── similarity.py            # String similarity algorithms
├── arbitrage/
│   ├── detector.py              # Opportunity detection
│   ├── calculator.py            # Profit calculations
│   └── validator.py             # Risk checks
├── execution/
│   ├── executor.py              # Order placement
│   └── position_tracker.py      # Position management
├── monitoring/
│   ├── websocket_monitor.py     # Real-time price tracking
│   ├── alerts.py                # Notification system
│   └── dashboard.py             # Web dashboard
├── database/
│   ├── models.py                # SQLite models
│   └── db.py                    # Database operations
├── logs/                         # Log files
└── tests/                        # Unit tests
```

### Monitoring Options

#### Option 1: Simple Email Alerts
```python
import smtplib
from email.mime.text import MIMEText

def send_alert(opportunity):
    msg = MIMEText(str(opportunity))
    msg['Subject'] = f'Arbitrage Alert: {opportunity.profit_pct:.2f}% profit'
    msg['From'] = 'bot@yourdomain.com'
    msg['To'] = 'you@yourdomain.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your_email', 'your_password')
        server.send_message(msg)
```

#### Option 2: Discord Webhook
```python
import aiohttp

async def send_discord_alert(opportunity):
    webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
    message = {
        "content": f"🎯 Arbitrage Opportunity: {opportunity.profit_pct:.2f}% profit!",
        "embeds": [{
            "title": opportunity.market_a.question[:100],
            "color": 0x00ff00,
            "fields": [
                {"name": "Strategy", "value": opportunity.strategy},
                {"name": "Profit", "value": f"{opportunity.profit:.2f}¢"},
                {"name": "Return", "value": f"{opportunity.profit_pct:.2f}%"}
            ]
        }]
    }
    
    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json=message)
```

#### Option 3: Telegram Bot
```python
import telegram

async def send_telegram_alert(opportunity):
    bot = telegram.Bot(token='YOUR_BOT_TOKEN')
    chat_id = 'YOUR_CHAT_ID'
    message = f"""
🎯 Arbitrage Opportunity!

Market: {opportunity.market_a.question}
Strategy: {opportunity.strategy}
Profit: {opportunity.profit:.2f}¢ ({opportunity.profit_pct:.2f}%)

Act fast! Opportunities may disappear quickly.
"""
    await bot.send_message(chat_id=chat_id, text=message)
```

---

## Safety Checklist Before Live Trading

- [ ] Verified API credentials work
- [ ] Tested with small amounts ($10-50)
- [ ] Fee calculations are accurate
- [ ] Error handling is robust
- [ ] Position limits are set
- [ ] Alert system works
- [ ] Can manually cancel orders if needed
- [ ] Understand tax implications
- [ ] Read platform TOS for restrictions
- [ ] Have emergency stop mechanism

---

## Monitoring & Optimization

### Key Metrics to Track
1. **Opportunity Frequency:** How often do opportunities appear?
2. **Average Profit:** What's the typical profit percentage?
3. **Execution Speed:** How fast can we detect and act?
4. **Fill Rate:** What % of orders execute successfully?
5. **Slippage:** How much do prices move before execution?

### Optimization Ideas
1. **Latency Reduction:**
   - Use WebSockets instead of polling
   - Host bot near exchange servers (if possible)
   - Optimize code for speed

2. **Better Matching:**
   - Use semantic similarity (word embeddings)
   - Maintain manual curation database
   - Learn from successful matches

3. **Capital Efficiency:**
   - Prefer markets settling soon
   - Calculate ROI per day locked
   - Prioritize high-profit opportunities

4. **Risk Management:**
   - Diversify across multiple markets
   - Set maximum exposure per market
   - Monitor platform health/uptime

---

## FAQ

**Q: Is this legal?**
A: Arbitrage is a legitimate trading strategy. However:
- Kalshi requires US residency and KYC
- Polymarket may have geographic restrictions
- Check local gambling/trading laws

**Q: How much capital do I need?**
A: Start small ($500-1,000) to test. More capital = more opportunities.

**Q: How much profit can I expect?**
A: Conservative estimate: 10-20% annual return. Highly variable.

**Q: Will this work forever?**
A: No. As more traders exploit inefficiencies, opportunities will diminish.

**Q: What are the risks?**
A:
- Execution risk (orders don't fill)
- Platform risk (downtime, rule changes)
- Regulatory risk (legal/tax issues)
- Technical risk (bugs in code)

**Q: Do I need to know how to code?**
A: Basic Python knowledge helps. The POC is designed to be readable for non-experts.

---

## Support & Resources

### Official Documentation
- Kalshi API: https://docs.kalshi.com/
- Polymarket API: https://docs.polymarket.com/

### Community
- Kalshi Discord: https://discord.gg/kalshi
- Polymarket Discord: https://discord.gg/polymarket

### Learning Resources
- Python Async Programming: https://realpython.com/async-io-python/
- Algorithmic Trading Basics: https://www.quantstart.com/

---

## Contact & Disclaimer

This is educational software for research purposes. Use at your own risk.

- No guarantees of profit
- Past performance doesn't predict future results
- Trading involves financial risk
- Consult legal/tax professionals before trading

**Disclaimer:** This bot is provided as-is. The author is not responsible for any financial losses incurred through its use.
