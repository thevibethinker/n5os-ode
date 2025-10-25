# Worker 6: Web Dashboard

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W6-WEB-DASHBOARD  
**Estimated Time:** 2 hours  
**Dependencies:** Worker 5 (RPI Calculator, all data available)

---

## Mission

Build lo-fi Arsenal FC-themed web dashboard using Bun + Hono that displays real-time productivity stats, RPI, XP, level, and historical comparisons.

---

## Context

The dashboard is the daily engagement point. It must be:
- Fast and lightweight
- Arsenal red/white themed
- Mobile-friendly
- Auto-refreshing
- Motivating and clear

---

## Dependencies

Worker 5 complete (RPI calculator, daily_stats populated)

---

## Deliverables

1. `/home/workspace/Sites/productivity-dashboard/` - Bun site
2. Registered user service on public URL
3. Dashboard showing today's stats + week view + era comparison
4. Manual refresh button working

---

## Requirements

### Pages

1. **Home/Today** - Current day stats, Arsenal player card aesthetic
2. **/week** - Last 7 days chart
3. **/history** - Era comparison
4. **/manual-load** - Form to add manual load events

### Today View Components

```
┌─────────────────────────────────────────┐
│     ARSENAL PRODUCTIVITY TRACKER        │
│              🔴 ⚪                       │
├─────────────────────────────────────────┤
│  Today: Friday, Oct 25, 2025            │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  Level 13 - First Team Squad      │  │
│  │  ███████████░░░░░ 75% to Level 14 │  │
│  │  XP: 1,875 / 2,500                │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Today's Performance                    │
│  ━━━━━━━━━━━━━━━━━━━                   │
│                                         │
│  Emails Sent: 10                        │
│  Expected: 8 (5 meetings + 6 incoming)  │
│                                         │
│  RPI: 125% 🔥                          │
│  "Top Performance"                      │
│                                         │
│  XP Earned Today: 281                   │
│  (Base: 225 × 1.25 multiplier + 50 bonus)│
│                                         │
│  Streak: 7 days 🔥                     │
│                                         │
│  Breakdown:                             │
│  • 3 New emails (30 XP)                 │
│  • 5 Follow-ups (40 XP)                 │
│  • 2 Responses (10 XP)                  │
│  • Clean Sheet Bonus (+50 XP)           │
│                                         │
│  [Refresh Stats] [Add Manual Load]      │
└─────────────────────────────────────────┘
```

### Tech Stack

