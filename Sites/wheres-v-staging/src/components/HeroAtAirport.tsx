interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
  confirmation?: string;
}

type Timezone = 'ET' | 'IST';

interface HeroAtAirportProps {
  message: string;
  destination: string;
  flight?: Flight | null;
  minutesUntilDeparture?: number;
  tripNotes?: string | null;
  legNumber?: number;
  totalLegs?: number;
  timezone: Timezone;
  onToggleTimezone: () => void;
  isBoarding?: boolean;
}

function formatTime(isoString: string, tz: Timezone): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  });
}

export function HeroAtAirport({
  message,
  destination,
  flight,
  minutesUntilDeparture,
  tripNotes,
  legNumber,
  totalLegs,
  timezone,
  onToggleTimezone,
  isBoarding = false
}: HeroAtAirportProps) {
  const borderColor = isBoarding ? 'border-amber-500/50' : 'border-sky-700/50';
  const bgColor = isBoarding ? 'bg-amber-950/30' : 'bg-sky-950/30';
  
  return (
    <div className="text-center">
      {/* Main status */}
      <div className={`${bgColor} border ${borderColor} rounded-2xl p-8 mb-6`}>
        <div className="text-5xl mb-4">🛫</div>
        <p className="text-2xl font-semibold text-white">{message}</p>
        
        {/* Boarding badge or countdown */}
        {isBoarding ? (
          <div className="mt-4 inline-flex items-center gap-2 bg-amber-500 text-black px-4 py-2 rounded-full font-bold animate-pulse">
            <span className="w-2 h-2 bg-black rounded-full"></span>
            BOARDING NOW
          </div>
        ) : minutesUntilDeparture !== undefined && (
          <div className="mt-4 inline-block bg-sky-900/50 text-sky-300 px-4 py-2 rounded-full font-medium">
            {minutesUntilDeparture <= 60 
              ? `Departing in ${minutesUntilDeparture} min`
              : `Departing in ${Math.floor(minutesUntilDeparture / 60)}h ${minutesUntilDeparture % 60}m`
            }
          </div>
        )}
      </div>

      {/* Trip notes */}
      {tripNotes && (
        <div className="mb-4 p-3 bg-zinc-900/50 border border-zinc-800 rounded-lg">
          <p className="text-sm text-zinc-400">{tripNotes}</p>
        </div>
      )}

      {/* Flight card */}
      {flight && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-zinc-500">Flight</span>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-zinc-300">{flight.number}</span>
              <button 
                onClick={onToggleTimezone}
                className="text-xs bg-zinc-800 hover:bg-zinc-700 px-2 py-1 rounded transition-colors text-zinc-400"
              >
                {timezone}
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between text-lg">
            <div className="text-center">
              <div className="font-bold text-white">{flight.departure_airport}</div>
              <div className="text-sm text-zinc-500">{formatTime(flight.departure_time, timezone)}</div>
            </div>
            <div className="flex-1 px-4">
              <div className="border-t border-dashed border-zinc-700 relative">
                <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-zinc-900 px-2 text-zinc-500">→</span>
              </div>
            </div>
            <div className="text-center">
              <div className="font-bold text-white">{flight.arrival_airport}</div>
              <div className="text-sm text-zinc-500">{formatTime(flight.arrival_time, timezone)}</div>
            </div>
          </div>
          
          {flight.confirmation && (
            <div className="mt-3 pt-3 border-t border-zinc-800 flex items-center justify-between">
              <span className="text-xs text-zinc-600">Confirmation</span>
              <span className="font-mono text-sm text-zinc-400">{flight.confirmation}</span>
            </div>
          )}
        </div>
      )}

      {/* Leg context */}
      {totalLegs && totalLegs > 1 && (
        <div className="text-sm text-zinc-600">
          Leg {legNumber} of {totalLegs}
        </div>
      )}
    </div>
  );
}
