import { Hono } from 'hono'
import { readFile, appendFile } from 'fs/promises'

const app = new Hono()

// Configuration
const TMDB_API_KEY = '01e0655ebb4895d40e2f076e39e75780'
const USAGE_LOG_FILE = '/home/workspace/streaming-player-setup/usage.log'
const RATE_LIMIT_WINDOW = 60000 // 1 minute
const MAX_REQUESTS_PER_WINDOW = 50 // 50 requests per minute per IP (generous but prevents abuse)
const ABUSE_THRESHOLD_DAILY = 500 // Flag IPs making more than 500 requests per day

// In-memory rate limiting and abuse tracking
const rateLimitStore: Map<string, { count: number; resetTime: number }> = new Map()
const dailyUsageStore: Map<string, { count: number; date: string }> = new Map()

// Middleware: Rate limiting with abuse detection
const rateLimitMiddleware = async (c: any, next: any) => {
  const ip = c.req.header('cf-connecting-ip') || c.req.header('x-forwarded-for') || 'unknown'
  const now = Date.now()
  const today = new Date().toISOString().split('T')[0]
  
  // Per-minute rate limiting
  let limitData = rateLimitStore.get(ip)
  
  if (!limitData || now > limitData.resetTime) {
    limitData = { count: 0, resetTime: now + RATE_LIMIT_WINDOW }
    rateLimitStore.set(ip, limitData)
  }
  
  limitData.count++
  
  if (limitData.count > MAX_REQUESTS_PER_WINDOW) {
    await logUsage(c, 'rate_limited', { ip, reason: 'exceeded_per_minute_limit' })
    return c.json({ error: 'Too many requests. Please slow down and try again in a minute.' }, 429)
  }
  
  // Daily abuse tracking
  let dailyData = dailyUsageStore.get(ip)
  
  if (!dailyData || dailyData.date !== today) {
    dailyData = { count: 0, date: today }
    dailyUsageStore.set(ip, dailyData)
  }
  
  dailyData.count++
  
  if (dailyData.count > ABUSE_THRESHOLD_DAILY) {
    await logUsage(c, 'abuse_detected', { ip, daily_count: dailyData.count })
  }
  
  await next()
}

// Middleware: Usage logging
const logUsage = async (c: any, action: string, details: any = {}) => {
  const ip = c.req.header('cf-connecting-ip') || c.req.header('x-forwarded-for') || 'unknown'
  const timestamp = new Date().toISOString()
  const logEntry = JSON.stringify({
    timestamp,
    ip,
    action,
    details,
    userAgent: c.req.header('user-agent') || 'unknown'
  })
  
  try {
    await appendFile(USAGE_LOG_FILE, logEntry + '\n')
  } catch (error) {
    console.error('Failed to log usage:', error)
  }
}

// API endpoint to search TMDB
app.get('/api/search', rateLimitMiddleware, async (c) => {
  const query = c.req.query('q')
  const type = c.req.query('type') || 'movie'
  
  if (!query) {
    return c.json({ error: 'Query parameter required' }, 400)
  }

  await logUsage(c, 'search', { query, type })

  try {
    const url = `https://api.themoviedb.org/3/search/${type}?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(query)}&language=en-US&page=1`
    const response = await fetch(url)
    const data = await response.json()
    return c.json(data)
  } catch (error) {
    return c.json({ error: 'Search failed' }, 500)
  }
})

// API endpoint to get TV show seasons
app.get('/api/tv/:id/seasons', rateLimitMiddleware, async (c) => {
  const id = c.req.param('id')
  
  await logUsage(c, 'fetch_seasons', { tvId: id })

  try {
    const url = `https://api.themoviedb.org/3/tv/${id}?api_key=${TMDB_API_KEY}&language=en-US`
    const response = await fetch(url)
    const data = await response.json()
    return c.json(data)
  } catch (error) {
    return c.json({ error: 'Failed to fetch seasons' }, 500)
  }
})