- **Bun** - Runtime
- **Hono** - Web framework
- **SQLite** - Database access
- **Vanilla JS** - Frontend (keep it simple)
- **CSS** - Arsenal red (#EF0107), white (#FFFFFF)

### API Endpoints

- `GET /` - Today view (HTML)
- `GET /api/today` - JSON stats
- `GET /api/week` - Last 7 days JSON
- `GET /api/history` - Era comparison JSON
- `POST /api/manual-load` - Add manual load event
- `POST /api/refresh` - Trigger scanner + RPI calc

---

## Implementation

```typescript
// index.tsx
import { Hono } from 'hono';
import Database from 'bun:sqlite';

const app = new Hono();
const db = new Database('/home/workspace/productivity_tracker.db');

app.get('/', (c) => {
  const today = new Date().toISOString().split('T')[0];
  const stats = db.query(`
    SELECT * FROM daily_stats WHERE date = ?
  `).get(today);
  
  if (!stats) {
    return c.html(`<html>
      <head><title>Arsenal Productivity</title></head>
      <body style="background: #EF0107; color: white; font-family: sans-serif; padding: 2rem;">
        <h1>⚽ Arsenal Productivity Tracker</h1>
        <p>No data for today yet. Run the scanner first!</p>
        <button onclick="fetch('/api/refresh', {method: 'POST'}).then(() => location.reload())">
          Refresh Data
        </button>
      </body>
    </html>`);
  }
  
  return c.html(`<!DOCTYPE html>
  <html>
  <head>
    <title>Arsenal Productivity Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body {
        background: linear-gradient(135deg, #EF0107 0%, #8B0000 100%);
        color: white;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        padding: 1rem;
        margin: 0;
      }
      .container {
        max-width: 600px;
        margin: 0 auto;
        background: rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      }
      .header {
        text-align: center;
        margin-bottom: 2rem;
      }
      .player-card {
        background: white;
        color: #EF0107;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
      }
      .xp-bar {
        background: #ccc;
        height: 24px;
        border-radius: 12px;
        overflow: hidden;
        margin: 0.5rem 0;
      }
      .xp-fill {
        background: linear-gradient(90deg, #EF0107, #FFD700);
        height: 100%;
        transition: width 0.3s;
      }
      .stat-box {
        background: rgba(255,255,255,0.15);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
      }
      .rpi-badge {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
      }
      button {
        background: white;
        color: #EF0107;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        margin: 0.5rem;
      }
      button:hover {
        background: #FFD700;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>⚽ ARSENAL PRODUCTIVITY</h1>
        <p>${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>
      
      <div class="player-card">
        <h2>Level ${stats.level} - ${getRank(stats.level)}</h2>
        <div class="xp-bar">
          <div class="xp-fill" style="width: ${getXPProgress(stats.level)}%"></div>
        </div>
        <p>XP: ${getTotalXP(stats.level)} / ${getNextLevelXP(stats.level)}</p>
      </div>
      
      <div class="stat-box">
        <h3>Today's Performance</h3>
        <div class="rpi-badge">${Math.round(stats.rpi)}% ${getRPIEmoji(stats.rpi)}</div>
        <p style="text-align: center; font-size: 1.2rem;">"${getRPILabel(stats.rpi)}"</p>
      </div>
      
      <div class="stat-box">
        <p><strong>Emails Sent:</strong> ${stats.emails_sent}</p>
        <p><strong>Expected:</strong> ${Math.round(stats.expected_emails)}</p>
        <p><strong>XP Earned:</strong> ${stats.xp_earned} (${stats.xp_multiplier}× multiplier)</p>
        <p><strong>Streak:</strong> ${stats.streak_days} days ${stats.streak_days >= 7 ? '🔥' : ''}</p>
      </div>
      
      <div class="stat-box">
        <h4>Breakdown</h4>
        <p>• ${stats.emails_new} New emails (${stats.emails_new * 10} XP)</p>
        <p>• ${stats.emails_followup} Follow-ups (${stats.emails_followup * 8} XP)</p>
        <p>• ${stats.emails_response} Responses (${stats.emails_response * 5} XP)</p>
      </div>
      
      <div style="text-align: center;">
        <button onclick="refresh()">🔄 Refresh Stats</button>
        <button onclick="location.href='/week'">📊 Week View</button>
      </div>
    </div>
    
    <script>
      function refresh() {
        fetch('/api/refresh', {method: 'POST'})
          .then(() => location.reload());
      }
      
      // Auto-refresh every 30 seconds
      setInterval(() => location.reload(), 30000);
    </script>
  </body>
  </html>`);
});

app.get('/api/today', (c) => {
  const today = new Date().toISOString().split('T')[0];
  const stats = db.query('SELECT * FROM daily_stats WHERE date = ?').get(today);
  return c.json(stats || {});
});

app.post('/api/refresh', async (c) => {
  // Trigger scanners
  // This would call the Python scripts
  return c.json({ status: 'refreshing' });
});

function getRank(level) {
  if (level < 5) return "Youth Academy";
  if (level < 10) return "Reserve Team";
  if (level < 15) return "First Team Squad";
  if (level < 20) return "Regular Starter";
  if (level < 25) return "Club Captain";
  return "Arsenal Legend";
}

function getRPILabel(rpi) {
  if (rpi >= 150) return "Invincible Form";
  if (rpi >= 125) return "Top Performance";
  if (rpi >= 100) return "Meeting Expectations";
  if (rpi >= 75) return "Catch Up Needed";
  return "Behind Schedule";
}

function getRPIEmoji(rpi) {
  if (rpi >= 150) return "👑";
  if (rpi >= 125) return "🔥";
  if (rpi >= 100) return "✓";
  if (rpi >= 75) return "⚠️";
  return "❌";
}

function getXPProgress(level) {
  // Calculate % to next level
  return 65; // Placeholder
}

function getTotalXP(level) {
  return level * level * 100;
}

function getNextLevelXP(level) {
  return (level + 1) * (level + 1) * 100;
}

export default app;
```

---

## Testing

```bash
cd /home/workspace/Sites/productivity-dashboard
bun run index.tsx
# Test at http://localhost:3000
```

---

## Report Back

1. ✅ Dashboard site created
2. ✅ Registered as user service
3. ✅ Public URL: https://va-productivity.zo.computer
4. ✅ Today view working
5. ✅ Arsenal theme applied
6. ✅ Auto-refresh working
7. ✅ Manual refresh button functional

---

**Orchestrator Contact:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 00:15 ET
