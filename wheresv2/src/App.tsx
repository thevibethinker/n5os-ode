import { useState, useEffect } from 'react';
import './FlightTracker.css';

export default function App() {
  const [tripData, setTripData] = useState<any>(null);
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
      const response = await fetch('/api/trip-status');
      const data = await response.json();
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
        <header>
          <h1>Where's V?</h1>
          <p>Loading flight information...</p>
        </header>
      </div>
    );
  }

  if (!tripData || tripData.error) {
    return (
      <div className="container">
        <header>
          <h1>Where's V?</h1>
          <p>No active trip at the moment ✈️</p>
        </header>
      </div>
    );
  }

  const { outbound_flight, return_flight, current_stage } = tripData;

  return (
    <div className="container">
      <header>
        <h1>✈️ Where's V?</h1>
        <p className="subtitle">Real-time flight tracking</p>
        <p className="last-update">Last updated: {lastUpdate.toLocaleTimeString()}</p>
      </header>

      <main>
        {/* Current Status Card */}
        <div className="status-card">
          <div className="status-icon">{getStageIcon(current_stage)}</div>
          <div className="status-text">
            <h2>{getStageTitle(current_stage, outbound_flight)}</h2>
            <p className="status-detail">{getStageDescription(current_stage, outbound_flight)}</p>
          </div>
        </div>

        {/* Progress Tracker */}
        <div className="progress-tracker">
          <div className={`progress-stage ${isStageCompleted('preparing', current_stage) ? 'completed' : current_stage === 'preparing' ? 'active' : ''}`}>
            <div className="stage-icon">📋</div>
            <div className="stage-label">Preparing</div>
          </div>
          
          <div className="progress-line"></div>
          
          <div className={`progress-stage ${isStageCompleted('boarding', current_stage) ? 'completed' : current_stage === 'boarding' ? 'active' : ''}`}>
            <div className="stage-icon">🚶</div>
            <div className="stage-label">Boarding</div>
          </div>
          
          <div className="progress-line"></div>
          
          <div className={`progress-stage ${isStageCompleted('in_air', current_stage) ? 'completed' : current_stage === 'in_air' ? 'active' : ''}`}>
            <div className="stage-icon">✈️</div>
            <div className="stage-label">In Flight</div>
          </div>
          
          <div className="progress-line"></div>
          
          <div className={`progress-stage ${current_stage === 'landed' ? 'completed' : ''}`}>
            <div className="stage-icon">🎉</div>
            <div className="stage-label">Landed</div>
          </div>
        </div>

        {/* Flight Details */}
        <div className="flight-details">
          <div className="flight-card">
            <h3>🛫 Outbound Flight</h3>
            <p className="flight-number">{outbound_flight.flight_iata}</p>
            <p className="route">{outbound_flight.departure.city} → {outbound_flight.arrival.city}</p>
            <p className="time">Departs: {formatTime(outbound_flight.departure.scheduled)}</p>
            <p className="time">Arrives: {formatTime(outbound_flight.arrival.scheduled)}</p>
          </div>

          {return_flight && (
            <div className="flight-card return">
              <h3>🛬 Return Flight</h3>
              <p className="flight-number">{return_flight.flight_iata}</p>
              <p className="route">{return_flight.departure.city} → {return_flight.arrival.city}</p>
              <p className="time">Departs: {formatTime(return_flight.departure.scheduled)}</p>
              <p className="time">Arrives: {formatTime(return_flight.arrival.scheduled)}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function getStageIcon(stage: string) {
  switch (stage) {
    case 'preparing': return '📋';
    case 'boarding': return '🚶';
    case 'in_air': return '✈️';
    case 'landed': return '🎉';
    default: return '✈️';
  }
}

function getStageTitle(stage: string, flight: any) {
  switch (stage) {
    case 'preparing': return 'Getting Ready';
    case 'boarding': return 'Boarding Now';
    case 'in_air': return 'In the Air';
    case 'landed': return 'Safely Landed!';
    default: return `En Route to ${flight.arrival.city}`;
  }
}

function getStageDescription(stage: string, flight: any) {
  switch (stage) {
    case 'preparing': return `Preparing for flight to ${flight.arrival.city}`;
    case 'boarding': return `Boarding ${flight.flight_iata} at gate ${flight.departure.gate || 'TBD'}`;
    case 'in_air': return `Currently flying to ${flight.arrival.city}`;
    case 'landed': return `Arrived in ${flight.arrival.city}`;
    default: return `${flight.departure.city} → ${flight.arrival.city}`;
  }
}

function isStageCompleted(stage: string, currentStage: string) {
  const stages = ['preparing', 'boarding', 'in_air', 'landed'];
  return stages.indexOf(stage) < stages.indexOf(currentStage);
}

function formatTime(isoString: string) {
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