// Visual stats dashboard
app.get('/stats', async (c) => {
  try {
    const logs = await readFile(USAGE_LOG_FILE, 'utf-8')
    const lines = logs.split('\n').filter(line => line.trim())
    const entries = lines.map(line => JSON.parse(line))
    
    const today = new Date().toISOString().split('T')[0]
    const todayEntries = entries.filter(e => e.timestamp.startsWith(today))
    
    const ipCounts: any = {}
    todayEntries.forEach(entry => {
      ipCounts[entry.ip] = (ipCounts[entry.ip] || 0) + 1
    })
    
    const abusiveIPs = Object.entries(ipCounts)
      .filter(([ip, count]) => (count as number) > ABUSE_THRESHOLD_DAILY)
      .map(([ip, count]) => ({ ip, count }))
    
    const actionCounts = entries.reduce((acc: any, entry) => {
      acc[entry.action] = (acc[entry.action] || 0) + 1
      return acc
    }, {})
    
    return c.html(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zo Stream - Usage Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 40px 20px;
      color: #ffffff;
    }
    
    .container { max-width: 1400px; margin: 0 auto; }
    
    .header {
      text-align: center;
      margin-bottom: 40px;
    }
    
    .header h1 {
      font-size: 42px;
      font-weight: 700;
      margin-bottom: 10px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header .subtitle {
      font-size: 16px;
      opacity: 0.9;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .stat-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 12px;
      padding: 25px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
      color: #37352f;
    }
    
    .stat-card .label {
      font-size: 14px;
      font-weight: 600;
      color: #6b6b6b;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .stat-card .value {
      font-size: 48px;
      font-weight: 700;
      color: #667eea;
      line-height: 1;
    }
    
    .stat-card.warning .value { color: #ffa726; }
    .stat-card.danger .value { color: #ef5350; }
    .stat-card.success .value { color: #66bb6a; }
    
    .section {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 12px;
      padding: 30px;
      margin-bottom: 20px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
      color: #37352f;
    }
    
    .section h2 {
      font-size: 24px;
      margin-bottom: 20px;
      color: #37352f;
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
    }
    
    th, td {
      text-align: left;
      padding: 12px 16px;
      border-bottom: 1px solid #e0e0e0;
    }
    
    th {
      background: #f5f5f5;
      font-weight: 600;
      font-size: 14px;
      color: #37352f;
    }
    
    tr:hover {
      background: #fafafa;
    }
    
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
    }
    
    .badge.danger { background: #ffebee; color: #c62828; }
    .badge.warning { background: #fff3e0; color: #e65100; }
    .badge.success { background: #e8f5e9; color: #2e7d32; }
    
    .back-link {
      display: inline-block;
      margin-bottom: 20px;
      padding: 10px 20px;
      background: rgba(255,255,255,0.2);
      color: white;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 600;
      transition: background 0.3s;
    }
    
    .back-link:hover {
      background: rgba(255,255,255,0.3);
    }
    
    .refresh-btn {
      float: right;
      padding: 10px 20px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
    }
    
    .refresh-btn:hover { background: #5568d3; }
  </style>
</head>
<body>
  <div class="container">
    <a href="/" class="back-link">← Back to Player</a>
    
    <div class="header">
      <h1>📊 Usage Dashboard</h1>
      <p class="subtitle">Real-time analytics and abuse monitoring</p>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="label">Total Requests</div>
        <div class="value">${entries.length}</div>
      </div>
      
      <div class="stat-card success">
        <div class="label">Today's Requests</div>
        <div class="value">${todayEntries.length}</div>
      </div>
      
      <div class="stat-card">
        <div class="label">Unique Users (All Time)</div>
        <div class="value">${new Set(entries.map(e => e.ip)).size}</div>
      </div>
      
      <div class="stat-card success">
        <div class="label">Unique Users (Today)</div>
        <div class="value">${new Set(todayEntries.map(e => e.ip)).size}</div>
      </div>
      
      <div class="stat-card ${abusiveIPs.length > 0 ? 'danger' : 'success'}">
        <div class="label">Abusive IPs Detected</div>
        <div class="value">${abusiveIPs.length}</div>
      </div>
    </div>
    
    ${abusiveIPs.length > 0 ? `
    <div class="section">
      <h2>⚠️ Flagged IPs (>500 requests/day)</h2>
      <table>
        <thead>
          <tr>
            <th>IP Address</th>
            <th>Request Count Today</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${abusiveIPs.map(({ ip, count }) => `
          <tr>
            <td>${ip}</td>
            <td>${count}</td>
            <td><span class="badge danger">ABUSE DETECTED</span></td>
          </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    ` : ''}
    
    <div class="section">
      <h2>📈 Action Breakdown</h2>
      <table>
        <thead>
          <tr>
            <th>Action Type</th>
            <th>Count</th>
            <th>Percentage</th>
          </tr>
        </thead>
        <tbody>
          ${Object.entries(actionCounts).map(([action, count]) => {
            const percentage = ((count as number) / entries.length * 100).toFixed(1)
            return `
          <tr>
            <td><strong>${action}</strong></td>
            <td>${count}</td>
            <td>${percentage}%</td>
          </tr>
            `
          }).join('')}
        </tbody>
      </table>
    </div>
    
    <div class="section">
      <h2>🕐 Recent Activity <button class="refresh-btn" onclick="location.reload()">Refresh</button></h2>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>IP</th>
            <th>Action</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          ${entries.slice(-30).reverse().map(entry => {
            const time = new Date(entry.timestamp).toLocaleString()
            const details = entry.details.query || entry.details.tvId || '-'
            return `
          <tr>
            <td>${time}</td>
            <td>${entry.ip}</td>
            <td><span class="badge ${entry.action.includes('abuse') || entry.action.includes('rate_limited') ? 'danger' : 'success'}">${entry.action}</span></td>
            <td>${details}</td>
          </tr>
            `
          }).join('')}
        </tbody>
      </table>
    </div>
  </div>
  
  <script>
    // Auto-refresh every 30 seconds
    setTimeout(() => location.reload(), 30000);
  </script>
</body>
</html>
    `)
  } catch (error) {
    return c.html('<html><body><h1>No stats available yet</h1><p>Start using the app to generate stats!</p></body></html>')
  }
})

// Usage stats endpoint
app.get('/api/stats', async (c) => {
  try {
    const logs = await readFile(USAGE_LOG_FILE, 'utf-8')
    const lines = logs.split('\n').filter(line => line.trim())
    const entries = lines.map(line => JSON.parse(line))
    
    const today = new Date().toISOString().split('T')[0]
    const todayEntries = entries.filter(e => e.timestamp.startsWith(today))
    
    // Find abusive IPs
    const ipCounts: any = {}
    todayEntries.forEach(entry => {
      ipCounts[entry.ip] = (ipCounts[entry.ip] || 0) + 1
    })
    
    const abusiveIPs = Object.entries(ipCounts)
      .filter(([ip, count]) => (count as number) > ABUSE_THRESHOLD_DAILY)
      .map(([ip, count]) => ({ ip, count }))
    
    const stats = {
      totalRequests: entries.length,
      todayRequests: todayEntries.length,
      uniqueIPs: new Set(entries.map(e => e.ip)).size,
      uniqueIPsToday: new Set(todayEntries.map(e => e.ip)).size,
      abusiveIPs: abusiveIPs,
      actionBreakdown: entries.reduce((acc: any, entry) => {
        acc[entry.action] = (acc[entry.action] || 0) + 1
        return acc
      }, {}),
      recentActivity: entries.slice(-30).reverse()
    }
    
    return c.json(stats)
  } catch (error) {
    return c.json({ error: 'Stats not available', totalRequests: 0 }, 200)
  }
})

// Main app page
app.get('/', async (c) => {
  await logUsage(c, 'page_view', {})
  
  return c.html(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zo Stream - Interactive Player</title>
  
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
      color: #ffffff;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
    }

    .header {
      text-align: center;
      margin-bottom: 40px;
      padding: 20px;
    }

    .header h1 {
      font-size: 48px;
      font-weight: 700;
      margin-bottom: 10px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    .header p {
      font-size: 18px;
      opacity: 0.9;
    }

    .search-section {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16px;
      padding: 30px;
      margin-bottom: 30px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
      color: #37352f;
    }

    .search-box {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }

    .search-box input {
      flex: 1;
      padding: 14px 20px;
      font-size: 16px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      outline: none;
      transition: border-color 0.3s;
    }

    .search-box input:focus {
      border-color: #667eea;
    }

    .type-toggle {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }

    .type-toggle button {
      flex: 1;
      padding: 12px;
      border: 2px solid #e0e0e0;
      background: white;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;
    }

    .type-toggle button.active {
      background: #667eea;
      color: white;
      border-color: #667eea;
    }

    .search-button {
      padding: 14px 40px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.3s;
    }

    .search-button:hover {
      background: #5568d3;
    }

    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }

    .result-card {
      background: white;
      border-radius: 12px;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.3s, box-shadow 0.3s;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .result-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }

    .result-card img {
      width: 100%;
      height: 300px;
      object-fit: cover;
    }

    .result-card .info {
      padding: 15px;
    }

    .result-card .title {
      font-weight: 600;
      font-size: 16px;
      margin-bottom: 5px;
      color: #37352f;
    }

    .result-card .year {
      font-size: 14px;
      color: #6b6b6b;
    }

    .player-section {
      background: rgba(0, 0, 0, 0.9);
      border-radius: 16px;
      padding: 30px;
      margin-bottom: 30px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
      display: none;
    }

    .player-section.active {
      display: block;
    }

    .player-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .player-title {
      font-size: 24px;
      font-weight: 600;
    }

    .close-player {
      padding: 10px 20px;
      background: #eb5757;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
    }

    .player-controls {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 20px;
    }

    .control-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .control-group label {
      font-size: 14px;
      font-weight: 600;
      color: #ccc;
    }

    .control-group select {
      padding: 10px;
      border: 2px solid #444;
      background: #222;
      color: white;
      border-radius: 6px;
      font-size: 14px;
    }

    .play-button {
      grid-column: 1 / -1;
      padding: 16px;
      background: #36b37e;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 18px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.3s;
    }

    .play-button:hover {
      background: #2a9566;
    }

    .video-container {
      width: 100%;
      max-width: 100%;
      margin: 0 auto;
      border-radius: 12px;
      overflow: hidden;
      background: #000;
    }

    .loading {
      text-align: center;
      padding: 20px;
      color: #667eea;
      font-weight: 600;
    }

    .error {
      background: #ffebee;
      color: #c62828;
      padding: 15px;
      border-radius: 8px;
      margin-top: 15px;
    }

    .no-results {
      text-align: center;
      padding: 40px;
      color: #6b6b6b;
      font-size: 18px;
    }

    @media (max-width: 768px) {
      .header h1 {
        font-size: 32px;
      }
      
      .results-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 15px;
      }

      .player-controls {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🎬 Zo Stream</h1>
      <p>Search and stream your favorite movies & TV shows instantly</p>
    </div>

    <div class="search-section">
      <h2 style="margin-bottom: 20px; color: #37352f;">Search Content</h2>
      
      <div class="type-toggle">
        <button id="movieBtn" class="active" onclick="setSearchType('movie')">🎥 Movies</button>
        <button id="tvBtn" onclick="setSearchType('tv')">📺 TV Shows</button>
      </div>

      <div class="search-box">
        <input 
          type="text" 
          id="searchInput" 
          placeholder="Enter movie or TV show name..."
          onkeypress="handleSearchKeypress(event)"
        />
        <button class="search-button" onclick="searchContent()">Search</button>
      </div>

      <div id="searchResults"></div>
    </div>

    <div class="player-section" id="playerSection">
      <div class="player-header">
        <h2 class="player-title" id="playerTitle">Now Playing</h2>
        <button class="close-player" onclick="closePlayer()">✕ Close</button>
      </div>

      <div class="player-controls" id="playerControls"></div>

      <div class="video-container" id="videoContainer">
        <iframe 
          id="playerFrame"
          style="width: 100%; height: 600px; border: none; border-radius: 12px;"
          allowfullscreen
          allow="autoplay; fullscreen; picture-in-picture"
        ></iframe>
      </div>
    </div>
  </div>

  <script>
    let currentType = 'movie';
    let selectedContent = null;
    let currentSeasons = [];

    function setSearchType(type) {
      currentType = type;
      document.getElementById('movieBtn').classList.toggle('active', type === 'movie');
      document.getElementById('tvBtn').classList.toggle('active', type === 'tv');
    }

    function handleSearchKeypress(event) {
      if (event.key === 'Enter') {
        searchContent();
      }
    }

    async function searchContent() {
      const query = document.getElementById('searchInput').value.trim();
      if (!query) return;

      const resultsDiv = document.getElementById('searchResults');
      resultsDiv.innerHTML = '<div class="loading">Searching...</div>';

      try {
        const response = await fetch(\`/api/search?q=\${encodeURIComponent(query)}&type=\${currentType}\`);
        const data = await response.json();

        if (data.error) {
          resultsDiv.innerHTML = \`<div class="error">\${data.error}</div>\`;
          return;
        }

        if (!data.results || data.results.length === 0) {
          resultsDiv.innerHTML = '<div class="no-results">No results found. Try a different search.</div>';
          return;
        }

        displayResults(data.results);
      } catch (error) {
        resultsDiv.innerHTML = '<div class="error">Search failed. Please try again.</div>';
      }
    }

    function displayResults(results) {
      const resultsDiv = document.getElementById('searchResults');
      
      const html = \`
        <div class="results-grid">
          \${results.map(item => \`
            <div class="result-card" onclick='selectContent(\${JSON.stringify(item).replace(/'/g, "&#39;")})'>
              <img 
                src="\${item.poster_path ? 'https://image.tmdb.org/t/p/w500' + item.poster_path : 'https://via.placeholder.com/200x300?text=No+Image'}" 
                alt="\${item.title || item.name}"
              />
              <div class="info">
                <div class="title">\${item.title || item.name}</div>
                <div class="year">\${(item.release_date || item.first_air_date || '').split('-')[0]}</div>
              </div>
            </div>
          \`).join('')}
        </div>
      \`;
      
      resultsDiv.innerHTML = html;
    }

    async function selectContent(content) {
      selectedContent = content;
      const playerSection = document.getElementById('playerSection');
      const playerTitle = document.getElementById('playerTitle');
      const playerControls = document.getElementById('playerControls');
      
      playerTitle.textContent = content.title || content.name;
      playerSection.classList.add('active');
      
      playerSection.scrollIntoView({ behavior: 'smooth' });

      if (currentType === 'movie') {
        playerControls.innerHTML = \`
          <div class="control-group">
            <label>Subtitle Language</label>
            <select id="subtitleLang">
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="pt">Portuguese</option>
              <option value="ja">Japanese</option>
              <option value="ko">Korean</option>
              <option value="zh">Chinese</option>
            </select>
          </div>
          <button class="play-button" onclick="playMovie()">▶ Play Movie</button>
        \`;
      } else {
        try {
          const response = await fetch(\`/api/tv/\${content.id}/seasons\`);
          const data = await response.json();
          
          if (data.error) {
            playerControls.innerHTML = \`<div class="error">\${data.error}</div>\`;
            return;
          }
          
          currentSeasons = data.seasons || [];
          
          playerControls.innerHTML = \`
            <div class="control-group">
              <label>Season</label>
              <select id="seasonSelect" onchange="updateEpisodes()">
                \${currentSeasons.map(season => \`
                  <option value="\${season.season_number}">\${season.name}</option>
                \`).join('')}
              </select>
            </div>
            <div class="control-group">
              <label>Episode</label>
              <select id="episodeSelect">
                <option value="1">Episode 1</option>
              </select>
            </div>
            <div class="control-group">
              <label>Subtitle Language</label>
              <select id="subtitleLang">
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
              </select>
            </div>
            <button class="play-button" onclick="playTVShow()">▶ Play Episode</button>
          \`;
          
          updateEpisodes();
        } catch (error) {
          playerControls.innerHTML = '<div class="error">Failed to load TV show details. Please try again.</div>';
        }
      }
    }

    function updateEpisodes() {
      const seasonSelect = document.getElementById('seasonSelect');
      const episodeSelect = document.getElementById('episodeSelect');
      const seasonNum = parseInt(seasonSelect.value);
      
      const season = currentSeasons.find(s => s.season_number === seasonNum);
      if (season) {
        const episodeCount = season.episode_count || 10;
        episodeSelect.innerHTML = Array.from({ length: episodeCount }, (_, i) => 
          \`<option value="\${i + 1}">Episode \${i + 1}</option>\`
        ).join('');
      }
    }

    function playMovie() {
      if (!selectedContent) return;
      
      const subtitleLang = document.getElementById('subtitleLang').value;
      const streamUrl = \`https://zo-stream-va.zocomputer.io/movie/\${selectedContent.id}?subtitle=\${subtitleLang}\`;
      
      loadPlayer(streamUrl);
    }

    function playTVShow() {
      if (!selectedContent) return;
      
      const season = document.getElementById('seasonSelect').value;
      const episode = document.getElementById('episodeSelect').value;
      const subtitleLang = document.getElementById('subtitleLang').value;
      const streamUrl = \`https://zo-stream-va.zocomputer.io/tv/\${selectedContent.id}/\${season}/\${episode}?subtitle=\${subtitleLang}\`;
      
      loadPlayer(streamUrl);
    }

    function loadPlayer(url) {
      const playerFrame = document.getElementById('playerFrame');
      playerFrame.src = url;
    }

    function closePlayer() {
      const playerSection = document.getElementById('playerSection');
      playerSection.classList.remove('active');
      const playerFrame = document.getElementById('playerFrame');
      playerFrame.src = '';
    }

    window.onload = () => {
      document.getElementById('searchInput').focus();
    };
  </script>
</body>
</html>
  `)
})

// Bun server export
export default {
  port: parseInt(process.env.PORT || '50650'),
  fetch: app.fetch,
}
