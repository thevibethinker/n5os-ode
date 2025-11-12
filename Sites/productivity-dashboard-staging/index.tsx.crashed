import { Hono } from 'hono';
import Database from 'bun:sqlite';

const app = new Hono();
const db = new Database('/home/workspace/productivity_tracker.db');

// Helper functions
function getRank(level: number): string {
  if (level < 5) return "Youth Academy";
  if (level < 10) return "Reserve Team";
  if (level < 15) return "First Team Squad";
  if (level < 20) return "Regular Starter";
  if (level < 25) return "Club Captain";
  return "Arsenal Legend";
}

function getRPILabel(rpi: number): string {
  if (rpi >= 150) return "Invincible Form";
  if (rpi >= 125) return "Top Performance";
  if (rpi >= 100) return "Meeting Expectations";
  if (rpi >= 75) return "Catch Up Needed";
  return "Behind Schedule";
}

function getRPIEmoji(rpi: number): string {
  if (rpi >= 150) return "👑";
  if (rpi >= 125) return "🔥";
  if (rpi >= 100) return "✓";
  if (rpi >= 75) return "⚠️";
  return "❌";
}

function getXPProgress(level: number): number {
  const currentLevelXP = level * level * 100;
  const nextLevelXP = (level + 1) * (level + 1) * 100;
  const xpIntoLevel = 0; // TODO: Calculate from xp_ledger
  return Math.round((xpIntoLevel / (nextLevelXP - currentLevelXP)) * 100);
}

function getTotalXP(level: number): number {
  return level * level * 100;
}

function getNextLevelXP(level: number): number {
  return (level + 1) * (level + 1) * 100;
}

