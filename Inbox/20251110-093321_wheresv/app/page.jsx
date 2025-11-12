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
      console.error('Error fetching trip data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading V's trip status...</div>
      </div>
    );
  }

  if (!tripData || tripData.status === 'completed') {
    return (
      <div className="container">
        <div className="no-trip">
          <h1>No Active Trips</h1>
          <p>V isn't traveling right now. Check back soon!</p>
        </div>
      </div>
    );
  }

  const outbound = tripData.outbound_flight;
  const returnFlight = tripData.return_flight;

  return (
    <div className="container">
      <header>
        <h1>Where's V?</h1>
        <p className="subtitle">Real-time flight tracking for peace of mind</p>
      </header>

      {/* Current Status Banner */}
      <div className="status-banner">
        <div className="status-icon">✈️</div>
        <div className="status-text">
          <h2>{getStatusMessage(outbound)}</h2>
          <p className="status-detail">{getStatusDetail(outbound)}</p>
        </div>
      </div>

      {/* Progress Tracker */}
      <div className="progress-section">
        <h3>Flight Progress</h3>
        <div className="progress-tracker">
          <ProgressStep 
            label="Preparing" 
            active={outbound.current_stage === 'preparing'}
            completed={isStageCompleted('preparing', outbound.current_stage)}
          />
          <ProgressStep 
            label="Boarding" 
            active={outbound.current_stage === 'boarding'}
            completed={isStageCompleted('boarding', outbound.current_stage)}
          />
          <ProgressStep 
            label="In the Air" 
            active={outbound.current_stage === 'in_air'}
            completed={isStageCompleted('in_air', outbound.current_stage)}
          />
          <ProgressStep 
            label="Landed" 
            active={outbound.current_stage === 'landed'}
            completed={isStageCompleted('landed', outbound.current_stage)}
          />
        </div>
      </div>

      {/* Flight Details */}
      <div className="flight-details">
        <div className="flight-card">
          <h3>✈️ Outbound Flight</h3>
          <div className="flight-info">
            <div className="flight-header">
              <span className="airline">{outbound.airline}</span>
              <span className="flight-number">{outbound.flight_number}</span>
            </div>
            <div className="route">
              <div className="airport">
                <div className="airport-code">{outbound.departure.airport}</div>
                <div className="airport-name">{outbound.departure.city}</div>
                <div className="time">{formatTime(outbound.departure.scheduled)}</div>
                {outbound.departure.gate && <div className="gate">Gate {outbound.departure.gate}</div>}
              </div>
              <div className="arrow">→</div>
              <div className="airport">
                <div className="airport-code">{outbound.arrival.airport}</div>
                <div className="airport-name">{outbound.arrival.city}</div>
                <div className="time">{formatTime(outbound.arrival.scheduled)}</div>
                {outbound.arrival.gate && <div className="gate">Gate {outbound.arrival.gate}</div>}
              </div>
            </div>
          </div>
        </div>

        {returnFlight && (
          <div className="flight-card return">
            <h3>🏠 Return Flight</h3>
            <div className="flight-info">
              <div className="flight-header">
                <span className="airline">{returnFlight.airline}</span>
                <span className="flight-number">{returnFlight.flight_number}</span>
              </div>
              <div className="route">
                <div className="airport">
                  <div className="airport-code">{returnFlight.departure.airport}</div>
                  <div className="airport-name">{returnFlight.departure.city}</div>
                  <div className="time">{formatTime(returnFlight.departure.scheduled)}</div>
                </div>
                <div className="arrow">→</div>
                <div className="airport">
                  <div className="airport-code">{returnFlight.arrival.airport}</div>
                  <div className="airport-name">{returnFlight.arrival.city}</div>
                  <div className="time">{formatTime(returnFlight.arrival.scheduled)}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Weather */}
      {tripData.destination?.weather && (
        <div className="weather-card">
          <h3>☀️ Weather in {tripData.destination.city}</h3>
          <div className="weather-info">
            <span className="temp">{tripData.destination.weather.temp_f}°F</span>
            <span className="condition">{tripData.destination.weather.condition}</span>
          </div>
        </div>
      )}

      {/* Manual Updates */}
      {tripData.manual_updates && tripData.manual_updates.length > 0 && (
        <div className="updates-section">
          <h3>📱 Updates from V</h3>
          {tripData.manual_updates.slice(-3).reverse().map((update, idx) => (
            <div key={idx} className="update-card">
              <div className="update-time">{formatTime(update.timestamp)}</div>
              <div className="update-message">{update.message}</div>
            </div>
          ))}
        </div>
      )}

      {/* Protected Link */}
      <div className="protected-link">
        <a href="/full">🔒 View Full Itinerary (PIN Required)</a>
      </div>

      <footer>
        <p>Last updated: {lastUpdate.toLocaleTimeString()}</p>
        <p className="auto-update">Updates automatically every 15 seconds</p>
      </footer>

      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .container {
          min-height: 100vh;
          background: #FFFFFF;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          color: #484848;
        }

        header {
          background: linear-gradient(135deg, #FF5A5F 0%, #FF385C 100%);
          color: white;
          padding: 2rem;
          text-align: center;
        }

        header h1 {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
          font-weight: 600;
        }

        .subtitle {
          font-size: 1.1rem;
          opacity: 0.95;
        }

        .status-banner {
          background: #00A699;
          color: white;
          padding: 2rem;
          display: flex;
          align-items: center;
          gap: 1.5rem;
          margin: 2rem;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 166, 153, 0.2);
        }

        .status-icon {
          font-size: 3rem;
        }

        .status-text h2 {
          font-size: 1.8rem;
          margin-bottom: 0.5rem;
        }

        .status-detail {
          font-size: 1rem;
          opacity: 0.9;
        }

        .progress-section {
          margin: 2rem;
        }

        .progress-section h3 {
          font-size: 1.5rem;
          margin-bottom: 1.5rem;
          color: #484848;
        }

        .progress-tracker {
          display: flex;
          justify-content: space-between;
          align-items: center;
          position: relative;
          padding: 2rem 0;
        }

        .progress-tracker::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 10%;
          right: 10%;
          height: 3px;
          background: #E0E0E0;
          z-index: 0;
        }

        .flight-details {
          margin: 2rem;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .flight-card {
          background: white;
          border: 2px solid #E0E0E0;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .flight-card h3 {
          font-size: 1.3rem;
          margin-bottom: 1rem;
          color: #FF5A5F;
        }

        .flight-card.return h3 {
          color: #00A699;
        }

        .flight-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .airline {
          font-size: 1.1rem;
          font-weight: 500;
        }

        .flight-number {
          background: #F7F7F7;
          padding: 0.3rem 0.8rem;
          border-radius: 6px;
          font-weight: 600;
          color: #484848;
        }

        .route {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
        }

        .airport {
          flex: 1;
          text-align: center;
        }

        .airport-code {
          font-size: 2rem;
          font-weight: 700;
          color: #484848;
          margin-bottom: 0.3rem;
        }

        .airport-name {
          font-size: 0.9rem;
          color: #767676;
          margin-bottom: 0.5rem;
        }

        .time {
          font-size: 1.1rem;
          font-weight: 500;
          color: #484848;
          margin-bottom: 0.3rem;
        }

        .gate {
          font-size: 0.85rem;
          color: #00A699;
          font-weight: 500;
        }

        .arrow {
          font-size: 2rem;
          color: #FF5A5F;
          flex-shrink: 0;
        }

        .weather-card {
          background: linear-gradient(135deg, #FFE9EA 0%, #FFF5F5 100%);
          border-radius: 12px;
          padding: 1.5rem;
          margin: 2rem;
        }

        .weather-card h3 {
          font-size: 1.3rem;
          margin-bottom: 1rem;
          color: #FF5A5F;
        }

        .weather-info {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .temp {
          font-size: 2.5rem;
          font-weight: 700;
          color: #484848;
        }

        .condition {
          font-size: 1.2rem;
          color: #767676;
        }

        .updates-section {
          margin: 2rem;
        }

        .updates-section h3 {
          font-size: 1.5rem;
          margin-bottom: 1rem;
          color: #484848;
        }

        .update-card {
          background: #F7F7F7;
          border-left: 4px solid #00A699;
          border-radius: 8px;
          padding: 1rem;
          margin-bottom: 1rem;
        }

        .update-time {
          font-size: 0.85rem;
          color: #767676;
          margin-bottom: 0.5rem;
        }

        .update-message {
          font-size: 1rem;
          color: #484848;
        }

        .protected-link {
          margin: 2rem;
          text-align: center;
        }

        .protected-link a {
          display: inline-block;
          background: #484848;
          color: white;
          padding: 1rem 2rem;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 500;
          transition: background 0.2s;
        }

        .protected-link a:hover {
          background: #333333;
        }

        footer {
          text-align: center;
          padding: 2rem;
          color: #767676;
          font-size: 0.9rem;
        }

        .auto-update {
          margin-top: 0.5rem;
          font-size: 0.85rem;
        }

        .loading, .no-trip {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          text-align: center;
          padding: 2rem;
        }

        .loading {
          font-size: 1.5rem;
          color: #767676;
        }

        .no-trip h1 {
          font-size: 2rem;
          color: #484848;
          margin-bottom: 1rem;
        }

        .no-trip p {
          font-size: 1.2rem;
          color: #767676;
        }

        @media (max-width: 768px) {
          header h1 {
            font-size: 2rem;
          }

          .route {
            flex-direction: column;
            gap: 1.5rem;
          }

          .arrow {
            transform: rotate(90deg);
          }

          .status-banner {
            flex-direction: column;
            text-align: center;
          }

          .weather-info {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
}

function ProgressStep({ label, active, completed }) {
  return (
    <div style={{
      position: 'relative',
      zIndex: 1,
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    }}>
      <div style={{
        width: '50px',
        height: '50px',
        borderRadius: '50%',
        background: completed ? '#00A699' : active ? '#FF5A5F' : '#E0E0E0',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        fontSize: '1.5rem',
        marginBottom: '0.5rem',
        transition: 'all 0.3s',
      }}>
        {completed ? '✓' : active ? '⋯' : '○'}
      </div>
      <div style={{
        fontSize: '0.9rem',
        color: active ? '#FF5A5F' : completed ? '#00A699' : '#767676',
        fontWeight: active || completed ? '600' : '400',
      }}>
        {label}
      </div>
    </div>
  );
}

function getStatusMessage(flight) {
  switch (flight.current_stage) {
    case 'preparing': return 'Preparing for Flight';
    case 'boarding': return 'Boarding Now';
    case 'in_air': return 'In the Air';
    case 'landed': return 'Landed Safely';
    default: return 'Flight Scheduled';
  }
}

function getStatusDetail(flight) {
  switch (flight.current_stage) {
    case 'preparing': return `Departing from ${flight.departure.city} soon`;
    case 'boarding': return `Gate ${flight.departure.gate || 'TBA'}`;
    case 'in_air': return `En route to ${flight.arrival.city}`;
    case 'landed': return `Arrived in ${flight.arrival.city}`;
    default: return `${flight.departure.city} → ${flight.arrival.city}`;
  }
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
