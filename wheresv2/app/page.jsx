'use client';
import { useState, useEffect } from 'react';

export default function HomePage() {
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    fetchTripData();
    const interval = setInterval(() => {
      fetchTripData();
    }, 15000); // Poll every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchTripData = async () => {
    try {
      const res = await fetch('/api/trip-status');
      const data = await res.json();
      setTripData(data);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch trip data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div style={{ fontSize: '2rem', color: '#FF5A5F' }}>Loading...</div>
      </div>
    );
  }

  if (!tripData || !tripData.outbound_flight) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h1 style={{ color: '#484848' }}>No active trips</h1>
        <p style={{ color: '#767676' }}>V is not traveling right now.</p>
      </div>
    );
  }

  const { outbound_flight, return_flight, weather } = tripData;

  return (
    <div className="container">
      <header>
        <h1>Where's V?</h1>
        <p className="subtitle">Real-time travel tracker</p>
      </header>

      <main>
        {/* Current Flight Status */}
        <section className="status-card">
          <div className="status-icon">✈️</div>
          <div className="status-text">
            <h2>{getStageMessage(outbound_flight)}</h2>
            <p className="status-detail">{getFlightRoute(outbound_flight)}</p>
            <p className="flight-number">{outbound_flight.airline} • {outbound_flight.flight_number}</p>
          </div>
        </section>

        {/* Progress Tracker */}
        <section className="progress-section">
          <h3>Trip Progress</h3>
          <div className="progress-tracker">
            <div className={`progress-step ${isStageCompleted('preparing', outbound_flight.stage) || outbound_flight.stage === 'preparing' ? 'completed' : ''}`}>
              <div className="step-icon">📋</div>
              <div className="step-label">Preparing</div>
            </div>
            <div className="progress-line"></div>
            <div className={`progress-step ${isStageCompleted('boarding', outbound_flight.stage) || outbound_flight.stage === 'boarding' ? 'completed' : ''}`}>
              <div className="step-icon">🚶</div>
              <div className="step-label">Boarding</div>
            </div>
            <div className="progress-line"></div>
            <div className={`progress-step ${isStageCompleted('in_air', outbound_flight.stage) || outbound_flight.stage === 'in_air' ? 'completed' : ''}`}>
              <div className="step-icon">✈️</div>
              <div className="step-label">In Air</div>
            </div>
            <div className="progress-line"></div>
            <div className={`progress-step ${outbound_flight.stage === 'landed' ? 'completed' : ''}`}>
              <div className="step-icon">🛬</div>
              <div className="step-label">Landed</div>
            </div>
          </div>
        </section>

        {/* Flight Details */}
        <section className="details-section">
          <div className="detail-card">
            <h4>Departure</h4>
            <p className="detail-city">{outbound_flight.departure.city}</p>
            <p className="detail-time">{formatTime(outbound_flight.departure.scheduled)}</p>
            <p className="detail-airport">{outbound_flight.departure.airport}</p>
          </div>
          <div className="detail-card">
            <h4>Arrival</h4>
            <p className="detail-city">{outbound_flight.arrival.city}</p>
            <p className="detail-time">{formatTime(outbound_flight.arrival.scheduled)}</p>
            <p className="detail-airport">{outbound_flight.arrival.airport}</p>
          </div>
        </section>

        {/* Return Flight Info */}
        {return_flight && (
          <section className="return-flight">
            <h3>Return Flight</h3>
            <div className="return-info">
              <p><strong>V returns on:</strong> {formatTime(return_flight.departure.scheduled)}</p>
              <p>{return_flight.airline} • {return_flight.flight_number}</p>
              <p>{return_flight.departure.city} → {return_flight.arrival.city}</p>
            </div>
          </section>
        )}

        {/* Weather */}
        {weather && (
          <section className="weather-card">
            <h3>Weather at Destination</h3>
            <p><strong>{weather.destination}:</strong> {weather.temp_f}°F, {weather.condition}</p>
          </section>
        )}

        {/* Last Update */}
        <footer>
          <p className="last-update">Last updated: {lastUpdate.toLocaleTimeString()}</p>
          <p className="tracking-note">Tracking via transponder {outbound_flight.icao24}</p>
        </footer>
      </main>

      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .container {
          font-family: 'Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          padding: 2rem;
        }

        header {
          text-align: center;
          color: white;
          margin-bottom: 2rem;
        }

        header h1 {
          font-size: 3rem;
          font-weight: 800;
          margin-bottom: 0.5rem;
        }

        .subtitle {
          font-size: 1.2rem;
          opacity: 0.9;
        }

        main {
          max-width: 800px;
          margin: 0 auto;
        }

        .status-card {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          margin-bottom: 2rem;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
          display: flex;
          align-items: center;
          gap: 2rem;
        }

        .status-icon {
          font-size: 4rem;
        }

        .status-text h2 {
          color: #FF5A5F;
          font-size: 2rem;
          margin-bottom: 0.5rem;
        }

        .status-detail {
          color: #484848;
          font-size: 1.2rem;
          margin-bottom: 0.5rem;
        }

        .flight-number {
          color: #767676;
          font-size: 1rem;
        }

        .progress-section {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          margin-bottom: 2rem;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        }

        .progress-section h3 {
          color: #484848;
          font-size: 1.5rem;
          margin-bottom: 1.5rem;
        }

        .progress-tracker {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .progress-step {
          text-align: center;
          opacity: 0.4;
          transition: opacity 0.3s;
        }

        .progress-step.completed {
          opacity: 1;
        }

        .step-icon {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
        }

        .step-label {
          color: #484848;
          font-size: 0.9rem;
          font-weight: 600;
        }

        .progress-line {
          flex: 1;
          height: 4px;
          background: #e0e0e0;
          margin: 0 1rem;
        }

        .details-section {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .detail-card {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .detail-card h4 {
          color: #767676;
          font-size: 0.9rem;
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-bottom: 1rem;
        }

        .detail-city {
          color: #484848;
          font-size: 1.5rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .detail-time {
          color: #FF5A5F;
          font-size: 1.1rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .detail-airport {
          color: #767676;
          font-size: 0.9rem;
        }

        .return-flight {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          margin-bottom: 2rem;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
          border-left: 4px solid #00A699;
        }

        .return-flight h3 {
          color: #484848;
          font-size: 1.3rem;
          margin-bottom: 1rem;
        }

        .return-info p {
          color: #484848;
          margin-bottom: 0.5rem;
        }

        .return-info strong {
          color: #00A699;
        }

        .weather-card {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          margin-bottom: 2rem;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .weather-card h3 {
          color: #484848;
          font-size: 1.3rem;
          margin-bottom: 1rem;
        }

        .weather-card p {
          color: #484848;
        }

        footer {
          text-align: center;
          color: white;
          margin-top: 2rem;
        }

        .last-update {
          font-size: 0.9rem;
          opacity: 0.8;
          margin-bottom: 0.5rem;
        }

        .tracking-note {
          font-size: 0.8rem;
          opacity: 0.6;
        }

        @media (max-width: 768px) {
          header h1 {
            font-size: 2rem;
          }

          .status-card {
            flex-direction: column;
            text-align: center;
          }

          .details-section {
            grid-template-columns: 1fr;
          }

          .progress-tracker {
            flex-wrap: wrap;
          }

          .progress-line {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}

function getStageMessage(flight) {
  switch (flight.stage) {
    case 'preparing': return 'Getting ready to travel';
    case 'boarding': return 'Boarding the plane';
    case 'in_air': return 'In the air!';
    case 'landed': return 'Landed safely';
    default: return 'Traveling';
  }
}

function getFlightRoute(flight) {
  return `${flight.departure.city} → ${flight.arrival.city}`;
}

function isStageCompleted(stage, currentStage) {
  const stages = ['preparing', 'boarding', 'in_air', 'landed'];
  return stages.indexOf(stage) < stages.indexOf(currentStage);
}

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}
