type Timezone = 'ET' | 'IST';

interface Flight {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
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

interface Hotel {
  name: string;
  address?: string;
  city?: string;
  check_in?: string;
  check_out?: string;
  confirmation?: string;
}

interface Leg {
  id: string;
  flight?: Flight;
  train?: Train;
  destination_city?: string;
}

interface HeroAtDestinationProps {
  message: string;
  hotel?: Hotel | null;
  nextLeg?: Leg | null;
  legNumber?: number;
  totalLegs?: number;
  timezone: Timezone;
  onToggleTimezone: () => void;
  justLanded?: boolean;
  stayingWith?: {
    name: string;
    phone?: string | null;
    notes?: string | null;
  } | null;
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

export function HeroAtDestination({
  message,
  hotel,
  nextLeg,
  legNumber,
  totalLegs,
  timezone,
  onToggleTimezone,
  justLanded,
  stayingWith
}: HeroAtDestinationProps) {
  const isTrainLeg = !!nextLeg?.train;
  const transport = nextLeg?.flight || nextLeg?.train;
  
  return (
    <div className="text-center">
      {/* Main status */}
      <div className={`${justLanded ? 'bg-sky-900/50 border-sky-700/50' : 'bg-emerald-900/50 border-emerald-700/50'} border rounded-2xl p-8 mb-6`}>
        <div className="text-4xl mb-4">{justLanded ? '🛬' : '📍'}</div>
        <p className={`text-xl font-semibold ${justLanded ? 'text-sky-100' : 'text-emerald-100'}`}>{message}</p>
      </div>

      {/* Staying with friend */}
      {stayingWith && (
        <div className="bg-purple-900/30 border border-purple-700/50 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm text-purple-300">🏠 Staying with</span>
          </div>
          <p className="font-semibold text-white">{stayingWith.name}</p>
          {stayingWith.phone && (
            <a 
              href={`tel:${stayingWith.phone}`}
              className="text-sm text-purple-300 hover:text-purple-200 transition-colors"
            >
              📞 {stayingWith.phone}
            </a>
          )}
          {stayingWith.notes && (
            <p className="text-xs text-purple-400 mt-1">{stayingWith.notes}</p>
          )}
        </div>
      )}

      {/* Hotel info */}
      {hotel && !stayingWith && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🏨</span>
            <span className="font-medium text-white">{hotel.name}</span>
          </div>
          {hotel.address && (
            <p className="text-sm text-zinc-400">{hotel.address}</p>
          )}
          {hotel.confirmation && (
            <p className="text-xs text-zinc-500 mt-2">Confirmation: {hotel.confirmation}</p>
          )}
        </div>
      )}

      {/* Next transport (flight or train) */}
      {transport && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-4 text-left">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-zinc-500">
              {isTrainLeg ? '🚂 Next Train' : '✈️ Next Flight'}
            </span>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-white">
                {isTrainLeg 
                  ? `${(transport as Train).carrier} ${(transport as Train).service || ''}`.trim()
                  : (transport as Flight).number
                }
              </span>
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
              <div className="font-bold text-white">
                {isTrainLeg 
                  ? (transport as Train).departure_station 
                  : (transport as Flight).departure_airport
                }
              </div>
              <div className="text-sm text-zinc-400">{formatTime(transport.departure_time, timezone)}</div>
            </div>
            <div className="flex-1 px-4">
              <div className="border-t border-dashed border-zinc-700 relative">
                <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-zinc-900 px-2 text-zinc-500">→</span>
              </div>
            </div>
            <div className="text-center">
              <div className="font-bold text-white">
                {isTrainLeg 
                  ? (transport as Train).arrival_station 
                  : (transport as Flight).arrival_airport
                }
              </div>
              <div className="text-sm text-zinc-400">{formatTime(transport.arrival_time, timezone)}</div>
            </div>
          </div>
          <div className="text-center text-xs text-zinc-500 mt-2">
            {formatDate(transport.departure_time, timezone)}
            {nextLeg?.destination_city && ` • to ${nextLeg.destination_city}`}
          </div>
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
