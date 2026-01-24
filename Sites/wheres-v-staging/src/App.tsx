import { useEffect, useState } from 'react';
import { HeroHome } from './components/HeroHome';
import { HeroPreDeparture } from './components/HeroPreDeparture';
import { HeroInTransit } from './components/HeroInTransit';
import { HeroAtDestination } from './components/HeroAtDestination';
import { HeroAtAirport } from './components/HeroAtAirport';

interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
  confirmation?: string;
}

interface Hotel {
  name: string;
  address?: string;
  city?: string;
  check_in?: string;
  check_out?: string;
  confirmation?: string;
}

interface Train {
  carrier: string;
  service?: string;
  departure_station: string;
  arrival_station: string;
  departure_time: string;
  arrival_time: string;
  confirmation?: string;
}

interface Leg {
  id: string;
  trip_id: string;
  sequence: number;
  type?: 'flight' | 'train';
  flight?: Flight;
  train?: Train;
  destination_city?: string;
  hotel?: Hotel | null;
  staying_with?: {
    name: string;
    phone?: string | null;
    notes?: string | null;
  } | null;
}

interface Trip {
  id: string;
  home_base: string;
  status: string;
  notes?: string;
  legs: string[];
}

interface AppState {
  state: 'home' | 'pre_departure' | 'traveling_today' | 'at_airport' | 'boarding' | 'in_transit' | 'landed' | 'at_destination';
  current_leg: Leg | null;
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
    hours_until_departure?: number;
    minutes_until_departure?: number;
    leg_number?: number;
    total_legs?: number;
  };
  upcoming_legs?: Leg[];
}

type Timezone = 'ET' | 'IST';

function formatTime(isoString: string, tz: Timezone): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  });
}

function formatDate(isoString: string, tz: Timezone): string {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  });
}

