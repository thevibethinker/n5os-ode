import { useEffect, useState } from 'react'
import './App.css'

interface TripStage {
  stage: string
  message: string
  next_event: string
  progress_percent: number
  emoji: string
}

interface TripData {
  hasTrip: boolean
  trip?: any
  stage?: TripStage
}

function App() {
  const [tripData, setTripData] = useState<TripData>({ hasTrip: false })
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)

  const fetchTripData = async () => {
    try {
      const response = await fetch('/api/status')
      const data = await response.json()
      setTripData(data)
    } catch (error) {
      console.error('Failed to fetch trip data:', error)
    } finally {
      setLoading(false)
    }
  }

  const scanEmails = async () => {
    setScanning(true)
    try {
      const response = await fetch('/api/scan-emails', { method: 'POST' })
      const data = await response.json()
      if (data.success) {
        await fetchTripData()
      }
    } catch (error) {
      console.error('Failed to scan emails:', error)
    } finally {
      setScanning(false)
    }
  }

  useEffect(() => {
    fetchTripData()
    const interval = setInterval(fetchTripData, 15000) // Poll every 15s
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  if (!tripData.hasTrip) {
    return (
      <div className="container">
        <div className="no-trip-card">
          <h1>Where's V?</h1>
          <p className="subtitle">No upcoming trips found</p>
          <button 
            className="scan-button"
            onClick={scanEmails}
            disabled={scanning}
          >
            {scanning ? 'Scanning Emails...' : 'Scan Gmail for Travel Plans'}
          </button>
        </div>
      </div>
    )
  }

  const { trip, stage } = tripData
  const outbound = trip.outbound_flight
  const returnFlight = trip.return_flight

  return (
    <div className="container">
      <header className="header">
        <h1>Where's V?</h1>
        <button 
          className="scan-button-small"
          onClick={scanEmails}
          disabled={scanning}
        >
          {scanning ? '⟳' : '↻'} Rescan
        </button>
      </header>

      {/* Current Status Card */}
      <div className="status-card">
        <div className="status-emoji">{stage?.emoji}</div>
        <h2 className="status-stage">{stage?.stage}</h2>
        <p className="status-message">{stage?.message}</p>
        
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${stage?.progress_percent}%` }}
          />
        </div>
        
        {stage?.next_event && (
          <p className="next-event">Next: {stage.next_event}</p>
        )}
      </div>

      {/* Flight Timeline */}
      <div className="timeline">
        <div className="timeline-item">
          <div className="timeline-label">Outbound Flight</div>
          <div className="flight-card">
            <div className="flight-header">
              <span className="flight-number">{outbound.airline} {outbound.flight_number}</span>
              <span className={`flight-status status-${trip.status}`}>
                {trip.status === 'upcoming' ? 'Upcoming' : trip.status === 'active' ? 'In Progress' : 'Completed'}
              </span>
            </div>
            <div className="flight-route">
              <div className="airport">
                <div className="airport-code">{outbound.departure.airport}</div>
                <div className="airport-time">{new Date(outbound.departure.time).toLocaleString('en-US', { 
                  month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
                })}</div>
                <div className="city-name">{outbound.departure.city}</div>
              </div>
              <div className="route-arrow">→</div>
              <div className="airport">
                <div className="airport-code">{outbound.arrival.airport}</div>
                <div className="airport-time">{new Date(outbound.arrival.time).toLocaleString('en-US', { 
                  month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
                })}</div>
                <div className="city-name">{outbound.arrival.city}</div>
              </div>
            </div>
          </div>
        </div>

        {returnFlight && (
          <div className="timeline-item">
            <div className="timeline-label">Return Flight</div>
            <div className="flight-card">
              <div className="flight-header">
                <span className="flight-number">{returnFlight.airline} {returnFlight.flight_number}</span>
              </div>
              <div className="flight-route">
                <div className="airport">
                  <div className="airport-code">{returnFlight.departure.airport}</div>
                  <div className="airport-time">{new Date(returnFlight.departure.time).toLocaleString('en-US', { 
                    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
                  })}</div>
                  <div className="city-name">{returnFlight.departure.city}</div>
                </div>
                <div className="route-arrow">→</div>
                <div className="airport">
                  <div className="airport-code">{returnFlight.arrival.airport}</div>
                  <div className="airport-time">{new Date(returnFlight.arrival.time).toLocaleString('en-US', { 
                    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
                  })}</div>
                  <div className="city-name">{returnFlight.arrival.city}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Contact Info */}
      <div className="contact-card">
        <h3>Need to Reach V?</h3>
        <div className="contact-methods">
          <div className="contact-method">
            <span className="contact-icon">📧</span>
            <span className="contact-value">attawar.v@gmail.com</span>
          </div>
          <div className="contact-method">
            <span className="contact-icon">📱</span>
            <span className="contact-value">(Check his email)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
