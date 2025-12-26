import { Hono } from 'hono'
import { serveStatic } from 'hono/bun'

const app = new Hono()

const TravelDashboard = ({ metrics }) => (
  <div style={{ fontFamily: 'sans-serif', padding: '2rem', background: '#f0f4f8', minHeight: '100vh' }}>
    <h1 style={{ color: '#1a365d' }}>🌍 2025 Travel Wrapped</h1>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
      <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3>✈️ Flights</h3>
        <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.summary.total_flights}</p>
      </div>
      <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3>🏨 Nights Away</h3>
        <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{metrics.summary.total_nights}</p>
      </div>
      <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3>🏙️ Top City</h3>
        <p style={{ fontSize: '1.5rem' }}>{metrics.summary.top_city}</p>
      </div>
    </div>
    <div style={{ marginTop: '2rem' }}>
      <h2>Recent Trips</h2>
      <ul>
        {metrics.trips.map((trip, i) => (
          <li key={i}>{trip.date}: {trip.provider} to {trip.dest}</li>
        ))}
      </ul>
    </div>
  </div>
)

app.get('/', (c) => {
  // In production, this would read from the local travel_metrics.json
  const metrics = JSON.parse(Bun.file('./travel_metrics.json').toString())
  return c.html(<TravelDashboard metrics={metrics} />)
})

export default app
