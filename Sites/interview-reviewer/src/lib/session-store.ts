// Ephemeral in-memory store for transcripts
// Transcripts are NEVER written to disk
// Auto-expire after 30 minutes

interface TranscriptEntry {
  transcript: string;
  company: string;
  jobDescription: string;      // Now required
  selfAssessment: string;      // Replaced sentiment
  customerName: string;        // For remarketing
  customerEmail: string;       // For remarketing
  createdAt: number;
}

const store = new Map<string, TranscriptEntry>();

const EXPIRY_MS = 30 * 60 * 1000; // 30 minutes

export function storeTranscript(
  sessionId: string,
  transcript: string,
  company: string,
  jobDescription: string,      // Now required
  selfAssessment: string,      // Replaced sentiment
  customerName: string,        // For remarketing
  customerEmail: string        // For remarketing
): void {
  // Clean expired entries first
  cleanExpired();

  store.set(sessionId, {
    transcript,
    company,
    jobDescription,
    selfAssessment,
    customerName,
    customerEmail,
    createdAt: Date.now(),
  });
}

export function getTranscript(
  sessionId: string
): TranscriptEntry | undefined {
  const entry = store.get(sessionId);
  if (!entry) return undefined;

  // Check if expired
  if (Date.now() - entry.createdAt > EXPIRY_MS) {
    store.delete(sessionId);
    return undefined;
  }

  return entry;
}

export function deleteTranscript(sessionId: string): void {
  store.delete(sessionId);
}

function cleanExpired(): void {
  const now = Date.now();
  for (const [key, entry] of store.entries()) {
    if (now - entry.createdAt > EXPIRY_MS) {
      store.delete(key);
    }
  }
}

// Run cleanup every 5 minutes
setInterval(cleanExpired, 5 * 60 * 1000);