// Routes
app.get('/', (c) => {
  const today = new Date().toISOString().split('T')[0];
  const statsQuery = db.query(`
    SELECT 
      date, emails_sent, expected_emails, rpi, xp_earned, 
      xp_multiplier, level, streak_days,
      emails_new, emails_followup, emails_response
    FROM daily_stats 
    WHERE date = ?
  `);
  const stats = statsQuery.get(today) as any;
  
  if (!stats) {
    return c.html(`<!DOCTYPE html>
    <html>
    <head>
      <title>Arsenal Productivity</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {
          background: linear-gradient(135deg, #EF0107 0%, #8B0000 100%);
          color: white;
          font-family: 'Helvetica Neue', Arial, sans-serif;
          padding: 2rem;
          margin: 0;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .container {
          text-align: center;
          background: rgba(255,255,255,0.1);
          border-radius: 16px;
          padding: 3rem;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        button {
          background: white;
          color: #EF0107;
          border: none;
          padding: 1rem 2rem;
          border-radius: 8px;
          font-weight: bold;
          cursor: pointer;
          font-size: 1.1rem;
          margin-top: 1rem;
        }
        button:hover {
          background: #FFD700;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>⚽ Arsenal Productivity Tracker</h1>
        <p>No data for today yet. Run the scanner first!</p>
        <button onclick="fetch('/api/refresh', {method: 'POST'}).then(() => setTimeout(() => location.reload(), 2000))">
          🔄 Refresh Data
        </button>
      </div>
    </body>
    </html>`);
  }
  
  const xpProgress = getXPProgress(stats.level);
  const totalXP = getTotalXP(stats.level);
  const nextXP = getNextLevelXP(stats.level);
  
  return c.html(`<!DOCTYPE html>
  <html>
  <head>
    <title>Arsenal Productivity Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      * {
        box-sizing: border-box;
      }
      body {
        background: linear-gradient(135deg, #EF0107 0%, #8B0000 100%);
        color: white;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        padding: 1rem;
        margin: 0;
        min-height: 100vh;
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
      .header h1 {
        margin: 0.5rem 0;
        font-size: 1.8rem;
      }
      .header p {
        margin: 0.5rem 0;
        opacity: 0.9;
      }
      .player-card {
        background: white;
        color: #EF0107;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
      }
      .player-card h2 {
        margin: 0 0 1rem 0;
        font-size: 1.5rem;
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
      .xp-text {
        margin: 0.5rem 0 0 0;
        font-weight: bold;
      }
      .stat-box {
        background: rgba(255,255,255,0.15);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
      }
      .stat-box h3 {
        margin: 0 0 1rem 0;
        font-size: 1.3rem;
      }
      .stat-box h4 {
        margin: 1rem 0 0.5rem 0;
        font-size: 1.1rem;
      }
      .stat-box p {
        margin: 0.5rem 0;
      }
      .rpi-badge {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
      }
      .rpi-label {
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 0;
      }
      .button-group {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        justify-content: center;
        margin-top: 1.5rem;
      }
      button {
        background: white;
        color: #EF0107;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        flex: 1;
        min-width: 140px;
      }
      button:hover {
        background: #FFD700;
      }
      @media (max-width: 600px) {
        .container {
          padding: 1rem;
        }
        .header h1 {
          font-size: 1.5rem;
        }
        .rpi-badge {
          font-size: 2.5rem;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>⚽ ARSENAL PRODUCTIVITY</h1>
        <p>${new Date(stats.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>
      
      <div class="player-card">
        <h2>Level ${stats.level} - ${getRank(stats.level)}</h2>
        <div class="xp-bar">
          <div class="xp-fill" style="width: ${xpProgress}%"></div>
        </div>
        <p class="xp-text">XP: ${totalXP} / ${nextXP}</p>
      </div>
      
      <div class="stat-box">
        <h3>Today's Performance</h3>
        <div class="rpi-badge">${Math.round(stats.rpi)}% ${getRPIEmoji(stats.rpi)}</div>
        <p class="rpi-label">"${getRPILabel(stats.rpi)}"</p>
      </div>
      
      <div class="stat-box">
        <p><strong>Emails Sent:</strong> ${stats.emails_sent}</p>
        <p><strong>Expected:</strong> ${Math.round(stats.expected_emails)}</p>
        <p><strong>XP Earned:</strong> ${Math.round(stats.xp_earned)} (${stats.xp_multiplier.toFixed(2)}× multiplier)</p>
        <p><strong>Streak:</strong> ${stats.streak_days} days ${stats.streak_days >= 7 ? '🔥' : ''}</p>
      </div>
      
      <div class="stat-box">
        <h4>Breakdown</h4>
        <p>• ${stats.emails_new || 0} New emails (${(stats.emails_new || 0) * 10} XP)</p>
        <p>• ${stats.emails_followup || 0} Follow-ups (${(stats.emails_followup || 0) * 8} XP)</p>
        <p>• ${stats.emails_response || 0} Responses (${(stats.emails_response || 0) * 5} XP)</p>
      </div>
      
      <div class="button-group">
        <button onclick="refresh()">🔄 Refresh</button>
        <button onclick="location.href='/week'">📊 Week</button>
        <button onclick="location.href='/history'">📈 History</button>
      </div>
    </div>
    
    <script>
      function refresh() {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '⏳ Refreshing...';
        fetch('/api/refresh', {method: 'POST'})
          .then(() => setTimeout(() => location.reload(), 2000))
          .catch(() => {
            btn.disabled = false;
            btn.textContent = '🔄 Refresh';
          });
      }
      
      // Auto-refresh every 60 seconds
      setInterval(() => {
        fetch('/api/today')
          .then(r => r.json())
          .then(data => {
            if (data.emails_sent !== ${stats.emails_sent}) {
              location.reload();
            }
          });
      }, 60000);
    </script>
  </body>
  </html>`);
});

app.get('/week', (c) => {
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  const startDate = sevenDaysAgo.toISOString().split('T')[0];
  
  const query = db.query(`
    SELECT date, emails_sent, expected_emails, rpi, xp_earned, level
    FROM daily_stats 
    WHERE date >= ?
    ORDER BY date ASC
  `);
  const weekData = query.all(startDate) as any[];
  
  const rows = weekData.map(d => `
    <tr>
      <td>${new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</td>
      <td>${d.emails_sent}</td>
      <td>${Math.round(d.expected_emails)}</td>
      <td>${Math.round(d.rpi)}%</td>
      <td>${Math.round(d.xp_earned)}</td>
      <td>${d.level}</td>
    </tr>
  `).join('');
  
  return c.html(`<!DOCTYPE html>
  <html>
  <head>
    <title>Weekly Stats - Arsenal Productivity</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body {
        background: linear-gradient(135deg, #EF0107 0%, #8B0000 100%);
        color: white;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        padding: 1rem;
        margin: 0;
        min-height: 100vh;
      }
      .container {
        max-width: 800px;
        margin: 0 auto;
        background: rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      }
      h1 {
        text-align: center;
        margin-bottom: 2rem;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        overflow: hidden;
      }
      th, td {
        padding: 1rem;
        text-align: left;
      }
      th {
        background: rgba(255,255,255,0.2);
        font-weight: bold;
      }
      tr:nth-child(even) {
        background: rgba(255,255,255,0.05);
      }
      button {
        background: white;
        color: #EF0107;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        margin: 1rem auto;
        display: block;
      }
      button:hover {
        background: #FFD700;
      }
      @media (max-width: 600px) {
        th, td {
          padding: 0.5rem;
          font-size: 0.9rem;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>📊 Last 7 Days</h1>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Sent</th>
            <th>Expected</th>
            <th>RPI</th>
            <th>XP</th>
            <th>Level</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
      <button onclick="location.href='/'">← Back to Today</button>
    </div>
  </body>
  </html>`);
});

