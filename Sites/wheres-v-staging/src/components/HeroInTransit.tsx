type Timezone = 'ET' | 'IST';

interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
}

interface Hotel {
  name: string;
  address?: string;
}

interface HeroInTransitProps {
  message: string;
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

export function HeroInTransit({
  message,
  flight,
  hotel,
  legNumber,
  totalLegs,
  timezone,
  onToggleTimezone
}: HeroInTransitProps) {
  // Calculate progress if we have flight times
  let progress = 50;
  if (flight) {
    const dep = new Date(flight.departure_time).getTime();
    const arr = new Date(flight.arrival_time).getTime();
    const now = Date.now();
    progress = Math.min(100, Math.max(0, ((now - dep) / (arr - dep)) * 100));
  }

  return (
    <div className="text-center">
      {/* Main status - animated gradient */}
      <div className="bg-gradient-to-r from-sky-900/40 via-zinc-900 to-sky-900/40 border border-sky-700/50 rounded-2xl p-8 mb-6 relative overflow-hidden">
        {/* Animated plane */}
        <div className="text-5xl mb-4 animate-bounce">✈️</div>
        <p className="text-2xl font-semibold text-white">{message}</p>
        
        {/* Progress bar */}
        {flight && (
          <div className="mt-6 relative">
            <div className="flex items-center justify-between text-xs text-zinc-500 mb-2">
              <span>{flight.departure_airport}</span>
              <span>{flight.arrival_airport}</span>
            </div>
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-sky-500 to-sky-400 rounded-full transition-all duration-1000"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-xs text-zinc-500 mt-2">
              <span>{formatTime(flight.departure_time, timezone)}</span>
              <span>ETA {formatTime(flight.arrival_time, timezone)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Flight card */}
      {flight && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-zinc-500">✈️ {flight.number}</span>
            <button 
              onClick={onToggleTimezone}
              className="text-xs bg-zinc-800 hover:bg-zinc-700 px-2 py-1 rounded transition-colors text-zinc-400"
            >
              {timezone}
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div className="text-center">
              <div className="font-bold text-white">{flight.departure_airport}</div>
              <div className="text-xs text-zinc-500">{formatTime(flight.departure_time, timezone)}</div>
            </div>
            <div className="text-zinc-600">→</div>
            <div className="text-center">
              <div className="font-bold text-white">{flight.arrival_airport}</div>
              <div className="text-xs text-zinc-500">{formatTime(flight.arrival_time, timezone)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Hotel waiting */}
      {hotel && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 text-left">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">🏨</span>
            <span className="font-medium text-white">{hotel.name}</span>
          </div>
          <p className="text-sm text-zinc-500">Waiting at destination</p>
        </div>
      )}

      {/* Leg context */}
      {totalLegs && totalLegs > 1 && (
        <div className="mt-4 text-sm text-zinc-600">
          Leg {legNumber} of {totalLegs}
        </div>
      )}
    </div>
  );
}
