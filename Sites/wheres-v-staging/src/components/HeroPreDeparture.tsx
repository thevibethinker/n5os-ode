type Timezone = 'ET' | 'IST';

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
  check_in?: string;
  check_out?: string;
}

interface HeroPreDepartureProps {
  message: string;
  destination: string;
  countdownDays: number;
  flight?: Flight | null;
  hotel?: Hotel | null;
  legNumber?: number;
  totalLegs?: number;
  timezone: Timezone;
  onToggleTimezone: () => void;
}

function formatTime(dateStr: string, tz: Timezone): string {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  });
}

function formatDate(dateStr: string, tz: Timezone): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric',
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  });
}

export function HeroPreDeparture({
  message,
  destination,
  countdownDays,
  flight,
  hotel,
  legNumber,
  totalLegs,
  timezone,
  onToggleTimezone
}: HeroPreDepartureProps) {
  return (
    <div className="text-center">
      {/* Main status */}
      <div className="bg-zinc-900 border border-zinc-700 rounded-2xl p-8 mb-6">
        <div className="text-5xl mb-4">✈️</div>
        <p className="text-2xl font-semibold text-white">{message}</p>
        
        {/* Countdown badge */}
        <div className="mt-4 inline-block bg-zinc-800 text-zinc-300 px-4 py-2 rounded-full font-medium border border-zinc-700">
          {countdownDays === 0 ? 'Today!' : 
           countdownDays === 1 ? 'Tomorrow' : 
           `${countdownDays} days away`}
        </div>
      </div>

      {/* Flight details */}
      {flight && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-zinc-500">Flight</span>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-zinc-400">{flight.number}</span>
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
                <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-zinc-900 px-2 text-zinc-600">→</span>
              </div>
            </div>
            <div className="text-center">
              <div className="font-bold text-white">{flight.arrival_airport}</div>
              <div className="text-sm text-zinc-500">{formatTime(flight.arrival_time, timezone)}</div>
            </div>
          </div>
          <div className="text-center text-xs text-zinc-500 mt-2">
            {formatDate(flight.departure_time, timezone)}
          </div>
        </div>
      )}

      {/* Hotel info */}
      {hotel && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🏨</span>
            <span className="font-medium text-white">{hotel.name}</span>
          </div>
          {hotel.address && (
            <p className="text-sm text-zinc-500">{hotel.address}</p>
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
