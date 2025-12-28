interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
}

interface HeroInTransitProps {
  message: string;
  destination: string;
  flight?: Flight | null;
  legNumber?: number;
  totalLegs?: number;
}

export function HeroInTransit({
  message,
  destination,
  flight,
  legNumber,
  totalLegs
}: HeroInTransitProps) {
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  };

  // Calculate progress if we have flight times
  const getFlightProgress = () => {
    if (!flight) return 50;
    const now = new Date().getTime();
    const dep = new Date(flight.departure_time).getTime();
    const arr = new Date(flight.arrival_time).getTime();
    const total = arr - dep;
    const elapsed = now - dep;
    return Math.min(100, Math.max(0, (elapsed / total) * 100));
  };

  const getETA = () => {
    if (!flight) return null;
    const arr = new Date(flight.arrival_time);
    const now = new Date();
    const diffMs = arr.getTime() - now.getTime();
    const diffMins = Math.round(diffMs / 60000);
    
    if (diffMins < 0) return 'Landed';
    if (diffMins < 60) return `${diffMins}m`;
    const hours = Math.floor(diffMins / 60);
    const mins = diffMins % 60;
    return `${hours}h ${mins}m`;
  };

  const progress = getFlightProgress();
  const eta = getETA();

  return (
    <div className="text-center">
      {/* Main status */}
      <div className="bg-sky-50 border-2 border-sky-200 rounded-2xl p-8 mb-6">
        <div className="text-6xl mb-4 animate-pulse">🛫</div>
        <p className="text-2xl font-semibold text-sky-800">{message}</p>
        
        {/* ETA badge */}
        {eta && (
          <div className="mt-4 inline-block bg-sky-100 text-sky-700 px-4 py-2 rounded-full font-medium">
            ETA: {eta}
          </div>
        )}
      </div>

      {/* Flight progress */}
      {flight && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <span className="font-mono text-sm text-gray-500">{flight.number}</span>
          </div>
          
          {/* Progress visualization */}
          <div className="flex items-center justify-between text-lg mb-2">
            <div className="text-center">
              <div className="font-bold text-gray-400">{flight.departure_airport}</div>
              <div className="text-xs text-gray-400">{formatTime(flight.departure_time)}</div>
            </div>
            <div className="flex-1 px-4">
              <div className="h-2 bg-gray-100 rounded-full relative overflow-hidden">
                <div 
                  className="absolute left-0 top-0 h-full bg-sky-500 rounded-full transition-all duration-1000"
                  style={{ width: `${progress}%` }}
                />
                <div 
                  className="absolute top-1/2 transform -translate-y-1/2 text-lg"
                  style={{ left: `${progress}%`, marginLeft: '-12px' }}
                >
                  ✈️
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className="font-bold text-sky-700">{flight.arrival_airport}</div>
              <div className="text-xs text-gray-500">{formatTime(flight.arrival_time)}</div>
            </div>
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

