import { Hono } from 'hono';
import Database from 'bun:sqlite';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

Date.prototype.getDayOfYear = function() {
  var start = new Date(this.getFullYear(), 0, 0);
  var diff = this - start;
  var oneDay = 1000 * 60 * 60 * 24;
  var day = Math.floor(diff / oneDay);
  return day;
};

const app = new Hono();
const db = new Database('/home/workspace/productivity_tracker.db');

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

function getStatusTier(rpi: number): { tier: string; emoji: string } {
  if (rpi >= 150) return { tier: "Legend", emoji: "👑" };
  if (rpi >= 125) return { tier: "First Team Player", emoji: "⭐" };
  if (rpi >= 100) return { tier: "Bench Player", emoji: "🔶" };
  if (rpi >= 75) return { tier: "Reserve Player", emoji: "⚠️" };
  return { tier: "Free Agent", emoji: "❌" };
}

function getRPIColor(rpi: number): string {
  if (rpi >= 125) {
    // Gold gradient for 125+
    const intensity = Math.min((rpi - 125) / 25, 1);
    return `rgba(255, ${215 - intensity * 20}, 0, 0.9)`;
  } else if (rpi >= 100) {
    // Green gradient for 100-124
    const intensity = (rpi - 100) / 24;
    return `rgba(${76 - intensity * 26}, ${175 + intensity * 40}, ${80 - intensity * 30}, 0.85)`;
  } else {
    // Red/Orange gradient for <100
    const intensity = Math.min(rpi / 100, 1);
    return `rgba(${200 + intensity * 55}, ${50 + intensity * 50}, ${46 - intensity * 16}, 0.8)`;
  }
}

