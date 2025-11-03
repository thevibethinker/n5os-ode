import { Hono } from 'hono';
import Database from 'bun:sqlite';

const app = new Hono();
const db = new Database('/home/workspace/productivity_tracker.db');

app.get('/', (c) => {
  const today = new Date().toISOString().split('T')[0];
  const statsQuery = db.query('SELECT * FROM daily_stats WHERE date = ?');
  const stats = statsQuery.get(today) as any;
  
  const teamQuery = db.query('SELECT * FROM team_status_history WHERE date = ? ORDER BY date DESC LIMIT 1');
  const teamStatus = teamQuery.get(today) as any;
  
  if (!stats) {
    return c.html(`<html>
    <head><title>Arsenal Productivity</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body { background: linear-gradient(135deg, #EF0107 0%, #8B0000 100%); color: white; font-family: Arial, sans-serif; padding: 2rem; text-align: center; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
      .container { background: rgba(255,255,255,0.1); border-radius: 16px; padding: 3rem; }
    </style>
    </head>
    <body><div class="container"><h1>⚽ Arsenal Productivity</h1><p>No data for today yet.</p></div></body>
    </html>`);
  }
  
  const rpiLabel = stats.rpi >= 10 ? "On Target" : "Needs Work";
  const rpiEmoji = stats.rpi >= 10 ? "✓" : "⚠️";
  
  const teamStatusBanner = teamStatus ? `
    <div class="team-banner">
      <div class="team-label">CAREER STATUS</div>
      <div class="team-value">${teamStatus.status.toUpperCase().replace('_', ' ')}</div>
      <div class="team-details">
        ${teamStatus.days_in_status} day${teamStatus.days_in_status !== 1 ? 's' : ''} at this level • 
        RPI: ${teamStatus.top5_avg.toFixed(2)}
      </div>
    </div>
  ` : '';
  
  return c.html(`<html>
  <head><title>Arsenal Productivity</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { background: linear-gradient(135deg, #EF0107 0%, #8B0000 100%); color: white; font-family: Arial, sans-serif; padding: 1rem; min-height: 100vh; }
    .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); border-radius: 16px; padding: 2rem; }
    .team-banner { background: linear-gradient(90deg, rgba(255,215,0,0.2) 0%, rgba(255,215,0,0.1) 100%); border-left: 4px solid #FFD700; padding: 1rem; margin-bottom: 1.5rem; border-radius: 8px; }
    .team-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-bottom: 0.25rem; }
    .team-value { font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; }
    .team-details { font-size: 0.85rem; opacity: 0.9; }
    .stat-card { background: rgba(255,255,255,0.15); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }
    .stat-value { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem; }
    .mini-stat { background: rgba(255,255,255,0.1); border-radius: 8px; padding: 1rem; text-align: center; }
    .mini-stat-value { font-size: 1.5rem; font-weight: bold; }
  </style>
  </head>
  <body>
    <div class="container">
      <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem;">⚽</div>
        <h1>Arsenal Productivity</h1>
        <div>${stats.date}</div>
      </div>
      ${teamStatusBanner}
      <div class="stat-card">
        <div>Response Productivity Index</div>
        <div class="stat-value">${rpiEmoji} ${stats.rpi.toFixed(2)}</div>
        <div>${rpiLabel}</div>
      </div>
      <div class="grid">
        <div class="mini-stat">
          <div class="mini-stat-value">${stats.email_count}</div>
          <div>📧 Emails</div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-value">${stats.total_words}</div>
          <div>📝 Words</div>
        </div>
      </div>
    </div>
  </body>
  </html>`);
});

app.get('/api/today', (c) => {
  const today = new Date().toISOString().split('T')[0];
  const query = db.query('SELECT * FROM daily_stats WHERE date = ?');
  const stats = query.get(today);
  return c.json(stats || {});
});

app.get('/api/status', (c) => {
  const today = new Date().toISOString().split('T')[0];
  const query = db.query('SELECT * FROM team_status_history WHERE date = ? ORDER BY date DESC LIMIT 1');
  const status = query.get(today);
  return c.json(status || {});
});

app.get('/api/career', (c) => {
  const query = db.query('SELECT * FROM career_stats ORDER BY id DESC LIMIT 1');
  const stats = query.get();
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
    // Accept email data from request body
    const body = await c.req.json();
    const emails = body.emails || [];
    
    if (emails.length === 0) {
      return c.json({ success: false, error: 'No emails provided' }, 400);
    }
    
    const today = new Date().toISOString().split('T')[0];
    
    // Count words excluding quoted replies and signatures
    function countWords(text: string): number {
      if (!text) return 0;
      
      const lines = text.split('\n');
      const originalLines: string[] = [];
      
      for (const line of lines) {
        // Skip quoted lines
        if (line.trim().startsWith('>')) continue;
        
        // Stop at reply markers
        if (line.includes('On ') || line.includes(' wrote:') ||
            line.includes('From:') || line.includes('Sent:') ||
            line.includes('To:') || line.includes('Subject:')) {
          break;
        }
        
        // Stop at signature
        if (line.includes('V-OS Tags:') || line.includes('{TWIN}') ||
            line.includes('{CATG}') || line.includes('Best,') ||
            line.includes('Sent via Superhuman') || line.includes('---')) {
          break;
        }
        
        originalLines.push(line);
      }
      
      return originalLines.join(' ').split(/\s+/).filter(w => w.length > 0).length;
    }
    
    // Calculate metrics
    let totalWords = 0;
    const emailDetails: any[] = [];
    
    for (const email of emails) {
      const words = countWords(email.payload || '');
      totalWords += words;
      emailDetails.push({
        subject: email.subject || 'No subject',
        words
      });
    }
    
    const rpi = emails.length + (totalWords / 100);
    
    // Update database
    const insertQuery = db.prepare(`
      INSERT OR REPLACE INTO daily_stats (date, email_count, total_words, rpi)
      VALUES (?, ?, ?, ?)
    `);
    insertQuery.run(today, emails.length, totalWords, rpi);
    
    return c.json({
      success: true,
      message: 'Dashboard updated',
      stats: {
        date: today,
        emails: emails.length,
        words: totalWords,
        rpi: rpi.toFixed(2)
      },
      details: emailDetails
    });
    
  } catch (error: any) {
    return c.json({ success: false, error: error.message }, 500);
  }
});

const port = 3000;
console.log(`🚀 Arsenal Productivity Dashboard running on http://localhost:${port}`);

export default {
  port,
  fetch: app.fetch,
};
