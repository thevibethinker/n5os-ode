type Timezone = 'ET' | 'IST';

interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
}

interface HeroHomeProps {
  message: string;
  lastDestination?: string | null;
  nextDestination?: string | null;
  nextFlight?: Flight | null;
  nextReturn?: Flight | null;
  nextTripNotes?: string | null;
  timezone: Timezone;
  onToggleTimezone: () => void;
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

function formatDate(isoString: string, tz: Timezone): string {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  });
}

export function HeroHome({ 
  message, 
  lastDestination, 
  nextDestination, 
  nextFlight, 
  nextReturn,
  nextTripNotes,
  timezone,
  onToggleTimezone
}: HeroHomeProps) {
  return (
    <div className="text-center">
      {/* Main status card */}
      <div className="bg-gradient-to-b from-emerald-900/30 to-zinc-900 border border-emerald-700/50 rounded-2xl p-8 mb-6">
        <div className="text-5xl mb-4">🏠</div>
        <p className="text-2xl font-semibold text-white">{message}</p>
      </div>

      {/* Next trip details */}
      {nextDestination && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 text-left">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide">
              Next Trip → {nextDestination}
            </h3>
            <button 
              onClick={onToggleTimezone}
              className="text-xs bg-zinc-800 hover:bg-zinc-700 px-2 py-1 rounded transition-colors text-zinc-400"
            >
              {timezone}
            </button>
          </div>

          {/* Trip notes */}
          {nextTripNotes && (
            <div className="mb-4 p-3 bg-zinc-800/50 border border-zinc-700 rounded-lg">
              <p className="text-sm text-zinc-300">{nextTripNotes}</p>
            </div>
          )}

          {/* Outbound flight */}
          {nextFlight && (
            <div className="flex justify-between items-center py-3 border-b border-zinc-800">
              <div>
                <div className="font-semibold text-white">
                  🛫 {formatDate(nextFlight.departure_time, timezone)}
                </div>
                <div className="text-sm text-zinc-500">
                  {nextFlight.departure_airport} → {nextFlight.arrival_airport}
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-zinc-300">{nextFlight.number}</div>
                <div className="text-sm text-zinc-500">{formatTime(nextFlight.departure_time, timezone)}</div>
              </div>
            </div>
          )}

          {/* Return flight */}
          {nextReturn && (
            <div className="flex justify-between items-center py-3">
              <div>
                <div className="font-semibold text-white">
                  🛬 {formatDate(nextReturn.departure_time, timezone)}
                </div>
                <div className="text-sm text-zinc-500">
                  {nextReturn.departure_airport} → {nextReturn.arrival_airport}
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-zinc-300">{nextReturn.number}</div>
                <div className="text-sm text-zinc-500">{formatTime(nextReturn.departure_time, timezone)}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Last destination */}
      {lastDestination && !nextDestination && (
        <div className="mt-4 text-sm text-zinc-600">
          Last trip: {lastDestination}
        </div>
      )}
    </div>
  );
}