app.get('/', (c) => {
  const today = new Date().toISOString().split('T')[0];
  
  const days = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    days.push({
      date: dateStr,
      dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
      shortDate: dateStr.substring(5),
      isToday: dateStr === today,
      matchDay: date.getDayOfYear()
    });
  }
  
  const stats = db.prepare(`
    SELECT date, emails_sent, expected_emails, rpi 
    FROM daily_stats 
    WHERE date IN (${days.map(() => '?').join(',')})
    ORDER BY date
  `).all(...days.map(d => d.date));
  
  const statsMap = new Map(stats.map((s: any) => [s.date, s]));
  
  const enrichedDays = days.map(day => {
    const stat = statsMap.get(day.date);
    return {
      ...day,
      emails_sent: stat?.emails_sent || 0,
      expected_emails: stat?.expected_emails || 0,
      rpi: stat?.rpi || 0
    };
  });

  const todayStats = statsMap.get(today) || { emails_sent: 0, expected_emails: 0, rpi: 0 };
  const weekTotal = enrichedDays.reduce((sum, d) => sum + (d.emails_sent || 0), 0);

  return c.html(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>V's Productivity Dashboard</title>
  <link rel="icon" type="image/jpeg" href="https://i.pinimg.com/736x/2d/4e/5d/2d4e5dac8067453da03517ea22ae92dd.jpg">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #C8102E;
      color: #fff;
      padding: 20px;
      min-height: 100vh;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    .header {
      text-align: center;
      margin-bottom: 40px;
      padding: 20px;
      background: transparent;
      border-radius: 12px;
    }
    .header h1 {
      font-size: 2.5rem;
      margin-bottom: 8px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .header p { font-size: 1.1rem; opacity: 0.9; }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .stat-card {
      background: rgba(255,255,255,0.15);
      backdrop-filter: blur(10px);
      padding: 24px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.2);
    }
    .stat-card h3 {
      font-size: 0.9rem;
      opacity: 0.8;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .stat-card .value {
      font-size: 2.5rem;
      font-weight: bold;
      margin-bottom: 4px;
    }
    .stat-card .label {
      font-size: 1rem;
      opacity: 0.9;
    }
    .status-badge {
      display: inline-block;
      background: rgba(255,255,255,0.2);
      backdrop-filter: blur(10px);
      padding: 16px 32px;
      border-radius: 50px;
      border: 2px solid rgba(255,255,255,0.3);
      font-size: 1.2rem;
      font-weight: bold;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .status-emoji {
      font-size: 1.5rem;
      margin-right: 10px;
    }
    .status-text {
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .week-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 12px;
      margin-bottom: 30px;
    }
    .day-card {
      background: rgba(255,255,255,0.1);
      padding: 16px;
      border-radius: 8px;
      text-align: center;
      border: 2px solid transparent;
      transition: all 0.2s;
    }
    .day-card.today {
      background: rgba(255,255,255,0.25);
      border-color: #FFD700;
      box-shadow: 0 0 20px rgba(255,215,0,0.3);
    }
    .day-card .day-name {
      font-size: 0.85rem;
      opacity: 0.8;
      margin-bottom: 4px;
    }
    .day-card .day-date {
      font-size: 0.75rem;
      opacity: 0.6;
      margin-bottom: 8px;
    }
    .day-card .emails {
      font-size: 1.8rem;
      font-weight: bold;
      margin: 8px 0;
    }
    .day-card .rpi {
      font-size: 1rem;
      opacity: 0.9;
    }
    .refresh-section {
      background: rgba(255,255,255,0.1);
      padding: 20px;
      border-radius: 12px;
      text-align: center;
      margin-top: 30px;
    }
    .refresh-btn {
      background: #FFD700;
      color: #8B0000;
      border: none;
      padding: 12px 32px;
      font-size: 1rem;
      font-weight: bold;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
    }
    .refresh-btn:hover {
      background: #FFC700;
      transform: scale(1.05);
    }
    .refresh-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .status {
      margin-top: 12px;
      font-size: 0.9rem;
      min-height: 24px;
    }
    @media (max-width: 768px) {
      .week-grid { grid-template-columns: repeat(4, 1fr); }
      .header h1 { font-size: 2rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <img src="https://i.pinimg.com/736x/2d/4e/5d/2d4e5dac8067453da03517ea22ae92dd.jpg" alt="Arsenal" style="width: 120px; height: auto; margin-bottom: 16px; border-radius: 8px;">
      <h1>V's Productivity Dashboard</h1>
      <p>Victoria Per Velocitatem Epistularum</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>Today's Emails 📧</h3>
        <div class="value">${todayStats.emails_sent}</div>
        <div class="label">sent</div>
      </div>
      <div class="stat-card">
        <h3>Today's RPI</h3>
        <div class="value">${getRPIEmoji(todayStats.rpi)} ${todayStats.rpi.toFixed(1)}%</div>
        <div class="label">${getRPILabel(todayStats.rpi)}</div>
      </div>
      <div class="stat-card">
        <h3>Week Total 📧</h3>
        <div class="value">${weekTotal}</div>
        <div class="label">emails this week</div>
      </div>
    </div>

    <div style="text-align: center; margin-bottom: 30px;">
      <div class="status-badge">
        <span class="status-emoji">${getStatusTier(todayStats.rpi).emoji}</span>
        <span class="status-text">${getStatusTier(todayStats.rpi).tier}</span>
      </div>
    </div>

    <div class="week-grid">
      ${enrichedDays.map(day => `
        <div class="day-card${day.isToday ? ' today' : ''}" style="background: ${getRPIColor(day.rpi)};">
          <div class="day-name">${day.dayName}</div>
          <div class="day-date">${day.shortDate}</div>
          <div class="emails">${day.emails_sent}</div>
          <div class="rpi">${day.rpi.toFixed(0)}% RPI</div>
        </div>
      `).join('')}
    </div>

    <div class="refresh-section">
      <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
      <div class="status" id="status"></div>
    </div>
  </div>

  <script>
    async function refreshData() {
      const btn = document.querySelector('.refresh-btn');
      const status = document.getElementById('status');
      
      btn.disabled = true;
      status.textContent = '⏳ Fetching Gmail data...';
      
      try {
        const response = await fetch('/api/refresh', { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
          status.textContent = '✅ ' + data.message;
          setTimeout(() => window.location.reload(), 1500);
        } else {
          status.textContent = '❌ ' + (data.error || 'Refresh failed');
        }
      } catch (error) {
        status.textContent = '❌ Network error';
      } finally {
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>`);
});

app.post('/api/refresh', async (c) => {
  try {
    const { stdout, stderr } = await execAsync('python3 /home/workspace/Sites/productivity-dashboard/sync_gmail.py');
    return c.json({ 
      success: true, 
      message: 'Data refreshed successfully',
      details: stdout
    });
  } catch (error: any) {
    console.error('Refresh error:', error);
    return c.json({ 
      success: false, 
      error: error.message,
      stderr: error.stderr
    }, 500);
  }
});

export default {
  port: 3001,
  fetch: app.fetch,
};

console.log('🚀 Arsenal Productivity Dashboard running on http://localhost:3001');
