import { Hono } from 'hono'
import { serveStatic } from 'hono/bun'

const app = new Hono()

// Component: Stat Card
const StatCard = ({ title, value, icon }) => (
  <div style={{
    background: 'white',
    padding: '1.5rem',
    borderRadius: '16px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center'
  }}>
    <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{icon}</div>
    <div style={{ color: '#64748b', fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{title}</div>
    <div style={{ color: '#1e293b', fontSize: '1.875rem', fontWeight: '800', marginTop: '0.25rem' }}>{value}</div>
  </div>
)

// Main Page
const WrappedPage = ({ data }) => (
  <div style={{
    fontFamily: 'system-ui, -apple-system, sans-serif',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    minHeight: '100vh',
    padding: '3rem 1rem',
    color: 'white'
  }}>
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <header style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <h1 style={{ fontSize: '3.5rem', fontWeight: '900', marginBottom: '0.5rem', letterSpacing: '-0.025em' }}>2025 Travel Wrapped</h1>
        <p style={{ fontSize: '1.25rem', opacity: '0.9' }}>Your year in motion, powered by Zo.</p>
      </header>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1.5rem',
        marginBottom: '3rem'
      }}>
        <StatCard title="Total Flights" value={data.summary.total_flights} icon="✈️" />
        <StatCard title="Cities Visited" value={data.summary.total_cities} icon="📍" />
        <StatCard title="Top Airline" value={data.summary.top_airline} icon="🏆" />
        <StatCard title="Busiest Month" value={data.summary.busiest_month} icon="📅" />
        <StatCard title="Chaos Score" value={data.summary.cancellation_rate} icon="🌀" />
      </div>
      <h2 style={{ color: '#2d3748', marginTop: '3rem' }}>📜 Your Travel Timeline</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {data.trips.map((trip, i) => (
          <li key={i} style={{ 
            background: 'white', 
            margin: '0.5rem 0', 
            padding: '1rem', 
            borderRadius: '12px',
            borderLeft: trip.status === 'Cancelled' ? '6px solid #e53e3e' : '6px solid #38a169',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span><strong>{trip.date}</strong>: {trip.provider} to {trip.dest}</span>
            <span style={{ 
              color: trip.status === 'Cancelled' ? '#e53e3e' : '#38a169',
              fontWeight: 'bold',
              textTransform: 'uppercase',
              fontSize: '0.8rem'
            }}>{trip.status}</span>
          </li>
        ))}
      </ul>

      <footer style={{ textAlign: 'center', marginTop: '4rem', opacity: '0.6', fontSize: '0.875rem' }}>
        Acknowledge: This tool targets major US carriers and Amtrak. Results may vary.
      </footer>
    </div>
  </div>
)

app.get('/', async (c) => {
  try {
    const file = Bun.file('./travel_metrics.json')
    const data = await file.json()
    return c.html(<WrappedPage data={data} />)
  } catch (e) {
    return c.text("Travel metrics not found. Run the extraction engine first.")
  }
})

export default app


