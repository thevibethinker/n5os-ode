import { useEffect, useState } from 'react';
import { HeroHome } from './components/HeroHome';
import { HeroPreDeparture } from './components/HeroPreDeparture';
import { HeroInTransit } from './components/HeroInTransit';
import { HeroAtDestination } from './components/HeroAtDestination';

interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
  destination_city?: string;
}

interface Trip {
  id: string;
  home_base: string;
  status: string;
  notes?: string;
  legs: string[];
}

interface AppState {
  state: 'home' | 'pre_departure' | 'in_transit' | 'at_destination';
  current_leg: any;
  current_trip: Trip | null;
  next_trip: Trip | null;
  last_trip: Trip | null;
  message: string;
  context: {
    last_destination?: string;
    next_destination?: string;
    next_flight?: Flight;
    next_return?: Flight;
    next_trip_notes?: string;
    countdown_days?: number;
  };
}

type Timezone = 'ET' | 'IST';

function App() {
  const [status, setStatus] = useState<AppState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [timezone, setTimezone] = useState<Timezone>(() => {
    // Load from localStorage or default to ET
    const saved = localStorage.getItem('wheresv-timezone');
    return (saved === 'IST' || saved === 'ET') ? saved : 'ET';
  });

  const toggleTimezone = () => {
    const newTz = timezone === 'ET' ? 'IST' : 'ET';
    setTimezone(newTz);
    localStorage.setItem('wheresv-timezone', newTz);
  };

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/current-state');
        if (!response.ok) throw new Error('Failed to fetch status');
        const data = await response.json();
        setStatus(data);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        setError('Could not load status');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-500">Error loading status</div>
      </div>
    );
  }

  const renderHero = () => {
    switch (status.state) {
      case 'home':
        return (
          <HeroHome
            message={status.message}
            lastDestination={status.context?.last_destination}
            nextDestination={status.context?.next_destination}
            nextFlight={status.context?.next_flight}
            nextReturn={status.context?.next_return}
            nextTripNotes={status.context?.next_trip_notes}
            timezone={timezone}
            onToggleTimezone={toggleTimezone}
          />
        );
      case 'pre_departure':
        return (
          <HeroPreDeparture
            message={status.message}
            countdownDays={status.context?.countdown_days}
            flight={status.current_leg?.flight}
            hotel={status.current_leg?.hotel}
            legNumber={status.context?.leg_number}
            totalLegs={status.context?.total_legs}
          />
        );
      case 'in_transit':
        return (
          <HeroInTransit
            message={status.message}
            flight={status.current_leg?.flight}
            legNumber={status.context?.leg_number}
            totalLegs={status.context?.total_legs}
          />
        );
      case 'at_destination':
        return (
          <HeroAtDestination
            message={status.message}
            hotel={status.current_leg?.hotel}
            returnFlight={status.next_trip?.legs ? undefined : status.current_leg?.flight}
            legNumber={status.context?.leg_number}
            totalLegs={status.context?.total_legs}
          />
        );
      default:
        return <HeroHome message="V is home in NYC" timezone={timezone} onToggleTimezone={toggleTimezone} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Where's V?</h1>
      
      <div className="w-full max-w-md">
        {renderHero()}
      </div>

      {error && (
        <p className="mt-4 text-sm text-amber-600">{error}</p>
      )}

      <p className="mt-8 text-sm text-gray-400">
        Last updated: {lastUpdated.toLocaleTimeString()}
      </p>
    </div>
  );
}

export default App;