app.get('/history', (c) => {
  const erasQuery = db.query(`
    SELECT 
      era_name,
      start_date,
      end_date,
      avg_emails_per_day,
      avg_response_rate,
      total_days
    FROM eras
    ORDER BY start_date DESC
  `);
  const eras = erasQuery.all() as any[];
  
  const rows = eras.map(e => `
    <tr>
      <td>${e.era_name}</td>
      <td>${new Date(e.start_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</td>
      <td>${e.end_date ? new Date(e.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Current'}</td>
      <td>${e.avg_emails_per_day.toFixed(1)}</td>
      <td>${(e.avg_response_rate * 100).toFixed(1)}%</td>
      <td>${e.total_days}</td>
    </tr>
  `).join('');
  
  return c.html(`<!DOCTYPE html>
  <html>
  <head>
    <title>Era History - Arsenal Productivity</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body {
        background: linear-gradient(135deg, #EF0107 0%, #8B0000 100%);
        color: white;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        padding: 1rem;
        margin: 0;
        min-height: 100vh;
      }
      .container {
        max-width: 900px;
        margin: 0 auto;
        background: rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      }
      h1 {
        text-align: center;
        margin-bottom: 2rem;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        overflow: hidden;
      }
      th, td {
        padding: 1rem;
        text-align: left;
      }
      th {
        background: rgba(255,255,255,0.2);
        font-weight: bold;
      }
      tr:nth-child(even) {
        background: rgba(255,255,255,0.05);
      }
      button {
        background: white;
        color: #EF0107;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        margin: 1rem auto;
        display: block;
      }
      button:hover {
        background: #FFD700;
      }
      @media (max-width: 600px) {
        th, td {
          padding: 0.5rem;
          font-size: 0.85rem;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>📈 Era Comparison</h1>
      <table>
        <thead>
          <tr>
            <th>Era</th>
            <th>Start</th>
            <th>End</th>
            <th>Avg Emails/Day</th>
            <th>Response Rate</th>
            <th>Days</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
      <button onclick="location.href='/'">← Back to Today</button>
    </div>
  </body>
  </html>`);
});

// API Routes
app.get('/api/today', (c) => {
  const today = new Date().toISOString().split('T')[0];
  const query = db.query('SELECT * FROM daily_stats WHERE date = ?');
  const stats = query.get(today);
  return c.json(stats || {});
});

app.get('/api/week', (c) => {
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  const startDate = sevenDaysAgo.toISOString().split('T')[0];
  
  const query = db.query('SELECT * FROM daily_stats WHERE date >= ? ORDER BY date ASC');
  const weekData = query.all(startDate);
  return c.json(weekData);
});

app.post('/api/refresh', async (c) => {
  try {
    const proc = Bun.spawn(['python3', '/home/workspace/N5/scripts/productivity_scanner.py'], {
      cwd: '/home/workspace',
      stdout: 'pipe',
      stderr: 'pipe'
    });
    await proc.exited;
    
    return c.json({ status: 'success', message: 'Data refreshed' });
  } catch (error) {
    return c.json({ status: 'error', message: String(error) }, 500);
  }
});

const port = 3000;
console.log(`🚀 Arsenal Productivity Dashboard running on http://localhost:${port}`);

export default {
  port,
  fetch: app.fetch,
};
