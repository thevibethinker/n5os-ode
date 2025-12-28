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
}

export function HeroPreDeparture({
  message,
  destination,
  countdownDays,
  flight,
  hotel,
  legNumber,
  totalLegs
}: HeroPreDepartureProps) {
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div className="text-center">
      {/* Main status */}
      <div className="bg-amber-50 border-2 border-amber-200 rounded-2xl p-8 mb-6">
        <div className="text-6xl mb-4">✈️</div>
        <p className="text-2xl font-semibold text-amber-800">{message}</p>
        
        {/* Countdown badge */}
        <div className="mt-4 inline-block bg-amber-100 text-amber-700 px-4 py-2 rounded-full font-medium">
          {countdownDays === 0 ? 'Today!' : 
           countdownDays === 1 ? 'Tomorrow' : 
           `${countdownDays} days away`}
        </div>
      </div>

      {/* Flight details */}
      {flight && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-500">Flight</span>
            <span className="font-mono text-sm">{flight.number}</span>
          </div>
          <div className="flex items-center justify-between text-lg">
            <div className="text-center">
              <div className="font-bold">{flight.departure_airport}</div>
              <div className="text-sm text-gray-500">{formatTime(flight.departure_time)}</div>
            </div>
            <div className="flex-1 px-4">
              <div className="border-t border-dashed border-gray-300 relative">
                <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-2 text-gray-400">→</span>
              </div>
            </div>
            <div className="text-center">
              <div className="font-bold">{flight.arrival_airport}</div>
              <div className="text-sm text-gray-500">{formatTime(flight.arrival_time)}</div>
            </div>
          </div>
          <div className="text-center text-xs text-gray-400 mt-2">
            {formatDate(flight.departure_time)}
          </div>
        </div>
      )}

      {/* Hotel info */}
      {hotel && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🏨</span>
            <span className="font-medium">{hotel.name}</span>
          </div>
          {hotel.address && (
            <p className="text-sm text-gray-500">{hotel.address}</p>
          )}
        </div>
      )}

      {/* Leg context */}
      {totalLegs && totalLegs > 1 && (
        <div className="text-sm text-gray-400">
          Leg {legNumber} of {totalLegs}
        </div>
      )}
    </div>
  );
}

