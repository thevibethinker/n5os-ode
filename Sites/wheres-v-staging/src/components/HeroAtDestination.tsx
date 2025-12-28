interface Hotel {
  name: string;
  address?: string;
  check_in?: string;
  check_out?: string;
}

interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
}

interface HeroAtDestinationProps {
  message: string;
  destination: string;
  hotel?: Hotel | null;
  nextLeg?: {
    flight: Flight;
    destination_city: string;
  } | null;
  legNumber?: number;
  totalLegs?: number;
}

export function HeroAtDestination({
  message,
  destination,
  hotel,
  nextLeg,
  legNumber,
  totalLegs
}: HeroAtDestinationProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  };

  // Fun location emoji based on destination
  const getLocationEmoji = (dest: string) => {
    const lower = dest.toLowerCase();
    if (lower.includes('beach') || lower.includes('puerto') || lower.includes('hawaii') || lower.includes('miami')) return '🏖️';
    if (lower.includes('mountain') || lower.includes('denver') || lower.includes('ski')) return '🏔️';
    if (lower.includes('paris') || lower.includes('london') || lower.includes('rome')) return '🏛️';
    if (lower.includes('tokyo') || lower.includes('japan')) return '🗼';
    return '📍';
  };

  return (
    <div className="text-center">
      {/* Main status */}
      <div className="bg-violet-50 border-2 border-violet-200 rounded-2xl p-8 mb-6">
        <div className="text-6xl mb-4">{getLocationEmoji(destination)}</div>
        <p className="text-2xl font-semibold text-violet-800">{message}</p>
      </div>

      {/* Hotel info */}
      {hotel && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🏨</span>
            <span className="font-medium">{hotel.name}</span>
          </div>
          {hotel.address && (
            <p className="text-sm text-gray-500 mb-2">{hotel.address}</p>
          )}
          {(hotel.check_in || hotel.check_out) && (
            <div className="flex gap-4 text-xs text-gray-400">
              {hotel.check_in && <span>Check-in: {formatDate(hotel.check_in)}</span>}
              {hotel.check_out && <span>Check-out: {formatDate(hotel.check_out)}</span>}
            </div>
          )}
        </div>
      )}

      {/* Next leg preview (return flight) */}
      {nextLeg && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-4 text-left">
          <div className="text-sm text-gray-500 mb-2">Return Flight</div>
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">{nextLeg.flight.departure_airport} → {nextLeg.flight.arrival_airport}</div>
              <div className="text-sm text-gray-500">
                {formatDate(nextLeg.flight.departure_time)} at {formatTime(nextLeg.flight.departure_time)}
              </div>
            </div>
            <div className="font-mono text-sm text-gray-400">{nextLeg.flight.number}</div>
          </div>
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