function UpcomingItinerary({ legs, timezone, onToggleTimezone }: { 
  legs: Leg[], 
  timezone: 'ET' | 'IST',
  onToggleTimezone: () => void 
}) {
  if (!legs || legs.length === 0) return null;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric',
      timeZone: timezone === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
    });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      timeZone: timezone === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
    });
  };

  return (
    <div className="mt-6 bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide">
          Upcoming Travel
        </h3>
        <button 
          onClick={onToggleTimezone}
          className="text-xs bg-zinc-800 hover:bg-zinc-700 px-2 py-1 rounded transition-colors text-zinc-400"
        >
          {timezone}
        </button>
      </div>
      
      <div className="space-y-3">
        {legs.map((leg, index) => {
          const isTrainLeg = !!leg.train;
          const transport = leg.flight || leg.train;
          if (!transport) return null;
          
          const depTime = transport.departure_time;
          const depLocation = isTrainLeg 
            ? (transport as any).departure_station 
            : (transport as any).departure_airport;
          const arrLocation = isTrainLeg 
            ? (transport as any).arrival_station 
            : (transport as any).arrival_airport;
          const transportNumber = isTrainLeg 
            ? `${(transport as any).carrier} ${(transport as any).service || ''}`.trim()
            : (transport as any).number;

          return (
            <div key={leg.id || index} className="flex items-center gap-4 p-3 bg-zinc-800/50 rounded-lg">
              {/* Date */}
              <div className="w-20 text-center">
                <div className="text-sm font-medium text-white">
                  {formatDate(depTime)}
                </div>
              </div>
              
              {/* Icon */}
              <div className="text-xl">
                {isTrainLeg ? '🚂' : '✈️'}
              </div>
              
              {/* Route */}
              <div className="flex-1">
                <div className="flex items-center gap-2 text-white font-medium">
                  <span>{depLocation}</span>
                  <span className="text-zinc-500">→</span>
                  <span>{arrLocation}</span>
                </div>
                <div className="text-xs text-zinc-500">
                  {transportNumber} • {formatTime(depTime)}
                </div>
              </div>
              
              {/* Destination */}
              <div className="text-right">
                <div className="text-sm text-zinc-300">{leg.destination_city}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function App() {
  const [status, setStatus] = useState<AppState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [timezone, setTimezone] = useState<Timezone>(() => {
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
    const interval = setInterval(fetchStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div 
        className="min-h-screen bg-black flex items-center justify-center"
        style={{
          backgroundImage: 'url(/logo-v-white-lines.png)',
          backgroundSize: '80% auto',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          filter: 'invert(1)',
          opacity: 0.04
        }}
      >
        <div className="animate-pulse text-zinc-500">Loading...</div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-red-500">Error loading status</div>
      </div>
    );
  }

  const renderHero = () => {
    const flight = status.current_leg?.flight;
    const hotel = status.current_leg?.hotel;
    const destination = status.current_leg?.destination_city || flight?.arrival_airport;
    
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
      
      case 'at_airport':
      case 'boarding':
      case 'traveling_today':
        return (
          <HeroAtAirport
            message={status.message}
            destination={destination || 'destination'}
            flight={flight}
            minutesUntilDeparture={status.context?.minutes_until_departure}
            tripNotes={status.current_trip?.notes}
            legNumber={status.context?.leg_number}
            totalLegs={status.context?.total_legs}
            timezone={timezone}
            onToggleTimezone={toggleTimezone}
            isBoarding={status.state === 'boarding'}
          />
        );
      
      case 'pre_departure':
        return (
          <HeroPreDeparture
            message={status.message}
            destination={destination || 'destination'}
            countdownDays={status.context?.countdown_days || 0}
            flight={flight}
            hotel={hotel}
            tripNotes={status.current_trip?.notes}
            legNumber={status.context?.leg_number}
            totalLegs={status.context?.total_legs}
            timezone={timezone}
            onToggleTimezone={toggleTimezone}
          />
        );
      
      case 'in_transit':
        return (
          <HeroInTransit
            message={status.message}
            flight={flight}
            legNumber={status.context?.leg_number}
            totalLegs={status.context?.total_legs}
            timezone={timezone}
            onToggleTimezone={toggleTimezone}
          />
        );
      
      case 'landed':
      case 'at_destination':
        // Get the next leg from upcoming_legs (the next transport after current location)
        const nextLeg = status.upcoming_legs?.[0];
        const nextTransport = nextLeg?.flight || nextLeg?.train;
        
        return (
          <HeroAtDestination
            message={status.message}
            hotel={hotel}
            nextLeg={nextLeg}
            legNumber={status.context?.leg_number}
            totalLegs={status.context?.total_legs}
            timezone={timezone}
            onToggleTimezone={toggleTimezone}
            justLanded={status.state === 'landed'}
            stayingWith={status.current_leg?.staying_with}
          />
        );
      
      default:
        // Fallback - show whatever message we have
        return (
          <div className="text-center">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
              <p className="text-xl font-semibold text-zinc-100">{status.message}</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-black text-zinc-100 flex flex-col items-center justify-center p-4 relative">
      {/* Wireframe V Background Overlay */}
      <div 
        className="fixed inset-0 z-0 pointer-events-none overflow-hidden"
      >
        <img 
          src="/logo-v-white-lines.png" 
          alt=""
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-[45%] w-auto min-w-[120vw] min-h-[120vh] object-contain"
          style={{
            filter: 'invert(1)',
            opacity: 0.18
          }}
        />
      </div>
      
      <div className="relative z-10 flex flex-col items-center">
        <h1 className="text-3xl font-bold text-white mb-8">
          Where's <span className="text-zinc-500">V</span>?
        </h1>
        
        <div className="w-full max-w-md">
          {renderHero()}
        </div>

        {/* 7-Day Itinerary */}
        {status.upcoming_legs && status.upcoming_legs.length > 0 && (
          <UpcomingItinerary 
            legs={status.upcoming_legs} 
            timezone={timezone}
            onToggleTimezone={toggleTimezone}
          />
        )}

        {error && (
          <p className="mt-4 text-sm text-amber-600">{error}</p>
        )}

        <p className="mt-8 text-sm text-zinc-600">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

export default App;

