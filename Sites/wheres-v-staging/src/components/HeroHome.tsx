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
  timezone: 'ET' | 'IST';
  onToggleTimezone: () => void;
}

function formatTime(isoString: string, tz: 'ET' | 'IST'): string {
  const date = new Date(isoString);
  const options: Intl.DateTimeFormatOptions = {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  };
  return date.toLocaleTimeString('en-US', options);
}

function formatDate(isoString: string, tz: 'ET' | 'IST'): string {
  const date = new Date(isoString);
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    timeZone: tz === 'ET' ? 'America/New_York' : 'Asia/Kolkata'
  };
  return date.toLocaleDateString('en-US', options);
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
      <div className="bg-emerald-50 border-2 border-emerald-100 rounded-2xl p-8 mb-6">
        <div className="text-4xl mb-4">🏠</div>
        <p className="text-2xl font-semibold text-emerald-800">{message}</p>
      </div>

      {/* Next trip details */}
      {nextDestination && (
        <div className="bg-white border border-gray-200 rounded-xl p-5 text-left">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
              Next Trip → {nextDestination}
            </h3>
            {/* Timezone toggle */}
            <button 
              onClick={onToggleTimezone}
              className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded transition-colors"
            >
              {timezone}
            </button>
          </div>

          {/* Trip notes */}
          {nextTripNotes && (
            <div className="mb-4 p-3 bg-amber-50 border border-amber-100 rounded-lg">
              <p className="text-sm text-amber-800">{nextTripNotes}</p>
            </div>
          )}

          {/* Outbound flight */}
          {nextFlight && (
            <div className="flex justify-between items-center py-3 border-b border-gray-100">
              <div>
                <div className="font-semibold text-gray-800">
                  🛫 {formatDate(nextFlight.departure_time, timezone)}
                </div>
                <div className="text-sm text-gray-500">
                  {nextFlight.departure_airport} → {nextFlight.arrival_airport}
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-gray-700">{nextFlight.number}</div>
                <div className="text-sm text-gray-400">{formatTime(nextFlight.departure_time, timezone)}</div>
              </div>
            </div>
          )}

          {/* Return flight */}
          {nextReturn && (
            <div className="flex justify-between items-center py-3">
              <div>
                <div className="font-semibold text-gray-800">
                  🛬 {formatDate(nextReturn.departure_time, timezone)}
                </div>
                <div className="text-sm text-gray-500">
                  {nextReturn.departure_airport} → {nextReturn.arrival_airport}
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-gray-700">{nextReturn.number}</div>
                <div className="text-sm text-gray-400">{formatTime(nextReturn.departure_time, timezone)}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Last destination */}
      {lastDestination && !nextDestination && (
        <div className="mt-4 text-sm text-gray-400">
          Last trip: {lastDestination}
        </div>
      )}
    </div>
  );
}

